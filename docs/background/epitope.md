# The knuckle epitope at residue resolution

The **knuckle** is the convex outer surface of one myostatin monomer's
β-fingers — the patch that ActRIIB grips. This page summarizes what we know about
it and how we pin down the exact residues. The full method is in
[Step 2 · Hotspot identification](../methods/02-hotspots.md).

## The core problem

No GDF8:ActRIIB structure exists, and our apo target **5JI1** has no receptor
bound. So we **cannot read the ActRIIB footprint off the target directly**.
Instead we transfer it by homology:

1. Superpose apo myostatin (5JI1) onto **GDF11** in the GDF11:ActRIIB:ALK5
   complex (**6MAC**).
2. Read off which myostatin residues fall under the ActRIIB footprint.

This works because GDF11 is **~90 % identical to GDF8 in the mature domain** and
binds the same type II receptor (ActRIIB) the same way — a far closer proxy than
the activin A:ActRIIB complex (1NYS) we considered first.

## What contacts what

On the **receptor** side, the ActRIIB aromatic triad **Tyr60 / Trp78 / Phe101**
forms the hydrophobic core of the interface (a fixed feature of ActRIIB,
independent of which ligand it grips). On the **ligand** side, the residues that
pack into that triad sit on the finger loops — the **finger 1–2 loop** and the
**convex face of finger 3**. You read the exact GDF11 contact residues off 6MAC
and map them onto GDF8 by the superposition; because the two are ~90 % identical
here, most map one-to-one.

A general TGF-β rule of thumb (from BMP-2 alanine scanning) is that ~6 of ~24
interface residues dominate binding, often with one absolutely conserved Leu at
the core — so expect a handful of buried hydrophobics/aromatics to matter most.

## Provisional myostatin hotspots

Mapping the GDF11 knuckle contacts onto myostatin gives a *provisional* hotspot
list (myostatin mature numbering; **confirm the scheme against 5JI1**):

| Region | Residues |
|---|---|
| finger 1–2 loop | Ile33, Ala34, Pro35, Tyr38 |
| finger 3 convex face | Met84, Leu85, Tyr86, Phe87 |

!!! warning "Confirm before use"
    These are a **hypothesis**. They must be confirmed by the 6MAC superposition
    on the actual extracted 5JI1 chain (numbering can shift on extraction), each
    position checked for GDF11→GDF8 conservation, and any residue that is
    disordered/missing in the apo structure dropped. RFdiffusion's
    `ppi.hotspot_res` wants only the **5–8 strongest** hydrophobic/aromatic
    positions, not the whole patch.

## Why this epitope is designable

It is hydrophobic, compact, and entirely within one monomer (it does **not**
touch the dimer interface, which is the separate type I / wrist site). That means
a single extracted chain presents the complete epitope, and a small helical
binder can bury it with a hydrophobic interface — exactly what RFdiffusion's
PPI/binder mode is good at.
