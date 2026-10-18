"""Low-level drawing primitives.

These are the pixels-level tools the component layer is built from. They are
deliberately numpy/PIL only (no cairo, no GPU) so the renderer runs anywhere
Python does.

Two rules make flat vector graphics look expensive, and both live here:

1. **Everything is drawn supersampled.** Components render at SS x resolution
   and are downscaled with LANCZOS. This is what gives clean curves without
   a GPU.
2. **Light is additive, not painted.** Glows are rendered as a blurred alpha
   mask and *screen*-blended onto the backdrop, so a glow adds light instead
   of replacing what is under it. The same for bloom.
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops

from . import theme as T


# --------------------------------------------------------------------------
# blending
# --------------------------------------------------------------------------

def screen(base, add):
    """Screen blend: 1-(1-a)(1-b). Used for every additive light.

    Returns RGBA. A transparent base must stay transparent - an additive
    glow adds light to what is underneath, it does not replace it, and
    losing the alpha here turns every glow into an opaque black-and-white
    plate that covers the frame."""
    b = np.asarray(base.convert("RGBA"), dtype=np.float32) / 255.0
    a = np.asarray(add.convert("RGBA"), dtype=np.float32) / 255.0
    ba, aa = b[..., 3:4], a[..., 3:4]
    br, ar = b[..., :3], a[..., :3]
    s = 1.0 - (1.0 - br) * (1.0 - ar)
    out_rgb = br * (1 - aa) + s * aa
    out_a = ba + aa * (1 - ba)
    out = np.concatenate([out_rgb, out_a], axis=2)
    return Image.fromarray(np.clip(out * 255, 0, 255).astype(np.uint8), "RGBA")


def screen_layer(base, add):
    """Screen-blend an RGBA layer onto a base, honouring alpha."""
    if add.mode != "RGBA":
        add = add.convert("RGBA")
    return screen(base, add)


def overlay_alpha(base, layer):
    """Alpha-composite an RGBA layer onto a base (normal blend).

    Returns RGBA. Keeping the alpha channel is not optional: a text layer
    is mostly transparent, and if this function returns RGB the layer
    becomes an opaque black plate that covers everything underneath it.

    Tolerates a layer that is a different size or mode: it is converted and
    pasted at the origin rather than raising, because several components
    build a partial-height body and then place it inside a full-frame
    canvas."""
    b = base.convert("RGBA")
    if layer.mode != "RGBA":
        layer = layer.convert("RGBA")
    if layer.size != b.size:
        canvas = Image.new("RGBA", b.size, (0, 0, 0, 0))
        canvas.paste(layer, (0, 0))
        layer = canvas
    return Image.alpha_composite(b, layer)


# --------------------------------------------------------------------------
# gradients
# --------------------------------------------------------------------------

def linear_gradient(size, stops, angle=45.0):
    """Linear gradient image.

    stops: list of (r,g,b) or (r,g,b,a). angle: 0 = left->right, 90 = top->bottom.
    """
    w, h = size
    rad = np.deg2rad(angle)
    xs = np.linspace(0, 1, w, dtype=np.float32)[None, :]
    ys = np.linspace(0, 1, h, dtype=np.float32)[:, None]
    t = xs * np.cos(rad) + ys * np.sin(rad)
    t = (t - t.min()) / max(1e-6, (t.max() - t.min()))
    if len(stops) == 1:
        arr = np.zeros((h, w, 4), dtype=np.float32)
        arr[..., 0:3] = stops[0][:3]
        arr[..., 3] = stops[0][3] if len(stops[0]) > 3 else 255
        return Image.fromarray(arr.astype(np.uint8), "RGBA")
    seg = len(stops) - 1
    pos = t * seg
    idx = np.clip(pos.astype(np.int32), 0, seg - 1)
    frac = (pos - idx)[..., None]
    c0 = np.array(stops[0][:3], dtype=np.float32)
    cols = [np.array(s[:3], dtype=np.float32) for s in stops]
    a0 = np.array(stops[0][3] if len(stops[0]) > 3 else 255, dtype=np.float32)
    alphas = [np.array(s[3] if len(s) > 3 else 255, dtype=np.float32) for s in stops]
    out = np.zeros((h, w, 4), dtype=np.float32)
    for i in range(seg):
        m = (idx == i)[..., None]
        if not m.any():
            continue
        f = frac
        out[..., 0:3] = np.where(m, c0 * (1 - f) + cols[i + 1] * f, out[..., 0:3])
        a = alphas[i] * (1 - f[..., 0]) + alphas[i + 1] * f[..., 0]
        out[..., 3] = np.where(m[..., 0], a, out[..., 3])
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), "RGBA")


def radial_gradient(size, inner, outer, center=(0.5, 0.5), radius=0.75):
    """Radial gradient - the workhorse for the bokeh/light-burst backgrounds."""
    w, h = size
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    cx, cy = center[0] * w, center[1] * h
    d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
    d = d / max(1.0, radius * max(w, h))
    t = np.clip(d, 0, 1)[..., None]
    c0 = np.array(inner[:3], dtype=np.float32)
    c1 = np.array(outer[:3], dtype=np.float32)
    out = c0 * (1 - t) + c1 * t
    rgba = np.zeros((h, w, 4), dtype=np.float32)
    rgba[..., 0:3] = out
    rgba[..., 3] = 255
    return Image.fromarray(rgba.astype(np.uint8), "RGBA")


def bokeh_background(size, colors, count=90, seed=7, max_r=0.16, alpha=70):
    """The signature deep-blue bokeh plate.

    Reference films use a shallow-DOF background of soft coloured discs almost
    everywhere their graphics sit. It hides banding, adds depth, and makes
    flat vectors feel like they are in a room.

    Keep it subtle: the reference film's background is over half below 0.25
    luma, so the bokeh is a texture in the dark, not a light source. If the
    plate reads as grey rather than navy, the discs are too big, too many,
    or too bright - lower `alpha` first.
    """
    rng = np.random.default_rng(seed)
    w, h = size
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for _ in range(count):
        r = rng.uniform(max_r * 0.25, max_r) * max(w, h)
        cx = rng.uniform(-0.05, 1.05) * w
        cy = rng.uniform(-0.05, 1.05) * h
        c = colors[rng.integers(0, len(colors))]
        a = int(alpha * rng.uniform(0.35, 1.0))
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(*c, a))
    img = img.filter(ImageFilter.GaussianBlur(radius=max(w, h) * 0.012))
    return img


# --------------------------------------------------------------------------
# shapes
# --------------------------------------------------------------------------

def rounded_rect_mask(size, radius, box=None, supersample=1):
    """Anti-aliased rounded-rectangle alpha mask."""
    w, h = int(size[0]), int(size[1])
    sw, sh = w * supersample, h * supersample
    m = Image.new("L", (sw, sh), 0)
    d = ImageDraw.Draw(m)
    r = int(round(radius * supersample))
    b = [0, 0, sw - 1, sh - 1] if box is None else [v * supersample for v in box]
    d.rounded_rectangle(b, radius=r, fill=255)
    if supersample > 1:
        m = m.resize((w, h), Image.LANCZOS)
    return m


def circle_mask(size, radius, center=None, supersample=1):
    w, h = int(size[0]), int(size[1])
    sw, sh = w * supersample, h * supersample
    m = Image.new("L", (sw, sh), 0)
    d = ImageDraw.Draw(m)
    cx = (center[0] if center else w / 2) * supersample
    cy = (center[1] if center else h / 2) * supersample
    r = int(round(radius * supersample))
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=255)
    if supersample > 1:
        m = m.resize((w, h), Image.LANCZOS)
    return m


def triangle_mask(size, points, supersample=1):
    w, h = size
    sw, sh = w * supersample, h * supersample
    m = Image.new("L", (sw, sh), 0)
    d = ImageDraw.Draw(m)
    d.polygon([(x * supersample, y * supersample) for x, y in points], fill=255)
    if supersample > 1:
        m = m.resize((w, h), Image.LANCZOS)
    return m


def fill_gradient(shape_mask, stops, angle=45.0):
    """Paint a gradient through a mask. Returns RGBA."""
    grad = linear_gradient(shape_mask.size, stops, angle)
    out = Image.new("RGBA", shape_mask.size, (0, 0, 0, 0))
    out.paste(grad, (0, 0), shape_mask)
    return out


# --------------------------------------------------------------------------
# light
# --------------------------------------------------------------------------

def glow(rgba, radius=28, strength=1.0, color=None):
    """Return an RGBA layer containing only the additive glow of `rgba`.

    Blur the alpha channel, tint it, and return it as a screen-blendable
    layer. Compositing it with screen() is what makes a pill look lit rather
    than pasted.
    """
    a = rgba.split()[-1]
    blur = a.filter(ImageFilter.GaussianBlur(radius))
    arr = np.asarray(blur, dtype=np.float32) / 255.0
    if color is None:
        # tint by the layer's own average colour
        rgb = np.asarray(rgba.convert("RGB"), dtype=np.float32)
        m = np.asarray(a, dtype=np.float32) / 255.0
        tot = m.sum() + 1e-6
        avg = (rgb * m[..., None]).sum(axis=(0, 1)) / tot
    else:
        avg = np.array(color, dtype=np.float32)
    out = np.zeros((rgba.height, rgba.width, 4), dtype=np.float32)
    out[..., 0:3] = avg
    out[..., 3] = arr * strength * 255
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), "RGBA")


def drop_shadow(rgba, offset=(0, 14), blur=26, opacity=0.55, color=(0, 0, 0)):
    """Soft drop shadow layer, for lifting cards off the background."""
    a = rgba.split()[-1]
    sh = Image.new("RGBA", rgba.size, (0, 0, 0, 0))
    tint = Image.new("RGBA", rgba.size, (*color, 255))
    sh.paste(tint, (0, 0), a)
    arr = np.asarray(sh, dtype=np.uint8).copy()
    arr[..., 3] = (np.asarray(sh.split()[-1], dtype=np.float32) * opacity).astype(np.uint8)
    sh = Image.fromarray(arr, "RGBA")
    sh = sh.filter(ImageFilter.GaussianBlur(blur))
    sh = sh.transform(sh.size, Image.AFFINE, (1, 0, -offset[0], 0, 1, -offset[1]))
    return sh


def vignette(img, strength=0.55, radius=1.05):
    """Darken the corners - the reference film crushes edges to #070E1E."""
    w, h = img.size
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    cx, cy = w / 2, h / 2
    d = np.sqrt(((xx - cx) / cx) ** 2 + ((yy - cy) / cy) ** 2) / radius
    v = np.clip(d, 0, 1) ** 2
    arr = np.asarray(img.convert("RGB"), dtype=np.float32)
    arr *= (1 - v[..., None] * strength)
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB")


