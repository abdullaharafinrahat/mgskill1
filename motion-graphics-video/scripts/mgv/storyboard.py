"""Storyboard loading, normalisation, and validation.

The storyboard is the contract between the narrative and the renderer. It is
deliberately *not* just a list of layers: every shot carries a `purpose`,
and every shot belongs to an `act`. That is what keeps a render from
degenerating into a pile of motion with no argument.

Validation is where the storytelling gets enforced. The rules below are
derived from the measured structure of the reference film, not invented:

* a hook lands in the first 3 seconds;
* every shot has a reason to exist;
* the edit breathes - a busy moment is always followed by a quiet one;
* there is exactly one argument, and it escalates;
* the ending asks for something.

Technical checks (missing assets, bad coordinates, unknown layer types) are
reported separately from narrative checks so you can tell "this will crash"
from "this will not persuade".
"""
import json
import os

VALID_LAYER_TYPES = {
    "bg", "text", "image", "video", "pill", "bubble", "card", "avatar",
    "label", "cursor", "monitor", "numeral", "sparkles", "graph", "icon",
    "phone", "circuit",
}

ASSET_LAYER_TYPES = {"image", "card", "avatar", "monitor", "phone"}

# Reference-film structure, used as the yardstick.
TARGETS = {
    "hook_deadline": 3.0,          # seconds
    "max_shot_without_purpose": 6.0,
    "words_per_second": (1.7, 3.3),
    "min_graphics_ratio": 0.25,
    "max_same_visual_run": 3,
    "punch_interval": 32.0,        # a "punch" at least this often
    "cta_window": 0.18,            # CTA must land in the final 18% of runtime
    "min_acts": 3,
    "recommended_acts": 4,
}


class Issue:
    def __init__(self, level, code, message, where=""):
        self.level = level      # "error" | "warn" | "info"
        self.code = code
        self.message = message
        self.where = where

    def __str__(self):
        loc = f" [{self.where}]" if self.where else ""
        return f"{self.level.upper():5s} {self.code}{loc}: {self.message}"


def load(path):
    with open(path, "r", encoding="utf-8") as f:
        sb = json.load(f)
    return normalise(sb, base_dir=os.path.dirname(os.path.abspath(path)))


def _resolve(path, base_dir):
    """Resolve an asset path relative to the storyboard file when it is not
    found relative to the current working directory. A storyboard that
    references 'assets/hero.png' should work wherever you run the build."""
    if not path or os.path.isabs(path):
        return path
    if os.path.exists(path):
        return os.path.abspath(path)
    if base_dir:
        cand = os.path.join(base_dir, path)
        if os.path.exists(cand):
            return os.path.abspath(cand)
    return path


def normalise(sb, base_dir=None):
    """Fill in defaults and compute absolute timings."""
    sb.setdefault("meta", {})
    sb.setdefault("theme", {})
    sb.setdefault("shots", [])
    t = 0.0
    for i, shot in enumerate(sb["shots"]):
        shot.setdefault("id", f"s{i+1:02d}")
        shot.setdefault("purpose", "")
        shot.setdefault("act", "")
        shot.setdefault("visual", "graphics")
        shot.setdefault("duration", 1.5)
        shot.setdefault("layers", [])
        shot["_start"] = round(t, 3)
        t += float(shot["duration"])
        shot["_end"] = round(t, 3)
    sb["_total"] = round(t, 3)
    if base_dir:
        for shot in sb["shots"]:
            for layer in shot.get("layers", []):
                if layer.get("src"):
                    layer["src"] = _resolve(layer["src"], base_dir)
        for a in sb.get("assets_needed", []):
            if a.get("path"):
                a["_rel_path"] = a["path"]
                a["path"] = _resolve(a["path"], base_dir)
        for shot in sb["shots"]:
            for layer in shot.get("layers", []):
                if layer.get("src"):
                    layer["_rel_path"] = layer["src"]
    return sb


def count_words(text):
    """Word count that works for space-separated scripts. For scripts in
    languages without spaces between words this undercounts, so the caller
    treats the speech-rate check as a soft warning."""
    return len([w for w in (text or "").split() if w.strip()])


