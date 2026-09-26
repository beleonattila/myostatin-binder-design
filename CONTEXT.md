# De Novo Miniprotein Binder Design Against Myostatin
## Project CONTEXT — Claude Code Reference Document

**Owner:** Attila Beleon  
**Goal:** Learn RFDiffusion and ProteinMPNN by designing de novo helical binders targeting the ActRIIB-binding epitope of myostatin (GDF-8). Produce credible, interpretable outputs to demonstrate practical experience with these tools.  
**Environment:** Now executing on a **native Ubuntu** machine (RTX 4050, 6 GB) — the project has moved off the Windows host. Miniforge (conda+mamba) installed; the three tool environments are built and GPU-verified. See "Execution environment — LIVE STATUS" below.

> 📌 **This file is the decision log.** Polished, user-facing documentation now lives in `docs/` (an MkDocs site) and `README.md`. See "Repository structure & best practices" below for the full layout. Keep recording dated decisions/corrections here; keep the narrative explanations in `docs/`.

---

## Session Log — 2026-09-26 (Step 6 EXECUTED — panel of 5 selected; pipeline complete)

**Done:** the 58 survivors ranked and the final panel written to
`results/top_designs/` (README, `ranking.tsv`, `panel.fasta`, 5 complexes, 6
figures). Scripts: `scripts/06_rank.py`, `scripts/06c_render_top.py`. One
command: **`make rank`**.

**The ranking axis — the decision Step 5 left open.** Step 3 (buried area) and
Step 5 (designability) were never two candidate rankings. They measure different
things and only one is a threshold:

- **Designability is a GATE, not a score.** A sequence that does not fold to its
  designed backbone has no interface at all — its buried area describes a
  structure that will not exist. Applied first, pass/fail.
- **Interface area is the OBJECTIVE.** Among sequences that do fold, burying more
  of the knuckle is the thing we set out to make.
- **One representative per backbone is a CONSTRAINT.** Five sequences off one
  backbone are one design with five spellings.

**The gate** (stricter than Step 5's floor): self-consistent **and** RMSD ≤ 1.0 Å,
TM ≥ 0.90, coverage = 1.00, mean pLDDT ≥ 85, min pLDDT ≥ 70.
**41 of 58 clear it, and all 8 backbones keep at least one.** That is what
dissolved the argument: `design_5` keeps exactly one sequence (`s2`), and one is
enough to carry the widest interface into the panel on merit. No axis had to
lose.

**Tie band — the rule that actually decides a cut.** dSASA is a backbone+CB lower
bound (Step 3: real receptor 293 Å² in these units vs 697 Å² full-atom, so
sidechains are 58 % of a real interface). Differences of a few Å² are noise, so
representatives within **10 Å²** are tied and ordered by designability. Four land
in one band (406 → 402 Å²) and the band straddles the cut: **`design_15` misses
the panel on a 4 Å² difference the representation cannot resolve.** `06_rank.py`
prints every band into the README rather than hiding it — a rule that decides a
cut has to be visible.

**The panel:**

| # | Sequence | Å² | RMSD | pLDDT | Gated | Rg | Charge |
|---|---|---|---|---|---|---|---|
| 1 | design_5_s2 | 469 | 0.48 | 85.5 | **1/8** | 1.29 | −2 |
| 2 | design_18_s4 | 448 | 0.45 | 91.6 | 4/8 | 1.28 | −2 |
| 3 | design_12_s4 | 402 | 0.40 | 90.2 | 7/8 | 1.29 | +3 |
| 4 | design_11_s7 | 402 | 0.42 | 89.1 | 6/8 | 1.30 | +2 |
| 5 | design_14_s7 | 404 | 0.43 | **93.1** | 5/8 | **1.06** | **0** |

**If only one is made, make `design_14_s7`** — not the rank-1 design. Its
interface is statistically indistinguishable from the middle of the panel, and it
wins on every secondary axis: most compact backbone of the twenty (Rg ratio 1.06),
highest pLDDT of any representative, and **net charge 0**, the one sequence that
largely escapes ProteinMPNN's over-charging bias. `design_5_s2` leads the ranking
but is the highest-variance pick in the set (1/8).

**Superseded:** the old Step 6 recipe in this file and in
`docs/methods/06-ranking.md` (filter `pTM > 0.7`, then rank by ProteinMPNN
log-likelihood) is **dead on both clauses** — the API returns no pTM, and Step 5
measured ρ = −0.06 between MPNN score and RMSD. Both documents now carry the real
method.

**Figure trap (new):** the first panel render coloured a binder `tv_orange`, the
same colour the epitope hotspots use, and zoomed on the target alone so the five
binders fell out of frame. Both fixed in `06c_render_top.py`; the shared view is
now fitted with all binders visible so panels are comparable at one scale.

**Honest limits, recorded in the deliverable README:** no binding has been
demonstrated; the interface numbers are lower bounds from RFdiffusion's own
docking, not an independent evaluation; ESMFold is a fallible judge with a known
bias toward isolated helices, so design_5's 1/8 may be the judge, not the design.
**The obvious next computational step is the orthogonal one this pipeline never
ran: AlphaFold-Multimer or Boltz on binder + target, which tests the interface
rather than the monomer fold.**

---

## Session Log — 2026-08-12 (Step 5 EXECUTED — 64 sequences refolded, 58 self-consistent)

**Done:** all 64 sequences folded with ESMFold via the ESM Atlas REST API,
compared against their parent backbones → `esm_validation/scores.tsv` and 64 PDBs
in `esm_validation/predicted_structures/`. Script: `scripts/05_esmfold.py`
(predictions cached on disk; reruns only fetch what is missing).

**Result: 58/64 (91 %) self-consistent** at RMSD < 2 Å, mean pLDDT ≥ 70,
TM ≥ 0.5, coverage ≥ 90 %.

| Backbone | Self-consistent |
|---|---|
| design_4, 9, 12, 14, 15, 18 | **8/8** each |
| design_11 | 7/8 |
| **design_5** | **3/8** |

Best: `design_12_s4` — RMSD **0.40 Å**, pLDDT 90.2, TM 0.976. Ten sequences
came in under 0.50 Å.

**Three API realities the old method notes got wrong:**

1. **No pTM.** `/foldSequence/v1/pdb/` returns a bare PDB — no confidence JSON,
   no pTM anywhere. The documented `pTM > 0.7` filter **cannot be evaluated from
   this endpoint**. Substituted and stated, not silently dropped: **mean pLDDT ≥ 70**
   for confidence, **TM-score ≥ 0.5** for "same fold". Real pTM needs ESMFold
   running locally with weights + GPU.
2. **pLDDT is on a 0–1 scale**, not 0–100 (B-factors 0.5–0.9). Applying the
   conventional `>70` cut to raw values fails *every* design. The script detects
   the scale rather than assuming, since local ESMFold emits 0–100.
3. **~1 call in 3 returns `HTTP 504`.** Retries with exponential backoff are
   mandatory; one sequence (`design_14_s3`) needed a second pass and then folded
   fine (RMSD 1.01 Å).

**Coverage filter added — it caught four false passes.** TMalign reports RMSD over
the residues it *managed to align*. Three `design_5` sequences aligned only **30 of
52 residues** and returned **0.55 Å**, which reads as an excellent fit and is
actually a 58 %-complete one. TM-score already penalised them (~0.55, barely over
the "same fold" line) but that was too close to the threshold to rely on. Now
requiring `aligned_length / design_length ≥ 0.90`, which drops `design_5` from 7/8
to 3/8. **RMSD without coverage is not a self-consistency metric.**

**`design_5`'s failure mode is worth remembering.** It was the **top-ranked
backbone in Step 3** (469 Å² buried, 12 contacts, most of any design) and is the
**worst for designability**. Rendering the overlay
(`analysis/step5/partial_design_5_s5.png`) shows why: the design is a helical
hairpin, and ESMFold predicts **one long straight helix** — it matched one arm and
ran straight on instead of forming the turn. Critically, it is **confident about
the wrong answer**: pLDDT 90.0. Isolated helices are easy to predict, so high
pLDDT does not mean the design is right. Interface quality and designability are
**different axes**, and Step 3 cannot see the second one.

**The finding that justifies this whole step:** the ProteinMPNN score does **not**
predict refold accuracy.

| Correlation (Spearman, n=64) | |
|---|---|
| MPNN score vs RMSD | **−0.055** |
| MPNN score vs TM-score | **+0.008** |
| mean pLDDT vs RMSD | −0.304 |
| mean pLDDT vs TM-score | +0.358 |

The best refold (`design_12_s4`, RMSD 0.40 Å) ranks only **41st of 64** by MPNN
score, and the second-best (`design_11_s7`, 0.42 Å) ranks **63rd of 64**; the best
MPNN score (`design_15_s4`, 0.957) refolds at only 1.65 Å.
**You cannot rank candidates on ProteinMPNN score — you have to refold them.**
That is the defence for why Step 5 is not optional.

**Also produced:** `analysis/step5/best_design_12_s4.png` (prediction coloured by
pLDDT over the grey design backbone, 0.40 Å) and
`analysis/step5/partial_design_5_s5.png` (the partial-alignment failure).

**Figure gotcha:** `cmd.align` is useless for overlaying a prediction on an
RFdiffusion backbone — it does a sequence alignment first, and the backbone is
poly-glycine, so it matched **4 atoms**. Use `cealign` (or TMalign), which are
purely structural. The scores in `scores.tsv` were always TMalign and were never
affected.

**Carry-in for Step 6:** rank the 58 survivors. `esm_validation/scores.tsv` already
carries pLDDT, RMSD, TM, coverage, MPNN score, interface hydrophobicity and net
charge per sequence; `rfdiffusion/outputs/triage.tsv` carries the backbone-level
buried area and hotspot count. Note that the two do **not** agree on which
backbone is best (design_5 vs design_12), so the ranking has to state which axis
it weights and why.

---

## Session Log — 2026-08-12 (Step 4 EXECUTED — 64 sequences designed)

**Done:** ProteinMPNN cloned, 8 sequences designed for each of the 8 shortlisted
backbones → 64 sequences in `proteinmpnn/outputs/seqs/`, analysed into
`proteinmpnn/outputs/sequences.tsv`. Scripts: `scripts/04_proteinmpnn.sh`,
`scripts/04b_analyze_sequences.py`. **~40 s total on CPU.**

**Run parameters:** `--pdb_path_chains B` (design binder, fix target by omission),
`--num_seq_per_target 8`, `--sampling_temp 0.1`, `--model_name v_48_020`,
`--omit_AAs CX`, `--seed 42`.

**Flag-name bug in the old docs:** both `CONTEXT.md` and
`docs/methods/04-proteinmpnn.md` said `--pdb_path_chains_to_design`. **That
argument does not exist** — argparse rejects it. The real flag is
**`--pdb_path_chains`**; everything not listed is fixed automatically. Corrected
in the docs.

**Verified before running:**
- The RFdiffusion output's chain A **keeps the real myostatin sequence** (only the
  binder is poly-glycine) — confirmed identical to `myostatin_target.pdb`. So
  fixing chain A genuinely conditions the design on myostatin's own sidechains,
  which is the entire reason this step runs on the complex rather than the
  isolated binder.
