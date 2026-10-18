"""Layer rendering + the animation system.

A storyboard shot is a stack of layers. Each layer renders itself for a
given *local* time (seconds since the shot started) and is composited in
order. Entrances and exits are declarative so a storyboard can be edited
without touching code.

The animation vocabulary here mirrors the motion grammar measured in the
reference film: entrances decelerate hard, exits accelerate away, and every
incoming element overshoots slightly and settles.
"""
import math
import os
import subprocess

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from . import theme as T
from . import draw as D
from . import components as C
from .easing import get as ease


# --------------------------------------------------------------------------
# animation
# --------------------------------------------------------------------------

class Transform:
    """The result of evaluating a layer's animation at time t."""

    __slots__ = ("dx", "dy", "scale", "rot", "alpha", "mask", "blur")

    def __init__(self):
        self.dx = 0.0
        self.dy = 0.0
        self.scale = 1.0
        self.rot = 0.0
        self.alpha = 1.0
        self.mask = None      # optional PIL "L" mask applied after rendering
        self.blur = 0.0


def _anim_progress(t, spec, dur_total):
    """0 before the animation, 1 after it, eased in between."""
    delay = spec.get("delay", 0.0)
    dur = max(1e-4, spec.get("dur", 0.35))
    if t < delay:
        return 0.0
    p = min(1.0, (t - delay) / dur)
    return ease(spec.get("ease", "ease_out"))(p)


def apply_anim(tf, t, spec, size, direction="in"):
    """Mutate a Transform according to one animation spec.

    `direction` is "in" for an entrance and "out" for an exit. The two use
    the same formulas with the progress mirrored: for an exit, progress 0
    means "still fully present" and progress 1 means "gone". Without the
    mirror an exit would hide the element from the moment the shot
    started."""
    if not spec:
        return
    kind = spec.get("type", "fade")
    p = _anim_progress(t, spec, size)
    e = p if direction == "in" else (1.0 - p)
    if kind == "fade":
        tf.alpha *= e
    elif kind == "slide":
        frm = spec.get("from", [-0.2, 0.0])
        tf.dx += frm[0] * (1 - e) * size[0]
        tf.dy += frm[1] * (1 - e) * size[1]
    elif kind == "rise":
        tf.dy += spec.get("from", 0.12) * (1 - e) * size[1]
        tf.alpha *= e
    elif kind == "pop":
        s = spec.get("from", 0.6)
        tf.scale *= s + (1 - s) * e
        tf.alpha *= min(1.0, e * 1.6)
    elif kind == "scale":
        s = spec.get("from", 0.8)
        tf.scale *= s + (1 - s) * e
    elif kind == "spin":
        tf.rot += spec.get("from", 90) * (1 - e)
        tf.alpha *= e
    elif kind == "whip":
        # fast diagonal pass across frame
        frm = spec.get("from", [-1.4, 0.35])
        tf.dx += frm[0] * (1 - e) * size[0]
        tf.dy += frm[1] * (1 - e) * size[1]
        tf.alpha *= e
    elif kind == "wipe_iris":
        r = e * 1.5
        w, h = size
        m = Image.new("L", (w, h), 0)
        d = ImageDraw.Draw(m)
        cx, cy = w * 0.5, h * 0.5
        rad = math.hypot(w, h) * 0.75 * r
        d.ellipse([cx - rad, cy - rad, cx + rad, cy + rad], fill=255)
        tf.mask = m if tf.mask is None else ImageChops_lighter(tf.mask, m)
    elif kind == "wipe_bars":
        w, h = size
        m = Image.new("L", (w, h), 0)
        d = ImageDraw.Draw(m)
        n = spec.get("bars", 12)
        bw = w / n
        for i in range(n):
            frac = (i + 1) / n
            if frac <= e:
                d.rectangle([i * bw, 0, (i + 1) * bw, h], fill=255)
        tf.mask = m if tf.mask is None else ImageChops_lighter(tf.mask, m)
    elif kind == "wipe_diagonal":
        w, h = size
        m = Image.new("L", (w, h), 0)
        d = ImageDraw.Draw(m)
        band = spec.get("band", 0.35)
        off = (1 - e) * (w + h)
        d.polygon([(off - h, 0), (off, 0), (off - h + w, h), (off - h, h)], fill=255)
        m2 = m.rotate(-18, fillcolor=0, resample=Image.BILINEAR)
        tf.mask = m2 if tf.mask is None else ImageChops_lighter(tf.mask, m2)
    elif kind == "type_on":
        w, h = size
        m = Image.new("L", (w, h), 0)
        d = ImageDraw.Draw(m)
        cut = e * w * 1.2
        d.rectangle([0, 0, cut, h], fill=255)
        tf.mask = m if tf.mask is None else ImageChops_lighter(tf.mask, m)
    elif kind == "blur_in":
        tf.blur += spec.get("from", 14) * (1 - e)
        tf.alpha *= e


