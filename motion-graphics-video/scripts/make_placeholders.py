#!/usr/bin/env python3
"""Resolve the assets a storyboard asks for.

For every asset slot the storyboard references, this script either finds the
file, or:

  1. writes a **placeholder** so the render is never blocked, and
  2. writes an **exact generation prompt** into ASSETS_REQUEST.md so the
     asset can be produced later (by the agent, or by the user, or by a
     designer).

The prompt is written to be handed straight to an image model, so it
specifies: subject, framing, lighting, palette, lens, and what the asset
must leave room for (e.g. "the lower third must stay clear for a label").

    python make_placeholders.py storyboard.json --outdir assets/ \\
        --requests ASSETS_REQUEST.md
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from mgv import theme as T
from mgv import components as C
from mgv import draw as D
from mgv import storyboard as SB


def placeholder(kind, size, seed, label):
    """A designed placeholder, not a grey box - a flat vector stand-in that
    already sits in the film's visual language."""
    w, h = size
    rng = np.random.default_rng(seed)
    img = Image.new("RGB", size, tuple(T.VOID))
    # soft colour wash
    cols = [tuple(T.NAVY), tuple(T.ELECTRIC), tuple(T.SKY), tuple(T.PERIWINKLE)]
    ov = D.bokeh_background(size, cols, count=26, seed=seed, alpha=60,
                            max_r=0.22)
    img = D.overlay_alpha(img, ov)
    d = ImageDraw.Draw(img)
    # diagonal hatch so it is obviously a stand-in
    step = max(18, w // 18)
    for i in range(-h, w + h, step):
        d.line([(i, 0), (i + h, h)], fill=(255, 255, 255, 18), width=2)
    d.rectangle([0, 0, w - 1, h - 1], outline=tuple(T.SKY), width=max(2, w // 200))
    font = None
    try:
        from mgv import fonts as F
        fonts_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "assets", "fonts")
        spec = F.font_for(F.resolve_fonts(fonts_dir), "bold")
        if spec:
            font = F.make_font(spec[0], max(12, int(min(w, h) * 0.075)), spec[1])
    except Exception:
        font = None
    if font is None:
        from PIL import ImageFont
        font = ImageFont.load_default()
    D.draw_text(d, (w / 2, h / 2), label, font, fill=(235, 242, 244), anchor="mm")
    return img


def build_prompt(slot):
    """Compose a generation prompt from the slot's declared intent."""
    subject = slot.get("subject", slot.get("id", "asset"))
    kind = slot.get("kind", "image")
    w = slot.get("width", 1920)
    h = slot.get("height", 1080)
    style = slot.get("style",
                     "cinematic 3D render, deep navy and electric azure palette, "
                     "soft rim light, shallow depth of field, no text, no logos, "
                     "no people's faces unless specified")
    use = slot.get("use", "")
    leave = slot.get("leave_clear", "")
    ratio = f"{w}x{h} ({'16:9' if abs(w / h - 16 / 9) < 0.05 else 'portrait' if h > w else 'square'})"
    parts = [
        f"Subject: {subject}.",
        f"Format: {ratio}.",
        f"Style: {style}.",
    ]
    if use:
        parts.append(f"Purpose in the edit: {use}.")
    if leave:
        parts.append(f"Composition constraint: {leave}.")
    if kind == "portrait":
        parts.append("Photoreal head-and-shoulders portrait, neutral expression, "
                     "looking at camera, even soft key light, plain dark background.")
    parts.append("No text, no watermark, no borders.")
    return " ".join(parts)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("storyboard")
    ap.add_argument("--outdir", default="assets")
    ap.add_argument("--requests", default="ASSETS_REQUEST.md")
    ap.add_argument("--no-placeholders", action="store_true")
    args = ap.parse_args()

    sb = SB.load(args.storyboard)
    slots = list(sb.get("assets_needed", []))
    # also pick up asset layers that reference a missing file
    for si, shot in enumerate(sb.get("shots", [])):
        for li, layer in enumerate(shot.get("layers", [])):
            if layer.get("type") in SB.ASSET_LAYER_TYPES:
                src = layer.get("src")
                if src and not os.path.exists(src):
                    slots.append({
                        "id": f"{shot.get('id')}_l{li}",
                        "kind": layer.get("type"),
                        "path": layer.get("_rel_path", src),
                        "width": int(layer.get("w", 0.4) * 1920),
                        "height": int(layer.get("h", 0.1) * 1080),
                        "subject": layer.get("subject", layer.get("text", "visual asset")),
                        "use": layer.get("purpose", shot.get("purpose", "")),
                        "leave_clear": layer.get("leave_clear", ""),
                    })

    os.makedirs(args.outdir, exist_ok=True)
    created, needed = [], []
    for i, slot in enumerate(slots):
        path = slot.get("path") or os.path.join(args.outdir, f"{slot.get('id', f'asset{i}')}.png")
        if os.path.exists(path):
            continue
        needed.append(slot)
        if args.no_placeholders:
            continue
        w = int(slot.get("width", 1920) or 1920)
        h = int(slot.get("height", 1080) or 1080)
        img = placeholder(slot.get("kind", "image"), (w, h), i + 3,
                          slot.get("subject", "ASSET")[:22].upper())
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        img.save(path)
        created.append(path)
        slot["_placeholder"] = path

    if needed:
        with open(args.requests, "w", encoding="utf-8") as f:
            f.write("# Assets needed\n\n")
            f.write("These are the visual assets this video asks for. Each one is "
                    "listed with a ready-to-use generation prompt.\n\n")
            f.write("**If you can generate images, generate them.** Paste the "
                    "prompt into your image model, save the output at the exact "
                    "path given, and re-run the build. If you cannot, hand these "
                    "to the user and ask them to supply the files at those "
                    "paths.\n\n")
            for slot in needed:
                f.write(f"## {slot.get('id', 'asset')}\n\n")
                f.write(f"- **Save to:** `{slot.get('path')}`\n")
                f.write(f"- **Size:** {slot.get('width', 1920)}x{slot.get('height', 1080)}"
                        f"  ·  **Kind:** {slot.get('kind', 'image')}\n")
                if slot.get("placeholder"):
                    f.write(f"- **Placeholder written to:** `{slot['_placeholder']}` "
                            "(replace it with the real asset)\n")
                f.write("\n**Prompt**\n\n```\n" + build_prompt(slot) + "\n```\n\n")
        print(f"wrote {args.requests} ({len(needed)} asset(s) requested)")
    if created:
        print(f"wrote {len(created)} placeholder(s):")
        for c in created:
            print(f"  {c}")
    if not needed:
        print("all assets present - nothing to request")
    return 0


if __name__ == "__main__":
    sys.exit(main())
