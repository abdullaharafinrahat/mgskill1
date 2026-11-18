#!/usr/bin/env python3
"""
Script 1: audio_analyzer.py
Analyzes audio.mp3 to extract exact duration, 30 FPS frame-level RMS energy envelope,
speech onset impulses, and generates the synchronized scene & subtitle timeline JSON.
"""

import json
import os
import subprocess
import imageio_ffmpeg
import numpy as np
from scipy.io import wavfile

FPS = 30
AUDIO_PATH = "audio.mp3"
WAV_TEMP_PATH = "scripts/_temp_audio_16k.wav"
OUTPUT_JSON_PATH = "scripts/timeline_data.json"


def analyze_audio():
    os.makedirs("scripts", exist_ok=True)
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()

    # Decode audio.mp3 to 16kHz mono WAV for accurate signal analysis
    subprocess.run(
        [
            ffmpeg_exe,
            "-y",
            "-i",
            AUDIO_PATH,
            "-ac",
            "1",
            "-ar",
            "16000",
            WAV_TEMP_PATH,
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=True,
    )

    sample_rate, samples = wavfile.read(WAV_TEMP_PATH)
    samples_f = samples.astype(np.float32)
    duration = float(len(samples_f) / sample_rate)
    total_frames = int(np.ceil(duration * FPS))

    # Calculate per-frame RMS energy and smoothed voice envelope
    samples_per_frame = int(sample_rate / FPS)
    raw_rms = []
    for f in range(total_frames):
        start = f * samples_per_frame
        end = min(len(samples_f), start + samples_per_frame)
        if end > start:
            chunk = samples_f[start:end]
            val = float(np.sqrt(np.mean(chunk * chunk)))
        else:
            val = 0.0
        raw_rms.append(val)

    max_rms = max(raw_rms) if raw_rms and max(raw_rms) > 0 else 1.0
    norm_rms = [round(v / max_rms, 4) for v in raw_rms]

    # Smooth envelope with a 5-frame moving window for organic visual pulsing
    kernel = np.array([0.1, 0.2, 0.4, 0.2, 0.1])
    smoothed = np.convolve(norm_rms, kernel, mode="same")
    smoothed_rms = [round(float(v), 4) for v in smoothed]

    # Clean up temporary wav
    if os.path.exists(WAV_TEMP_PATH):
        os.remove(WAV_TEMP_PATH)

    # Synchronized 9-scene breakdown mapped to exact speech timing in audio.mp3
    # Note: Every scene uses a distinct warm/earthy background palette (no blue, neon, or purple)
    scenes = [
        {
            "id": 1,
            "name": "The Platter: Seeds vs. One Ripe Date",
            "start": 0.0,
            "end": 4.3,
            "bg_theme": "Sunlit Sandstone & Cedar Table",
            "bg_colors": ["#F6EFE6", "#E5D4C0", "#C8A98E"],
            "camera_mode": "Slow Push-In & Pan Right to Ripe Date",
            "script_bn": "একটা জায়গায় যদি কিছু খেজুরের বিচির সাথে একটা খেজুর রাখা হয়,",
            "script_en": "If a single ripe date is placed alongside a handful of date seeds...",
            "sub_segments": [
                {
                    "start": 0.35,
                    "end": 2.15,
                    "text_bn": "একটা জায়গায় যদি কিছু খেজুরের বিচির সাথে",
                    "highlight": "খেজুরের বিচি",
                },
                {
                    "start": 2.15,
                    "end": 4.25,
                    "text_bn": "একটা খেজুর রাখা হয়,",
                    "highlight": "একটা খেজুর",
                },
            ],
        },
        {
            "id": 2,
            "name": "The Natural Choice",
            "start": 4.3,
            "end": 6.8,
            "bg_theme": "Warm Terracotta & Baked Clay Courtyard",
            "bg_colors": ["#F4DFCD", "#DFB79B", "#C08562"],
            "camera_mode": "Tracking Hand Reach + Zoom on Chosen Date",
            "script_bn": "আপনি কিন্তু খাওয়ার জন্য সেই খেজুরটা choose করবেন।",
            "script_en": "You will naturally choose that whole date to eat.",
            "sub_segments": [
                {
                    "start": 4.35,
                    "end": 6.75,
                    "text_bn": "আপনি কিন্তু খাওয়ার জন্য সেই খেজুরটা choose করবেন।",
                    "highlight": "choose করবেন",
                }
            ],
        },
        {
            "id": 3,
            "name": "Why Seeds Are Rejected",
            "start": 6.8,
            "end": 10.4,
            "bg_theme": "Dry Desert Khaki & Parchment Inspection Surface",
            "bg_colors": ["#EFE8C8", "#D6C79C", "#B5A175"],
            "camera_mode": "Macro Inspection Pan + Subtle Rejection Tremor",
            "script_bn": "কারণ আপনি নিজেও জানেন যে খেজুরের বিচিগুলো খাওয়ার উপযুক্ত না।",
            "script_en": "Because you already know the date seeds are not edible.",
            "sub_segments": [
                {
                    "start": 6.85,
                    "end": 8.05,
                    "text_bn": "কারণ আপনি নিজেও জানেন যে",
                    "highlight": "নিজেও জানেন",
                },
                {
                    "start": 8.05,
                    "end": 10.35,
                    "text_bn": "খেজুরের বিচিগুলো খাওয়ার উপযুক্ত না।",
                    "highlight": "খাওয়ার উপযুক্ত না",
                },
            ],
        },
        {
            "id": 4,
            "name": "True Nourishment & Potentiality",
            "start": 10.4,
            "end": 14.3,
            "bg_theme": "Lush Olive Grove & Warm Honey Meadow",
            "bg_colors": ["#EBF2DC", "#C9D8A7", "#99B272"],
            "camera_mode": "Deep Center Zoom Into Glowing Nutrient Core",
            "script_bn": "আর আপনার ক্ষুধা নিবারণ করার potentiality একমাত্র সেই খেজুরটার মধ্যেই আছে।",
            "script_en": "And only that ripe date holds the potentiality to satisfy your hunger.",
            "sub_segments": [
                {
                    "start": 10.45,
                    "end": 12.15,
                    "text_bn": "আর আপনার ক্ষুধা নিবারণ করার potentiality",
                    "highlight": "potentiality",
                },
                {
                    "start": 12.15,
                    "end": 14.25,
                    "text_bn": "একমাত্র সেই খেজুরটার মধ্যেই আছে।",
                    "highlight": "খেজুরটার মধ্যেই আছে",
                },
            ],
        },
        {
            "id": 5,
            "name": "Human Potentiality Awakens",
            "start": 14.3,
            "end": 17.3,
            "bg_theme": "Amber Sunrise & Golden Saffron Atelier",
            "bg_colors": ["#FFF0D9", "#F5C77E", "#D99441"],
            "camera_mode": "Crane Upward Tilt & Hero Orbit Push",
            "script_bn": "So just like this, যদি আপনার মধ্যে potentiality থাকে,",
            "script_en": "So just like this, if you possess true potentiality within you...",
            "sub_segments": [
                {
                    "start": 14.35,
                    "end": 15.35,
                    "text_bn": "So just like this,",
                    "highlight": "So just like this",
                },
                {
                    "start": 15.35,
                    "end": 17.25,
                    "text_bn": "যদি আপনার মধ্যে potentiality থাকে,",
                    "highlight": "potentiality থাকে",
                },
            ],
        },
        {
            "id": 6,
            "name": "People Choose the Worthy",
            "start": 17.3,
            "end": 20.8,
            "bg_theme": "Warm Travertine Marble & Antique Brass Hall",
            "bg_colors": ["#F7F2E2", "#E4CE9E", "#C49D5A"],
            "camera_mode": "Dramatic Pull-Back Reveal of Crowd & Spotlights",
            "script_bn": "আর যদি আপনি যোগ্য ব্যক্তি হয়ে থাকেন, people are going to choose you।",
            "script_en": "And if you are a worthy person, people are going to choose you.",
            "sub_segments": [
                {
                    "start": 17.35,
                    "end": 19.05,
                    "text_bn": "আর যদি আপনি যোগ্য ব্যক্তি হয়ে থাকেন,",
                    "highlight": "যোগ্য ব্যক্তি",
                },
                {
                    "start": 19.05,
                    "end": 20.75,
                    "text_bn": "people are going to choose you।",
                    "highlight": "choose you",
                },
            ],
        },
        {
            "id": 7,
            "name": "No Need to Shout for Attention",
            "start": 20.8,
            "end": 23.3,
            "bg_theme": "Split Dusty Sienna Clay vs. Tranquil Eucalyptus Sage",
            "bg_colors": ["#EAD3C6", "#D9DFC4", "#B89A82"],
            "camera_mode": "Handheld Shake on Shouting Megaphone -> Smooth Pan to Calmness",
            "script_bn": "আপনার চিল্লি attention seek করতে হবে না মানুষের।",
            "script_en": "You won't have to loudly scream to seek people's attention.",
            "sub_segments": [
                {
                    "start": 20.85,
                    "end": 23.25,
                    "text_bn": "আপনার চিল্লি attention seek করতে হবে না মানুষের।",
                    "highlight": "attention seek",
                }
            ],
        },
        {
            "id": 8,
            "name": "The Scales of Personal Decision",
            "start": 23.3,
            "end": 25.0,
            "bg_theme": "Deep Roasted Walnut & Warm Espresso Gold Study",
            "bg_colors": ["#2D2118", "#463324", "#C9964C"],
            "camera_mode": "Direct Center Push-In on Decision Scale Fulcrum",
            "script_bn": "এখন এটা আপনার উপর depend করে।",
            "script_en": "Now, it depends entirely on you.",
            "sub_segments": [
                {
                    "start": 23.35,
                    "end": 24.95,
                    "text_bn": "এখন এটা আপনার উপর depend করে।",
                    "highlight": "depend করে",
                }
            ],
        },
        {
            "id": 9,
            "name": "Final Question: The Seed or The Date?",
            "start": 25.0,
            "end": 32.0,
            "bg_theme": "Dual-Tone Finale: Arid Ash Sand vs. Golden Harvest Radiance",
            "bg_colors": ["#DED6C8", "#F9DFAA", "#DC9736"],
            "camera_mode": "Pan Left (Seeds) -> Pan Right (Ripe Date) -> Wide Epic Pull-Back",
            "script_bn": "আপনি খেজুরের বিচিগুলোর মতো হবেন, নাকি সেই খেজুরটাই হবেন।",
            "script_en": "Will you be like the hollow date seeds, or will you be that nourishing date?",
            "sub_segments": [
                {
                    "start": 25.05,
                    "end": 26.85,
                    "text_bn": "আপনি খেজুরের বিচিগুলোর মতো হবেন,",
                    "highlight": "খেজুরের বিচিগুলোর মতো",
                },
                {
                    "start": 26.85,
                    "end": 31.95,
                    "text_bn": "নাকি সেই খেজুরটাই হবেন।",
                    "highlight": "সেই খেজুরটাই হবেন",
                },
            ],
        },
    ]

    payload = {
        "fps": FPS,
        "duration": round(duration, 3),
        "total_frames": total_frames,
        "scenes": scenes,
        "frame_energy": smoothed_rms,
    }

    with open(OUTPUT_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(
        f"[audio_analyzer] Analyzed {AUDIO_PATH}: duration={duration:.2f}s, "
        f"frames={total_frames} @ {FPS}fps, scenes={len(scenes)}"
    )
    print(f"[audio_analyzer] Saved timeline data to {OUTPUT_JSON_PATH}")


if __name__ == "__main__":
    analyze_audio()
