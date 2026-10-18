"""The reusable asset kit.

A full motion-graphics promo can look like hundreds of unique elements while
actually being built from a handful of repeating components. The reference
film uses **eight**: a gradient pill, a speech bubble, a glass card, an
avatar badge, a cursor triangle, a monitor on a stand, a label pill with a
pointer, and a circuit plate.

Building them once, here, means every shot in the storyboard gets the same
material language for free - which is exactly why the reference film reads as
one hand made it.

Every component returns an RGBA image of the requested size, drawn at
supersampled resolution and downscaled internally.
"""
import math

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from . import theme as T
from . import draw as D


def _blank(size):
    return Image.new("RGBA", size, (0, 0, 0, 0))


def _grad_stops(th, name, fallback=None):
    g = th.get("GRADIENTS", T.GRADIENTS)
    return g.get(name, fallback or [th.get("ELECTRIC", T.ELECTRIC), th.get("SKY", T.SKY)])


def _font(th, weight="bold", px=48):
    """Resolve a font from the theme's font table.

    The table holds (path, weight) pairs; components normally receive a
    pre-sized font from the layer, and this is only the fallback."""
    from . import fonts as F
    spec = F.font_for(th.get("FONTS", {}), weight)
    if not spec:
        return None
    path, w = spec
    return F.make_font(path, px, w)


# --------------------------------------------------------------------------
# 1. gradient pill - the most-used component in the film (19 instances)
# --------------------------------------------------------------------------

def pill(th, size, text="", gradient="azure_blue", text_color=None,
         bullet=True, glow_strength=1.0, radius=None, font=None,
         pad_x=0.055, pad_y=0.42, letter_spacing=1.0, shadow=True):
    """Rounded gradient bar with an optional white bullet dot and a neon glow.

    This single component carries the film's meaning: green = money, red =
    wrong, lime = a service tier. Because the colour is a parameter, the
    semantics stay consistent across the whole edit.
    """
    w, h = int(size[0]), int(size[1])
    ss = T.SS
    canvas = _blank((w, h))
    r = radius if radius is not None else h / 2

    mask = D.rounded_rect_mask((w, h), r, supersample=ss)
    body = D.fill_gradient(mask, _grad_stops(th, gradient), angle=0)

    if shadow:
        sh = D.drop_shadow(body, offset=(0, int(h * 0.12)),
                           blur=int(h * 0.22), opacity=0.45)
        canvas = D.overlay_alpha(canvas, sh)

    # bullet dot on the left
    text_col = text_color or th.get("PAPER", T.PAPER)
    f = font or _font(th, "bold")
    d = ImageDraw.Draw(body)
    tx = 0
    if text:
        try:
            bb = d.textbbox((0, 0), text, font=f)
            tw, thh = bb[2] - bb[0], bb[3] - bb[1]
        except Exception:
            tw = thh = int(h * 0.4)
    else:
        tw = thh = int(h * 0.4)

    dot_r = h * 0.075
    left = w * pad_x
    if bullet:
        cx = left + dot_r
        cy = h / 2
        d.ellipse([cx - dot_r, cy - dot_r, cx + dot_r, cy + dot_r], fill=(*text_col, 255))
        tx = cx + dot_r + h * 0.14
    else:
        tx = left

    if text:
        D.draw_text(d, (tx, h / 2), text, f, fill=(*text_col, 255), anchor="lm",
                    letter_spacing=letter_spacing)

    canvas = D.overlay_alpha(canvas, body)
    if glow_strength > 0:
        g = D.glow(body, radius=int(h * 0.35), strength=0.85 * glow_strength)
        canvas = D.screen_layer(canvas, g)
    return canvas


# --------------------------------------------------------------------------
# 2. speech bubble
# --------------------------------------------------------------------------