def grain(img, amount=5.0, seed=3):
    """Very fine film grain. Breaks up gradient banding, adds texture."""
    rng = np.random.default_rng(seed)
    arr = np.asarray(img.convert("RGB"), dtype=np.float32)
    n = rng.normal(0, amount, arr.shape[:2])[..., None]
    return Image.fromarray(np.clip(arr + n, 0, 255).astype(np.uint8), "RGB")


def bloom(img, threshold=190, radius=40, strength=0.42):
    """Highlight bloom - pick the bright pixels, blur them, add them back."""
    arr = np.asarray(img.convert("RGB"), dtype=np.float32)
    lum = arr.mean(axis=2)
    mask = np.clip((lum - threshold) / max(1.0, 255 - threshold), 0, 1)
    hi = Image.fromarray((mask * 255).astype(np.uint8), "L")
    hi = hi.filter(ImageFilter.GaussianBlur(radius))
    hia = (np.asarray(hi, dtype=np.float32) / 255.0)[..., None]
    out = arr + arr * hia * strength
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), "RGB")


# --------------------------------------------------------------------------
# type
# --------------------------------------------------------------------------

_FONT_CACHE = {}


def load_font(path, size):
    key = (path, int(size))
    if key not in _FONT_CACHE:
        _FONT_CACHE[key] = ImageFont.truetype(path, int(size))
    return _FONT_CACHE[key]


