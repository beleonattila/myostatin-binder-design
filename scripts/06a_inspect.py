#!/usr/bin/env python
"""Step 6a - open an interactive PyMOL session for the final visual inspection.

Loads the four things you need on screen to settle the Step 6 ranking question:

  target      full-atom myostatin (5JI1 chain A), knuckle footprint pale cyan,
              the six RFdiffusion hotspots orange with sidechains shown
  design_12   RFdiffusion backbone that WON on designability (8/8 sequences refold)
  design_5    RFdiffusion backbone that WON on interface area (469 A^2, 12 contacts)
  esm_12_s4   best ESMFold prediction of all 64 - 0.40 A to its parent backbone
  esm_5_s5    the counter-example: pLDDT 90 and structurally wrong

Both RFdiffusion backbones are loaded because Step 3 and Step 5 disagree about
which one is best, and that disagreement is the decision this session is for.

The ESMFold predictions are superposed with cealign, NOT align: the RFdiffusion
binder is poly-glycine, so a sequence-anchored alignment matches ~4 atoms and
silently produces a garbage overlay.

Predictions are coloured by pLDDT (red = low confidence, green = high). Note that
esm_5_s5 is almost entirely green - high confidence is not correctness.

Run:  conda activate esm && pymol scripts/06a_inspect.py
"""

from pathlib import Path

from pymol import cmd

def find_root():
    """Locate the repo root.

    Not Path(__file__): PyMOL runs a .py argument with __file__ bound to its own
    pymol/__init__.py, so the usual idiom silently points into site-packages.
    Walk up from the working directory to a marker instead.
    """
    for d in [Path.cwd(), *Path.cwd().parents]:
        if (d / "CONTEXT.md").exists() and (d / "scripts").is_dir():
            return d
    raise SystemExit("Run this from inside the project (CONTEXT.md not found "
                     f"at or above {Path.cwd()}).")


ROOT = find_root()
TARGET = ROOT / "data" / "prepared" / "myostatin_target.pdb"
RFDIR = ROOT / "rfdiffusion" / "outputs"
ESMDIR = ROOT / "esm_validation" / "predicted_structures"

HOTSPOTS = [33, 34, 85, 87, 93, 95]
FOOTPRINT = [25, 33, 34, 35, 36, 37, 38, 39, 80, 81, 82, 83, 84, 85, 87, 91, 93,
             95, 97, 102, 104]

# (design, colour, esmfold sample to overlay, colour of that overlay's label)
PAIRS = [
    ("design_12", "marine", "design_12_s4"),
    ("design_5", "salmon", "design_5_s5"),
]

sele = lambda nums: "resi " + "+".join(map(str, nums))


def load_binder(design, colour):
    """Load an RFdiffusion output, move it into the target frame, keep chain B.

    Chain A of the output carries the real myostatin sequence (backbone atoms
    only), so a sequence-aware align is safe here - unlike on the binder.
    """
    raw = f"raw_{design}"
    cmd.load(str(RFDIR / f"{design}.pdb"), raw)
    cmd.align(f"{raw} and chain A and name N+CA+C+O",
              "target and name N+CA+C+O", cycles=0)
    cmd.create(design, f"{raw} and chain B")
    cmd.delete(raw)
    cmd.show("cartoon", design)
    cmd.color(colour, design)


def load_prediction(name, parent):
    """Load an ESMFold prediction and superpose it on its parent backbone."""
    cmd.load(str(ESMDIR / f"{name}.pdb"), name)
    rms = cmd.cealign(parent, name)["RMSD"]
    cmd.hide("everything", name)
    cmd.show("cartoon", name)
    # B-factors are pLDDT. The ESM Atlas API emits 0-1; local ESMFold emits
    # 0-100. Detect rather than assume, as scripts/05_esmfold.py does.
    bfac = []
    cmd.iterate(f"{name} and name CA", "bfac.append(b)", space={"bfac": bfac})
    hi = 1.0 if max(bfac) <= 1.0 else 100.0
    cmd.spectrum("b", "red_yellow_green", name, minimum=0.5 * hi, maximum=0.9 * hi)
    return rms, 100.0 * sum(bfac) / len(bfac) / hi


def main():
    cmd.delete("all")
    cmd.bg_color("white")
    cmd.set("ray_opaque_background", 1)
    cmd.set("antialias", 2)
    cmd.set("transparency", 0.25)
    cmd.set("cartoon_transparency", 0.0)

    cmd.load(str(TARGET), "target")
    cmd.hide("everything")
    cmd.show("surface", "target")
    cmd.color("grey80", "target")
    cmd.color("palecyan", f"target and {sele(FOOTPRINT)}")
    cmd.color("tv_orange", f"target and {sele(HOTSPOTS)}")
    cmd.show("sticks", f"target and {sele(HOTSPOTS)} and not (name C+N+O)")
    cmd.color("orange", f"target and {sele(HOTSPOTS)} and elem C")
    cmd.set("stick_radius", 0.18)

    print("\n" + "=" * 68)
    print("STEP 6 VISUAL INSPECTION")
    print("=" * 68)
    for design, colour, pred in PAIRS:
        load_binder(design, colour)
        rms, plddt = load_prediction(pred, design)
        print(f"  {design:<10} {colour:<7} + {pred:<13} "
              f"cealign {rms:4.2f} A, mean pLDDT {plddt:.1f}")

    cmd.orient(f"target and {sele(HOTSPOTS)}")
    cmd.turn("x", -15)
    cmd.zoom("target", 4)

    # Named scenes - recall with F1/F2/F3, or the "scene" menu.
    cmd.disable("design_5")
    cmd.disable("design_5_s5")
    cmd.disable("design_12_s4")
    cmd.scene("F1", "store", "design_12 alone on the epitope")
    cmd.enable("design_12_s4")
    cmd.scene("F2", "store", "design_12 + its 0.40 A refold (the designable one)")
    cmd.disable("design_12")
    cmd.disable("design_12_s4")
    cmd.enable("design_5")
    cmd.scene("F3", "store", "design_5 alone (biggest interface, 469 A^2)")
    cmd.enable("design_5_s5")
    cmd.scene("F4", "store", "design_5 + refold: hairpin predicted as one helix")

    cmd.scene("F1", "recall")

    print("-" * 68)
    print("  target   grey surface | palecyan = ActRIIB footprint | orange = hotspots")
    print("  predictions coloured by pLDDT: red 50 -> green 90")
    print("\n  F1  design_12 alone            F3  design_5 alone")
    print("  F2  design_12 + refold (0.40 A) F4  design_5 + refold (the failure)")
    print("=" * 68 + "\n")


main()
