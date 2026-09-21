#!/usr/bin/env python
"""Step 6b - the knuckle epitope, colour-coded by what each region actually does.

06a colours the epitope the way the pipeline sees it: footprint vs hotspot, a
binary. That view cannot show *why* those six residues were chosen. This builds
one scene per question instead:

  F1 LOBES      the two-lobe architecture - cool = finger 1-2, warm = finger 3-4
  F2 BURIAL     per-residue dSASA against ActRIIB, white -> red heatmap
  F3 CHEMISTRY  hydrophobic core vs polar/charged rim
  F4 RECEPTOR   the real ActRIIB docked on, aromatic triad as sticks
  F5 TRP78      the one receptor residue that bridges both lobes
  F6 DESIGNS    design_12 and design_5 back on the epitope for comparison

Burial numbers are recomputed here from 6MAC rather than hardcoded, by the same
superposition scripts/02_hotspots.py uses, so the heatmap cannot drift from the
committed hotspot file.

Run:  conda activate esm && pymol scripts/06b_epitope_anatomy.py
      (or, inside a running PyMOL:  run scripts/06b_epitope_anatomy.py)
"""

from pathlib import Path

from pymol import cmd


def find_root():
    """PyMOL binds __file__ to its own __init__.py, so walk up from cwd."""
    for d in [Path.cwd(), *Path.cwd().parents]:
        if (d / "CONTEXT.md").exists() and (d / "scripts").is_dir():
            return d
    raise SystemExit(f"CONTEXT.md not found at or above {Path.cwd()}.")


ROOT = find_root()
TARGET = ROOT / "data" / "prepared" / "myostatin_target.pdb"
RFDIR = ROOT / "rfdiffusion" / "outputs"

# --- the epitope, split by what it does ------------------------------------
LOBE_A = [25, 33, 34, 35, 36, 37, 38, 39]              # finger 1-2 loop + strand
LOBE_B = [80, 81, 82, 83, 84, 85, 87, 91, 93, 95, 97, 102, 104]   # finger 3-4
HOT_A, HOT_B = [33, 34], [85, 87, 93, 95]
FOOTPRINT = LOBE_A + LOBE_B
MET84 = 84          # 4.5 A "contact" that buries 0.2 A^2 - the cutoff's failure

# ActRIIB aromatic triad (Thompson 2003), confirmed as partners in 6MAC
TRIAD = {60: "Tyr60", 78: "Trp78", 101: "Phe101"}
# what Trp78 touches - note it spans BOTH lobes
TRP78_CONTACTS = [34, 35, 83, 84, 85, 95]

CHEMISTRY = [
    ("hydrophobic", "orange",    [33, 34, 35, 81, 82, 84, 85, 93, 102]),
    ("aromatic",    "yellow",    [38, 87, 95]),
    ("polar",       "palegreen", [80, 83]),
    ("basic (+)",   "marine",    [36, 37, 39, 97]),
    ("acidic (-)",  "firebrick", [25, 91, 104]),
]

sele = lambda nums: "resi " + "+".join(map(str, nums))
side = lambda nums: f"({sele(nums)}) and not (name C+N+O)"   # sidechain + CA


def dock_receptor():
    """Bring 6MAC's ActRIIB into the target's frame.

    super() moves the whole object containing the mobile selection, so
    superposing 6MAC's GDF11 onto our GDF8 carries the receptor along with it.
    """
    cmd.load(str(ROOT / "data" / "raw" / "6MAC.cif"), "m6")
    rms = cmd.super("m6 and chain A and polymer", "target")
    cmd.create("actriib", "m6 and chain C and polymer")
    cmd.delete("m6")
    return rms[0]


def burial_into_bfactors():
    """Per-residue dSASA vs ActRIIB, written to B-factors for spectrum colouring."""
    cmd.set("dot_solvent", 1)
    cmd.set("dot_density", 4)
    cmd.create("_cplx", "target or actriib")
    cmd.alter("target", "b=0.0")
    areas = {}
    for r in FOOTPRINT:
        free = cmd.get_area(f"target and resi {r}")
        bound = cmd.get_area(f"_cplx and chain A and resi {r}")
        areas[r] = free - bound
        cmd.alter(f"target and resi {r}", f"b={areas[r]:.2f}")
    cmd.delete("_cplx")
    cmd.sort("target")
    return areas


def load_binder(design, colour):
    raw = f"raw_{design}"
    cmd.load(str(RFDIR / f"{design}.pdb"), raw)
    cmd.align(f"{raw} and chain A and name N+CA+C+O",
              "target and name N+CA+C+O", cycles=0)
    cmd.create(design, f"{raw} and chain B")
    cmd.delete(raw)
    cmd.hide("everything", design)
    cmd.show("cartoon", design)
    cmd.color(colour, design)
    cmd.disable(design)


def base_surface():
    """Reset to plain grey target surface, nothing else shown.

    Representations are hidden, not just disabled - otherwise a cartoon shown in
    one scene reappears in the next one and quietly hides what it is about.
    """
    cmd.hide("everything", "target")
    cmd.show("surface", "target")
    cmd.color("grey80", "target")
    cmd.set("transparency", 0.0)
    cmd.hide("everything", "actriib")
    cmd.disable("actriib")


