# De Novo Myostatin Binder Design

A reproducible pipeline for designing and validating de novo helical
miniprotein binders against the **type II receptor (knuckle) epitope** of
myostatin (GDF-8).

This site is both the theory knowledge base and the runnable protocol. It
assumes a working knowledge of structural biology and bioinformatics, and
focuses on *why* each step is done the way it is.

## The one-paragraph version

Myostatin signals through the type II receptor **ActRIIB**, which binds the
convex, hydrophobic **knuckle** on a single ligand monomer's β-fingers.
We take apo myostatin from PDB **5JI1**, define the knuckle hotspots by homology
transfer from the GDF11:ActRIIB complex (PDB **6MAC**, GDF11 being ~90 % identical
to GDF8), generate binder backbones docked onto those hotspots with
**RFdiffusion**, design sequences for them with **ProteinMPNN**, and validate each
sequence by refolding it with **ESMFold** and checking it returns to the intended
shape. Designs that pass (pTM > 0.7, RMSD < 2 Å to the backbone) are ranked and
kept.

## How to read this

- **[Concepts](concepts/de-novo-binder-design.md)** — the theory: the fold family,
  what a hotspot is, how diffusion and inverse folding work, how to read the
  metrics.
- **[Molecules](molecules/GDF8.md)** — the cast: the ligand, its proxy, the
  receptor, and each PDB entry with its role and its caveats.
- **[Tools](tools/RFdiffusion.md)** — what each program actually does, its inputs
  and outputs, and what its numbers do *not* mean.
- **[Methods](methods/01-target-prep.md)** — the six runnable steps, reproducible
  with the environments in `envs/`.
- **[Reference](reference/glossary.md)** — glossary and hardware notes.

For an ordered learning path rather than random access, work through
`SYLLABUS.md` at the repo root; every step there links back into these pages.

---

## Page network

The dependency structure — read upstream pages before downstream ones.

```
                          ┌─────────────────────────┐
                          │  TGF-β superfamily       │  (fold family, epitopes)
                          └───────────┬─────────────┘
                                      │
        ┌─────────────────────────────┼─────────────────────────────┐
        │                             │                             │
   ┌────▼────┐                  ┌─────▼─────┐                 ┌──────▼──────┐
   │  GDF8   │◄─── 90% id ──────│  GDF11    │                 │  ActRIIB    │
   │(target) │                  │ (proxy)   │                 │(competitor) │
   └────┬────┘                  └─────┬─────┘                 └──────┬──────┘
        │                             │                             │
   ┌────▼──────┐   ┌──────────────┐   │  ┌────────────────────┐     │
   │   5JI1    │   │    3HH2      │   └──►│      6MAC          │◄────┘
   │(apo, tgt) │   │(GDF8:Fst288) │      │(GDF11:ActRIIB:ALK5)│
   └────┬──────┘   └──────┬───────┘      └─────────┬──────────┘
        │                 │                        │
        │            ┌────▼─────────┐              │
        │            │follistatin-  │              │
        │            │    288       │              │
        │            └──────────────┘              │
        │                                          │
        │        (target)          (hotspot source)│
        └───────────────┬──────────────────────────┘
                        │
              ┌─────────▼──────────┐
              │  PPI hotspots      │  (interface theory)
              └─────────┬──────────┘
                        │
     ═══════════════════▼═══════════════════  PIPELINE  ═══════════════
                        │
   ┌────────────────┐   │   ┌──────────────────┐   ┌───────────────────┐
   │ diffusion      ├───┼──►│   RFdiffusion    ├──►│  ProteinMPNN      │
   │ models (theory)│   │   │ (backbone gen)   │   │ (sequence design) │
   └────────────────┘   │   └──────────────────┘   └─────────┬─────────┘
                        │            ▲                       │
              ┌─────────▼──────┐     │             ┌─────────▼─────────┐
              │ de novo binder │─────┘             │ inverse folding   │
              │ design (arc)   │                   │ (theory)          │
              └────────────────┘                   └─────────┬─────────┘
                                                             │
                              ┌──────────────────────────────▼───────────┐
                              │            VALIDATION                     │
                              │  ESMFold / AlphaFold2 → PyMOL / TMalign   │
                              │        → validation metrics              │
                              └──────────────────────────────────────────┘
```

---

## Molecules

| Page | Role in project | One-liner |
|------|-----------------|-----------|
| [GDF8 (myostatin)](molecules/GDF8.md) | Design target | The ligand you are blocking |
| [GDF11](molecules/GDF11.md) | Hotspot proxy | ~90% identical mature domain; supplies interface geometry |
| [follistatin-288](molecules/follistatin-288.md) | Context | Natural antagonist occupying the epitope in 3HH2 |
| [ActRIIB](molecules/ActRIIB.md) | Competitor | Type II receptor your binder must out-compete |
| [3HH2](molecules/3HH2.md) | Reference structure | GDF8:Fst288 complex — cross-check, **not** a target |
| [5JI1](molecules/5JI1.md) | RFdiffusion target | Apo GDF8, clean exposed epitope |
| [6MAC](molecules/6MAC.md) | Hotspot source | GDF11:ActRIIB:ALK5 ternary complex |

## Tools

| Page | Stage | One-liner |
|------|-------|-----------|
| [RFdiffusion](tools/RFdiffusion.md) | Backbone generation | Fine-tuned RoseTTAFold denoising diffusion model |
| [ProteinMPNN](tools/ProteinMPNN.md) | Sequence design | Graph MPNN inverse-folding network |
| [ESMFold](tools/ESMFold.md) | Validation | Language-model structure prediction (fast) |
| [AlphaFold2](tools/AlphaFold2.md) | Validation | MSA-based prediction; AF2-multimer for interfaces |
| [PyMOL](tools/PyMOL.md) | Analysis | Structure inspection, selection, superposition |
| [TMalign](tools/TMalign.md) | Analysis | Sequence-independent structural alignment / RMSD |

## Concepts

| Page | Ties together |
|------|---------------|
| [TGF-β superfamily](concepts/TGF-beta-superfamily.md) | The fold family and its receptor epitopes |
| [TGF-β receptor logic](concepts/tgf-beta-receptors.md) | Wrist vs knuckle, the cascade, why blocking type II works |
| [The knuckle epitope](concepts/epitope.md) | The target site at residue resolution |
| [PPI hotspots](concepts/PPI-hotspots.md) | Why interfaces reduce to a few residues |
| [de novo binder design](concepts/de-novo-binder-design.md) | The full pipeline logic, end to end |
| [diffusion models](concepts/diffusion-models.md) | Generative denoising, the math behind RFdiffusion |
| [inverse folding](concepts/inverse-folding.md) | The structure→sequence problem |
| [validation metrics](concepts/validation-metrics.md) | pLDDT, pTM, pAE, iPTM, RMSD, wwPDB sliders |

---

## Conventions used across pages

- **Mature domain numbering** vs **full-length UniProt numbering** are
  distinguished explicitly wherever residues are named, because myostatin is
  cleaved from a precursor and the two schemes differ by ~260 residues. Always
  check which one a PDB uses before trusting a residue ID.
- Claims about current tooling and structures are dated; verify against RCSB or
  the tool's GitHub before running, since both move fast.
- Every "Defend" sentence in the syllabus maps to theory on exactly one page.

> The dated decision log — including corrections made along the way — is
> `CONTEXT.md` at the repo root.
