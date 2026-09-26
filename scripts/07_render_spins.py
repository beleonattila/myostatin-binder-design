#!/usr/bin/env python
"""Step 7a - render spinning-molecule PNG frame stacks for the dashboard.

Four scenes, one per pipeline stage, in the same colour conventions as
scripts/03c_render_designs.py (grey target surface, palecyan ActRIIB footprint,
tv_orange hotspots, marine binder) but on a dark background, because the
dashboard shows them on a dark plate in both light and dark themes.

  epitope    the prepared target with footprint + hotspots      (steps 1-2)
  design_5   the widest interface of the twenty                 (step 3)
  design_12  the most designable backbone                       (steps 3+5)
  refold     design_12_s4's ESMFold prediction on its backbone  (step 5)

Prerequisites: steps 1, 3 and 5 must have been run, i.e. data/prepared/,
rfdiffusion/outputs/ and esm_validation/predicted_structures/ are populated.
data/prepared/ and the predictions are git-ignored, so on a fresh clone run
scripts/01_prepare_target.py and scripts/05_esmfold.py first.

Run:  conda activate esm
      pymol -cq scripts/07_render_spins.py -- [outdir] [frames] [size]
or:   make dashboard
"""

import sys
from pathlib import Path

from pymol import cmd

def find_root():
    """Locate the project root.

    `__file__` is useless here: PyMOL runs this through its own execfile, which
    leaves __file__ pointing at pymol/__init__.py in site-packages. So look for
    the directory that actually holds this project, starting at the cwd.
    """
    for c in [Path.cwd(), *Path.cwd().parents]:
        if (c / "Makefile").exists() and (c / "scripts").is_dir():
            return c
    raise SystemExit("run this from inside the project (no Makefile found above cwd)")


ROOT = find_root()
TARGET_FULL = ROOT / "data" / "prepared" / "myostatin_target.pdb"
DESIGNS = ROOT / "rfdiffusion" / "outputs"
PREDS = ROOT / "esm_validation" / "predicted_structures"

HOTSPOTS = [33, 34, 85, 87, 93, 95]
FOOTPRINT = [25, 33, 34, 35, 36, 37, 38, 39, 80, 81, 82, 83, 84, 85, 87, 91, 93,
             95, 97, 102, 104]
HOT_SEL = "+".join(map(str, HOTSPOTS))
FOOT_SEL = "+".join(map(str, FOOTPRINT))

# near-black slate; must match --plate in the dashboard template
BG = [0.043, 0.055, 0.078]


def setup():
    cmd.feedback("disable", "all", "everything")
    cmd.set("bg_rgb", BG)
    cmd.set("ray_opaque_background", 1)
    cmd.set("antialias", 1)
    cmd.set("ray_shadows", 0)
    cmd.set("specular", 0.2)
    cmd.set("surface_quality", 0)
    cmd.set("cartoon_sampling", 8)
    cmd.set("ribbon_sampling", 4)
    cmd.set("two_sided_lighting", 1)
    cmd.set("ambient", 0.18)
    # orthoscopic + a deep slab so nothing clips as the scene turns edge-on
    cmd.set("orthoscopic", 1)
    cmd.set("field_of_view", 20)


def load_target(name="target"):
    cmd.load(str(TARGET_FULL), name)
    cmd.hide("everything", name)
    cmd.show("surface", name)
    cmd.color("grey70", name)
    cmd.color("palecyan", f"{name} and resi {FOOT_SEL}")
    cmd.color("tv_orange", f"{name} and resi {HOT_SEL}")


def load_binder(design):
    """Superpose the design's backbone-only target copy onto the full-atom
    target, then keep only its binder chain - same trick as 03c, so every
    scene shares one target in one orientation."""
    raw = f"raw_{design}"
    cmd.load(str(DESIGNS / f"{design}.pdb"), raw)
    cmd.align(f"{raw} and chain A and name N+CA+C+O",
              "target and name N+CA+C+O", cycles=0)
    cmd.create(design, f"{raw} and chain B")
    cmd.delete(raw)
    cmd.hide("everything", design)
    cmd.show("cartoon", design)
    cmd.color("marine", design)


def spin(outdir, tag, frames, size):
    """Write `frames` PNGs, one per equal step of a full 360 deg y rotation."""
    d = outdir / tag
    d.mkdir(parents=True, exist_ok=True)
    for f in d.glob("*.png"):
        f.unlink()
    cmd.clip("slab", 300)
    step = 360.0 / frames
    for i in range(frames):
        cmd.png(str(d / f"{i:03d}.png"), width=size, height=size, dpi=72, ray=1)
        cmd.turn("y", step)
    print(f"  {tag}: {frames} frames at {size}px -> {d.relative_to(ROOT)}")


def scene_epitope(outdir, frames, size):
    cmd.delete("all")
    load_target()
    cmd.orient("target")
    cmd.zoom("target", 1.5)
    spin(outdir, "epitope", frames, size)


def scene_complex(outdir, design, frames, size):
    cmd.delete("all")
    load_target()
    load_binder(design)
    cmd.orient(f"target or {design}")
    cmd.zoom(f"target or {design}", 1.5)
    spin(outdir, design, frames, size)


def scene_refold(outdir, frames, size):
    """ESMFold prediction over its parent RFdiffusion backbone.

    cealign, never align: the backbone is poly-glycine, so a sequence-anchored
    alignment matches a handful of atoms (see the Step 5 session log).
    """
    cmd.delete("all")
    cmd.load(str(DESIGNS / "design_12.pdb"), "raw")
    # NOT "backbone": that is a reserved PyMOL selection keyword, and an object
    # of that name is shadowed by it - cealign then silently aligns pred to
    # itself and the two objects sit side by side instead of superimposed.
    cmd.create("dsn12", "raw and chain B")
    cmd.delete("raw")
    cmd.load(str(PREDS / "design_12_s4.pdb"), "pred")
    res = cmd.cealign("dsn12", "pred")
    print(f"  refold cealign: {res['alignment_length']} res, "
          f"RMSD {res['RMSD']:.2f} A  (scores.tsv says 0.40)")
    cmd.hide("everything")
    cmd.show("cartoon", "dsn12")
    cmd.color("grey50", "dsn12")
    cmd.show("cartoon", "pred")
    cmd.color("tv_green", "pred")
    cmd.set("cartoon_transparency", 0.0)
    cmd.orient("dsn12")
    cmd.zoom("dsn12", 5.0)
    spin(outdir, "refold", frames, size)


def main():
    # PyMOL leaves its own flags and the script path in sys.argv, so only the
    # values after `--` are ours. No `--` means "use the defaults".
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    outdir = Path(args[0]) if args else ROOT / "analysis" / "dashboard" / "frames"
    if not outdir.is_absolute():
        outdir = ROOT / outdir
    frames = int(args[1]) if len(args) > 1 else 36
    size = int(args[2]) if len(args) > 2 else 340

    for p in (TARGET_FULL, DESIGNS / "design_12.pdb", PREDS / "design_12_s4.pdb"):
        if not p.exists():
            raise SystemExit(f"missing input: {p.relative_to(ROOT)} - see the "
                             "prerequisites in this script's docstring")

    outdir.mkdir(parents=True, exist_ok=True)
    setup()
    scene_epitope(outdir, frames, size)
    scene_complex(outdir, "design_5", frames, size)
    scene_complex(outdir, "design_12", frames, size)
    scene_refold(outdir, frames, size)
    print("done")


main()
