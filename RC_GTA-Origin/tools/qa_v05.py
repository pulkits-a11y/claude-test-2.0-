#!/usr/bin/env python3
"""v05 QA: the measurable items of the instruction doc's section 5 checklist, on the preview (or any export).

  python3 tools/qa_v05.py 07_Exports/RC_GTA-Origin_v05_preview.mp4

Checks
  1  frame 0: mean luma, saturation, black share (doc: "full-bleed, bright and readable as a still thumbnail")
  2  0-4.5 s, every frame: no empty black frame (mean luma < 12 / 255 with >= 90% near-black pixels)
  5  no black half-frames anywhere (left or right half >= 92% near-black) and no flat-black run longer than 0.8 s
  8  the silence after "Grand Theft Auto." (VO words) <= 0.4 s; integrated loudness -14 LUFS +-0.5; true peak <= -1 dBTP
  9  loop: the last frame vs frame 0 (mean absolute difference)
Writes checks/qa_v05.json next to the export and prints a table. Visual items (depth edges, captions with the sound
off, components present) are reviewed on contact sheets, not here.
"""
import json, subprocess, sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def frames(path, w=320, h=180):
    cmd = ["ffmpeg", "-v", "error", "-i", str(path), "-vf", f"scale={w}:{h}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, h, w, 3)


def luma(a):
    return 0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2]


def loudness(path):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-af", "ebur128=peak=true", "-f", "null", "-"],
                       capture_output=True, text=True)
    out = r.stderr.splitlines()
    I = tp = None
    for i, l in enumerate(out):
        if l.strip().startswith("I:") and "LUFS" in l:
            I = float(l.split()[1])
        if l.strip().startswith("Peak:") and "dBFS" in l:
            tp = float(l.split()[1])
    return I, tp


def main():
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "07_Exports/RC_GTA-Origin_v05_preview.mp4"
    fps = 30
    F = frames(path).astype(np.float32)
    n = len(F)
    Y = luma(F)
    near_black = Y < 18
    rep = {"file": str(path.relative_to(ROOT)) if str(path).startswith(str(ROOT)) else str(path), "frames": int(n)}
    f0 = F[0]
    mx, mn = f0.max(-1), f0.min(-1)
    sat = float(np.mean((mx - mn) / np.maximum(mx, 1)))
    rep["1_frame0"] = {"mean_luma": round(float(Y[0].mean()), 1), "mean_saturation": round(sat, 3),
                       "near_black_share": round(float(near_black[0].mean()), 3)}
    blk = [(i, round(float(Y[i].mean()), 1)) for i in range(min(n, int(4.5 * fps)))
           if Y[i].mean() < 12 and near_black[i].mean() >= 0.9]
    rep["2_hook_black_frames"] = blk
    w = F.shape[2]
    halves = []
    for i in range(n):
        l, r = near_black[i][:, : w // 2].mean(), near_black[i][:, w // 2:].mean()
        if (l >= 0.92) != (r >= 0.92):
            halves.append((i, round(i / fps, 2), "left" if l >= 0.92 else "right"))
    rep["5_black_half_frames"] = {"count": len(halves), "first": halves[:12]}
    runs, start = [], None
    for i in range(n + 1):
        b = i < n and near_black[i].mean() >= 0.9 and Y[i].mean() < 14
        if b and start is None:
            start = i
        if not b and start is not None:
            if i - start > 0.8 * fps:
                runs.append((start, i - 1, round((i - start) / fps, 2)))
            start = None
    rep["5_flat_black_runs_over_0.8s"] = runs
    bm = json.load(open(ROOT / "timing/beat_map.json"))
    words = [x for b in bm["beats"] for x in b["words"]]
    auto = next(x for x in words if x["beat"] == "B13" and x["text"] == "Auto.")
    nxt = next(x for x in words if x["beat"] == "B14")
    I, tp = loudness(path)
    rep["8_logo_silence_s"] = round(nxt["start"] - auto["end"], 3)
    rep["8_loudness"] = {"integrated_lufs": I, "true_peak_dbtp": tp}
    rep["9_loop_last_vs_first_mad"] = round(float(np.abs(F[-1] - F[0]).mean()), 2)
    out = path.parent / "checks"
    out.mkdir(exist_ok=True)
    json.dump(rep, open(out / "qa_v05.json", "w"), indent=1)
    print(json.dumps(rep, indent=1))


if __name__ == "__main__":
    main()