def bubble(th, size, text="", tail="left", fill=None, text_color=None,
           font=None, glow_strength=0.35, max_width_ratio=0.62):
    """Rounded speech bubble with a triangular tail.

    Two tail positions in the reference film: pointing down-left (a label
    above a subject) and pointing left (a reply). Colour distinguishes the
    speaker: white = the host, green = a client, red = a warning.
    """
    w, h = int(size[0]), int(size[1])
    ss = T.SS
    fill = fill or th.get("PAPER", T.PAPER)
    text_color = text_color or th.get("VOID", T.VOID)
    f = font or _font(th, "bold")

    tail_h = h * 0.30
    tail_w = h * 0.28
    body_h = int(h - tail_h)
    canvas = _blank((w, h))

    # the bubble body is built at full canvas height so the glow and the
    # tail share one coordinate space
    mask = Image.new("L", (w, h), 0)
    mask.paste(D.rounded_rect_mask((w, int(body_h)), h * 0.30, supersample=ss), (0, 0))
    body = Image.new("RGBA", (w, h), (*fill, 255))
    body.putalpha(mask)

    # tail
    td = ImageDraw.Draw(body)
    if tail == "down":
        x0, x1 = w * 0.18, w * 0.18 + tail_w
        td.polygon([(x0, body_h - 2), (x1, body_h - 2), (x0 + tail_w * 0.5, body_h + tail_h)],
                   fill=(*fill, 255))
    elif tail == "left":
        x0 = w * 0.06
        td.polygon([(x0, body_h * 0.35), (x0, body_h * 0.85), (x0 - tail_w, body_h * 0.60)],
                   fill=(*fill, 255))
    else:
        x0 = w - w * 0.24
        td.polygon([(x0, body_h * 0.35), (x0, body_h * 0.85), (x0 + tail_w, body_h * 0.60)],
                   fill=(*fill, 255))

    if text:
        d = ImageDraw.Draw(body)
        # shrink the type until the wrapped lines fit inside the bubble
        for _ in range(8):
            wrap = _wrap(d, text, f, int(w * max_width_ratio))
            line_h = (d.textbbox((0, 0), "Ag", font=f)[3]) * 1.32
            if len(wrap) * line_h <= body_h * 0.80:
                break
            try:
                nxt = max(8, int(f.size * 0.88))
                if nxt >= f.size:
                    break
                f = f.font_variant(size=nxt)
            except Exception:
                break
        y = body_h / 2 - (len(wrap) - 1) * line_h / 2
        for ln in wrap:
            D.draw_text(d, (w * 0.12, y), ln, f, fill=(*text_color, 255), anchor="lm")
            y += line_h

    if glow_strength > 0:
        g = D.glow(body, radius=int(h * 0.18), strength=glow_strength)
        canvas = D.screen_layer(body, g)
    return canvas


def _wrap(draw, text, font, max_w):
    words = text.split()
    if not words:
        return []
    lines, cur = [], words[0]
    for word in words[1:]:
        trial = cur + " " + word
        bb = draw.textbbox((0, 0), trial, font=font)
        if bb[2] - bb[0] <= max_w:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    lines.append(cur)
    return lines


# --------------------------------------------------------------------------
# 3. glass card with corner brackets
# --------------------------------------------------------------------------

def card(th, size, fill=None, alpha=235, border=True, brackets=True,
         radius=None, image=None, image_fit="cover", shadow=True,
         bracket_color=None, corner=0.16, border_color=None):
    """Dark navy glass panel, optionally showing an image, with the
    'designed frame' corner brackets the reference film uses to signal
    'this is a constructed frame, not a screenshot'.
    """
    w, h = int(size[0]), int(size[1])
    ss = T.SS
    radius = radius if radius is not None else h * 0.055
    fill = fill or th.get("NAVY", T.NAVY)
    canvas = _blank((w, h))

    mask = D.rounded_rect_mask((w, h), radius, supersample=ss)
    body = Image.new("RGBA", (w, h), (*fill, alpha))
    body.putalpha(mask)

    if image is not None:
        img = _fit(image.convert("RGB"), (w, h), image_fit)
        body.paste(img, (0, 0), mask)
        # slight darken so overlaid type stays readable
        shade = Image.new("RGBA", (w, h), (0, 0, 0, 70))
        body = D.overlay_alpha(body, shade)

    if shadow:
        sh = D.drop_shadow(body, offset=(0, int(h * 0.05)),
                           blur=int(h * 0.10), opacity=0.5)
        canvas = D.overlay_alpha(canvas, sh)
    canvas = D.overlay_alpha(canvas, body)

    d = ImageDraw.Draw(canvas)
    if border:
        bc = border_color or th.get("SKY", T.SKY)
        d.rounded_rectangle([1, 1, w - 2, h - 2], radius=radius,
                            outline=(*bc, 110), width=max(1, int(h * 0.006)))
    if brackets:
        cc = bracket_color or th.get("PAPER", T.PAPER)
        L = int(min(w, h) * corner)
        t = max(2, int(min(w, h) * 0.012))
        for (x, y, dx, dy) in ((0, 0, 1, 1), (w, 0, -1, 1), (0, h, 1, -1), (w, h, -1, -1)):
            d.line([(x, y), (x + dx * L, y)], fill=(*cc, 235), width=t)
            d.line([(x, y), (x, y + dy * L)], fill=(*cc, 235), width=t)
    return canvas.convert("RGBA")


