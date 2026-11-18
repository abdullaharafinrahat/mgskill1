#!/usr/bin/env python3
"""
Script 3: visual_assets.py
Provides HarfBuzz-shaped Bengali & English typography sprites (via PyMuPDF HTMLBox)
and detailed 2D illustration primitives (ripe Medjool date, dry cracked date seeds,
ceramic platter, reaching hand, magnifying lens, expressive 2D characters, megaphone,
crowd figures, and brass decision scale).
"""

import math
import cv2
import numpy as np
import pymupdf
from camera_engine import hex_to_bgr, clamp, lerp

FONT_PATH = "assets/fonts/NotoSansBengali.ttf"
_TEXT_CACHE = {}


def render_html_sprite(
    html_body: str,
    width: int,
    height: int,
    font_size_pt: int = 22,
    text_color: str = "#2A1B10",
    align: str = "center",
) -> np.ndarray:
    """
    Renders complex HarfBuzz-shaped Bengali + English HTML text into an RGBA numpy array.
    """
    width = max(80, int(width))
    height = max(28, int(height))
    cache_key = (html_body, width, height, font_size_pt, text_color, align)
    if cache_key in _TEXT_CACHE:
        return _TEXT_CACHE[cache_key]

    doc = pymupdf.open()
    page = doc.new_page(width=width, height=height)
    css = f"""
    @font-face {{
        font-family: 'NotoBengali';
        src: url('{FONT_PATH}');
    }}
    body {{
        font-family: 'NotoBengali', sans-serif;
        font-size: {font_size_pt}pt;
        font-weight: bold;
        color: {text_color};
        text-align: {align};
        line-height: 1.28;
        margin: 0;
        padding: 0;
    }}
    .hl {{
        color: #B64518;
        font-weight: bold;
    }}
    .hl-gold {{
        color: #E09124;
        font-weight: bold;
    }}
    .hl-green {{
        color: #2B6E36;
        font-weight: bold;
    }}
    """
    page.insert_htmlbox(
        pymupdf.Rect(4, 2, width - 4, height - 2),
        f"<body>{html_body}</body>",
        css=css,
    )
    pix = page.get_pixmap(alpha=True)
    arr = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, 4).copy()
    doc.close()
    # Convert RGBA to BGRA for OpenCV
    bgra = arr[:, :, [2, 1, 0, 3]]
    _TEXT_CACHE[cache_key] = bgra
    return bgra


def composite_bgra(canvas: np.ndarray, sprite: np.ndarray, x: int, y: int, opacity: float = 1.0):
    """
    Alpha-blends a BGRA sprite onto a BGR canvas at top-left position (x, y).
    """
    ch, cw = canvas.shape[:2]
    sh, sw = sprite.shape[:2]

    x1 = max(0, x)
    y1 = max(0, y)
    x2 = min(cw, x + sw)
    y2 = min(ch, y + sh)
    if x2 <= x1 or y2 <= y1:
        return

    sx1 = x1 - x
    sy1 = y1 - y
    sx2 = sx1 + (x2 - x1)
    sy2 = sy1 + (y2 - y1)

    roi = canvas[y1:y2, x1:x2].astype(np.float32)
    sub = sprite[sy1:sy2, sx1:sx2].astype(np.float32)
    alpha = (sub[:, :, 3:4] / 255.0) * clamp(opacity, 0.0, 1.0)

    blended = sub[:, :, :3] * alpha + roi * (1.0 - alpha)
    canvas[y1:y2, x1:x2] = blended.astype(np.uint8)


def draw_rounded_card(
    canvas: np.ndarray,
    x1: int,
    y1: int,
    x2: int,
    y2: int,
    fill_bgr,
    border_bgr=None,
    radius: int = 18,
    alpha: float = 0.92,
):
    if alpha <= 0.02:
        return
    overlay = canvas.copy()
    cv2.rectangle(overlay, (x1 + radius, y1), (x2 - radius, y2), fill_bgr, -1)
    cv2.rectangle(overlay, (x1, y1 + radius), (x2, y2 - radius), fill_bgr, -1)
    for cx, cy in [
        (x1 + radius, y1 + radius),
        (x2 - radius, y1 + radius),
        (x1 + radius, y2 - radius),
        (x2 - radius, y2 - radius),
    ]:
        cv2.circle(overlay, (cx, cy), radius, fill_bgr, -1, cv2.LINE_AA)
    if border_bgr is not None:
        cv2.rectangle(overlay, (x1 + 3, y1 + 3), (x2 - 3, y2 - 3), border_bgr, 2, cv2.LINE_AA)
    cv2.addWeighted(overlay, alpha, canvas, 1.0 - alpha, 0, canvas)


