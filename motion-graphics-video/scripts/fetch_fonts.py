#!/usr/bin/env python3
"""Download the fonts the renderer needs.

The renderer needs a geometric sans with a heavy weight for display type and
a script-appropriate face for non-Latin text. Fonts are fetched once into
`assets/fonts/` so the skill works offline afterwards.

    python fetch_fonts.py [--dir assets/fonts] [--all-scripts]
"""
import argparse
import os
import sys
import urllib.request

# Variable fonts from the Google Fonts repository. One file per family
# covers every weight - the renderer sets the weight axis, so a single
# 850 KB download gives Regular through Black.
FONTS = {
    "Inter-Variable.ttf":
        "https://github.com/google/fonts/raw/main/ofl/inter/"
        "Inter%5Bopsz%2Cwght%5D.ttf",
}

SCRIPT_FONTS = {
    "NotoSansBengali.ttf":
        "https://github.com/google/fonts/raw/main/ofl/notosansbengali/"
        "NotoSansBengali%5Bwdth%2Cwght%5D.ttf",
    "NotoSansDevanagari.ttf":
        "https://github.com/google/fonts/raw/main/ofl/notosansdevanagari/"
        "NotoSansDevanagari%5Bwdth%2Cwght%5D.ttf",
    "NotoSansArabic.ttf":
        "https://github.com/google/fonts/raw/main/ofl/notosansarabic/"
        "NotoSansArabic%5Bwdth%2Cwght%5D.ttf",
}


def fetch(url, dest, force=False):
    if os.path.exists(dest) and not force and os.path.getsize(dest) > 1024:
        return "cached"
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=60) as r:
            data = r.read()
        if len(data) < 1024:
            return "too small (%d bytes)" % len(data)
        with open(dest, "wb") as f:
            f.write(data)
        return f"ok ({len(data)//1024} KB)"
    except Exception as e:
        return f"FAILED: {e}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default=os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "fonts"))
    ap.add_argument("--all-scripts", action="store_true",
                    help="also fetch Bengali/Devanagari/Arabic faces")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    print(f"Fetching fonts into {args.dir}")
    for name, url in FONTS.items():
        print(f"  {name:34s} {fetch(url, os.path.join(args.dir, name), args.force)}")
    if args.all_scripts:
        for name, url in SCRIPT_FONTS.items():
            print(f"  {name:34s} {fetch(url, os.path.join(args.dir, name), args.force)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
