#!/usr/bin/env python3
"""B16 VHS rewind: build the reversed-at-8x picture run as one frame-exact clip.

  cd hyperframes/b16-bug-origin && python3 tools/make_rewind.py
  -> assets/rewind/b16-rewind.mp4   (1920x1080, 30 fps, 48 frames = composition local frames 0..47, no audio)
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
0.0 / f0 until that file exists). B4 (v05, lane 5 FINAL): B4's OWN frames, rendered by the HyperFrames CLI (snapshot)
from a throwaway copy of hyperframes/b04-racenchase in a temp folder (B4's folder is never written): the dark title page
(05_GFX/shared/racenchase_title_page_dark_v05.jpg) at S 1.5 with page point (1093, 540) on the frame centre, tilted
-4 deg, pushed 100 -> 115% over B4 local 6-46 (sine.inOut), the pink highlighter on "Race'n'Chase" (16), the yellow
circle round "March 22, 1995" (28) and "It's called" printed above the title, so the rewind shows exactly B4's page.
Re-run after B4 changes too.
Usage: python3 tools/make_rewind.py [output_dir]   (default assets/rewind; another folder = dry run for comparisons)

Output frame j = composition local frame j (local = beat + 6). An 8x rewind of an edit frame e steps e -> e - 8 per
output frame; the B14 run is compressed (it jumps from shot to shot: 3 escape, 2 lights, 3 chase, then 1 frame per
burst game, newest to oldest), then 9 frames of B9's GTA 1, then B4's page run backwards every 8 frames from its last
page frame (B4 local 45, 115%, highlighted + circled) through 37, 29, 21, 13 (the circle and the highlighter unwind, the
eased push runs back out), landing on B4's opening framing (local 5: 100%, before "It's" on 6), held under the X7
dissolve.

v02 (REVISION_v02.md, VO 115%): every beat is ~6% shorter. B16's rewind is beat f-6..28 (local 0..33, the tape stops on
local 34 = beat 28; v01 beat 30) and the X7 dissolve local 34..46 (12f), so the clip is 48 frames (v01 52). The B14 shot
boundaries (escape / lights / chase / burst clips) and B14's last frame are read from B14's v02 shots, B9's R9.1 shot end
from B9's shots; the edit frames picked inside them are v02 frames (see plan()).
"""
import glob, json, os, shutil, subprocess, sys, tempfile
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
FOOT = os.path.join(PROJ, "assets", "footage")
OUT_DIR = os.path.join(PROJ, "assets", "rewind")
W, H, FPS = 1920, 1080, 30
N_FRAMES = 48                     # local 0..47 (the clip is used to local 46, the end of the X7 dissolve)

# ---- source in-points of the shots being rewound (seconds into the R-ID file) ----
B14 = {   # filled by load_inpoints() from hyperframes/b14-since/tesseract_shots.json (required)
    "escape": None, "lights": None, "roadblock": None, "chase": None,
    # burst: clip k (0..9) = edit frames 6k..6k+6; two moments per game (a = first, b = second clip)
    "burst": [],
}
# B9 L1 shot R9.1 (B9 f0-127): source_in_s / crop from lane E's tesseract_shots.json when it exists. Until then a
# PROVISIONAL GTA 1 police-chase moment: R9.1 @126.83-129.23 (the white police car on the red car's tail, the moment
# B2 also uses) with B2's crop 736:414:59:40 (16:9 inside the 4:3 picture). Flagged in BEAT_NOTES.
B9_R91_SRC_IN = 125.0
B9_R91_START_F = 0
B9_R91_END_F = 120
B9_R91_CROP = "736:414:59:40"
ROOT = os.path.dirname(os.path.dirname(PROJ))
B9_R91_SOURCE = "04_Broll/_originals/B02/R9.1__GTA 1 Police Chase 001 [HX8infRFBTc].mp4"
HF = os.path.dirname(PROJ)


