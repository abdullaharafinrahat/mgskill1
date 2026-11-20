# জাহিদের ৫০ মিনিট – 2D animation (9:16, 1080x1920, 30fps, MP4)

- `zahid_50_minute_promise.mp4` – final video (H.264 + original `audio01.mp3`, 124.37s)
- `scripts/` – Python scripts used to analyse the audio, align the script, draw (Skia + HarfBuzz) and render the video
  1. `s1_analyze_audio.py`  – pause detection  (`s1b/s1c_asr*.py` – Whisper check)
  2. `s2_lib.py`            – drawing library (Bengali shaping, characters, props)
  3. `s3_align.py`          – sentence timing (timeline.json) + voice envelope for mouth movement
  4. `s4_scenes_a.py`, `s4_scenes_b.py` – scenes + camera moves
  5. `s5_render.py`         – camera, transitions, captions, parallel render + mux

Note: `audio01.mp3` ends in the middle of the story (after "…একটা বিরল মডেলের ফোন। কাজ করতে…"), so the video covers exactly the narrated part.
