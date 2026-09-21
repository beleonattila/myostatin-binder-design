#!/usr/bin/env bash
# Step 3 - RFdiffusion binder backbone generation against the myostatin knuckle.
#
# Usage:  conda activate rfdiffusion && scripts/03_rfdiffusion.sh [NUM_DESIGNS]
#         (defaults to 20; pass 1 for a smoke test)
#
# Output: rfdiffusion/outputs/design_N.pdb   backbone-only, binder + target
#         rfdiffusion/outputs/design_N.trb   the contig mapping / metadata
#         rfdiffusion/outputs/traj/          denoising trajectories
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
NUM_DESIGNS="${1:-20}"

# --- the two settings that are easy to get wrong ------------------------------
#
# CONTIGS: the target is given as TWO fragments, not one range. 5JI1 chain A is
# unresolved at 51-64, so `A1-109` would ask RFdiffusion for coordinates that do
# not exist. Written as `A1-50/A65-109`, the contig parser inserts a residue-index
# jump of exactly 14 between the fragments (contigs.py: idx_jump = 65-50-1),
# so the model sees the real sequence separation rather than a false bond.
# The trailing `/0` marks the end of the receptor chain; ` 45-60` (whitespace-
# separated) is the binder, whose length is sampled per design.
#
# HOTSPOTS: matched against the INPUT pdb numbering (model_runners.py compares
# against contig_map.con_ref_pdb_idx), so these are chain A, mature numbering --
# exactly what hotspots/hotspot_residues.txt records. No renumbering.
CONTIGS='contigmap.contigs=[A1-50/A65-109/0 45-60]'
HOTSPOTS='ppi.hotspot_res=[A33,A34,A85,A87,A93,A95]'

# noise_scale 0: RFdiffusion's authors recommend removing the sampling noise for
# PPI/binder design. It trades topological diversity for designability, and with
# only ~20 designs on one GPU we want the hit rate, not the variety.
# empty_cache_per_design: 6 GB of VRAM, ~140-155 total residues -- free the
# allocator between designs so fragmentation does not accumulate into an OOM.
cd "$ROOT/RFdiffusion"
python scripts/run_inference.py \
  inference.input_pdb="$ROOT/data/prepared/myostatin_target.pdb" \
  inference.output_prefix="$ROOT/rfdiffusion/outputs/design" \
  "$CONTIGS" \
  "$HOTSPOTS" \
  inference.num_designs="$NUM_DESIGNS" \
  diffuser.T=50 \
  denoiser.noise_scale_ca=0 \
  denoiser.noise_scale_frame=0 \
  inference.empty_cache_per_design=True \
  hydra.run.dir="$ROOT/rfdiffusion/logs"
