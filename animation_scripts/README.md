# জাহিদের ৫০ মিনিট — 2D animation (9:16)

`zahid_fifty_minutes.mp4` : 1080x1920, 30fps, H.264 + AAC, narration = `audioe0.mp3`

Pipeline (all Python, rendered with pycairo + Pillow/raqm, encoded with ffmpeg):

| step | file | what it does |
|------|------|--------------|
| 0 | `script_data.py` | script split into caption chunks (+ who is speaking) |
| 1 | `01_timing.py` | analyses the audio (pauses, loudness) and aligns every chunk to the narration (DP alignment) -> `timeline.json`, `amp.npy` |
| 2 | `engine.py`, `chars.py` | mini 2D engine: camera, easing, Bengali text shaping, characters, props |
| 3 | `shots1.py`, `shots2.py`, `shots3.py` | the 49 hand-built animated scenes (camera pans / zooms / shakes) |
| 4 | `registry.py` | scene <-> script mapping, transitions, captions, progress bar |
| 5 | `02_preview.py` | contact sheet for QA |
| 6 | `03_render_parts.py` | renders frames in 4 parallel workers into H.264 segments |
| 7 | `04_assemble.py` | concatenates segments + muxes audio |

Setup: `pip install pillow numpy imageio-ffmpeg mutagen`, `apt install python3-cairo libraqm0 fonts-noto-core`,
then put the ffmpeg binary path into a file called `ffpath` and `audio.mp3` next to the scripts.