- **The 51–64 gap is handled correctly.** ProteinMPNN reports `length 169`
  (= 109 + 60), because its parser expands chain A over its full numbering range
  and inserts the 14 unresolved residues as `-` with NaN coordinates. Checked
  `tied_featurize` directly: those positions get **`mask = 0`**, NaNs are zeroed
  only *after* masking, and they still occupy their index slots, so the positional
  encoding across the gap stays truthful. Nothing to fix.
- Cysteine omitted at design time: free Cys risks disulfide scrambling against
  myostatin's nine cysteines.

**Repeated the Step 3 mistake, then fixed it structurally.** The first version of
`04b` measured which binder positions touch the epitope by querying the raw
`design_N.pdb` — backbone-only on *both* chains — and found only **1–5** contact
positions with meaningless residue identities (hotspot hydrophobicity 0.31, *below*
the whole-binder mean). Same trap as Step 3. Rather than patch it again, the
corrected representation was factored into **`scripts/_structure_utils.py`**
(`add_virtual_cb`, `load_design`, `contacting_binder_positions`); `03b` and `04b`
both import it now, and `03b`'s numbers are unchanged after the refactor. **Any
future script that asks "what does the binder touch?" must go through that
module.**

**Results — the sequences match the structural intent.**

| Check | Result |
|---|---|
| Hotspot-contacting binder positions | **7–13** per design (was 1–5 under the broken measurement) |
| ProteinMPNN score (neg. log-likelihood, lower better) | 0.957–1.225 |
| Mean pairwise identity | **66 %** — healthy, no collapse at T=0.1 |
| Cysteines | none |
| Net charge | −7 to +4 (mean −1.3) |

**The hydrophobic gradient is the headline result:** whole binder **0.33** →
epitope-contacting face **0.46** → hotspot-contacting ring **0.57**. Apolar
residues placed exactly where the design buries surface, polar left on the solvent
face. That ordering — not the raw score — is the evidence that ProteinMPNN
"understood" the interface.

**Best by score:** `design_15` sample 4 (0.957), `design_15` sample 5 (0.961),
`design_15` sample 3 (0.963), `design_4` sample 2 (0.978), `design_14` sample 4
(0.986). Note `design_14`'s sequences carry the *highest* interface hydrophobicity
(0.67–0.75) while scoring mid-pack — score and interface quality are not the same
axis, and Step 5 arbitrates.

**Known bias, stated rather than hidden:** the sequences are heavily E/K/A-rich —
ProteinMPNN's well-documented tendency to over-charge solvent-exposed faces. Good
for its likelihood, a real liability for expression and non-specific binding.
`--use_soluble_model` is the lever if it matters later.

**Also fixed:** `03b` wrote `triage.tsv` with `\r\n` (Python `csv` default), which
put a trailing CR inside the last field's value and made the awk shortlist parse in
`04_proteinmpnn.sh` silently return zero designs. Writer now pins
`lineterminator="\n"`, and the awk strips CR defensively.

**Carry-in for Step 5:** 64 sequences, 52–60 aa — all well inside the ESMFold API
limit. Fold each, superpose onto its parent RFdiffusion backbone (chain B of the
corresponding `design_N.pdb`), and record pTM / mean pLDDT / Cα-RMSD. The parent
backbone for each sequence is the `backbone` column of `sequences.tsv`.

---

## Session Log — 2026-08-12 (Step 3 EXECUTED — 20 backbones generated and triaged)

**Done:** 20 binder backbones in `rfdiffusion/outputs/`, scored into
`rfdiffusion/outputs/triage.tsv`, shortlist of 8 selected for ProteinMPNN.
Scripts: `scripts/03_rfdiffusion.sh`, `scripts/03b_triage_backbones.py`,
`scripts/03c_render_designs.py`.

**Run parameters** (all encoded in `scripts/03_rfdiffusion.sh`):

```
contigmap.contigs=[A1-50/A65-109/0 45-60]
ppi.hotspot_res=[A33,A34,A85,A87,A93,A95]
inference.num_designs=20  diffuser.T=50
denoiser.noise_scale_ca=0  denoiser.noise_scale_frame=0
inference.empty_cache_per_design=True
```

Checkpoint auto-selected as `Complex_base_ckpt.pt` (triggered by `ppi.hotspot_res`
being set); `d_t1d=24`, so the hotspot feature is genuinely active. **0.76
min/design**, ~16 min for 20, no OOM on the 6 GB card at 140–155 total residues.
Motif RMSD 0.13 Å every step — the target stays rigid, as intended.

**Three traps hit and resolved — all worth remembering:**

1. **`denoising_steps` is not a parameter.** The old `docs/methods/03-rfdiffusion.md`
   recipe used it; Hydra rejects it. The key is **`diffuser.T`**.
2. **The "changing diffuser.T" warning is benign here.** RFdiffusion warns on
   *any* explicit CLI override of a trained parameter — including when the value
   is identical. `Complex_base_ckpt.pt` was trained at **T=50**, exactly what we
   passed (checked via `ckpt['config_dict']['diffuser']['T']`). Do **not** "raise
   T to 200 for final runs" as the old docs suggested.
3. **Output is BACKBONE-ONLY (N, CA, C, O — no CB), on both chains.** This
   produced a completely false first triage: every design looked like a floater
   (~100 Å² buried, 1/6 hotspots, 2–3 contacts). A properly packed interface
   *shows* a 4–8 Å backbone gap, because that is the sidechain layer. Fixes:
   restore the target's real sidechains by superposing `myostatin_target.pdb`
   onto output chain A (valid because the target is rigid), and build **virtual
   CB** on the binder from N/CA/C — validated against real CB atoms at **0.040 Å
   mean deviation**. Then **`cmd.alter(..., 'vdw=1.7')`**: PyMOL creates
   pseudoatoms with `vdw=1.0` regardless of `elem`, which was silently shrinking
   every buried-area number by ~35 %.

**Output convention (verified against the .trb):** chain A = target, 5JI1 mature
numbering, 51–64 gap preserved; chain B = binder, numbered from 1. Step 2
hotspots therefore apply to the outputs unchanged.

**Calibration instead of invented thresholds.** The real ActRIIB:GDF11 interface
(6MAC) scored in both representations: **697 Å² full-atom vs 293 Å² backbone+CB**
over 22 vs 9 ligand residues. Sidechains carry **58 %** of a real interface, so
all design dSASA figures are lower bounds and ProteinMPNN supplies the remaining
~2.4×. Treated as a floor for "is it docked", not a quality bar — ActRIIB binds
via sidechain knobs off a β-sheet while these designs pack helices flat, so
backbone burial is not strictly comparable across binding modes.

**Results — 17/20 PASS, all 20 docked on the right epitope.**

| Metric | Range across 20 |
|---|---|
| Hotspots engaged | **5–6 of 6** (10 designs hit all six) |
| Buried area (backbone+CB) | 205–472 Å² (real receptor: 293 Å² in the same units) |
| Helix fraction | 0.73–0.97 |
| Binder length | 51–60 |

Per-hotspot engagement: A33 20/20, A85 20/20, A93 20/20, A87 18/20, A95 17/20,
A34 15/20. Every hotspot is reachable — the Step 2 set was not over-constrained.

