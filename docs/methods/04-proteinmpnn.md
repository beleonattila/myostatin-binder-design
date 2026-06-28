# Step 4 · ProteinMPNN (sequence design)

**Goal:** assign amino-acid sequences to the binder backbone — keeping the
myostatin target sequence fixed, designing only the binder chain.

**Environment:** `proteinmpnn` (CPU is fine at our scale).

```bash
mamba env create -f envs/proteinmpnn.yml
git clone https://github.com/dauparas/ProteinMPNN.git   # runs from the clone
```

## Run

```bash
mamba activate proteinmpnn
cd ProteinMPNN
python protein_mpnn_run.py \
  --pdb_path ../myostatin_test/rfdiffusion/outputs/design_0.pdb \
  --pdb_path_chains_to_design "B" \
  --out_folder ../myostatin_test/proteinmpnn/outputs/ \
  --num_seq_per_target 8 \
  --sampling_temp "0.1" \
  --seed 42 --batch_size 1
```

| Parameter | Meaning | Setting |
|---|---|---|
| `--pdb_path_chains_to_design` | chain(s) to redesign | the **binder** chain (check in PyMOL — usually `B`) |
| `--num_seq_per_target` | sequences per backbone | 8 to test, 32–64 for real sampling |
| `--sampling_temp` | diversity | 0.1 conservative, 0.2 for more diversity |

## Reading the output

- A FASTA with N sequences per backbone, each carrying a **log-likelihood score**
  (more negative = better in ProteinMPNN's convention).
- Sequences ~45–60 aa, no `X`, no stop codons.
- If all sequences look identical, **raise `sampling_temp` to 0.2** — diversity is
  what gives you multiple candidates to validate.

→ Continue to [Step 5 · ESMFold validation](05-esmfold.md).
