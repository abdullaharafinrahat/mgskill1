"""Shared constants + helpers for the Zahid animation pipeline."""
import math, os, json
import skia

W, H, FPS = 1080, 1920, 30
ROOT = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.path.join(ROOT, "fonts")
AUDIO = os.path.join(ROOT, "audio01.mp3")
OUT = os.path.join(ROOT, "out")
TIMELINE = os.path.join(OUT, "timeline.json")
ENV_FILE = os.path.join(OUT, "env.json")
try:
    import imageio_ffmpeg
    FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
except Exception:
    FFMPEG = "ffmpeg"


# ---------- colour ----------
def C(h, a=1.0):
    h = h.lstrip('#')
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return skia.ColorSetARGB(int(max(0, min(1, a)) * 255), r, g, b)


def mix(h1, h2, t):
    h1 = h1.lstrip('#'); h2 = h2.lstrip('#')
    a = [int(h1[i:i + 2], 16) for i in (0, 2, 4)]
    b = [int(h2[i:i + 2], 16) for i in (0, 2, 4)]
    return '#%02x%02x%02x' % tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def fill(color, a=1.0):
    return skia.Paint(AntiAlias=True, Color=C(color, a))


def stroke(color, w, a=1.0, cap=skia.Paint.kRound_Cap, join=skia.Paint.kRound_Join):
    p = skia.Paint(AntiAlias=True, Color=C(color, a))
    p.setStyle(skia.Paint.kStroke_Style)
    p.setStrokeWidth(w)
    p.setStrokeCap(cap)
    p.setStrokeJoin(join)
    return p


def grad(x0, y0, x1, y1, c0, c1, a=1.0):
    p = skia.Paint(AntiAlias=True)
    p.setShader(skia.GradientShader.MakeLinear([(x0, y0), (x1, y1)], [C(c0, a), C(c1, a)]))
    return p


def radial(cx, cy, r, c0, c1, a0=1.0, a1=1.0):
    p = skia.Paint(AntiAlias=True)
    p.setShader(skia.GradientShader.MakeRadial((cx, cy), r, [C(c0, a0), C(c1, a1)]))
    return p


def blur_paint(color, sigma, a=1.0):
    p = fill(color, a)
    p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, sigma))
    return p


# ---------- easing / interpolation ----------
def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x


def lerp(a, b, t):
    return a + (b - a) * t


def smooth(t):
    t = clamp(t)
    return t * t * (3 - 2 * t)


def ease_out(t):
    t = clamp(t)
    return 1 - (1 - t) ** 3


def ease_in(t):
    t = clamp(t)
    return t ** 3


def ease_io(t):
    t = clamp(t)
    return 4 * t ** 3 if t < .5 else 1 - (-2 * t + 2) ** 3 / 2


def back_out(t, s=1.70158):
    t = clamp(t) - 1
    return t * t * ((s + 1) * t + s) + 1


def elastic(t):
    t = clamp(t)
    if t in (0, 1):
        return t
    return 2 ** (-9 * t) * math.sin((t * 10 - 0.75) * (2 * math.pi) / 3) + 1


def prog(t, t0, t1):
    """0..1 progress of t between t0 and t1."""
    if t1 <= t0:
        return 1.0 if t >= t0 else 0.0
    return clamp((t - t0) / (t1 - t0))


def keys(t, ks, ease=smooth):
    """Keyframe interpolation: ks=[(time,value),...] values may be tuples."""
    if t <= ks[0][0]:
        return ks[0][1]
    if t >= ks[-1][0]:
        return ks[-1][1]
    for (t0, v0), (t1, v1) in zip(ks, ks[1:]):
        if t0 <= t <= t1:
            u = ease((t - t0) / (t1 - t0))
            if isinstance(v0, (tuple, list)):
                return tuple(lerp(a, b, u) for a, b in zip(v0, v1))
            return lerp(v0, v1, u)
    return ks[-1][1]


def noise(t, seed=0.0):
    """Cheap smooth pseudo-noise in [-1,1] for handheld shake."""
    return (math.sin(t * 2.3 + seed) + math.sin(t * 4.1 + seed * 1.7) * .5 + math.sin(t * 7.7 + seed * 2.9) * .25) / 1.75


class Timeline:
    """Gives scenes access to audio-synchronised chunk timings + voice envelope."""

    def __init__(self):
        d = json.load(open(TIMELINE, encoding="utf-8"))
        self.chunks = d["chunks"]
        self.scenes = {int(k): v for k, v in d["scenes"].items()}
        self.duration = d["duration"]
        self.env = json.load(open(ENV_FILE))["env"]
        self.by_id = {c["id"]: c for c in self.chunks}

    def s(self, i):
        return self.by_id[i]["start"]

    def e(self, i):
        return self.by_id[i]["end"]

    def amp(self, t):
        i = int(t * FPS)
        if i < 0 or i >= len(self.env):
            return 0.0
        return self.env[i]

    def talking(self, t, a, b=None):
        b = a if b is None else b
        return self.s(a) <= t <= self.e(b)

    def mouth(self, t, a, b=None):
        return clamp(self.amp(t) * 1.3) if self.talking(t, a, b) else 0.0
