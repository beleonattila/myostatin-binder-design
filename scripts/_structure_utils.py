"""Shared structure handling for the RFdiffusion output files.

This module exists because the same mistake was made twice: RFdiffusion writes
BACKBONE ONLY - N, CA, C, O, no CB - for both the binder and the target. Measuring
an interface on those files directly finds almost nothing, because the 4-8 A gap
between backbones is exactly the space sidechains would occupy. Any script that
asks "what does the binder touch?" must go through `load_design()` here rather
than loading design_N.pdb and selecting on it.
"""

import numpy as np
from pymol import cmd

# vdW radius of carbon. PyMOL creates pseudoatoms with vdw=1.0 no matter what
# `elem` you pass, which silently shrinks every SASA they take part in (~35% of
# the buried area, measured against real CB atoms).
CARBON_VDW = 1.7


def add_virtual_cb(obj):
    """Build CB from N/CA/C with ideal geometry (trRosetta formula).

    Validated against real CB atoms in 6MAC: mean deviation 0.040 A, max 0.218 A.
    Every residue gets one - these backbones carry no sequence, so this is a probe
    for "which way would a sidechain point", not a claim about identity.
    """
    coords = {}
    for name in ("N", "CA", "C"):
        for atom in cmd.get_model(f"{obj} and name {name}").atom:
            coords.setdefault((atom.chain, int(atom.resi)), {})[name] = \
                np.array(atom.coord)

    made = 0
    for (chain, resi), d in sorted(coords.items()):
        if len(d) != 3:
            continue
        b = d["CA"] - d["N"]
        c = d["C"] - d["CA"]
        a = np.cross(b, c)
        cb = -0.58273431 * a + 0.56802827 * b - 0.54067466 * c + d["CA"]
        cmd.pseudoatom(obj, name="CB", chain=chain, resi=str(resi),
                       elem="C", pos=list(map(float, cb)), state=1)
        made += 1
    cmd.alter(f"{obj} and name CB", f"vdw={CARBON_VDW}")
    cmd.rebuild(obj)
    cmd.sort(obj)
    return made


def load_design(design_pdb, target_full_pdb,
                target_obj="target", binder_obj="binder"):
    """Load one RFdiffusion output in a form that can actually be measured.

    The target is rigid during diffusion (motif RMSD ~0.13 A), so its real
    sidechains are recovered by superposing the prepared full-atom target onto the
    output's chain A. The binder keeps backbone + virtual CB - its real sidechains
    are ProteinMPNN's job, so any buried area computed from this is a LOWER BOUND.

    Returns the alignment RMSD; anything above ~0.5 A means the assumption of a
    rigid target failed and the measurements should not be trusted.
    """
    cmd.delete("all")
    cmd.load(str(design_pdb), "_raw")
    cmd.create(binder_obj, "_raw and chain B")
    add_virtual_cb(binder_obj)

    cmd.load(str(target_full_pdb), target_obj)
    rms = cmd.align(f"{target_obj} and name N+CA+C+O",
                    "_raw and chain A and name N+CA+C+O", cycles=0)[0]
    cmd.delete("_raw")
    return rms


def contacting_binder_positions(target_resis, cutoff=5.0,
                                target_obj="target", binder_obj="binder"):
    """1-based binder positions with any atom within `cutoff` of the given target residues."""
    sel = (f"byres ({binder_obj}) within {cutoff} of "
           f"({target_obj} and resi {'+'.join(map(str, target_resis))})")
    cmd.select("_contact", sel)
    out = []
    cmd.iterate("_contact and name CA", "out.append(int(resi))",
                space={"out": out, "int": int})
    cmd.delete("_contact")
    return sorted(set(out))