def validate(sb, strict=True):
    """Return a list of Issue objects. `strict` promotes narrative warnings
    to errors - use it when the user asked for a finished video."""
    issues = []
    shots = sb.get("shots", [])
    total = sb.get("_total", 0.0)

    if not shots:
        issues.append(Issue("error", "NO_SHOTS", "The storyboard has no shots."))
        return issues

    # ---------------- narrative: acts ----------------
    acts = [a for a in sb.get("acts", [])]
    act_names = {a.get("id") for a in acts if a.get("id")}
    used_acts = {s.get("act") for s in shots if s.get("act")}
    if len(acts) < TARGETS["min_acts"]:
        issues.append(Issue(
            "error", "ACTS_TOO_FEW",
            f"Only {len(acts)} act(s) declared. A persuasive piece needs at "
            f"least {TARGETS['min_acts']} (hook, problem, proof, offer).",
            "meta"))
    if acts and len(acts) < TARGETS["recommended_acts"]:
        issues.append(Issue(
            "warn", "ACTS_THIN",
            f"{len(acts)} act(s) - consider {TARGETS['recommended_acts']}: "
            "Hook, Problem, Credibility, Offer.", "meta"))
    orphan = used_acts - act_names
    if orphan:
        issues.append(Issue(
            "error", "ACT_UNDECLARED",
            f"Shots reference undeclared act(s): {', '.join(sorted(orphan))}.", "meta"))

    # ---------------- narrative: hook ----------------
    first = shots[0]
    if float(first.get("duration", 0)) > TARGETS["hook_deadline"]:
        issues.append(Issue(
            "error", "HOOK_LATE",
            f"The first shot lasts {first.get('duration')}s. The hook must land "
            f"within {TARGETS['hook_deadline']}s or the viewer leaves.",
            first.get("id", "shot 1")))

    # ---------------- narrative: every shot earns its place ----------------
    for s in shots:
        if not str(s.get("purpose", "")).strip():
            issues.append(Issue(
                "error" if strict else "warn", "NO_PURPOSE",
                "This shot has no stated purpose. Say what it is doing for the "
                "argument, or cut it.", s.get("id")))
        if float(s.get("duration", 0)) > TARGETS["max_shot_without_purpose"]:
            issues.append(Issue(
                "warn", "SHOT_TOO_LONG",
                f"{s.get('duration')}s is long for a single idea. Break it up or "
                "give the hold a reason.", s.get("id")))
        if float(s.get("duration", 0)) <= 0:
            issues.append(Issue("error", "BAD_DURATION",
                                "Duration must be > 0.", s.get("id")))

    # ---------------- narrative: visual variety ----------------
    run, run_id = 1, shots[0].get("id")
    for a, b in zip(shots, shots[1:]):
        if a.get("visual") == b.get("visual"):
            run += 1
            if run > TARGETS["max_same_visual_run"]:
                issues.append(Issue(
                    "warn", "VISUAL_MONOTONY",
                    f"{run} consecutive '{a.get('visual')}' shots. Interleave a "
                    "different visual mode so the edit keeps moving.",
                    b.get("id")))
                run = 1
        else:
            run = 1

    # ---------------- narrative: graphics ratio ----------------
    gcount = sum(1 for s in shots if s.get("visual") in ("graphics", "b-roll"))
    ratio = gcount / len(shots)
    if ratio < TARGETS["min_graphics_ratio"]:
        issues.append(Issue(
            "warn", "LOW_GRAPHICS_RATIO",
            f"Only {ratio:.0%} of shots are graphics/b-roll. A talking-head "
            "video with too few graphic beats reads as a slide deck with "
            "confetti - aim for at least "
            f"{TARGETS['min_graphics_ratio']:.0%}.", "meta"))

    # ---------------- narrative: punch / rest rhythm ----------------
    punches = [s for s in shots if s.get("punch")]
    if shots:
        span = total
        if span > 40 and len(punches) < max(1, int(span / TARGETS["punch_interval"])):
            issues.append(Issue(
                "warn", "NO_PUNCHES",
                f"A {span:.0f}s film with no 'punch' moments will feel flat. "
                "Mark the high-energy beats with \"punch\": true.", "meta"))
    for p in punches:
        idx = shots.index(p)
        rest_after = None
        for q in shots[idx + 1: idx + 4]:
            if q.get("rest") or float(q.get("duration", 0)) >= 1.6:
                rest_after = q
                break
        if rest_after is None:
            issues.append(Issue(
                "warn", "NO_REST_AFTER_PUNCH",
                "A punch is not followed by a rest within three shots. Busy "
                "followed by busy reads as noise.", p.get("id")))

    # ---------------- narrative: the ask ----------------
    tail = shots[int(len(shots) * (1 - TARGETS["cta_window"])):]
    cta = [s for s in tail if s.get("cta")]
    if not cta:
        issues.append(Issue(
            "warn", "NO_CTA",
            "No call to action in the closing stretch. Decide what the viewer "
            "should do next and put it on screen.", "meta"))

    # ---------------- narrative: speech rate ----------------
    voice = " ".join(s.get("voice", "") for s in shots)
    wc = count_words(voice)
    if total > 0 and voice:
        wps = wc / total
        lo, hi = TARGETS["words_per_second"]
        if wps < lo:
            issues.append(Issue(
                "warn", "SPEECH_SPARSE",
                f"{wc} words over {total:.1f}s = {wps:.2f} w/s (reference "
                f"{lo}-{hi}). Either the visuals will outrun the voice or the "
                "script is missing.", "meta"))
        elif wps > hi:
            issues.append(Issue(
                "warn", "SPEECH_DENSE",
                f"{wc} words over {total:.1f}s = {wps:.2f} w/s (reference "
                f"{lo}-{hi}). The voice will not land - cut words or extend the "
                "runtime.", "meta"))

    # ---------------- technical ----------------
    for s in shots:
        for li, layer in enumerate(s.get("layers", [])):
            k = layer.get("type")
            loc = f"{s.get('id')}/layer[{li}]"
            if k not in VALID_LAYER_TYPES:
                issues.append(Issue("error", "BAD_LAYER_TYPE",
                                    f"Unknown layer type '{k}'. Valid: "
                                    f"{', '.join(sorted(VALID_LAYER_TYPES))}", loc))
            for axis in ("x", "y"):
                v = layer.get(axis)
                if v is not None and not (-0.5 <= float(v) <= 1.5):
                    issues.append(Issue("warn", "OFFSCREEN",
                                        f"{axis}={v} is well outside the frame.",
                                        loc))
            src = layer.get("src")
            if k in ASSET_LAYER_TYPES:
                if not src:
                    issues.append(Issue("error", "MISSING_SRC",
                                        "Asset layer has no 'src'.", loc))
                elif not os.path.exists(src):
                    issues.append(Issue("error", "ASSET_MISSING",
                                        f"Asset not found: {src}", loc))
            if k == "video":
                src = layer.get("src")
                if not src:
                    issues.append(Issue("error", "MISSING_SRC",
                                        "Video layer has no 'src'.", loc))
                elif not os.path.exists(src):
                    issues.append(Issue("error", "ASSET_MISSING",
                                        f"Source video not found: {src}", loc))

    # ---------------- asset manifest consistency ----------------
    for a in sb.get("assets_needed", []):
        path = a.get("path", "")
        if path and os.path.exists(path):
            continue
        if not a.get("prompt"):
            issues.append(Issue(
                "warn", "ASSET_NO_PROMPT",
                f"Asset '{a.get('id', path)}' is neither present nor described "
                "by a prompt, so nothing can be produced for it.",
                "assets_needed"))
    return issues


def format_issues(issues):
    return "\n".join(str(i) for i in issues) or "No issues."


def summarise(issues):
    errs = sum(1 for i in issues if i.level == "error")
    warns = sum(1 for i in issues if i.level == "warn")
    return {"errors": errs, "warnings": warns, "ok": errs == 0}
