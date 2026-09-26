#!/usr/bin/env python
"""Step 7c - compute the dashboard's numbers and build the standalone page.

Two jobs, kept in one script so the page can never disagree with the data:

  1. Roll up esm_validation/scores.tsv and rfdiffusion/outputs/triage.tsv into
     one JSON blob, recomputing the Spearman correlations from the committed
     data rather than copying them out of CONTEXT.md.
  2. Inject that blob and the GIFs (as base64 data URIs) into
     scripts/dashboard_template.html, producing a single self-contained file.

Everything is embedded because the page is published as an artifact, which
loads no external images.

Run:  conda activate esm && python scripts/07c_build_dashboard.py
or:   make dashboard
"""

import base64
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "scripts" / "dashboard_template.html"
OUTDIR = ROOT / "analysis" / "dashboard"
GIFS = OUTDIR / "gifs"
SCENES = ["epitope", "design_5", "design_12", "refold"]


def spearman(a, b):
    """Rank correlation, average ranks for ties (scipy is not in this env)."""
    ra = pd.Series(a).rank().to_numpy()
    rb = pd.Series(b).rank().to_numpy()
    return float(np.corrcoef(ra, rb)[0, 1])


def collect():
    scores = pd.read_csv(ROOT / "esm_validation" / "scores.tsv", sep="\t")
    triage = pd.read_csv(ROOT / "rfdiffusion" / "outputs" / "triage.tsv", sep="\t")
    scores = scores.assign(
        ok=scores["self_consistent"].astype(str).str.strip() == "True")

    tri = triage.set_index("design")
    rows = []
    for bb, g in scores.groupby("backbone"):
        t = tri.loc[bb]
        rows.append({
            "backbone": bb,
            "n": int(len(g)),
            "pass": int(g.ok.sum()),
            "best_rmsd": round(float(g.rmsd_to_design.min()), 2),
            "median_rmsd": round(float(g.rmsd_to_design.median()), 2),
            "best_tm": round(float(g.tm_score.max()), 3),
            "mean_plddt": round(float(g.mean_plddt.mean()), 1),
            "dsasa": float(t.dSASA),
            "contacts": int(t.n_contacts),
            "hotspots": int(t.hotspots_hit),
            "binder_len": int(t.binder_len),
            "rg_ratio": float(t.rg_ratio),
            "helix_frac": float(t.helix_frac),
        })
    rows.sort(key=lambda r: -r["dsasa"])

    pts = [{
        "bb": r.backbone, "s": int(r.sample),
        "mpnn": round(float(r.mpnn_score), 4),
        "rmsd": float(r.rmsd_to_design), "tm": float(r.tm_score),
        "plddt": float(r.mean_plddt), "cov": float(r.coverage),
        "ok": bool(r.ok), "len": int(r.length),
    } for r in scores.itertuples()]

    fail_counts = {}
    for f in scores.loc[~scores.ok, "why_failed"].fillna("").tolist():
        fail_counts[f] = fail_counts.get(f, 0) + 1

    best_mpnn = scores.loc[scores.mpnn_score.idxmin()]
    best_rmsd = scores.loc[scores.rmsd_to_design.idxmin()]

    return {
        "correlations": {
            "mpnn_rmsd": round(spearman(scores.mpnn_score, scores.rmsd_to_design), 3),
            "mpnn_tm": round(spearman(scores.mpnn_score, scores.tm_score), 3),
            "plddt_rmsd": round(spearman(scores.mean_plddt, scores.rmsd_to_design), 3),
            "plddt_tm": round(spearman(scores.mean_plddt, scores.tm_score), 3),
        },
        "backbones": rows,
        "points": pts,
        "fail_counts": fail_counts,
        "totals": {
            "sequences": int(len(scores)),
            "self_consistent": int(scores.ok.sum()),
            "under_half_angstrom": int((scores.rmsd_to_design < 0.5).sum()),
            "designs_generated": int(len(triage)),
            "designs_pass": int((triage.verdict == "PASS").sum()),
            "designs_shortlisted": int((triage.shortlisted.astype(str) == "True").sum()),
            "all_six_hotspots": int((triage.hotspots_hit == 6).sum()),
            "best": str(best_rmsd["name"]),
            "best_rmsd": float(best_rmsd.rmsd_to_design),
            "dsasa_min": float(triage.dSASA.min()),
            "dsasa_max": float(triage.dSASA.max()),
            "helix_min": float(triage.helix_frac.min()),
            "helix_max": float(triage.helix_frac.max()),
            "mpnn_min": float(scores.mpnn_score.min()),
            "mpnn_max": float(scores.mpnn_score.max()),
            "len_min": int(scores.length.min()),
            "len_max": int(scores.length.max()),
        },
        "ranking_paradox": {
            "best_mpnn_name": str(best_mpnn["name"]),
            "best_mpnn_score": float(best_mpnn.mpnn_score),
            "best_mpnn_rmsd": float(best_mpnn.rmsd_to_design),
            "best_refold_name": str(best_rmsd["name"]),
            "best_refold_rmsd": float(best_rmsd.rmsd_to_design),
            "best_refold_mpnn": float(best_rmsd.mpnn_score),
            "best_refold_mpnn_rank":
                int(scores.mpnn_score.rank().loc[scores.rmsd_to_design.idxmin()]),
            "n": int(len(scores)),
        },
    }


def uri(path, mime):
    if not path.exists():
        raise SystemExit(f"missing {path.relative_to(ROOT)} - run "
                         "scripts/07_render_spins.py and 07b_frames_to_gif.py first")
    return f"data:{mime};base64,{base64.b64encode(path.read_bytes()).decode()}"


def main():
    data = collect()
    OUTDIR.mkdir(parents=True, exist_ok=True)
    (OUTDIR / "dashboard_data.json").write_text(json.dumps(data, indent=1))

    c = data["correlations"]
    t = data["totals"]
    print(f"  {t['sequences']} sequences, {t['self_consistent']} self-consistent, "
          f"{t['under_half_angstrom']} under 0.50 A")
    print(f"  spearman mpnn~rmsd {c['mpnn_rmsd']:+.3f}   plddt~rmsd {c['plddt_rmsd']:+.3f}")

    html = TEMPLATE.read_text()
    html = html.replace("{{DATA}}", json.dumps(data, separators=(",", ":")))
    for s in SCENES:
        html = html.replace(f"{{{{GIF_{s}}}}}", uri(GIFS / f"{s}.gif", "image/gif"))
        html = html.replace(f"{{{{STILL_{s}}}}}",
                            uri(GIFS / f"{s}_still.png", "image/png"))

    left = [m for m in ("{{GIF_", "{{STILL_", "{{DATA") if m in html]
    if left:
        sys.exit(f"unfilled placeholders remain: {left}")

    out = OUTDIR / "dashboard.html"
    out.write_text(html)
    mb = out.stat().st_size / 1024 / 1024
    print(f"  wrote {out.relative_to(ROOT)} ({mb:.2f} MB)")
    if mb > 15:
        sys.exit("too big for the 16 MB artifact limit")


main()