def load_inpoints():
    """Overrides the defaults above with the live Tesseract shot lists, so the rewind always mirrors what B14 and B9
    actually show: hyperframes/b14-since/tesseract_shots.json (this lane) and hyperframes/b09-throughyou/... (lane E)."""
    global B9_R91_SRC_IN, B9_R91_START_F, B9_R91_CROP, B9_R91_SOURCE, B9_R91_END_F
    src = {"B14": "defaults", "B9": "defaults"}
    p14 = os.path.join(HF, "b14-since", "tesseract_shots.json")
    if os.path.exists(p14):
        shots = json.load(open(p14))["shots"]
        full = {s["id"]: s for s in shots}
        for key, sid in (("escape", "B14-escape"), ("lights", "B14-police-lights"), ("roadblock", "B14-gta5-roadblock-stars"),
                         ("chase", "B14-gta5-chase-stars")):
            if sid in full:
                B14[key] = {"rid": full[sid]["rid"], "start_f": full[sid]["start_f"], "end_f": full[sid]["end_f"],
                            "src_in": full[sid]["source_in_s"], "source": full[sid]["source"], "crop": full[sid].get("crop")}
        burst = sorted([s for s in shots if s.get("screen") == "L10"], key=lambda s: s["start_f"])
        if len(burst) == 10:
            B14["burst"] = [(s["rid"], s["source_in_s"], s["source"], s.get("crop"), s["start_f"], s["end_f"]) for s in burst]
        src["B14"] = os.path.relpath(p14, HF)
    p9 = os.path.join(HF, "b09-throughyou", "tesseract_shots.json")
    if os.path.exists(p9):
        r91 = [s for s in json.load(open(p9))["shots"] if s.get("rid") == "R9.1"]
        if r91:
            s = sorted(r91, key=lambda s: s["start_f"])[0]
            B9_R91_SRC_IN, B9_R91_START_F = float(s["source_in_s"]), int(s["start_f"])
            B9_R91_END_F = int(s["end_f"])
            B9_R91_CROP = s.get("crop")
            if s.get("source"): B9_R91_SOURCE = s["source"]
            src["B9"] = os.path.relpath(p9, HF)
    return src
# B4 v05 (lane 5 FINAL, b04-racenchase): the page is B4 local 0-45 (hard cut to the grid on 46); push 100 -> 115% over
# local 6-46 (sine.inOut, C.push); highlighter from 16 (8 f), circle from 28 (9 f), "It's" 6 / "called" 12. The rewind
# shows B4's own frames 45, 37, 29, 21, 13 (8x backwards) and lands on 5 (100%, no text yet).
B4_DIR = os.path.join(HF, "b04-racenchase")
B4_PAGE_LAST_F, B4_LAND_F, STEP = 45, 5, 8
DOC = {"b4": "hyperframes/b04-racenchase (snapshot of a temp copy)", "page": "05_GFX/shared/racenchase_title_page_dark_v05.jpg",
       "page_scale": 1.5, "page_point_on_centre": (1093, 540), "tilt_deg": -4, "push_from": 1.0, "push_to": 1.15,
       "push_f0": 6, "push_f1": 46, "push_ease": "sine.inOut", "page_last_f": B4_PAGE_LAST_F, "land_f": B4_LAND_F}


def ease_in_out_sine(p):
    import math
    return -(math.cos(math.pi * p) - 1) / 2


def b4_zoom_at(f):
    """B4's eased push value on B4 local frame f (documentation only: the frames themselves are B4's own)."""
    p = min(1.0, max(0.0, (f - DOC["push_f0"]) / (DOC["push_f1"] - DOC["push_f0"])))
    return DOC["push_from"] + (DOC["push_to"] - DOC["push_from"]) * ease_in_out_sine(p)


