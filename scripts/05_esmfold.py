#!/usr/bin/env python
"""Step 5 - ESMFold validation: does each designed sequence fold back to its backbone?

This is the gate the whole pipeline exists to pass. RFdiffusion proposed a shape and
ProteinMPNN proposed a sequence for it; neither ever checked that the sequence
actually encodes the shape. Here the sequence is folded from scratch, with no
structural input, and compared to the backbone it was designed for. Agreement is
"self-consistency", and it is the in-silico measure that correlates with wet-lab
success.

Folding runs server-side on the ESM Atlas REST API, so no GPU is needed.

  ---------------------------------------------------------------------------
  TWO THINGS THE API DOES NOT DO WHAT THE DOCS ASSUMED

  1. It returns NO pTM. The /foldSequence/v1/pdb/ endpoint returns a bare PDB;
     there is no confidence JSON and no pTM anywhere in it. The "pTM > 0.7"
     threshold in the method notes cannot be evaluated from this endpoint at all.
     Substituted, and stated rather than quietly dropped:
       - mean pLDDT       covers "is the model confident in this fold"
       - TM-score (TMalign) covers "is it the SAME fold as the design"
     For a single-domain 55-mer these carry what pTM would have; getting real pTM
     means running ESMFold locally, which needs the weights and a GPU.

  2. pLDDT comes back on a 0-1 SCALE, not 0-100. B-factors land in 0.5-0.9. Apply
     the conventional ">70" cut to those raw numbers and every design fails. The
     scale is detected below rather than assumed, because other ESMFold builds do
     emit 0-100 and this script should survive either.
  ---------------------------------------------------------------------------

RMSD is measured against CHAIN B of the parent design_N.pdb - the binder backbone
alone. Comparing against the whole complex would fold the 95-residue target into
the number and swamp it.

Run:  conda activate esm && python scripts/05_esmfold.py [--limit N]
      Predictions are cached on disk; rerunning only fetches what is missing.
"""

import argparse
import csv
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
SEQ_TABLE = ROOT / "proteinmpnn" / "outputs" / "sequences.tsv"
DESIGNDIR = ROOT / "rfdiffusion" / "outputs"
PREDDIR = ROOT / "esm_validation" / "predicted_structures"
SCORES = ROOT / "esm_validation" / "scores.tsv"

API = "https://api.esmatlas.com/foldSequence/v1/pdb/"
MAX_RETRIES = 4
BACKOFF = 5      # seconds, doubled per retry
POLITE_DELAY = 1.0   # between successful calls; the endpoint is free, don't hammer it

# Self-consistency thresholds. RMSD < 2 A is the standard bar from the RFdiffusion
# binder work; pLDDT > 70 is the usual "confident fold" line; TM > 0.5 means "same
# fold" in TMalign's own calibration.
MAX_RMSD = 2.0
MIN_PLDDT = 70.0
MIN_TM = 0.5

# COVERAGE IS NOT OPTIONAL. TMalign reports RMSD over the residues it managed to
# align, so a prediction that matches only part of the design scores a flattering
# RMSD: three design_5 sequences aligned just 30 of 52 residues and came back at
# 0.55 A, which reads as a superb fit and is actually a 58%-complete one. TM-score
# already penalises this (they fell to ~0.55, barely over the "same fold" line),
# but requiring coverage states the failure directly instead of hoping a
# borderline TM catches it.
MIN_COVERAGE = 0.90


def fold(sequence, dest):
    """POST one sequence to ESMFold, with retries. Returns True if dest now exists."""
    if dest.exists() and dest.stat().st_size > 0:
        return True
    delay = BACKOFF
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            r = requests.post(API, data=sequence, timeout=180,
                              headers={"Content-Type": "application/x-www-form-urlencoded"})
            if r.status_code == 200 and r.text.lstrip().startswith(("HEADER", "ATOM")):
                dest.write_text(r.text)
                time.sleep(POLITE_DELAY)
                return True
            reason = f"HTTP {r.status_code}: {r.text[:120]}"
        except requests.RequestException as exc:
            reason = f"{type(exc).__name__}: {exc}"
        if attempt < MAX_RETRIES:
            print(f"      retry {attempt}/{MAX_RETRIES - 1} in {delay}s ({reason})")
            time.sleep(delay)
            delay *= 2
        else:
            print(f"      FAILED after {MAX_RETRIES} attempts ({reason})")
    return False


def plddt(pdb_path):
    """Mean and minimum pLDDT, normalised to the conventional 0-100 scale."""
    vals = [float(l[60:66]) for l in pdb_path.read_text().splitlines()
            if l.startswith("ATOM") and l[12:16].strip() == "CA"]
    if not vals:
        return None, None
    # The ESM Atlas endpoint emits 0-1; local ESMFold emits 0-100. Detect, do not assume.
    if max(vals) <= 1.0:
        vals = [v * 100 for v in vals]
    return sum(vals) / len(vals), min(vals)


def binder_only(design, tmpdir):
    """Extract chain B (the designed binder backbone) from a design_N.pdb."""
    src = DESIGNDIR / f"{design}.pdb"
    out = Path(tmpdir) / f"{design}_binder.pdb"
    out.write_text("".join(l for l in src.read_text().splitlines(keepends=True)
                           if l.startswith("ATOM") and l[21] == "B"))
    return out


