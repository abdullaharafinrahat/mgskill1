# Step 4: concatenate segments, add narration audio (short fade-out at the cut end), write final MP4
import glob, json, subprocess
DUR = json.load(open("timing.json"))["duration"]
segs = sorted(glob.glob("seg_*.mp4"))
open("concat.txt", "w").write("".join(f"file '{s}'\n" for s in segs))
subprocess.run(["./ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", "concat.txt", "-c", "copy", "video_only.mp4"], check=True)
subprocess.run(["./ffmpeg", "-y", "-loglevel", "error", "-i", "video_only.mp4", "-i", "audio01.mp3",
                "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                "-af", f"afade=t=out:st={DUR-0.35:.2f}:d=0.35", "-t", f"{DUR:.3f}", "-movflags", "+faststart", "zahid_50_minute.mp4"], check=True)
print("done")
