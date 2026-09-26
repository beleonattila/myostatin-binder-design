#!/usr/bin/env python
"""Step 7b - assemble the PNG frame stacks into looping GIFs plus still frames.

One shared palette per GIF, derived from a montage of every frame, so the
molecule's colours do not shift from frame to frame (which is both uglier and
larger). The still is the first frame; the dashboard shows it to viewers who
prefer reduced motion, and as the paused state.

  RUNS IN THE rfdiffusion ENV, not esm. Pillow ships with that env's torch
  stack and is not installed in esm, while PyMOL (step 7a) is only in esm.
  That split is why rendering and encoding are two scripts.

Run:  conda activate rfdiffusion
      python scripts/07b_frames_to_gif.py [framesdir] [outdir] [colors] [ms]
or:   make dashboard
"""

import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_FRAMES = ROOT / "analysis" / "dashboard" / "frames"
DEFAULT_OUT = ROOT / "analysis" / "dashboard" / "gifs"


def build_palette(frames, colors):
    """Median-cut a vertical montage of all frames -> one representative palette."""
    w, h = frames[0].size
    montage = Image.new("RGB", (w, h * len(frames)))
    for i, fr in enumerate(frames):
        montage.paste(fr, (0, i * h))
    return montage.quantize(colors=colors, method=Image.MEDIANCUT)


def assemble(src, gif, still, colors, duration):
    pngs = sorted(src.glob("*.png"))
    if not pngs:
        return None
    frames = [Image.open(p).convert("RGB") for p in pngs]
    pal = build_palette(frames, colors)
    quant = [f.quantize(palette=pal, dither=Image.Dither.NONE) for f in frames]
    quant[0].save(
        gif,
        save_all=True,
        append_images=quant[1:],
        loop=0,
        duration=duration,
        optimize=True,
        disposal=1,
    )
    quant[0].save(still, optimize=True)
    return gif.stat().st_size, still.stat().st_size


def main():
    a = sys.argv[1:]
    framesdir = Path(a[0]) if a else DEFAULT_FRAMES
    outdir = Path(a[1]) if len(a) > 1 else DEFAULT_OUT
    colors = int(a[2]) if len(a) > 2 else 96
    duration = int(a[3]) if len(a) > 3 else 90
    if not framesdir.is_absolute():
        framesdir = ROOT / framesdir
    if not outdir.is_absolute():
        outdir = ROOT / outdir

    if not framesdir.is_dir():
        raise SystemExit(f"no frames at {framesdir} - run scripts/07_render_spins.py first")
    outdir.mkdir(parents=True, exist_ok=True)

    total = 0
    for src in sorted(p for p in framesdir.iterdir() if p.is_dir()):
        res = assemble(src, outdir / f"{src.name}.gif",
                       outdir / f"{src.name}_still.png", colors, duration)
        if res is None:
            print(f"  {src.name}: no frames, skipped")
            continue
        gif, still = res
        total += gif + still
        print(f"  {src.name}.gif: {gif / 1024:.0f} KB   still: {still / 1024:.0f} KB")
    print(f"total {total / 1024:.0f} KB  (base64 ~{total * 4 / 3 / 1024:.0f} KB)")


main()
