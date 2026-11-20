"""Script 1: detect speech segments (pauses) in the narration with ffmpeg silencedetect."""
import subprocess, re, json
r = subprocess.run(["ffmpeg","-hide_banner","-i","/tmp/work/audio01.mp3","-af",
    "silencedetect=noise=-33dB:d=0.14","-f","null","-"],capture_output=True,text=True)
st=[float(x) for x in re.findall(r"silence_start: ([\d.]+)",r.stderr)]
en=[float(x) for x in re.findall(r"silence_end: ([\d.]+)",r.stderr)]
D=124.369
speech=[]; t=0.0
for s,e in zip(st,en):
    if s>t+0.05: speech.append([round(t,3),round(s,3)])
    t=e
if t<D-0.05: speech.append([round(t,3),D])
json.dump(speech,open("/tmp/work/speech.json","w"))
for i,(a,b) in enumerate(speech): print(i,f"{a:7.2f} {b:7.2f} {b-a:5.2f}")
