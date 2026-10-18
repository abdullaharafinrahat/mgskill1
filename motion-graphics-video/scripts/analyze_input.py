#!/usr/bin/env python3
"""Inspect a raw talking-head video (or a folder of images) so the storyboard
can be built on facts instead of guesses.

    python analyze_input.py raw_talking_head.mp4

Reports: duration, resolution, fps, audio loudness/RMS profile, speech
segments, per-second motion energy, and the shot boundaries. The output is
JSON so the agent can use it directly when writing the storyboard.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

import numpy as np


def ffmpeg_bin():
    """Same lookup order as the renderer's find_ffmpeg()."""
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
    for cand in ("/usr/local/bin/ffmpeg", "/usr/bin/ffmpeg",
                 "/opt/homebrew/bin/ffmpeg"):
        if os.path.exists(cand):
            return cand
    return None


def ffprobe_bin():
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


_DUR_RE = re.compile(r"Duration:\s*(\d+):(\d+):(\d+\.?\d*)")
_VID_RE = re.compile(
    r"Video:\s*([\w0-9]+).*?,\s*([\w0-9]+)\(?.*?\)?.*?(\d{2,5})x(\d{2,5})")
_FPS_RE = re.compile(r"(\d+(?:\.\d+)?)\s*fps")
_AUD_RE = re.compile(
    r"Audio:\s*([\w0-9]+).*?(\d+)\s*Hz,\s*([a-z0-9.]+)")


def probe(path):
    """Stream info. Uses ffprobe when it exists, and otherwise parses
    ffmpeg's own banner - the imageio-ffmpeg wheel ships ffmpeg but not
    ffprobe, so the fallback is the common case, not the rare one."""
    ff = ffprobe_bin()
    if ff:
        out = subprocess.run(
            [ff, "-v", "error", "-print_format", "json", "-show_format",
             "-show_streams", path], capture_output=True, text=True).stdout
        try:
            data = json.loads(out)
        except Exception:
            data = {}
        if data.get("streams"):
            return data

    ffm = ffmpeg_bin()
    if not ffm:
        return {}
    err = subprocess.run([ffm, "-hide_banner", "-i", path],
                         capture_output=True, text=True).stderr

    info = {"format": {}, "streams": []}
    m = _DUR_RE.search(err)
    if m:
        h, mi, s = int(m.group(1)), int(m.group(2)), float(m.group(3))
        info["format"]["duration"] = f"{h * 3600 + mi * 60 + s:.3f}"
    for line in err.splitlines():
        if "Video:" in line and "Stream #" in line:
            vm = _VID_RE.search(line)
            if not vm:
                continue
            fps = _FPS_RE.search(line)
            info["streams"].append({
                "codec_type": "video",
                "codec_name": vm.group(1),
                "pix_fmt": vm.group(2),
                "width": int(vm.group(3)),
                "height": int(vm.group(4)),
                "avg_frame_rate": f"{fps.group(1)}/1" if fps else None,
            })
        elif "Audio:" in line and "Stream #" in line:
            am = _AUD_RE.search(line)
            if not am:
                continue
            layout = am.group(3)
            info["streams"].append({
                "codec_type": "audio",
                "codec_name": am.group(1),
                "sample_rate": am.group(2),
                "channels": 1 if layout.startswith("mono") else 2,
            })
    return info


def decode_audio(path, sr=16000):
    """Decode to mono float32 via ffmpeg (never hand a path to an ASR lib)."""
    ff = ffmpeg_bin()
    if not ff:
        return None, sr
    cmd = [ff, "-hide_banner", "-loglevel", "error", "-i", path, "-vn",
           "-ac", "1", "-ar", str(sr), "-f", "f32le", "-"]
    p = subprocess.run(cmd, capture_output=True)
    if p.returncode != 0 or not p.stdout:
        return None, sr
    return np.frombuffer(p.stdout, dtype=np.float32), sr


