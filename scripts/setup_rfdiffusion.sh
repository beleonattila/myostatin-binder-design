#!/usr/bin/env bash
# =============================================================================
# setup_rfdiffusion.sh  —  install the from-source pieces AFTER the conda env
# =============================================================================
# Run once, with the `rfdiffusion` env ACTIVE:
#     mamba activate rfdiffusion
#     scripts/setup_rfdiffusion.sh
#
# envs/rfdiffusion.yml already provides the full coherent GPU stack (pytorch +
# dgl + e3nn on CUDA 11.8, all from conda-forge). This script only adds the two
# things that must come from source, plus the model weights:
#   1. RFdiffusion + its bundled SE3Transformer  (editable, --no-deps)
#   2. binder/PPI model weights (~1 GB)
#
# WHY --no-deps: RFdiffusion's setup.py declares install_requires=['torch',
# 'se3-transformer']. Without --no-deps, pip would try to "satisfy" torch from
# PyPI and UPGRADE the conda CUDA build off cu118 (this exact bug broke earlier
# attempts: dgl then failed with libcudart.so.11 / undefined-symbol errors).
# Everything torch needs is already in the conda env, so --no-deps is correct.
# -----------------------------------------------------------------------------
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [[ "${CONDA_DEFAULT_ENV:-}" != "rfdiffusion" ]]; then
  echo "ERROR: activate the env first ->  mamba activate rfdiffusion" >&2
  exit 1
fi

echo "[1/3] Clone RFdiffusion (if missing) ..."
[[ -d RFdiffusion ]] || git clone https://github.com/RosettaCommons/RFdiffusion.git

echo "[2/3] Editable install of RFdiffusion + SE3Transformer (--no-deps) ..."
python -m pip install --no-deps --no-build-isolation -e RFdiffusion/env/SE3Transformer
python -m pip install --no-deps --no-build-isolation -e RFdiffusion

echo "[3/3] Download binder-design model weights (~1 GB) ..."
mkdir -p RFdiffusion/models
cd RFdiffusion/models
[[ -f Base_ckpt.pt ]]         || wget -q --show-progress http://files.ipd.uw.edu/pub/RFdiffusion/6f5902ac237024bdd0c176cb93063dc4/Base_ckpt.pt
[[ -f Complex_base_ckpt.pt ]] || wget -q --show-progress http://files.ipd.uw.edu/pub/RFdiffusion/e29311f6f1bf1af907f9ef9f44b8328b/Complex_base_ckpt.pt
cd "$ROOT"

echo
echo "Sanity check (fails loudly if the GPU stack isn't coherent):"
python - <<'PY'
import torch
print("  torch:", torch.__version__, "| CUDA available:", torch.cuda.is_available())
assert torch.cuda.is_available(), "CUDA not available"
import dgl;  print("  dgl  :", dgl.__version__, "(imports cleanly)")
import e3nn; print("  e3nn :", e3nn.__version__)
from se3_transformer.model import basis  # exercises torch+dgl+e3nn together
print("  SE3Transformer basis import: OK")
print("  OK -> ready for Step 3 (RFdiffusion inference)")
PY
