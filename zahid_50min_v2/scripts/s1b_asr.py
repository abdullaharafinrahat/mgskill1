"""Script 1b: Whisper ASR (word timestamps) used only to verify/refine sentence alignment."""
import json, sys
from faster_whisper import WhisperModel
name = sys.argv[1] if len(sys.argv) > 1 else "small"
m = WhisperModel(name, device="cpu", compute_type="int8", cpu_threads=4)
segs, info = m.transcribe("/tmp/vid/audio_repo/audio01.mp3", language="bn", word_timestamps=True, beam_size=5, vad_filter=False)
out = []
for s in segs:
    out.append({"start": s.start, "end": s.end, "text": s.text, "words": [{"w": w.word, "s": w.start, "e": w.end} for w in (s.words or [])]})
json.dump(out, open("/tmp/vid/out/asr_%s.json" % name, "w"), ensure_ascii=False, indent=1)
print("done", len(out))