def text_size(draw, text, font, spacing=0):
    if not text:
        return (0, 0)
    try:
        b = draw.textbbox((0, 0), text, font=font)
        return b[2] - b[0], b[3] - b[1]
    except Exception:
        return draw.textsize(text, font=font)


def draw_text(draw, xy, text, font, fill=(255, 255, 255), anchor="la",
              stroke_width=0, stroke_fill=(0, 0, 0), spacing=4, align="left",
              letter_spacing=0.0):
    """Draw text with optional letter spacing (tracked-out caps look expensive).

    PIL cannot letter-space natively, so we draw glyph by glyph when
    letter_spacing != 0. Note that this path is Latin-only; complex scripts
    must be drawn as a single run to keep correct shaping.
    """
    if letter_spacing and text.isascii():
        widths = []
        for ch in text:
            b = draw.textbbox((0, 0), ch, font=font)
            widths.append(b[2] - b[0])
        total = sum(widths) + letter_spacing * (len(text) - 1)
        x = xy[0]
        if anchor[0] == "m":
            x -= total / 2
        elif anchor[0] == "r":
            x -= total
        for ch, wch in zip(text, widths):
            draw.text((x, xy[1]), ch, font=font, fill=fill, anchor=anchor[0] + anchor[1],
                      stroke_width=stroke_width, stroke_fill=stroke_fill)
            x += wch + letter_spacing
        return total
    draw.text(xy, text, font=font, fill=fill, anchor=anchor,
              stroke_width=stroke_width, stroke_fill=stroke_fill,
              spacing=spacing, align=align)


def gradient_text(size, text, font, stops, angle=0, letter_spacing=0.0):
    """Render text filled with a gradient (used for the hero numerals)."""
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    draw_text(d, (0, 0), text, font, fill=(255, 255, 255), anchor="lt",
              letter_spacing=letter_spacing)
    bbox = layer.getbbox()
    if not bbox:
        return layer
    glyph = layer.crop(bbox)
    grad = linear_gradient(glyph.size, stops, angle)
    out = Image.new("RGBA", glyph.size, (0, 0, 0, 0))
    out.paste(grad, (0, 0), glyph.split()[-1])
    canvas = Image.new("RGBA", size, (0, 0, 0, 0))
    canvas.paste(out, (bbox[0], bbox[1]))
    return canvas
