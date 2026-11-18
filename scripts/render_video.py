#!/usr/bin/env python3
"""
Script 5: render_video.py
Executes the full 2D animation rendering pipeline:
1. Loads timeline & audio envelope from scripts/timeline_data.json
2. Renders all frames at 1280x720 @ 30 FPS via scene_compositor.py
3. Encodes H.264/AAC .mp4 video synced with audio.mp3 using FFmpeg
4. Exports scene keyframe thumbnails for verification and web studio preview
"""

import json
import os
import shutil
import subprocess
import sys
import time
import cv2
import imageio_ffmpeg

# Ensure scripts directory is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from audio_analyzer import analyze_audio, OUTPUT_JSON_PATH, AUDIO_PATH
from camera_engine import WIDTH, HEIGHT
from scene_compositor import render_frame_at_time


def build_video():
    t0 = time.time()
    if not os.path.exists(OUTPUT_JSON_PATH):
        analyze_audio()

    with open(OUTPUT_JSON_PATH, "r", encoding="utf-8") as f:
        timeline = json.load(f)

    fps = timeline["fps"]
    total_frames = timeline["total_frames"]
    scenes = timeline["scenes"]

    os.makedirs("public/frames", exist_ok=True)

    # Map representative mid-scene frame indices to save preview thumbnails
    scene_mid_frames = {}
    for sc in scenes:
        mid_t = (sc["start"] + sc["end"]) * 0.5
        mid_f = min(total_frames - 1, max(0, int(mid_t * fps)))
        scene_mid_frames[mid_f] = sc["id"]

    output_mp4 = "public/output.mp4"
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()

    cmd = [
        ffmpeg_exe,
        "-y",
        "-f",
        "rawvideo",
        "-vcodec",
        "rawvideo",
        "-s",
        f"{WIDTH}x{HEIGHT}",
        "-pix_fmt",
        "bgr24",
        "-r",
        str(fps),
        "-i",
        "-",
        "-i",
        AUDIO_PATH,
        "-c:v",
        "libx264",
        "-preset",
        "veryfast",
        "-crf",
        "20",
        "-pix_fmt",
        "yuv420p",
        "-c:a",
        "aac",
        "-b:a",
        "192k",
        "-shortest",
        "-movflags",
        "+faststart",
        output_mp4,
    ]

    print(f"[render_video] Starting 2D animation render: {total_frames} frames @ {WIDTH}x{HEIGHT} ({fps} FPS)...")
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)

    for f_idx in range(total_frames):
        frame = render_frame_at_time(f_idx, timeline)
        proc.stdin.write(frame.tobytes())

        if f_idx in scene_mid_frames:
            sc_id = scene_mid_frames[f_idx]
            thumb_path = f"public/frames/scene_{sc_id}.png"
            cv2.imwrite(thumb_path, frame)

        if (f_idx + 1) % 150 == 0 or f_idx == total_frames - 1:
            elapsed = time.time() - t0
            print(f"[render_video] Rendered frame {f_idx + 1}/{total_frames} ({elapsed:.1f}s)")

    proc.stdin.close()
    stderr_out = proc.stderr.read().decode("utf-8", errors="ignore")
    proc.wait()

    if proc.returncode != 0:
        print("[render_video] FFmpeg error:", stderr_out[-600:])
        sys.exit(1)

    # Copy to root output.mp4 and video.mp4 for convenient access & GitHub push
    shutil.copyfile(output_mp4, "output.mp4")
    shutil.copyfile(output_mp4, "video.mp4")
    shutil.copyfile(AUDIO_PATH, "public/audio.mp3")
    shutil.copyfile(OUTPUT_JSON_PATH, "public/timeline_data.json")

    size_mb = os.path.getsize("output.mp4") / (1024 * 1024)
    total_time = time.time() - t0
    print(f"[render_video] SUCCESS! Created output.mp4 & video.mp4 ({size_mb:.2f} MB) in {total_time:.1f}s")


if __name__ == "__main__":
    build_video()
