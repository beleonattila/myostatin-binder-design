# GDF8 (Myostatin)

**The design target.** The ligand whose receptor interaction your binder is meant to block.

| Field | Value |
|-------|-------|
| Names | GDF-8, myostatin, MSTN |
| Human UniProt | O14793 (GDF8_HUMAN) |
| Mouse UniProt | O08689 |
| Gene | MSTN, Gene ID 2660, chr 2q32.2 |
| Family | TGF-β superfamily → [see fold page](../concepts/TGF-beta-superfamily.md) |
| Mature domain | ~residues 267/268–375 of the precursor |
| Biological unit | Disulfide-linked homodimer |
| Receptors | Type II: [ActRIIB](ActRIIB.md) (primary), ActRIIA; Type I: ALK4/ALK5 |

---

## Biology in one paragraph

Myostatin is a secreted myokine and the strongest known negative regulator of skeletal muscle mass. Loss-of-function produces the "double-muscled" phenotype documented in cattle, mice, dogs, and at least one human. It is synthesised as an inactive precursor (pro-myostatin), proteolytically matured, and the active species is a covalent homodimer of the C-terminal growth-factor domain. Signalling proceeds by assembling a heterotetrameric receptor complex — two type II receptors (predominantly ActRIIB) and two type I receptors (ALK4/5) — which activates SMAD2/3 and represses the myogenic program. This is why myostatin inhibition is a durable therapeutic idea for muscle-wasting disease, and increasingly for metabolic disease, where the interest reaches beyond the GLP-1 axis.

---

## Structure you need to hold

Myostatin adopts the canonical TGF-β **cystine-knot growth factor fold** — read [TGF-β superfamily](../concepts/TGF-beta-superfamily.md) first if that phrase isn't automatic for you. The essentials for *this* project:

- The monomer is often described as a **hand**: two β-sheet "fingers" extending from a cystine-knot "palm", with a central α-helix (the "wrist").
- Two monomers assemble into a **butterfly-shaped dimer**, held together by an inter-chain disulfide and hydrophobic packing at the heel.
- **Two receptor-binding surfaces per monomer:**
  - **Type II ("knuckle") epitope** — convex, on the outer fingertips/knuckle, binds ActRIIB. **This is your target epitope.**
  - **Type I ("wrist") epitope** — concave, near the pre-helix loop and the dimer interface, binds ALK4/5.

Because the dimer is two-fold symmetric, there are **two** ActRIIB sites. A binder occupying one knuckle is already a partial competitive antagonist; occupying both would be ideal but is not required for a proof-of-concept design.

---

## The structural problem at the heart of this project

**There is no crystal structure of GDF8 bound to ActRIIB.** Every deposited GDF8 structure has the ligand either apo or bound to an *antagonist* (follistatin, FSTL3, GASP1, antibodies), not to its receptor. Consequences:

1. Your RFdiffusion **target** should be apo GDF8 so the knuckle epitope is unoccupied → use [5JI1](5JI1.md).
2. Your **hotspot residues** (which GDF8 atoms contact ActRIIB) cannot be read directly. You transfer them from the GDF11:ActRIIB complex ([6MAC](6MAC.md)), licensed by the ~90% mature-domain identity with [GDF11](GDF11.md).

This indirection is the intellectually interesting part of the project. Own it — do not paper over it.

---

## Key structures in the PDB

| PDB | Contents | Use here |
|-----|----------|----------|
| [5JI1](5JI1.md) | Apo GDF8, 2.25 Å | **RFdiffusion target** |
| [3HH2](3HH2.md) | GDF8:[follistatin-288](follistatin-288.md) | Reference / cross-check only |
| 3SEK | GDF8:FSTL3 (murine) | Alt. antagonist reference |
| 5F3B | Antibody-bound GDF8 | Epitope comparison |
| 6UMX | Pro-myostatin:Fab | Latency mechanism (not needed here) |

---

## Numbering warning

Different sources number GDF8 residues either by **full-length precursor** (1–375) or by **mature domain** (starting near residue 1 of the cleaved growth factor). A residue called "Met" at one number in a paper may be ~260 off from the same atom in a mature-domain PDB. **Before writing your hotspot file, confirm which scheme [5JI1](5JI1.md) uses** (mature domain) and convert everything into it. Getting this wrong silently points RFdiffusion at the wrong residues.

---

## Links

- Fold family: [TGF-β superfamily](../concepts/TGF-beta-superfamily.md)
- The receptor you compete with: [ActRIIB](ActRIIB.md)
- The proxy for hotspots: [GDF11](GDF11.md) → [6MAC](6MAC.md)
- Target structure: [5JI1](5JI1.md)
- Why not 3HH2: [3HH2](3HH2.md)
- What to do with it: [RFdiffusion](../methods/RFdiffusion.md)
