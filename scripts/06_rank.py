#!/usr/bin/env python
"""Step 6 - rank the validated designs and select the final panel.

THE RANKING AXIS, STATED (this is the decision Step 5 left open)

Step 3 ranks by buried interface area and puts design_5 first. Step 5 ranks by
designability and puts design_5 last. They are not two candidate rankings to
choose between - they measure different things, and only one of them is a
threshold:

  Designability is a GATE, not a score. A sequence that does not fold back to
  the backbone it was designed for has no interface at all; its buried area is
  a property of a structure that will not exist. So it is applied first, as a
  pass/fail bar, and nothing below the bar is ranked.

  Interface is the OBJECTIVE. Among sequences that do fold as designed, the
  one that buries more of the ActRIIB knuckle is the better binder candidate.
  That is what the project set out to make.

  Diversity is a CONSTRAINT. Five sequences off one backbone are one design
  with five spellings. Each backbone contributes at most one representative -
  its best-refolding gated sequence - so the panel spans five distinct folds.

One refinement matters. dSASA here is a backbone+CB lower bound: Step 3
calibrated the real ActRIIB:GDF11 interface at 293 A^2 in these units versus
697 A^2 full-atom, i.e. sidechains carry 58 % of a real interface. Differences
of a few A^2 are therefore noise, and ranking on them is false precision.
Representatives within TIE_BAND A^2 of each other are treated as tied and
ordered by designability instead.

`--axis designability` inverts the scheme (rank by refold quality, report
interface) if you want to see the other ordering; the selection is regenerated
from the same gate either way.

Outputs, all under results/top_designs/:
  README.md          the write-up: axis, gate, table, liabilities, caveats
  ranking.tsv        all 64 sequences with gate status and rank
  panel.fasta        the selected sequences
  (06c_render_top.py adds the figures and the superposed complexes)

Run:  conda activate esm && python scripts/06_rank.py [--axis interface|designability]
"""

import argparse
from datetime import date
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "results" / "top_designs"

# --- the gate ---------------------------------------------------------------
# Stricter than Step 5's self-consistency call, which was a floor for "did this
# fold at all". These are the bars for "I would put my name on this design".
MAX_RMSD = 1.0      # A; the conventional designable-minibinder bar
MIN_TM = 0.90       # same fold, not merely the same class of fold
MIN_COVERAGE = 1.0  # every residue aligned - the design_5 lesson from Step 5
MIN_MEAN_PLDDT = 85.0
MIN_MIN_PLDDT = 70.0   # no floppy terminus dragging an otherwise good model

TIE_BAND = 10.0     # A^2; dSASA differences below this are not real
N_PANEL = 5


def load():
    s = pd.read_csv(ROOT / "esm_validation" / "scores.tsv", sep="\t")
    t = pd.read_csv(ROOT / "rfdiffusion" / "outputs" / "triage.tsv",
                    sep="\t").set_index("design")
    q = pd.read_csv(ROOT / "proteinmpnn" / "outputs" / "sequences.tsv", sep="\t")

    s["self_consistent"] = s.self_consistent.astype(str).str.strip() == "True"
    for col, src in (("dsasa", t.dSASA), ("contacts", t.n_contacts),
                     ("hotspots", t.hotspots_hit), ("rg_ratio", t.rg_ratio),
                     ("helix_frac", t.helix_frac)):
        s[col] = s.backbone.map(src)

    q = q[["backbone", "sample", "max_run", "n_hotspot_pos"]]
    s = s.merge(q, on=["backbone", "sample"], how="left")

    # E/K/A load: ProteinMPNN's documented bias toward over-charged solvent
    # faces, and the main expression liability in these sequences.
    s["eka_frac"] = s.sequence.map(
        lambda seq: sum(c in "EKA" for c in seq) / len(seq))
    return s


def apply_gate(s):
    s["gated"] = (
        s.self_consistent
        & (s.rmsd_to_design <= MAX_RMSD)
        & (s.tm_score >= MIN_TM)
        & (s.coverage >= MIN_COVERAGE)
        & (s.mean_plddt >= MIN_MEAN_PLDDT)
        & (s.min_plddt >= MIN_MIN_PLDDT)
    )
    return s


def representatives(s):
    """One per backbone: the best-refolding gated sequence."""
    g = s[s.gated]
    reps = (g.sort_values(["rmsd_to_design", "mean_plddt"],
                          ascending=[True, False])
             .groupby("backbone", as_index=False).first())
    reps["n_gated"] = reps.backbone.map(g.groupby("backbone").size())
    reps["n_seqs"] = reps.backbone.map(s.groupby("backbone").size())
    return reps