**Compactness filter added after inspecting the results.** Three designs (10, 17,
19) had **Rg 21–24 Å against ~12–14 Å** for the rest. A folded globular protein
obeys Rg ≈ 2.2·N^0.38 (≈10 Å at N=55), so these are ~2.3× the folded expectation.
Rendering `design_10` confirmed it: a **single continuous 56-residue helix** lying
across the epitope with most of its length in solvent. It engaged 5 hotspots and
buried 205 Å², so every contact-based filter would have passed it. Rejected on
`Rg/expected > 1.5`; the separation is cleanly bimodal (passes 1.06–1.34,
rejects 2.05–2.35). **Contact metrics alone cannot tell a binder from a stick.**

**Shortlist for Step 4** (top 8, all 6/6 hotspots, ranked by buried area):
`design_5` (469 Å²), `design_18` (448), `design_15` (406), `design_14` (404),
`design_12` (402), `design_11` (402), `design_4` (385), `design_9` (370).
Visually these are 3–4 helix bundles packed onto the knuckle; `design_14` is the
most compact (Rg 10.8, ratio 1.06).

**Also produced:** `analysis/step3_designs/*.png` (one panel per shortlisted
design, plus `REJECTED_design_10.png` as the counter-example) and
`analysis/pymol_sessions/step3_shortlist.pse` (all 8 on one target — toggle in
the object panel).

**Carry-in for Step 4:** ProteinMPNN must **fix chain A and design chain B** —
note this is the opposite assignment from the input file, where the target was
chain A alone. Clone `github.com/dauparas/ProteinMPNN` first (not yet present).

---

## Session Log — 2026-08-12 (Step 2 EXECUTED — hotspots finalized)

**Done:** the ActRIIB footprint was transferred onto apo GDF8 and committed to
`hotspots/hotspot_residues.txt`. Reproducible via `scripts/02_hotspots.py`
(`conda activate esm && python scripts/02_hotspots.py`).

**Method.** Superposed the prepared target onto the GDF11 chain of **two**
independent complexes and read the GDF8 residues within 4.5 Å of ActRIIB:

| Complex | Res. | Chains used | Superposition (`super`) | Footprint |
|---|---|---|---|---|
| **6MAC** GDF11:ActRIIB:ALK5 | 2.34 Å | ligand A, ActRIIB C | 0.70 Å / 81 res | 21 residues |
| **7MRZ** GDF11:ActRIIB-ALK4:Fab | 3.00 Å | ligand A, ActRIIB = **C resi 19-120** | 0.99 Å / 81 res | 23 residues |

Used `super` (structure-based, outlier-rejecting), not `align` — correct choice
for homologs, where sequence-anchored alignment gets dragged by the loops.

**Result — the transfer is verified, not assumed.** Three independent checks:

1. **Reproducibility across crystal forms.** All 21 6MAC residues reappear in
   7MRZ (different crystal form, ALK4 not ALK5, Fab bound). 7MRZ adds only two
   peripheral residues (78, 105) — treated as crystal-form noise and dropped.
   **Consensus footprint (21):** E25, I33, A34, P35, K36, R37, Y38, K39, S80,
   P81, I82, N83, M84, L85, F87, E91, I93, Y95, K97, V102, D104.
2. **Conservation.** GDF11↔GDF8 is 91 % identical over the aligned mature domain
   (86/94) — and **20 of 21 footprint residues are the identical amino acid**.
   The sole exception is **Q91→E**, conservative (BLOSUM62 +2) and burying only
   35 Å² (23 %). This is the sentence that makes the homology transfer defensible.
3. **Dimer occlusion — none.** Recomputed SASA of every footprint residue in
   `myostatin_target.pdb` (monomer) vs `myostatin_dimer.pdb`. Max occlusion 5 %
   (Y38); everything else 0 %. **Quantitatively confirms the Step 1 monomer
   decision** — the partner monomer covers no part of the type II epitope.

**Hotspot selection.** Ranked by buried surface area (ΔSASA against ActRIIB),
not by distance — a 4.5 Å cutoff scores a glancing backbone contact the same as
an engulfed sidechain. Final set spans **both lobes** of the epitope (finger 1–2
loop + finger 3 convex face) so a binder cannot satisfy it with half the surface:

```
ppi.hotspot_res=[A33,A34,A85,A87,A93,A95]
```
I33 (46 Å²/81 %), A34 (40/99), L85 (57/100), F87 (47/59), I93 (53/62), Y95 (78/50).
Widest Cβ–Cβ separation 11.4 Å — comfortably spanned by a 45–60 residue binder.
Conservative fallback if RFdiffusion struggles: `[A33,A34,A85,A87]`.

**Correction to the provisional list.** The old provisional set was
I33/A34/P35/M84/L85/Y86/F87. Three changes, all evidence-driven:
- **M84 dropped** — buries **0.2 Å² (1 %)**. The 2026-08-10 carry-in note guessed
  "7 % exposed, expect to drop it"; the SASA calculation confirms it outright.
  It points into GDF8's own hydrophobic core and is unreachable.
- **Y86 dropped** — it is **not** in the ActRIIB footprint at all. In 6MAC, Y86
  faces the **type I (ALK5)** site, not type II. The provisional list had it on
  the wrong receptor interface.
- **I93, Y95 added** — both heavily buried against ActRIIB (53 and 78 Å²) and
  absent from the provisional list; Y95 buries the most area of any residue in
  the whole footprint.
- **P35 demoted** to tier 2 (85 % buried but only 26 Å²).

**Also produced:** `analysis/step2_knuckle_epitope.png` (ActRIIB cartoon over the
epitope surface — hotspots orange, full footprint cyan),
`analysis/step2_hotspots_surface.png` (receptor hidden), and the PyMOL session
`analysis/pymol_sessions/step2_hotspots.pse`. New raw inputs:
`data/raw/6MAC.cif`, `data/raw/7MRZ.cif`.

**Carry-in for Step 3:** contig must express **both resolved segments** —
`A1-50/A65-109`, never `A1-109` (14-residue disordered gap at 51–64). Hotspots
are in mature numbering, chain A, matching `myostatin_target.pdb` exactly — no
renumbering needed. Watch the 6 GB VRAM ceiling: 95 target residues + 45–60 binder.

---

## Decision Update — 2026-08-12 (docs consolidation: `wiki/` merged into `docs/`)

> ⚠️ **Supersedes every `wiki/…` path in the entries below.** The `wiki/` tree no
> longer exists. Historical narrative referring to "importing the theory wiki" is
> left intact as history; the path pointers have been updated in place.

**Problem.** The repo carried two parallel documentation trees. `mkdocs.yml` sets
`docs_dir: docs`, so everything under `wiki/` was **excluded from the built
site** — roughly 1,100 lines of theory that was unsearchable and invisible to
anyone reading the rendered docs. The split also had no stable meaning:
`docs/background/` and `wiki/concepts/` were the same kind of content.

**Change.** Merged `wiki/` into `docs/` and deleted it.

| Old | New | Note |
|---|---|---|
| `wiki/concepts/` | `docs/concepts/` | joined by the two ex-`background/` theory pages |
| `docs/molecules/` | `docs/molecules/` | unchanged |
| `wiki/methods/` | **`docs/tools/`** | renamed — collided with `docs/methods/`, which is the *runnable steps*, not tool theory |
| `docs/background/tgf-beta-receptors.md` | `docs/concepts/tgf-beta-receptors.md` | |
| `docs/background/epitope.md` | `docs/concepts/epitope.md` | |
| `docs/background/myostatin.md` | **merged into** `docs/molecules/GDF8.md` | ~70 % duplicate; GDF8 page was the fuller one |
| `wiki/index.md` | **merged into** `docs/index.md` | page-network diagram and page tables preserved |

`docs/background/` is gone. All moves used `git mv`, so file history is intact.

**Content reconciliation.** Two pages contradicted each other on mechanism:
`docs/background/tgf-beta-receptors.md` and `docs/reference/glossary.md` both
described the binder as an **ActRIIB "mimic"**, while `docs/molecules/ActRIIB.md`
correctly states it occupies ActRIIB's *footprint on the ligand* without
reproducing the receptor surface. Corrected to the latter in both places — this
is a real mechanistic distinction, not wording.

`concepts/PPI-hotspots.md` (general ΔΔG/alanine-scanning theory) and
`concepts/epitope.md` (the myostatin knuckle at residue resolution) were kept as
separate pages — different altitude, not duplicates — and cross-linked.

**Residual overlap, accepted:** `concepts/TGF-beta-superfamily.md` and
`concepts/tgf-beta-receptors.md` each carry a wrist-vs-knuckle table. They are
consistent and framed differently (epitopes-as-ligand-surfaces vs
receptors-and-cascade), so both were kept with cross-links rather than merged.
Revisit if they drift.

**Also updated:** `mkdocs.yml` nav (Concepts / Molecules / Tools / Methods /
Reference), `README.md`, `SYLLABUS.md` (~20 links), and the pointers in this file.

---

## Session Log — 2026-08-10 (Step 1 EXECUTED — target prepared)

**Step 1 is done.** `scripts/01_prepare_target.py` (Biopython, `esm` env) is the
reproducible recipe; PyMOL (`pymol-open-source`) was added to the `esm` env for
the figures and for Step 2's superposition.

**Artifacts produced:**