# --------------------------------------------------------------------------
# 4. avatar badge
# --------------------------------------------------------------------------

def avatar(th, size, image=None, ring_color=None, ring_width=None, fallback_text=""):
    """Circular portrait with a coloured ring - the recurring 'people' motif."""
    w, h = int(size[0]), int(size[1])
    ss = T.SS
    ring_color = ring_color or th.get("GREEN", T.GREEN)
    rw = ring_width or int(h * 0.11)
    canvas = _blank((w, h))
    r = (w - rw) / 2
    d = ImageDraw.Draw(canvas)
    d.ellipse([rw / 2, rw / 2, w - rw / 2, h - rw / 2], fill=(*ring_color, 235))

    inner = D.circle_mask((w, h), r, center=(w / 2, h / 2), supersample=ss)
    if image is not None:
        img = _fit(image.convert("RGB"), (int(r * 2), int(r * 2)), "cover")
        plate = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        plate.paste(img, (int((w - r * 2) / 2), int((h - r * 2) / 2)),
                    D.circle_mask((int(r * 2), int(r * 2)), r, supersample=ss))
        canvas = D.overlay_alpha(canvas, plate)
    else:
        plate = Image.new("RGBA", (w, h), (*th.get("NAVY", T.NAVY), 255))
        plate.putalpha(inner)
        canvas = D.overlay_alpha(canvas, plate)
        if fallback_text:
            dd = ImageDraw.Draw(canvas)
            f = _font(th, "bold")
            D.draw_text(dd, (w / 2, h / 2), fallback_text, f,
                        fill=(*th.get("PAPER", T.PAPER), 255), anchor="mm")
    return canvas.convert("RGBA")


# --------------------------------------------------------------------------
# 5. label pill with pointer
# --------------------------------------------------------------------------

def label_pill(th, size, text="", gradient="azure_blue", pointer="down",
               font=None, glow_strength=0.5, text_color=None):
    """A small pill that points at the thing it names."""
    w, h = int(size[0]), int(size[1])
    ss = T.SS
    f = font or _font(th, "bold")
    text_color = text_color or th.get("PAPER", T.PAPER)
    body_h = int(h * 0.74)
    canvas = _blank((w, h))

    mask = Image.new("L", (w, h), 0)
    mask.paste(D.rounded_rect_mask((w, int(body_h)), body_h / 2, supersample=ss), (0, 0))
    body = D.fill_gradient(mask, _grad_stops(th, gradient), angle=0)
    d = ImageDraw.Draw(body)
    D.draw_text(d, (w / 2, body_h / 2), text, f, fill=(*text_color, 255), anchor="mm")

    if pointer == "down":
        cx = w / 2
        d.polygon([(cx - h * 0.11, body_h - 2), (cx + h * 0.11, body_h - 2),
                   (cx, body_h + h * 0.24)], fill=(*_grad_stops(th, gradient)[0], 255))
    if glow_strength > 0:
        g = D.glow(body, radius=int(h * 0.3), strength=glow_strength)
        canvas = D.screen_layer(body, g)
    return canvas


# --------------------------------------------------------------------------
# 6. cursor triangle
# --------------------------------------------------------------------------

def cursor(th, size, color=None, tilt=-12):
    """The purple triangular pointer that 'clicks' things on screen."""
    w, h = int(size[0]), int(size[1])
    color = color or th.get("PURPLE_CURSOR", T.PURPLE_CURSOR)
    canvas = _blank((w, h))
    d = ImageDraw.Draw(canvas)
    pts = [(w * 0.06, h * 0.04), (w * 0.92, h * 0.52), (w * 0.48, h * 0.60),
           (w * 0.60, h * 0.96)]
    a = math.radians(tilt)
    cx, cy = w / 2, h / 2
    pts = [(cx + (px - cx) * math.cos(a) - (py - cy) * math.sin(a),
            cy + (px - cx) * math.sin(a) + (py - cy) * math.cos(a)) for px, py in pts]
    d.polygon(pts, fill=(*color, 245))
    d.polygon([(px, py) for px, py in pts], outline=(255, 255, 255, 170),
              width=max(1, int(w * 0.012)))
    g = D.glow(canvas, radius=int(w * 0.12), strength=0.5)
    return D.screen_layer(canvas, g)


