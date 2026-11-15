#!/usr/bin/env python3
"""B16 VHS rewind: build the reversed-at-8x picture run as one frame-exact clip.

  cd hyperframes/b16-bug-origin && python3 tools/make_rewind.py
  -> assets/rewind/b16-rewind.mp4   (1920x1080, 30 fps, 52 frames = composition local frames 0..51, no audio)
     assets/rewind/b16-rewind.map.json  (which source frame / zoom every output frame shows)

Plan p.27 B16 step 1: "VHS rewind for about 1 s: the B14 clips, then B9 GTA 1, then the 1995 design document, all
reversed at 8x speed with the VHS overlay (RT1) and tracking lines". HyperFrames has no reverse playback (playback
rate 0.1-10), so the reversal is baked here (a cut/retime, not a look). The VHS LOOK is NOT baked: it is a media
treatment on the <video> in index.html, and the tracking lines are drawn there.

Re-run after `python3 ../../tools/sync_footage.py .` brings in real footage, then re-render. The source in-points
below MIRROR the Tesseract shots they rewind: B14 = hyperframes/b14-since/tesseract_shots.json, B9 = the R9.1 L1
shot in hyperframes/b09-throughyou/tesseract_shots.json (lane E; 0.0 until it exists), B4 = the R4.5 framing and
the 100 -> 118% push of hyperframes/b04-racenchase/index.html (lane B). Keep them in sync (BEAT_NOTES "Pending").

Output frame j = composition local frame j (local = beat + 6). An 8x rewind of an edit frame e steps e -> e - 8 per
output frame; the B14 run is compressed (it jumps from shot to shot: 3 escape, 2 lights, 3 chase, then 1 frame per
burst game, newest to oldest), then 10 frames of B9's GTA 1, then the R4.5 page zooming back out 118% -> 100% at
8x the B4 push rate (18% over 44f -> 3.27% a frame), landing on B4's opening framing, held under the X7 dissolve.
"""
import json, os, shutil, subprocess, sys, tempfile
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
FOOT = os.path.join(PROJ, "assets", "footage")
OUT_DIR = os.path.join(PROJ, "assets", "rewind")
W, H, FPS = 1920, 1080, 30
N_FRAMES = 52                     # local 0..51 (the clip is used to local 50, the end of the X7 dissolve)

# ---- source in-points of the shots being rewound (seconds into the R-ID file) ----
B14 = {   # hyperframes/b14-since/tesseract_shots.json (beat-relative frames)
    "escape": {"rid": "R14.5", "start_f": 163, "src_in": 8.0},
    "lights": {"rid": "RT3", "start_f": 133, "src_in": 1.0},
    "chase":  {"rid": "R1.3", "start_f": 60, "src_in": 2.0},
    # burst: clip k (0..9) = edit frames 6k..6k+6; two moments per game (a = first, b = second clip)
    "burst": [("R14.1", 1.0), ("R14.1", 5.0), ("R14.2", 1.0), ("R14.2", 5.0), ("R14.3", 1.0), ("R14.3", 5.0),
              ("R14.4", 1.0), ("R14.4", 5.0), ("R14.5", 1.0), ("R14.5", 5.0)],
}
B9_R91_SRC_IN = 0.0      # B9 L1 shot R9.1 (B9 f0-127): source_in_s from lane E's tesseract_shots.json when it exists
B9_R91_START_F = 0
# B4 framing of the R4.5 title page (b04-racenchase): page drawn at 1.4 x page px, boxed-title centre (878, 307.5)
# on screen (960, 400); L7 push 1.00 -> 1.18 about the spotlight-hole centre (959, 402) over B4 f0-44, linear.
DOC = {"page_scale": 1.4, "title_page": (878.0, 307.5), "title_screen": (960.0, 400.0), "push_origin": (959.0, 402.0),
       "push_from": 1.0, "push_to": 1.18, "push_frames": 44}


def b14_source(e):
    """B14 edit frame e (beat-relative) -> (rid, source seconds)."""
    if e >= 163:
        s = B14["escape"]; return s["rid"], s["src_in"] + (e - s["start_f"]) / FPS
    if e >= 133:
        s = B14["lights"]; return s["rid"], s["src_in"] + (e - s["start_f"]) / FPS
    if e >= 60:
        s = B14["chase"]; return s["rid"], s["src_in"] + (e - s["start_f"]) / FPS
    k = e // 6
    rid, src_in = B14["burst"][k]
    return rid, src_in + (e - 6 * k) / FPS


