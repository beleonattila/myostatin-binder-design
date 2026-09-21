#!/usr/bin/env python
"""Step 4b - inspect the ProteinMPNN sequences before spending Step 5 on them.

ESMFold calls are the expensive part of the pipeline, so this is the cheap gate in
front of them. It answers four questions:

  1. Did sampling actually sample?  At temperature 0.1 ProteinMPNN can collapse to
     near-identical sequences, which turns "8 candidates" into one candidate
     folded eight times. Reported as mean pairwise identity per backbone; if it is
     high, rerun Step 4 at --sampling_temp 0.2.

  2. Are the interface positions hydrophobic?  The binder residues that sit under
     the knuckle hotspots are the ones that have to carry the affinity. Polar or
     charged residues there mean the sequence does not match the structural intent,
     regardless of what the MPNN score says.

  3. Is the surface plausible?  ProteinMPNN is known to over-produce E/K/R on
     solvent-exposed faces - great for its likelihood, and a real liability for
     expression and non-specific binding. Net charge and hydrophobic fraction are
     reported so the bias is visible rather than assumed away.

  4. Any junk?  Cysteines (should be none - omitted at design time), low-complexity
     runs, or sequences whose length does not match the backbone.

Scores: ProteinMPNN reports negative log-likelihood, so LOWER IS BETTER. `score` is
over the designed chain only; `global_score` covers the whole complex. Rank on
`score` - global_score is dominated by the fixed 95-residue target and barely moves.

Run:  conda activate esm && python scripts/04b_analyze_sequences.py
"""

import csv
import re
import sys
from collections import Counter
from itertools import combinations
from pathlib import Path

from pymol import cmd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _structure_utils import contacting_binder_positions, load_design

ROOT = Path(__file__).resolve().parent.parent
SEQDIR = ROOT / "proteinmpnn" / "outputs" / "seqs"
DESIGNDIR = ROOT / "rfdiffusion" / "outputs"
TARGET_FULL = ROOT / "data" / "prepared" / "myostatin_target.pdb"
REPORT = ROOT / "proteinmpnn" / "outputs" / "sequences.tsv"

HOTSPOTS = [33, 34, 85, 87, 93, 95]
FOOTPRINT = [25, 33, 34, 35, 36, 37, 38, 39, 80, 81, 82, 83, 84, 85, 87, 91, 93,
             95, 97, 102, 104]
INTERFACE_CUTOFF = 5.0

HYDROPHOBIC = set("AVLIMFWYC")
CHARGED_POS = set("KR")
CHARGED_NEG = set("DE")


def parse_fasta(path):
    """-> (native_seq, [(meta, seq), ...]) for a ProteinMPNN output FASTA."""
    entries = []
    header = None
    chunks = []
    for line in path.read_text().splitlines():
        if line.startswith(">"):
            if header is not None:
                entries.append((header, "".join(chunks)))
            header, chunks = line[1:], []
        elif line.strip():
            chunks.append(line.strip())
    if header is not None:
        entries.append((header, "".join(chunks)))

    native = entries[0][1]
    samples = []
    for head, seq in entries[1:]:
        meta = dict(re.findall(r"(\w+)=([-\d.]+)", head))
        samples.append((meta, seq))
    return native, samples


def interface_positions(design):
    """1-based binder positions contacting a hotspot, and the wider epitope.

    Goes through _structure_utils.load_design, NOT the raw PDB: both chains in the
    output are backbone-only, and measuring them directly finds 1-3 positions
    instead of the real interface (the missing sidechain layer again).
    """
    rms = load_design(DESIGNDIR / f"{design}.pdb", TARGET_FULL)
    hs = contacting_binder_positions(HOTSPOTS, INTERFACE_CUTOFF)
    core = contacting_binder_positions(FOOTPRINT, INTERFACE_CUTOFF)
    return hs, core, rms


def mean_pairwise_identity(seqs):
    if len(seqs) < 2:
        return float("nan")
    vals = [sum(a == b for a, b in zip(s1, s2)) / len(s1)
            for s1, s2 in combinations(seqs, 2)]
    return sum(vals) / len(vals)


def low_complexity(seq, run=5):
    """Longest single-residue run - catches poly-A / poly-E stretches."""
    best = cur = 1
    for a, b in zip(seq, seq[1:]):
        cur = cur + 1 if a == b else 1
        best = max(best, cur)
    return best


