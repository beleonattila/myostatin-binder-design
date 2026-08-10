# ESMFold

**Stage 3 — fast validation.** Refolds each designed sequence to test self-consistency: does the sequence ProteinMPNN wrote actually fold into the backbone RFdiffusion designed?

| Field | Value |
|-------|-------|
| Paper | Lin et al., "Evolutionary-scale prediction of atomic-level protein structure with a language model", *Science* 379, 1123–1130 (2023) |
| Lab | Meta AI (FAIR) |
| Basis | ESM-2 protein language model + folding head |
| Input | Single amino acid sequence |
| Output | Predicted structure PDB + per-residue pLDDT (+ pTM) |
| Access | Free REST API (`api.esmatlas.com`), or local install |
| Needs GPU | Not if you use the API |

Prerequisite: [validation metrics](../concepts/validation-metrics.md). Upstream: [ProteinMPNN](ProteinMPNN.md). Compare with: [AlphaFold2](AlphaFold2.md).

---

## What it is and why it's here

ESMFold predicts structure directly from a **single sequence** using a large protein language model (ESM-2), **without building a multiple sequence alignment (MSA)**. That makes it much faster than AlphaFold2 (which depends on MSA search), at some cost in accuracy. For your purpose — quickly screening many designed sequences — speed and no-MSA are exactly right, because your **de novo** sequences have no natural homologs to align anyway, which partly neutralises AF2's MSA advantage.

---

## The self-consistency logic (this is the whole point)

You are running a loop-closure test on your own pipeline:

```
RFdiffusion  →  backbone shape  B
ProteinMPNN  →  sequence         S   (designed to fold into B)
ESMFold(S)   →  predicted shape  B'  (folded independently, no knowledge of B)

If  B' ≈ B  →  the sequence encodes the intended structure  →  designable
If  B' ≠ B  →  the sequence does NOT reliably encode B      →  reject
```

ESMFold never sees the target or the design backbone. If, from sequence alone, it independently arrives at the same fold RFdiffusion intended, that is strong evidence the design is *self-consistent* — the property that empirically predicts wet-lab success in these pipelines. This is a **filter**, not proof of binding.

---

## The metrics it gives you

- **pLDDT** (per-residue, 0–100): local confidence. ESMFold stores it in the **B-factor column** of the output PDB — read it from there. Mean pLDDT > 70 is a reasonable bar; regions < 50 are effectively disordered.
- **pTM** (predicted TM-score, 0–1): global fold confidence. > 0.7 is a common threshold for "confident, compact fold."
- **RMSD to design**: you compute this yourself by superposing B' on B — see [PyMOL](PyMOL.md) / [TMalign](TMalign.md). < 2 Å Cα-RMSD is the standard pass.

Full definitions and thresholds: [validation metrics](../concepts/validation-metrics.md).

---

## Using the API

POST the raw sequence to the fold endpoint; you get back a PDB string with pLDDT in the B-factors. Constraints to respect:
- Sequences roughly > 400–600 residues fail — irrelevant for your 50–70 aa binders.
- The server rate-limits and occasionally times out; retry with backoff.
- Fold the **binder sequence** (and optionally the complex, though single-sequence ESMFold handles monomers most cleanly; for the *interface* you'll usually want [AlphaFold2](AlphaFold2.md)-multimer).

Minimal pattern is in `CONTEXT.md` Module 5/Step 5.

---

## ESMFold vs AlphaFold2 for this project

| | ESMFold | [AlphaFold2](AlphaFold2.md) |
|--|---------|------------|
| Speed | Fast | Slow (MSA search) |
| MSA needed | No | Yes |
| De novo sequences | Well-suited (no homologs anyway) | MSA thin for novel designs |
| Interface scoring (iPTM/pAE) | Limited | AF2-multimer is the standard |
| Role here | First-pass screen of all designs | Confirm top designs + interface |

Sensible workflow: **screen everything with ESMFold, confirm the survivors with AF2-multimer** if you have the compute budget.

---

## What to be able to say

*"I validated design self-consistency by refolding each ProteinMPNN sequence with ESMFold and requiring the independently-predicted structure to match the RFdiffusion backbone within ~2 Å RMSD, with pTM > 0.7 — using ESMFold because it's single-sequence and fast, which suits de novo designs that lack MSAs."*

---

## Links

- Metric definitions: [validation metrics](../concepts/validation-metrics.md)
- What it validates: [ProteinMPNN](ProteinMPNN.md) output
- Stronger interface check: [AlphaFold2](AlphaFold2.md)
- RMSD tools: [PyMOL](PyMOL.md), [TMalign](TMalign.md)
