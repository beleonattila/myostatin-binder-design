# Project Wiki — Myostatin Binder Design

Knowledge base for the de novo binder project. Each page is self-contained theory at graduate level, cross-linked to the pages it depends on. Start from the [SYLLABUS](../SYLLABUS.md) for the ordered learning path; use this index for random access.

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

## Methods

| Page | Stage | One-liner |
|------|-------|-----------|
| [RFdiffusion](methods/RFdiffusion.md) | Backbone generation | Fine-tuned RoseTTAFold denoising diffusion model |
| [ProteinMPNN](methods/ProteinMPNN.md) | Sequence design | Graph MPNN inverse-folding network |
| [ESMFold](methods/ESMFold.md) | Validation | Language-model structure prediction (fast) |
| [AlphaFold2](methods/AlphaFold2.md) | Validation | MSA-based prediction; AF2-multimer for interfaces |
| [PyMOL](methods/PyMOL.md) | Analysis | Structure inspection, selection, superposition |
| [TMalign](methods/TMalign.md) | Analysis | Sequence-independent structural alignment / RMSD |

## Concepts

| Page | Ties together |
|------|---------------|
| [TGF-β superfamily](concepts/TGF-beta-superfamily.md) | The fold family and its receptor epitopes |
| [PPI hotspots](concepts/PPI-hotspots.md) | Why interfaces reduce to a few residues |
| [de novo binder design](concepts/de-novo-binder-design.md) | The full pipeline logic, end to end |
| [diffusion models](concepts/diffusion-models.md) | Generative denoising, the math behind RFdiffusion |
| [inverse folding](concepts/inverse-folding.md) | The structure→sequence problem |
| [validation metrics](concepts/validation-metrics.md) | pLDDT, pTM, pAE, iPTM, RMSD, wwPDB sliders |

---

## Conventions used across pages

- **Mature domain numbering** vs **full-length UniProt numbering** are distinguished explicitly wherever residues are named, because myostatin is cleaved from a precursor and the two schemes differ by ~260 residues. Always check which one a PDB uses before trusting a residue ID.
- Claims about current tooling and structures are dated; verify against RCSB / the tool's GitHub before running, since both move fast.
- Every "Defend" sentence in the syllabus maps to theory on exactly one of these pages.
