"""The frame loop: storyboard -> pixels -> mp4.

Design notes
------------
* Frames are rendered at SS x resolution and downscaled, so curves are clean
  without a GPU.
* Video clips are pre-extracted once into a frame cache rather than being
  decoded per-frame; a 2-minute film with 30 video layers would otherwise
  decode the same file hundreds of times.
* Output is piped straight into ffmpeg as rawvideo - no intermediate PNG
  sequences, no disk churn.
"""
import json
import math
import os
import shutil
import subprocess
import sys
import tempfile

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from . import theme as T
from . import draw as D
from . import layers as L
from . import components as C
from . import fonts as F


def find_ffmpeg():
    """Locate ffmpeg.

    Looked for, in order: the FFMPEG_BINARY environment variable, PATH, the
    imageio-ffmpeg wheel, a bin/ffmpeg inside the skill, and the usual
    system locations. Failing this is the single most common setup
    problem, so the error message lists everywhere that was checked.
    """
    env = os.environ.get("FFMPEG_BINARY")
    if env and os.path.exists(env):
        return env
    exe = shutil.which("ffmpeg")
    if exe:
        return exe
    try:
        import imageio_ffmpeg
        p = imageio_ffmpeg.get_ffmpeg_exe()
        if p and os.path.exists(p):
            return p
    except Exception:
        pass
    local = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__)))), "bin", "ffmpeg")
    if os.path.exists(local):
        return local
    for cand in ("/usr/local/bin/ffmpeg", "/usr/bin/ffmpeg",
                 "/opt/homebrew/bin/ffmpeg", "/snap/bin/ffmpeg",
                 "/usr/local/ffmpeg/bin/ffmpeg"):
        if os.path.exists(cand):
            return cand
    raise RuntimeError(
        "ffmpeg not found. Checked: $FFMPEG_BINARY, PATH, the imageio-ffmpeg "
        "wheel, <skill>/bin/ffmpeg, /usr/local/bin, /usr/bin, /opt/homebrew/bin.\n"
        "Install it with `apt install ffmpeg` / `brew install ffmpeg`, or "
        "`pip install imageio-ffmpeg`, or set FFMPEG_BINARY=/path/to/ffmpeg.")


def find_ffprobe():
    exe = shutil.which("ffprobe")
    if exe:
        return exe
    try:
        import imageio_ffmpeg
        p = imageio_ffmpeg.get_ffmpeg_exe().replace("ffmpeg", "ffprobe")
        if os.path.exists(p):
            return p
    except Exception:
        pass
    return None


# --------------------------------------------------------------------------
# fonts
# --------------------------------------------------------------------------

def resolve_fonts(fonts_dir, overrides=None):
    """Backwards-compatible shim; the real work lives in mgv.fonts."""
    return F.resolve_fonts(fonts_dir, overrides)


def font_for(th, role):
    return F.font_for(th.get("FONTS", {}), role)


# --------------------------------------------------------------------------
# media preparation
# --------------------------------------------------------------------------

def probe_duration(path):
    ff = find_ffprobe()
    if not ff:
        return None
    out = subprocess.run([ff, "-v", "error", "-show_entries", "format=duration",
                          "-of", "default=nw=1:nk=1", path],
                         capture_output=True, text=True).stdout.strip()
    try:
        return float(out)
    except Exception:
        return None


def extract_video_frames(path, src_in, duration, fps, width, height, cache_dir,
                          tag):
    """Extract a clip's frames once, into a temp dir, scaled to the render
    size.

    The frames stay on disk. Holding them in memory is fine for a 720p
    preview and fatal for 1080p - a 3-second clip is 90 frames of
    1920x1080x3 bytes, which is 560 MB of RAM for one layer. The renderer
    reads them back one at a time instead.

    Returns (directory, [filenames], frame_offset)."""
    os.makedirs(cache_dir, exist_ok=True)
    out_dir = os.path.join(cache_dir, tag)
    if os.path.exists(out_dir):
        shutil.rmtree(out_dir)
    os.makedirs(out_dir, exist_ok=True)
    ff = find_ffmpeg()
    pat = os.path.join(out_dir, "%06d.jpg")
    cmd = [ff, "-hide_banner", "-loglevel", "error",
           "-ss", f"{max(0.0, src_in):.3f}", "-i", path,
           "-t", f"{duration:.3f}",
           "-vf", f"fps={fps},scale={width}:{height}:force_original_aspect_ratio=increase,crop={width}:{height}",
           "-q:v", "2", "-vsync", "0", pat, "-y"]
    subprocess.run(cmd, capture_output=True)
    files = sorted(os.listdir(out_dir))
    return out_dir, files, 0


