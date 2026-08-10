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

## Procedure (the script that was actually run)

```bash
conda activate esm
curl -o data/raw/5JI1.pdb https://files.rcsb.org/download/5JI1.pdb
python scripts/01_prepare_target.py
```

`scripts/01_prepare_target.py` (Biopython) keeps chain A's standard-amino-acid
`ATOM` records, drops waters and the MPD cryoprotectant, collapses altlocs to the
highest-occupancy conformer, and prints the resolved-range report reproduced
below. It also writes the A+B dimer alongside, for comparison.

## Procedure (PyMOL equivalent)

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

## Results (run 2026-08-10)

```
chains present: A, B          non-polymer stripped: HOH x30, MPD x7
chain A: 95 residues resolved, 2 segments: 1-50, 65-109   (gap 51-64, 14 res)
chain B: 92 residues resolved, 2 segments: 1-48, 66-109   (gap 49-65, 17 res)
```

**Numbering.** `DBREF` maps PDB residues **1–109** to UniProt O08689 **268–376**:
5JI1 is already in **mature-domain numbering (Asp1 = residue 1)**, the same scheme
the hotspot list uses — no conversion is needed. Note the entry is **mouse** GDF8;
its mature domain is a 100 % exact match to human O14793 267–375 (verified by
alignment), so it is a valid stand-in.

**The gap is not at the epitope.** Residues 51–64 are the α-helix / "heel" — the
type I (wrist) site — 33–46 Å from the knuckle hotspot centroid. It was left
unmodelled: building a 14-residue loop de novo would be invented geometry.
**But it changes the contig** — chain A is two segments, so Step 3 must use
`A1-50/A65-109`, never `A1-109`.

**Monomer, decided on evidence.** Per-residue SASA for the hotspots is *identical*
in the monomer and in the dimer — chain B buries ~603 Å² of chain A, none of it at
the knuckle. The dimer would cost 109 extra residues of VRAM and buy nothing, so
`myostatin_target.pdb` is chain A alone.

**Epitope sanity check.** All 7 provisional hotspots are resolved and form one
compact patch (12.6 Å across; Ala34 and Leu85 are 5.0 Å apart despite being 51
apart in sequence). Caveat for Step 2: **Met84 is only 7 % solvent-exposed** and is
likely too buried to serve as a hotspot; the other six are 19–33 %.

→ Continue to [Step 2 · Hotspots](02-hotspots.md).
