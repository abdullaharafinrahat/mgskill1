# -*- coding: utf-8 -*-
"""Contact sheets: one frame from (almost) every shot, for visual QA."""
import sys, cairo
from PIL import Image
from registry import *
sel = [int(a) for a in sys.argv[2:]] if len(sys.argv) > 2 else list(range(len(SHOTS)))
frac = float(sys.argv[1]) if len(sys.argv) > 1 else 0.7
tiles = []
for k in sel:
    fn, sc, g0, g1 = SHOTS[k]
    gt = g0 + (g1 - g0) * frac + 0.01
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    ctx = cairo.Context(surf)
    draw_frame(ctx, gt)
    surf.write_to_png("/tmp/_f.png")
    im = Image.open("/tmp/_f.png").convert("RGB").resize((360, 640), Image.LANCZOS)
    tiles.append(im)
cols = 4
rows = (len(tiles) + cols - 1) // cols
sheet = Image.new("RGB", (cols * 364, rows * 644), (20, 20, 20))
for i, im in enumerate(tiles):
    sheet.paste(im, ((i % cols) * 364 + 2, (i // cols) * 644 + 2))
sheet.save("preview/sheet.png")
print("ok", len(tiles))
