# Step 5 · ESMFold validation

**Goal:** the critical gate. Fold each designed sequence *without giving the model
any structural information*. If it independently returns to the RFdiffusion
backbone shape, the sequence credibly encodes the intended fold.

**Environment:** `esm` (API client + analysis; folding happens server-side).

## Fold via the REST API

```python
import requests

def fold_sequence(sequence: str, name: str, out_dir: str):
    r = requests.post(
        "https://api.esmatlas.com/foldSequence/v1/pdb/",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data=sequence, timeout=120,
    )
    r.raise_for_status()
    open(f"{out_dir}/{name}.pdb", "w").write(r.text)
    return r.text   # ESMFold stores per-residue pLDDT in the B-factor column
```

Sequences > ~600 aa will fail; our binders (~45–60 aa) are well within range.
Retry on transient timeouts.

## Metrics

| Metric | Threshold | Meaning |
|---|---|---|
| **pTM** | > 0.7 | global fold confidence (< 0.5 ≈ disordered) |
| **mean pLDDT** | > 70 | local confidence (from B-factor column; < 50 ≈ disordered) |
| **RMSD to design** | < 2.0 Å | does the refold match the RFdiffusion backbone? |

RMSD / TM-score via the `esm` env's TMalign:

```bash
TMalign esm_validation/predicted_structures/design_0_seq1.pdb \
        rfdiffusion/outputs/design_0.pdb
```

## Interpreting

- **Success:** compact fold, pTM > 0.7, interface pLDDT > 70, RMSD < 2 Å.
- **Failure:** disordered coil (pTM < 0.5), or a different fold (RMSD > 5 Å) — the
  sequence doesn't encode the design. Go back to Step 4: more sequences or a
  higher sampling temperature; or Step 3 with a shorter binder.

→ Continue to [Step 6 · Ranking](06-ranking.md).
