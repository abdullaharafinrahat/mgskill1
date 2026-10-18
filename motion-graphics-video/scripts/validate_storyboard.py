#!/usr/bin/env python3
"""Check a storyboard for narrative and technical problems.

    python validate_storyboard.py storyboard.json [--strict] [--json]

Exit code 0 = no errors, 1 = errors found, 2 = could not read the file.
This is the gate that keeps "make it look cool" from quietly destroying the
argument the video is trying to make.
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mgv import storyboard as SB


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("storyboard")
    ap.add_argument("--strict", action="store_true",
                    help="treat narrative warnings as errors")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    ap.add_argument("--timeline", action="store_true",
                    help="print the shot timeline")
    args = ap.parse_args()

    if not os.path.exists(args.storyboard):
        print(f"no such file: {args.storyboard}", file=sys.stderr)
        return 2
    sb = SB.load(args.storyboard)
    issues = SB.validate(sb, strict=args.strict)

    if args.json:
        print(json.dumps({
            "ok": not any(i.level == "error" for i in issues),
            "total_duration": sb.get("_total", 0),
            "shots": len(sb.get("shots", [])),
            "issues": [{"level": i.level, "code": i.code, "where": i.where,
                        "message": i.message} for i in issues],
        }, indent=2, ensure_ascii=False))
        return 0 if not any(i.level == "error" for i in issues) else 1

    if args.timeline:
        print(f"{'shot':<6}{'act':<14}{'start':>7}{'dur':>7}  {'visual':<9}purpose")
        print("-" * 100)
        for s in sb.get("shots", []):
            print(f"{s.get('id',''):<6}{str(s.get('act','')):<14}"
                  f"{s.get('_start',0):>7.2f}{float(s.get('duration',0)):>7.2f}  "
                  f"{str(s.get('visual','')):<9}{str(s.get('purpose',''))[:52]}")
        print("-" * 100)
        print(f"{'TOTAL':<6}{'':<14}{0:>7.2f}{sb.get('_total',0):>7.2f}\n")

    for i in issues:
        print("  " + str(i))
    s = SB.summarise(issues)
    print(f"\n{s['errors']} error(s), {s['warnings']} warning(s), "
          f"{len(sb.get('shots', []))} shots, {sb.get('_total', 0):.2f}s")
    return 0 if s["errors"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
