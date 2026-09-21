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

Use `scripts/03_rfdiffusion.sh` (it encodes everything below):

```bash
conda activate rfdiffusion
scripts/03_rfdiffusion.sh 20        # pass 1 for a smoke test first
```

which runs, from the `RFdiffusion/` clone:

```bash
python scripts/run_inference.py \
  inference.input_pdb=.../data/prepared/myostatin_target.pdb \
  inference.output_prefix=.../rfdiffusion/outputs/design \
  'contigmap.contigs=[A1-50/A65-109/0 45-60]' \
  'ppi.hotspot_res=[A33,A34,A85,A87,A93,A95]' \
  inference.num_designs=20 \
  diffuser.T=50 \
  denoiser.noise_scale_ca=0 \
  denoiser.noise_scale_frame=0 \
  inference.empty_cache_per_design=True
```

| Parameter | Meaning | Setting |
|---|---|---|
| `contigmap.contigs` | target fragments / binder length | `[A1-50/A65-109/0 45-60]` — **two fragments**, see below |
| `ppi.hotspot_res` | residues the binder must contact | the **verified** Step 2 list, in *input-PDB* numbering |
| `inference.num_designs` | backbone attempts | 20 to test, 100+ for real work |
| `diffuser.T` | denoising steps | 50 — what `Complex_base_ckpt.pt` was trained with |
| `denoiser.noise_scale_ca/_frame` | sampling noise | **0** for binder design |

!!! danger "`denoising_steps` is not a real parameter"
    Earlier drafts of this page used `denoising_steps=50`. Hydra would reject it.
    The key is **`diffuser.T`**. And do not "raise it to 200 for final" — the
    complex checkpoint was *trained* at T=50; check the value inside the
    checkpoint (`ckpt['config_dict']['diffuser']['T']`) before overriding it.
    RFdiffusion prints a warning on any explicit override of a trained parameter,
    **even when the value you pass is identical**, so that warning alone doesn't
    mean you did anything wrong.

### The contig must name both fragments

5JI1 chain A is unresolved at 51–64. `A1-109` asks for coordinates that do not
exist. Written as `A1-50/A65-109`, the parser inserts a residue-index jump of
exactly 14 between the fragments (`contigs.py`: `idx_jump = 65-50-1`), so the
model sees the true sequence separation instead of a false bond. The trailing
`/0` closes the receptor chain; the whitespace-separated ` 45-60` is the binder,
whose length is sampled per design.

### Why noise_scale=0

RFdiffusion's authors recommend removing sampling noise for PPI work. It trades
topological diversity for designability — with ~20 designs on one GPU, take the
hit rate.

Binder length **45–60** respects the 6 GB VRAM budget (~140–155 total residues,
~0.8 min/design on an RTX 4050). On CUDA OOM, shrink the binder first.

## Reading the output

- `design_N.pdb` — **chain A is the target** (5JI1 mature numbering, gap intact),
  **chain B is the binder** (numbered from 1). Step 2 hotspots apply unchanged.
- `design_N.trb` — the contig mapping and the full resolved config. This is where
  you check what actually ran (`config`, `sampled_mask`).
- **Good:** compact helical binder packed onto the hotspots, no clashes.
- **Bad:** binder floating away, extended/coil, on the wrong face.

!!! warning "The output is backbone-only — N, CA, C, O, and no CB"
    This catches everyone. Score these files naively and *every* design looks
    like a floater: buried area lands near 100 Å² and a 5 Å contact search finds
    two or three residues. That is the **missing sidechain layer**, not a failed
    dock. A well-packed interface shows a **4–8 Å backbone-to-backbone gap**,
    because that is the space sidechains occupy.

    Two corrections make the numbers meaningful, both in
    `scripts/03b_triage_backbones.py`:

    1. **Restore the target's sidechains.** The target is rigid during diffusion
       (motif RMSD ≈ 0.13 Å), so superpose `myostatin_target.pdb` back onto the
       output's chain A.
    2. **Build virtual CB** on the binder from N/CA/C
       (`CB = -0.58273431·a + 0.56802827·b - 0.54067466·c + CA`, where
       `b = CA-N`, `c = C-CA`, `a = b×c`). Verified against real CB atoms here:
       mean deviation **0.040 Å**.

    Then **set `vdw=1.7` on those pseudoatoms**. PyMOL creates pseudoatoms with
    `vdw=1.0` whatever `elem` you pass, which silently shrank every buried-area
    number by ~35 % until it was caught.

### Calibrate against a real interface

Absolute Å² means nothing until you know what good looks like *in the same
representation*. Scoring the genuine ActRIIB:GDF11 interface (6MAC) both ways:

| Representation | Buried area | Ligand residues contacted |
|---|---|---|
| Full atom | **697 Å²** | 22 |
| Backbone + CB | **293 Å²** | 9 |

So sidechains carry **58 %** of a real interface — backbone-only numbers are a
lower bound, and ProteinMPNN supplies the remaining ~2.4× in Step 4. Treat this
as a **floor** for "is it docked at all", not a quality bar: ActRIIB binds via
sidechain knobs off a β-sheet while these designs pack helices flat, so backbone
burial is not strictly comparable across the two binding modes.

Run the triage, then open the survivors in PyMOL:

```bash
conda activate esm && python scripts/03b_triage_backbones.py
```

It writes `rfdiffusion/outputs/triage.tsv` and marks a shortlist for ProteinMPNN.
→ Continue to [Step 4 · ProteinMPNN](04-proteinmpnn.md).