def plan():
    frames = []
    def add(kind, **kw):
        frames.append(dict(local=len(frames), beat=len(frames) - 6, kind=kind, **kw))
    # beat -6..2 (head handle + 3 frames): the escape shot rewinding from B14's last frame (edit 188), 8 edit frames per
    # output frame; the handle continues it backward in time (= later source frames under B14's shut slats)
    for b in range(-6, 3):
        e = 188 - 8 * b
        rid, t = b14_source(e); add("B14", rid=rid, edit_f=e, src_s=round(t, 4))
    # beat 3..4: police lights (edit 156, 148); beat 5..7: GTA 5 chase (edit 132, 124, 116)
    for e in (156, 148, 132, 124, 116):
        rid, t = b14_source(e); add("B14", rid=rid, edit_f=e, src_s=round(t, 4))
    # beat 8..12: the L10 burst, one frame per game, newest to oldest (2013 -> 2001)
    for e in (52, 44, 28, 20, 4):
        rid, t = b14_source(e); add("B14", rid=rid, edit_f=e, src_s=round(t, 4))
    # beat 13..22: B9's GTA 1 chase (R9.1, the L1 shot B9 f0-127) rewinding from its last frame, 8x
    for i in range(10):
        e = 127 - 8 * i
        add("B9", rid="R9.1", edit_f=e, src_s=round(B9_R91_SRC_IN + (e - B9_R91_START_F) / FPS, 4))
    # beat 23..29: the 1995 design document, B4's push (1.00 -> 1.18 over 44f) run backwards at 8x, then B4's opening
    # framing (1.00); beat 30..45: held there (the tape has stopped) under the X7 light-leak dissolve
    rate = (DOC["push_to"] - DOC["push_from"]) / DOC["push_frames"] * 8
    for i in range(N_FRAMES - len(frames)):
        z = max(DOC["push_from"], DOC["push_to"] - rate * i)
        add("B4", rid="R4.5", zoom=round(z, 5))
    return frames


def cover_frame(src_png, dst_png):
    im = Image.open(src_png).convert("RGB")
    s = max(W / im.width, H / im.height)
    nw, nh = round(im.width * s), round(im.height * s)
    im = im.resize((nw, nh), Image.LANCZOS)
    x0, y0 = (nw - W) // 2, (nh - H) // 2
    im.crop((x0, y0, x0 + W, y0 + H)).save(dst_png)


def video_frame(rid, t, dst_png, tmp):
    src = os.path.join(FOOT, rid + ".mp4")
    raw = os.path.join(tmp, "raw.png")
    # accurate seek: the first frame with pts >= t - 0.03 f is frame round(t * 30)
    n = round(t * FPS)
    subprocess.run(["ffmpeg", "-nostdin", "-loglevel", "error", "-y", "-ss", "%.5f" % ((n - 0.03) / FPS), "-i", src,
                    "-frames:v", "1", raw], check=True)
    cover_frame(raw, dst_png)


def doc_frame(page, z, dst_png):
    k = DOC["page_scale"]; (px, py) = DOC["title_page"]; (ax, ay) = DOC["title_screen"]; (cx, cy) = DOC["push_origin"]
    # screen S = C + z * (A + k (P - Pt) - C)  =>  P = Pt + ((S - C) / z + C - A) / k
    a = 1.0 / (k * z)
    c0 = px + (-cx / z + cx - ax) / k
    f0 = py + (-cy / z + cy - ay) / k
    im = page.transform((W, H), Image.AFFINE, (a, 0, c0, 0, a, f0), resample=Image.BICUBIC, fillcolor=(255, 255, 255))
    im.save(dst_png)


def main():
    frames = plan()
    os.makedirs(OUT_DIR, exist_ok=True)
    page = Image.open(os.path.join(FOOT, "R4.5.png")).convert("RGB")
    tmp = tempfile.mkdtemp(prefix="b16rw-")
    try:
        for fr in frames:
            dst = os.path.join(tmp, "f%03d.png" % fr["local"])
            if fr["kind"] == "B4":
                doc_frame(page, fr["zoom"], dst)
            else:
                video_frame(fr["rid"], fr["src_s"], dst, tmp)
        out = os.path.join(OUT_DIR, "b16-rewind.mp4")
        subprocess.run(["ffmpeg", "-nostdin", "-loglevel", "error", "-y", "-framerate", str(FPS), "-i",
                        os.path.join(tmp, "f%03d.png"), "-c:v", "libx264", "-preset", "medium", "-crf", "12",
                        "-g", "6", "-pix_fmt", "yuv420p", "-color_primaries", "bt709", "-color_trc", "bt709",
                        "-colorspace", "bt709", "-r", str(FPS), out], check=True)
        json.dump({"note": "local frame j of b16-bug-origin shows output frame j (beat = j - 6); see make_rewind.py",
                   "sources": {"B14": B14, "B9_R9.1_src_in": B9_R91_SRC_IN, "B4_doc": DOC}, "frames": frames},
                  open(os.path.join(OUT_DIR, "b16-rewind.map.json"), "w"), indent=1)
        print(out, len(frames), "frames")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
