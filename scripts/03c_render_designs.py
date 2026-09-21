#!/usr/bin/env python
"""Step 3c - render the shortlisted backbones for visual inspection.

The numbers in triage.tsv say a design is docked on the hotspots; they do not say
it looks like a protein. This renders each shortlisted design on the target so the
"inspect every output in PyMOL" step actually happens, and leaves a .pse behind so
you can rotate them yourself.

Each design gets one panel: target surface in grey with the knuckle footprint in
pale cyan and the six hotspots in orange, binder as a cartoon.

Run:  conda activate esm && python scripts/03c_render_designs.py [N]
      (N = how many top designs to render, default: all shortlisted in triage.tsv)
"""

import csv
import sys
from pathlib import Path

from pymol import cmd

ROOT = Path(__file__).resolve().parent.parent
OUTDIR = ROOT / "rfdiffusion" / "outputs"
TRIAGE = OUTDIR / "triage.tsv"
TARGET_FULL = ROOT / "data" / "prepared" / "myostatin_target.pdb"
FIGDIR = ROOT / "analysis" / "step3_designs"
SESSION = ROOT / "analysis" / "pymol_sessions" / "step3_shortlist.pse"

HOTSPOTS = [33, 34, 85, 87, 93, 95]
FOOTPRINT = [25, 33, 34, 35, 36, 37, 38, 39, 80, 81, 82, 83, 84, 85, 87, 91, 93,
             95, 97, 102, 104]


def main():
    if not TRIAGE.exists():
        raise SystemExit("Run scripts/03b_triage_backbones.py first.")
    with TRIAGE.open() as fh:
        rows = [r for r in csv.DictReader(fh, delimiter="\t")
                if r["shortlisted"] == "True"]
    if len(sys.argv) > 1:
        rows = rows[:int(sys.argv[1])]
    if not rows:
        raise SystemExit("No shortlisted designs in triage.tsv.")

    FIGDIR.mkdir(parents=True, exist_ok=True)
    cmd.feedback("disable", "all", "everything")
    cmd.bg_color("white")
    cmd.set("ray_opaque_background", 1)
    cmd.set("antialias", 2)
    cmd.set("cartoon_transparency", 0.0)

    cmd.delete("all")
    cmd.load(str(TARGET_FULL), "target")
    cmd.hide("everything")
    cmd.show("surface", "target")
    cmd.color("grey80", "target")
    cmd.color("palecyan", "target and resi " + "+".join(map(str, FOOTPRINT)))
    cmd.color("tv_orange", "target and resi " + "+".join(map(str, HOTSPOTS)))

    for i, r in enumerate(rows):
        name = r["design"]
        cmd.load(str(OUTDIR / f"{name}.pdb"), f"raw_{name}")
        # align the design's target copy onto our full-atom target, then keep only
        # the binder - so every panel shares one target in one orientation
        cmd.align(f"raw_{name} and chain A and name N+CA+C+O",
                  "target and name N+CA+C+O", cycles=0)
        cmd.create(name, f"raw_{name} and chain B")
        cmd.delete(f"raw_{name}")
        cmd.show("cartoon", name)
        cmd.color("marine", name)
        cmd.disable(name)

    # one shared view, oriented on the epitope
    cmd.orient("target and resi " + "+".join(map(str, HOTSPOTS)))
    cmd.turn("x", -15)
    cmd.zoom("target", 4)

    for r in rows:
        name = r["design"]
        cmd.enable(name)
        png = FIGDIR / f"{name}.png"
        cmd.png(str(png), width=1200, height=900, dpi=150, ray=1)
        cmd.disable(name)
        print(f"  {png.relative_to(ROOT)}  "
              f"({r['hotspots_hit']}/6 hotspots, {float(r['dSASA']):.0f} A^2, "
              f"helix {float(r['helix_frac']):.0%})")

    for r in rows:
        cmd.enable(r["design"])
    SESSION.parent.mkdir(parents=True, exist_ok=True)
    cmd.save(str(SESSION))
    print(f"\nWrote {len(rows)} panels to {FIGDIR.relative_to(ROOT)}")
    print(f"Wrote {SESSION.relative_to(ROOT)} - open it and toggle designs "
          "in the object panel")


if __name__ == "__main__":
    main()