def ImageChops_lighter(a, b):
    from PIL import ImageChops
    return ImageChops.lighter(a, b)


def layer_transform(layer, t, size):
    tf = Transform()
    apply_anim(tf, t, layer.get("in"), size)
    out = layer.get("out")
    if out:
        # exits are relative to the END of the shot
        end = layer.get("_shot_duration", 0)
        apply_anim(tf, t - (end - out.get("dur", 0.3) - out.get("delay", 0)),
                   out, size, direction="out")
    return tf


# --------------------------------------------------------------------------
# background
# --------------------------------------------------------------------------

def render_bg(th, layer, t, size):
    kind = layer.get("style", "gradient")
    if kind == "solid":
        img = Image.new("RGB", size, T.parse_color(layer.get("color"), th.get("VOID", T.VOID)))
    elif kind == "radial":
        img = D.radial_gradient(size, T.parse_color(layer.get("inner"), th.get("NAVY", T.NAVY)),
                                T.parse_color(layer.get("outer"), th.get("VOID", T.VOID)),
                                center=tuple(layer.get("center", (0.5, 0.5))),
                                radius=layer.get("radius", 0.8)).convert("RGB")
    elif kind == "bokeh":
        base = Image.new("RGB", size, T.parse_color(layer.get("base"), th.get("VOID", T.VOID)))
        cols = [T.parse_color(th.get(k, T.VOID)) for k in layer.get(
            "colors", ["NAVY", "ELECTRIC", "SKY"])]
        ov = D.bokeh_background(size, cols, count=layer.get("count", 64),
                                seed=layer.get("seed", 7),
                                alpha=layer.get("alpha", 32),
                                max_r=layer.get("max_r", 0.13))
        img = D.overlay_alpha(base, ov)
    elif kind == "circuit":
        base = Image.new("RGB", size, T.parse_color(layer.get("base"), th.get("NAVY", T.NAVY)))
        img = D.overlay_alpha(base, C.circuit(th, size, seed=layer.get("seed", 11)))
    elif kind == "gradient":
        stops = D.linear_gradient(size, T.parse_stops(layer.get("stops")) or
                                  [th.get("NAVY", T.NAVY), th.get("VOID", T.VOID)], 45.0)
        img = stops.convert("RGB")
    else:
        img = Image.new("RGB", size, T.parse_color(th.get("VOID"), T.VOID))
    if layer.get("vignette", True):
        img = D.vignette(img, strength=layer.get("vignette_strength", 0.5))
    return img


# --------------------------------------------------------------------------
# text
# --------------------------------------------------------------------------