| File | Contents |
|---|---|
| `data/raw/5JI1.pdb`, `.cif` | Raw RCSB deposition |
| `data/prepared/myostatin_target.pdb` | **The RFdiffusion target** — chain A only, 729 ATOM records, 0 HETATM, no altlocs |
| `data/prepared/myostatin_dimer.pdb` | Chains A+B, the physiological ligand (kept for reference/comparison) |
| `analysis/step1_knuckle_face.png`, `step1_opposite_face.png` | Surface renders, hotspot patch in red, gap edges in blue |

**Findings that change how later steps must be run:**

1. **Numbering scheme resolved — and it needs no conversion.** `DBREF` says PDB
   residues **1–109** map to UniProt **O08689 268–376**. So 5JI1 is numbered in
   **mature-domain numbering with Asp1 = residue 1**, which is the same scheme
   the provisional hotspot list already uses. Confirmed by sequence: positions
   33/34/35 really are Ile/Ala/Pro and 84/85/86/87 really are Met/Leu/Tyr/Phe.
   *Nothing needs renumbering before RFdiffusion.*
2. **This is MOUSE GDF8 (O08689), not human.** Not a problem, and worth stating
   proactively: mouse mature 268–376 is a **100 % exact match** to human
   (O14793) 267–375 — verified by alignment, not assumed. Mature myostatin is
   sequence-identical across mammals, so the mouse crystal is a valid stand-in.
3. **There is a 14-residue disordered gap (51–64) in chain A** (chain B is worse:
   49–65). It is **not** near the epitope: 33–46 Å from the hotspot centroid, at
   the opposite end of the molecule (this is the α-helix / "heel" region, i.e.
   the type I / wrist site — not our target). Left unmodelled deliberately: a
   14-residue de novo loop would be invented geometry, and it is irrelevant here.
   ⚠️ **Consequence for Step 3:** chain A is **two segments, 1–50 and 65–109**.
   The RFdiffusion contig must express both, e.g. `A1-50/A65-109`, not `A1-109`.
4. **Monomer chosen over dimer — and the choice is now evidence-based.** Per-residue
   SASA was computed for the hotspots in the monomer and in the dimer: the values
   are **identical**. Chain B buries ~603 Å² of chain A, none of it at the knuckle.
   So the dimer costs +109 residues of VRAM (a real concern at 6 GB) and buys
   nothing at the epitope. Chain A was picked over B because it has fewer
   unresolved residues (14 vs 17).
5. **The provisional hotspots hold up geometrically.** All 7 are resolved; the
   patch spans only 12.6 Å (Cα–Cα max), and Ala34 and Leu85 — 51 residues apart in
   sequence — are 5.0 Å apart in space. Two finger loops converging into one
   compact convex surface is exactly the expected knuckle.
   ⚠️ **Carry into Step 2:** **Met84 is only 7 % solvent-exposed** — too buried for
   a binder to contact meaningfully. It is a likely drop from the final
   `ppi.hotspot_res` list. The other six are 19–33 % exposed.

**Still unverified:** the hotspot list is still *homology-provisional*. Step 2 must
derive it from the actual 6MAC superposition rather than confirm it by eye — the
consistency found above is encouraging, not proof.

---

## Decision Update — 2026-07-07 (target & hotspot-source change)

> ⚠️ **Supersedes the original Step 1/Step 2 structure choices below.** After
> importing the theory wiki (`wiki/`), the target and hotspot-source structures
> were reconsidered and changed. The detailed 3HH2/1NYS prose later in this log is
> kept for history but is **no longer the plan**.

| Decision | Old choice | **New choice (2026-07-07)** | Why changed |
|---|---|---|---|
| RFdiffusion target | 3HH2 (myostatin:follistatin) | **5JI1 (apo GDF8)** | Apo → epitope exposed in its unbound conformation; 2017/2.25 Å with modern OneDep validation, vs 3HH2's occluded epitope and poor 2009-era geometry (clashscore ~44, ~14 % sidechain outliers). |
| Hotspot source | 1NYS (activin A:ActRIIB) | **6MAC (GDF11:ActRIIB:ALK5)** | GDF11 is ~90 % identical to GDF8 in the mature domain and uses the same type II receptor — a far closer homology transfer than activin. Corroborate with 7MRZ. |

**Cost of the change:** none sunk — Steps 1 and 2 had not been executed (no target
PDB extracted, no hotspot list committed). This is a plan change, not a rework.
Full rationale and per-structure detail: `docs/molecules/5JI1.md`,
`docs/molecules/6MAC.md`, `docs/molecules/3HH2.md`. Runnable recipes updated in
`docs/methods/01-target-prep.md` and `docs/methods/02-hotspots.md`.

**Carry-over caveat:** confirm the numbering scheme 5JI1 uses before writing
hotspots (the deposited mature-domain fragment does not necessarily start at 1),
and check the knuckle finger loops are resolved in the apo structure.

---

## Session Log — 2026-06-28 (infrastructure build)

**What we accomplished this session (all infrastructure, no science steps run yet):**

- Confirmed hardware/software: RTX 4050 (6 GB, Ada/sm_89), no prior conda, system Python 3.14 (unusable for the tools).
- Installed **Miniforge** (conda 26.3.2 / mamba 2.5.0).
- Restructured the project into a **reproducible scientific repo** (README, LICENSE, CITATION.cff, Makefile, mkdocs.yml, .gitignore, `envs/`, `scripts/`, `docs/` wiki).
- Built and **GPU-verified all three conda environments** (`rfdiffusion`, `proteinmpnn`, `esm`) — including resolving a multi-layer RFdiffusion CUDA dependency hell (see traps below).
- Wrote the full **MkDocs "wiki"** (background biology, runnable methods 1–6, reference/glossary).
- Initialized **git** and made the first commit (`4315015`, 32 files).
- Private step-by-step retrace lives in `SESSION_WALKTHROUGH.md` (git-ignored).

**Decisions locked in (rationale in full below / in `docs/`):**

| Decision | Choice | Why |
|---|---|---|
| Env manager | **conda/mamba**, not venv | only conda handles py3.9 + CUDA torch + dgl/SE3 binaries |
| Docker | **deferred**, repo kept Docker-ready | valuable here, but would compete with the RFdiffusion learning goal |
| Docs | **in-repo `docs/` (MkDocs Material)** | versioned with the code, reproducible |
| License | **MIT** | permissive, standard |
| RFdiffusion GPU stack | **one coherent conda-forge solve** + RFdiffusion via `pip --no-deps` | the fix that ended the dependency hell |

> ✅ **Session committed.** `make` installed; the Makefile was hardened to source conda inside each recipe (recipes run in a bare non-interactive shell with no `~/.bashrc`). Two commits exist: `4315015` (initial scaffold) and a second "tooling + session docs" commit (this session log, all-conda recipe corrections, expanded Makefile, walkthrough ignore rule).

## TODO — Next Session

1. ~~**Structure tooling check**~~ — **DONE 2026-08-10.** `pymol-open-source` installed into the `esm` env; Biopython used for the prep script itself.
2. ~~**Step 1 — Target prep**~~ — **DONE 2026-08-10.** See the 2026-08-10 session log above for the numbering scheme, the 51–64 gap, and the monomer decision.
3. ~~**Step 2 — Hotspots**~~ — **DONE 2026-08-12.** See the 2026-08-12 session log above. Final set `[A33,A34,A85,A87,A93,A95]`; Met84 dropped as predicted, and Tyr86 dropped too (it sits on the type I interface).
4. ~~**Step 3 — First RFdiffusion run**~~ — **DONE 2026-08-12.** 20 designs, 17 pass triage, 8 shortlisted. See the Step 3 session log above.
5. ~~**Step 4 — ProteinMPNN**~~ — **DONE 2026-08-12.** 64 sequences. See the Step 4 session log above.
6. ~~**Step 5 — ESMFold validation**~~ — **DONE 2026-08-12.** 58/64 self-consistent. See the Step 5 session log above.
7. ~~**Step 6 — Ranking and write-up**~~ — **DONE 2026-09-26.** Panel of 5 in `results/top_designs/`. Axis: designability as a gate (41/58 clear it), interface area as the objective, one representative per backbone. See the 2026-09-26 session log. **Pipeline steps 1–6 are complete.**

**Quick start command next session:** `cd` into the project and run `make verify` to confirm all three envs are still healthy before doing anything.

---

## Scientific Rationale

Myostatin (GDF-8) is a TGF-β superfamily member that negatively regulates muscle mass. It signals through the type II receptor ActRIIB. Inhibiting this interaction is a validated therapeutic strategy for muscle-wasting conditions and metabolic disease.

The structural basis of the interaction is well-understood:
- ActRIIB is a **type II** receptor. In the TGF-β family, type II receptors bind the **knuckle epitope** — the *convex* outer surface of the β-strand "fingers" of a **single** ligand monomer. (Type I receptors, e.g. Alk4/Alk5, bind the *concave* **wrist** epitope at the dimer interface — that is a different site and NOT our target.)
- The knuckle interface is dominated by **hydrophobic contacts**: on the receptor side, an aromatic triad (ActRIIB Tyr60/Trp78/Phe101) grips hydrophobic residues on the ligand's convex finger surface, plus a few peripheral H-bonds/salt bridges.
- This epitope is a legitimate, well-characterized design target for de novo binders. A successful binder is essentially a **synthetic ActRIIB mimic** that occupies the knuckle.

> ⚠️ **Correction (verified 2026-06-25, see Step 1/2):** an earlier draft of this document said ActRIIB binds the "concave wrist epitope." That is wrong — that is the type I site. ActRIIB binds the **convex knuckle**. All downstream steps target the knuckle.

