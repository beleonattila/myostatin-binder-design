# RFdiffusion

**Stage 1 — backbone generation.** Generates novel protein backbones conditioned on your target and hotspots. Outputs geometry only — no sequence.

| Field | Value |
|-------|-------|
| Paper | Watson et al., "De novo design of protein structure and function with RFdiffusion", *Nature* 620, 1089–1100 (2023) |
| Lab | Baker lab, IPD, University of Washington |
| Repo | github.com/RosettaCommons/RFdiffusion |
| Type | Denoising diffusion probabilistic model (DDPM) built on RoseTTAFold |
| Input | Target PDB + hotspot residues + contig spec |
| Output | Backbone PDB(s), no sequence |
| Needs GPU | Yes |

Prerequisite theory: [diffusion models](../concepts/diffusion-models.md). Downstream: [ProteinMPNN](ProteinMPNN.md).

---

## What it actually is

RFdiffusion is the **RoseTTAFold structure-prediction network, fine-tuned to run in reverse as a generative denoising model.** The insight of the paper: rather than build a protein diffusion model from scratch (which had underperformed), take a network that already encodes deep priors about protein structure from the PDB and re-purpose it to denoise.

Two framings to keep straight:
- In **RoseTTAFold** (prediction): input is primarily *sequence*, output is *structure*.
- In **RFdiffusion** (generation): input is *noised residue frames* (coordinates + orientations), output is the predicted *clean* structure at each denoising step.

The forward (training) process progressively corrupts real PDB structures — Gaussian noise on Cα translations, Brownian rotation on residue orientations — over ~200 steps until they are random. The network learns to reverse this. At inference you **start from random frames and denoise**, over 50–200 steps, into a coherent backbone. A **self-conditioning** trick feeds the previous step's prediction back in as a template, which keeps trajectories coherent.

---

## Why this matters for *your* project

You are using the **protein–protein interaction (PPI) binder** mode. You supply:
- a **target** (apo [GDF8](../molecules/GDF8.md), from [5JI1](../molecules/5JI1.md)) held fixed, and
- **hotspot residues** on the target (from [6MAC](../molecules/6MAC.md), the ActRIIB epitope),

and RFdiffusion generates a **new binder backbone** constrained to fold up against the target and make contact at those hotspots. It inherits the PDB's structural priors, so it produces physically plausible folds (helical bundles, mixed α/β) without you specifying a topology.

Crucially: **the output is backbone-only.** The residues are placeholder (often poly-glycine / Cα trace). It has decided *shape*, not *identity*. Assigning amino acids is the next tool's job → [ProteinMPNN](ProteinMPNN.md). Conflating these two is the most common conceptual error; don't.

---

## The parameters you'll set

| Parameter | Controls | Starting value |
|-----------|----------|----------------|
| `inference.input_pdb` | target structure | `data/prepared/myostatin_target.pdb` |
| `contigmap.contigs` | which target residues to keep + binder length range | e.g. `[A1-109/0 50-70]` |
| `ppi.hotspot_res` | target residues the binder must contact | your ActRIIB-epitope hotspots |
| `inference.num_designs` | how many backbones | 20 for learning, 100+ for real |
| `denoising_steps` (a.k.a. `diffuser.T` / `inference.final_step`) | quality vs speed | 50 test, up to 200 final |

Contig syntax reads like: keep target chain A residues 1–109, chain break (`/0`), then design a new chain of 50–70 residues. Verify the exact chain ID and residue range against your cleaned target — do not copy a range blindly.

---

## Reading the output

Watch during the run:
- **Loss should decrease** across denoising steps. Spikes or `NaN` usually mean GPU OOM or a malformed input PDB (leftover HETATM, altlocs, missing backbone atoms).
- Per-design scores are printed but are **proxies**, not the final verdict.

Triage each output backbone in [PyMOL](PyMOL.md) against the target:

| Good | Bad |
|------|-----|
| Compact helical/mixed binder | Extended coil, no secondary structure |
| Buried contact at the hotspots | Binder floating off the surface |
| Clean interface, no clashes | Binder on the wrong face |
| 40–70 residues, single domain | Fragmented / tangled |

Keep 5–10 good backbones for sequence design.

---

## Install / run reality

- **Local (WSL2 + CUDA):** conda env, PyTorch matched to your CUDA, `pip install -e .`, SE3/`dgl`/`e3nn` deps, download model weights (~1.5 GB).
- **No local GPU:** use the Baker/Sokrypton ColabDesign RFdiffusion notebook; upload your target PDB, run the binder section, download backbones, continue the rest of the pipeline locally.

See [Step 3 · RFdiffusion](../methods/03-rfdiffusion.md) for the runnable recipe, and `SYLLABUS.md` Module 4 / `CONTEXT.md` at the repo root for the exact commands and their rationale.

---

## What to be able to say

*"RFdiffusion is a fine-tuned RoseTTAFold run as a denoising diffusion model; I used its PPI binder mode, conditioning on the apo-GDF8 target and the ActRIIB-epitope hotspots, to generate backbone-only binder scaffolds — sequence assignment was a separate downstream step."*

---

## Links

- Theory it rests on: [diffusion models](../concepts/diffusion-models.md)
- Where its inputs come from: [5JI1](../molecules/5JI1.md) (target), [6MAC](../molecules/6MAC.md) (hotspots)
- What consumes its output: [ProteinMPNN](ProteinMPNN.md)
- Pipeline overview: [de novo binder design](../concepts/de-novo-binder-design.md)
- Triage tool: [PyMOL](PyMOL.md)
