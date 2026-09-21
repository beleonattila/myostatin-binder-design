#!/usr/bin/env bash
# Step 4 - ProteinMPNN: assign sequences to the shortlisted binder backbones.
#
# Usage:  conda activate proteinmpnn && scripts/04_proteinmpnn.sh [N_SEQ]
#         (N_SEQ defaults to 8 sequences per backbone)
#
# Reads the shortlist straight out of rfdiffusion/outputs/triage.tsv so Step 3 and
# Step 4 cannot drift apart. Writes one FASTA per backbone to proteinmpnn/outputs/.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MPNN="$ROOT/ProteinMPNN"
TRIAGE="$ROOT/rfdiffusion/outputs/triage.tsv"
OUT="$ROOT/proteinmpnn/outputs"
N_SEQ="${1:-8}"

[[ -d "$MPNN" ]] || { echo "Clone ProteinMPNN into $MPNN first"; exit 1; }
[[ -f "$TRIAGE" ]] || { echo "Run scripts/03b_triage_backbones.py first"; exit 1; }

# column 'shortlisted' == True  ->  column 'design'  (sub() strips any trailing CR,
# which would otherwise live inside the value of the last field)
mapfile -t DESIGNS < <(awk -F'\t' '
  { sub(/\r$/, "") }
  NR==1 { for (i=1;i<=NF;i++) col[$i]=i; next }
  $col["shortlisted"]=="True" { print $col["design"] }' "$TRIAGE")

[[ ${#DESIGNS[@]} -gt 0 ]] || { echo "No shortlisted designs parsed from $TRIAGE"; exit 1; }

echo "Designing ${N_SEQ} sequences for each of ${#DESIGNS[@]} backbones: ${DESIGNS[*]}"
mkdir -p "$OUT"

# --- the choices that matter --------------------------------------------------
#
# --pdb_path_chains "B"  designs chain B and FIXES everything else (the script
#   derives fixed_chain_list as "all chains not listed"). Chain B is the binder;
#   chain A is myostatin. Getting this backwards redesigns the target.
#   NOTE the flag name: it is --pdb_path_chains, NOT --pdb_path_chains_to_design.
#
# Designing against the COMPLEX rather than the isolated binder is the whole
# point: ProteinMPNN sees myostatin's real sidechains (the target chain keeps its
# sequence in the RFdiffusion output - verified) and picks interface residues
# that complement them.
#
# --omit_AAs CX  drops cysteine. Standard practice for de novo binders: a free Cys
#   invites disulfide scrambling, and myostatin carries nine of its own (the
#   cystine knot plus the interchain bond), so an unpaired binder Cys is a real
#   aggregation and expression liability. X is the ProteinMPNN default.
#
# --model_name v_48_020  the vanilla weights trained with 0.20 A backbone noise -
#   the usual choice for RFdiffusion backbones, which are idealised and benefit
#   from a model that expects some coordinate slop.
#
# --sampling_temp 0.1  conservative. Raise to 0.2 if the sequences come out
#   near-identical; scripts/04b_analyze_sequences.py reports the diversity.
cd "$MPNN"
for d in "${DESIGNS[@]}"; do
  echo "  -> $d"
  python protein_mpnn_run.py \
    --pdb_path "$ROOT/rfdiffusion/outputs/${d}.pdb" \
    --pdb_path_chains "B" \
    --out_folder "$OUT" \
    --num_seq_per_target "$N_SEQ" \
    --sampling_temp "0.1" \
    --model_name "v_48_020" \
    --omit_AAs "CX" \
    --seed 42 \
    --batch_size 1
done

echo
echo "FASTAs in ${OUT}/seqs/"
ls -1 "$OUT/seqs/" 2>/dev/null || true
