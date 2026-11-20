"""Script 1c: second ASR pass (VAD + no previous-text conditioning) to verify what the audio actually contains."""
import json
from faster_whisper import WhisperModel
m = WhisperModel("small", device="cpu", compute_type="int8", cpu_threads=4)
segs, _ = m.transcribe("/tmp/vid/audio_repo/audio01.mp3", language="bn", beam_size=5, condition_on_previous_text=False,
                       vad_filter=True, vad_parameters=dict(min_silence_duration_ms=250, speech_pad_ms=100), temperature=0.0)
out = [{"start": s.start, "end": s.end, "text": s.text.strip()} for s in segs]
json.dump(out, open("/tmp/vid/out/asr2.json", "w"), ensure_ascii=False, indent=1)
for s in out: print(f"{s['start']:6.2f}-{s['end']:6.2f} {s['text']}")