def main():
    cmd.delete("all")
    cmd.bg_color("white")
    cmd.set("ray_opaque_background", 1)
    cmd.set("antialias", 2)
    cmd.set("stick_radius", 0.2)
    cmd.set("surface_quality", 1)
    cmd.set("spec_reflect", 0.1)

    cmd.load(str(TARGET), "target")
    rms = dock_receptor()
    areas = burial_into_bfactors()

    cmd.hide("everything")
    cmd.orient(f"target and {sele(HOT_A + HOT_B)}")
    cmd.turn("x", -15)
    cmd.zoom("target", 4)

    # ---- F1 LOBES ---------------------------------------------------------
    base_surface()
    cmd.color("lightblue", f"target and {sele(LOBE_A)}")
    cmd.color("wheat", f"target and {sele(LOBE_B)}")
    cmd.show("sticks", f"target and {side(HOT_A + HOT_B)}")
    cmd.color("density", f"target and {side(HOT_A)}")
    cmd.color("firebrick", f"target and {side(HOT_B)}")
    cmd.color("yellow", f"target and {side([MET84])}")
    cmd.show("sticks", f"target and {side([MET84])}")
    cmd.scene("F1", "store", "LOBES: blue=finger1-2, wheat=finger3-4, "
                             "sticks=hotspots, yellow=Met84")

    # ---- F2 BURIAL --------------------------------------------------------
    base_surface()
    cmd.spectrum("b", "white_yellow_red", "target and b > 0", minimum=0,
                 maximum=80)
    cmd.show("sticks", f"target and {side(HOT_A + HOT_B + [MET84])}")
    cmd.scene("F2", "store", "BURIAL: dSASA vs ActRIIB, white 0 -> red 80 A^2")

    # ---- F3 CHEMISTRY -----------------------------------------------------
    base_surface()
    for _, colour, nums in CHEMISTRY:
        cmd.color(colour, f"target and {sele(nums)}")
    cmd.show("sticks", f"target and {side(FOOTPRINT)}")
    cmd.scene("F3", "store", "CHEMISTRY: orange/yellow apolar core, "
                             "blue/red charged rim")

    # ---- F4 RECEPTOR ------------------------------------------------------
    base_surface()
    cmd.color("lightblue", f"target and {sele(LOBE_A)}")
    cmd.color("wheat", f"target and {sele(LOBE_B)}")
    cmd.set("transparency", 0.45)
    cmd.enable("actriib")
    cmd.show("cartoon", "actriib")
    cmd.color("grey50", "actriib")
    cmd.set("cartoon_transparency", 0.55, "actriib")
    cmd.show("sticks", f"actriib and {side(list(TRIAD))}")
    cmd.set("stick_radius", 0.28, "actriib")
    cmd.color("magenta", f"actriib and {side([78])}")
    cmd.color("teal", f"actriib and {side([60, 101])}")
    cmd.scene("F4", "store", "RECEPTOR: ActRIIB docked, triad "
                             "Tyr60/Phe101 teal, Trp78 magenta")

    # ---- F5 TRP78 ---------------------------------------------------------
    base_surface()
    cmd.color("grey90", "target")
    cmd.color("lightblue", f"target and {sele([r for r in TRP78_CONTACTS if r in LOBE_A])}")
    cmd.color("wheat", f"target and {sele([r for r in TRP78_CONTACTS if r in LOBE_B])}")
    cmd.set("transparency", 0.35)
    cmd.show("sticks", f"target and {side(TRP78_CONTACTS)}")
    cmd.enable("actriib")
    # sticks ONLY - the receptor cartoon would sit straight over the cleft
    cmd.show("sticks", f"actriib and {side([78])}")
    cmd.color("magenta", f"actriib and {side([78])}")
    cmd.set("stick_radius", 0.28, "actriib")
    cmd.scene("F5", "store", "TRP78: the residue that bridges both lobes")

    # ---- F6 DESIGNS -------------------------------------------------------
    load_binder("design_12", "marine")
    load_binder("design_5", "salmon")
    base_surface()
    cmd.color("lightblue", f"target and {sele(LOBE_A)}")
    cmd.color("wheat", f"target and {sele(LOBE_B)}")
    cmd.show("sticks", f"target and {side(HOT_A + HOT_B)}")
    cmd.color("density", f"target and {side(HOT_A)}")
    cmd.color("firebrick", f"target and {side(HOT_B)}")
    cmd.enable("design_12")
    cmd.enable("design_5")
    cmd.scene("F6", "store", "DESIGNS: design_12 marine, design_5 salmon, "
                             "over the two lobes")

    cmd.scene("F1", "recall")

    w = 70
    print("\n" + "=" * w)
    print("KNUCKLE EPITOPE ANATOMY")
    print("=" * w)
    print(f"  ActRIIB docked from 6MAC, superposition {rms:.2f} A")
    print(f"  lobe A (finger 1-2): {LOBE_A}")
    print(f"  lobe B (finger 3-4): {LOBE_B}")
    print("-" * w)
    print(f"  {'residue':<9}{'dSASA':>7}   role")
    for r in sorted(areas, key=lambda x: -areas[x]):
        tag = "HOTSPOT" if r in HOT_A + HOT_B else ""
        if r == MET84:
            tag = "<- contact by distance, not by burial"
        print(f"  {r:<9}{areas[r]:7.1f}   {tag}")
    print("-" * w)
    print("  F1 lobes    F2 burial   F3 chemistry")
    print("  F4 receptor F5 Trp78    F6 designs")
    print("=" * w + "\n")


main()
