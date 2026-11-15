#!/usr/bin/env python3
"""Contact sheets for picking the moment in each real B-roll clip.

  python3 tools/footage_sheets.py                 # every R-ID that has a real clip in 04_Broll/
  python3 tools/footage_sheets.py R17.1 R9.1      # only these
  python3 tools/footage_sheets.py --every 2       # seconds between thumbnails (default: auto)

For each clip: 04_Broll/_sheets/<RID>_sheetNN.jpg - 5x6 grids of 384x216 thumbnails, each stamped with
its source time (mm:ss.s), plus <RID>.json (duration, size, fps). Long videos (> 10 min, the plan says
they are there for specific moments) get one thumbnail every 10 s on a first pass; re-run with
--range START,END --every 1 to zoom in. Set the chosen window in 04_Broll/broll_manifest.json
(source_in / source_out, seconds), then run tools/sync_footage.py for the beats that use the clip.
"""
import argparse, glob, json, os, subprocess, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sync_footage import find_real  # noqa

ROOT = "/home/user/claude-test-2.0-/RC_GTA-Origin"
OUT = f"{ROOT}/04_Broll/_sheets"
FONT = f"{ROOT}/06_Fonts/Inter-Medium.ttf"


def probe(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height,r_frame_rate:format=duration",
                        "-of", "json", path], capture_output=True, text=True)
    d = json.loads(r.stdout)
    s = d["streams"][0]
    num, den = s["r_frame_rate"].split("/")
    return {"duration_s": float(d["format"]["duration"]), "width": s["width"], "height": s["height"], "fps": round(float(num) / float(den), 3)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("rids", nargs="*")
    ap.add_argument("--every", type=float, default=None)
    ap.add_argument("--range", default=None, help="START,END seconds")
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    man = json.load(open(f"{ROOT}/04_Broll/broll_manifest.json"))["clips"]
    for e in man:
        if a.rids and e["rid"] not in a.rids:
            continue
        real = [r for r in find_real(e) if r.lower().endswith((".mp4", ".mov", ".m4v", ".webm", ".mkv"))]
        if not real:
            continue
        src = real[0]
        info = probe(src)
        t0, t1 = 0.0, info["duration_s"]
        if a.range:
            t0, t1 = (float(x) for x in a.range.split(","))
        span = t1 - t0
        every = a.every or (10.0 if span > 600 else 2.0 if span > 120 else 1.0 if span > 30 else 0.5)
        tag = f"{e['rid']}" + (f"_{int(t0)}-{int(t1)}" if a.range else "")
        pattern = f"{OUT}/{tag}_sheet%02d.jpg"
        for old in glob.glob(f"{OUT}/{tag}_sheet*.jpg"):
            os.remove(old)
        vf = (f"fps=1/{every},scale=384:216:force_original_aspect_ratio=decrease,pad=384:216:(ow-iw)/2:(oh-ih)/2,"
              f"drawtext=fontfile={FONT}:text='%{{pts\\:hms\\:{t0}}}':x=6:y=6:fontsize=18:fontcolor=white:box=1:boxcolor=black@0.6,"
              f"tile=5x6:padding=4:color=black")
        subprocess.run(["ffmpeg", "-nostdin", "-loglevel", "error", "-y", "-ss", str(t0), "-t", str(span), "-i", src,
                        "-vf", vf, "-q:v", "4", pattern], check=True)
        info.update({"rid": e["rid"], "file": os.path.relpath(src, ROOT), "every_s": every, "range": [t0, t1],
                     "need": e["note"], "beats": e["beats"]})
        json.dump(info, open(f"{OUT}/{tag}.json", "w"), indent=1)
        print(f"{e['rid']:6} {info['duration_s']:8.1f}s {info['width']}x{info['height']}@{info['fps']}  every {every}s -> "
              f"{len(glob.glob(f'{OUT}/{tag}_sheet*.jpg'))} sheet(s)  | need: {e['note'][:70]}")


if __name__ == "__main__":
    main()
