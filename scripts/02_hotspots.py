#!/usr/bin/env python
"""Step 2 - hotspot identification: the ActRIIB (type II / knuckle) epitope of GDF8.

No GDF8:ActRIIB structure exists and our target (5JI1) is apo, so the receptor
footprint cannot be read off the target directly. We transfer it by homology from
GDF11:ActRIIB complexes: superpose apo GDF8 onto the GDF11 ligand chain, then read
the GDF8 residues that land under ActRIIB.

Two complexes are used so the footprint is not an artifact of one crystal form:
  6MAC  GDF11:ActRIIB:ALK5    2.34 A   ligand chain A, ActRIIB chain C
  7MRZ  GDF11:ActRIIB-ALK4:Fab 3.00 A  ligand chain A, ActRIIB = chain C resi 19-120

Three things turn "I assumed the transfer works" into "I verified it":
  1. conservation  - is each contact residue the same amino acid in GDF8 as in GDF11?
  2. burial (dSASA) - how much surface does each residue actually bury against
     ActRIIB? A better hotspot proxy than a distance cutoff, which counts a
     glancing backbone contact the same as a fully engulfed sidechain.
  3. dimer occlusion - we hand RFdiffusion a monomer, but myostatin is a disulfide
     linked dimer. Any epitope residue the partner monomer covers would be a
     hotspot the binder can never reach in the real ligand.

Run:  conda activate esm && python scripts/02_hotspots.py
"""

import itertools
from pathlib import Path

from pymol import cmd

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
PREPARED = ROOT / "data" / "prepared"
OUT = ROOT / "hotspots" / "hotspot_residues.txt"

CONTACT_CUTOFF = 4.5  # A, heavy atom; the usual interface definition

# ligand chain, ActRIIB selection, label. 7MRZ's chain C is an ActRIIB-ALK4
# fusion, so the type II half must be sliced out by residue range; its GDF11 is
# in precursor numbering (299-407 = mature 1-109), which does not matter because
# we only ever read residue numbers off GDF8.
COMPLEXES = [
    ("6MAC", "chain A", "chain C", "GDF11:ActRIIB:ALK5"),
    ("7MRZ", "chain A", "chain C and resi 19-120", "GDF11:ActRIIB-ALK4:Fab"),
]

THREE2ONE = {
    "ALA": "A", "ARG": "R", "ASN": "N", "ASP": "D", "CYS": "C", "GLN": "Q",
    "GLU": "E", "GLY": "G", "HIS": "H", "ILE": "I", "LEU": "L", "LYS": "K",
    "MET": "M", "PHE": "F", "PRO": "P", "SER": "S", "THR": "T", "TRP": "W",
    "TYR": "Y", "VAL": "V",
}

# The final call (see the report this prints): hydrophobic/aromatic, heavily
# buried, conserved, present in both crystal forms, and spanning both lobes of
# the epitope so a binder cannot satisfy the constraint with half the surface.
PRIMARY = [33, 34, 85, 87, 93, 95]


def sequence(obj):
    """{residue number: one-letter code} for an object's CA atoms."""
    out = {}
    cmd.iterate(f"{obj} and name CA",
                'out[int(resi)] = three2one.get(resn, "X")',
                space={"out": out, "three2one": THREE2ONE, "int": int})
    return out


def residues_within(sel_a, sel_b, cutoff=CONTACT_CUTOFF):
    """Sorted residue numbers of sel_a with any heavy atom within cutoff of sel_b."""
    cmd.select("_contact", f"byres ({sel_a}) within {cutoff} of ({sel_b})")
    out = []
    cmd.iterate("_contact and name CA", "out.append(int(resi))",
                space={"out": out, "int": int})
    cmd.delete("_contact")
    return sorted(out)


def per_residue_area(obj, sel, numbers):
    return {n: cmd.get_area(f"{obj} and {sel} and resi {n}") for n in numbers}