def render_text(th, layer, t, size):
    from . import fonts as F
    f = layer.get("_font")
    if f is None:
        path = layer.get("_font_path")
        if not path:
            return Image.new("RGBA", size, (0, 0, 0, 0))
        scale = layer.get("size", T.TYPE_SCALE["headline"])
        f = F.make_font(path, max(8, int(size[1] * scale)),
                        layer.get("_font_weight", 400))
    px = max(8, int(size[1] * layer.get("size", T.TYPE_SCALE["headline"])))

    # auto-fit: a headline that overruns its slot collides with whatever is
    # next to it, which is the single most common layout failure
    max_w = layer.get("max_width")
    if max_w and layer.get("_font_path"):
        limit = float(max_w) * size[0]
        probe = ImageDraw.Draw(Image.new("RGB", (1, 1)))
        widest = 0
        for ln in (layer.get("lines") or [layer.get("text", "")]):
            bb = probe.textbbox((0, 0), ln, font=f)
            widest = max(widest, bb[2] - bb[0])
        if widest > limit and widest > 0:
            scale = limit / widest
            px = max(8, int(px * scale))
            f = F.make_font(layer["_font_path"], px, layer.get("_font_weight", 400))

    color = T.parse_color(layer.get("color"), th.get("PAPER", T.PAPER))
    layer_img = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer_img)
    x = layer.get("x", 0.5) * size[0]
    y = layer.get("y", 0.5) * size[1]
    anchor = layer.get("anchor", "mm")
    lines = layer.get("lines") or [layer.get("text", "")]
    ls = layer.get("line_spacing", 1.22)
    if len(lines) > 1:
        lh = px * ls
        y0 = y - (len(lines) - 1) * lh / 2
        for i, ln in enumerate(lines):
            va = "m" if anchor[0] in "lm" else anchor[1]
            D.draw_text(d, (x, y0 + i * lh), ln, f, fill=(*color, 255),
                        anchor=anchor[0] + va,
                        letter_spacing=layer.get("letter_spacing", 0.0))
    else:
        D.draw_text(d, (x, y), lines[0], f, fill=(*color, 255), anchor=anchor,
                    letter_spacing=layer.get("letter_spacing", 0.0))

    if layer.get("stroke"):
        sw = max(1, int(px * 0.012))
        sc = T.parse_color(layer.get("stroke_color"), (0, 0, 0))
        sl = Image.new("RGBA", size, (0, 0, 0, 0))
        sd = ImageDraw.Draw(sl)
        D.draw_text(sd, (x, y), lines[0], f, fill=(*sc, 255), anchor=anchor,
                    stroke_width=sw, stroke_fill=(*sc, 255))
        layer_img = D.overlay_alpha(sl, layer_img)
    if layer.get("shadow", True):
        sh = D.drop_shadow(layer_img, offset=(0, int(px * 0.05)),
                           blur=int(px * 0.12), opacity=0.5)
        # the shadow sits BEHIND the type - compositing it on top would
        # darken the glyphs themselves
        layer_img = D.overlay_alpha(sh, layer_img)
    if layer.get("underline"):
        uy = y + px * 0.62
        uw = layer.get("underline_w", 0.3) * size[0]
        d.rectangle([x - uw / 2, uy, x + uw / 2, uy + max(2, int(px * 0.05))],
                    fill=(*color, 255))
    return layer_img


# --------------------------------------------------------------------------
# media layers
# --------------------------------------------------------------------------

def render_image(th, layer, t, size):
    path = layer.get("src")
    img = _load_image(path)
    if img is None:
        ph = Image.new("RGBA", size, (*th.get("CHARCOAL", T.CHARCOAL), 255))
        d = ImageDraw.Draw(ph)
        f = C._font(th, "bold")
        D.draw_text(d, (size[0] / 2, size[1] / 2), "MISSING ASSET", f,
                    fill=(*th.get("PAPER", T.PAPER), 255), anchor="mm")
        return ph
    w = int(size[0] * layer.get("w", 1.0))
    h = int(size[1] * layer.get("h", 1.0))
    fit = layer.get("fit", "cover")
    img = C._fit(img.convert("RGBA"), (w, h), fit)
    canvas = Image.new("RGBA", size, (0, 0, 0, 0))
    x = int(layer.get("x", 0.5) * size[0] - w / 2)
    y = int(layer.get("y", 0.5) * size[1] - h / 2)
    if layer.get("radius"):
        m = D.rounded_rect_mask((w, h), layer["radius"], supersample=T.SS)
        img.putalpha(m)
    canvas.paste(img, (x, y), img)
    if layer.get("shadow", True):
        sh = D.drop_shadow(img, offset=(0, int(h * 0.04)), blur=int(h * 0.08), opacity=0.5)
        canvas = D.overlay_alpha(canvas, sh)
    return canvas


_FRAME_CACHE = {}
_FRAME_CACHE_ORDER = []
_FRAME_CACHE_MAX = 6


