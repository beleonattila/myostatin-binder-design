# =============================================================================
# Makefile — named, self-documenting entry points for the pipeline.
# `make` or `make help` lists the targets. This turns "the 6 steps" into
# reproducible commands so nobody has to remember long invocations.
# =============================================================================
# conda/mamba can't "activate" inside a recipe the way an interactive shell can,
# so we run each tool with `conda run -n <env> ...`.
CONDA_RUN = conda run --no-capture-output -n

.DEFAULT_GOAL := help

.PHONY: help envs envs-rfdiffusion envs-proteinmpnn envs-esm setup-rfdiffusion \
        gpu-check docs clean-docs

help:  ## Show this help
	@grep -E '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

# --- Environments ------------------------------------------------------------
envs: envs-rfdiffusion envs-proteinmpnn envs-esm  ## Create all three conda envs

envs-rfdiffusion:  ## Create the rfdiffusion env (then run setup-rfdiffusion)
	mamba env create -f envs/rfdiffusion.yml

envs-proteinmpnn:  ## Create the proteinmpnn env (CPU torch)
	mamba env create -f envs/proteinmpnn.yml

envs-esm:  ## Create the esm validation env
	mamba env create -f envs/esm.yml

setup-rfdiffusion:  ## Install RFdiffusion GPU chain + weights (env must exist)
	$(CONDA_RUN) rfdiffusion bash scripts/setup_rfdiffusion.sh

# --- Sanity checks -----------------------------------------------------------
gpu-check:  ## Confirm PyTorch sees the GPU in the rfdiffusion env
	$(CONDA_RUN) rfdiffusion python -c "import torch; print('CUDA available:', torch.cuda.is_available(), '|', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'no GPU')"

# --- Docs --------------------------------------------------------------------
docs:  ## Serve the documentation site locally (needs mkdocs-material)
	mkdocs serve

clean-docs:  ## Remove the built docs site
	rm -rf site/
