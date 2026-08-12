# TGF-β receptor logic: wrist vs knuckle

TGF-β-family ligands signal through **two classes of single-pass serine/threonine
kinase receptors**. Getting the geometry of these two sites straight is the single
most important conceptual step in this project — target the wrong face and every
downstream design is wasted.

This page covers the **receptors and the cascade**. For the ligand-side anatomy
those receptors bind — the cystine-knot fold, and where the fingers, wrist and
heel are — read [TGF-β superfamily](TGF-beta-superfamily.md) first.

## Two receptor types, two sites

| | **Type I** (e.g. Alk4/Alk5/Alk7) | **Type II** (e.g. ActRIIB, ActRIIA, BMPRII) |
|---|---|---|
| Binds the… | **wrist** epitope | **knuckle** epitope |
| Location | *Concave* surface at the **dimer interface** (spans the heel helix of one monomer + fingers of the other) | *Convex* outer face of **one monomer's** β-fingers |
| Chemistry | mixed polar/hydrophobic | **hydrophobic-dominated** |
| Our target? | **No** | **Yes — ActRIIB** |

## The signalling cascade (why blocking type II works)

1. The ligand dimer recruits **type II** receptors at the knuckles.
2. The type II kinase then **trans-phosphorylates** a recruited **type I**
   receptor at the wrist.
3. The activated type I receptor phosphorylates **R-Smads (Smad2/3)**, which
   complex with Smad4 and drive the muscle-restraining transcriptional program.

Because the type II receptor sits *upstream* and its recruitment is the first
committed step, a binder that occupies the **knuckle** competitively blocks
ActRIIB engagement and shuts the cascade down. That makes our binder a functional
**ActRIIB antagonist** — but note the mechanism precisely: it works by occupying
the receptor's *footprint on the ligand*, **not** by mimicking the receptor. We
are not reproducing the ActRIIB surface; we are covering the patch it needs.

Two further consequences worth holding:

- The type II kinase is **constitutively active**, so the regulated step is
  proximity, not enzyme activation. Preventing the complex from assembling is
  therefore sufficient — no kinase inhibition is needed.
- Myostatin can also use **ActRIIA** at lower affinity, so blocking one receptor
  leaves an escape route. Both type II receptors dock the *same* knuckle, so
  occluding it on the ligand closes both routes at once. See
  [ActRIIB](../molecules/ActRIIB.md) for the full ligand-vs-receptor argument.

## ActRIIB specifically

ActRIIB is a type II receptor with a small (~100-residue) ectodomain in a
**three-finger-toxin fold**. It grips the ligand knuckle with an **aromatic triad
— Tyr60 / Trp78 / Phe101 —** burying ~720 Å² of mostly hydrophobic surface, plus
a handful of peripheral hydrogen bonds and salt bridges. The aromatic triad is a
fixed feature of ActRIIB; the ~720 Å² figure was first measured in the activin
A:ActRIIB structure (1NYS). For defining *myostatin* hotspots we use the closer
**GDF11:ActRIIB complex (PDB 6MAC)** as the homology template — GDF11 is ~90 %
identical to GDF8, so its ActRIIB footprint transfers with more confidence than
activin's (see [hotspot identification](../methods/02-hotspots.md)).

## Why this matters for de novo design

The type II/knuckle site is **hydrophobic, compact, and contained within a single
monomer** — three properties that make it an unusually friendly de novo binder
target:

- *Single monomer* → we can extract one chain and stay within a small VRAM budget.
- *Hydrophobic* → easy to bury with a designed helical interface.
- *Tolerant* → mutagenesis across the family shows only a handful of interface
  residues dominate binding, so the binder doesn't need to reproduce every contact.

Next: what the [knuckle epitope](epitope.md) looks like at residue resolution.