def _load_frame(path):
    """Read one extracted frame, with a tiny LRU cache.

    Video frames live on disk, not in memory - a 3-second 1080p clip is
    560 MB if you keep it all. This reads one frame at a time and keeps
    a handful around so overlapping layers do not thrash the disk.
    """
    if path in _FRAME_CACHE:
        return _FRAME_CACHE[path]
    img = Image.open(path).convert("RGB")
    _FRAME_CACHE[path] = img
    _FRAME_CACHE_ORDER.append(path)
    while len(_FRAME_CACHE_ORDER) > _FRAME_CACHE_MAX:
        old = _FRAME_CACHE_ORDER.pop(0)
        _FRAME_CACHE.pop(old, None)
    return img


def render_video(th, layer, t, size):
    """A clip from the source talking-head video.

    `src_in` is the offset into the source file; the layer plays from there
    for the duration of the shot. The renderer pre-extracts the frames so
    this stays fast, and reads them back one at a time.
    """
    files = layer.get("_frame_files")
    fdir = layer.get("_frame_dir")
    if not files:
        return Image.new("RGBA", size, (0, 0, 0, 0))
    idx = int(t * layer.get("fps", 30)) + layer.get("_frame_offset", 0)
    if idx < 0:
        idx = 0
    if idx >= len(files):
        idx = len(files) - 1
    img = _load_frame(os.path.join(fdir, files[idx]))
    w = int(size[0] * layer.get("w", 1.0))
    h = int(size[1] * layer.get("h", 1.0))
    img = C._fit(img.convert("RGBA"), (w, h), layer.get("fit", "cover"))
    canvas = Image.new("RGBA", size, (0, 0, 0, 0))
    x = int(layer.get("x", 0.5) * size[0] - w / 2)
    y = int(layer.get("y", 0.5) * size[1] - h / 2)
    if layer.get("radius"):
        m = D.rounded_rect_mask((w, h), layer["radius"], supersample=T.SS)
        img.putalpha(m)
    canvas.paste(img, (x, y), img)
    return canvas


# --------------------------------------------------------------------------
# component layers
# --------------------------------------------------------------------------

def _component_size(layer, size):
    w = int(size[0] * layer.get("w", 0.4))
    h = int(size[1] * layer.get("h", 0.10))
    return max(8, w), max(8, h)


def _place(canvas, layer, size, sub, ss=1):
    """Paste a sub-image onto a fresh full-canvas layer at the layer's x/y
    (centre-anchored). The canvas is always empty here, so the sub's own
    alpha is copied directly rather than used as a paste mask (which would
    multiply the alpha by itself and dim every glow)."""
    if sub.mode != "RGBA":
        sub = sub.convert("RGBA")
    w, h = sub.size
    x = int(layer.get("x", 0.5) * size[0] - w / 2)
    y = int(layer.get("y", 0.5) * size[1] - h / 2)
    canvas.paste(sub, (x, y))
    return canvas


def render_pill(th, layer, t, size):
    w, h = _component_size(layer, size)
    sub = C.pill(th, (w, h), text=layer.get("text", ""),
                 gradient=layer.get("gradient", "azure_blue"),
                 bullet=layer.get("bullet", True),
                 glow_strength=layer.get("glow", 1.0),
                 text_color=T.parse_color(layer["color"]) if layer.get("color") else None,
                 letter_spacing=layer.get("letter_spacing", 1.0),
                 font=layer.get("_font"))
    return _place(Image.new("RGBA", size, (0, 0, 0, 0)), layer, size, sub)


def render_bubble(th, layer, t, size):
    w, h = _component_size(layer, size)
    sub = C.bubble(th, (w, h), text=layer.get("text", ""),
                   tail=layer.get("tail", "left"),
                   fill=T.parse_color(layer["fill"]) if layer.get("fill") else None,
                   text_color=T.parse_color(layer["text_color"]) if layer.get("text_color") else None,
                   glow_strength=layer.get("glow", 0.35),
                   font=layer.get("_font"))
    return _place(Image.new("RGBA", size, (0, 0, 0, 0)), layer, size, sub)


def render_card(th, layer, t, size):
    w, h = _component_size(layer, size)
    img = layer.get("_image")
    sub = C.card(th, (w, h), fill=T.parse_color(layer["fill"]) if layer.get("fill") else None,
                 alpha=layer.get("alpha", 235),
                 border=layer.get("border", True),
                 brackets=layer.get("brackets", True),
                 image=img, image_fit=layer.get("fit", "cover"))
    return _place(Image.new("RGBA", size, (0, 0, 0, 0)), layer, size, sub)


