#!/usr/bin/env python
"""Step 3b - triage RFdiffusion backbones: which designs are worth sequencing?

RFdiffusion happily returns designs docked nowhere useful. The syllabus says
"inspect every output in PyMOL and discard floaters and coils"; this script makes
that judgement explicit and reproducible, so the shortlist is a threshold rather
than a vibe. Still open the survivors in PyMOL - this decides the order.

  ---------------------------------------------------------------------------
  THE TRAP THIS SCRIPT EXISTS TO AVOID
  RFdiffusion writes BACKBONE ONLY - N, CA, C, O, and no CB - for *both* chains.
  Score those files naively and every design looks like a floater: buried area
  comes out near 100 A^2 and a 5 A contact search finds two or three residues.
  That is not a failed dock, it is the missing sidechain layer. A well-packed
  interface has a 4-8 A backbone-to-backbone gap, because that is the space
  sidechains occupy.

  Two corrections, both cheap:
    1. The target is held rigid during diffusion (motif RMSD ~0.13 A), so its
       real sidechains can be restored by superposing data/prepared/
       myostatin_target.pdb back onto the output's chain A.
    2. The binder gets virtual CB atoms built from N/CA/C with ideal geometry -
       the standard trick for reasoning about a backbone-only model, and enough
       to tell "packed against the epitope" from "hovering over it".
  The binder's own sidechains stay missing - that is ProteinMPNN's job in Step 4 -
  so buried area here is a systematic UNDERESTIMATE. Hence the positive control.
  ---------------------------------------------------------------------------

Thresholds are calibrated, not guessed: the same measurements are run on the real
ActRIIB:GDF11 interface from 6MAC, reduced to the identical representation
(ligand full-atom, receptor backbone+CB). That is what a genuine type II
interface scores in these units, and the pass marks are set as fractions of it.

Output PDB convention (verified against the .trb): chain A is the target keeping
5JI1's mature numbering including the 51-64 gap, chain B is the designed binder
numbered from 1. Step 2 hotspots (A33, A34, ...) therefore apply unchanged.

Run:  conda activate esm && python scripts/03b_triage_backbones.py
"""

import csv
import sys
from collections import Counter
from pathlib import Path

import numpy as np
from pymol import cmd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _structure_utils import add_virtual_cb, load_design

ROOT = Path(__file__).resolve().parent.parent
OUTDIR = ROOT / "rfdiffusion" / "outputs"
TARGET_FULL = ROOT / "data" / "prepared" / "myostatin_target.pdb"
CONTROL = ROOT / "data" / "raw" / "6MAC.cif"
REPORT = OUTDIR / "triage.tsv"

HOTSPOTS = [33, 34, 85, 87, 93, 95]
CONTACT_CUTOFF = 5.0

# Fractions of the real ActRIIB interface (computed at runtime). ActRIIB's
# ectodomain is 95 residues against our 45-60, so a design cannot be expected to
# match it - half its buried area is already a substantial miniprotein interface.
DSASA_FRACTION = 0.50
MIN_HOTSPOTS = 3
MIN_HELIX = 0.40

# Compactness. A folded globular protein obeys Rg ~= 2.2 * N^0.38 (Angstroms);
# a 55-residue binder should therefore sit near 10 A. Anything past 1.5x that is
# not a folded miniprotein - it is a long or splayed helix lying along the
# surface, which racks up contacts and buried area without being a protein that
# ProteinMPNN and ESMFold can plausibly reproduce.
MAX_RG_RATIO = 1.5


# How many survivors go on to ProteinMPNN. The floors above only remove designs
# that are not really docked; when most of a run clears them, the shortlist is a
# ranking decision. Ordered by hotspots engaged, then buried area.
SHORTLIST_N = 8


def expected_rg(n_res):
    return 2.2 * n_res ** 0.38