def snap_b4(frames_local, tmp):
    """B4's own frames at the given B4 local frames, rendered by the HyperFrames CLI from a throwaway copy of
    hyperframes/b04-racenchase (B4's folder is only read). Returns {local frame: png path}."""
    work = os.path.join(tmp, "b04-copy")
    shutil.copytree(B4_DIR, work, ignore=shutil.ignore_patterns(".hyperframes", "review", "prep", "node_modules"))
    out = os.path.join(tmp, "b04-snap")
    fs = sorted(set(frames_local))
    at = ",".join("%.5f" % (f / FPS + 0.00005) for f in fs)
    subprocess.run(["npx", "--yes", "hyperframes@0.9.52", "snapshot", work, "--at", at, "--no-end", "-o", out],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    pngs = sorted(glob.glob(os.path.join(out, "frame-*-at-*.png")), key=lambda p: int(os.path.basename(p).split("-")[1]))
    if len(pngs) != len(fs):
        sys.exit("make_rewind: B4 snapshot gave %d frames for %d times" % (len(pngs), len(fs)))
    return dict(zip(fs, pngs))


def b14_source(e):
    """B14 edit frame e (beat-relative) -> (rid, source seconds in the original, original path, crop). The shot
    boundaries come from B14's tesseract_shots.json (v02: escape f154, lights f126, chase f59, burst 9 x 6f + 5f)."""
    for key in ("escape", "lights", "roadblock", "chase"):      # v05: B14 split its chase shot at f91 (roadblock)
        s = B14[key]
        if s is not None and e >= s["start_f"]:
            return s["rid"], s["src_in"] + (e - s["start_f"]) / FPS, s["source"], s["crop"]
    for rid, src_in, source, crop, f0, f1 in B14["burst"]:
        if f0 <= e < f1:
            return rid, src_in + (e - f0) / FPS, source, crop
    raise SystemExit("make_rewind: B14 edit frame %d is in no shot" % e)


def plan():
    frames = []
    def add(kind, **kw):
        frames.append(dict(local=len(frames), beat=len(frames) - 6, kind=kind, **kw))
    end14 = B14["escape"]["end_f"]          # B14's last frame (v02: 177)
    # beat -6..2 (head handle + 3 frames): the escape shot rewinding from B14's last frame, 8 edit frames per output
    # frame; the handle continues it backward in time (= later source frames under B14's shut slats)
    for b in range(-6, 3):
        e = end14 - 8 * b
        rid, t, so, cr = b14_source(e); add("B14", rid=rid, edit_f=e, src_s=round(t, 4), source=so, crop=cr)
    # beat 3..4: police lights (v02 f126-154: edit 150, 142); beat 5..7: GTA 5 chase (v02 f59-126: edit 118, 110, 102)
    for e in (150, 142, 118, 110, 102):
        rid, t, so, cr = b14_source(e); add("B14", rid=rid, edit_f=e, src_s=round(t, 4), source=so, crop=cr)
    # beat 8..12: the L10 burst, one frame per game, newest to oldest (2013 -> 2001)
    for e in (52, 44, 28, 20, 4):
        rid, t, so, cr = b14_source(e); add("B14", rid=rid, edit_f=e, src_s=round(t, 4), source=so, crop=cr)
    # beat 13..21: B9's GTA 1 chase (R9.1, the L1 shot, v02 B9 f0-120) rewinding from its last frame, 8x, 9 frames
    for i in range(9):
        e = B9_R91_END_F - 8 * i
        add("B9", rid="R9.1", edit_f=e, src_s=round(B9_R91_SRC_IN + (e - B9_R91_START_F) / FPS, 4),
            source=B9_R91_SOURCE, crop=B9_R91_CROP)
    # beat 22..26: the 1995 design document = B4's own page frames run backwards at 8x from its last page frame (45, 37,
    # 29, 21, 13: 115% -> 101%, the circle and the highlighter unwind); beat 27.. (local 33 on): held at B4's opening
    # framing (local 5: 100%, before "It's") - the tape has stopped - under the X7 light-leak dissolve
    f4 = B4_PAGE_LAST_F
    while f4 > B4_LAND_F:
        add("B4", rid="R4.5", b4_local=f4, zoom=round(b4_zoom_at(f4), 5))
        f4 -= STEP
    while len(frames) < N_FRAMES:
        add("B4", rid="R4.5", b4_local=B4_LAND_F, zoom=round(b4_zoom_at(B4_LAND_F), 5))
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


def b4_frame(png, dst_png):
    im = Image.open(png)
    if im.mode == "RGBA":
        bg = Image.new("RGBA", im.size, (14, 14, 16, 255)); bg.alpha_composite(im); im = bg
    im = im.convert("RGB")
    if im.size != (W, H):
        sys.exit("make_rewind: B4 snapshot is %dx%d" % im.size)
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
    tmp = tempfile.mkdtemp(prefix="b16rw-")
    try:
        b4 = snap_b4([fr["b4_local"] for fr in frames if fr["kind"] == "B4"], tmp)
        for fr in frames:
            dst = os.path.join(tmp, "f%03d.png" % fr["local"])
            if fr["kind"] == "B4":
                b4_frame(b4[fr["b4_local"]], dst)
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
