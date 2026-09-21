# Step 4 · ProteinMPNN (sequence design)

**Goal:** assign amino-acid sequences to the binder backbone — keeping the
myostatin target sequence fixed, designing only the binder chain.

**Environment:** `proteinmpnn` (CPU is fine at our scale).

```bash
mamba env create -f envs/proteinmpnn.yml
git clone https://github.com/dauparas/ProteinMPNN.git   # runs from the clone
```

Model weights ship inside the clone (`vanilla_model_weights/`,
`soluble_model_weights/`, `ca_model_weights/`) — nothing extra to download. At
this scale the whole step is ~40 s on CPU for 8 backbones × 8 sequences.

## Run

```bash
conda activate proteinmpnn
scripts/04_proteinmpnn.sh 8      # 8 sequences per shortlisted backbone
```

which runs, per backbone:

```bash
python protein_mpnn_run.py \
  --pdb_path .../rfdiffusion/outputs/design_5.pdb \
  --pdb_path_chains "B" \
  --out_folder .../proteinmpnn/outputs/ \
  --num_seq_per_target 8 \
  --sampling_temp "0.1" \
  --model_name "v_48_020" \
  --omit_AAs "CX" \
  --seed 42 --batch_size 1
```

!!! danger "The flag is `--pdb_path_chains`"
    Earlier drafts of this page said `--pdb_path_chains_to_design`. **No such
    argument exists** — argparse rejects it outright. The real flag is
    `--pdb_path_chains`, and everything *not* listed is fixed automatically
    (`fixed_chain_list = [c for c in all_chains if c not in designed]`).

| Parameter | Meaning | Setting |
|---|---|---|
| `--pdb_path_chains` | chain(s) to **redesign** | `B` — the binder. Chain A (target) is then fixed by omission |
| `--num_seq_per_target` | sequences per backbone | 8 to test, 32–64 for real sampling |
| `--sampling_temp` | diversity | 0.1 conservative, 0.2 for more |
| `--model_name` | weights | `v_48_020` (vanilla, 0.20 Å training noise) suits idealised RFdiffusion backbones |
| `--omit_AAs` | forbidden residues | `CX` — see below |

**Design against the complex, not the isolated binder.** The target chain keeps
its real sequence in the RFdiffusion output (verified: chain A reads back as the
exact myostatin sequence, only the binder is poly-glycine), so fixing chain A lets
ProteinMPNN choose interface residues that complement myostatin's actual
sidechains. That is the entire reason this step runs on the complex.

**Why omit cysteine.** A free Cys invites disulfide scrambling, and myostatin
carries nine of its own (the cystine knot plus the interchain bond). An unpaired
binder Cys is a real aggregation and expression liability.

### The disordered gap is handled correctly

ProteinMPNN reports `length 169` for a 60-residue binder on a 95-residue target,
which looks alarming: 109 + 60. Its parser expands chain A across its full
numbering range, inserting the 14 unresolved residues (51–64) as `-` with NaN
coordinates. Checking `tied_featurize`, those positions get **`mask = 0`** and are
excluded from the graph, while still occupying their index slots — so the
positional encoding across the gap stays truthful. Nothing to fix.

## Reading the output

- One FASTA per backbone in `proteinmpnn/outputs/seqs/`. The first record is the
  poly-glycine input; the rest are designs.
- **`score` is a negative log-likelihood — lower is better.** `score` covers the
  designed chain, `global_score` the whole complex. **Rank on `score`**:
  `global_score` is dominated by the 95 fixed target residues and barely moves.
- `seq_recovery` is meaningless here — it compares against poly-glycine.

```bash
conda activate esm && python scripts/04b_analyze_sequences.py
```

!!! warning "Measure the interface through `_structure_utils.load_design`"
    Working out *which* binder positions touch the epitope means measuring against
    the RFdiffusion output — which is backbone-only on **both** chains. Query it
    directly and you find 1–5 contacting positions instead of 7–13, and the
    residue identities you read off are noise. `scripts/_structure_utils.py`
    restores the target's sidechains and adds virtual CB; both Step 3 and Step 4
    go through it. This mistake has been made twice in this project.

### What good output looks like

The single most informative check is the **hydrophobic gradient** — hydrophobic
fraction should rise as you move from the whole binder inward to the contact
patch. For this run:

| Region | Hydrophobic fraction |
|---|---|
| Whole binder | 0.33 |
| Epitope-contacting face | 0.46 |
| Hotspot-contacting ring | **0.57** |

That ordering is the evidence that the sequence matches the structural intent:
apolar residues placed where the design buries surface, polar ones left on the
solvent face. A flat or inverted gradient means the sequence is fighting the
backbone, whatever its score.

Also check: no `C`, no long single-residue runs, and **mean pairwise identity
below ~80 %** — at temperature 0.1 ProteinMPNN can collapse to near-identical
sequences, which turns "8 candidates" into one candidate folded eight times. If
it collapses, rerun at `--sampling_temp 0.2`.

!!! note "Expect a charged surface"
    ProteinMPNN over-produces E/K/R on solvent-exposed faces — good for its
    likelihood, and a known liability for expression and non-specific binding.
    Here that shows as heavily E/K/A-rich sequences at net charge −7 to +4. Worth
    stating out loud rather than discovering later; `--use_soluble_model` is the
    usual lever if it becomes a problem.

→ Continue to [Step 5 · ESMFold validation](05-esmfold.md).
