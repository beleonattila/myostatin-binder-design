# =============================================================================
# Makefile — named, self-documenting entry points for the pipeline.
# Run `make` (or `make help`) to list every target.
# =============================================================================
# IMPORTANT: make runs each recipe in a NON-interactive shell that never reads
# ~/.bashrc, so the `conda` set up by `conda init` is NOT available by default.
# We therefore (1) force bash and (2) `source` conda's profile script in every
# recipe that needs conda. CONDA_BASE is auto-detected, falling back to the
# default Miniforge location.
SHELL := /bin/bash
CONDA_BASE := $(shell conda info --base 2>/dev/null || echo $(HOME)/miniforge3)
ACTIVATE   := source $(CONDA_BASE)/etc/profile.d/conda.sh   # makes conda/mamba usable
RUN        := conda run --no-capture-output -n              # run a command inside an env

.DEFAULT_GOAL := help

.PHONY: help \
        envs envs-rfdiffusion envs-proteinmpnn envs-esm setup-rfdiffusion \
        gpu-check verify verify-rfdiffusion verify-proteinmpnn verify-esm \
        docs docs-build clean-docs

help:  ## Show this help (the list of targets)
	@grep -E '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-22s\033[0m %s\n", $$1, $$2}'

# --- Environments ------------------------------------------------------------
envs: envs-rfdiffusion envs-proteinmpnn envs-esm  ## Create all three conda envs

envs-rfdiffusion:  ## Create the rfdiffusion env (then run `make setup-rfdiffusion`)
	$(ACTIVATE) && mamba env create -f envs/rfdiffusion.yml

envs-proteinmpnn:  ## Create the proteinmpnn env (CPU torch)
	$(ACTIVATE) && mamba env create -f envs/proteinmpnn.yml

envs-esm:  ## Create the esm validation env
	$(ACTIVATE) && mamba env create -f envs/esm.yml

setup-rfdiffusion:  ## Install RFdiffusion (--no-deps) + model weights (env must exist)
	$(ACTIVATE) && $(RUN) rfdiffusion bash scripts/setup_rfdiffusion.sh

# --- Verification ------------------------------------------------------------
verify: verify-rfdiffusion verify-proteinmpnn verify-esm  ## Check all three envs

gpu-check:  ## Quick: does PyTorch see the GPU in the rfdiffusion env?
	$(ACTIVATE) && $(RUN) rfdiffusion python -c "import torch; print('CUDA available:', torch.cuda.is_available(), '|', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'no GPU')"

verify-rfdiffusion:  ## Full GPU stack: torch + dgl + e3nn + SE3Transformer + a GPU op
	$(ACTIVATE) && $(RUN) rfdiffusion python -c "import torch,dgl,e3nn; from se3_transformer.model import basis; \
x=torch.randn(512,512,device='cuda'); torch.cuda.synchronize(); \
g=dgl.graph(([0,1],[1,0])).to('cuda'); \
print('rfdiffusion OK | torch',torch.__version__,'cuda',torch.cuda.is_available(),'| dgl',dgl.__version__,'| e3nn',e3nn.__version__,'| dgl graph on',str(g.device))"

verify-proteinmpnn:  ## Check the proteinmpnn env imports
	$(ACTIVATE) && $(RUN) proteinmpnn python -c "import torch,numpy; print('proteinmpnn OK | torch',torch.__version__,'| numpy',numpy.__version__)"

verify-esm:  ## Check the esm env (client libs + TMalign)
	$(ACTIVATE) && $(RUN) esm python -c "import requests,Bio,pandas,numpy; print('esm OK | biopython',Bio.__version__)"
	@$(ACTIVATE) && $(RUN) esm which TMalign >/dev/null && echo "esm OK | TMalign present" || echo "esm WARN | TMalign missing"

# --- Docs --------------------------------------------------------------------
docs:  ## Serve the documentation site locally (needs: pip install mkdocs-material)
	mkdocs serve

docs-build:  ## Build the static documentation site into ./site
	mkdocs build

clean-docs:  ## Remove the built docs site
	rm -rf site/
