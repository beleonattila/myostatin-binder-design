# TMalign

**Sequence-independent structural alignment.** Gives a length-normalised similarity score (TM-score) and RMSD between two structures without needing matched sequences — the right tool for comparing a de novo design to its intended backbone.

| Field | Value |
|-------|-------|
| Paper | Zhang & Skolnick, *Nucleic Acids Research* 33, 2302–2309 (2005) |
| Type | Structural superposition algorithm |
| Install | `conda install -c bioconda tmalign` |
| Role here | Quantify RFdiffusion-backbone vs ESMFold-refold similarity |

---

## Why not just use PyMOL `align`?

[PyMOL](PyMOL.md) `align` starts from a **sequence** alignment, then superposes. That's fine for GDF8↔GDF11 (similar sequences) but awkward for design validation, where you compare a designed backbone to an independently-folded model of the *same* sequence — and you want a metric that doesn't depend on getting a sequence alignment right or on chain-length quirks.

TMalign superposes on **structure alone** and reports the **TM-score**, which is:
- **normalised to protein length** (so it isn't inflated/deflated by size the way raw RMSD is),
- bounded in (0, 1],
- interpretable: **> 0.5** ≈ same fold; **> 0.9** ≈ near-identical.

This makes it a cleaner "did the refold reproduce the design?" number than raw RMSD alone.

---

## Use in the pipeline (Module 6)

```bash
TMalign  esm_validation/predicted_structures/design_0_seq1.pdb \
         rfdiffusion/outputs/design_0.pdb
```

Read from the output:
- **TM-score** (note it reports two, normalised by each chain's length — for same-length designs they'll be close),
- **RMSD** over the aligned region,
- number of aligned residues.

Record TM-score alongside your RMSD in `esm_validation/scores.tsv`. Pass criteria: **RMSD < 2 Å** and **TM-score > 0.5** (ideally > 0.7) between refold and design.

---

## TM-score vs pTM — don't confuse them

- **TM-score (TMalign):** measured similarity between *two actual structures* you provide.
- **pTM (ESMFold/AF2):** the model's *predicted* TM-score of its own output vs the (unknown) true structure — a self-confidence estimate.

They're the same underlying metric conceptually, but one is a measurement between two files and the other is a model's confidence. Your validation uses both: pTM says "the model is confident this fold is right"; TMalign says "and it does match the backbone we designed." See [validation metrics](../concepts/validation-metrics.md).

---

## Links

- Complementary tool: [PyMOL](PyMOL.md)
- Metric context: [validation metrics](../concepts/validation-metrics.md)
- Inputs come from: [RFdiffusion](RFdiffusion.md) (design) and [ESMFold](ESMFold.md) (refold)