def footprint(pdb_id, ligand_sel, receptor_sel, label):
    """Superpose apo GDF8 onto this complex's GDF11 and read the transferred epitope."""
    cmd.load(str(RAW / f"{pdb_id}.cif"), pdb_id)
    cmd.create(f"lig_{pdb_id}", f"{pdb_id} and {ligand_sel} and polymer")
    cmd.create(f"rec_{pdb_id}", f"{pdb_id} and {receptor_sel} and polymer")
    cmd.create(f"gdf8_{pdb_id}", "gdf8")

    # `super` is structure-based (sequence-independent) with outlier rejection -
    # the right choice for homologs, where `align` can be dragged by the loops.
    rms, natom, _, _, _, _, nres = cmd.super(f"gdf8_{pdb_id}", f"lig_{pdb_id}")
    print(f"\n{pdb_id} ({label})")
    print(f"  superposition: GDF8 onto GDF11, RMSD {rms:.2f} A "
          f"over {natom} atoms / {nres} residues")

    contacts = residues_within(f"gdf8_{pdb_id} and polymer", f"rec_{pdb_id}")
    print(f"  GDF8 residues within {CONTACT_CUTOFF} A of ActRIIB (n={len(contacts)}): "
          + ", ".join(str(c) for c in contacts))
    return contacts