This is not a random tutorial problem. This connects directly to the scientific area (myostatin inhibition, next-gen therapeutics, peptide/protein design) the user wants to work in professionally.

---

## Tool Chain Overview

The pipeline has four steps. Each tool is independent and has a defined input/output contract. Do not conflate them.

```
[1] TARGET PREP         Get and clean the myostatin PDB structure
                        ↓
[2] RFDiffusion         Diffuse new protein backbones conditioned on the target
                        Input:  target PDB + hotspot residues
                        Output: designed backbone PDBs (no sequence yet)
                        ↓
[3] ProteinMPNN         Design amino acid sequences for each backbone
                        Input:  backbone PDB
                        Output: FASTA sequences (multiple per backbone)
                        ↓
[4] ESMFold (API)       Fold the designed sequences in silico to validate
                        Input:  FASTA sequence
                        Output: predicted structure PDB + pTM + pLDDT scores
```

Validation is not optional. You are not "done" after ProteinMPNN. The ESMFold step is what distinguishes a real design exercise from just pressing buttons.

---

## Compute Reality on Windows 11

RFDiffusion requires a GPU for any practical throughput. ProteinMPNN can run on CPU but is slow. ESMFold is accessed via REST API.

### Step 0 — Assess your compute before anything else

Open PowerShell and run:
```powershell
nvidia-smi
```

**Interpret the output:**
- If you see a GPU (RTX series, GTX 1080+, anything with ≥8GB VRAM): you can run RFDiffusion locally via WSL2 with CUDA support.
- If you see nothing or an error: you have no local GPU. Use Google Colab for RFDiffusion only. Everything else runs locally.
- If you see a GPU with <6GB VRAM: usable but limiting. Stick to small binder sizes (40–60 residues).

Also check WSL2 status:
```powershell
wsl --status
wsl --list --verbose
```

You want WSL2, not WSL1. If WSL is not installed:
```powershell
wsl --install
```
Then restart. Claude Code will guide GPU passthrough to WSL2 separately if needed.

### Step 0 — FINDINGS (assessed 2026-06-25, Windows host)

