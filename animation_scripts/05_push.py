# -*- coding: utf-8 -*-
"""Step 8: push the finished video + scripts to GitHub. Token is read from env GH_TOKEN and never stored in git config."""
import os, subprocess, shutil, base64, sys
HERE = os.path.dirname(os.path.abspath(__file__))
TOKEN = os.environ["GH_TOKEN"]
REPO = "https://github.com/abdullaharafinrahat/mgskill1.git"
WORK = "/tmp/push_repo"
shutil.rmtree(WORK, ignore_errors=True)
auth = base64.b64encode(f"x-access-token:{TOKEN}".encode()).decode()
G = ["git", "-c", f"http.extraheader=AUTHORIZATION: basic {auth}"]
def run(args, cwd=WORK, check=True):
    r = subprocess.run(args, cwd=cwd, capture_output=True, text=True)
    print(" ".join(a for a in args if "AUTHORIZATION" not in a), "->", r.returncode, (r.stdout + r.stderr).strip()[-400:])
    if check and r.returncode:
        sys.exit(1)
    return r
run(G + ["clone", REPO, WORK], cwd="/tmp")
os.makedirs(f"{WORK}/animation_scripts", exist_ok=True)
for f in ["README.md", "script_data.py", "01_timing.py", "02_preview.py", "03_render_parts.py", "04_assemble.py", "05_push.py",
          "engine.py", "chars.py", "shots1.py", "shots2.py", "shots3.py", "registry.py", "timeline.json"]:
    shutil.copy(os.path.join(HERE, f), f"{WORK}/animation_scripts/{f}")
shutil.copy(os.path.join(HERE, "zahid_fifty_minutes.mp4"), f"{WORK}/zahid_fifty_minutes.mp4")
run(["git", "config", "user.email", "animator@example.com"])
run(["git", "config", "user.name", "animation-bot"])
run(["git", "add", "-A"])
run(["git", "commit", "-m", "Add 9:16 2D animation video (Zahid's 50 minutes) + python render scripts"])
branch = run(["git", "rev-parse", "--abbrev-ref", "HEAD"]).stdout.strip()
run(G + ["push", "origin", branch])
print("PUSHED to", REPO, "branch", branch)
