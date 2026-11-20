# জাহিদের ঘড়ি – 2D animation (9:16 MP4)

`zahid_50_minute.mp4` – 1080x1920, 30fps, H.264 + AAC, synced to `audio01.mp3`.

Note: the supplied `audio01.mp3` ends at 2:04 (mid-sentence, "কাজ করতে সত্তর…"), so the video covers the script up to that point.

Pipeline (`scripts/`):
1. `s01_align.py` – forced alignment (MMS_FA wav2vec2 + CTC Viterbi) of script text to audio -> `timing.json`
2. `v_lib.py`, `v_props.py`, `v_scenes1.py`, `v_scenes2.py` – Skia + HarfBuzz vector drawing (characters, props, camera moves)
3. `s02_render.py` – scene timeline, transitions, synced captions, frame renderer
4. `s03_render_all.py` – parallel segment rendering
5. `s04_mux.py` – concat + audio mux