def interface_metrics(target_sel, binder_sel, complex_obj):
    """Contacts, hotspot engagement and buried area for one target:binder pair."""
    cmd.select("_if", f"byres ({target_sel} within {CONTACT_CUTOFF} of {binder_sel})")
    contacts = []
    cmd.iterate("_if and name CA", "out.append(int(resi))",
                space={"out": contacts, "int": int})
    contacts = sorted(set(contacts))

    cmd.set("dot_solvent", 1)
    cmd.set("dot_density", 3)
    # dSASA needs SEPARATE objects: get_area on a selection inside the complex
    # already accounts for the partner chain and silently returns ~0.
    cmd.create("_t", target_sel)
    cmd.create("_b", binder_sel)
    dsasa = (cmd.get_area("_t") + cmd.get_area("_b")
             - cmd.get_area(complex_obj)) / 2.0
    cmd.delete("_t")
    cmd.delete("_b")
    return contacts, dsasa


def positive_control():
    """Score the real ActRIIB:GDF11 interface, full-atom and in design units.

    Returns (full_atom, backbone_cb) results. The pair matters: their ratio is how
    much of a genuine interface is invisible in a backbone-only model, i.e. how
    much ProteinMPNN still has to add in Step 4.
    """
    out = {}
    cmd.delete("all")
    cmd.load(str(CONTROL), "ctl")
    cmd.create("ctl_lig", "ctl and chain A and polymer")            # GDF11, full atom

    cmd.create("ctl_full", "ctl and chain C and polymer")           # ActRIIB, full atom
    cmd.create("cx_full", "ctl_lig or ctl_full")
    out["full"] = interface_metrics("ctl_lig", "ctl_full", "cx_full")

    cmd.create("ctl_bb", "ctl and chain C and polymer and name N+CA+C+O")
    add_virtual_cb("ctl_bb")                                        # ActRIIB, bb+CB
    cmd.create("cx_bb", "ctl_lig or ctl_bb")
    out["bb"] = interface_metrics("ctl_lig", "ctl_bb", "cx_bb")

    out["n_rec"] = cmd.count_atoms("ctl_bb and name CA")
    cmd.delete("all")
    return out


def measure(pdb, target_full_path):
    rms = load_design(pdb, target_full_path)
    n_binder = cmd.count_atoms("binder and name CA")

    cmd.create("cplx", "target or binder")
    contacts, dsasa = interface_metrics("target", "binder", "cplx")
    hit = [h for h in HOTSPOTS if h in contacts]

    cmd.dss("binder")
    ss = []
    cmd.iterate("binder and name CA", "out.append(ss)", space={"out": ss})
    helix = ss.count("H") / len(ss) if ss else 0.0
    sheet = ss.count("S") / len(ss) if ss else 0.0

    xs = np.array([a.coord for a in cmd.get_model("binder and name CA").atom])
    radgyr = float(np.sqrt(((xs - xs.mean(0)) ** 2).sum(1).mean()))

    return {
        "design": pdb.stem,
        "binder_len": n_binder,
        "align_rms": round(rms, 2),
        "hotspots_hit": len(hit),
        "hotspots": "+".join(str(h) for h in hit) or "-",
        "n_contacts": len(contacts),
        "dSASA": round(dsasa, 1),
        "helix_frac": round(helix, 2),
        "sheet_frac": round(sheet, 2),
        "radgyr": round(radgyr, 1),
        "rg_ratio": round(radgyr / expected_rg(n_binder), 2),
        "contacts": " ".join(str(c) for c in contacts),
    }


