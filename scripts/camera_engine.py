#!/usr/bin/env python3
"""
Script 2: camera_engine.py
Provides the 2D Virtual Camera system (zoom, pan, focal tracking, Dutch tilt, and micro-shake)
and renders 9 distinct procedural backgrounds (strictly warm, earthy, sage, terracotta,
sandstone, amber, and walnut palettes — never blue, neon, or purple).
"""

import math
import cv2
import numpy as np

WIDTH = 1280
HEIGHT = 720


def clamp(v: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, v))


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * clamp(t, 0.0, 1.0)


def ease_in_out_cubic(t: float) -> float:
    t = clamp(t, 0.0, 1.0)
    return 4 * t * t * t if t < 0.5 else 1 - pow(-2 * t + 2, 3) / 2


def ease_out_cubic(t: float) -> float:
    t = clamp(t, 0.0, 1.0)
    return 1 - pow(1 - t, 3)


def ease_out_back(t: float, s: float = 1.70158) -> float:
    t = clamp(t, 0.0, 1.0)
    t -= 1.0
    return t * t * ((s + 1) * t + s) + 1.0


def hex_to_bgr(hex_str: str):
    h = hex_str.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return (b, g, r)


def create_vertical_gradient(w: int, h: int, top_bgr, bottom_bgr) -> np.ndarray:
    ratio = np.linspace(0.0, 1.0, h, dtype=np.float32)[:, None, None]
    top = np.array(top_bgr, dtype=np.float32)[None, None, :]
    bot = np.array(bottom_bgr, dtype=np.float32)[None, None, :]
    grad = top + (bot - top) * ratio
    return np.repeat(grad.astype(np.uint8), w, axis=1)


