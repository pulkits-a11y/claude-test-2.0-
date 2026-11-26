"""Builds GTA911_CoverReel.tsrct: assets -> document JSON -> commit -> keyframes + voiceover -> check frames."""
import json, os, shutil, subprocess, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import reel
from lib import ROOT, ms
X = reel.X
OUT = os.path.join(ROOT, "GTA911_CoverReel.tsrct")
WORK = os.path.join(ROOT, ".tesseract-work")

def run(*a):
    r = subprocess.run(list(a), capture_output=True, text=True)
    if r.returncode: print(r.stderr[-3000:]); raise SystemExit(1)
    return r.stdout

t0 = time.time()
doc = reel.main()
json.dump(doc, open(os.path.join(WORK, "editable.json"), "w"))
acts = reel.D.finalize()
vo = reel.R["vo"]
acts.append({"type": "createFxAudioLayer", "compositionId": "main", "layerId": reel.D.nid(), "name": "Voiceover (processed, tight 118%)",
             "activeRange": {"start": 0, "duration": ms(reel.END)}, "sourceRange": {"start": 0, "duration": 35230}, "sourceIntrinsicDuration": 35230,
             "source": {"assetId": "vo"}, "volume": 1.0})
json.dump(acts, open(os.path.join(WORK, "edits.json"), "w"))
print("layers/actions built", len(acts), "actions", round(time.time() - t0, 1), "s")
shutil.copy(reel.prep.BASE, OUT)
out = run(X, "project", "commit", "--project", OUT, "--file", os.path.join(WORK, "editable.json"))
print("commit", out[-400:])
out = run(X, "project", "apply", "--project", OUT, "--actions", os.path.join(WORK, "edits.json"))
w = json.loads(out).get("warnings")
print("apply ok, warnings:", json.dumps(w)[:1500])
print("done", round(time.time() - t0, 1), "s")
