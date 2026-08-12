# De Novo Miniprotein Binder Design Against Myostatin (GDF-8)

> Designing synthetic ActRIIB mimics that occupy the type II (knuckle) epitope of
> myostatin, using **RFdiffusion → ProteinMPNN → ESMFold**.

This repository is a reproducible, end-to-end pipeline for generating and
validating de novo helical miniprotein binders against the receptor-binding
surface of myostatin. It is built to be read and re-run by someone with a
background in biology/bioinformatics: the prose explains the *biology*, the
scripts and environment files explain the *how*.

---

## Scientific summary

Myostatin (GDF-8) is a TGF-β-superfamily ligand that limits skeletal muscle
growth. It signals by recruiting the **type II receptor ActRIIB**, which docks
onto the **convex "knuckle" surface of one ligand monomer's β-fingers** — a
compact, hydrophobic-dominated epitope. Blocking that interaction is a validated
therapeutic strategy for muscle-wasting and metabolic disease.

A successful de novo binder here is, in effect, a **synthetic ActRIIB
antagonist**: a small (45–60 residue) protein engineered to sit on the knuckle
and out-compete the receptor for it. Note the mechanism precisely — it works by
covering ActRIIB's footprint *on the ligand*, not by reproducing the receptor's
own binding surface. See [`docs/concepts/`](docs/concepts/tgf-beta-receptors.md)
for the full structural rationale, and [`CONTEXT.md`](CONTEXT.md) for the design
decision log.

---

## The pipeline

| Step | Tool | Input → Output | Environment |
|---|---|---|---|
| 1 · Target prep | PyMOL / Biopython | PDB **5JI1** (apo GDF8) → clean myostatin target | (none / `esm`) |
| 2 · Hotspots | PyMOL | **6MAC** (GDF11:ActRIIB) superposition → knuckle residue list | (none) |
| 3 · Backbones | **RFdiffusion** | target + hotspots → backbone PDBs | `rfdiffusion` |
| 4 · Sequences | **ProteinMPNN** | backbone → FASTA sequences | `proteinmpnn` |
| 5 · Validation | **ESMFold** (API) | sequence → predicted structure + pLDDT/pTM | `esm` |
| 6 · Ranking | pandas / TMalign | metrics → ranked top designs | `esm` |

Validation (steps 5–6) is **not optional**: refolding each designed sequence
with ESMFold and checking it returns to the intended backbone (RMSD < 2 Å,
pTM > 0.7) is what separates a real design exercise from "pressing buttons".

---

## Quickstart

```bash
# 0. Prerequisites: a CUDA GPU + NVIDIA driver, and conda/mamba (Miniforge).
git clone <your-fork-url> myostatin_binder && cd myostatin_binder

# 1. Create the per-tool environments (one command each — the "dependency list")
mamba env create -f envs/rfdiffusion.yml
mamba env create -f envs/proteinmpnn.yml
mamba env create -f envs/esm.yml

# 2. Add RFdiffusion itself (--no-deps) + model weights (env already has torch/dgl/e3nn)
mamba activate rfdiffusion && scripts/setup_rfdiffusion.sh

# 3. Clone the tool repos that run from-source
git clone https://github.com/dauparas/ProteinMPNN.git
```

Then follow the per-step instructions in [`docs/methods/`](docs/methods/).

---

## Environments & dependencies

Each tool gets **its own conda environment** — they have conflicting, binary
(CUDA/Python-version) dependencies and must not be merged. The `envs/*.yml`
files *are* the dependency manifest: one `mamba env create -f` per file installs
everything for that block.

