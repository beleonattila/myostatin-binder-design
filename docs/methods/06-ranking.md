# Step 6 · Ranking & final selection

**Goal:** turn 58 validated sequences into a defensible panel of five, and state
the axis that produced it.

**Environment:** `esm` (pandas + PyMOL). **Run:** `make rank`.

!!! warning "This step's original recipe was wrong, and Step 5 is what disproved it"
    The first version of this page said: filter on `pTM > 0.7`, then **rank by
    ProteinMPNN log-likelihood**. Neither survives contact with the data.

    - **pTM is not available.** The ESM Atlas `/foldSequence/v1/pdb/` endpoint
      returns a bare PDB — no confidence JSON, no pTM. Step 5 substituted mean
      pLDDT ≥ 70 and TM-score ≥ 0.5, and said so rather than quietly dropping it.
    - **The MPNN score does not predict refold accuracy.** Measured over all 64
      sequences: Spearman ρ = **−0.06** against Cα-RMSD, ρ = **+0.01** against
      TM-score. Ranking on it would have been ranking on noise.

## The axis

Step 3 ranks by buried interface area and puts `design_5` first. Step 5 ranks by
designability and puts `design_5` last. These are not two candidate rankings to
pick between — they measure different things, and only one of them is a
threshold.

| Role | Metric | Why that role |
|---|---|---|
| **Gate** | designability | A sequence that does not fold to its designed backbone has no interface; its buried area describes a structure that will not exist. Pass/fail, applied first. |
| **Objective** | buried interface area | Among sequences that fold as designed, burying more of the ActRIIB knuckle is what makes a better binder candidate. |
| **Constraint** | one per backbone | Five sequences off one backbone are one design with five spellings. |

### The gate

| Criterion | Bar | Why |
|---|---|---|
| Self-consistent (Step 5) | pass | RMSD < 2 Å, pLDDT ≥ 70, TM ≥ 0.5, coverage ≥ 0.90 |
| Cα-RMSD to design | ≤ 1.0 Å | the conventional designable-minibinder bar |
| TM-score | ≥ 0.90 | the same fold, not merely the same class of fold |
| Coverage | = 1.00 | every residue aligned — the `design_5` lesson |
| Mean pLDDT | ≥ 85 | confident model |
| Min pLDDT | ≥ 70 | no floppy terminus hiding inside a good average |

**41 of 58** clear it, and all eight shortlisted backbones keep at least one.
That is what dissolves the Step 3 / Step 5 argument: `design_5` keeps exactly one
sequence, and one is enough to carry the widest interface into the panel on merit.

### The tie band

dSASA is a backbone+CB **lower bound** — Step 3 calibrated the real
ActRIIB:GDF11 interface at 293 Å² in these units against 697 Å² full-atom, so
sidechains carry 58 % of a real interface. Differences of a few Å² are noise, and
ranking on them is false precision. Representatives within **10 Å²** are treated
as tied and ordered by designability instead.

Four representatives land in one band (406 → 402 Å²), and that band straddles the
cut: `design_15` misses the panel on a 4 Å² interface difference this
representation cannot resolve, with designability deciding it. A rule that
decides a cut has to be visible, so `06_rank.py` prints it into the README.

## The panel

| # | Sequence | Buried Å² | RMSD Å | pLDDT | Gated | Rg ratio | Charge |
|---|---|---|---|---|---|---|---|
| 1 | `design_5_s2` | 469 | 0.48 | 85.5 | 1/8 | 1.29 | −2 |
| 2 | `design_18_s4` | 448 | 0.45 | 91.6 | 4/8 | 1.28 | −2 |
| 3 | `design_12_s4` | 402 | 0.40 | 90.2 | 7/8 | 1.29 | +3 |
| 4 | `design_11_s7` | 402 | 0.42 | 89.1 | 6/8 | 1.30 | +2 |
| 5 | `design_14_s7` | 404 | 0.43 | 93.1 | 5/8 | **1.06** | **0** |

`design_5_s2` leads on the objective but carries the panel's highest variance:
only 1 of its 8 sequences clears the gate, because ESMFold predicts its helical
hairpin as one straight helix for five of the other seven — confidently.

**If only one design is made, prefer `design_14_s7`**: an interface
indistinguishable from the middle of the panel, the most compact backbone of the
twenty (Rg ratio 1.06), the highest confidence of any representative (pLDDT
93.1), and net charge 0 — the one sequence that largely escapes ProteinMPNN's
over-charging bias.

## Outputs

```
results/top_designs/
├── README.md              the write-up: axis, gate, table, liabilities, caveats
├── ranking.tsv            all 64 sequences, gate status and every metric
├── panel.fasta            the 5 selected sequences
├── complexes/             each prediction superposed onto the target, as a PDB
└── figures/               one render per selection + panel_overview.png
```

The complex, not the binder alone, is the deliverable: predictions are placed on
the full-atom target with `cealign` (never `align` — the RFdiffusion backbone is
poly-glycine).

## What you can credibly claim afterwards

> *"I ran RFdiffusion binder design against the ActRIIB (type II / knuckle)
> epitope of myostatin — hotspots defined by homology transfer from the
> GDF11:ActRIIB complexes 6MAC and 7MRZ onto apo myostatin (5JI1), verified by
> reproducibility across two crystal forms and 20/21 residue conservation —
> designed sequences with ProteinMPNN, validated self-consistency by refolding
> with ESMFold, and selected a five-design panel by gating on designability and
> ranking on interface area. I measured that the ProteinMPNN score does not
> predict refold accuracy (ρ = −0.06, n = 64), which is why the panel is not
> ranked on it."*

**What it is not:** no binding has been demonstrated. Self-consistency says a
sequence folds to its intended backbone, not that the fold binds myostatin. The
obvious next computational step is an orthogonal check this pipeline never ran —
independent complex prediction (AlphaFold-Multimer or Boltz) of binder + target,
which tests the *interface* rather than the monomer fold.