def main():
    cmd.feedback("disable", "all", "everything")
    designs = sorted(OUTDIR.glob("design_*.pdb"),
                     key=lambda p: int(p.stem.split("_")[1]))
    if not designs:
        raise SystemExit("No designs found - run scripts/03_rfdiffusion.sh first.")

    ctl = positive_control()
    (f_con, f_area), (b_con, b_area), ctl_len = ctl["full"], ctl["bb"], ctl["n_rec"]
    min_dsasa = DSASA_FRACTION * b_area
    print(f"Positive control - the real ActRIIB:GDF11 interface (6MAC), "
          f"{ctl_len}-residue receptor:")
    print(f"   full atom        : {f_area:6.0f} A^2 buried, "
          f"{len(f_con):2d} ligand residues contacted")
    print(f"   backbone + CB    : {b_area:6.0f} A^2 buried, "
          f"{len(b_con):2d} ligand residues contacted   <- design units")
    print(f"   sidechains carry {100 * (1 - b_area / f_area):.0f}% of a real "
          f"interface, so every dSASA below is a LOWER BOUND;")
    print(f"   ProteinMPNN supplies the rest in Step 4 "
          f"(x{f_area / b_area:.1f} once sidechains exist).")
    print(f"   Floor for 'actually docked' set at {DSASA_FRACTION:.0%} of the "
          f"backbone control = {min_dsasa:.0f} A^2.")
    print("   Caveat: ActRIIB engages via sidechain knobs off a beta-sheet, our "
          "designs pack\n   helices flat, so backbone burial is not strictly "
          "comparable - this is a floor,\n   not a quality bar. Ranking picks the "
          "shortlist.\n")

    rows = [measure(p, TARGET_FULL) for p in designs]
    for r in rows:
        if r["hotspots_hit"] < MIN_HOTSPOTS:
            r["verdict"] = "REJECT wrong/weak epitope"
        elif r["dSASA"] < min_dsasa:
            r["verdict"] = "REJECT interface too small"
        elif r["helix_frac"] < MIN_HELIX:
            r["verdict"] = "REJECT not helical"
        elif r["rg_ratio"] > MAX_RG_RATIO:
            r["verdict"] = "REJECT extended, not folded"
        else:
            r["verdict"] = "PASS"

    rows.sort(key=lambda r: (-r["hotspots_hit"], -r["dSASA"]))

    shortlist = [r for r in rows if r["verdict"] == "PASS"][:SHORTLIST_N]
    picked = {r["design"] for r in shortlist}
    for r in rows:
        r["shortlisted"] = r["design"] in picked

    print(f"Triage of {len(rows)} RFdiffusion backbones "
          f"(hotspots {HOTSPOTS}, contact cutoff {CONTACT_CUTOFF} A)\n")
    hdr = (f"{'':2}{'design':<11}{'len':>4}{'hs':>4}{'hotspots hit':>21}"
           f"{'cont':>6}{'dSASA':>8}{'helix':>7}{'Rg':>6}{'Rg/exp':>8}  verdict")
    print(hdr)
    print("-" * len(hdr))
    for r in rows:
        mark = "->" if r["shortlisted"] else "  "
        print(f"{mark}{r['design']:<11}{r['binder_len']:>4}{r['hotspots_hit']:>4}"
              f"{r['hotspots']:>21}{r['n_contacts']:>6}{r['dSASA']:>8.0f}"
              f"{r['helix_frac']:>7.2f}{r['radgyr']:>6.1f}{r['rg_ratio']:>8.2f}"
              f"  {r['verdict']}")

    bad_align = [r["design"] for r in rows if r["align_rms"] > 0.5]
    if bad_align:
        print(f"\n!! target superposition worse than 0.5 A for: {bad_align} "
              "- these metrics are unreliable")

    passed = [r for r in rows if r["verdict"] == "PASS"]
    print(f"\nPASS: {len(passed)}/{len(rows)}  (>={MIN_HOTSPOTS} hotspots, "
          f">={min_dsasa:.0f} A^2 buried, >={MIN_HELIX:.0%} helix, "
          f"Rg <={MAX_RG_RATIO}x the folded expectation)")
    if shortlist:
        print(f"shortlist for ProteinMPNN (top {len(shortlist)} of {len(passed)}): "
              + ", ".join(r["design"] for r in shortlist))
    print("\nverdicts: " + ", ".join(f"{k} x{v}" for k, v in
                                     Counter(r["verdict"] for r in rows).most_common()))
    print("\nhotspot engagement across all designs:")
    for h in HOTSPOTS:
        n = sum(1 for r in rows if str(h) in r["hotspots"].split("+"))
        print(f"   A{h}: contacted by {n}/{len(rows)} designs")

    with REPORT.open("w", newline="") as fh:
        # csv defaults to \r\n; that trailing CR ends up inside the LAST field's
        # value for anything parsing this with awk/cut, so pin it to \n.
        w = csv.DictWriter(fh, fieldnames=list(rows[0]), delimiter="\t",
                           lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    print(f"\nWrote {REPORT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
