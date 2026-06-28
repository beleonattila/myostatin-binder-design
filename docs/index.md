# De Novo Myostatin Binder Design

A reproducible pipeline for designing and validating de novo helical
miniprotein binders against the **type II receptor (knuckle) epitope** of
myostatin (GDF-8).

This site is the project "wiki". It assumes a working knowledge of structural
biology and bioinformatics and focuses on *why* each step is done the way it is.

## How to read this

- **Background** — the biology you need to understand the target: what myostatin
  is, how TGF-β receptors choose their binding sites, and what the knuckle
  epitope actually is.
- **Methods** — the six runnable steps, from cleaning the crystal structure to
  ranking the final designs. Each page is reproducible with the environments in
  `envs/`.
- **Reference** — a glossary of the acronyms (pLDDT, pTM, contig, SE(3)…) and
  notes on hardware and the deferred Docker plan.

## The one-paragraph version

Myostatin signals through the type II receptor **ActRIIB**, which binds the
convex, hydrophobic **knuckle** on a single ligand monomer's β-fingers.
We extract one myostatin monomer from PDB **3HH2**, define the knuckle hotspots
by homology transfer from the ActRIIB:activin complex (PDB **1NYS**), generate
binder backbones docked onto those hotspots with **RFdiffusion**, design
sequences for them with **ProteinMPNN**, and validate each sequence by refolding
it with **ESMFold** and checking it returns to the intended shape. Designs that
pass (pTM > 0.7, RMSD < 2 Å to the backbone) are ranked and kept.

> See the [project decision log](https://github.com) in `CONTEXT.md` at the repo
> root for the full, dated rationale behind every choice (including corrections
> made along the way).