def draw_label_pill(
    canvas: np.ndarray,
    cx: int,
    cy: int,
    text_html: str,
    w: int = 280,
    h: int = 54,
    bg_hex: str = "#FFF8EB",
    border_hex: str = "#C88A4B",
    text_hex: str = "#2C1D11",
    font_pt: int = 18,
    opacity: float = 1.0,
):
    if opacity <= 0.02:
        return
    x1, y1 = int(cx - w // 2), int(cy - h // 2)
    x2, y2 = x1 + w, y1 + h
    draw_rounded_card(
        canvas,
        x1 + 4,
        y1 + 5,
        x2 + 4,
        y2 + 5,
        hex_to_bgr("#3E2B1C"),
        None,
        radius=14,
        alpha=0.22 * opacity,
    )
    draw_rounded_card(
        canvas,
        x1,
        y1,
        x2,
        y2,
        hex_to_bgr(bg_hex),
        hex_to_bgr(border_hex),
        radius=14,
        alpha=0.95 * opacity,
    )
    sprite = render_html_sprite(text_html, w - 16, h - 10, font_size_pt=font_pt, text_color=text_hex)
    composite_bgra(canvas, sprite, x1 + 8, y1 + 11, opacity=opacity)


def draw_platter(canvas: np.ndarray, cx: int, cy: int, rx: int = 340, ry: int = 95):
    """
    Draws a handcrafted ceramic & antique brass serving platter on the table.
    """
    # Soft drop shadow
    shadow = canvas.copy()
    cv2.ellipse(shadow, (cx + 8, cy + 18), (rx + 12, ry + 8), 0, 0, 360, hex_to_bgr("#5A3E28"), -1, cv2.LINE_AA)
    cv2.addWeighted(shadow, 0.35, canvas, 0.65, 0, canvas)
    # Outer brass rim
    cv2.ellipse(canvas, (cx, cy), (rx, ry), 0, 0, 360, hex_to_bgr("#C89B57"), -1, cv2.LINE_AA)
    cv2.ellipse(canvas, (cx, cy), (rx, ry), 0, 0, 360, hex_to_bgr("#8F652D"), 3, cv2.LINE_AA)
    # Inner warm cream ceramic basin
    cv2.ellipse(canvas, (cx, cy - 3), (int(rx * 0.88), int(ry * 0.80)), 0, 0, 360, hex_to_bgr("#F5EAD8"), -1, cv2.LINE_AA)
    cv2.ellipse(canvas, (cx, cy - 3), (int(rx * 0.88), int(ry * 0.80)), 0, 0, 360, hex_to_bgr("#D7C2A3"), 2, cv2.LINE_AA)


def draw_date_seed(
    canvas: np.ndarray,
    cx: int,
    cy: int,
    scale: float = 1.0,
    angle_deg: float = 15.0,
    crossed_out: bool = False,
):
    """
    Draws a dry, hard, rough date seed (খেজুরের বিচি) with longitudinal furrow and cracks.
    """
    rx = int(34 * scale)
    ry = int(15 * scale)
    if rx < 2 or ry < 2:
        return

    # Ground shadow
    cv2.ellipse(
        canvas,
        (cx + 3, cy + int(7 * scale)),
        (rx, ry),
        angle_deg,
        0,
        360,
        hex_to_bgr("#6E5844"),
        -1,
        cv2.LINE_AA,
    )
    # Dry gray-taupe body
    cv2.ellipse(
        canvas,
        (cx, cy),
        (rx, ry),
        angle_deg,
        0,
        360,
        hex_to_bgr("#9E8B76"),
        -1,
        cv2.LINE_AA,
    )
    # Darker woody outline
    cv2.ellipse(
        canvas,
        (cx, cy),
        (rx, ry),
        angle_deg,
        0,
        360,
        hex_to_bgr("#5C4B3B"),
        max(1, int(2 * scale)),
        cv2.LINE_AA,
    )
    # Center longitudinal seed crease/groove
    rad = math.radians(angle_deg)
    dx = int(math.cos(rad) * (rx * 0.78))
    dy = int(math.sin(rad) * (rx * 0.78))
    cv2.line(
        canvas,
        (cx - dx, cy - dy),
        (cx + dx, cy + dy),
        hex_to_bgr("#4A3A2C"),
        max(1, int(2.5 * scale)),
        cv2.LINE_AA,
    )
    # Small dry cracks
    nx = int(-math.sin(rad) * (ry * 0.55))
    ny = int(math.cos(rad) * (ry * 0.55))
    cv2.line(canvas, (cx, cy), (cx + nx, cy + ny), hex_to_bgr("#5C4B3B"), 1, cv2.LINE_AA)

    if crossed_out:
        r_cross = int(32 * scale)
        cv2.line(
            canvas,
            (cx - r_cross, cy - r_cross),
            (cx + r_cross, cy + r_cross),
            hex_to_bgr("#C83E2B"),
            max(2, int(4 * scale)),
            cv2.LINE_AA,
        )
        cv2.line(
            canvas,
            (cx + r_cross, cy - r_cross),
            (cx - r_cross, cy + r_cross),
            hex_to_bgr("#C83E2B"),
            max(2, int(4 * scale)),
            cv2.LINE_AA,
        )


def draw_ripe_date(
    canvas: np.ndarray,
    cx: int,
    cy: int,
    scale: float = 1.0,
    glow_phase: float = 0.0,
    cross_section: bool = False,
):
    """
    Draws a rich, plump, glossy amber-mahogany Medjool date (খেজুর) with golden aura,
    natural leaf bed, specular shine, and optional glowing nutrient core.
    """
    rx = int(68 * scale)
    ry = int(42 * scale)
    if rx < 3 or ry < 3:
        return

    # Golden radiant aura behind the ripe date
    overlay = canvas.copy()
    pulse = int(math.sin(glow_phase * 3.5) * 10 * scale)
    for r_mult, col_hex in [(1.85, "#F9E29C"), (1.42, "#F2C15A")]:
        cv2.circle(
            overlay,
            (cx, cy),
            max(10, int(rx * r_mult) + pulse),
            hex_to_bgr(col_hex),
            -1,
            cv2.LINE_AA,
        )
    cv2.addWeighted(overlay, 0.36, canvas, 0.64, 0, canvas)

    # Fresh olive-green palm leaf cushion beneath the date
    leaf_pts = np.array(
        [
            [cx - int(rx * 1.25), cy + int(ry * 0.35)],
            [cx - int(rx * 0.3), cy - int(ry * 0.65)],
            [cx + int(rx * 1.25), cy + int(ry * 0.25)],
            [cx + int(rx * 0.2), cy + int(ry * 0.95)],
        ],
        np.int32,
    )
    cv2.fillPoly(canvas, [leaf_pts], hex_to_bgr("#6A8E4E"))
    cv2.polylines(canvas, [leaf_pts], True, hex_to_bgr("#476332"), 2, cv2.LINE_AA)

    # Drop shadow
    cv2.ellipse(
        canvas,
        (cx + 5, cy + int(14 * scale)),
        (rx, int(ry * 0.85)),
        -6,
        0,
        360,
        hex_to_bgr("#4A2B18"),
        -1,
        cv2.LINE_AA,
    )

    # Main plump mahogany-amber date fruit body
    cv2.ellipse(
        canvas,
        (cx, cy),
        (rx, ry),
        -6,
        0,
        360,
        hex_to_bgr("#7A2E18"),
        -1,
        cv2.LINE_AA,
    )
    # Inner rich caramel flesh shading
    cv2.ellipse(
        canvas,
        (cx - int(4 * scale), cy - int(4 * scale)),
        (int(rx * 0.86), int(ry * 0.78)),
        -6,
        0,
        360,
        hex_to_bgr("#9B3F21"),
        -1,
        cv2.LINE_AA,
    )
    # Deep outline
    cv2.ellipse(
        canvas,
        (cx, cy),
        (rx, ry),
        -6,
        0,
        360,
        hex_to_bgr("#3E1408"),
        max(2, int(3 * scale)),
        cv2.LINE_AA,
    )

    if cross_section:
        # Glowing golden honey-amber nutrient interior reveal
        cv2.ellipse(
            canvas,
            (cx, cy),
            (int(rx * 0.68), int(ry * 0.62)),
            -6,
            0,
            360,
            hex_to_bgr("#E89928"),
            -1,
            cv2.LINE_AA,
        )
        cv2.ellipse(
            canvas,
            (cx, cy),
            (int(rx * 0.44), int(ry * 0.38)),
            -6,
            0,
            360,
            hex_to_bgr("#FDE08D"),
            -1,
            cv2.LINE_AA,
        )
    else:
        # Glossy caramel specular highlight arc along top-left
        cv2.ellipse(
            canvas,
            (cx - int(12 * scale), cy - int(12 * scale)),
            (int(rx * 0.55), int(ry * 0.26)),
            -12,
            0,
            360,
            hex_to_bgr("#D97941"),
            -1,
            cv2.LINE_AA,
        )
        cv2.ellipse(
            canvas,
            (cx - int(18 * scale), cy - int(15 * scale)),
            (int(rx * 0.28), int(ry * 0.12)),
            -12,
            0,
            360,
            hex_to_bgr("#F7C58E"),
            -1,
            cv2.LINE_AA,
        )

    # Golden stem calyx cap on the right tip of the date
    cap_x = cx + int(rx * 0.92)
    cap_y = cy - int(ry * 0.10)
    cv2.circle(canvas, (cap_x, cap_y), max(4, int(11 * scale)), hex_to_bgr("#D9A043"), -1, cv2.LINE_AA)
    cv2.circle(canvas, (cap_x, cap_y), max(4, int(11 * scale)), hex_to_bgr("#7A4F16"), 2, cv2.LINE_AA)

    # Warm floating sparkle stars around the ripe date
    for idx, (ox, oy) in enumerate([(-rx - 18, -ry + 4), (rx + 22, -ry - 10), (0, -ry - 26)]):
        sp_r = int((6 + 3 * math.sin(glow_phase * 4.0 + idx * 2.1)) * scale)
        if sp_r > 2:
            sx, sy = cx + int(ox), cy + int(oy)
            cv2.line(canvas, (sx - sp_r, sy), (sx + sp_r, sy), hex_to_bgr("#E09A2B"), 2, cv2.LINE_AA)
            cv2.line(canvas, (sx, sy - sp_r), (sx, sy + sp_r), hex_to_bgr("#E09A2B"), 2, cv2.LINE_AA)


def draw_reaching_hand(
    canvas: np.ndarray,
    start_x: int,
    start_y: int,
    hand_x: int,
    hand_y: int,
    pinching: bool = False,
):
    """
    Draws an expressive stylized human forearm, sleeve, and hand reaching toward a target.
    """
    # Forearm / warm olive-ochre sleeve
    arm_pts = np.array(
        [
            [start_x, start_y - 38],
            [start_x, start_y + 38],
            [hand_x + 48, hand_y + 24],
            [hand_x + 48, hand_y - 24],
        ],
        np.int32,
    )
    cv2.fillPoly(canvas, [arm_pts], hex_to_bgr("#6E7E48"))
    cv2.polylines(canvas, [arm_pts], True, hex_to_bgr("#3E4A24"), 3, cv2.LINE_AA)

    # Cuff
    cv2.rectangle(canvas, (hand_x + 38, hand_y - 26), (hand_x + 56, hand_y + 26), hex_to_bgr("#F2E5D0"), -1)
    cv2.rectangle(canvas, (hand_x + 38, hand_y - 26), (hand_x + 56, hand_y + 26), hex_to_bgr("#4A3520"), 2)

    # Warm skin palm & fingers
    skin_bgr = hex_to_bgr("#E0A97B")
    outline_bgr = hex_to_bgr("#5C3A21")
    cv2.ellipse(canvas, (hand_x + 12, hand_y), (32, 22), -10, 0, 360, skin_bgr, -1, cv2.LINE_AA)
    cv2.ellipse(canvas, (hand_x + 12, hand_y), (32, 22), -10, 0, 360, outline_bgr, 2, cv2.LINE_AA)

    # Thumb & index finger pinching/selecting
    spread = 6 if pinching else 18
    # Index finger
    cv2.ellipse(canvas, (hand_x - 16, hand_y - spread), (22, 8), -15, 0, 360, skin_bgr, -1, cv2.LINE_AA)
    cv2.ellipse(canvas, (hand_x - 16, hand_y - spread), (22, 8), -15, 0, 360, outline_bgr, 2, cv2.LINE_AA)
    # Thumb
    cv2.ellipse(canvas, (hand_x - 12, hand_y + spread), (19, 8), 20, 0, 360, skin_bgr, -1, cv2.LINE_AA)
    cv2.ellipse(canvas, (hand_x - 12, hand_y + spread), (19, 8), 20, 0, 360, outline_bgr, 2, cv2.LINE_AA)


def draw_magnifying_glass(canvas: np.ndarray, cx: int, cy: int, radius: int = 115):
    """
    Draws an inspection magnifying lens with antique brass rim and warm glass tint.
    """
    # Handle extending down-right
    hx1, hy1 = cx + int(radius * 0.70), cy + int(radius * 0.70)
    hx2, hy2 = hx1 + 110, hy1 + 110
    cv2.line(canvas, (hx1, hy1), (hx2, hy2), hex_to_bgr("#4A2F1B"), 22, cv2.LINE_AA)
    cv2.line(canvas, (hx1, hy1), (hx2, hy2), hex_to_bgr("#7A5030"), 14, cv2.LINE_AA)

    # Warm glass lens highlight
    overlay = canvas.copy()
    cv2.circle(overlay, (cx, cy), radius, hex_to_bgr("#FFFDF4"), -1, cv2.LINE_AA)
    cv2.addWeighted(overlay, 0.28, canvas, 0.72, 0, canvas)

    # Brass rim
    cv2.circle(canvas, (cx, cy), radius, hex_to_bgr("#C99646"), 12, cv2.LINE_AA)
    cv2.circle(canvas, (cx, cy), radius + 6, hex_to_bgr("#5E4119"), 2, cv2.LINE_AA)
    cv2.circle(canvas, (cx, cy), radius - 6, hex_to_bgr("#5E4119"), 2, cv2.LINE_AA)

    # Glint arc
    cv2.ellipse(
        canvas,
        (cx - int(radius * 0.35), cy - int(radius * 0.35)),
        (int(radius * 0.35), int(radius * 0.16)),
        -40,
        0,
        180,
        hex_to_bgr("#FFFFFF"),
        4,
        cv2.LINE_AA,
    )


def draw_character(
    canvas: np.ndarray,
    cx: int,
    cy: int,
    scale: float = 1.0,
    mode: str = "capable",
    t: float = 0.0,
    fill_ratio: float = 1.0,
):
    """
    Draws expressive 2D characters for the story:
    - 'hungry_to_fed': Shows stomach nourishment & energy rising from the ripe date.
    - 'capable': Calm, skilled, magnetic protagonist with glowing inner potentiality.
    - 'shouting': Frantic, noisy attention-seeker jumping with a giant megaphone.
    - 'crowd': Supportive people turning toward and choosing the worthy protagonist.
    """
    head_r = int(38 * scale)
    torso_w = int(62 * scale)
    torso_h = int(115 * scale)

    if mode == "shouting":
        # Jumping frantic motion
        bounce = int(abs(math.sin(t * 14.0)) * 22 * scale)
        cy = cy - bounce

    # Soft ground shadow
    cv2.ellipse(
        canvas,
        (cx, cy + torso_h + int(35 * scale)),
        (int(58 * scale), int(14 * scale)),
        0,
        0,
        360,
        hex_to_bgr("#6E5842"),
        -1,
        cv2.LINE_AA,
    )

    # Choose outfit color (warm earthy tones, zero blue/neon/purple)
    if mode == "shouting":
        shirt_hex = "#A67C68"  # dull dusty clay-brown
    elif mode == "crowd":
        shirt_hex = "#849468"  # muted sage
    else:
        shirt_hex = "#3E6B48"  # rich forest olive green

    # Torso rounded trapezoid
    torso_pts = np.array(
        [
            [cx - int(torso_w * 0.78), cy - int(10 * scale)],
            [cx + int(torso_w * 0.78), cy - int(10 * scale)],
            [cx + torso_w, cy + torso_h],
            [cx - torso_w, cy + torso_h],
        ],
        np.int32,
    )
    cv2.fillPoly(canvas, [torso_pts], hex_to_bgr(shirt_hex))
    cv2.polylines(canvas, [torso_pts], True, hex_to_bgr("#271A10"), max(2, int(3 * scale)), cv2.LINE_AA)

    # Neck & Head
    head_cy = cy - int(58 * scale)
    cv2.rectangle(
        canvas,
        (cx - int(12 * scale), head_cy + int(22 * scale)),
        (cx + int(12 * scale), cy - int(4 * scale)),
        hex_to_bgr("#DBA374"),
        -1,
    )
    cv2.circle(canvas, (cx, head_cy), head_r, hex_to_bgr("#E5B183"), -1, cv2.LINE_AA)
    cv2.circle(canvas, (cx, head_cy), head_r, hex_to_bgr("#2B1A0E"), max(2, int(3 * scale)), cv2.LINE_AA)

    # Warm dark-brown hair cap
    cv2.ellipse(
        canvas,
        (cx, head_cy - int(10 * scale)),
        (head_r + 2, int(head_r * 0.78)),
        0,
        180,
        360,
        hex_to_bgr("#2D1D12"),
        -1,
        cv2.LINE_AA,
    )

    # Facial expression
    eye_y = head_cy - int(4 * scale)
    eye_dx = int(13 * scale)
    if mode == "shouting":
        # Strained squinted eyes + wide shouting mouth + sweat drops
        cv2.line(canvas, (cx - eye_dx - 5, eye_y - 4), (cx - eye_dx + 5, eye_y + 2), hex_to_bgr("#2B1A0E"), 3, cv2.LINE_AA)
        cv2.line(canvas, (cx + eye_dx + 5, eye_y - 4), (cx + eye_dx - 5, eye_y + 2), hex_to_bgr("#2B1A0E"), 3, cv2.LINE_AA)
        cv2.ellipse(
            canvas,
            (cx + int(8 * scale), head_cy + int(14 * scale)),
            (int(14 * scale), int(11 * scale)),
            0,
            0,
            360,
            hex_to_bgr("#8F2418"),
            -1,
            cv2.LINE_AA,
        )
        # Giant megaphone attached to mouth
        mega_pts = np.array(
            [
                [cx + int(20 * scale), head_cy + int(8 * scale)],
                [cx + int(115 * scale), head_cy - int(32 * scale)],
                [cx + int(115 * scale), head_cy + int(48 * scale)],
                [cx + int(20 * scale), head_cy + int(22 * scale)],
            ],
            np.int32,
        )
        cv2.fillPoly(canvas, [mega_pts], hex_to_bgr("#D95338"))
        cv2.polylines(canvas, [mega_pts], True, hex_to_bgr("#4A190E"), 3, cv2.LINE_AA)
        # Jagged noisy soundwaves coming out of megaphone
        for w_idx in range(3):
            wx = cx + int((130 + w_idx * 28) * scale)
            wy = head_cy + int(8 * scale)
            r_arc = int((22 + w_idx * 16) * scale)
            cv2.ellipse(canvas, (wx - 20, wy), (r_arc, r_arc), 0, -45, 45, hex_to_bgr("#C83722"), 3, cv2.LINE_AA)
    else:
        # Calm, confident, warm smile
        cv2.circle(canvas, (cx - eye_dx, eye_y), max(2, int(4 * scale)), hex_to_bgr("#2B1A0E"), -1, cv2.LINE_AA)
        cv2.circle(canvas, (cx + eye_dx, eye_y), max(2, int(4 * scale)), hex_to_bgr("#2B1A0E"), -1, cv2.LINE_AA)
        cv2.ellipse(
            canvas,
            (cx, head_cy + int(10 * scale)),
            (int(12 * scale), int(7 * scale)),
            0,
            15,
            165,
            hex_to_bgr("#2B1A0E"),
            max(2, int(2.5 * scale)),
            cv2.LINE_AA,
        )

    # Mode-specific chest visual indicators
    if mode == "hungry_to_fed":
        # Stomach / Energy battery inside torso filling up from red/empty to golden-green
        box_w = int(42 * scale)
        box_h = int(64 * scale)
        bx1, by1 = cx - box_w, cy + int(14 * scale)
        bx2, by2 = cx + box_w, by1 + box_h
        cv2.rectangle(canvas, (bx1, by1), (bx2, by2), hex_to_bgr("#23180F"), -1)
        fill_h = int((box_h - 6) * clamp(fill_ratio, 0.05, 1.0))
        fill_col = hex_to_bgr("#D98A2B") if fill_ratio < 0.5 else hex_to_bgr("#6CA344")
        cv2.rectangle(canvas, (bx1 + 3, by2 - 3 - fill_h), (bx2 - 3, by2 - 3), fill_col, -1)
        cv2.rectangle(canvas, (bx1, by1), (bx2, by2), hex_to_bgr("#F2D08B"), 2, cv2.LINE_AA)

    elif mode == "capable":
        # Glowing golden star/core of Potentiality in the chest
        core_y = cy + int(42 * scale)
        pulse_r = int((22 + 5 * math.sin(t * 4.5)) * scale)
        overlay = canvas.copy()
        cv2.circle(overlay, (cx, core_y), int(pulse_r * 1.7), hex_to_bgr("#FCE29C"), -1, cv2.LINE_AA)
        cv2.addWeighted(overlay, 0.45, canvas, 0.55, 0, canvas)
        cv2.circle(canvas, (cx, core_y), pulse_r, hex_to_bgr("#F2A92C"), -1, cv2.LINE_AA)
        cv2.circle(canvas, (cx, core_y), int(pulse_r * 0.55), hex_to_bgr("#FFF8E0"), -1, cv2.LINE_AA)


def draw_balance_scale(canvas: np.ndarray, cx: int, cy: int, tilt_deg: float = -12.0):
    """
    Draws an ornate antique brass balance scale weighing dry seeds (left) vs the ripe date (right).
    """
    # Base pedestal
    cv2.ellipse(canvas, (cx, cy + 165), (125, 24), 0, 0, 360, hex_to_bgr("#8A6228"), -1, cv2.LINE_AA)
    cv2.ellipse(canvas, (cx, cy + 160), (105, 18), 0, 0, 360, hex_to_bgr("#C9964C"), -1, cv2.LINE_AA)
    # Central pillar
    cv2.rectangle(canvas, (cx - 12, cy - 110), (cx + 12, cy + 160), hex_to_bgr("#B8843B"), -1)
    cv2.rectangle(canvas, (cx - 12, cy - 110), (cx + 12, cy + 160), hex_to_bgr("#6E4B1A"), 2)

    # Fulcrum wheel
    fulcrum_y = cy - 95
    cv2.circle(canvas, (cx, fulcrum_y), 24, hex_to_bgr("#E5B567"), -1, cv2.LINE_AA)
    cv2.circle(canvas, (cx, fulcrum_y), 24, hex_to_bgr("#6E4B1A"), 3, cv2.LINE_AA)

    # Tilted crossbeam
    rad = math.radians(tilt_deg)
    arm_len = 240
    lx = int(cx - math.cos(rad) * arm_len)
    ly = int(fulcrum_y - math.sin(rad) * arm_len)
    rx = int(cx + math.cos(rad) * arm_len)
    ry = int(fulcrum_y + math.sin(rad) * arm_len)
    cv2.line(canvas, (lx, ly), (rx, ry), hex_to_bgr("#DDA853"), 10, cv2.LINE_AA)
    cv2.line(canvas, (lx, ly), (rx, ry), hex_to_bgr("#6E4B1A"), 2, cv2.LINE_AA)

    # Left & Right hanging pans
    for px, py in [(lx, ly), (rx, ry)]:
        pan_y = py + 115
        cv2.line(canvas, (px, py), (px - 58, pan_y), hex_to_bgr("#9E7432"), 2, cv2.LINE_AA)
        cv2.line(canvas, (px, py), (px + 58, pan_y), hex_to_bgr("#9E7432"), 2, cv2.LINE_AA)
        cv2.ellipse(canvas, (px, pan_y), (72, 18), 0, 0, 180, hex_to_bgr("#D4A152"), -1, cv2.LINE_AA)
        cv2.ellipse(canvas, (px, pan_y), (72, 18), 0, 0, 360, hex_to_bgr("#6E4B1A"), 2, cv2.LINE_AA)

    # Left pan carries dry seeds; Right pan carries the glowing ripe date
    draw_date_seed(canvas, lx - 22, ly + 102, scale=0.72, angle_deg=-12)
    draw_date_seed(canvas, lx + 18, ly + 105, scale=0.72, angle_deg=18)
    draw_ripe_date(canvas, rx, ry + 88, scale=0.75, glow_phase=tilt_deg * 0.2)
