# Step 1 · Target preparation

**Goal:** turn the raw crystal structure into a single, clean myostatin chain
that RFdiffusion can use as the binding target.

**Environment:** none required for PyMOL; Biopython path can use the `esm` env.

## Why 3HH2

PDB **3HH2** is the myostatin:follistatin-288 complex (Cash et al., *EMBO J*
2009; 2.15 Å). Chains **A, B** are the myostatin growth-factor dimer; **C, D** are
follistatin (an antagonist — *not* a receptor; we remove it). We keep **one
myostatin monomer (chain A)** because the knuckle epitope is entirely within one
chain, and a ~109-residue target keeps us inside the 6 GB VRAM budget.

## Procedure (PyMOL)

```python
fetch 3hh2, async=0
util.cbc                      # color by chain; confirm A,B = myostatin, C,D = follistatin

create target, (3hh2 and chain A and polymer.protein)
remove solvent
remove not polymer            # drop HETATM (waters, sulfate/heparin mimics)
remove not alt ''+A           # keep altloc A only
alter target, alt=''
save data/prepared/myostatin_target.pdb, target
```

Biopython equivalent: select `chain A`, keep only `ATOM` records, drop
`HETATM`/waters, collapse altlocs to the highest-occupancy conformer.

## Verify before moving on

- Only chain A, only protein `ATOM` records remain (no follistatin, no HETATM).
- **Record the resolved residue range** (look for gaps in numbering). A gap inside
  the fingers would compromise the knuckle. This range — *not* a hard-coded
  `1–109` — is what goes into the RFdiffusion contig string.
- Confirm mature numbering starts at **Asp1 (D1)**; Step 2 hotspot numbers assume
  this scheme.
- Optional quality gate: don't design against Clashscore > 20 or Ramachandran
  outliers > 1.5 % without repair (`pdbfixer`). 3HH2 at 2.15 Å is fine.

→ Continue to [Step 2 · Hotspots](02-hotspots.md).