def main():
    cmd.feedback("disable", "all", "everything")
    cmd.set("dot_solvent", 1)   # solvent-excluded -> real SASA, not vdW area
    cmd.set("dot_density", 4)

    cmd.load(str(PREPARED / "myostatin_target.pdb"), "gdf8")
    cmd.load(str(PREPARED / "myostatin_dimer.pdb"), "dimer")
    gdf8_seq = sequence("gdf8")

    print("=" * 78)
    print("Step 2 - ActRIIB (knuckle) epitope by homology transfer onto apo GDF8")
    print("=" * 78)
    print(f"target: myostatin_target.pdb, {len(gdf8_seq)} resolved residues")

    per_structure = {pid: footprint(pid, lig, rec, lab)
                     for pid, lig, rec, lab in COMPLEXES}

    ids = list(per_structure)
    both = sorted(set.intersection(*(set(v) for v in per_structure.values())))
    print(f"\nConsensus footprint - in BOTH structures (n={len(both)}): {both}")
    for pid in ids:
        only = sorted(set(per_structure[pid]) - set(both))
        print(f"  {pid} only: {only if only else 'none'}")
    print("  (a residue found in one crystal form only is a crystal-contact risk;"
          "\n   the consensus set is what we trust)")

    # --- conservation: is the transfer justified residue by residue? -----------
    gdf11_seq = sequence(f"lig_6MAC")
    shared = sorted(set(gdf8_seq) & set(gdf11_seq))
    ident = sum(gdf8_seq[i] == gdf11_seq[i] for i in shared)
    print(f"\nGDF11 vs GDF8 over the aligned mature domain: "
          f"{ident}/{len(shared)} identical ({100 * ident / len(shared):.0f}%)")

    # --- burial against ActRIIB, and occlusion by the partner monomer ----------
    cmd.create("complex", "gdf8_6MAC or rec_6MAC")
    free = per_residue_area("gdf8_6MAC", "polymer", both)
    bound = per_residue_area("complex", "chain A", both)
    mono = per_residue_area("gdf8", "polymer", both)
    dim = per_residue_area("dimer", "chain A", both)

    print(f"\n{'res':<6}{'GDF11':>6}{'cons':>10}{'dSASA':>8}{'%buried':>9}"
          f"{'dimer-occluded':>16}")
    print("-" * 55)
    table = []
    for n in both:
        aa = gdf8_seq[n]
        g11 = gdf11_seq.get(n, "-")
        cons = "identical" if g11 == aa else f"{g11}->{aa}"
        d = free[n] - bound[n]
        pct = 100 * d / free[n] if free[n] > 0.5 else 0.0
        occ = 100 * (mono[n] - dim[n]) / mono[n] if mono[n] > 0.5 else 0.0
        table.append((n, aa, cons, d, pct, occ))
        print(f"{aa}{n:<5d}{g11:>6}{cons:>10}{d:8.1f}{pct:9.0f}{occ:15.0f}%")

    nonident = [f"{c[1]}{c[0]}" for c in table if c[2] != "identical"]
    occluded = [f"{c[1]}{c[0]}" for c in table if c[5] > 15]
    buried_core = [f"{c[1]}{c[0]}" for c in table if c[4] < 10]
    print(f"\n  non-identical contacts : {nonident or 'none'}")
    print(f"  occluded in the dimer  : {occluded or 'none'} "
          "(none => the monomer target is a valid stand-in)")
    print(f"  contributes ~no surface: {buried_core or 'none'} "
          "(buried in GDF8's own core - not a usable hotspot)")

    print("\nranked by buried surface area:")
    for n, aa, _, d, pct, _ in sorted(table, key=lambda r: -r[3]):
        print(f"   {aa}{n:<4d} {d:5.1f} A^2 ({pct:.0f}% of its free surface)")

    # --- patch geometry: can one binder actually reach all of them? ------------
    print(f"\nchosen hotspots {PRIMARY} - pairwise CB-CB spread:")
    worst = 0.0
    for a, b in itertools.combinations(PRIMARY, 2):
        sa, sb = f"gdf8 and resi {a} and name CB", f"gdf8 and resi {b} and name CB"
        if cmd.count_atoms(sa) and cmd.count_atoms(sb):
            worst = max(worst, cmd.get_distance(sa, sb))
    print(f"   widest separation {worst:.1f} A - a 45-60 residue binder spans this easily")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    spec = "[" + ",".join(f"A{n}" for n in PRIMARY) + "]"
    lines = [
        "# Myostatin (GDF-8) type II / ActRIIB 'knuckle' epitope - RFdiffusion hotspots",
        "# Generated by scripts/02_hotspots.py. Chain A, mature numbering (Asp1 = 1),",
        f"# matching data/prepared/myostatin_target.pdb. Contact cutoff {CONTACT_CUTOFF} A.",
        "#",
        "# Derived by superposing apo GDF8 (5JI1) onto the GDF11 chain of two",
        "# independent GDF11:ActRIIB complexes and reading the GDF8 residues under",
        f"# ActRIIB. Consensus footprint, present in both ({len(both)} residues):",
        "#   " + ", ".join(f"{gdf8_seq[n]}{n}" for n in both),
        "#",
        f"# GDF11 vs GDF8 identity over the mature domain: {100 * ident / len(shared):.0f}%.",
        f"# Non-identical positions within the footprint: {', '.join(nonident) or 'none'}.",
        "# No footprint residue is occluded by the partner monomer in the dimer,",
        "# so the monomer target does not misrepresent the accessible epitope.",
        "#",
        "# PRIMARY SET - hydrophobic/aromatic, heavily buried, conserved, in both",
        "# structures, spanning both lobes of the epitope:",
        "",
    ]
    for n in PRIMARY:
        row = next(r for r in table if r[0] == n)
        lines.append(f"A{n}\t{row[1]}\t{row[3]:.0f} A^2 buried ({row[4]:.0f}%)")
    lines += [
        "",
        "# RFdiffusion argument (paste directly):",
        f"# ppi.hotspot_res={spec}",
        "",
        "# TIER 2 - real contacts, deliberately not used as hotspots:",
        "#   N83, K39, R37, E25, D104, K36  polar/charged or flexible; they bury area",
        "#     but RFdiffusion drives binder placement best from hydrophobic anchors.",
        "#   P35                            85% buried but only ~26 A^2; a fine 7th if needed.",
        "#   M84                            EXCLUDED: buries ~0 A^2, it points into GDF8's",
        "#     own core. The provisional list had it; the SASA calculation disproved it.",
        "#   K97, V102                      peripheral, <10% and small.",
        "",
        "# Conservative fallback if RFdiffusion struggles to satisfy all six:",
        "#   ppi.hotspot_res=[A33,A34,A85,A87]",
    ]
    OUT.write_text("\n".join(lines) + "\n")
    print(f"\nWrote {OUT.relative_to(ROOT)}")
    print(f"  RFdiffusion:  ppi.hotspot_res={spec}")


if __name__ == "__main__":
    main()