def render_scene_background(scene_id: int, t: float, w: int = WIDTH, h: int = HEIGHT) -> np.ndarray:
    """
    Renders a unique, non-consistent background environment for each of the 9 scenes.
    Strictly avoids blue, neon, or purple tones; uses organic, warm, tactile colors.
    """
    if scene_id == 1:
        # Scene 1: Sunlit Sandstone & Warm Cedar Kitchen Table
        canvas = create_vertical_gradient(w, h, hex_to_bgr("#F7EFE4"), hex_to_bgr("#E3D0BA"))
        # Warm sunlit window diagonal beams
        overlay = canvas.copy()
        for i in range(3):
            offset = i * 240 + int(math.sin(t * 0.7 + i) * 12)
            pts = np.array(
                [
                    [120 + offset, 0],
                    [290 + offset, 0],
                    [520 + offset, h],
                    [310 + offset, h],
                ],
                np.int32,
            )
            cv2.fillPoly(overlay, [pts], hex_to_bgr("#FFF8EE"))
        cv2.addWeighted(overlay, 0.32, canvas, 0.68, 0, canvas)
        # Cedar wooden table surface at bottom
        table_y = int(h * 0.62)
        cv2.rectangle(canvas, (0, table_y), (w, h), hex_to_bgr("#C8A27E"), -1)
        cv2.line(canvas, (0, table_y), (w, table_y), hex_to_bgr("#9E7754"), 4, cv2.LINE_AA)
        for g in range(1, 5):
            gy = table_y + g * 52
            cv2.line(canvas, (0, gy), (w, gy), hex_to_bgr("#BA926D"), 2, cv2.LINE_AA)
        return canvas

    elif scene_id == 2:
        # Scene 2: Warm Terracotta & Baked Clay Courtyard
        canvas = create_vertical_gradient(w, h, hex_to_bgr("#F4DFCD"), hex_to_bgr("#D9A98A"))
        overlay = canvas.copy()
        # Subtle warm clay archways in background
        for idx, cx in enumerate([240, 640, 1040]):
            cv2.ellipse(
                overlay,
                (cx, int(h * 0.60)),
                (160, 240),
                0,
                180,
                360,
                hex_to_bgr("#E8C8B0"),
                -1,
                cv2.LINE_AA,
            )
            cv2.rectangle(overlay, (cx - 160, int(h * 0.60)), (cx + 160, h), hex_to_bgr("#E8C8B0"), -1)
        cv2.addWeighted(overlay, 0.45, canvas, 0.55, 0, canvas)
        # Terracotta surface
        cv2.rectangle(canvas, (0, int(h * 0.68)), (w, h), hex_to_bgr("#B97B57"), -1)
        cv2.line(canvas, (0, int(h * 0.68)), (w, int(h * 0.68)), hex_to_bgr("#8E5737"), 4, cv2.LINE_AA)
        return canvas

    elif scene_id == 3:
        # Scene 3: Dry Desert Khaki & Parchment Inspection Surface
        canvas = create_vertical_gradient(w, h, hex_to_bgr("#F0E9CC"), hex_to_bgr("#D2C295"))
        # Subtle botanical analysis grid lines in warm sepia
        for x in range(0, w, 64):
            cv2.line(canvas, (x, 0), (x, h), hex_to_bgr("#E2D6B1"), 1, cv2.LINE_AA)
        for y in range(0, h, 64):
            cv2.line(canvas, (0, y), (w, y), hex_to_bgr("#E2D6B1"), 1, cv2.LINE_AA)
        # Dry sand dune waves at bottom
        pts = np.array(
            [
                [0, int(h * 0.75)],
                [320, int(h * 0.70)],
                [760, int(h * 0.77)],
                [w, int(h * 0.71)],
                [w, h],
                [0, h],
            ],
            np.int32,
        )
        cv2.fillPoly(canvas, [pts], hex_to_bgr("#BFA97A"))
        return canvas

    elif scene_id == 4:
        # Scene 4: Lush Olive Grove & Golden Honey Meadow
        canvas = create_vertical_gradient(w, h, hex_to_bgr("#EEF4DF"), hex_to_bgr("#C8D8A4"))
        overlay = canvas.copy()
        # Soft sunlit golden foliage circles in distance
        for i in range(7):
            cx = 100 + i * 190 + int(math.sin(t + i) * 14)
            cy = 130 + (i % 3) * 55
            cv2.circle(overlay, (cx, cy), 95, hex_to_bgr("#DFEBBE"), -1, cv2.LINE_AA)
        cv2.addWeighted(overlay, 0.5, canvas, 0.5, 0, canvas)
        # Rolling sage meadow hills
        hill1 = np.array(
            [[0, int(h * 0.72)], [420, int(h * 0.65)], [900, int(h * 0.74)], [w, int(h * 0.68)], [w, h], [0, h]],
            np.int32,
        )
        cv2.fillPoly(canvas, [hill1], hex_to_bgr("#A3BA7A"))
        return canvas

    elif scene_id == 5:
        # Scene 5: Warm Amber Sunrise & Ochre Atelier
        canvas = create_vertical_gradient(w, h, hex_to_bgr("#FFF2DC"), hex_to_bgr("#F1C074"))
        overlay = canvas.copy()
        # Expanding concentric sunrise rings
        center = (w // 2, int(h * 0.52))
        for r in range(420, 80, -70):
            pulse = int(math.sin(t * 2.2 + r * 0.01) * 10)
            cv2.circle(overlay, center, r + pulse, hex_to_bgr("#FDE4B4"), -1, cv2.LINE_AA)
        cv2.addWeighted(overlay, 0.38, canvas, 0.62, 0, canvas)
        cv2.rectangle(canvas, (0, int(h * 0.78)), (w, h), hex_to_bgr("#C9893B"), -1)
        return canvas

    elif scene_id == 6:
        # Scene 6: Grand Travertine Cream & Antique Brass Amphitheater
        canvas = create_vertical_gradient(w, h, hex_to_bgr("#F8F3E3"), hex_to_bgr("#E0CA9B"))
        # Classical warm sandstone pillars
        for px in [110, 270, 1010, 1170]:
            cv2.rectangle(canvas, (px - 26, 60), (px + 26, int(h * 0.76)), hex_to_bgr("#EAE0C8"), -1)
            cv2.rectangle(canvas, (px - 34, 48), (px + 34, 70), hex_to_bgr("#D2BE92"), -1)
            cv2.rectangle(canvas, (px - 34, int(h * 0.74)), (px + 34, int(h * 0.77)), hex_to_bgr("#D2BE92"), -1)
        cv2.rectangle(canvas, (0, int(h * 0.77)), (w, h), hex_to_bgr("#B99556"), -1)
        return canvas

    elif scene_id == 7:
        # Scene 7: Split Contrast — Dusty Sienna Clay (Left) vs Calm Eucalyptus Sage (Right)
        left_bg = create_vertical_gradient(w // 2, h, hex_to_bgr("#EED6C8"), hex_to_bgr("#D2A892"))
        right_bg = create_vertical_gradient(w - w // 2, h, hex_to_bgr("#E7EED8"), hex_to_bgr("#C2CFA8"))
        canvas = np.hstack([left_bg, right_bg])
        # Diagonal divider accent
        cv2.line(canvas, (w // 2, 0), (w // 2, h), hex_to_bgr("#8A6E56"), 4, cv2.LINE_AA)
        cv2.rectangle(canvas, (0, int(h * 0.76)), (w // 2, h), hex_to_bgr("#B5846B"), -1)
        cv2.rectangle(canvas, (w // 2, int(h * 0.76)), (w, h), hex_to_bgr("#98AA7B"), -1)
        return canvas

    elif scene_id == 8:
        # Scene 8: Deep Roasted Walnut & Warm Espresso Gold Study
        canvas = create_vertical_gradient(w, h, hex_to_bgr("#35261B"), hex_to_bgr("#211710"))
        overlay = canvas.copy()
        # Warm golden spotlight cone from top center
        pts = np.array([[w // 2 - 90, 0], [w // 2 + 90, 0], [w // 2 + 430, h], [w // 2 - 430, h]], np.int32)
        cv2.fillPoly(overlay, [pts], hex_to_bgr("#59402A"))
        cv2.addWeighted(overlay, 0.48, canvas, 0.52, 0, canvas)
        cv2.rectangle(canvas, (0, int(h * 0.78)), (w, h), hex_to_bgr("#473221"), -1)
        cv2.line(canvas, (0, int(h * 0.78)), (w, int(h * 0.78)), hex_to_bgr("#C9964C"), 3, cv2.LINE_AA)
        return canvas

    else:
        # Scene 9: Dual-Tone Earthy Finale — Arid Ash Sand (Left) vs Radiant Golden Harvest (Right)
        left_bg = create_vertical_gradient(w // 2, h, hex_to_bgr("#E5DEC9"), hex_to_bgr("#C4B99F"))
        right_bg = create_vertical_gradient(w - w // 2, h, hex_to_bgr("#FFF1C9"), hex_to_bgr("#E5A94C"))
        canvas = np.hstack([left_bg, right_bg])
        # Warm sun glow on right half
        overlay = canvas.copy()
        cv2.circle(overlay, (int(w * 0.75), int(h * 0.42)), 230, hex_to_bgr("#FFF8DF"), -1, cv2.LINE_AA)
        cv2.addWeighted(overlay, 0.35, canvas, 0.65, 0, canvas)
        cv2.line(canvas, (w // 2, 0), (w // 2, h), hex_to_bgr("#8C6239"), 5, cv2.LINE_AA)
        return canvas


def get_camera_state(scene_id: int, t: float, scene_start: float, scene_end: float):
    """
    Computes dynamic 2D camera parameters (zoom, focus_x, focus_y, tilt_deg, shake_px)
    tailored to the narrative beat of each scene.
    """
    dur = max(0.001, scene_end - scene_start)
    p = clamp((t - scene_start) / dur, 0.0, 1.0)
    ep = ease_in_out_cubic(p)

    zoom = 1.0
    focus_x = WIDTH * 0.5
    focus_y = HEIGHT * 0.5
    tilt_deg = 0.0
    shake_px = 0.0

    if scene_id == 1:
        # Start wide on the platter, then pan right & zoom in as the single ripe date lands at t=2.15s
        if t < 2.1:
            sub_p = ease_in_out_cubic((t - scene_start) / 2.1)
            zoom = lerp(1.0, 1.08, sub_p)
            focus_x = lerp(WIDTH * 0.45, WIDTH * 0.42, sub_p)
            focus_y = lerp(HEIGHT * 0.50, HEIGHT * 0.52, sub_p)
        else:
            sub_p = ease_in_out_cubic((t - 2.1) / (scene_end - 2.1))
            zoom = lerp(1.08, 1.22, sub_p)
            focus_x = lerp(WIDTH * 0.42, WIDTH * 0.62, sub_p)
            focus_y = lerp(HEIGHT * 0.52, HEIGHT * 0.48, sub_p)

    elif scene_id == 2:
        # Follow the hand reaching from right to the chosen date & push in
        zoom = lerp(1.04, 1.24, ep)
        focus_x = lerp(WIDTH * 0.52, WIDTH * 0.63, ep)
        focus_y = lerp(HEIGHT * 0.48, HEIGHT * 0.46, ep)
        tilt_deg = math.sin(p * math.pi) * 1.2

    elif scene_id == 3:
        # Macro inspection pan across the dry seeds + subtle rejection shake at t=8.2..9.6
        zoom = lerp(1.18, 1.06, ep)
        focus_x = lerp(WIDTH * 0.38, WIDTH * 0.54, ep)
        focus_y = lerp(HEIGHT * 0.48, HEIGHT * 0.50, ep)
        if 8.1 <= t <= 9.6:
            shake_px = 4.5 * math.sin((t - 8.1) * 28.0)

    elif scene_id == 4:
        # Deep warm push-in toward the glowing nutrient core & hunger satisfaction gauge
        zoom = lerp(1.02, 1.25, ep)
        focus_x = lerp(WIDTH * 0.50, WIDTH * 0.48, ep)
        focus_y = lerp(HEIGHT * 0.52, HEIGHT * 0.45, ep)

    elif scene_id == 5:
        # Upward crane tilt & hero push-in as human potentiality awakens
        zoom = lerp(1.16, 1.03, ep)
        focus_x = WIDTH * 0.50
        focus_y = lerp(HEIGHT * 0.58, HEIGHT * 0.46, ep)

    elif scene_id == 6:
        # Start close on the worthy individual, then pull back wide to reveal people choosing them
        zoom = lerp(1.26, 1.0, ep)
        focus_x = WIDTH * 0.50
        focus_y = lerp(HEIGHT * 0.42, HEIGHT * 0.50, ep)

    elif scene_id == 7:
        # Handheld camera shake on the noisy shouting megaphone (left), then smooth pan right to calm dignity
        if t < 22.0:
            sub_p = ease_in_out_cubic((t - scene_start) / (22.0 - scene_start))
            zoom = lerp(1.16, 1.28, sub_p)
            focus_x = lerp(WIDTH * 0.44, WIDTH * 0.39, sub_p)
            focus_y = HEIGHT * 0.48
            shake_px = 5.5
            tilt_deg = math.sin(t * 22.0) * 1.2
        else:
            sub_p = ease_in_out_cubic((t - 22.0) / (scene_end - 22.0))
            zoom = lerp(1.28, 1.04, sub_p)
            focus_x = lerp(WIDTH * 0.39, WIDTH * 0.52, sub_p)
            focus_y = HEIGHT * 0.49
            shake_px = lerp(4.5, 0.0, sub_p)

    elif scene_id == 8:
        # Direct dramatic center push-in onto the decision balance scale fulcrum
        zoom = lerp(1.0, 1.24, ep)
        focus_x = WIDTH * 0.50
        focus_y = lerp(HEIGHT * 0.52, HEIGHT * 0.45, ep)

    elif scene_id == 9:
        # Pan Left to Seeds (25.0 - 26.8s) -> Pan Right to Ripe Date (26.8 - 29.2s) -> Wide Epic Pull-back (29.2 - 32.0s)
        if t < 26.8:
            sub_p = ease_in_out_cubic((t - 25.0) / 1.8)
            zoom = lerp(1.08, 1.28, sub_p)
            focus_x = lerp(WIDTH * 0.48, WIDTH * 0.39, sub_p)
            focus_y = HEIGHT * 0.47
        elif t < 29.2:
            sub_p = ease_in_out_cubic((t - 26.8) / 2.4)
            zoom = lerp(1.28, 1.26, sub_p)
            focus_x = lerp(WIDTH * 0.39, WIDTH * 0.60, sub_p)
            focus_y = HEIGHT * 0.46
        else:
            sub_p = ease_in_out_cubic((t - 29.2) / 2.8)
            zoom = lerp(1.26, 1.0, sub_p)
            focus_x = lerp(WIDTH * 0.60, WIDTH * 0.50, sub_p)
            focus_y = lerp(HEIGHT * 0.46, HEIGHT * 0.50, sub_p)

    return {
        "zoom": zoom,
        "focus_x": focus_x,
        "focus_y": focus_y,
        "tilt_deg": tilt_deg,
        "shake_px": shake_px,
    }


def apply_camera_transform(frame: np.ndarray, cam: dict, frame_idx: int) -> np.ndarray:
    """
    Applies 2D affine camera transformation (zoom around focal point, pan, tilt, and shake)
    to the world canvas while clamping the camera viewport inside canvas boundaries.
    """
    h, w = frame.shape[:2]
    zoom = max(1.0, float(cam["zoom"]))
    fx = float(cam["focus_x"])
    fy = float(cam["focus_y"])
    tilt = float(cam["tilt_deg"])
    shake = float(cam["shake_px"])

    if shake > 0.01:
        # Ensure zoom gives enough overscan margin for shake + tilt
        zoom = max(zoom, 1.06)
        sx = math.sin(frame_idx * 1.9) * shake
        sy = math.cos(frame_idx * 2.7) * shake
    else:
        sx, sy = 0.0, 0.0

    # Clamp focal center so the zoomed viewport never crosses outside [0, w] x [0, h]
    half_vw = (w * 0.5) / zoom
    half_vh = (h * 0.5) / zoom
    margin_x = max(0.0, (w * 0.5) - half_vw - abs(sx) - 6.0)
    margin_y = max(0.0, (h * 0.5) - half_vh - abs(sy) - 6.0)

    fx = clamp(fx, w * 0.5 - margin_x, w * 0.5 + margin_x)
    fy = clamp(fy, h * 0.5 - margin_y, h * 0.5 + margin_y)

    # Rotation + scale matrix around (fx, fy)
    mat = cv2.getRotationMatrix2D((fx, fy), tilt, zoom)
    mat[0, 2] += (w * 0.5 - fx) + sx
    mat[1, 2] += (h * 0.5 - fy) + sy

    transformed = cv2.warpAffine(
        frame,
        mat,
        (w, h),
        flags=cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_REPLICATE,
    )
    return transformed
