# Final design panel — myostatin (GDF-8) knuckle binders

Selected 2026-09-26 by `scripts/06_rank.py --axis interface`
from the 58 self-consistent sequences of Step 5.

## The ranking axis

Steps 3 and 5 disagreed about which design leads. They were not two candidate
rankings — they measure different things, and only one of them is a threshold.

**Designability is a gate, not a score.** A sequence that does not fold back to
the backbone it was designed for has no interface: its buried area describes a
structure that will not exist. So it is applied first, pass/fail, and nothing
below the bar is ranked.

**Interface area is the objective.** Among sequences that do fold as designed,
burying more of the ActRIIB knuckle is what makes a better binder candidate.

**Diversity is a constraint.** Each backbone contributes at most one
representative — its best-refolding gated sequence — so this panel is five
distinct folds, not one fold spelled five ways.

### The gate

| Criterion | Bar | Why |
|---|---|---|
| Self-consistent (Step 5) | pass | RMSD < 2 Å, pLDDT ≥ 70, TM ≥ 0.5, coverage ≥ 0.90 |
| Cα-RMSD to design | ≤ 1.0 Å | the conventional designable-minibinder bar |
| TM-score | ≥ 0.90 | the same fold, not merely the same class of fold |
| Coverage | = 1.00 | every residue aligned — the design_5 lesson |
| Mean pLDDT | ≥ 85 | confident model |
| Min pLDDT | ≥ 70 | no floppy terminus inside a good average |

**41 of 58** self-consistent sequences clear it, and every one of the
eight shortlisted backbones keeps at least one. That is what dissolves the
argument: design_5, the interface leader that failed Step 5 at the backbone
level, keeps exactly one sequence — `design_5_s2` — and it is enough to carry
the widest interface into the panel on merit.

### One refinement

dSASA is a backbone+CB **lower bound**: Step 3 calibrated the real
ActRIIB:GDF11 interface at 293 Å² in these units versus 697 Å² full-atom, so
sidechains carry 58 % of a real interface. Differences of a few Å² are noise.
Representatives within **10 Å²** of each other are treated as tied
and ordered by designability instead.

4 representatives fall in one band (406 → 402 Å²) and are ordered by designability: `design_12` (402 Å², 7/8 gated), `design_11` (402 Å², 6/8 gated), `design_14` (404 Å², 5/8 gated), `design_15` (406 Å², 4/8 gated). This band straddles the cut: `design_15` misses the panel on an interface difference of 4 Å², which this representation cannot resolve — designability decides it.

## The panel

Bold rows are the selected 5. One representative per backbone, ranked by
interface area under the tie rule above.

| # | Sequence | Buried Å² | Contacts | Hotspots | RMSD Å | pLDDT | Gated | Rg ratio | Charge | Hotspot φ |
|---|---|---|---|---|---|---|---|---|---|---|
| **1** | **`design_5_s2`** | 469 | 12 | 6/6 | 0.48 | 85.5 | 1/8 | 1.29 | -2 | 0.54 |
| **2** | **`design_18_s4`** | 448 | 9 | 6/6 | 0.45 | 91.6 | 4/8 | 1.28 | -2 | 0.67 |
| **3** | **`design_12_s4`** | 402 | 8 | 6/6 | 0.40 | 90.2 | 7/8 | 1.29 | +3 | 0.55 |
| **4** | **`design_11_s7`** | 402 | 11 | 6/6 | 0.42 | 89.1 | 6/8 | 1.30 | +2 | 0.70 |
| **5** | **`design_14_s7`** | 404 | 10 | 6/6 | 0.43 | 93.1 | 5/8 | 1.06 | +0 | 0.58 |
| 6 | `design_15_s5` | 406 | 9 | 6/6 | 0.45 | 90.3 | 4/8 | 1.29 | -4 | 0.40 |
| 7 | `design_4_s5` | 385 | 11 | 6/6 | 0.47 | 91.2 | 8/8 | 1.27 | -3 | 0.43 |
| 8 | `design_9_s1` | 370 | 8 | 6/6 | 0.71 | 87.9 | 6/8 | 1.34 | -1 | 0.50 |

*Gated = how many of that backbone's 8 sequences clear the gate; a robustness
measure, not a rank term. Hotspot φ = hydrophobic fraction of the
hotspot-contacting positions. Rg ratio = radius of gyration over the folded
expectation for that length; 1.0 is ideal, > 1.5 was rejected in Step 3.*

## If only one is made: `0`

It leads on interface (469 Å², 12 contacts, all six
hotspots) and it refolds at 0.48 Å with pLDDT
85.5. **But note the risk column**: only
1 of its 8 sequences clear the gate. Its
backbone is a helical hairpin, and for five of eight sequences ESMFold predicts
one long straight helix instead — confidently. That is the highest-variance
choice in the panel.

**The lowest-variance choice is `design_14_s7`**, and if the goal is one design
that works rather than the largest interface, prefer it:

- interface statistically indistinguishable from the middle of the panel
  (404 Å² vs 402 Å²), well above the real receptor's 293 Å²
- the **most compact backbone of the twenty** (Rg ratio 1.06 against 1.06–1.34
  for the passes) — the most protein-like thing RFdiffusion produced here
- the **highest confidence of any representative** (pLDDT 93.1), refolding at
  0.43 Å
- **net charge 0**, against −7…+4 across the set: the one design that largely
  escapes ProteinMPNN's over-charging bias, which is the main expression
  liability in this batch

## What this panel is and is not

It is five in-silico designs that satisfy an interface objective and a
self-consistency gate. That is the whole claim.

- **No binding has been demonstrated.** Self-consistency says a sequence folds
  to its intended backbone; it says nothing about whether that fold binds
  myostatin, or with what affinity.
- **The interface numbers are lower bounds** measured on backbone+CB, and they
  come from RFdiffusion's own docking, not from an independent evaluation.
- **ESMFold is a fallible judge**, and it has a known bias toward isolated
  helices. `design_5`'s 1/8 rate may reflect that bias as much as a real flaw.
- **The sequences are E/K/A-rich** (see `eka_frac` in `ranking.tsv`), a known
  ProteinMPNN tendency and a real liability for expression and non-specific
  binding. `--use_soluble_model` is the lever if this panel is ever made.
- The obvious next computational step is an orthogonal check that this pipeline
  never ran: independent complex prediction (AlphaFold-Multimer or Boltz) of
  binder + target, to test the *interface* rather than the monomer fold.

## Files

| File | Contents |
|---|---|
| `README.md` | this write-up |
| `ranking.tsv` | all 64 sequences, gate status and every metric |
| `panel.fasta` | the 5 selected sequences |
| `figures/` | one render per selection, plus the panel overview |
| `complexes/` | each prediction superposed onto the target, as a PDB |

Regenerate with `make rank`.
