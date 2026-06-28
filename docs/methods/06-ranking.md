# Step 6 · Ranking & final selection

**Goal:** combine the metrics into one table and pick the top designs.

**Environment:** `esm` (pandas + TMalign).

## Build the scores table

Collect one row per (backbone, sequence) into `results/scores.tsv`:

```
design_id        backbone   seq_id  pTM   mean_pLDDT  RMSD_to_design  mpnn_score
design_0_seq1    design_0   1       0.82  78.3        1.4             -1.34
design_0_seq2    design_0   2       0.61  61.0        3.8             -1.21
```

- `pTM`, `mean_pLDDT` — from the ESMFold output (pLDDT averaged from the B-factor
  column).
- `RMSD_to_design` — TMalign of the ESMFold prediction vs the RFdiffusion backbone.
- `mpnn_score` — ProteinMPNN log-likelihood (more negative = better).

## Filter, in order

1. pTM > 0.7
2. mean pLDDT > 70
3. RMSD to design backbone < 2.0 Å
4. Among survivors, rank by ProteinMPNN log-likelihood (more negative first)

Take the **top 3–5**. Open them in PyMOL alongside the myostatin target and
visually confirm the interface contacts the knuckle hotspots. Save winners to
`results/top_designs/`.

## What you can credibly claim afterwards

> *"I ran RFdiffusion binder design against the ActRIIB (type II / knuckle)
> epitope of myostatin — hotspots defined by homology transfer from the
> ActRIIB:activin A complex (1NYS) onto the myostatin crystal structure (3HH2) —
> designed sequences with ProteinMPNN, and validated self-consistency by
> refolding with ESMFold, filtering for pTM > 0.7 and RMSD < 2 Å."*