def main():
    cmd.feedback("disable", "all", "everything")
    fastas = sorted(SEQDIR.glob("design_*.fa"),
                    key=lambda p: int(p.stem.split("_")[1]))
    if not fastas:
        raise SystemExit("No FASTAs - run scripts/04_proteinmpnn.sh first.")

    rows = []
    print("Per-backbone summary "
          "(ProteinMPNN score = negative log-likelihood, LOWER IS BETTER)\n")
    hdr = (f"{'backbone':<12}{'len':>4}{'n':>3}{'best':>7}{'worst':>7}"
           f"{'ident%':>8}{'nHS':>5}{'nEpi':>6}  hotspot-contacting residues (best seq)")
    print(hdr)
    print("-" * (len(hdr) + 6))

    for fa in fastas:
        design = fa.stem
        native, samples = parse_fasta(fa)
        iface, epitope, rms = interface_positions(design)
        seqs = [s for _, s in samples]
        ident = mean_pairwise_identity(seqs)

        scored = sorted(samples, key=lambda t: float(t[0]["score"]))
        best_seq = scored[0][1]
        iface_aa = "".join(best_seq[p - 1] for p in iface if p <= len(best_seq))

        print(f"{design:<12}{len(best_seq):>4}{len(samples):>3}"
              f"{float(scored[0][0]['score']):>7.3f}"
              f"{float(scored[-1][0]['score']):>7.3f}"
              f"{100 * ident:>7.0f}%{len(iface):>5}{len(epitope):>6}  {iface_aa}")

        for rank, (meta, seq) in enumerate(scored, 1):
            comp = Counter(seq)
            n = len(seq)
            hyd = sum(comp[a] for a in HYDROPHOBIC) / n
            charge = sum(comp[a] for a in CHARGED_POS) - sum(comp[a] for a in CHARGED_NEG)
            ia = "".join(seq[p - 1] for p in iface if p <= n)
            ea = "".join(seq[p - 1] for p in epitope if p <= n)
            iface_hyd = (sum(1 for a in ia if a in HYDROPHOBIC) / len(ia)) if ia else 0.0
            epi_hyd = (sum(1 for a in ea if a in HYDROPHOBIC) / len(ea)) if ea else 0.0
            rows.append({
                "backbone": design,
                "rank": rank,
                "sample": meta.get("sample", "?"),
                "score": float(meta["score"]),
                "global_score": float(meta["global_score"]),
                "length": n,
                "target_align_rms": round(rms, 2),
                "hydrophobic_frac": round(hyd, 3),
                "net_charge": charge,
                "n_cys": comp["C"],
                "max_run": low_complexity(seq),
                "n_hotspot_pos": len(iface),
                "hotspot_residues": ia,
                "hotspot_hydrophobic_frac": round(iface_hyd, 3),
                "n_epitope_pos": len(epitope),
                "epitope_residues": ea,
                "epitope_hydrophobic_frac": round(epi_hyd, 3),
                "mean_pairwise_identity": round(ident, 3),
                "sequence": seq,
            })

    # ---- global sanity checks -------------------------------------------------
    print("\nChecks across all %d sequences:" % len(rows))
    cys = [r for r in rows if r["n_cys"]]
    print(f"   cysteines (omitted at design time) : "
          f"{'NONE - as intended' if not cys else str(len(cys)) + ' sequences contain C !!'}")
    runs = [r for r in rows if r["max_run"] >= 5]
    print(f"   low-complexity runs (>=5 identical): "
          f"{len(runs)} sequence(s)"
          + (f" - worst {max(r['max_run'] for r in runs)}" if runs else ""))
    idents = {r["backbone"]: r["mean_pairwise_identity"] for r in rows}
    collapsed = [k for k, v in idents.items() if v > 0.80]
    print(f"   sampling diversity                 : mean pairwise identity "
          f"{100 * sum(idents.values()) / len(idents):.0f}%"
          + (f"  COLLAPSED for {collapsed} - rerun at temp 0.2" if collapsed
             else "  (healthy; <80% everywhere)"))

    bad_rms = {r["backbone"] for r in rows if r["target_align_rms"] > 0.5}
    print(f"   target superposition               : "
          f"{'all < 0.5 A' if not bad_rms else 'FAILED for ' + str(bad_rms)}")

    hyd = [r["hydrophobic_frac"] for r in rows]
    ifh = [r["hotspot_hydrophobic_frac"] for r in rows]
    eph = [r["epitope_hydrophobic_frac"] for r in rows]
    chg = [r["net_charge"] for r in rows]
    print(f"   hydrophobic fraction, whole binder : "
          f"{min(hyd):.2f}-{max(hyd):.2f} (mean {sum(hyd)/len(hyd):.2f})")
    print(f"   hydrophobic fraction, epitope face : "
          f"{min(eph):.2f}-{max(eph):.2f} (mean {sum(eph)/len(eph):.2f})")
    print(f"   hydrophobic fraction, hotspot ring : "
          f"{min(ifh):.2f}-{max(ifh):.2f} (mean {sum(ifh)/len(ifh):.2f})"
          "   <- should exceed the whole-binder value")
    print(f"   net charge                         : "
          f"{min(chg):+d} to {max(chg):+d} (mean {sum(chg)/len(chg):+.1f})")

    print("\nTop 10 sequences overall by ProteinMPNN score:")
    for r in sorted(rows, key=lambda r: r["score"])[:10]:
        print(f"   {r['backbone']:<11} sample {r['sample']:<3} "
              f"score {r['score']:.3f}  hotspotHyd {r['hotspot_hydrophobic_frac']:.2f} "
              f"({r['hotspot_residues']})  epiHyd {r['epitope_hydrophobic_frac']:.2f}  "
              f"charge {r['net_charge']:+d}")
        print(f"      {r['sequence']}")

    with REPORT.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]), delimiter="\t",
                           lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    print(f"\nWrote {REPORT.relative_to(ROOT)} ({len(rows)} sequences)")


if __name__ == "__main__":
    main()