def render_avatar(th, layer, t, size):
    w, h = _component_size(layer, size)
    sub = C.avatar(th, (w, h), image=layer.get("_image"),
                   ring_color=T.parse_color(layer["ring"]) if layer.get("ring") else None)
    return _place(Image.new("RGBA", size, (0, 0, 0, 0)), layer, size, sub)


def render_label(th, layer, t, size):
    w, h = _component_size(layer, size)
    sub = C.label_pill(th, (w, h), text=layer.get("text", ""),
                       gradient=layer.get("gradient", "azure_blue"),
                       pointer=layer.get("pointer", "down"),
                       font=layer.get("_font"),
                       glow_strength=layer.get("glow", 0.5))
    return _place(Image.new("RGBA", size, (0, 0, 0, 0)), layer, size, sub)


def render_cursor(th, layer, t, size):
    w, h = _component_size(layer, size)
    sub = C.cursor(th, (w, h))
    return _place(Image.new("RGBA", size, (0, 0, 0, 0)), layer, size, sub)


def render_monitor(th, layer, t, size):
    w, h = _component_size(layer, size)
    sub = C.monitor(th, (w, h), screen_image=layer.get("_image"),
                    stand=layer.get("stand", True))
    return _place(Image.new("RGBA", size, (0, 0, 0, 0)), layer, size, sub)


def render_numeral(th, layer, t, size):
    w, h = _component_size(layer, size)
    sub = C.numeral(th, (w, h), text=layer.get("text", "22"),
                    gradient=layer.get("gradient", "azure_blue"),
                    rays=layer.get("rays", True),
                    font=layer.get("_font"))
    return _place(Image.new("RGBA", size, (0, 0, 0, 0)), layer, size, sub)


def render_sparkles(th, layer, t, size):
    w, h = _component_size(layer, size)
    sub = C.sparkles(th, (w, h), count=layer.get("count", 7),
                     seed=layer.get("seed", 5))
    return _place(Image.new("RGBA", size, (0, 0, 0, 0)), layer, size, sub)


def render_graph(th, layer, t, size):
    w, h = _component_size(layer, size)
    sub = C.line_graph(th, (w, h), values=layer.get("values"),
                       color=T.parse_color(layer["color"]) if layer.get("color") else None)
    return _place(Image.new("RGBA", size, (0, 0, 0, 0)), layer, size, sub)


def render_icon(th, layer, t, size):
    w, h = _component_size(layer, size)
    sub = C.icon_tile(th, (w, h), glyph=layer.get("glyph", ""),
                      font=layer.get("_font"))
    return _place(Image.new("RGBA", size, (0, 0, 0, 0)), layer, size, sub)


def render_phone(th, layer, t, size):
    w, h = _component_size(layer, size)
    sub = C.phone(th, (w, h), screen_image=layer.get("_image"))
    return _place(Image.new("RGBA", size, (0, 0, 0, 0)), layer, size, sub)


def render_circuit(th, layer, t, size):
    return C.circuit(th, size, seed=layer.get("seed", 11))


def render_grain(th, layer, t, size):
    return Image.new("RGBA", size, (0, 0, 0, 0))


RENDERERS = {
    "bg": render_bg,
    "text": render_text,
    "image": render_image,
    "video": render_video,
    "pill": render_pill,
    "bubble": render_bubble,
    "card": render_card,
    "avatar": render_avatar,
    "label": render_label,
    "cursor": render_cursor,
    "monitor": render_monitor,
    "numeral": render_numeral,
    "sparkles": render_sparkles,
    "graph": render_graph,
    "icon": render_icon,
    "phone": render_phone,
    "circuit": render_circuit,
}


# --------------------------------------------------------------------------
# image cache
# --------------------------------------------------------------------------

_IMG_CACHE = {}


def _load_image(path):
    if not path:
        return None
    key = os.path.abspath(path)
    if key not in _IMG_CACHE:
        if not os.path.exists(key):
            _IMG_CACHE[key] = None
        else:
            _IMG_CACHE[key] = Image.open(key).convert("RGBA")
    return _IMG_CACHE[key]
