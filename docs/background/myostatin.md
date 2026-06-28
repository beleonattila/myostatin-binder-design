# Myostatin (GDF-8)

## What it is

Myostatin, also called **growth/differentiation factor 8 (GDF-8)**, is a secreted
signalling protein of the **TGF-β superfamily**. Its physiological role is to act
as a *negative* regulator of skeletal muscle mass — it tells muscle "stop
growing". Loss-of-function mutations produce the dramatic "double-muscling"
phenotype seen in Belgian Blue cattle, whippets, and rare human cases. That
phenotype is precisely why myostatin **inhibition** is a long-standing
therapeutic target for muscle-wasting (cachexia, sarcopenia, muscular dystrophy)
and metabolic disease.

## Biosynthesis and latency

Myostatin is made as a precursor with an N-terminal **prodomain** and a
C-terminal **mature growth-factor domain**. After cleavage, the prodomain
remains non-covalently bound, holding the ligand in a **latent** complex; further
proteolysis (e.g. by BMP-1/tolloid) releases the active mature dimer. The mature,
active species — the one that engages receptors — is what we design against.

## The fold: a TGF-β "hand"

The mature domain adopts the classic TGF-β **cystine-knot** fold, often described
as a hand:

- **Palm** — the cystine-knot core, three disulfides forming a knotted ring.
- **Fingers** — two long, curved β-strand pairs (the four-stranded β-sheet
  "fingers") extending from the palm. Their **convex outer face** is the
  receptor-binding knuckle (see [the epitope](epitope.md)).
- **Wrist** — an α-helix ("heel" helix) packed against the palm; at the dimer
  interface it forms the *type I* receptor site.

Two monomers associate into a covalent **dimer** (an inter-chain disulfide),
giving the butterfly-shaped growth factor. Each monomer presents its own knuckle,
so the dimer can engage two type II receptors.

## Why it's a clean design target

- **Extraordinary conservation** — myostatin is one of the most conserved
  proteins across mammals; mouse and human mature domains are essentially
  identical. That means a structure solved in mouse is a valid stand-in for the
  human target (verify the sequence match during prep).
- **Well-characterized interfaces** — decades of TGF-β structural work mean the
  type I (wrist) and type II (knuckle) sites are mapped, so we can target the
  receptor epitope rationally rather than blindly.

## Structure we use

| PDB | Contents | Role here |
|---|---|---|
| **3HH2** | Myostatin dimer (chains A, B) + follistatin-288 (C, D), 2.15 Å | Step 1 target — we extract one myostatin monomer (chain A). |
| **1NYS** | ActRIIB ectodomain : activin A complex | Step 2 template — defines the ActRIIB footprint we transfer onto myostatin. |

Note 3HH2 contains **no receptor** — follistatin is an antagonist, not a
receptor — which is exactly why we need 1NYS to locate the receptor epitope.
Continue to [TGF-β receptor logic](tgf-beta-receptors.md).