# --------------------------------------------------------------------------
# renderer
# --------------------------------------------------------------------------

class Renderer:
    def __init__(self, storyboard, out_path, width=1920, height=1080, fps=30,
                 workdir=None, fonts_dir=None, preview=None):
        self.sb = storyboard
        self.out_path = out_path
        self.W, self.H = width, height
        self.fps = fps
        self.size = (width, height)
        self.workdir = workdir or tempfile.mkdtemp(prefix="mgv_")
        self.cache_dir = os.path.join(self.workdir, "frames")
        os.makedirs(self.cache_dir, exist_ok=True)
        fonts_dir = fonts_dir or os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(
                os.path.abspath(__file__)))),
            "assets", "fonts")
        self.th = T.theme_from_dict(storyboard.get("theme", {}))
        self.th["FONTS"] = resolve_fonts(fonts_dir, storyboard.get("fonts", {}))
        self._lang_role = F.script_for_language(
            storyboard.get("meta", {}).get("language"))
        self.shots = storyboard.get("shots", [])
        self.total = sum(float(s.get("duration", 1.0)) for s in self.shots)
        self.preview = preview
        self._prepared = False

    # ---------------- media ----------------
    def _role_for(self, layer):
        role = layer.get("font_role")
        if role:
            return role
        if self._lang_role:
            weight = layer.get("weight", "bold")
            if weight in ("bold", "black", "display"):
                cand = f"{self._lang_role}_bold"
                if cand in self.th["FONTS"]:
                    return cand
            return self._lang_role
        return layer.get("weight", "bold")

    def _font_px(self, layer, kind):
        H = self.H
        if kind == "text":
            return max(10, int(H * layer.get("size", T.TYPE_SCALE["headline"])))
        h = float(layer.get("h", 0.10)) * H
        factor = {"pill": 0.40, "bubble": 0.26, "label": 0.38,
                  "numeral": 0.60, "icon": 0.46}.get(kind, 0.35)
        return max(10, int(h * factor))

    def prepare(self):
        if self._prepared:
            return
        for si, shot in enumerate(self.shots):
            for li, layer in enumerate(shot.get("layers", [])):
                kind = layer.get("type")
                if kind == "video":
                    src = layer.get("src")
                    if src and os.path.exists(src):
                        fdir, files, off = extract_video_frames(
                            src, layer.get("src_in", 0.0),
                            float(layer.get("src_dur", shot["duration"])),
                            self.fps, self.W, self.H, self.cache_dir,
                            f"s{si}_l{li}")
                        layer["_frame_dir"] = fdir
                        layer["_frame_files"] = files
                        layer["_frame_offset"] = off
                elif kind in ("image",):
                    layer["_image"] = L._load_image(layer.get("src"))
                elif kind in ("card", "avatar", "monitor", "phone"):
                    layer["_image"] = L._load_image(layer.get("src"))
                if kind in ("pill", "bubble", "label", "numeral", "icon", "text"):
                    spec = F.font_for(self.th["FONTS"], self._role_for(layer))
                    if spec:
                        path, weight = spec
                        px = self._font_px(layer, kind)
                        layer["_font_path"] = path
                        layer["_font_weight"] = weight
                        layer["_font"] = F.make_font(path, px, weight)
        self._prepared = True

    # ---------------- frame ----------------
    def render_shot_frame(self, shot, t):
        canvas = Image.new("RGB", self.size, T.parse_color(self.th.get("VOID"), T.VOID))
        for layer in shot.get("layers", []):
            kind = layer.get("type")
            fn = L.RENDERERS.get(kind)
            if fn is None:
                continue
            layer["_shot_duration"] = float(shot.get("duration", 1.0))
            try:
                sub = fn(self.th, layer, t, self.size)
            except Exception as e:  # a broken layer must not kill the render
                print(f"  ! layer '{kind}' failed: {e}", file=sys.stderr)
                continue
            if sub is None:
                continue
            if sub.mode != "RGBA":
                sub = sub.convert("RGBA")
            tf = L.layer_transform(layer, t, self.size)
            if tf.alpha <= 0.001:
                continue

            px = layer.get("x", 0.5) * self.size[0]
            py = layer.get("y", 0.5) * self.size[1]

            if tf.rot:
                sub = sub.rotate(-tf.rot, resample=Image.BICUBIC,
                                 center=(px, py))
            if abs(tf.scale - 1.0) > 1e-3:
                s = max(0.01, tf.scale)
                sub = sub.transform(
                    sub.size, Image.AFFINE,
                    (1 / s, 0, px * (s - 1) / s, 0, 1 / s, py * (s - 1) / s),
                    resample=Image.BICUBIC)
            if tf.dx or tf.dy:
                sub = sub.transform(sub.size, Image.AFFINE,
                                    (1, 0, -tf.dx, 0, 1, -tf.dy),
                                    resample=Image.BILINEAR)
            if tf.blur > 0.05:
                sub = sub.filter(ImageFilter.GaussianBlur(tf.blur))
            if tf.mask is not None:
                a = sub.split()[-1]
                sub.putalpha(Image.composite(a, Image.new("L", a.size, 0), tf.mask))
            if tf.alpha < 0.999:
                a = sub.split()[-1].point(lambda v: int(v * tf.alpha))
                sub.putalpha(a)
            canvas = D.overlay_alpha(canvas, sub)
        return canvas.convert("RGB")

    def render(self, audio_path=None, music_path=None, music_gain_db=-13.0,
               music_duck=False):
        self.prepare()
        ff = find_ffmpeg()
        nframes = int(round(self.total * self.fps))

        tmp_out = self.out_path + ".silent.mp4"
        cmd = [ff, "-hide_banner", "-loglevel", "error", "-y",
               "-f", "rawvideo", "-pix_fmt", "rgb24",
               "-s", f"{self.W}x{self.H}", "-r", str(self.fps), "-i", "-",
               "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "19",
               "-pix_fmt", "yuv420p", "-movflags", "+faststart", tmp_out]
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)

        t0 = 0.0
        done = 0
        for shot in self.shots:
            dur = float(shot.get("duration", 1.0))
            steps = max(1, int(round(dur * self.fps)))
            for i in range(steps):
                lt = i / self.fps
                frame = self.render_shot_frame(shot, lt)
                if self.preview and (done % max(1, self.preview) == 0):
                    frame.save(f"{self.workdir}/preview_{done:05d}.jpg", quality=88)
                proc.stdin.write(frame.tobytes())
                done += 1
            t0 += dur
        proc.stdin.close()
        err = proc.stderr.read().decode(errors="ignore")
        proc.wait()
        if proc.returncode != 0:
            raise RuntimeError(f"ffmpeg failed:\n{err}")

        self._mux(tmp_out, audio_path, music_path, music_gain_db, music_duck,
                  duration=self.total)
        return self.out_path

    def _mux(self, video, audio_path, music_path, music_gain_db, music_duck,
             duration=None):
        ff = find_ffmpeg()
        inputs = ["-i", video]
        if audio_path:
            inputs += ["-i", audio_path]
        if music_path:
            inputs += ["-i", music_path]
        filt = []
        maps = []
        if audio_path:
            if music_path:
                filt.append(f"[1:a]aresample=48000[a0]")
                filt.append(f"[2:a]aresample=48000,volume={music_gain_db}dB[m0]")
                if music_duck:
                    filt.append("[a0][m0]sidechaincompress=threshold=0.02:ratio=8:attack=20:release=400[ducked]")
                    filt.append("[ducked][m0]amix=inputs=2:duration=longest:weights=1 1[aout]")
                else:
                    filt.append("[a0][m0]amix=inputs=2:duration=longest:weights=1 1[aout]")
                maps += ["-map", "0:v", "-map", "[aout]"]
            else:
                maps += ["-map", "0:v", "-map", "1:a"]
        else:
            if music_path:
                filt.append(f"[1:a]aresample=48000,volume={music_gain_db}dB[aout]")
                maps += ["-map", "0:v", "-map", "[aout]"]
            else:
                maps += ["-map", "0:v"]
        cmd = [ff, "-hide_banner", "-loglevel", "error", "-y"] + inputs
        if filt:
            cmd += ["-filter_complex", ";".join(filt)]
        cmd += maps + ["-c:v", "copy", "-c:a", "aac", "-b:a", "192k"]
        if duration:
            # the storyboard owns the runtime: a longer voice track must not
            # stretch the film past its last shot
            cmd += ["-t", f"{duration:.3f}"]
        cmd += ["-movflags", "+faststart", self.out_path]
        p = subprocess.run(cmd, capture_output=True)
        if p.returncode != 0 or not os.path.exists(self.out_path):
            err = p.stderr.decode(errors="ignore")
            raise RuntimeError(f"muxing failed:\n{err}")
        try:
            os.remove(video)
        except OSError:
            pass