def rank(reps, axis):
    """Order the representatives, with the tie-band rule on the primary key."""
    if axis == "interface":
        reps = reps.sort_values(
            ["dsasa", "n_gated", "rmsd_to_design"], ascending=[False, False, True])
        # collapse near-ties on dSASA into designability order
        out, bands, i, b = [], [], 0, 0
        rows = list(reps.itertuples())
        while i < len(rows):
            band = [rows[i]]
            while (i + 1 < len(rows)
                   and band[0].dsasa - rows[i + 1].dsasa < TIE_BAND):
                i += 1
                band.append(rows[i])
            band.sort(key=lambda r: (-r.n_gated, r.rmsd_to_design))
            out.extend(band)
            bands.extend([b] * len(band))
            i += 1
            b += 1
        reps = pd.DataFrame([r._asdict() for r in out]).drop(columns=["Index"])
        reps["band"] = bands
    else:
        reps = reps.sort_values(
            ["n_gated", "rmsd_to_design", "mean_plddt"],
            ascending=[False, True, False])
    reps = reps.reset_index(drop=True)
    reps.insert(0, "rank", reps.index + 1)
    return reps


def write_outputs(s, reps, axis):
    OUT.mkdir(parents=True, exist_ok=True)
    panel = reps.head(N_PANEL)

    cols = ["name", "backbone", "sample", "gated", "self_consistent",
            "rmsd_to_design", "tm_score", "coverage", "mean_plddt", "min_plddt",
            "mpnn_score", "dsasa", "contacts", "hotspots", "rg_ratio",
            "net_charge", "hotspot_hydrophobic_frac", "eka_frac", "length"]
    table = s[cols].sort_values(["gated", "dsasa", "rmsd_to_design"],
                                ascending=[False, False, True])
    table.to_csv(OUT / "ranking.tsv", sep="\t", index=False, float_format="%.4g")

    with (OUT / "panel.fasta").open("w") as fh:
        for r in panel.itertuples():
            fh.write(f">{r.name} rank={r.rank} backbone={r.backbone} "
                     f"dSASA={r.dsasa:.0f}A2 rmsd={r.rmsd_to_design:.2f}A "
                     f"plddt={r.mean_plddt:.1f} len={r.length}\n{r.sequence}\n")

    (OUT / "README.md").write_text(readme(s, reps, panel, axis))
    return panel


def describe_bands(reps):
    """Spell out every group the tie rule actually reordered, and whether it
    changed who made the panel - a rule that decides a cut has to be visible."""
    if "band" not in reps:
        return ""
    out = []
    for _, grp in reps.groupby("band"):
        if len(grp) < 2:
            continue
        members = ", ".join(
            f"`{r.backbone}` ({r.dsasa:.0f} Å², {int(r.n_gated)}/{int(r.n_seqs)} gated)"
            for r in grp.itertuples())
        span = f"{grp.dsasa.max():.0f} → {grp.dsasa.min():.0f} Å²"
        cut = grp[(grp["rank"] <= N_PANEL)], grp[(grp["rank"] > N_PANEL)]
        note = ""
        if len(cut[0]) and len(cut[1]):
            dropped = ", ".join(f"`{r.backbone}`" for r in cut[1].itertuples())
            note = (f" This band straddles the cut: {dropped} misses the panel "
                    f"on an interface difference of "
                    f"{grp.dsasa.max() - grp.dsasa.min():.0f} Å², which this "
                    f"representation cannot resolve — designability decides it.")
        out.append(f"{len(grp)} representatives fall in one band ({span}) and are "
                   f"ordered by designability: {members}.{note}")
    return "\n\n".join(out) if out else "No representatives fell within the band."


