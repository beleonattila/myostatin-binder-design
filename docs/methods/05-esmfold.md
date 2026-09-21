# Step 5 · ESMFold validation

**Goal:** the critical gate. Fold each designed sequence *without giving the model
any structural information*. If it independently returns to the RFdiffusion
backbone shape, the sequence credibly encodes the intended fold.

**Environment:** `esm` (API client + analysis; folding happens server-side).

## Fold via the REST API

```bash
conda activate esm && python scripts/05_esmfold.py        # --limit N to smoke test
```

The script POSTs each sequence to `https://api.esmatlas.com/foldSequence/v1/pdb/`,
caches every prediction in `esm_validation/predicted_structures/`, and writes
`esm_validation/scores.tsv`. Sequences > ~600 aa fail; our 52–60 aa binders are
well within range.

**Retries are not optional.** The endpoint returns intermittent
`HTTP 504 Endpoint request timed out` under normal use — roughly one call in three
in this run. The script retries with exponential backoff and caches successes, so a
rerun only fetches what is still missing.

!!! danger "Two things this endpoint does not do"
    **1. It returns no pTM.** `/foldSequence/v1/pdb/` returns a bare PDB — no
    confidence JSON, no pTM anywhere. The `pTM > 0.7` threshold that earlier drafts
    of this page specified **cannot be evaluated from this API at all**. Getting
    real pTM means running ESMFold locally with the weights and a GPU.

    The substitution used here, stated rather than quietly dropped:

    | Intended | Used instead | Covers |
    |---|---|---|
    | pTM > 0.7 | mean pLDDT ≥ 70 | is the model confident in this fold |
    | — | TM-score ≥ 0.5 (TMalign) | is it the *same* fold as the design |

    For a single-domain ~55-mer these two carry what pTM would have.

    **2. pLDDT comes back on a 0–1 scale, not 0–100.** B-factors land in 0.5–0.9.
    Apply the conventional `>70` cut to those raw numbers and *every* design fails.
    Local ESMFold builds emit 0–100, so detect the scale rather than assume it:

    ```python
    if max(vals) <= 1.0:
        vals = [v * 100 for v in vals]
    ```

## Metrics

| Metric | Threshold | Meaning |
|---|---|---|
| **mean pLDDT** | ≥ 70 | fold confidence (B-factor column; < 50 ≈ disordered) |
| **RMSD to design** | < 2.0 Å | does the refold match the RFdiffusion backbone? |
| **TM-score** | ≥ 0.5 | same fold, by TMalign's own calibration |
| **coverage** | ≥ 0.90 | fraction of the design that aligned at all |

!!! danger "RMSD without coverage is not a self-consistency metric"
    TMalign reports RMSD over the residues it **managed to align**. A prediction
    matching only part of the design therefore scores a *flattering* RMSD. In this
    project three `design_5` sequences aligned just **30 of 52 residues** and came
    back at **0.55 Å** — which reads as an excellent fit and is actually a
    58 %-complete one. Always divide `Aligned length` by the design length and
    require ~0.9.

**Compare against chain B only.** The parent `design_N.pdb` holds the 95-residue
target in chain A; superposing the whole complex folds the target into the number
and swamps the signal. Extract the binder first:

```bash
TMalign esm_validation/predicted_structures/design_5_s4.pdb  binder_only.pdb
```

TMalign prints two TM-scores, normalised by each input in turn; take the one
normalised by the **design backbone** (the second, given that argument order).

## Interpreting

- **Success:** compact fold, mean pLDDT ≥ 70, RMSD < 2 Å, TM ≥ 0.5.
- **Failure:** disordered coil (pLDDT < 50 throughout), or a different fold
  (RMSD > 5 Å, TM < 0.5) — the sequence doesn't encode the design. Go back to
  Step 4 for more sequences or a higher sampling temperature; or Step 3 with a
  shorter binder.

### Results for this project

**58 of 64 sequences (91 %) self-consistent.** Six of the eight backbones refolded
8/8; `design_11` managed 7/8 and `design_5` only 3/8. Best: `design_12_s4` at
**RMSD 0.40 Å**, pLDDT 90.2, TM 0.976.

**Why Step 5 cannot be skipped — the ProteinMPNN score does not predict refolding:**

| Spearman correlation (n = 64) | |
|---|---|
| MPNN score vs RMSD | **−0.055** |
| MPNN score vs TM-score | **+0.008** |
| mean pLDDT vs RMSD | −0.304 |

The best refold (`design_12_s4`, 0.40 Å) ranks only **41st of 64** by MPNN score, and
the second-best (`design_11_s7`, 0.42 Å) ranks **63rd of 64**; the best MPNN score
refolds at only 1.65 Å. Inverse-folding likelihood and designability are different
quantities — you have to fold the sequences to find out.

!!! tip "High pLDDT on the wrong structure"
    `design_5` was the **best backbone in Step 3** (most buried area, most
    contacts) and the **worst for designability**. The overlay shows ESMFold
    predicting **one long straight helix** where the design is a helical hairpin —
    it matched one arm and ran straight on instead of forming the turn. And it was
    *confident*: pLDDT **90**. Isolated helices are easy to predict, so a high
    pLDDT says nothing on its own about whether the intended fold was reproduced.
    Interface quality and designability are independent axes.

!!! bug "Don't use `cmd.align` to overlay a prediction on a backbone"
    PyMOL's `align` runs a **sequence** alignment first. RFdiffusion backbones are
    poly-glycine, so it finds nothing in common with a designed sequence and
    superposes on a handful of atoms (4, in this project). Use **`cealign`** or
    TMalign — both are purely structural.

!!! warning "What this step does and does not prove"
    Self-consistency says the **sequence encodes the designed fold**. It says
    nothing about **binding** — the binder is folded *alone* here, with myostatin
    absent. A design can refold perfectly and still not bind.

    Assessing the interface needs a co-folding method: AF2-multimer or Boltz/Chai,
    scored on **iPTM** and interface PAE. That is the honest boundary of this
    pipeline, and it should be stated before anyone asks. See
    [AlphaFold2](../tools/AlphaFold2.md).

→ Continue to [Step 6 · Ranking](06-ranking.md).
