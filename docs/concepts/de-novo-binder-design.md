# De Novo Binder Design — The Pipeline Logic

The page that ties everything together. Read it at the start (for the map) and again at the end (when the pieces click). Every other page is a node in the pipeline described here.

---

## The problem

Design, from scratch, a small protein that binds a chosen surface of a target — here, the [ActRIIB](../molecules/ActRIIB.md) epitope of [GDF8](../molecules/GDF8.md). "From scratch" (de novo) means the binder is not derived from a natural binder or antibody; its fold and sequence are generated.

Doing this in one shot is intractable — the joint space of backbone shapes *and* sequences that fold *and* bind is astronomically large. The modern solution **factorises** the problem into three tractable sub-problems, each with a dedicated tool.

---

## The three sub-problems (why three tools, not one)

```
                 TARGET + EPITOPE
                        │
        ┌───────────────▼────────────────┐
        │ 1. SHAPE                        │
        │ What backbone geometry docks    │   → RFdiffusion
        │ against this epitope?           │      (backbone only, no sequence)
        └───────────────┬─────────────────┘
                        │  backbone
        ┌───────────────▼────────────────┐
        │ 2. SEQUENCE                     │
        │ What amino acids fold into      │   → ProteinMPNN
        │ this backbone?                  │      (inverse folding)
        └───────────────┬─────────────────┘
                        │  sequence(s)
        ┌───────────────▼────────────────┐
        │ 3. VALIDATION                   │
        │ Does that sequence actually     │   → ESMFold / AF2-multimer
        │ fold into that backbone (and    │      (self-consistency + interface)
        │ dock)?                          │
        └───────────────┬─────────────────┘
                        │
                 FILTER & RANK → top designs
```

Each arrow is a hand-off of a concrete artifact (PDB → PDB+FASTA → PDB+scores). Keeping the three problems separate is what makes the whole thing work and is the single most important conceptual point to articulate.

---

## Step 1 — Shape: [RFdiffusion](../tools/RFdiffusion.md)

A denoising [diffusion model](diffusion-models.md) (fine-tuned RoseTTAFold) generates novel binder **backbones** conditioned on the target and the [hotspots](PPI-hotspots.md). Output is geometry only — placeholder residues. It answers "what shape sits here," nothing about identity.

## Step 2 — Sequence: [ProteinMPNN](../tools/ProteinMPNN.md)

An [inverse-folding](inverse-folding.md) graph network assigns amino acid sequences predicted to fold into each backbone. The target chain is fixed; only the binder is designed. Output: several candidate sequences per backbone.

## Step 3 — Validation: [ESMFold](../tools/ESMFold.md) / [AlphaFold2](../tools/AlphaFold2.md)

Refold each designed sequence *independently* and check it reproduces the intended backbone (**self-consistency**), plus — with AF2-multimer — that the binder docks at the target ([validation metrics](validation-metrics.md): pTM, pLDDT, pAE, iPTM, RMSD/TM-score). Survivors of the filter are your designs.

---

## The self-consistency principle (why validation is trustworthy at all)

You never do a wet-lab experiment in this project, so what makes a design "good"? The field's answer: **self-consistency predicts experimental success.** If

```
ESMFold( ProteinMPNN( RFdiffusion(target) ) ) ≈ RFdiffusion(target)
```

— i.e. an independent folding model, given only the designed sequence, reconstructs the shape you designed — the design is likely to behave as intended in reality. This closed loop is the logical backbone of the whole exercise. It is a **predictive filter**, not proof.

---

## What this pipeline does and does NOT establish

**Does:** produce candidate binder designs with quantified in silico self-consistency and (with AF2-multimer) interface confidence; demonstrate fluency with the standard de novo design stack.

**Does NOT:** prove binding, affinity, specificity, expressibility, or stability. Those need synthesis + biophysics (SPR/BLI, SEC, crystallography/cryo-EM). No wet-lab, no proof.

For your outreach, this framing is the credible one: *"an in silico design exercise demonstrating the RFdiffusion→ProteinMPNN→refold pipeline against a real, motivated target, with honest scope limits."* Overclaiming binding from in silico scores is the fastest way to lose a structural-biology audience.

---

## The project's target choice recap

| Decision | Choice | Rationale page |
|----------|--------|----------------|
| Target ligand | [GDF8](../molecules/GDF8.md) | motivated by myostatin/muscle biology |
| Epitope | ActRIIB knuckle (type II) | [ActRIIB](../molecules/ActRIIB.md), [TGF-β fold](TGF-beta-superfamily.md) |
| Target structure | [5JI1](../molecules/5JI1.md) apo | epitope exposed, good validation |
| Hotspot source | [6MAC](../molecules/6MAC.md) via [GDF11](../molecules/GDF11.md) | no GDF8:ActRIIB structure exists |
| Not used as target | [3HH2](../molecules/3HH2.md) | epitope occluded + poor validation |

---

## Links (the whole map)

Methods: [RFdiffusion](../tools/RFdiffusion.md) · [ProteinMPNN](../tools/ProteinMPNN.md) · [ESMFold](../tools/ESMFold.md) · [AlphaFold2](../tools/AlphaFold2.md) · [PyMOL](../tools/PyMOL.md) · [TMalign](../tools/TMalign.md)
Concepts: [diffusion models](diffusion-models.md) · [inverse folding](inverse-folding.md) · [PPI hotspots](PPI-hotspots.md) · [validation metrics](validation-metrics.md) · [TGF-β superfamily](TGF-beta-superfamily.md)
