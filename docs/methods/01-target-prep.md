# Step 1 · Target preparation

**Goal:** turn the raw crystal structure into a single, clean myostatin chain
that RFdiffusion can use as the binding target.

**Environment:** none required for PyMOL; Biopython path can use the `esm` env.

## Why 5JI1 (apo GDF8)

PDB **5JI1** is **apo** myostatin — the mature growth-factor domain with **no
binding partner** (Walker et al., *BMC Biology* 2017, 15:19; 2.25 Å). Because
nothing is bound, the ActRIIB (knuckle) epitope is solvent-exposed and in its
unbound conformation — exactly the clean surface RFdiffusion expects. The knuckle
epitope lies entirely within one monomer, so a single ~100-residue chain keeps us
inside the 6 GB VRAM budget.

We deliberately avoid the older **3HH2** (myostatin:follistatin-288, 2009): its
epitope is occluded by follistatin, and its 2009-era validation (clashscore ~44,
~14 % sidechain outliers) makes interface geometry unreliable. 3HH2 is a fold
reference only — see `wiki/molecules/3HH2.md` for the full disqualification.

## Procedure (PyMOL)

```python
fetch 5ji1, async=0
util.cbc                      # color by chain; identify the GDF8 chain(s)

create target, (5ji1 and polymer.protein)   # apo GDF8 — no partner to strip
remove solvent
remove not polymer            # drop HETATM (waters, cryoprotectants, ions)
remove not alt ''+A           # keep altloc A only
alter target, alt=''
save data/prepared/myostatin_target.pdb, target
```

Decide **monomer vs dimer** deliberately: targeting one knuckle on the intact
dimer is the most physiological setup; an isolated monomer is simpler. Record the
choice.

Biopython equivalent: keep the GDF8 chain(s), keep only `ATOM` records, drop
`HETATM`/waters, collapse altlocs to the highest-occupancy conformer.

## Verify before moving on

- Only the GDF8 protein `ATOM` records remain (no HETATM, no waters).
- **Record the resolved residue range** (look for gaps in numbering). Apo-GDF8 has
  reported conformational flexibility, so **confirm the knuckle finger loops are
  actually resolved** — a gap there would compromise the epitope. This range —
  not a hard-coded length — is what goes into the RFdiffusion contig string.
- **Record which numbering scheme 5JI1 uses** (the deposited mature-domain
  fragment does *not* necessarily start at 1). Step 2 hotspots must be expressed
  in this same scheme before they reach RFdiffusion.
- Optional quality gate: don't design against Clashscore > 20 or Ramachandran
  outliers > 1.5 % without repair (`pdbfixer`). 5JI1 at 2.25 Å (2017, modern
  OneDep validation) is fine — check its RCSB validation report to confirm.

→ Continue to [Step 2 · Hotspots](02-hotspots.md).