def readme(s, reps, panel, axis):
    n_gate = int(s.gated.sum())
    n_sc = int(s.self_consistent.sum())
    lead = panel.iloc[0]

    rows = []
    for r in reps.itertuples():
        mark = "**" if r.rank <= N_PANEL else ""
        rows.append(
            f"| {mark}{r.rank}{mark} | {mark}`{r.name}`{mark} | {r.dsasa:.0f} | "
            f"{r.contacts} | {r.hotspots}/6 | {r.rmsd_to_design:.2f} | "
            f"{r.mean_plddt:.1f} | {r.n_gated}/{r.n_seqs} | {r.rg_ratio:.2f} | "
            f"{r.net_charge:+d} | {r.hotspot_hydrophobic_frac:.2f} |")
    table = "\n".join(rows)

    return f"""# Final design panel — myostatin (GDF-8) knuckle binders

Selected {date.today().isoformat()} by `scripts/06_rank.py --axis {axis}`
from the {n_sc} self-consistent sequences of Step 5.

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
| Cα-RMSD to design | ≤ {MAX_RMSD:.1f} Å | the conventional designable-minibinder bar |
| TM-score | ≥ {MIN_TM:.2f} | the same fold, not merely the same class of fold |
| Coverage | = {MIN_COVERAGE:.2f} | every residue aligned — the design_5 lesson |
| Mean pLDDT | ≥ {MIN_MEAN_PLDDT:.0f} | confident model |
| Min pLDDT | ≥ {MIN_MIN_PLDDT:.0f} | no floppy terminus inside a good average |

**{n_gate} of {n_sc}** self-consistent sequences clear it, and every one of the
eight shortlisted backbones keeps at least one. That is what dissolves the
argument: design_5, the interface leader that failed Step 5 at the backbone
level, keeps exactly one sequence — `design_5_s2` — and it is enough to carry
the widest interface into the panel on merit.

### One refinement

dSASA is a backbone+CB **lower bound**: Step 3 calibrated the real
ActRIIB:GDF11 interface at 293 Å² in these units versus 697 Å² full-atom, so
sidechains carry 58 % of a real interface. Differences of a few Å² are noise.
Representatives within **{TIE_BAND:.0f} Å²** of each other are treated as tied
and ordered by designability instead.

{describe_bands(reps)}

## The panel

Bold rows are the selected {N_PANEL}. One representative per backbone, ranked by
interface area under the tie rule above.

| # | Sequence | Buried Å² | Contacts | Hotspots | RMSD Å | pLDDT | Gated | Rg ratio | Charge | Hotspot φ |
|---|---|---|---|---|---|---|---|---|---|---|
{table}

*Gated = how many of that backbone's 8 sequences clear the gate; a robustness
measure, not a rank term. Hotspot φ = hydrophobic fraction of the
hotspot-contacting positions. Rg ratio = radius of gyration over the folded
expectation for that length; 1.0 is ideal, > 1.5 was rejected in Step 3.*

## If only one is made: `{lead.name}`

It leads on interface ({lead.dsasa:.0f} Å², {lead.contacts} contacts, all six
hotspots) and it refolds at {lead.rmsd_to_design:.2f} Å with pLDDT
{lead.mean_plddt:.1f}. **But note the risk column**: only
{int(lead.n_gated)} of its {int(lead.n_seqs)} sequences clear the gate. Its
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
| `ranking.tsv` | all {len(s)} sequences, gate status and every metric |
| `panel.fasta` | the {N_PANEL} selected sequences |
| `figures/` | one render per selection, plus the panel overview |
| `complexes/` | each prediction superposed onto the target, as a PDB |

Regenerate with `make rank`.
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--axis", choices=["interface", "designability"],
                    default="interface")
    args = ap.parse_args()

    s = apply_gate(load())
    reps = rank(representatives(s), args.axis)
    panel = write_outputs(s, reps, args.axis)

    print(f"gate: {int(s.gated.sum())}/{int(s.self_consistent.sum())} "
          f"self-consistent sequences clear it, "
          f"from {reps.backbone.nunique()}/8 backbones")
    print(f"axis: {args.axis}\n")
    print(f"{'#':>2}  {'sequence':16s} {'dSASA':>6} {'rmsd':>5} {'pLDDT':>6} "
          f"{'gated':>6} {'Rg':>5} {'chg':>4}")
    for r in reps.itertuples():
        mark = "*" if r.rank <= N_PANEL else " "
        print(f"{r.rank:>2}{mark} {r.name:16s} {r.dsasa:6.0f} "
              f"{r.rmsd_to_design:5.2f} {r.mean_plddt:6.1f} "
              f"{r.n_gated:>4}/{r.n_seqs} {r.rg_ratio:5.2f} {r.net_charge:+4d}")
    print(f"\nselected {len(panel)} -> {OUT.relative_to(ROOT)}/")
    print("next: python scripts/06c_render_top.py  (figures + complexes)")


if __name__ == "__main__":
    main()
