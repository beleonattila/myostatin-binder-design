#!/usr/bin/env python
"""Step 6c - render the selected panel and write each design as a complex.

Two deliverables for results/top_designs/:

  complexes/<name>_complex.pdb   the ESMFold prediction of the binder, placed
                                 on the full-atom target. A binder PDB on its
                                 own is not the result; the complex is.
  figures/<name>.png             one panel each, plus panel_overview.png with
                                 all five on the same target in one view.

The prediction is placed by cealign onto its parent RFdiffusion backbone (which
is already in the target's frame), NOT by align: the backbone is poly-glycine,
so a sequence-anchored alignment matches a handful of atoms. Same trap as
Steps 3 and 5.

Reads the selection from results/top_designs/panel.fasta, so it always renders
whatever 06_rank.py last chose.

Run:  conda activate esm && pymol -cq scripts/06c_render_top.py
or:   make rank
"""

from pathlib import Path

from pymol import cmd


def find_root():
    """PyMOL's execfile leaves __file__ pointing into site-packages, so find
    the project by walking up from the cwd."""
    for c in [Path.cwd(), *Path.cwd().parents]:
        if (c / "Makefile").exists() and (c / "scripts").is_dir():
            return c
    raise SystemExit("run this from inside the project (no Makefile found above cwd)")


ROOT = find_root()
TARGET_FULL = ROOT / "data" / "prepared" / "myostatin_target.pdb"
DESIGNS = ROOT / "rfdiffusion" / "outputs"
PREDS = ROOT / "esm_validation" / "predicted_structures"
PANEL = ROOT / "results" / "top_designs"
FIGS = PANEL / "figures"
CPLX = PANEL / "complexes"
# sessions live with the other PyMOL sessions, which the repo does not track
SESSION = ROOT / "analysis" / "pymol_sessions" / "step6_panel.pse"

HOTSPOTS = [33, 34, 85, 87, 93, 95]
FOOTPRINT = [25, 33, 34, 35, 36, 37, 38, 39, 80, 81, 82, 83, 84, 85, 87, 91, 93,
             95, 97, 102, 104]
HOT_SEL = "+".join(map(str, HOTSPOTS))
FOOT_SEL = "+".join(map(str, FOOTPRINT))

# One colour per panel member for the overview, in rank order. None of these
# may be tv_orange or palecyan: those belong to the hotspots and the footprint,
# and a binder sharing the epitope's colour makes the figure unreadable.
COLOURS = ["marine", "tv_green", "violetpurple", "hotpink", "firebrick"]
SOLO_COLOUR = "marine"   # single-design panels: only binder-vs-target matters


def read_panel():
    if not (PANEL / "panel.fasta").exists():
        raise SystemExit("run scripts/06_rank.py first (no panel.fasta)")
    names = []
    for line in (PANEL / "panel.fasta").read_text().splitlines():
        if line.startswith(">"):
            names.append(line[1:].split()[0])
    return names


def setup():
    cmd.feedback("disable", "all", "everything")
    cmd.bg_color("white")
    cmd.set("ray_opaque_background", 1)
    cmd.set("antialias", 2)
    cmd.set("surface_quality", 1)
    cmd.set("transparency", 0.0)


def load_target():
    cmd.load(str(TARGET_FULL), "target")
    cmd.hide("everything", "target")
    cmd.show("surface", "target")
    cmd.color("grey80", "target")
    cmd.color("palecyan", f"target and resi {FOOT_SEL}")
    cmd.color("tv_orange", f"target and resi {HOT_SEL}")


def place(name):
    """Load one prediction and put it in the target's frame. Returns the object
    name of the placed prediction."""
    backbone = name.rsplit("_s", 1)[0]
    raw, bb, pred = f"raw_{name}", f"bb_{name}", f"pred_{name}"

    cmd.load(str(DESIGNS / f"{backbone}.pdb"), raw)
    cmd.align(f"{raw} and chain A and name N+CA+C+O",
              "target and name N+CA+C+O", cycles=0)
    cmd.create(bb, f"{raw} and chain B")
    cmd.delete(raw)

    cmd.load(str(PREDS / f"{name}.pdb"), pred)
    res = cmd.cealign(bb, pred)          # structural, never sequence-anchored
    cmd.delete(bb)
    cmd.hide("everything", pred)
    cmd.show("cartoon", pred)
    print(f"  {name}: placed by cealign, {res['alignment_length']} res, "
          f"RMSD {res['RMSD']:.2f} A")
    return pred


def main():
    names = read_panel()
    FIGS.mkdir(parents=True, exist_ok=True)
    CPLX.mkdir(parents=True, exist_ok=True)

    setup()
    cmd.delete("all")
    load_target()
    placed = []
    for i, name in enumerate(names):
        obj = place(name)
        cmd.color(COLOURS[i % len(COLOURS)], obj)
        placed.append((name, obj))
        # the complex is the deliverable: binder as chain B on the real target
        cmd.alter(obj, "chain='B'")
        cmd.sort()
        cmd.create("cplx", f"target or {obj}")
        cmd.save(str(CPLX / f"{name}_complex.pdb"), "cplx")
        cmd.delete("cplx")

    # One shared view for every figure, so the panels are directly comparable.
    # Fit it with all five binders visible, not just the target: they sit on
    # one face, and zooming on the target alone throws them out of frame.
    cmd.orient(f"target and resi {HOT_SEL}")
    cmd.turn("x", -15)
    cmd.zoom("visible", 1)

    for name, obj in placed:
        for _, other in placed:
            cmd.disable(other)
        cmd.enable(obj)
        cmd.color(SOLO_COLOUR, obj)
        cmd.png(str(FIGS / f"{name}.png"), width=1200, height=900, dpi=150, ray=1)

    for i, (_, obj) in enumerate(placed):
        cmd.enable(obj)
        cmd.color(COLOURS[i % len(COLOURS)], obj)
    cmd.png(str(FIGS / "panel_overview.png"), width=1600, height=1200, dpi=150, ray=1)
    SESSION.parent.mkdir(parents=True, exist_ok=True)
    cmd.save(str(SESSION))

    print(f"\nwrote {len(placed)} complexes -> {CPLX.relative_to(ROOT)}/")
    print(f"wrote {len(placed) + 1} figures  -> {FIGS.relative_to(ROOT)}/")
    print(f"wrote session          -> {SESSION.relative_to(ROOT)}")


main()
