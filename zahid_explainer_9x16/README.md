# Zahid 50-minute explainer (9:16, 720x1280, 30fps)
- `zahid_50_minute_explainer_720x1280.mp4` – final video (audio muxed, 171.17 s)
- `src/` – generator: pause detection + DP alignment (`align.py`), engine/sprites/camera/captions (`engine.py`), props, 40 scenes, chunked renderer, audio synth.
Timing: no usable Bengali ASR was available (Whisper-small failed), so sync = RMS pause detection + DP clause matching + syllable-weighted word timing (word-level accuracy approx. +/-0.1-0.25 s; scene cuts sit in real pauses).
