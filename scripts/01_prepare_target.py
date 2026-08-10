#!/usr/bin/env python
"""Step 1 - target preparation: 5JI1 (apo GDF8) -> clean RFdiffusion target.

Reads the raw RCSB deposition and writes ATOM-only PDBs containing nothing but
the GDF8 polymer: waters and the MPD cryoprotectant are dropped, and alternate
conformers are collapsed to the highest-occupancy one (Biopython's
DisorderedAtom already selects on occupancy; we additionally blank the altloc
character so downstream tools never see a duplicate).

Two outputs, because the monomer/dimer choice is a real decision (see the
report this prints and CONTEXT.md):
  data/prepared/myostatin_target.pdb  - chain A only, the RFdiffusion target
  data/prepared/myostatin_dimer.pdb   - chains A+B, the physiological ligand

Run:  conda activate esm && python scripts/01_prepare_target.py
"""

from pathlib import Path

from Bio.PDB import PDBParser, PDBIO, Select
from Bio.PDB.Polypeptide import is_aa

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw" / "5JI1.pdb"
PREPARED = ROOT / "data" / "prepared"

TARGET_CHAIN = "A"  # fewer unresolved residues than B (14 vs 17)


class CleanProtein(Select):
    """Keep only standard amino-acid ATOM records from the requested chains."""

    def __init__(self, chains):
        self.chains = set(chains)

    def accept_chain(self, chain):
        return chain.id in self.chains

    def accept_residue(self, residue):
        # hetflag ' ' excludes waters (W) and ligands (H_MPD) in one test
        hetflag, _, _ = residue.id
        return hetflag == " " and is_aa(residue, standard=True)

    def accept_atom(self, atom):
        if atom.is_disordered():
            # DisorderedAtom exposes its highest-occupancy conformer; blank the
            # altloc so the written record is unambiguous.
            atom.set_altloc(" ")
        return True


def segments(numbers):
    """[1,2,3,7,8] -> [(1,3),(7,8)] - contiguous runs, i.e. the contig segments."""
    runs, start, prev = [], None, None
    for n in sorted(numbers):
        if start is None:
            start = prev = n
        elif n == prev + 1:
            prev = n
        else:
            runs.append((start, prev))
            start = prev = n
    if start is not None:
        runs.append((start, prev))
    return runs


def report(structure, chain_id):
    chain = structure[0][chain_id]
    resnums = [r.id[1] for r in chain if r.id[0] == " " and is_aa(r, standard=True)]
    runs = segments(resnums)
    print(f"  chain {chain_id}: {len(resnums)} residues resolved, "
          f"{len(runs)} segment(s): "
          + ", ".join(f"{a}-{b}" for a, b in runs))
    for (_, end), (start, _) in zip(runs, runs[1:]):
        print(f"    !! gap: {end + 1}-{start - 1} unresolved "
              f"({start - end - 1} residues)")
    return runs


def main():
    PREPARED.mkdir(parents=True, exist_ok=True)
    structure = PDBParser(QUIET=True).get_structure("5ji1", str(RAW))

    print(f"Input: {RAW.relative_to(ROOT)}")
    chains = [c.id for c in structure[0]]
    print(f"  chains present: {', '.join(chains)}")
    het = {}
    for res in structure[0].get_residues():
        flag = res.id[0]
        if flag != " ":
            het[res.get_resname()] = het.get(res.get_resname(), 0) + 1
    print(f"  non-polymer to strip: "
          + ", ".join(f"{k} x{v}" for k, v in sorted(het.items())))

    print("\nResolved ranges (these define the RFdiffusion contig):")
    for cid in chains:
        report(structure, cid)

    io = PDBIO()
    io.set_structure(structure)

    monomer = PREPARED / "myostatin_target.pdb"
    io.save(str(monomer), select=CleanProtein([TARGET_CHAIN]))
    dimer = PREPARED / "myostatin_dimer.pdb"
    io.save(str(dimer), select=CleanProtein(chains))

    print(f"\nWrote {monomer.relative_to(ROOT)} (chain {TARGET_CHAIN})")
    print(f"Wrote {dimer.relative_to(ROOT)} (chains {'+'.join(chains)})")


if __name__ == "__main__":
    main()
