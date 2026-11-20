# -*- coding: utf-8 -*-
"""Step 4: concat the segments and mux with the narration audio -> final mp4 (9:16, H.264 + AAC)."""
import os, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
FF = open(os.path.join(HERE, "ffpath")).read().strip()
lst = os.path.join(HERE, "parts", "list.txt")
with open(lst, "w") as f:
    for k in range(4):
        f.write(f"file 'part{k}.mp4'\n")
out = os.path.join(HERE, "zahid_fifty_minutes.mp4")
subprocess.run([FF, "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", lst, "-i", os.path.join(HERE, "audio.mp3"),
                "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-ar", "44100",
                "-shortest", "-movflags", "+faststart", out], check=True)
print("written", out, os.path.getsize(out) // 1024, "KB")
