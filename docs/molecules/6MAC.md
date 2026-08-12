# 6MAC — GDF11 : ActRIIB : ALK5 Ternary Complex

**The hotspot source.** The closest available crystallographic proxy for "myostatin bound to ActRIIB." You extract the type II interface here and transfer it to [GDF8](GDF8.md).

| Field | Value |
|-------|-------|
| Title | Ternary structure of GDF11 bound to ActRIIB-ECD and ALK5-ECD |
| Deposited | 2019 (Goebel et al., *PNAS* 116:15505) |
| Contents | [GDF11](GDF11.md) dimer + [ActRIIB](ActRIIB.md) ECD (type II) + ALK5 ECD (type I) |
| Method | X-ray diffraction |
| Why it exists here | No GDF8:ActRIIB structure exists; GDF11 is the ~90%-identical stand-in |

---

## What it shows

A complete activin-class signalling geometry: the GDF11 ligand dimer engaging **both** receptor types at once. The key findings relevant to you:

- Receptor positioning resembles the BMP class, with **no inter-receptor contacts** — type II (ActRIIB) and type I (ALK5) each contact the ligand independently.
- The **type I** interactions sit toward the ligand **fingertips** (this is where GDF8/GDF11 differ, and where potency differences arise — not your concern).
- The **type II (ActRIIB)** interactions define the knuckle epitope — **this is what you extract.**

Because there are no inter-receptor contacts, you can cleanly isolate the ActRIIB footprint without worrying about ALK5 geometry contaminating it.

---

## The transfer procedure (Module 3, the crux)

```text
Goal: GDF8 residues equivalent to the GDF11 residues that contact ActRIIB.

1. Load 6MAC in PyMOL.
2. Identify chains: GDF11 (ligand), ActRIIB ECD, ALK5 ECD.
3. Select the type II interface:
     select actriib_epitope, (GDF11 chain) within 4.5 of (ActRIIB chain)
4. List those GDF11 residue numbers.
5. Superpose apo-GDF8 (5JI1) onto the GDF11 chain of 6MAC:
     align 5JI1_GDF8, 6MAC_GDF11
   Expect low Cα-RMSD over the core (they're near-identical folds).
6. For each GDF11 epitope residue, read the spatially-equivalent
   GDF8 residue from the superposition AND confirm via sequence alignment.
7. Check conservation: is each transferred position identical or a
   conservative substitution in GDF8? Flag any that aren't.
8. Write GDF8 residue numbers (5JI1 mature-domain scheme) to
   hotspots/hotspot_residues.txt
```

Detail on the interface concept: [PPI hotspots](../concepts/PPI-hotspots.md). Detail on tools: [PyMOL](../tools/PyMOL.md), [TMalign](../tools/TMalign.md).

---

## Alternative / corroborating structure: 7MRZ

7MRZ (2022) shows GDF11 bound to a **fused ActRIIB–ALK4-Fc** construct with an anti-ActRIIB Fab, replicating the ternary complex with more extensive receptor contacts. Use it as a **second opinion**: if a residue is in the ActRIIB footprint in both 6MAC and 7MRZ, you can trust it. Discrepancies between the two are worth a closer look before committing a residue to your hotspot list.

---

## Why this transfer is defensible (and where it isn't)

**Defensible:** the type II epitope is the *more conserved* of GDF11's two receptor interfaces; GDF8 and GDF11 use the same type II receptor with comparable affinity; the fold superposition is near-perfect.

**Not fully ground truth:** it is still GDF11, not GDF8. State this explicitly. The mitigation is step 7 — per-residue conservation checking — which turns "I assumed it transfers" into "I verified each contact residue is conserved." That distinction is the difference between a naive and a rigorous account of the same work.

---

## Links

- The proxy ligand: [GDF11](GDF11.md)
- The real target it informs: [GDF8](GDF8.md) via [5JI1](5JI1.md)
- The receptor defining the epitope: [ActRIIB](ActRIIB.md)
- Interface theory: [PPI hotspots](../concepts/PPI-hotspots.md)
- Tools: [PyMOL](../tools/PyMOL.md), [TMalign](../tools/TMalign.md)