| File | Env | Why it exists / notable choices |
|---|---|---|
| `envs/rfdiffusion.yml` | `rfdiffusion` | The whole GPU stack (PyTorch + dgl + e3nn) is solved as **one coherent conda-forge install on CUDA 11.8** — verified: torch 2.3.1, dgl 2.3.0, e3nn 0.5.6. `scripts/setup_rfdiffusion.sh` then adds RFdiffusion itself (`--no-deps`) + weights. **CUDA 11.8** is required for Ada GPUs (sm_89) — the upstream cu11.1 pin fails on RTX 40-series. |
| `envs/proteinmpnn.yml` | `proteinmpnn` | CPU-only PyTorch (pip wheel, ~190 MB) — sufficient at 45–60 residues and far smaller than the CUDA build. |
| `envs/esm.yml` | `esm` | API client + analysis only (requests, biopython, pandas, TMalign). ESMFold folding runs server-side via REST, so no local GPU/torch. |
| `envs/docs.yml` | `docs` | MkDocs Material only — no coupling to the science stack. Pins `mkdocs<2`, since upstream MkDocs 2.0 drops the plugin system with no migration path. |

> **Hard-won lesson encoded in these files:** in a CUDA stack, never let `pip`
> resolve an unpinned `torch` — a package like `e3nn` will silently upgrade
> PyTorch off the CUDA build you chose (breaking dgl's ABI with
> `libcudart.so.11`/`undefined symbol` errors). The fix that actually held:
> solve the **entire** GPU stack from conda-forge in one go, and install
> RFdiffusion itself with `pip --no-deps` so it can't perturb that stack. See the
> comments in `envs/rfdiffusion.yml` and `scripts/setup_rfdiffusion.sh`.

### Why not Docker (yet)?

This stack is the poster child for "works on my machine" failures, so Docker
genuinely adds value here. We **deferred** it deliberately: the repo is built to
be *Docker-ready* (pinned versions, clean env files, a setup script) so adding a
`Dockerfile` later is a short, focused exercise — without letting
`nvidia-container-toolkit` + GPU passthrough compete with the core goal of
learning the design tools. See [`docs/reference/`](docs/reference/) for the plan.

---

## Documentation

All documentation — theory and runnable protocol alike — lives in
[`docs/`](docs/index.md) and builds into a searchable site with MkDocs Material.
It is also browsable directly on GitHub, or as an Obsidian vault pointed at
`docs/`.

```bash
make envs-docs    # one-time: create the `docs` conda env from envs/docs.yml
make docs         # live preview at http://127.0.0.1:8000
make docs-build   # render into ./site (strict — fails on broken links)
```

- `docs/concepts/` — the theory: TGF-β superfamily and receptor logic, the
  knuckle epitope, PPI hotspots, diffusion models, inverse folding, the
  end-to-end pipeline, validation metrics
- `docs/molecules/` — the cast: GDF8, GDF11, ActRIIB, follistatin-288, and the
  key PDB structures (5JI1, 6MAC, 3HH2)
- `docs/tools/` — what each program does: RFdiffusion, ProteinMPNN, ESMFold,
  AlphaFold2, PyMOL, TMalign
- `docs/methods/` — step-by-step, runnable method notes (steps 1–6)
- `docs/reference/` — glossary, hardware notes, the Docker plan

---

## Learning path

Where `docs/` is organised for **random access**, [`SYLLABUS.md`](SYLLABUS.md)
imposes an **order** on it: a 0–7 module curriculum for building defensible
competence in RFdiffusion + ProteinMPNN. Each module pairs an action with the
theory to hold first, links to the relevant `docs/` pages, and states the
one-sentence claim you should be able to defend afterwards.

---

## Hardware this was developed on

- **GPU:** NVIDIA RTX 4050 Laptop, **6 GB VRAM** (Ada / sm_89), driver 595.71, CUDA 13.2 capable
- **OS:** Ubuntu (native Linux), conda/mamba via Miniforge
- **Constraint:** 6 GB VRAM → keep binders **45–60 residues** and the target to a
  single myostatin chain; reduce sizes first on any CUDA OOM.

---

## Status

Pipeline scaffolding, environments, and docs are in place. Execution of the
scientific steps is tracked in [`CONTEXT.md`](CONTEXT.md#status-tracker).

## License & citation

MIT (see [`LICENSE`](LICENSE)). If you use this work, please cite via the
"Cite this repository" button (metadata in [`CITATION.cff`](CITATION.cff)).
Underlying tools — RFdiffusion (Watson et al. 2023), ProteinMPNN (Dauparas et
al. 2022), ESMFold (Lin et al. 2023) — should be cited directly; see
[`docs/`](docs/) for the reference list.
