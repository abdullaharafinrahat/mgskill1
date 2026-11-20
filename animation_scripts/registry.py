# -*- coding: utf-8 -*-
"""Maps every shot to its chunk range, handles transitions, captions & per-frame drawing."""
import json, os, math
import numpy as np
from shots3 import *

HERE = os.path.dirname(os.path.abspath(__file__))
TL = json.load(open(os.path.join(HERE, "timeline.json")))
ENV = np.load(os.path.join(HERE, "amp.npy"))
DURATION = TL["duration"]
FPS = 30

REG = [
    (shot_hook_phone, 0, 0), (shot_shop_glow, 1, 1), (shot_shutter_sad, 2, 2), (shot_mirpur, 3, 3),
    (shot_father, 4, 4), (shot_wallclock, 5, 5), (shot_tried_all, 6, 6), (shot_never_measured, 7, 7),
    (shot_ad_poster, 8, 8), (shot_how_fast, 9, 9), (shot_cust_ask, 10, 11), (shot_zahid_hoye, 12, 13),
    (shot_kokhon, 14, 15), (shot_shrug, 16, 16), (shot_street, 17, 17), (shot_girl_arrive, 18, 19),
    (shot_girl_ask, 20, 21), (shot_zahid_reply, 22, 23), (shot_girl_choice, 24, 26), (shot_think, 27, 28),
    (shot_not_only_fix, 29, 29), (shot_when_back, 30, 30), (shot_night_clock, 31, 31), (shot_ten_phones, 32, 32),
    (shot_notebook_chart, 33, 34), (shot_cross_old, 35, 35), (shot_new_ad, 36, 37), (shot_half_charge, 38, 38),
    (shot_day1_arrive, 39, 39), (shot_waiting, 40, 41), (shot_calendar_rare, 42, 43), (shot_seventy, 44, 44),
    (shot_give_half, 45, 47), (shot_surprised, 48, 49), (shot_nod, 50, 50), (shot_brother, 51, 51),
    (shot_slowly, 52, 52), (shot_not_only_fast, 53, 53), (shot_promise, 54, 54), (shot_book, 55, 55),
    (shot_balloons, 56, 56), (shot_solid, 57, 57), (shot_takeaway, 58, 58), (shot_ask_yourself, 59, 59),
    (shot_check_time, 60, 60), (shot_clock_home, 61, 62), (shot_claim, 63, 63), (shot_promise_stamp, 64, 64),
    (shot_follow, 65, 65),
]

CH = TL["chunks"]
SHOTS = []
for fn, a, b in REG:
    g0 = CH[a]["start"]
    g1 = CH[b]["end"]
    SHOTS.append((fn, ShotCtx(TL, a, b, g0, g1, ENV), g0, g1))

TRANS = ["slide", "iris", "slideup", "bars", "fade", "iris", "slide", "bars"]
TD0, TD1 = 0.15, 0.40  # transition window relative to shot start (before / after)


def _draw(ctx, k, gt):
    fn, sc, g0, g1 = SHOTS[k]
    ctx.save()
    ctx.rectangle(0, 0, W, H)
    ctx.clip()
    sc.at(max(0.0, gt - g0))
    fn(ctx, sc)
    ctx.restore()


def draw_world(ctx, gt):
    cur = 0
    for i, (_, _, g0, g1) in enumerate(SHOTS):
        if gt >= g0 - TD0:
            cur = i
    g0 = SHOTS[cur][2]
    if cur > 0 and gt <= g0 + TD1:
        p = smooth((gt - (g0 - TD0)) / (TD0 + TD1))
        ty = TRANS[cur % len(TRANS)]
        if ty == "slide":
            ctx.save()
            ctx.translate(-p * W, 0)
            _draw(ctx, cur - 1, gt)
            ctx.restore()
            ctx.save()
            ctx.translate((1 - p) * W, 0)
            _draw(ctx, cur, gt)
            ctx.restore()
            return
        _draw(ctx, cur - 1, gt)
        ctx.save()
        if ty == "slideup":
            ctx.translate(0, (1 - p) * H)
            _draw(ctx, cur, gt)
        elif ty == "iris":
            ctx.new_path()
            ctx.arc(540, 960, p * 1250, 0, math.tau)
            ctx.clip()
            _draw(ctx, cur, gt)
        elif ty == "bars":
            ctx.new_path()
            for i in range(8):
                q = clamp(p * 1.6 - i * 0.08)
                ctx.rectangle(0, i * H / 8, W * q, H / 8 + 1)
            ctx.clip()
            _draw(ctx, cur, gt)
        else:
            ctx.push_group()
            _draw(ctx, cur, gt)
            ctx.pop_group_to_source()
            ctx.paint_with_alpha(p)
        ctx.restore()
    else:
        _draw(ctx, cur, gt)


def draw_caption(ctx, gt):
    idx = None
    for ch in CH:
        if gt >= ch["s0"] - 0.06:
            idx = ch["i"]
    if idx is None:
        return
    ch = CH[idx]
    if gt > ch["s1"] + 0.45:
        return
    q = back(prog(gt, ch["s0"] - 0.06, 0.22), 1.2)
    txt = ch["text"]
    col = "#FFD36B" if ch["speaker"] else "#FFF6E3"
    surf, _, w, h, _, nl = text_sprite(txt, 56, col, True and "sans", True, maxw=880)
    pw, ph = w + 26, h + 6
    cy = 1650
    ctx.save()
    ctx.translate(540, cy)
    ctx.scale(0.88 + 0.12 * q, 0.88 + 0.12 * q)
    ctx.translate(-540, -cy)
    rect(ctx, 540 - pw / 2, cy - ph / 2, pw, ph, "#241812", 44, a=0.86 * clamp(q))
    text(ctx, txt, 540, cy, 56, col, a=clamp(q), maxw=880)
    ctx.restore()


def draw_frame(ctx, gt):
    draw_world(ctx, gt)
    # progress bar
    rect(ctx, 0, 0, W, 12, "#000000", a=0.18)
    rect(ctx, 0, 0, W * gt / DURATION, 12, "#FFF3D0", a=0.95)
    draw_caption(ctx, gt)
