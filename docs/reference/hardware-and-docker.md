# Hardware & the Docker plan

## Development hardware

| | |
|---|---|
| GPU | NVIDIA RTX 4050 Laptop, **6 GB VRAM** (Ada, compute capability **sm_89**) |
| Driver / CUDA | 595.71 / CUDA 13.2 capable |
| OS | Ubuntu (native Linux) |
| Package manager | conda + mamba via Miniforge |

**The 6 GB VRAM constraint drives two design choices:** keep binders **45–60
residues**, and feed RFdiffusion a **single myostatin chain** (not the dimer or
the full complex). On any CUDA out-of-memory error, reduce binder length and
target size *before* touching anything else.

**Ada (sm_89) compatibility:** PyTorch built for CUDA ≤ 11.1 lacks kernels that
run on Ada and fails with *"no kernel image is available for execution on the
device"*. We therefore use **CUDA 11.8** (conda-forge torch 2.3.1 + dgl 2.3.0 +
e3nn 0.5.6, solved together), whose Ampere `sm_86` kernels are forward-compatible
with Ada's `sm_89` (same major compute-capability 8.x). Verified with a live GPU
matmul and a dgl graph on the GPU.

## Why Docker was deferred (and the plan to add it)

Computational structural biology is the textbook case for "works on my machine"
failures — RFdiffusion couples a specific Python, a CUDA-matched PyTorch, `dgl`,
and the SE3Transformer. Docker is the standard way labs ship these tools, so it
genuinely adds value here. We deferred it on purpose:

- The core goal is learning the **design tools**, and learning
  `nvidia-container-toolkit` + GPU passthrough at the same time would compete for
  attention — especially on a 6 GB laptop.
- The repo is built to be **Docker-ready**: pinned versions, clean `envs/*.yml`,
  and a single `scripts/setup_rfdiffusion.sh` that already encodes the whole
  fragile install order. Turning that into a `Dockerfile` is then a short,
  focused exercise rather than a detour.

### Sketch of the eventual image

```dockerfile
# FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04
# - install miniforge
# - mamba env create -f envs/rfdiffusion.yml
# - run scripts/setup_rfdiffusion.sh
# - ENTRYPOINT into the rfdiffusion env
# Run with:  docker run --gpus all ...
```

The CPU-only ProteinMPNN and the API-only ESM steps don't need GPU images and
can stay as lightweight envs or their own small images.