# --------------------------------------------------------------------------
# 7. monitor on a stand
# --------------------------------------------------------------------------

def monitor(th, size, screen_image=None, stand=True, bezel=None, radius=None):
    """A flat-panel monitor on a thin stand - the default 'show a UI' frame."""
    w, h = int(size[0]), int(size[1])
    ss = T.SS
    bezel = bezel if bezel is not None else th.get("VOID", T.VOID)
    radius = radius if radius is not None else w * 0.018
    stand_h = h * 0.30 if stand else 0
    scr_h = int(h - stand_h)
    canvas = _blank((w, h))

    body = D.rounded_rect_mask((w, scr_h), radius, supersample=ss)
    panel = Image.new("RGBA", (w, scr_h), (*bezel, 255))
    panel.putalpha(body)
    canvas = D.overlay_alpha(canvas, panel)

    if screen_image is not None:
        inset = int(w * 0.012)
        sw, sh = w - inset * 2, scr_h - inset * 2
        img = _fit(screen_image.convert("RGB"), (sw, sh), "contain")
        plate = Image.new("RGBA", (w, scr_h), (0, 0, 0, 0))
        plate.paste(img, (inset, inset))
        canvas = D.overlay_alpha(canvas, plate)

    d = ImageDraw.Draw(canvas)
    if stand:
        cx = w / 2
        d.rectangle([cx - w * 0.012, scr_h, cx + w * 0.012, h * 0.88],
                    fill=(*th.get("STEEL", T.STEEL), 255))
        d.ellipse([cx - w * 0.10, h * 0.86, cx + w * 0.10, h * 0.97],
                  fill=(*th.get("STEEL", T.STEEL), 255))
    return canvas.convert("RGBA")


# --------------------------------------------------------------------------
# 8. circuit plate (background)
# --------------------------------------------------------------------------

def circuit(th, size, seed=11, trace_color=None, chip=True):
    """A blue circuit-board plate. Used as the 'technology' background."""
    w, h = int(size[0]), int(size[1])
    rng = np.random.default_rng(seed)
    trace_color = trace_color or th.get("SKY", T.SKY)
    canvas = _blank((w, h))
    d = ImageDraw.Draw(canvas)
    lw = max(2, int(min(w, h) * 0.006))
    for _ in range(26):
        x = rng.uniform(0, w)
        y = rng.uniform(0, h)
        pts = [(x, y)]
        for _ in range(rng.integers(2, 5)):
            if rng.random() < 0.5:
                x += rng.uniform(-0.28, 0.28) * w
            else:
                y += rng.uniform(-0.28, 0.28) * h
            pts.append((x, y))
        d.line(pts, fill=(*trace_color, 46), width=lw, joint="curve")
        d.ellipse([pts[-1][0] - lw, pts[-1][1] - lw,
                   pts[-1][0] + lw, pts[-1][1] + lw], fill=(*trace_color, 80))
    if chip:
        cw, ch = w * 0.16, h * 0.10
        cx, cy = w * 0.5, h * 0.5
        d.rounded_rectangle([cx - cw / 2, cy - ch / 2, cx + cw / 2, cy + ch / 2],
                            radius=cw * 0.1, fill=(*th.get("VOID", T.VOID), 255))
        d.rounded_rectangle([cx - cw / 2, cy - ch / 2, cx + cw / 2, cy + ch / 2],
                            radius=cw * 0.1, outline=(*trace_color, 120), width=lw)
    return canvas


# --------------------------------------------------------------------------
# 9. hero numeral with radial burst
# --------------------------------------------------------------------------

