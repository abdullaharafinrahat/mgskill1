"""Bengali-capable text rendering: HarfBuzz shaping -> Skia paths (cached)."""
import os
import uharfbuzz as hb
import skia
from fontTools.ttLib import TTFont
from fontTools.pens.basePen import BasePen
from common import FONT_DIR, fill, stroke


class _SkPen(BasePen):
    def __init__(self, gs):
        super().__init__(gs)
        self.p = skia.Path()

    def _moveTo(self, pt): self.p.moveTo(*pt)
    def _lineTo(self, pt): self.p.lineTo(*pt)
    def _curveToOne(self, a, b, c): self.p.cubicTo(*a, *b, *c)
    def _qCurveToOne(self, a, b): self.p.quadTo(*a, *b)
    def _closePath(self): self.p.close()


class _Font:
    def __init__(self, fn):
        path = os.path.join(FONT_DIR, fn)
        self.tt = TTFont(path)
        self.upem = self.tt['head'].unitsPerEm
        self.cmap = self.tt.getBestCmap()
        self.gs = self.tt.getGlyphSet()
        self.order = self.tt.getGlyphOrder()
        blob = hb.Blob.from_file_path(path)
        self.hb = hb.Font(hb.Face(blob))
        self._glyph = {}

    def glyph_path(self, gid):
        if gid not in self._glyph:
            pen = _SkPen(self.gs)
            self.gs[self.order[gid]].draw(pen)
            self._glyph[gid] = pen.p
        return self._glyph[gid]

    def shape(self, text):
        buf = hb.Buffer()
        buf.add_str(text)
        buf.guess_segment_properties()
        hb.shape(self.hb, buf, {"kern": True, "liga": True})
        return buf.glyph_infos, buf.glyph_positions


_FONTS = {}
_CACHE = {}


def _font(kind):
    if kind not in _FONTS:
        _FONTS[kind] = _Font({"bn": "NotoBengaliBold.ttf", "bnr": "NotoBengaliReg.ttf",
                              "lat": "NotoLatinBold.ttf"}[kind])
    return _FONTS[kind]


def _runs(text, bn):
    """Split into runs by whether the Bengali font has the glyph."""
    runs, cur, kind = [], "", None
    for ch in text:
        k = "bn" if (ord(ch) in bn.cmap and ch != ' ') else ("sp" if ch == ' ' else "lat")
        if k == "sp":
            k = kind or "bn"
        if kind is None:
            kind = k
        if k != kind:
            runs.append((kind, cur)); cur = ""; kind = k
        cur += ch
    if cur:
        runs.append((kind, cur))
    return runs


def text_path(text, size, regular=False):
    """Return (skia.Path with baseline at y=0 starting at x=0, width)."""
    key = (text, round(size, 1), regular)
    if key in _CACHE:
        return _CACHE[key]
    bn = _font("bnr" if regular else "bn")
    path = skia.Path()
    x = 0.0
    for kind, run in _runs(text, bn):
        f = bn if kind == "bn" else _font("lat")
        infos, poss = f.shape(run)
        sc = size / f.upem
        for inf, pos in zip(infos, poss):
            gp = f.glyph_path(inf.codepoint)
            if not gp.isEmpty():
                m = skia.Matrix()
                m.setScale(sc, -sc)
                m.postTranslate(x + pos.x_offset * sc, -pos.y_offset * sc)
                p2 = skia.Path()
                gp.transform(m, p2)
                path.addPath(p2)
            x += pos.x_advance * sc
    _CACHE[key] = (path, x)
    return _CACHE[key]


def text_width(text, size, regular=False):
    return text_path(text, size, regular)[1]


def draw_text(c, text, x, y, size, color="#ffffff", align="c", outline=None, outline_w=0,
              alpha=1.0, regular=False, shadow=None):
    """Draw text with baseline y. align: l/c/r. outline=(color) stroke around."""
    path, w = text_path(text, size, regular)
    ox = x - w / 2 if align == "c" else (x - w if align == "r" else x)
    c.save()
    c.translate(ox, y)
    if shadow:
        c.save(); c.translate(shadow[0], shadow[1])
        c.drawPath(path, fill(shadow[2], alpha * shadow[3] if len(shadow) > 3 else alpha))
        c.restore()
    if outline:
        c.drawPath(path, stroke(outline, outline_w, alpha))
    c.drawPath(path, fill(color, alpha))
    c.restore()
    return w


def wrap(text, size, maxw, regular=False):
    words, lines, cur = text.split(' '), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if text_width(t, size, regular) <= maxw or not cur:
            cur = t
        else:
            lines.append(cur); cur = w
    if cur:
        lines.append(cur)
    return lines