def tmalign(pred, ref):
    """-> (rmsd, tm_score_normalised_by_reference, n_aligned)."""
    res = subprocess.run(["TMalign", str(pred), str(ref)],
                         capture_output=True, text=True, check=True)
    out = res.stdout
    rmsd = re.search(r"RMSD=\s*([\d.]+)", out)
    aln = re.search(r"Aligned length=\s*(\d+)", out)
    # TMalign prints two TM-scores; the second is normalised by the reference
    # (our design backbone), which is the one we want.
    tms = re.findall(r"TM-score=\s*([\d.]+)", out)
    return (float(rmsd.group(1)) if rmsd else None,
            float(tms[1]) if len(tms) > 1 else None,
            int(aln.group(1)) if aln else None)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=None,
                    help="only process the first N sequences (smoke test)")
    args = ap.parse_args()

    if not SEQ_TABLE.exists():
        raise SystemExit("Run scripts/04b_analyze_sequences.py first.")
    with SEQ_TABLE.open() as fh:
        seqs = list(csv.DictReader(fh, delimiter="\t"))
    if args.limit:
        seqs = seqs[:args.limit]

    PREDDIR.mkdir(parents=True, exist_ok=True)
    cached = sum(1 for r in seqs
                 if (PREDDIR / f"{r['backbone']}_s{r['sample']}.pdb").exists())
    print(f"{len(seqs)} sequences to validate ({cached} already folded and cached)\n")

    rows, failures = [], []
    with tempfile.TemporaryDirectory() as tmp:
        refs = {}
        for i, rec in enumerate(seqs, 1):
            design, sample = rec["backbone"], rec["sample"]
            name = f"{design}_s{sample}"
            dest = PREDDIR / f"{name}.pdb"
            fresh = not dest.exists()
            if fresh:
                print(f"  [{i:>2}/{len(seqs)}] folding {name} ({len(rec['sequence'])} aa)")
            if not fold(rec["sequence"], dest):
                failures.append(name)
                continue

            mean_pl, min_pl = plddt(dest)
            if design not in refs:
                refs[design] = binder_only(design, tmp)
            rmsd, tm, naln = tmalign(dest, refs[design])

            design_len = int(rec["length"])
            coverage = naln / design_len if naln else 0.0
            ok = (rmsd is not None and rmsd < MAX_RMSD
                  and mean_pl >= MIN_PLDDT and tm is not None and tm >= MIN_TM
                  and coverage >= MIN_COVERAGE)
            rows.append({
                "name": name,
                "backbone": design,
                "sample": sample,
                "length": rec["length"],
                "mpnn_score": rec["score"],
                "mean_plddt": round(mean_pl, 1),
                "min_plddt": round(min_pl, 1),
                "rmsd_to_design": round(rmsd, 2) if rmsd is not None else None,
                "tm_score": round(tm, 3) if tm is not None else None,
                "aligned_len": naln,
                "coverage": round(coverage, 3),
                "hotspot_hydrophobic_frac": rec["hotspot_hydrophobic_frac"],
                "net_charge": rec["net_charge"],
                "self_consistent": ok,
                "why_failed": [] if ok else [
                    lbl for cond, lbl in (
                        (rmsd is None or rmsd >= MAX_RMSD, "RMSD"),
                        (mean_pl < MIN_PLDDT, "pLDDT"),
                        (tm is None or tm < MIN_TM, "TM"),
                        (coverage < MIN_COVERAGE, "partial align"),
                    ) if cond],
                "sequence": rec["sequence"],
            })

    if failures:
        print(f"\n!! {len(failures)} sequence(s) could not be folded: {failures}")
    if not rows:
        raise SystemExit("Nothing folded successfully.")

    rows.sort(key=lambda r: (not r["self_consistent"], r["rmsd_to_design"]))
    out = [{**r, "why_failed": "|".join(r["why_failed"])} for r in rows]
    with SCORES.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0]), delimiter="\t",
                           lineterminator="\n")
        w.writeheader()
        w.writerows(out)

    print(f"\nSelf-consistency: RMSD < {MAX_RMSD} A, mean pLDDT >= {MIN_PLDDT}, "
          f"TM >= {MIN_TM}, coverage >= {MIN_COVERAGE:.0%}")
    print("(RMSD is over ALIGNED residues only - read it together with coverage)\n")
    hdr = (f"{'name':<18}{'len':>4}{'pLDDT':>7}{'minPL':>7}{'RMSD':>7}"
           f"{'TM':>7}{'cov':>6}{'MPNN':>7}  ok")
    print(hdr)
    print("-" * len(hdr))
    for r in rows:
        flag = "" if r["self_consistent"] else " <- " + ", ".join(r["why_failed"])
        print(f"{r['name']:<18}{r['length']:>4}{r['mean_plddt']:>7.1f}"
              f"{r['min_plddt']:>7.1f}{r['rmsd_to_design']:>7.2f}"
              f"{r['tm_score']:>7.3f}{r['coverage']:>6.2f}"
              f"{float(r['mpnn_score']):>7.3f}"
              f"  {'PASS' if r['self_consistent'] else flag}")

    n_ok = sum(r["self_consistent"] for r in rows)
    print(f"\nSELF-CONSISTENT: {n_ok}/{len(rows)} sequences "
          f"({100 * n_ok / len(rows):.0f}%)")
    per_bb = {}
    for r in rows:
        per_bb.setdefault(r["backbone"], []).append(r["self_consistent"])
    print("per backbone:")
    for bb, oks in sorted(per_bb.items(), key=lambda kv: -sum(kv[1])):
        print(f"   {bb:<12} {sum(oks)}/{len(oks)}")
    print(f"\nWrote {SCORES.relative_to(ROOT)}")


if __name__ == "__main__":
    sys.exit(main())
