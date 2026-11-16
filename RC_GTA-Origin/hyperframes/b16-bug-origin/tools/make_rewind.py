#!/usr/bin/env python3
"""B16 VHS rewind: build the reversed-at-8x picture run as one frame-exact clip.

  cd hyperframes/b16-bug-origin && python3 tools/make_rewind.py
  -> assets/rewind/b16-rewind.mp4   (1920x1080, 30 fps, 52 frames = composition local frames 0..51, no audio)
     assets/rewind/b16-rewind.map.json  (which source frame / zoom every output frame shows)

Plan p.27 B16 step 1: "VHS rewind for about 1 s: the B14 clips, then B9 GTA 1, then the 1995 design document, all
reversed at 8x speed with the VHS overlay (RT1) and tracking lines". HyperFrames has no reverse playback (playback
rate 0.1-10), so the reversal is baked here (a cut/retime, not a look). The VHS LOOK is NOT baked: it is a media
treatment on the <video> in index.html, and the tracking lines are drawn there.

FOOTAGE PASS: every video frame is now taken straight from the ORIGINAL download (04_Broll/_originals) at the shot's
source time, with the shot's crop (the same `source`, `source_in_s` and `crop` the Tesseract assembly uses), so the
rewind shows exactly what B14 / B9 show (no working clips needed). Re-run after B14 or B9 change, then re-render. The source in-points
MIRROR the Tesseract shots they rewind and are read live by load_inpoints(): B14 = hyperframes/b14-since/
tesseract_shots.json, B9 = the R9.1 shot in hyperframes/b09-throughyou/tesseract_shots.json (lane E; the default
0.0 / f0 until that file exists). B4 = the R4.5 framing and the 100 -> 118% push of hyperframes/b04-racenchase/
index.html (lane B), copied into DOC below: keep it in sync by hand (BEAT_NOTES "Pending").
Usage: python3 tools/make_rewind.py [output_dir]   (default assets/rewind; another folder = dry run for comparisons)

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
B14 = {   # filled by load_inpoints() from hyperframes/b14-since/tesseract_shots.json (required)
    "escape": None, "lights": None, "chase": None,
    # burst: clip k (0..9) = edit frames 6k..6k+6; two moments per game (a = first, b = second clip)
    "burst": [],
}
# B9 L1 shot R9.1 (B9 f0-127): source_in_s / crop from lane E's tesseract_shots.json when it exists. Until then a
# PROVISIONAL GTA 1 police-chase moment: R9.1 @126.83-129.23 (the white police car on the red car's tail, the moment
# B2 also uses) with B2's crop 736:414:59:40 (16:9 inside the 4:3 picture). Flagged in BEAT_NOTES.
B9_R91_SRC_IN = 125.0
B9_R91_START_F = 0
B9_R91_CROP = "736:414:59:40"
ROOT = os.path.dirname(os.path.dirname(PROJ))
B9_R91_SOURCE = "04_Broll/_originals/B02/R9.1__GTA 1 Police Chase 001 [HX8infRFBTc].mp4"
HF = os.path.dirname(PROJ)


def load_inpoints():
    """Overrides the defaults above with the live Tesseract shot lists, so the rewind always mirrors what B14 and B9
    actually show: hyperframes/b14-since/tesseract_shots.json (this lane) and hyperframes/b09-throughyou/... (lane E)."""
    global B9_R91_SRC_IN, B9_R91_START_F, B9_R91_CROP, B9_R91_SOURCE
    src = {"B14": "defaults", "B9": "defaults"}
    p14 = os.path.join(HF, "b14-since", "tesseract_shots.json")
    if os.path.exists(p14):
        shots = json.load(open(p14))["shots"]
        full = {s["id"]: s for s in shots}
        for key, sid in (("escape", "B14-escape"), ("lights", "B14-police-lights"), ("chase", "B14-gta5-chase-stars")):
            if sid in full:
                B14[key] = {"rid": full[sid]["rid"], "start_f": full[sid]["start_f"], "src_in": full[sid]["source_in_s"],
                            "source": full[sid]["source"], "crop": full[sid].get("crop")}
        burst = sorted([s for s in shots if s.get("screen") == "L10"], key=lambda s: s["start_f"])
        if len(burst) == 10:
            B14["burst"] = [(s["rid"], s["source_in_s"], s["source"], s.get("crop")) for s in burst]
        src["B14"] = os.path.relpath(p14, HF)
    p9 = os.path.join(HF, "b09-throughyou", "tesseract_shots.json")
    if os.path.exists(p9):
        r91 = [s for s in json.load(open(p9))["shots"] if s.get("rid") == "R9.1"]
        if r91:
            s = sorted(r91, key=lambda s: s["start_f"])[0]
            B9_R91_SRC_IN, B9_R91_START_F = float(s["source_in_s"]), int(s["start_f"])
            B9_R91_CROP = s.get("crop")
            if s.get("source"): B9_R91_SOURCE = s["source"]
            src["B9"] = os.path.relpath(p9, HF)
    return src
# B4 framing of the R4.5 title page (b04-racenchase): page drawn at 1.4 x page px, boxed-title centre (878, 307.5)
# on screen (960, 400); L7 push 1.00 -> 1.18 about the spotlight-hole centre (959, 402) over B4 f0-44, linear.
DOC = {"page_scale": 1.4, "title_page": (878.0, 307.5), "title_screen": (960.0, 400.0), "push_origin": (959.0, 402.0),
       "push_from": 1.0, "push_to": 1.18, "push_frames": 44}


def b14_source(e):
    """B14 edit frame e (beat-relative) -> (rid, source seconds in the original, original path, crop)."""
    for key, f0 in (("escape", 163), ("lights", 133), ("chase", 60)):
        if e >= f0:
            s = B14[key]; return s["rid"], s["src_in"] + (e - s["start_f"]) / FPS, s["source"], s["crop"]
    k = e // 6
    rid, src_in, source, crop = B14["burst"][k]
    return rid, src_in + (e - 6 * k) / FPS, source, crop


def plan():
    frames = []
    def add(kind, **kw):
        frames.append(dict(local=len(frames), beat=len(frames) - 6, kind=kind, **kw))
    # beat -6..2 (head handle + 3 frames): the escape shot rewinding from B14's last frame (edit 188), 8 edit frames per
    # output frame; the handle continues it backward in time (= later source frames under B14's shut slats)
    for b in range(-6, 3):
        e = 188 - 8 * b
        rid, t, so, cr = b14_source(e); add("B14", rid=rid, edit_f=e, src_s=round(t, 4), source=so, crop=cr)
    # beat 3..4: police lights (edit 156, 148); beat 5..7: GTA 5 chase (edit 132, 124, 116)
    for e in (156, 148, 132, 124, 116):
        rid, t, so, cr = b14_source(e); add("B14", rid=rid, edit_f=e, src_s=round(t, 4), source=so, crop=cr)
    # beat 8..12: the L10 burst, one frame per game, newest to oldest (2013 -> 2001)
    for e in (52, 44, 28, 20, 4):
        rid, t, so, cr = b14_source(e); add("B14", rid=rid, edit_f=e, src_s=round(t, 4), source=so, crop=cr)
    # beat 13..22: B9's GTA 1 chase (R9.1, the L1 shot B9 f0-127) rewinding from its last frame, 8x
    for i in range(10):
        e = 127 - 8 * i
        add("B9", rid="R9.1", edit_f=e, src_s=round(B9_R91_SRC_IN + (e - B9_R91_START_F) / FPS, 4),
            source=B9_R91_SOURCE, crop=B9_R91_CROP)
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


def video_frame(source, t, crop, dst_png, tmp):
    """One frame of the ORIGINAL at source time t (accurate seek, the frame showing at t), cropped like the shot."""
    src = os.path.join(ROOT, source)
    raw = os.path.join(tmp, "raw.png")
    cmd = ["ffmpeg", "-nostdin", "-loglevel", "error", "-y", "-ss", "%.5f" % max(0.0, t - 0.001), "-i", src, "-frames:v", "1"]
    vf = ["crop=" + crop] if crop else []
    # square the pixels (crop is in stored pixels; R14.4 is anamorphic, SAR 320:569) - a no-op for square sources
    vf += ["scale=w='trunc(iw*sar/2)*2':h=ih:flags=lanczos", "setsar=1"]
    cmd += ["-vf", ",".join(vf)]
    subprocess.run(cmd + [raw], check=True)
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
    global OUT_DIR
    if len(sys.argv) > 1:          # optional output folder (for comparisons); default assets/rewind
        OUT_DIR = os.path.abspath(sys.argv[1])
    inpoints_from = load_inpoints()
    if not (B14["escape"] and B14["lights"] and B14["chase"] and len(B14["burst"]) == 10):
        sys.exit("make_rewind: hyperframes/b14-since/tesseract_shots.json is incomplete")
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
                video_frame(fr["source"], fr["src_s"], fr.get("crop"), dst, tmp)
        out = os.path.join(OUT_DIR, "b16-rewind.mp4")
        subprocess.run(["ffmpeg", "-nostdin", "-loglevel", "error", "-y", "-framerate", str(FPS), "-i",
                        os.path.join(tmp, "f%03d.png"), "-c:v", "libx264", "-preset", "medium", "-crf", "12",
                        "-g", "6", "-pix_fmt", "yuv420p", "-color_primaries", "bt709", "-color_trc", "bt709",
                        "-colorspace", "bt709", "-r", str(FPS), out], check=True)
        json.dump({"note": "local frame j of b16-bug-origin shows output frame j (beat = j - 6); see make_rewind.py",
                   "inpoints_from": inpoints_from,
                   "sources": {"B14": B14, "B9_R9.1_src_in": B9_R91_SRC_IN, "B9_R9.1_start_f": B9_R91_START_F, "B4_doc": DOC},
                   "frames": frames},
                  open(os.path.join(OUT_DIR, "b16-rewind.map.json"), "w"), indent=1)
        print(out, len(frames), "frames")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
