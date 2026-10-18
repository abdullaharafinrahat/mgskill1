#!/usr/bin/env python3
"""Build a motion-graphics video from a storyboard.

    python build_video.py storyboard.json -o out.mp4

The storyboard is validated first. If it fails validation the render is
refused by default, because a video that does not tell a story is a waste of
a render. Pass --force to override (you may be iterating on look, not story).
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mgv import storyboard as SB
from mgv import render as R


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("storyboard", help="path to storyboard JSON")
    ap.add_argument("-o", "--out", default="out.mp4", help="output video path")
    ap.add_argument("--width", type=int, default=1920)
    ap.add_argument("--height", type=int, default=1080)
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--audio", default=None,
                    help="narration track (wav/mp3). Defaults to the storyboard's "
                         "meta.audio")
    ap.add_argument("--music", default=None, help="music bed")
    ap.add_argument("--music-gain", type=float, default=-13.0,
                    help="music level in dB relative to full scale")
    ap.add_argument("--duck", action="store_true",
                    help="duck the music under the narration")
    ap.add_argument("--fonts-dir", default=None)
    ap.add_argument("--workdir", default=None)
    ap.add_argument("--preview", type=int, default=0,
                    help="save a preview still every N frames")
    ap.add_argument("--force", action="store_true",
                    help="render even if validation reports errors")
    ap.add_argument("--skip-validate", action="store_true")
    args = ap.parse_args()

    sb = SB.load(args.storyboard)
    meta = sb.get("meta", {})

    if not args.skip_validate:
        issues = SB.validate(sb)
        errs = [i for i in issues if i.level == "error"]
        warns = [i for i in issues if i.level == "warn"]
        print("Storyboard check")
        print("-" * 60)
        for i in issues:
            print("  " + str(i))
        s = SB.summarise(issues)
        print("-" * 60)
        print(f"{s['errors']} error(s), {s['warnings']} warning(s)")
        if errs and not args.force:
            print("\nRefusing to render a story that does not hold together.")
            print("Fix the errors above, or pass --force if you are iterating "
                  "on the look.")
            return 2
        if warns:
            print("\nWarnings are advisory - but read them. Most of them are "
                  "the difference\nbetween a video that persuades and one that "
                  "just moves.")

    audio = args.audio or meta.get("audio")
    music = args.music or meta.get("music")
    if audio and not os.path.exists(audio):
        if args.audio:
            print(f"ERROR: audio track not found: {args.audio}", file=sys.stderr)
            return 2
        # the storyboard named a track that is not there yet - warn and
        # render silent rather than refusing the whole build
        print(f"WARNING: meta.audio not found ({audio}); rendering without it.",
              file=sys.stderr)
        audio = None
    if music and not os.path.exists(music):
        if args.music:
            print(f"ERROR: music not found: {args.music}", file=sys.stderr)
            return 2
        print(f"WARNING: meta.music not found ({music}); rendering without it.",
              file=sys.stderr)
        music = None

    r = R.Renderer(sb, args.out, width=args.width, height=args.height,
                   fps=args.fps, workdir=args.workdir, fonts_dir=args.fonts_dir,
                   preview=args.preview or None)
    print(f"\nRendering {len(sb['shots'])} shots / {sb['_total']:.2f}s "
          f"at {args.width}x{args.height} {args.fps}fps ...")
    r.render(audio_path=audio, music_path=music,
             music_gain_db=args.music_gain, music_duck=args.duck)
    print(f"Wrote {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
