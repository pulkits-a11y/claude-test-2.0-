#!/usr/bin/env python3
"""Put the footage each beat uses into its HyperFrames project.

  python3 tools/sync_footage.py hyperframes/b03-dundee      # reads <proj>/footage.json
  python3 tools/sync_footage.py --all                        # every beat project

footage.json:
  {"beat": "B3",
   "rids": ["R3.1", "R3.7", ...],
   "moments": {                                  # the window cut from the real clip, per R-ID
     "R3.7": {"in": 61.2, "out": 69.5,           # seconds in the ORIGINAL download
              "crop": "1440:1080:240:0",         # optional ffmpeg crop (w:h:x:y) in the ORIGINAL's stored pixels
                                                 # (ffprobe width x height), e.g. remove a 4:3 pillarbox
              "note": "team at computers, wide"}}}

Resolution per R-ID:
  1. a real still placed directly in 04_Broll/Bxx (R4.5 design-document scan) -> assets/footage/<RID>.png
  2. an original download in 04_Broll/_originals/<folder>/<RID>__*.mp4 AND a moment for it -> the window is
     cut to assets/footage/<RID>.mp4 (H.264, fits 1920x1080 keeping aspect, 30 fps CFR, no audio)
  3. otherwise the labelled stand-in 04_Broll/_placeholders/<RID>.mp4 (an original without a moment is
     reported as "needs-moment" so it is never used blindly)
assets/footage/SOURCES.json records what was used (for credits and the QA list).

Non-square pixels (e.g. R14.4, stored 2276x720 with SAR 320:569 = 1280x720 on screen): the crop is applied in
stored pixels first, then the pixel aspect is corrected to square, then the picture is fitted - never stretched.
tools/build_tesseract_picture.py uses the same crop convention.
"""
import glob, json, os, shutil, subprocess, sys

ROOT = "/home/user/claude-test-2.0-/RC_GTA-Origin"
VIDEO = (".mp4", ".mov", ".m4v", ".webm", ".mkv")
STILL = (".png", ".jpg", ".jpeg", ".webp")


def _beat_dirs(entry):
    return sorted(set([entry["folder"]] + [f"04_Broll/B{int(b[1:]):02d}" for b in entry["beats"].split(",") if b.startswith("B")] + ["04_Broll/Textures"]))


def find_real(entry):
    """Real media placed directly in 04_Broll/Bxx (stills such as R4.5, or trimmed clips)."""
    rid, hits = entry["rid"], []
    for d in _beat_dirs(entry):
        for pat in (f"{rid}__*", f"{rid}.*", f"{rid}_*"):
            hits += [h for h in glob.glob(f"{ROOT}/{d}/{pat}") if h.lower().endswith(VIDEO + STILL)]
    return sorted(set(hits))


def find_original(rid):
    hits = [h for h in glob.glob(f"{ROOT}/04_Broll/_originals/*/{rid}__*") if h.lower().endswith(VIDEO)]
    return sorted(hits)[0] if hits else None


def sar_of(src):
    """Sample (pixel) aspect ratio of the source as 'n:d' when it is not square, else None."""
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=sample_aspect_ratio",
                        "-of", "csv=p=0", src], capture_output=True, text=True).stdout.strip()
    try:
        n, d = (int(x) for x in r.split(":"))
    except ValueError:
        return None
    return f"{n}:{d}" if n > 0 and d > 0 and n != d else None


def cut(src, dst, m):
    vf = []
    if m.get("crop"):
        vf.append(f"crop={m['crop']}")
    if sar_of(src):  # anamorphic source: make the pixels square before fitting (else it comes out stretched)
        vf.append("scale=w='trunc(iw*sar/2)*2':h=ih:flags=lanczos")
        vf.append("setsar=1")
    vf.append("scale=w=1920:h=1080:force_original_aspect_ratio=decrease:force_divisible_by=2:flags=lanczos,setsar=1,fps=30")
    cmd = ["ffmpeg", "-nostdin", "-loglevel", "error", "-y", "-ss", str(m["in"]), "-i", src, "-t", str(float(m["out"]) - float(m["in"])),
           "-an", "-vf", ",".join(vf), "-c:v", "libx264", "-crf", "14", "-preset", "medium", "-pix_fmt", "yuv420p", "-movflags", "+faststart", dst]
    subprocess.run(cmd, check=True)


def sync(proj):
    proj = os.path.abspath(proj)
    spec = json.load(open(f"{proj}/footage.json"))
    moments = spec.get("moments", {})
    man = {e["rid"]: e for e in json.load(open(f"{ROOT}/04_Broll/broll_manifest.json"))["clips"]}
    out_dir = f"{proj}/assets/footage"
    os.makedirs(out_dir, exist_ok=True)
    prev = {}
    if os.path.exists(f"{out_dir}/SOURCES.json"):
        prev = json.load(open(f"{out_dir}/SOURCES.json"))
    report = {}
    for rid in spec.get("rids", []):
        e = man[rid]
        stills = [r for r in find_real(e) if r.lower().endswith(STILL)]
        orig = find_original(rid)
        if stills:
            for i, r in enumerate(stills):
                shutil.copy2(r, f"{out_dir}/{rid}{'' if i == 0 else '_' + str(i + 1)}{os.path.splitext(r)[1].lower()}")
            report[rid] = {"kind": "still", "files": [os.path.relpath(s, ROOT) for s in stills]}
        elif orig and rid in moments:
            m = moments[rid]
            entry = {"kind": "real", "source": os.path.relpath(orig, ROOT), "in": m["in"], "out": m["out"], "crop": m.get("crop"), "note": m.get("note")}
            if sar_of(orig):
                entry["sar"] = sar_of(orig)  # also forces a re-cut of copies made before the pixel-aspect fix
            dst = f"{out_dir}/{rid}.mp4"
            same = prev.get(rid) == entry and os.path.exists(dst)
            if not same:
                cut(orig, dst, m)
            report[rid] = entry
        else:
            ph = f"{ROOT}/04_Broll/_placeholders/{rid}.mp4"
            if not os.path.exists(ph):
                raise SystemExit(f"no footage and no placeholder for {rid}")
            shutil.copy2(ph, f"{out_dir}/{rid}.mp4")
            report[rid] = {"kind": "needs-moment" if orig else "placeholder", "source": os.path.relpath(ph, ROOT),
                           "original": os.path.relpath(orig, ROOT) if orig else None}
    json.dump(report, open(f"{out_dir}/SOURCES.json", "w"), indent=1)
    print(os.path.basename(proj), {k: v["kind"] for k, v in report.items()})


if __name__ == "__main__":
    if sys.argv[1] == "--all":
        for p in sorted(glob.glob(f"{ROOT}/hyperframes/b[0-9][0-9]-*")):
            if os.path.exists(f"{p}/footage.json"):
                sync(p)
    else:
        sync(sys.argv[1])