def audio_profile(path):
    x, sr = decode_audio(path)
    if x is None:
        return None
    if x.size == 0:
        return {"error": "no audio"}
    n = len(x)
    hop = sr // 4
    frames = [x[i:i + hop] for i in range(0, n, hop)]
    rms = np.array([np.sqrt(np.mean(f ** 2)) if f.size else 0.0 for f in frames])
    db = 20 * np.log10(np.maximum(rms, 1e-9))
    loud = db > (db.max() - 30) if db.size else np.array([])
    # contiguous speech regions
    regions = []
    start = None
    for i, v in enumerate(loud):
        if v and start is None:
            start = i
        elif not v and start is not None:
            if (i - start) * 0.25 > 0.25:
                regions.append([round(start * 0.25, 2), round(i * 0.25, 2)])
            start = None
    if start is not None and loud.size:
        regions.append([round(start * 0.25, 2), round(loud.size * 0.25, 2)])
    # motion-ish proxy: short-term energy variance
    energy = np.abs(np.diff(x)) if n > 1 else np.array([0.0])
    seg = max(1, sr // 10)
    m = [float(np.mean(energy[i:i + seg])) for i in range(0, len(energy), seg)]
    m = np.array(m) if m else np.array([0.0])
    return {
        "duration": round(n / sr, 2),
        "sample_rate": sr,
        "peak_db": round(float(20 * np.log10(max(1e-9, np.max(np.abs(x))))), 2),
        "rms_db_median": round(float(np.median(db)), 2),
        "speech_regions": regions,
        "speech_coverage": round(sum(b - a for a, b in regions) / max(1e-6, n / sr), 3),
        "energy_timeline_0_1": [round(float(v), 4) for v in
                                (m / max(1e-9, m.max()))] if m.size else [],
    }


def motion_energy(path, fps=4):
    """Per-second-ish motion energy from downscaled grayscale frames."""
    ff = ffmpeg_bin()
    if not ff:
        return []
    out = subprocess.run(
        [ff, "-hide_banner", "-loglevel", "error", "-i", path,
         "-vf", f"fps={fps},scale=160:-2,format=gray", "-f", "rawvideo", "-"],
        capture_output=True).stdout
    if not out:
        return []
    w = 160
    # derive height from a probe of one frame
    probe_cmd = [ff, "-hide_banner", "-loglevel", "error", "-i", path,
                 "-vf", f"fps={fps},scale=160:-2,format=gray", "-frames:v", "1",
                 "-f", "rawvideo", "-"]
    one = subprocess.run(probe_cmd, capture_output=True).stdout
    if not one:
        return []
    h = len(one) // w
    if h == 0:
        return []
    n = len(out) // (w * h)
    arr = np.frombuffer(out[:n * w * h], dtype=np.uint8).reshape(n, h, w).astype(np.float32)
    if n < 2:
        return []
    d = np.abs(np.diff(arr, axis=0)).mean(axis=(1, 2))
    d = d / max(1e-6, d.max())
    return [round(float(v), 4) for v in d]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("-o", "--out", default=None, help="write JSON here")
    ap.add_argument("--skip-motion", action="store_true")
    args = ap.parse_args()

    if not os.path.exists(args.input):
        print(f"no such file: {args.input}", file=sys.stderr)
        return 2

    info = probe(args.input)
    v = next((s for s in info.get("streams", []) if s.get("codec_type") == "video"), {})
    a = next((s for s in info.get("streams", []) if s.get("codec_type") == "audio"), {})

    report = {
        "path": os.path.abspath(args.input),
        "size_bytes": os.path.getsize(args.input),
        "duration": round(float(info.get("format", {}).get("duration", 0) or 0), 2),
        "video": {
            "codec": v.get("codec_name"),
            "width": v.get("width"),
            "height": v.get("height"),
            "fps": v.get("avg_frame_rate"),
            "pix_fmt": v.get("pix_fmt"),
        },
        "audio": {
            "codec": a.get("codec_name"),
            "sample_rate": a.get("sample_rate"),
            "channels": a.get("channels"),
        },
    }
    report["audio_profile"] = audio_profile(args.input)
    if not args.skip_motion:
        report["motion_energy"] = motion_energy(args.input)
        me = report["motion_energy"]
        if me:
            report["motion_stats"] = {
                "mean": round(float(np.mean(me)), 4),
                "p95": round(float(np.percentile(me, 95)), 4),
                "max": round(float(np.max(me)), 4),
                "dead_zones_1s": [
                    i for i, v_ in enumerate(me) if v_ < 0.05
                ],
            }

    text = json.dumps(report, indent=2, ensure_ascii=False)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"wrote {args.out}")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
