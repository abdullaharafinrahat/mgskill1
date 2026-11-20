# Zahid 50-minute explainer (9:16, 720x1280, 30fps)
- `zahid_50_minute_explainer_720x1280.mp4` – final video (audio muxed, 171.17 s)
- `src/` – generator: pause detection + DP alignment (`align.py`), engine/sprites/camera/captions (`engine.py`), props, 40 scenes, chunked renderer, audio synth.
Timing: no usable Bengali ASR was available (Whisper-small failed), so sync = RMS pause detection + DP clause matching + syllable-weighted word timing (word-level accuracy approx. +/-0.1-0.25 s; scene cuts sit in real pauses).

## Fixed version (`zahid_50_minute_explainer_720x1280_fixed.mp4`)
Frame-by-frame review of the original render; only code fixes, same scenes / timing / audio, re-rendered. Fixes:
- **Characters' arms (engine.py)**: hanging arms bent *inward* and crossed over the torso (an "X" on the girl's uniform) because of a dead `pass` branch in the elbow code; elbows now bend outward for all characters.
- **Scene 6 (tried)**: end camera zoom cropped Zahid in half at the left edge; camera now keeps him in frame next to the stopwatch.
- **Scene 7 (ad)**: Zahid's head covered the first letters of the board text ("মোবাইল"); board raised, Zahid moved, final zoom reduced.
- **Scene 16 (silence)**: giant "কখন?" covered the girl's face and the clock was cut by the top edge; text moved above the head, zoom reduced.
- **Scene 17 (fork)**: both sign arrows pointed at the pole; "অপেক্ষা" now points to the bench (left) and "অন্য দোকান" to the big shop (right).
- **Scene 18 (simple)**: speech bubble floated with no speaker; the girl (memory silhouette) now says it.
- **Scene 22 (chart)**: counter showed ৪৯ while narrator said "পঞ্চাশ" and ৩৭ at "চল্লিশ" (counted 0→40, landing after the cut); now lands on 50 and counts 50→40 in sync.
- **Scene 24 (write)**: handwriting wipe finished exactly at the cut, leaving the ad text clipped; it now completes ~0.35 s earlier.
- **Scene 37 (takeaway)**: ✓ / ✗ marks covered the card text; moved to card corners.
- `render.py`: Pool(2) (was 4) so it fits small machines. Inputs not stored in repo: `voice16k.wav`, `voice44.wav` (from `audioe0.mp3`), `db.npy` (`pauses.py`).
