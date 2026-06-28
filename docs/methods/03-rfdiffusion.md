# Step 3 · RFdiffusion (backbone generation)

**Goal:** generate de novo binder **backbones** docked against the knuckle
hotspots. Output is backbone-only — no sequence yet.

**Environment:** `rfdiffusion` (GPU). Set it up once:

```bash
mamba env create -f envs/rfdiffusion.yml      # base interpreter
mamba activate rfdiffusion
scripts/setup_rfdiffusion.sh                  # torch+cu118, dgl, e3nn, SE3, weights
make gpu-check                                # confirm CUDA is visible
```

!!! note "Why our env diverges from upstream"
    The official `SE3nv.yml` pins CUDA 11.1, whose kernels stop at sm_86 and fail
    on Ada GPUs (RTX 40-series, sm_89) with *"no kernel image available"*. We
    instead solve the **entire** GPU stack from conda-forge on **CUDA 11.8** in
    one go (verified: torch 2.3.1, dgl 2.3.0, e3nn 0.5.6), and install RFdiffusion
    with `pip --no-deps` so nothing can move torch off that build. See
    `envs/rfdiffusion.yml` for the full reasoning.

## Run binder design

From the `RFdiffusion/` clone:

```bash
python scripts/run_inference.py \
  inference.output_prefix=../myostatin_test/rfdiffusion/outputs/design \
  inference.input_pdb=../myostatin_test/data/prepared/myostatin_target.pdb \
  'contigmap.contigs=[A1-109/0 45-60]' \
  'ppi.hotspot_res=[A33,A34,A35,A85,A86,A87]' \
  inference.num_designs=20 \
  denoising_steps=50
```

| Parameter | Meaning | Setting |
|---|---|---|
| `contigmap.contigs` | target range / binder length | `[A1-109/0 45-60]` — **match the resolved range** from Step 1 |
| `ppi.hotspot_res` | residues the binder must contact | your **verified** Step 2 list |
| `inference.num_designs` | backbone attempts | 20 to test, 100+ for real work |
| `denoising_steps` | quality vs speed | 50 to test, 200 for final |

Binder length **45–60** respects the 6 GB VRAM budget. On CUDA OOM, shrink the
binder/target first.

## Reading the output

- Files `design_0.pdb`, `design_1.pdb`, … are **backbones only** (poly-glycine /
  Cα trace), each with a small protein docked on the target.
- **Good:** compact helical binder physically touching the hotspots, no clashes.
- **Bad:** binder floating away, fully extended/coil, on the wrong face, or not
  contacting hotspots → re-check numbering and hotspots.

Open each in PyMOL alongside the target; keep the top 5–10 for ProteinMPNN.
→ Continue to [Step 4 · ProteinMPNN](04-proteinmpnn.md).
