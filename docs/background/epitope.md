# The knuckle epitope at residue resolution

The **knuckle** is the convex outer surface of one myostatin monomer's
β-fingers — the patch that ActRIIB grips. This page summarizes what we know about
it and how we pin down the exact residues. The full method is in
[Step 2 · Hotspot identification](../methods/02-hotspots.md).

## The core problem

Our target structure, **3HH2**, contains *no receptor* (it is
myostatin:follistatin). So we **cannot read the ActRIIB footprint off 3HH2
directly**. Instead we transfer it by homology:

1. Superpose one myostatin monomer onto **activin A** in the activin:ActRIIB
   complex (**1NYS**).
2. Read off which myostatin residues fall under the ActRIIB footprint.

This works because activin A and myostatin share the TGF-β fold and bind ActRIIB
the same way; their finger sequences align well at the contact regions.

## What contacts what

On the **receptor** side, the ActRIIB aromatic triad **Tyr60 / Trp78 / Phe101**
forms the hydrophobic core of the interface. On the **ligand** side (mapped from
activin A's contacts), the residues that pack into that triad sit on the finger
loops:

- finger 1–2 loop — activin **Ile30 / Ala31 / Pro32**
- finger 3 — activin **Pro88 / Leu92 / Tyr94**
- finger 4 — activin **Ile100**

The central, load-bearing contacts are **Ala31 / Pro32 / Leu92**. A general TGF-β
rule of thumb (from BMP-2 alanine scanning) is that ~6 of ~24 interface residues
dominate binding, often with one absolutely conserved Leu at the core.

## Provisional myostatin hotspots

Aligning myostatin to activin A at the contact regions gives a *provisional*
knuckle hotspot list (myostatin mature numbering, Asp1 = residue 1):

| Region | Residues |
|---|---|
| finger 1–2 loop | Ile33, Ala34, Pro35, Tyr38 |
| finger 3 convex face | Met84, Leu85, Tyr86, Phe87 |

!!! warning "Confirm before use"
    These are a **hypothesis**. They must be confirmed by the 1NYS superposition
    on the actual extracted chain (numbering can shift on extraction), and any
    residue that is disordered/missing in chain A must be dropped. RFdiffusion's
    `ppi.hotspot_res` wants only the **5–8 strongest** hydrophobic/aromatic
    positions, not the whole patch.

## Why this epitope is designable

It is hydrophobic, compact, and entirely within one monomer (it does **not**
touch the dimer interface, which is the separate type I / wrist site). That means
a single extracted chain presents the complete epitope, and a small helical
binder can bury it with a hydrophobic interface — exactly what RFdiffusion's
PPI/binder mode is good at.
