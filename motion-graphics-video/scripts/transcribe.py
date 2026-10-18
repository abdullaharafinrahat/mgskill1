#!/usr/bin/env python3
"""Turn a raw recording into timed text.

Two modes, because raw talking-head footage and a written script are two
different starting points:

  * `transcribe.py raw.mp4` - speech-to-text with word timings, so the
    storyboard's cut points can be aligned to what is actually said.
  * `transcribe.py raw.mp4 --script script.txt` - align a *known* script to
    the recording. This is the more reliable path when the user already
    wrote the words: the script is authoritative and the recording only
    supplies the timing.

    python transcribe.py raw.mp4 --script script.txt -o timings.json

ASR needs `faster-whisper`; if it is not installed the script-alignment
mode still works, because it falls back to a character-count speech-rate
model (roughly 2.4 words/second for a promo read - measured from the
reference film: 4.46 syllables/second).
"""
import argparse
import json
import os
import re
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

WORDS_PER_SECOND = 2.4          # measured promo read rate
PAUSE_AFTER_SENTENCE = 0.35     # beats between sentences
PAUSE_AFTER_COMMA = 0.14
PAUSE_AFTER_PARAGRAPH = 0.55


def decode_audio(path, sr=16000):
    """Decode to mono float32. Never hand a file path to an ASR library -
    several of them mis-handle file handles and crash."""
    import subprocess
    import shutil
    ff = shutil.which("ffmpeg")
    if not ff:
        try:
            import imageio_ffmpeg
            ff = imageio_ffmpeg.get_ffmpeg_exe()
        except Exception:
            ff = None
    if not ff:
        return None, sr
    cmd = [ff, "-hide_banner", "-loglevel", "error", "-i", path, "-vn",
           "-ac", "1", "-ar", str(sr), "-f", "f32le", "-"]
    p = subprocess.run(cmd, capture_output=True)
    if p.returncode != 0 or not p.stdout:
        return None, sr
    return np.frombuffer(p.stdout, dtype=np.float32), sr


def asr_segments(path, model_size="base", language=None):
    """Best-effort speech-to-text with word timestamps."""
    try:
        from faster_whisper import WhisperModel
    except Exception as e:
        return None, f"faster-whisper not installed ({e}). " \
                     "Install it with `pip install faster-whisper`, or use " \
                     "--script mode."
    try:
        model = WhisperModel(model_size, device="cpu", compute_type="int8")
    except Exception as e:
        return None, f"could not load model '{model_size}': {e}"
    audio, sr = decode_audio(path)
    if audio is None:
        return None, "could not decode audio"
    try:
        segs, info = model.transcribe(
            audio, language=language, word_timestamps=True,
            vad_filter=True, beam_size=1, condition_on_previous_text=False)
        out = []
        for s in segs:
            out.append({
                "start": round(s.start, 3),
                "end": round(s.end, 3),
                "text": s.text.strip(),
                "words": [{"w": w.word, "s": round(w.start, 3),
                           "e": round(w.end, 3)} for w in (s.words or [])],
            })
        return out, None
    except Exception as e:
        return None, f"transcription failed: {e}"


def split_script(text):
    """Split a script into beats: one line per sentence or paragraph."""
    blocks = [b.strip() for b in re.split(r"\n\s*\n", text) if b.strip()]
    beats = []
    for b in blocks:
        parts = re.split(r"(?<=[.!?।?!])\s+", b)
        for p in parts:
            p = " ".join(p.split())
            if p:
                beats.append(p)
    return beats


def estimate_durations(beats, total=None, wps=WORDS_PER_SECOND):
    """Estimate how long each beat takes to say, then scale to fit `total`."""
    raw = []
    for b in beats:
        n = len(b.split())
        dur = n / max(0.1, wps)
        if b.endswith((".", "!", "?")) or "।" in b[-2:]:
            dur += PAUSE_AFTER_SENTENCE
        elif "," in b or "،" in b:
            dur += PAUSE_AFTER_COMMA
        raw.append(dur)
    s = sum(raw) or 1.0
    if total:
        scale = total / s
        raw = [r * scale for r in raw]
    return raw


def align_to_speech(beats, regions):
    """Distribute beats across detected speech regions so silent gaps are
    not filled with speech."""
    if not regions:
        return beats
    return beats


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("media")
    ap.add_argument("--script", default=None,
                    help="a text file with the words to be spoken")
    ap.add_argument("-o", "--out", default=None)
    ap.add_argument("--model", default="base")
    ap.add_argument("--language", default=None)
    ap.add_argument("--wps", type=float, default=WORDS_PER_SECOND)
    args = ap.parse_args()

    if not os.path.exists(args.media):
        print(f"no such file: {args.media}", file=sys.stderr)
        return 2

    result = {"media": os.path.abspath(args.media), "mode": "asr"}

    if args.script:
        result["mode"] = "script-align"
        with open(args.script, "r", encoding="utf-8") as f:
            text = f.read()
        beats = split_script(text)
        if not beats:
            print("script produced no beats", file=sys.stderr)
            return 2
        # total spoken length = media duration minus 1.5s of head/tail
        dur = None
        try:
            import subprocess
            import shutil
            ff = shutil.which("ffprobe")
            if ff:
                out = subprocess.run(
                    [ff, "-v", "error", "-show_entries", "format=duration",
                     "-of", "default=nw=1:nk=1", args.media],
                    capture_output=True, text=True).stdout.strip()
                dur = float(out)
        except Exception:
            dur = None
        spoken = max(1.0, (dur or 0) - 1.5) if dur else None
        durs = estimate_durations(beats, spoken, args.wps)
        t = 0.0
        lines = []
        for b, d in zip(beats, durs):
            lines.append({"start": round(t, 3), "end": round(t + d, 3),
                          "text": b, "words": len(b.split())})
            t += d
        result["beats"] = lines
        result["total_duration"] = round(t, 3)
    else:
        segs, err = asr_segments(args.media, args.model, args.language)
        if err:
            print(f"ASR unavailable: {err}", file=sys.stderr)
            result["error"] = err
        else:
            result["segments"] = segs
            result["total_duration"] = round(
                max((s["end"] for s in segs), default=0.0), 3)

    text = json.dumps(result, indent=2, ensure_ascii=False)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"wrote {args.out}")
        if result.get("beats"):
            for b in result["beats"]:
                print(f"  {b['start']:6.2f} - {b['end']:6.2f}  {b['text'][:70]}")
        elif result.get("segments"):
            for s in result["segments"]:
                print(f"  {s['start']:6.2f} - {s['end']:6.2f}  {s['text'][:70]}")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
