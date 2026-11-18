#!/usr/bin/env python3
"""
Script 4: scene_compositor.py
Choreographs all 9 animated 2D scenes synced to the Bengali/English voiceover script,
applies dynamic 2D camera movements (zoom, pan, tilt, shake), and renders synchronized
Bengali + English kinetic typography and audio-reactive elements.
"""

import math
import cv2
import numpy as np
from camera_engine import (
    WIDTH,
    HEIGHT,
    clamp,
    lerp,
    ease_out_cubic,
    ease_out_back,
    ease_in_out_cubic,
    hex_to_bgr,
    render_scene_background,
    get_camera_state,
    apply_camera_transform,
)
from visual_assets import (
    draw_platter,
    draw_date_seed,
    draw_ripe_date,
    draw_reaching_hand,
    draw_magnifying_glass,
    draw_character,
    draw_balance_scale,
    draw_label_pill,
    draw_rounded_card,
    render_html_sprite,
    composite_bgra,
)


SEED_OFFSETS = [
    (-210, -22, -25),
    (-145, 24, 14),
    (-185, 38, 42),
    (-95, -28, -12),
    (-75, 22, 28),
    (-245, 12, -8),
    (-130, -6, 33),
]


def render_scene_world(scene_id: int, t: float, scene_start: float, scene_end: float, energy: float) -> np.ndarray:
    """
    Renders the 2D world canvas for the active scene before camera transformation.
    """
    canvas = render_scene_background(scene_id, t, WIDTH, HEIGHT)
    dur = max(0.001, scene_end - scene_start)
    p = clamp((t - scene_start) / dur, 0.0, 1.0)

    if scene_id == 1:
        # "একটা জায়গায় যদি কিছু খেজুরের বিচির সাথে একটা খেজুর রাখা হয়,"
        platter_cx, platter_cy = int(WIDTH * 0.50), int(HEIGHT * 0.57)
        draw_platter(canvas, platter_cx, platter_cy, rx=370, ry=108)

        # Dry date seeds drop in one by one during 0.2s .. 1.8s
        for idx, (ox, oy, ang) in enumerate(SEED_OFFSETS):
            appear_t = 0.20 + idx * 0.16
            if t >= appear_t:
                drop_p = ease_out_back(clamp((t - appear_t) / 0.42, 0.0, 1.0))
                sy = int(lerp(platter_cy + oy - 160, platter_cy + oy, drop_p))
                draw_date_seed(canvas, platter_cx + ox, sy, scale=0.95 * drop_p, angle_deg=ang)

        if t >= 0.55:
            draw_label_pill(
                canvas,
                platter_cx - 195,
                platter_cy - 148,
                "কিছু খেজুরের বিচি (Dry Seeds)",
                w=305,
                h=50,
                bg_hex="#F4ECE1",
                border_hex="#8C735B",
                text_hex="#4A3828",
                font_pt=15,
                opacity=clamp((t - 0.55) / 0.35),
            )

        # At t=1.85s, the single plump ripe Medjool date lands with a warm golden glow
        if t >= 1.85:
            date_p = ease_out_back(clamp((t - 1.85) / 0.45, 0.0, 1.0))
            date_x = platter_cx + 175
            date_y = int(lerp(platter_cy - 210, platter_cy - 4, date_p))
            draw_ripe_date(
                canvas,
                date_x,
                date_y,
                scale=1.18 * date_p + energy * 0.06,
                glow_phase=t,
            )
            draw_label_pill(
                canvas,
                date_x + 15,
                platter_cy - 148,
                "একটা খেজুর ★ (One Ripe Date)",
                w=315,
                h=50,
                bg_hex="#FFF6DC",
                border_hex="#D4882A",
                text_hex="#6E290E",
                font_pt=15,
                opacity=clamp((t - 1.95) / 0.25),
            )

    elif scene_id == 2:
        # "আপনি কিন্তু খাওয়ার জন্য সেই খেজুরটা choose করবেন।"
        platter_cx, platter_cy = int(WIDTH * 0.48), int(HEIGHT * 0.58)
        draw_platter(canvas, platter_cx, platter_cy, rx=370, ry=108)

        # Draw rejected seeds on left
        for ox, oy, ang in SEED_OFFSETS:
            draw_date_seed(canvas, platter_cx + ox, platter_cy + oy, scale=0.92, angle_deg=ang, crossed_out=(p > 0.32))

        date_x, date_y = platter_cx + 150, platter_cy - 6
        # Hand reaches in, hovers near center, then chooses the ripe date and lifts it slightly
        reach_p = ease_in_out_cubic(clamp(p * 1.45, 0.0, 1.0))
        lift_p = ease_out_cubic(clamp((p - 0.58) / 0.42, 0.0, 1.0))
        lift_dy = int(lift_p * -34)

        # Selection rings pulsing around the chosen date
        if p > 0.42:
            ring_r = int(95 + (p - 0.42) * 110)
            cv2.circle(canvas, (date_x, date_y + lift_dy), ring_r, hex_to_bgr("#3E7C47"), 3, cv2.LINE_AA)

        draw_ripe_date(canvas, date_x, date_y + lift_dy, scale=1.22 + lift_p * 0.12, glow_phase=t)

        hand_x = int(lerp(WIDTH + 80, date_x + 28, reach_p))
        hand_y = int(lerp(HEIGHT * 0.25, date_y - 12 + lift_dy, reach_p))
        draw_reaching_hand(canvas, WIDTH + 120, int(HEIGHT * 0.36), hand_x, hand_y, pinching=(p > 0.48))

        if p > 0.45:
            draw_label_pill(
                canvas,
                date_x,
                date_y - 145 + lift_dy,
                "✓ CHOSEN • খাওয়ার জন্য নির্বাচিত",
                w=355,
                h=54,
                bg_hex="#EBF7E8",
                border_hex="#2F7A3E",
                text_hex="#1D5227",
                font_pt=16,
                opacity=clamp((p - 0.45) / 0.2),
            )

    elif scene_id == 3:
        # "কারণ আপনি নিজেও জানেন যে খেজুরের বিচিগুলো খাওয়ার উপযুক্ত না।"
        # Macro inspection board showing 4 large dry date seeds under a scanning magnifying lens
        seed_positions = [
            (310, 360, -18),
            (520, 410, 22),
            (740, 355, -10),
            (940, 405, 16),
        ]
        for idx, (sx, sy, sang) in enumerate(seed_positions):
            crossed = t >= (7.8 + idx * 0.32)
            draw_date_seed(canvas, sx, sy, scale=1.85, angle_deg=sang, crossed_out=crossed)

        # Diagnostic meters on top-left & top-right
        draw_label_pill(
            canvas,
            330,
            155,
            "পুষ্টিমান / Nutrition: 0%",
            w=310,
            h=52,
            bg_hex="#F9E5DF",
            border_hex="#B83B28",
            text_hex="#7A1F12",
            font_pt=16,
        )
        if t >= 8.0:
            draw_label_pill(
                canvas,
                880,
                155,
                "✗ খাওয়ার উপযুক্ত না (NOT EDIBLE)",
                w=390,
                h=56,
                bg_hex="#FBE2DC",
                border_hex="#C4301C",
                text_hex="#8C1B0B",
                font_pt=16,
                opacity=clamp((t - 8.0) / 0.30),
            )

        # Magnifying glass sweeping across the seeds
        lens_x = int(lerp(280, 920, ease_in_out_cubic(p)))
        lens_y = int(380 + math.sin(t * 3.0) * 18)
        draw_magnifying_glass(canvas, lens_x, lens_y, radius=118)

    elif scene_id == 4:
        # "আর আপনার ক্ষুধা নিবারণ করার potentiality একমাত্র সেই খেজুরটার মধ্যেই আছে।"
        # Left side: Glowing cross-section of the ripe date radiating golden energy streams
        date_cx, date_cy = 410, 365
        draw_ripe_date(
            canvas,
            date_cx,
            date_cy,
            scale=1.85 + energy * 0.12,
            glow_phase=t,
            cross_section=(p > 0.18),
        )
        draw_label_pill(
            canvas,
            date_cx,
            165,
            "একমাত্র খেজুরের মধ্যেই আছে ★",
            w=345,
            h=52,
            bg_hex="#FFF7DF",
            border_hex="#D18824",
            text_hex="#6B340E",
            font_pt=16,
        )

        # Golden energy particles flowing from the date into the person on the right
        char_cx, char_cy = 885, 360
        for i in range(8):
            flow_p = ((t * 0.85 + i * 0.125) % 1.0)
            px = int(lerp(date_cx + 95, char_cx - 65, flow_p))
            py = int(lerp(date_cy, char_cy + 35, flow_p) - math.sin(flow_p * math.pi) * 48)
            r_orb = int(7 + 4 * math.sin(flow_p * math.pi))
            cv2.circle(canvas, (px, py), r_orb + 4, hex_to_bgr("#FCE694"), -1, cv2.LINE_AA)
            cv2.circle(canvas, (px, py), r_orb, hex_to_bgr("#E09024"), -1, cv2.LINE_AA)

        # Person whose hunger meter fills up to 100%
        fill_lvl = clamp(0.15 + p * 0.90, 0.15, 1.0)
        draw_character(canvas, char_cx, char_cy, scale=1.22, mode="hungry_to_fed", t=t, fill_ratio=fill_lvl)
        pct = min(100, int(round(fill_lvl * 10)) * 10)
        draw_label_pill(
            canvas,
            char_cx,
            165,
            f"ক্ষুধা নিবারণ POTENTIALITY: {pct}%",
            w=375,
            h=52,
            bg_hex="#EDF7E6",
            border_hex="#3B7D3B",
            text_hex="#1E4F20",
            font_pt=15,
        )

    elif scene_id == 5:
        # "So just like this, যদি আপনার মধ্যে potentiality থাকে,"
        # Visual bridge: The glowing golden core inside a capable human surrounded by orbiting value badges
        hero_cx, hero_cy = WIDTH // 2, 395
        draw_character(canvas, hero_cx, hero_cy, scale=1.38, mode="capable", t=t)

        # Orbiting skill & inner potentiality badges
        badges = [
            ("দক্ষতা • Skill", -275, -95),
            ("জ্ঞান • Knowledge", 275, -95),
            ("মূল্যবোধ • Value", -285, 45),
            ("সক্ষমতা • Potentiality", 285, 45),
        ]
        for idx, (b_text, ox, oy) in enumerate(badges):
            appear = clamp((p - idx * 0.12) / 0.30, 0.0, 1.0)
            if appear > 0.02:
                float_dy = int(math.sin(t * 2.8 + idx * 1.4) * 9)
                bx, by = hero_cx + ox, hero_cy + oy + float_dy
                # Connecting golden filament line to hero's glowing core
                cv2.line(
                    canvas,
                    (hero_cx, hero_cy + 45),
                    (bx, by),
                    hex_to_bgr("#DFA042"),
                    2,
                    cv2.LINE_AA,
                )
                draw_label_pill(
                    canvas,
                    bx,
                    by,
                    b_text,
                    w=245,
                    h=48,
                    bg_hex="#FFF8E6",
                    border_hex="#C9872C",
                    text_hex="#4A2B0F",
                    font_pt=14,
                    opacity=appear,
                )

        draw_label_pill(
            canvas,
            hero_cx,
            125,
            "INNER POTENTIALITY • আপনার ভেতরের সক্ষমতা",
            w=470,
            h=54,
            bg_hex="#FFF3D1",
            border_hex="#C87D20",
            text_hex="#5C2E09",
            font_pt=16,
        )

    elif scene_id == 6:
        # "আর যদি আপনি যোগ্য ব্যক্তি হয়ে থাকেন, people are going to choose you।"
        # Protagonist elevated on a warm sandstone podium in the center, while crowd figures choose them
        hero_cx, hero_cy = WIDTH // 2, 330
        # Podium
        cv2.rectangle(canvas, (hero_cx - 110, 485), (hero_cx + 110, 565), hex_to_bgr("#D9C298"), -1)
        cv2.rectangle(canvas, (hero_cx - 110, 485), (hero_cx + 110, 565), hex_to_bgr("#8A6E3E"), 3)
        draw_character(canvas, hero_cx, hero_cy, scale=1.22, mode="capable", t=t)

        draw_label_pill(
            canvas,
            hero_cx,
            118,
            "★ যোগ্য ব্যক্তি • PEOPLE CHOOSE YOU ★",
            w=460,
            h=54,
            bg_hex="#ECF7E6",
            border_hex="#2E7838",
            text_hex="#1B4D22",
            font_pt=16,
        )

        # Crowd members on left & right gravitating toward the worthy person
        crowd_specs = [
            (205, 425, 0.88),
            (355, 440, 0.92),
            (925, 440, 0.92),
            (1075, 425, 0.88),
        ]
        for idx, (ccx, ccy, cscale) in enumerate(crowd_specs):
            slide = ease_out_cubic(clamp((p - idx * 0.08) / 0.45, 0.0, 1.0))
            cur_x = int(lerp(ccx + (-90 if ccx < hero_cx else 90), ccx, slide))
            draw_character(canvas, cur_x, ccy, scale=cscale, mode="crowd", t=t + idx)
            # Selection arrow pointing toward the worthy protagonist
            if p > 0.35:
                dir_sign = 1 if ccx < hero_cx else -1
                ax1 = cur_x + dir_sign * 48
                ay1 = ccy - 15
                ax2 = hero_cx - dir_sign * 95
                ay2 = hero_cy + 30
                cv2.arrowedLine(
                    canvas,
                    (ax1, ay1),
                    (ax2, ay2),
                    hex_to_bgr("#2E7838"),
                    3,
                    cv2.LINE_AA,
                    tipLength=0.18,
                )

    elif scene_id == 7:
        # "আপনার চিল্লি attention seek করতে হবে না মানুষের।"
        # Left half: Frantic shouting megaphone figure crossed out
        shouter_cx, shouter_cy = 310, 395
        draw_character(canvas, shouter_cx, shouter_cy, scale=1.18, mode="shouting", t=t)
        draw_label_pill(
            canvas,
            320,
            135,
            "✗ চিল্লি Attention Seek (Noisy & Hollow)",
            w=415,
            h=52,
            bg_hex="#FBE3DC",
            border_hex="#C43520",
            text_hex="#7D1B0D",
            font_pt=15,
        )
        # Giant red cancel slash over the megaphone shouting after t=21.5s
        if t >= 21.4:
            slash_p = ease_out_back(clamp((t - 21.4) / 0.4, 0.0, 1.0))
            r_no = int(115 * slash_p)
            ncx, ncy = shouter_cx + 45, shouter_cy - 10
            cv2.circle(canvas, (ncx, ncy), r_no, hex_to_bgr("#C42E1B"), 8, cv2.LINE_AA)
            d = int(r_no * 0.707)
            cv2.line(canvas, (ncx - d, ncy - d), (ncx + d, ncy + d), hex_to_bgr("#C42E1B"), 8, cv2.LINE_AA)

        # Right half: Calm, dignified, worthy person with natural magnetism
        calm_cx, calm_cy = 955, 390
        draw_character(canvas, calm_cx, calm_cy, scale=1.22, mode="capable", t=t)
        draw_label_pill(
            canvas,
            955,
            135,
            "✓ নীরব যোগ্যতা (Quiet Value Attracts)",
            w=405,
            h=52,
            bg_hex="#EBF6E5",
            border_hex="#337A3B",
            text_hex="#1D4F23",
            font_pt=15,
        )

    elif scene_id == 8:
        # "এখন এটা আপনার উপর depend করে।"
        # Brass decision balance scale tilting toward high value in the warm walnut study
        tilt = math.sin(t * 2.6) * 9.0 - 6.0 * p
        draw_balance_scale(canvas, WIDTH // 2, 360, tilt_deg=tilt)
        draw_label_pill(
            canvas,
            WIDTH // 2,
            125,
            "সিদ্ধান্ত আপনার • IT DEPENDS ON YOU",
            w=450,
            h=56,
            bg_hex="#FFF5DC",
            border_hex="#D49A3D",
            text_hex="#3B230D",
            font_pt=17,
        )

    elif scene_id == 9:
        # "আপনি খেজুরের বিচিগুলোর মতো হবেন, নাকি সেই খেজুরটাই হবেন।"
        # Left side (25.0s+): Hollow dry date seeds scattered in dust
        left_cx, left_cy = 320, 385
        for idx, (ox, oy, ang) in enumerate([(-85, -15, -20), (0, 22, 15), (85, -10, 32), (-35, -55, -8), (52, 55, -28)]):
            draw_date_seed(canvas, left_cx + ox, left_cy + oy, scale=1.55, angle_deg=ang, crossed_out=(t > 26.2))

        draw_label_pill(
            canvas,
            320,
            145,
            "খেজুরের বিচিগুলোর মতো? (Like Hollow Seeds?)",
            w=440,
            h=54,
            bg_hex="#F2EAE0",
            border_hex="#8A7259",
            text_hex="#4A3828",
            font_pt=15,
        )

        # Right side (26.8s+): The radiant nourishing whole date + worthy protagonist
        right_cx, right_cy = 960, 395
        emph = 1.12 if t >= 26.8 else 0.92
        draw_ripe_date(canvas, right_cx - 125, right_cy + 25, scale=1.45 * emph, glow_phase=t)
        draw_character(canvas, right_cx + 85, right_cy - 15, scale=1.18 * emph, mode="capable", t=t)

        draw_label_pill(
            canvas,
            960,
            145,
            "নাকি সেই খেজুরটাই হবেন? ★ (Or Be The Ripe Date!)",
            w=465,
            h=56,
            bg_hex="#FFF6D6",
            border_hex="#D48820",
            text_hex="#5E290A",
            font_pt=15,
        )

    return canvas


def render_hud_and_subtitles(
    canvas: np.ndarray,
    scene: dict,
    t: float,
    duration: float,
    energy: float,
):
    """
    Renders the crisp HarfBuzz-shaped Bengali + English subtitle card at the bottom
    plus a subtle audio-reactive voice waveform pill and scene progress bar.
    """
    # Find active sub-segment text
    active_bn = scene["script_bn"]
    for seg in scene.get("sub_segments", []):
        if seg["start"] <= t <= seg["end"]:
            active_bn = seg["text_bn"]
            break

    # Subtitle card container at bottom center
    card_w = 1020
    card_h = 104
    cx = WIDTH // 2
    cy = HEIGHT - 72
    x1, y1 = cx - card_w // 2, cy - card_h // 2
    x2, y2 = x1 + card_w, y1 + card_h

    draw_rounded_card(
        canvas,
        x1 + 4,
        y1 + 6,
        x2 + 4,
        y2 + 6,
        hex_to_bgr("#24170D"),
        None,
        radius=18,
        alpha=0.28,
    )
    draw_rounded_card(
        canvas,
        x1,
        y1,
        x2,
        y2,
        hex_to_bgr("#FFFDF7"),
        hex_to_bgr("#C88E4B"),
        radius=18,
        alpha=0.94,
    )

    # Audio-reactive warm amber accent bar on left inside subtitle card
    bar_h = int(22 + energy * 52)
    cv2.rectangle(
        canvas,
        (x1 + 22, cy - bar_h // 2),
        (x1 + 32, cy + bar_h // 2),
        hex_to_bgr("#D47A22"),
        -1,
    )

    # Render HarfBuzz Bengali primary line
    bn_sprite = render_html_sprite(
        active_bn,
        card_w - 90,
        54,
        font_size_pt=21,
        text_color="#2A180C",
        align="center",
    )
    composite_bgra(canvas, bn_sprite, x1 + 45, y1 + 10)

    # Render English translation subtitle underneath
    en_sprite = render_html_sprite(
        scene["script_en"],
        card_w - 90,
        36,
        font_size_pt=12,
        text_color="#7A5638",
        align="center",
    )
    composite_bgra(canvas, en_sprite, x1 + 45, y1 + 62)

    # Warm gold timeline progress bar along very bottom edge
    prog_w = int(WIDTH * clamp(t / max(0.1, duration), 0.0, 1.0))
    cv2.rectangle(canvas, (0, HEIGHT - 6), (WIDTH, HEIGHT), hex_to_bgr("#D9CBB8"), -1)
    cv2.rectangle(canvas, (0, HEIGHT - 6), (prog_w, HEIGHT), hex_to_bgr("#C87828"), -1)


def render_frame_at_time(frame_idx: int, timeline: dict) -> np.ndarray:
    """
    Renders a single complete 1280x720 BGR video frame at `frame_idx`.
    """
    fps = timeline["fps"]
    duration = timeline["duration"]
    t = min(duration, frame_idx / float(fps))
    energies = timeline["frame_energy"]
    energy = energies[min(frame_idx, len(energies) - 1)] if energies else 0.0

    # Locate active scene
    active_scene = timeline["scenes"][-1]
    for sc in timeline["scenes"]:
        if sc["start"] <= t <= sc["end"]:
            active_scene = sc
            break

    scene_id = active_scene["id"]
    s_start = active_scene["start"]
    s_end = active_scene["end"]

    # 1. Render 2D world scene
    world = render_scene_world(scene_id, t, s_start, s_end, energy)

    # 2. Compute & apply 2D virtual camera movement (zoom, pan, tilt, shake)
    cam = get_camera_state(scene_id, t, s_start, s_end)
    framed = apply_camera_transform(world, cam, frame_idx)

    # 3. Smooth cross-dissolve transition during the first 0.22s of scenes 2..9
    if scene_id > 1 and (t - s_start) < 0.22:
        alpha = clamp((t - s_start) / 0.22, 0.0, 1.0)
        prev_scene = timeline["scenes"][scene_id - 2]
        prev_world = render_scene_world(prev_scene["id"], t, prev_scene["start"], prev_scene["end"], energy)
        prev_cam = get_camera_state(prev_scene["id"], t, prev_scene["start"], prev_scene["end"])
        prev_framed = apply_camera_transform(prev_world, prev_cam, frame_idx)
        framed = cv2.addWeighted(framed, alpha, prev_framed, 1.0 - alpha, 0)

    # 4. Overlay crisp HarfBuzz Bengali + English subtitles and progress bar
    render_hud_and_subtitles(framed, active_scene, t, duration, energy)

    return framed