**GPU: present, VRAM-limited.**
- NVIDIA GeForce RTX 4050 Laptop, driver 596.21, CUDA 13.2 capable.
- **6 GB VRAM (6141 MiB)**, near-idle at assessment.
- Verdict: RFDiffusion runs **locally** — no Colab needed. But 6 GB is at the "usable but limiting" boundary. Constraints to carry forward:
  - Keep binder length small: **40–60 residues**.
  - Trim the target chain (don't feed a large multi-chain complex).
  - On CUDA OOM, reduce binder length / target size first before anything else.

**WSL2: NOT installed on this host.**
- `wsl --status` → "The Windows Subsystem for Linux is not installed."
- Action required on the Linux host/WSL setup: install WSL2 + Ubuntu (`wsl --install`, needs admin + reboot), OR continue on the native Ubuntu machine the project is being moved to. Driver 596.21 already supports CUDA-in-WSL passthrough natively (no extra driver needed).

**Decided workflow:** formulate the scientific design (Steps 1–2: target prep + hotspot identification — both GPU-free) as theory in this CONTEXT, then move the project to **Ubuntu** to execute the GPU steps (RFDiffusion, ProteinMPNN) and ESMFold validation. Compute envs are NOT being installed on the Windows host.

---

## Environment Setup Strategy

**Do not mix environments carelessly.** Each tool gets its **own** conda env — they have conflicting binary (CUDA/Python-version) dependency trees and must not be merged. We use `mamba` (Miniforge) for all of it.

All work happens on the **native Ubuntu** host (no longer WSL2).

### The reproducible "one-command" install (this is the dependency list)

The env specs live in `envs/*.yml`. One `mamba env create -f <file>` installs each block:

```bash
mamba env create -f envs/rfdiffusion.yml && mamba activate rfdiffusion && scripts/setup_rfdiffusion.sh
mamba env create -f envs/proteinmpnn.yml
mamba env create -f envs/esm.yml
```

| Env | Tool | Python | Notable, deliberate choices |
|---|---|---|---|
| `rfdiffusion` | RFDiffusion | 3.9 | **Whole GPU stack solved together from conda-forge on CUDA 11.8** (verified torch 2.3.1, dgl 2.3.0, e3nn 0.5.6, torchdata 0.7.1). `scripts/setup_rfdiffusion.sh` adds RFdiffusion itself (`pip --no-deps`) + weights. See traps below. |
| `proteinmpnn` | ProteinMPNN | 3.9 | **CPU-only** torch via pip wheel (~190 MB); sufficient at 45–60 aa, far smaller than CUDA build |
| `esm` | ESMFold validation | 3.11 | API client + analysis only: requests, biopython, pandas, **TMalign**. Folding is server-side (REST) — no local torch/GPU |

The ESMFold env intentionally does **not** install ESMFold locally — we use the REST API (faster, no GPU). Local fair-esm/openfold is optional and heavy; skip unless batching offline.

### ⚠️ Install traps we hit (and how the final files prevent recurrence)

The RFDiffusion env took several iterations; each fix exposed the next problem. Recorded so nobody repeats them:

1. **Ada GPU needs CUDA ≥ 11.8.** Upstream `env/SE3nv.yml` pins `pytorch=1.9 + cudatoolkit=11.1`; those kernels stop at sm_86 and fail on the RTX 4050 (sm_89) with *"no kernel image is available"*. **Fix:** CUDA **11.8** (its sm_86 kernels are forward-compatible with Ada's sm_89).
2. **Unpinned `torch` gets silently upgraded.** `e3nn 0.6.0` requires `torch>=2.2`, so pip uninstalled our pinned torch and pulled the latest PyPI wheel (cu128) — which then broke dgl's ABI (`libcudart.so.11` / `undefined symbol`).
3. **pip + conda torch don't mix.** A pip torch alongside a leftover conda libtorch in `$CONDA_PREFIX/lib` collided (`undefined symbol`), and the pip dgl wheel couldn't find `libcusparse.so.11` on the loader path.
4. **dgl 2.3 ↔ torchdata.** dgl 2.3's `graphbolt` imports `torchdata.datapipes`, removed in `torchdata>=0.8` → pin **`torchdata<0.8`**.

**The fix that actually held:** stop hand-patching; solve the **entire** GPU stack in ONE conda-forge transaction (`cuda-version=11.8`, `pytorch=*=cuda*`, `dgl`, `e3nn`, `torchdata<0.8`) so the solver guarantees mutual compatibility and manages all CUDA `.so`s coherently — and install RFdiffusion itself with `pip --no-deps`. No pip/conda torch mixing, no library-path hacks.

### Installed & verified (2026-06-28)

- Miniforge: conda **26.3.2**, mamba **2.5.0** (`~/miniforge3`).
- `rfdiffusion`: torch **2.3.1** (CUDA build) → `cuda.is_available()` True, RTX 4050 detected; dgl **2.3.0**, e3nn **0.5.6**, torchdata **0.7.1**. Verified: GPU matmul + a **dgl graph on the GPU** + `se3_transformer.model.basis` import. RFdiffusion 1.1.0 installed `--no-deps`; weights (Base + Complex_base, ~923 MB) present. **GPU stack fully GREEN — ready for Step 3.**
- `proteinmpnn`: torch 2.8.0+cpu, numpy 1.26.4 (~1.1 GB).
- `esm`: requests / biopython 1.87 / pandas / numpy / TMalign CLI all present.

> **Disk note:** the root partition is only 74 GB and filled up twice during env builds; removing MATLAB (~28 GB in `/usr`, done 2026-06-28) restored headroom. The conda-forge GPU download is ~3 GB and timed out once on a slow connection — just re-run `mamba env create` (it resumes from cache).

## Repository structure & best practices

The project was restructured as a reproducible scientific GitHub repo:

```
myostatin_test/
├── README.md            # front door: summary, pipeline table, quickstart
├── LICENSE              # MIT
├── CITATION.cff         # "Cite this repository" metadata
├── CONTEXT.md           # THIS FILE — dated decision log
├── Makefile             # named targets: make envs / gpu-check / docs ...
├── mkdocs.yml           # builds docs/ into a searchable site
├── .gitignore           # excludes weights, raw PDBs, outputs, site/
├── envs/                # rfdiffusion.yml | proteinmpnn.yml | esm.yml
├── scripts/             # setup_rfdiffusion.sh (+ pipeline scripts to come)
├── docs/                # all docs: concepts/ molecules/ tools/ methods/ reference/
├── data/ hotspots/ rfdiffusion/ proteinmpnn/ esm_validation/ analysis/ results/
```

**Docs:** in-repo `docs/` rendered with **MkDocs Material** (`mkdocs serve`). Written for a bioinformatics/biology reader. `docs/concepts/` = theory, `docs/molecules/` = the ligands/receptors/PDB entries, `docs/tools/` = what each program does, `docs/methods/` = runnable steps 1–6, `docs/reference/` = glossary + hardware/Docker.

**Docker — deferred (decided 2026-06-28).** This stack is the poster child for "works on my machine", so Docker genuinely adds value — but learning `nvidia-container-toolkit` mid-project would compete with the core goal. The repo is built **Docker-ready** (pinned versions, clean env files, one setup script); adding a `Dockerfile` is a short later exercise. Plan sketch in `docs/reference/hardware-and-docker.md`.

---

## Project Directory Structure

Create this layout before running anything:

```
~/projects/myostatin_binder/
├── CONTEXT.md                  ← this file
├── data/
│   ├── raw/                    ← downloaded PDBs, unmodified
│   └── prepared/               ← cleaned, chain-extracted PDBs
├── hotspots/
│   └── hotspot_residues.txt    ← list of target residues on myostatin
├── rfdiffusion/
│   ├── configs/                ← YAML config files for each run
│   ├── outputs/                ← raw backbone PDBs from RFDiffusion
│   └── logs/
├── proteinmpnn/
│   ├── outputs/                ← FASTA files per backbone
│   └── logs/
├── esm_validation/
│   ├── predicted_structures/   ← PDBs from ESMFold
│   └── scores.tsv              ← pTM, pLDDT per design
├── analysis/
│   └── pymol_sessions/         ← PyMOL alignment sessions
└── results/
    └── top_designs/            ← filtered top candidates
```

---

## Step 1 — Target Preparation

> 🛑 **SUPERSEDED (2026-07-07).** The target is now **5JI1 (apo GDF8)** and the
> hotspot source is now **6MAC (GDF11:ActRIIB)** — see "Decision Update —
> 2026-07-07" near the top of this file and the recipes in `docs/methods/`. The
> 3HH2/1NYS analysis below is retained as history (the 3HH2 chain-assignment
> correction remains a useful record) but is **no longer the plan to execute**.

### Which structure to use — VERIFIED FACTS (checked against RCSB + primary literature, 2026-06-25)

**Primary target structure: PDB 3HH2.** This is the crystal structure of **myostatin (GDF-8) bound to follistatin-288** (Cash et al., *EMBO J* 2009; 2.15 Å). Important verified details:

| Entity | Chains | What it is |
|---|---|---|
| **Myostatin (GDF-8)** mature growth-factor dimer | **A, B** | *Mus musculus*, 109 aa modeled per chain. **This is our target.** |
| **Follistatin-288** | **C, D** | Human antagonist. **Not a receptor** — remove it. |

> ⚠️ **The earlier draft of this doc was wrong about 3HH2.** It claimed 3HH2 = "ActRIIB bound to GDF-11" with receptor on chains A/B and ligand on C/D. That is incorrect on every count: 3HH2 contains **no ActRIIB and no GDF-11**. The myostatin is on **chains A/B**, follistatin on **C/D**. Do NOT run the old "select contacts to receptor chain A/B" recipe — it would extract the myostatin:follistatin interface, not the receptor epitope.

**Why 3HH2 is still the right Step 1 target:** it is the *actual* myostatin growth factor (not a GDF-11 proxy), at good resolution, with the full TGF-β "hand" fold (four-stranded β-fingers, cystine-knot palm, wrist helix). The **knuckle epitope sits on the convex outer face of one monomer's fingers** — it is fully intact on a single extracted chain and does NOT touch the dimer interface. Follistatin's FSD1/FSD2 domains happen to bury the type II (knuckle) site, which is useful corroboration but is **not** how we'll define hotspots (see Step 2).

**Homology template for the receptor epitope (Step 2):** **PDB 1NYS** (and isoform **1NYU**) — ActRIIB ectodomain : activin A complex (Thompson et al., *EMBO J* 2003). This is where the actual ActRIIB footprint is defined; we transfer it onto myostatin by superposition.

**Fallback target:** AlphaFold model of human myostatin (UniProt **O14793**, mature domain res ~268–375). Use only if 3HH2 cleanup proves problematic. Note: mouse (3HH2) and human myostatin mature domains are essentially identical (myostatin is extraordinarily conserved), so 3HH2 is a valid stand-in for the human target — **verify the sequence match during prep**.

**Quality rule (unchanged):** don't design against a structure with Clashscore > 20 or Ramachandran outliers > 1.5% without repair. 3HH2 at 2.15 Å is fine; check its validation report on RCSB before committing.

### What to do (run on Ubuntu)

1. Fetch 3HH2 from https://www.rcsb.org → `data/raw/3hh2.pdb` (biological assembly).
2. Inspect chains in PyMOL:
   ```python
   fetch 3hh2, async=0
   show cartoon
   util.cbc          # color by chain
   # Confirm: chains A,B = myostatin (the cystine-knot growth factor); C,D = follistatin (larger, wraps around)
   ```
3. Extract a **single myostatin monomer** as the target — chain A. (One monomer is sufficient: the knuckle epitope is entirely within one chain, and a ~109-residue target keeps RFDiffusion within the 6 GB VRAM budget from Step 0.)
   ```python
   # PyMOL
   create target, (3hh2 and chain A and polymer.protein)
   remove solvent
   remove not polymer            # drop HETATM: waters, sulfate/heparin mimetics, etc.
   remove not alt ''+A           # keep only altloc A where present
   alter target, alt=''
   save data/prepared/myostatin_target.pdb, target
   ```
   Biopython equivalent (if no PyMOL): select `chain A`, keep only `ATOM` records, drop `HETATM`/waters, collapse altlocs to the highest-occupancy conformer.
4. **Verify after extraction:**
   - Only chain A, only protein ATOM records remain (no follistatin, no HETATM).
   - Note any **missing/disordered residues** (gaps in numbering) — especially near the fingers, since a gap inside the knuckle would compromise the epitope. Record the resolved residue range; you'll need it for the RFDiffusion `contigmap`.
   - Confirm the mature numbering starts at **D1** (Asp1) — Step 2 hotspot numbers assume this scheme.

**Pay attention to:** missing residues, HETATM records, alternate conformations. RFDiffusion expects a clean single-chain backbone. The resolved residue range of chain A (not a hard-coded "1–100") is what goes into the contig string.

---

## Step 2 — Hotspot Residue Identification

This is the most scientifically critical step. You are telling RFDiffusion *where* on the myostatin surface the binder should dock. Get it wrong and you generate binders against the wrong face.

**The central problem:** 3HH2 has **no receptor in it** (it's myostatin:follistatin). So you CANNOT read the ActRIIB epitope off 3HH2 directly. Instead we define the epitope by **homology transfer** from a structure that *does* contain the type II receptor (activin A : ActRIIB, PDB **1NYS**), then map it onto myostatin.

### What the knuckle (type II / ActRIIB) epitope is

- It is on the **convex outer surface of the β-fingers** of a **single** myostatin monomer (NOT the dimer-interface wrist).
- It is **hydrophobic-dominated**. On the receptor, an aromatic triad **ActRIIB Tyr60 / Trp78 / Phe101** forms the core, burying ~720 Å² per receptor (Thompson et al. 2003).
- On the **ligand** (activin A), the residues that pack against that triad sit on the finger loops: **Ile30, Ala31, Pro32** (finger 1–2 loop) and **Pro88, Leu92, Tyr94** (finger 3), plus **Ile100** (finger 4). Ala31/Pro32/Leu92 are the central contacts.
- General TGF-β rule: the type II epitope is hydrophobic and tolerant — BMP-2 mutagenesis showed only ~6 of 24 interface residues dominate binding, with a single absolutely-conserved Leu at the core.

### Method — homology transfer (do this on Ubuntu, in PyMOL)

This is the rigorous way to get exact myostatin residue numbers. Superpose myostatin onto activin A in the receptor complex, then read off which myostatin residues fall under the ActRIIB footprint.

```python
# PyMOL — both structures are receptor-free-of-our-concern except for the footprint
fetch 3hh2, async=0          # myostatin (A,B) + follistatin (C,D)
fetch 1nys, async=0          # activin A + ActRIIB ectodomain

# 1. Superpose one myostatin monomer onto one activin A monomer.
#    (Identify the activin chain vs the ActRIIB chain in 1NYS first: ActRIIB ectodomain
#     is the smaller ~100-aa three-finger-toxin fold; activin is the cystine-knot ligand.)
align (3hh2 and chain A), (1nys and chain <ACTIVIN_CHAIN>)

# 2. Select myostatin residues that now lie within the ActRIIB footprint.
select knuckle, byres (3hh2 and chain A) within 5 of (1nys and chain <ACTRIIB_CHAIN>)
iterate knuckle and name CA, print(f"{resi} {resn}")
show sticks, knuckle
```

The residues printed = your data-driven knuckle hotspot list. Cross-check them against the provisional list below; they should overlap heavily.

**Corroboration (optional, sanity check):** follistatin FSD1/FSD2 in 3HH2 bury the type II site. Selecting `byres (chain A) within 5 of (chain C+D)` and intersecting with the homology footprint shows which buried residues are specifically the *receptor* knuckle (vs the type I/wrist patch follistatin also covers).

### Provisional knuckle hotspot list (myostatin mature numbering, D1 = res 1)

Derived by aligning the myostatin sequence to activin A at the known contact regions (`IIAP-K-RYKANYC` ↔ activin `IIAP-S-GYHANYC`; finger-3 `PINMLYF` ↔ activin `PMSMLYY`). **Treat as a hypothesis to confirm with the superposition above — do not feed to RFDiffusion unverified.**

```
# hotspot_residues.txt  — myostatin (GDF-8) type II / knuckle epitope, chain A of 3HH2
# Mature numbering, Asp1 = residue 1. PROVISIONAL — confirm by 1NYS superposition.
#
# Finger 1-2 loop (core knuckle, ↔ activin Ile30/Ala31/Pro32):
A32  ILE
A33  ILE
A34  ALA
A35  PRO
A38  TYR
# Finger 3 convex face (↔ activin Pro88/Leu92/Tyr94):
A84  MET
A85  LEU
A86  TYR
A87  PHE
# (consider also the conserved finger-tip W29/W31 of the GWDW motif as anchor context)
```

Pick the **5–8 strongest hydrophobic/aromatic positions** after verification — RFDiffusion's `ppi.hotspot_res` wants the few residues the binder MUST contact, not the whole patch. Favor Ile33, Ala34, Pro35, Leu85, Tyr86, Phe87.

**Pay attention to:**
- **Numbering must match the extracted target PDB.** After you `save` chain A, re-open it and confirm the residue numbers still read 1…109 (PyMOL/Biopython can renumber on extraction). RFDiffusion reads these literal numbers from the input PDB.
- **Chain ID after extraction.** If you rename the extracted chain (e.g. to `A`), the hotspot prefix must match (`A32`, not `C32`).
- A hotspot inside a disordered/missing loop is useless — drop any provisional residue that isn't actually resolved in chain A.

---

## Step 3 — RFDiffusion Installation and Run

### Installation (WSL2, with GPU)

```bash
# Inside WSL2 Ubuntu
conda create -n rfdiffusion python=3.9 -y
conda activate rfdiffusion

# PyTorch with CUDA — match your CUDA version from nvidia-smi
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
# Adjust cu118 → cu121 based on your driver

# Clone RFDiffusion
git clone https://github.com/RosettaCommons/RFdiffusion.git
cd RFdiffusion
pip install -e .

# SE3 equivariant networks (required)
pip install dgl -f https://data.dgl.ai/wheels/repo.html
pip install e3nn

# Download model weights (~1.5GB total)
mkdir models
cd models
wget http://files.ipd.uw.edu/pub/RFdiffusion/6f5902ac237024bdd0c176cb93063dc4/Base_ckpt.pt
wget http://files.ipd.uw.edu/pub/RFdiffusion/e29311f6f1bf1af907f9ef9f44b8328b/Complex_base_ckpt.pt
```

**If no local GPU — use Colab instead:**
- Open the official RFDiffusion Colab: https://colab.research.google.com/github/sokrypton/ColabDesign/blob/v1.1.1/rf/examples/diffusion.ipynb
- Upload your `myostatin_target.pdb` to Colab
- Follow the binder design section
- Download the output backbone PDBs to `rfdiffusion/outputs/`
- Continue the rest of the pipeline locally

### Running binder hallucination

The key command for binder design (run from `RFdiffusion/` directory):

```bash
python scripts/run_inference.py \
  inference.output_prefix=../myostatin_binder/rfdiffusion/outputs/design \
  inference.input_pdb=../myostatin_binder/data/prepared/myostatin_target.pdb \
  'contigmap.contigs=[A1-109/0 45-60]' \
  'ppi.hotspot_res=[A33,A34,A35,A85,A86,A87]' \
  inference.num_designs=20 \
  denoising_steps=50
```

> **Note:** the contig must match the *actual resolved* residue range and numbering of the extracted **5JI1** GDF8 chain (adjust for missing termini/loops; do not assume `A1-109`). The hotspot list above is the **verified** knuckle set from Step 2 — replace these placeholders with whatever your **6MAC** superposition confirmed. Binder length is set to **45–60** to respect the 6 GB VRAM budget from Step 0.

**Breaking down the key parameters:**

| Parameter | What it controls | What to set |
|---|---|---|
| `contigmap.contigs` | Target chain range / binder length range | `[A1-109/0 45-60]` = use resolved chain A of target, design a 45–60-residue binder |
| `ppi.hotspot_res` | Residues the binder must contact | Your **verified** knuckle residues from Step 2 (chain-A numbering) |
| `inference.num_designs` | How many backbone attempts | Start with 20; 100+ for serious work |
| `denoising_steps` | Quality vs speed tradeoff | 50 for testing, 200 for final designs |

**Pay attention to during the run:**
- Watch the loss values printed per step — they should decrease. If they spike or go NaN, something is wrong (usually a GPU memory issue or a corrupt input PDB).
- RFDiffusion will print a pAE-interaction proxy score per design. Higher is generally better but this is not the final validation metric.
- Output PDBs will be named `design_0.pdb`, `design_1.pdb`, etc. Each is a backbone only — no sequence information yet. You will see only Cα atoms or a poly-glycine backbone.

**What good output looks like:**
- Backbone PDB with a small helical protein docked against the target surface
- The designed chain is physically touching the hotspot residues
- No steric clashes visible in PyMOL
- Chain lengths in the 40–70 residue range

**What bad output looks like:**
- Binder floating away from the target
- Fully extended / coil-like binder (no secondary structure)
- Binder on the wrong face of the protein
- Zero contact with hotspot residues

After the run: open each design in PyMOL alongside the target, visually inspect. Keep the top 5–10 for ProteinMPNN.

---

## Step 4 — ProteinMPNN Sequence Design

### Installation

```bash
conda create -n proteinmpnn python=3.9 -y
conda activate proteinmpnn
pip install torch numpy

git clone https://github.com/dauparas/ProteinMPNN.git
cd ProteinMPNN
# No further install needed — it's pure Python
```

### Preparing input

ProteinMPNN needs:
1. Your designed backbone PDB from RFDiffusion (binder + target complex)
2. A specification of which chain to design (the binder) and which to fix (the target)

The target chain sequence is fixed — you do not redesign the myostatin surface. Only the binder chain gets new sequences.

### Running ProteinMPNN

```bash
conda activate proteinmpnn
cd ProteinMPNN

python protein_mpnn_run.py \
  --pdb_path ../myostatin_binder/rfdiffusion/outputs/design_0.pdb \
  --pdb_path_chains_to_design "B" \
  --out_folder ../myostatin_binder/proteinmpnn/outputs/ \
  --num_seq_per_target 8 \
  --sampling_temp "0.1" \
  --seed 42 \
  --batch_size 1
```

**Breaking down key parameters:**

| Parameter | What it controls | What to set |
|---|---|---|
| `--pdb_path_chains_to_design` | Which chain(s) to assign new sequences | Your binder chain (check in PyMOL — usually chain B) |
| `--num_seq_per_target` | Sequences generated per backbone | 8 for testing; 32–64 for serious sampling |
| `--sampling_temp` | Sequence diversity (higher = more diverse) | 0.1 for conservative; 0.2 for diversity |

**What good output looks like:**
- FASTA file with 8 sequences per backbone
- Each sequence has a log-probability (score) printed — lower (more negative) is better in ProteinMPNN's convention (it's a log-likelihood)
- Sequences should be ~40–70 amino acids matching your binder length
- No stop codons, no X residues

**Pay attention to:** ProteinMPNN sometimes outputs identical or near-identical sequences at low temperature. If all 8 sequences look the same, raise `sampling_temp` to 0.2. The diversity in sequences is what gives you multiple candidates to validate.

---

## Step 5 — ESMFold Validation

This is the critical gate. You are asking: does this designed sequence fold into the backbone shape RFDiffusion intended?

You fold each sequence *without* giving ESMFold any structure information — if it independently arrives at a structure matching your design backbone, that's a strong signal the sequence is designable.

### Using the ESMFold REST API (no local GPU needed)

```python
import requests
import json

def fold_sequence(sequence: str, name: str, output_dir: str):
    """Fold a single sequence via ESMFold API and save PDB."""
    url = "https://api.esmatlas.com/foldSequence/v1/pdb/"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    
    response = requests.post(url, headers=headers, data=sequence, timeout=120)
    
    if response.status_code == 200:
        pdb_string = response.text
        out_path = f"{output_dir}/{name}.pdb"
        with open(out_path, "w") as f:
            f.write(pdb_string)
        print(f"Saved: {out_path}")
        return pdb_string
    else:
        print(f"Error {response.status_code}: {response.text}")
        return None
```

Parse pLDDT from the B-factor column of the output PDB (ESMFold stores per-residue pLDDT there).

### Validation metrics — what you are measuring

| Metric | Threshold | What it means |
|---|---|---|
| **pTM** (predicted TM-score) | > 0.7 | Global fold confidence. < 0.5 = likely disordered |
| **pLDDT** (per-residue) | Mean > 70 | Local structural confidence. < 50 = disordered region |
| **RMSD to design** | < 2.0 Å | How well the folded sequence matches the designed backbone |

The RMSD comparison requires PyMOL or TMalign:
```bash
# TMalign (install via conda)
conda install -c bioconda tmalign
TMalign esm_predicted.pdb rfdiffusion_backbone.pdb
```

**What a successful design looks like:**
- ESMFold predicts a compact folded structure (not a disordered chain)
- The predicted structure, when superposed onto the RFDiffusion backbone, gives RMSD < 2Å
- pTM > 0.7
- The binding interface residues have pLDDT > 70

**What a failed design looks like:**
- ESMFold outputs a disordered coil (pTM < 0.5, pLDDT < 50 throughout)
- The fold is completely different from the design backbone (RMSD > 5Å)
- This means the sequence does not encode the intended structure — go back to ProteinMPNN, try different temperature or more sequences

---

## Step 6 — Ranking and Final Selection

> ⚠️ **SUPERSEDED 2026-09-26 — the recipe below is wrong on both clauses.** The
> ESMFold API returns **no pTM**, so criterion 1 cannot be evaluated; and the
> ProteinMPNN score **does not predict refold accuracy** (Spearman ρ = −0.06,
> n = 64), so criterion 4 ranks on noise. The method actually used is in the
> 2026-09-26 session log above and in `docs/methods/06-ranking.md`: designability
> as a gate, interface area as the objective, one representative per backbone.
> Kept here only to show what changed and why.

Build a scoring table `esm_validation/scores.tsv`:

```
design_id    backbone    seq_id    pTM    mean_pLDDT    RMSD_to_design    mpnn_score
design_0_seq1   design_0    1     0.82    78.3          1.4               -1.34
design_0_seq2   design_0    2     0.61    61.0          3.8               -1.21
...
```

Filter criteria (apply in order):
1. pTM > 0.7
2. mean pLDDT > 70
3. RMSD to design backbone < 2.0 Å
4. Among passing designs, rank by ProteinMPNN log-likelihood (more negative = better)

Take the top 3–5 sequences. Open them in PyMOL alongside the myostatin target. Visually confirm interface contacts. These are your final designs.

---

## What to be able to say about this project

After completing this pipeline, you can credibly state:

> *"I ran RFdiffusion binder hallucination against the ActRIIB-binding epitope of apo myostatin (PDB 5JI1), using hotspot residues transferred by homology from the GDF11:ActRIIB complex (PDB 6MAC; GDF11 is ~90 % identical to GDF8 in the mature domain). I designed sequences for the resulting backbones with ProteinMPNN and validated self-consistency by refolding with ESMFold, filtering for pTM > 0.7 and RMSD < 2 Å to the design backbone."*

That sentence is technically precise, tells the full pipeline story, and demonstrates you understand what each tool contributes.

---

## Known Failure Modes — Read Before You Start

| Problem | Likely cause | Fix |
|---|---|---|
| RFDiffusion crashes on import | CUDA/PyTorch version mismatch | Match torch version to your CUDA version exactly |
| Binder doesn't contact hotspots | Wrong residue numbering | Re-inspect PDB chain numbering in PyMOL |
| All ProteinMPNN sequences identical | Temperature too low | Raise `sampling_temp` to 0.2 |
| ESMFold API timeout | Sequence too long or server busy | Retry; sequences >600 AA will fail |
| High RMSD in all designs | Backbone too difficult to encode | Try shorter binder length (40–50 residues) |
| Structure repair needed | Poor input PDB | Run `pdbfixer` or use AF2 model instead |

---

## References (papers to read alongside doing this)

1. **RFDiffusion** — Watson et al., *Nature* 2023. "De novo design of protein structure and function with RFdiffusion."
2. **ProteinMPNN** — Dauparas et al., *Science* 2022. "Robust deep learning–based protein sequence design using ProteinMPNN."
3. **ESMFold** — Lin et al., *Science* 2023. "Evolutionary-scale prediction of atomic-level protein structure with a language model."
4. **Myostatin structure** — Cash, Rejon, McPherron, Bernard, Thompson. *EMBO J* 2009, 28:2662–2676. "The structure of myostatin:follistatin 288: insights into receptor utilization and heparin binding." **PDB 3HH2** (myostatin chains A/B + follistatin-288 chains C/D). This is the Step 1 target structure — read the "receptor utilization" section for how type I/II sites map onto myostatin.
5. **ActRIIB type II epitope template** — Thompson, Woodruff, Jardetzky, et al. *EMBO J* 2003. "Structures of an ActRIIB:activin A complex reveal a novel binding mode." **PDB 1NYS / 1NYU** — defines the knuckle interface (receptor triad Tyr60/Trp78/Phe101; ligand contacts Ala31/Pro32/Leu92). Step 2 homology template.

---

## Status Tracker

- [x] Step 0: Assess local GPU — RTX 4050 6GB (local GPU OK, small binders 45–60 res). Now on **native Ubuntu** (WSL2 plan dropped); Miniforge installed.
- [x] Infra: Repo restructured to scientific best-practices (README, LICENSE, CITATION.cff, Makefile, mkdocs, .gitignore, docs/ wiki, envs/, scripts/) — 2026-06-28.
- [x] Infra: All three conda envs created + verified — 2026-06-28. **rfdiffusion GPU stack fully GREEN** (torch 2.3.1/dgl 2.3.0/e3nn 0.5.6, GPU matmul + dgl-graph-on-GPU + SE3Transformer import; RFdiffusion 1.1.0 + weights installed); proteinmpnn CPU; esm.
- [x] Step 1: **Target prepared — 2026-08-10.** 5JI1 fetched → chain A extracted, HETATM/waters/MPD stripped, altlocs collapsed → `data/prepared/myostatin_target.pdb` (729 atoms, 95 resolved residues in 2 segments: **1–50, 65–109**). Numbering = mature (Asp1 = 1), no conversion needed. Mouse GDF8, 100 % identical to human mature domain. Monomer chosen (dimer buries no epitope surface). Script: `scripts/01_prepare_target.py`.
- [x] Step 2: **Hotspots finalized — 2026-08-12.** Footprint transferred from **6MAC** *and* corroborated with **7MRZ** (identical 21-residue consensus). 20/21 contacts identical GDF11↔GDF8 (only Q91→E, conservative); zero dimer occlusion. Final: **`ppi.hotspot_res=[A33,A34,A85,A87,A93,A95]`** → `hotspots/hotspot_residues.txt`. Provisional list corrected: **M84 dropped** (buries 0.2 Å²), **Y86 dropped** (it is on the *type I*/ALK5 interface, not type II), **I93+Y95 added**. Script: `scripts/02_hotspots.py`.
- [x] Step 3: RFDiffusion env fully installed + GPU-verified (setup script run; RFdiffusion 1.1.0 + weights present). Ready to generate backbones.
- [x] Step 3: **20 backbone designs generated — 2026-08-12.** `Complex_base_ckpt.pt`, T=50, noise_scale 0, 0.76 min/design, no OOM. Contig `[A1-50/A65-109/0 45-60]`, hotspots from Step 2. Script: `scripts/03_rfdiffusion.sh`.
- [x] Step 3: **Triaged + inspected — 2026-08-12.** 17/20 PASS; all 20 dock the correct epitope (5–6 of 6 hotspots). 3 rejected as extended (single-helix, Rg ≈2.3× folded expectation). **Shortlist of 8:** design_5, 18, 15, 14, 12, 11, 4, 9 — all 6/6 hotspots, 370–469 Å² buried, 88–95 % helical. Key gotcha: output is **backbone-only**, so naive scoring calls every design a floater — see the session log. Scripts: `scripts/03b_triage_backbones.py`, `scripts/03c_render_designs.py`.
- [x] Step 4: ProteinMPNN environment installed (CPU torch); **repo cloned 2026-08-12** (weights ship with it).
- [x] Step 4: **Sequences generated — 2026-08-12.** 64 sequences (8 backbones × 8) at T=0.1, chain B designed / chain A fixed, Cys omitted. Diversity healthy (66 % mean pairwise identity), no Cys, scores 0.957–1.225. **Hydrophobic gradient 0.33 → 0.46 → 0.57** (whole binder → epitope face → hotspot ring) confirms the sequences match the structural intent. Flag-name gotcha: it is `--pdb_path_chains`, **not** `--pdb_path_chains_to_design`. Scripts: `scripts/04_proteinmpnn.sh`, `scripts/04b_analyze_sequences.py`.
- [x] Step 5: ESMFold validation env installed (API client + TMalign)
- [x] Step 5: **ESMFold validation run — 2026-08-12.** All 64 sequences refolded via the ESM Atlas API; **58/64 (91 %) self-consistent** (RMSD < 2 Å, pLDDT ≥ 70, TM ≥ 0.5, coverage ≥ 90 %). Best `design_12_s4` at **0.40 Å**. Gotchas: API returns **no pTM** (substituted pLDDT + TM-score), **pLDDT on a 0–1 scale**, ~⅓ of calls 504. **Coverage filter is essential** — it caught 4 false passes where TMalign aligned only 30/52 residues at a flattering 0.55 Å. **MPNN score does not predict refolding** (Spearman −0.055 vs RMSD). Script: `scripts/05_esmfold.py`.
- [x] Step 6: **Ranking executed — 2026-09-26.** Gate (RMSD ≤ 1.0 Å, TM ≥ 0.90, coverage = 1.00, pLDDT ≥ 85 mean / ≥ 70 min) passed by **41/58**, all 8 backbones represented; ranked by buried area with a 10 Å² tie band resolved on designability. Panel of 5 in `results/top_designs/`: design_5_s2, design_18_s4, design_12_s4, design_11_s7, design_14_s7. **Single best pick: design_14_s7** (Rg 1.06, pLDDT 93.1, net charge 0). Scripts: `06_rank.py`, `06c_render_top.py`; `make rank`.
- [x] Step 6: Final designs inspected in PyMOL — `06a_inspect.py`, `06b_epitope_anatomy.py`, and the panel session `analysis/pymol_sessions/step6_panel.pse`.

---

*This document is intended to be read by Claude Code at the start of each session. Update the status tracker as steps are completed. Add notes under each step about what was observed, what failed, and why.*
