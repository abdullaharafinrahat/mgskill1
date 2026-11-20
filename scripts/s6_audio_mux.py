"""Script 8: build the audio track (original narration + soft clock tick + gentle music bed + hit sounds) and mux with the video."""
import subprocess, json, wave, numpy as np
SR = 44100
END = json.load(open("/tmp/work/timeline.json"))["end"]; N = int(END * SR)
raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", "/tmp/work/audio01.mp3", "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"], capture_output=True).stdout
voice = np.frombuffer(raw, np.float32); print("voice sec", len(voice) / SR)
vo = np.zeros(N, np.float32); vo[:min(N, len(voice))] = voice[:N]
t = np.arange(N) / SR
# music bed: warm pad chords + soft plucks
chords = [(220.0, 261.63, 329.63), (174.61, 220.0, 261.63), (261.63, 329.63, 392.0), (196.0, 246.94, 293.66)]
mus = np.zeros(N, np.float32); beat = 2.0
for i in range(int(END / beat) + 1):
    a, b = int(i * beat * SR), min(N, int((i + 1) * beat * SR + SR * .5))
    if a >= N: break
    tt = np.arange(b - a) / SR; env = np.minimum(1, tt / .6) * np.exp(-np.maximum(0, tt - beat) * 3)
    ch = chords[(i // 2) % 4]; seg = sum(np.sin(2 * np.pi * f * tt) + .3 * np.sin(4 * np.pi * f * tt) for f in ch) / 3
    mus[a:b] += (seg * env * .5).astype(np.float32)
    # pluck arpeggio
    for k, f in enumerate((ch[0] * 2, ch[1] * 2, ch[2] * 2, ch[1] * 2)):
        s0 = a + int(k * beat / 4 * SR); n2 = min(N - s0, int(.8 * SR))
        if n2 > 0:
            tp = np.arange(n2) / SR; mus[s0:s0 + n2] += (np.sin(2 * np.pi * f * tp) * np.exp(-tp * 6) * .35).astype(np.float32)
gain = np.where(t < 124.4, 0.045, 0.045 + 0.075 * np.clip((t - 124.4) / 2.0, 0, 1)).astype(np.float32)
gain *= np.clip(t / 2.0, 0, 1) * np.clip((END - t) / 2.5, 0, 1)
mus *= gain
# clock tick-tock
tick = np.zeros(N, np.float32); rng = np.random.default_rng(3)
for s in range(int(END)):
    a = int((s + .02) * SR); n2 = int(.03 * SR)
    if a + n2 < N:
        tt = np.arange(n2) / SR; f = 1900 if s % 2 == 0 else 1400
        tick[a:a + n2] += ((np.sin(2 * np.pi * f * tt) * .6 + rng.standard_normal(n2) * .25) * np.exp(-tt * 140) * .05).astype(np.float32)
fx = np.zeros(N, np.float32)
def thump(at, amp=.5):
    a = int(at * SR); n2 = int(.5 * SR); tt = np.arange(n2) / SR; fx[a:a + n2] += (np.sin(2 * np.pi * (60 + 90 * np.exp(-tt * 18)) * tt) * np.exp(-tt * 7) * amp).astype(np.float32)
def chime(at, f=1318.5, amp=.12):
    a = int(at * SR); n2 = int(1.2 * SR); tt = np.arange(n2) / SR; fx[a:a + n2] += ((np.sin(2 * np.pi * f * tt) + .4 * np.sin(2 * np.pi * f * 2 * tt)) * np.exp(-tt * 3.5) * amp).astype(np.float32)
for at in (.35, 107.6, 123.4): thump(at)
for at in (75.0, 162.6, 173.2): chime(at)
chime(4.9, 1568, .1); thump(189.5, .25)
mix = vo * 1.0 + mus + tick + fx
mix = np.tanh(mix * 1.1) * .95
pcm = (mix * 32767).astype(np.int16)
with wave.open("/tmp/work/mix.wav", "wb") as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
out = "/tmp/work/zahid_50_minutes.mp4"
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", "/tmp/work/video_silent.mp4", "-i", "/tmp/work/mix.wav", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "44100",
                "-t", str(END), "-movflags", "+faststart", out])
print(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_name,width,height,r_frame_rate,duration", "-of", "default=nw=1", out], capture_output=True, text=True).stdout)