def numeral(th, size, text="22", gradient="azure_blue", rays=True,
            ray_count=18, font=None, shadow=True, letter_spacing=0.0):
    """The big number with radiating light rays behind it."""
    w, h = int(size[0]), int(size[1])
    canvas = _blank((w, h))
    f = font or _font(th, "black")
    if rays:
        rl = _blank((w, h))
        d = ImageDraw.Draw(rl)
        cx, cy = w / 2, h / 2
        for i in range(ray_count):
            a = (i / ray_count) * 2 * math.pi
            r0 = min(w, h) * 0.16
            r1 = min(w, h) * 0.62
            wid = math.radians(360 / ray_count * 0.32)
            p = [(cx + math.cos(a - wid) * r0, cy + math.sin(a - wid) * r0),
                 (cx + math.cos(a - wid * 0.45) * r1, cy + math.sin(a - wid * 0.45) * r1),
                 (cx + math.cos(a + wid * 0.45) * r1, cy + math.sin(a + wid * 0.45) * r1),
                 (cx + math.cos(a + wid) * r0, cy + math.sin(a + wid) * r0)]
            d.polygon(p, fill=(255, 255, 255, 120))
        rl = rl.filter(ImageFilter.GaussianBlur(min(w, h) * 0.012))
        canvas = D.screen_layer(canvas, rl)

    if f is None:
        return canvas
    bbox_layer = D.gradient_text((w, h), text, f, _grad_stops(th, gradient),
                                 angle=0, letter_spacing=letter_spacing)
    bb = bbox_layer.getbbox()
    if bb:
        txt = bbox_layer.crop(bb)
        # centre the numerals in the component's own box
        ox = max(0, (w - txt.width) // 2)
        oy = max(0, (h - txt.height) // 2)
        if shadow:
            sh = Image.new("RGBA", (w, h), (0, 0, 0, 0))
            sh.paste(Image.new("RGBA", txt.size, (*th.get("VOID", T.VOID), 215)),
                     (ox + int(w * 0.012), oy + int(h * 0.022)), txt.split()[-1])
            canvas = D.overlay_alpha(canvas, sh)
        placed = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        placed.paste(txt, (ox, oy), txt)
        canvas = D.overlay_alpha(canvas, placed)
    return canvas.convert("RGBA")


# --------------------------------------------------------------------------
# 10. sparkles
# --------------------------------------------------------------------------

def sparkles(th, size, count=7, color=None, seed=5):
    """Four-point stars that pop around a focal element."""
    w, h = int(size[0]), int(size[1])
    color = color or th.get("PAPER", T.PAPER)
    rng = np.random.default_rng(seed)
    canvas = _blank((w, h))
    d = ImageDraw.Draw(canvas)
    for _ in range(count):
        cx, cy = rng.uniform(0.1, 0.9) * w, rng.uniform(0.1, 0.9) * h
        r = rng.uniform(0.02, 0.055) * min(w, h)
        a = int(rng.uniform(120, 255))
        d.polygon([(cx, cy - r), (cx + r * 0.26, cy - r * 0.26), (cx + r, cy),
                   (cx + r * 0.26, cy + r * 0.26), (cx, cy + r),
                   (cx - r * 0.26, cy + r * 0.26), (cx - r, cy),
                   (cx - r * 0.26, cy - r * 0.26)], fill=(*color, a))
    g = D.glow(canvas, radius=int(min(w, h) * 0.04), strength=0.7)
    return D.screen_layer(canvas, g)


# --------------------------------------------------------------------------
# 11. rising line graph
# --------------------------------------------------------------------------

def line_graph(th, size, values=None, color=None, width=None, arrow=True,
               fill_under=False):
    """A rising graph with an arrow head - the 'growth / earnings' motif."""
    w, h = int(size[0]), int(size[1])
    color = color or th.get("GREEN", T.GREEN)
    lw = width or max(3, int(min(w, h) * 0.035))
    values = values or [0.1, 0.18, 0.16, 0.34, 0.46, 0.55, 0.78, 1.0]
    canvas = _blank((w, h))
    d = ImageDraw.Draw(canvas)
    pts = [(w * 0.04 + (w * 0.92) * i / (len(values) - 1), h * 0.92 - h * 0.86 * v)
           for i, v in enumerate(values)]
    if fill_under:
        poly = pts + [(pts[-1][0], h), (pts[0][0], h)]
        d.polygon(poly, fill=(*color, 40))
    d.line(pts, fill=(*color, 255), width=lw, joint="curve")
    if arrow:
        x, y = pts[-1]
        s = lw * 2.4
        d.polygon([(x + s, y), (x - s * 0.2, y - s * 0.75), (x - s * 0.2, y + s * 0.75)],
                  fill=(*color, 255))
    g = D.glow(canvas, radius=int(min(w, h) * 0.06), strength=0.55)
    return D.screen_layer(canvas, g)


# --------------------------------------------------------------------------
# 12. app icon tile (3D-ish)
# --------------------------------------------------------------------------

def icon_tile(th, size, glyph="", gradient=None, bg=None, radius=None,
              font=None, shadow=True):
    """A dark rounded-square app icon with a glyph - the 3D icon stack."""
    w, h = int(size[0]), int(size[1])
    ss = T.SS
    radius = radius if radius is not None else w * 0.22
    canvas = _blank((w, h))
    mask = D.rounded_rect_mask((w, h), radius, supersample=ss)
    body = Image.new("RGBA", (w, h), (*(bg or th.get("VOID", T.VOID)), 255))
    body.putalpha(mask)
    if shadow:
        canvas = D.overlay_alpha(canvas, D.drop_shadow(
            body, offset=(0, int(h * 0.10)), blur=int(h * 0.16), opacity=0.55))
    canvas = D.overlay_alpha(canvas, body)
    if glyph:
        d = ImageDraw.Draw(canvas)
        f = font or _font(th, "black")
        D.draw_text(d, (w / 2, h / 2), glyph, f, fill=(255, 255, 255, 255), anchor="mm")
    # top edge specular so it reads as a physical object
    spec = _blank((w, h))
    sd = ImageDraw.Draw(spec)
    sd.rounded_rectangle([0, 0, w, h * 0.45], radius=radius, fill=(255, 255, 255, 34))
    spec = spec.filter(ImageFilter.GaussianBlur(w * 0.05))
    canvas = D.screen_layer(canvas, spec)
    return canvas


# --------------------------------------------------------------------------
# 13. phone mockup
# --------------------------------------------------------------------------

def phone(th, size, screen_image=None, radius=None, glow_color=None):
    """A phone mockup - the vehicle for balances, earnings and dashboards."""
    w, h = int(size[0]), int(size[1])
    ss = T.SS
    radius = radius if radius is not None else w * 0.11
    canvas = _blank((w, h))
    body = D.rounded_rect_mask((w, h), radius, supersample=ss)
    plate = Image.new("RGBA", (w, h), (*th.get("VOID", T.VOID), 255))
    plate.putalpha(body)
    canvas = D.overlay_alpha(canvas, D.drop_shadow(
        plate, offset=(0, int(h * 0.03)), blur=int(h * 0.08), opacity=0.6))
    canvas = D.overlay_alpha(canvas, plate)

    inset = int(w * 0.028)
    sw, sh = w - inset * 2, h - inset * 2
    if screen_image is not None:
        img = _fit(screen_image.convert("RGB"), (sw, sh), "contain")
        inner = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        inner.paste(img, (inset, inset))
        canvas = D.overlay_alpha(canvas, inner)
    d = ImageDraw.Draw(canvas)
    nw = int(w * 0.30)
    d.rounded_rectangle([w / 2 - nw / 2, inset * 0.55, w / 2 + nw / 2, inset * 1.5],
                        radius=inset * 0.5, fill=(*th.get("VOID", T.VOID), 255))
    g = D.glow(canvas, radius=int(w * 0.08),
               strength=0.7, color=glow_color or th.get("SKY", T.SKY))
    return D.screen_layer(canvas, g)


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------

def _fit(img, size, mode="cover"):
    """Scale an image into `size`. cover = fill & crop, contain = fit inside."""
    tw, th = size
    iw, ih = img.size
    if iw == 0 or ih == 0:
        return Image.new("RGB", size, (0, 0, 0))
    s = max(tw / iw, th / ih) if mode == "cover" else min(tw / iw, th / ih)
    nw, nh = max(1, int(iw * s)), max(1, int(ih * s))
    img = img.resize((nw, nh), Image.LANCZOS)
    if mode == "cover":
        x = (nw - tw) // 2
        y = (nh - th) // 2
        return img.crop((x, y, x + tw, y + th))
    out = Image.new("RGB", size, (0, 0, 0))
    out.paste(img, ((tw - nw) // 2, (th - nh) // 2))
    return out
