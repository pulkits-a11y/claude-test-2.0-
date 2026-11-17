#!/usr/bin/env python3
"""Final assembly and export of RC_GTA-Origin (Tesseract), deterministic and re-runnable.

Golden rule: 00_Brief/GTA_VI_Edit_Plan.pdf (Toolchain + Handoff rules p.3-4, Audio mix and export settings
p.38-39). Steps:

  1. AUDIO   runs tools/build_tesseract_audio.py if .tesseract-work/audio.tsrct is missing or older than any
             of its inputs (beat cues.json files, timing/*.json, music/SFX plans, the VO, the script itself)
  2. PICTURE runs tools/build_tesseract_picture.py (-> .tesseract-work/picture.tsrct, always rebuilt)
  3. MERGE   `tsrct project merge --mode overlay --at 0` packages both documents' assets into one project, but it
             re-numbers every merged layer with random 16-digit ids. So the merged package only supplies the
             assets: the final document is the picture JSON plus the audio JSON (ids kept: picture 1..8999,
             audio >= 9000; dynamics concatenated; asset ids passed through the merge's assetMap, which shares
             byte-identical files) committed into it -> RC_GTA-Origin.tsrct, then `project check`.
  4. CHECKS  filmstrips of the merged project (overview + each beat that has Tesseract shots) in
             .tesseract-work/checks/strip_*.png
  5. EXPORT  07_Exports/.master_<version>.mp4 with `tsrct export` (1080p, 30 fps, external FFmpeg backend). The
             backend runs `ffmpeg ... -c:v libx264 -b:v 10000000 -g 30` and has no bitrate/2-pass option, so it is
             pointed at a wrapper (.tesseract-work/ffmpeg_master.py) that replaces only `-b:v N` with
             `-crf <--master-crf> -preset medium` (near-lossless master; --master-crf 0 keeps Tesseract's 10 Mbps).
             The mix is exported losslessly (`tsrct export-audio`) and the delivery file is encoded with FFmpeg
             to the plan's settings: H.264 High, 1920x1080, 30 fps constant, 2-pass VBR 16 Mbps (20 Mbps max),
             AAC 320 kbps, 48 kHz stereo -> 07_Exports/RC_GTA-Origin_<version>_16x9.mp4. Loudness is measured on
             the delivered AAC; only if it misses -14 LUFS +-1 / <= -1.0 dBTP, a measured two-pass loudnorm is
             applied to the delivery's audio (recipe recorded). Prints ffprobe + loudness.

v02 (REVISION_v02.md): the 115% voiceover (01_VO/VO_processed_115.wav + VO_words_115.json), the v02 beat map
(every duration from it), the music re-anchored on the new 'fun', S10 = B8's glitch (note 5), the whole-edit finish
(grain, vignette, dust overlay, chromatic aberration) and eased keyframes in the picture half. Disk: the merged
project is about 2.3 GB, so the picture intermediate (.tesseract-work/picture.tsrct, the same size) is deleted after a
successful merge (--keep-picture keeps it), and the build stops before a step that would not fit.

v03: `--preview` is a fast path for showing the client a result: the audio half as usual, the picture half with the
beat renders imported as ProRes 4444 proxies at the preview height (cached in .tesseract-work/proxies), no merge, no
filmstrips, no 2-pass: the picture project and the audio project are exported separately (720p by default, one x264
CRF pass) and muxed with the same mix -> 07_Exports/RC_GTA-Origin_<version>_preview.mp4 (+ checks/preview_report.json).
RC_GTA-Origin.tsrct is left as it is (the last full build).

v05 (REVISION_v05.md): the voiceover comes from the beat map's `vo_file` (01_VO/VO_processed_v05.wav, doc cuts A/B),
18 beats (B18 = the CTA end card, 05_GFX/renders/b18-cta.mov), edit 2288 f; the audio half reads the cues.json v05
schema and the 03_SFX/v05 library (both are audio inputs below); the picture finish has the v05 grain (size 1.2, 3.9%),
no global chromatic aberration, a light vignette on the CTA card that returns to full over its last 6 frames, and
CA + VHS wobble on Tesseract shots inside cues.json `archival` ranges.

Usage:  python3 tools/build_tesseract.py [--version v05] [--force-audio] [--skip-export] [--master-crf 14]
        python3 tools/build_tesseract.py --version v05 --preview [--preview-resolution 720p|1080p]
"""
from __future__ import annotations

import argparse
import glob
import json
import math
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / ".tesseract-work"
CHECKS = WORK / "checks"
EXPORTS = ROOT / "07_Exports"
TSRCT = Path("/root/.local/share/Tesseract/bin/tsrct")
FFMPEG = "/usr/bin/ffmpeg"
AUDIO_SCRIPT = ROOT / "tools/build_tesseract_audio.py"
PICTURE_SCRIPT = ROOT / "tools/build_tesseract_picture.py"
AUDIO = WORK / "audio.tsrct"
PICTURE = WORK / "picture.tsrct"
FINAL = ROOT / "RC_GTA-Origin.tsrct"
FINAL_JSON = WORK / "final.editable.json"
PIC_REPORT = CHECKS / "picture_report.json"
DELIVERY_REPORT = CHECKS / "delivery_report.json"
WRAPPER = WORK / "ffmpeg_master.py"
FPS = 30

# plan p.39 "16:9 master" + p.38 master loudness
V_BITRATE, V_MAXRATE, V_BUFSIZE = "16M", "20M", "40M"
A_BITRATE, A_RATE = "320k", "48000"
LUFS_TARGET, LUFS_TOL, TP_MAX = -14.0, 1.0, -1.0
LOUDNORM_TP = -1.5                       # target ceiling if a loudnorm pass is needed (0.5 dB AAC headroom)


def log(*a):
    print(*a, flush=True)


def run(cmd, check=True, **kw):
    r = subprocess.run([str(c) for c in cmd], capture_output=True, text=True, **kw)
    if check and r.returncode != 0:
        raise SystemExit("command failed (%d): %s\n%s\n%s" % (r.returncode, " ".join(map(str, cmd)), r.stdout[-3000:],
                                                             r.stderr[-3000:]))
    return r


def tsrct(*args, check=True):
    return run([TSRCT] + list(args), check=check)


def rel(p) -> str:
    try:
        return str(Path(p).resolve().relative_to(ROOT))
    except ValueError:
        return str(p)


# --------------------------------------------------------------------------------------------
# 1. audio freshness
# --------------------------------------------------------------------------------------------
def vo_inputs():
    """v05: the voiceover is the beat map's `vo_file` (+ VO_words_<tag>.json, VO_processing_<tag>.json beside it),
    the same rule as tools/build_tesseract_audio.py."""
    try:
        bm = json.loads((ROOT / "timing/beat_map.json").read_text())
    except (OSError, ValueError):
        bm = {}
    vo = ROOT / (bm.get("vo_file") or "01_VO/VO_processed_115.wav")
    tag = vo.stem[len("VO_processed_"):] if vo.stem.startswith("VO_processed_") else vo.stem
    words = ROOT / bm["words_file"] if bm.get("words_file") else vo.with_name("VO_words_%s.json" % tag)
    return [vo, words, vo.with_name("VO_processing_%s.json" % tag)]


def audio_inputs():
    pats = ["hyperframes/*/cues.json", "timing/*.json", "02_Music/music_plan.json", "03_SFX/sfx_plan.json",
            "03_SFX/sfx_analysis.json", "03_SFX/v05/*", "STORYBOARD.md", ".tesseract-work/cues_v01_snapshot.json",
            "tools/build_tesseract_audio.py"]
    out = [p for p in vo_inputs() if p.exists()]
    for p in pats:
        out += [Path(x) for x in glob.glob(str(ROOT / p))]
    return out


def audio_stale():
    if not AUDIO.exists():
        return "missing"
    t = AUDIO.stat().st_mtime
    newer = [rel(p) for p in audio_inputs() if p.stat().st_mtime > t]
    return ("newer inputs: " + ", ".join(sorted(newer))) if newer else None


# --------------------------------------------------------------------------------------------
# 3. merge
# --------------------------------------------------------------------------------------------
def walk(layers):
    for L in layers:
        yield L
        if L.get("type") == "Group":
            yield from walk(L.get("layers") or [])


def remap_assets(layers, amap):
    n = 0
    for L in walk(layers):
        src = L.get("source")
        if isinstance(src, dict) and src.get("assetId") in amap and amap[src["assetId"]] != src["assetId"]:
            src["assetId"] = amap[src["assetId"]]
            n += 1
    return n


def free_gb(path: Path = ROOT) -> float:
    return shutil.disk_usage(str(path)).free / 1e9


def need_space(gb: float, what: str):
    f = free_gb()
    if f < gb:
        raise SystemExit("not enough disk for %s: %.1f GB free, about %.1f GB needed" % (what, f, gb))
    log("  disk: %.1f GB free (%s needs about %.1f GB)" % (f, what, gb))


def merge(final: Path, keep_picture: bool = False):
    tmp = WORK / "merge.tmp.tsrct"
    if tmp.exists():
        tmp.unlink()
    # the merge writes a full package (about the size of the picture half) next to the old final project
    need_space(PICTURE.stat().st_size / 1e9 * 1.05 + 0.3, "the merged package")
    r = json.loads(tsrct("project", "merge", "--project", PICTURE, "--from", AUDIO, "--mode", "overlay", "--at", "0",
                         "--output", tmp).stdout)
    src = r["sources"][0]
    amap = src.get("assetMap", {})
    # the documents as authored (fresh checkouts)
    pj, aj, mj = WORK / "picture.checkout.json", WORK / "audio.checkout.json", WORK / "merged.checkout.json"
    tsrct("project", "checkout", "--project", PICTURE, "--output", pj)
    tsrct("project", "checkout", "--project", AUDIO, "--output", aj)
    tsrct("project", "checkout", "--project", tmp, "--output", mj)
    pic, aud, mer = (json.loads(p.read_text()) for p in (pj, aj, mj))
    deleted = None
    if not keep_picture:
        # `project commit` writes a new package next to the old one (temp + rename), so the merged package exists
        # twice for a moment; the picture half (about the same size) is no longer needed once checked out.
        deleted = round(PICTURE.stat().st_size / 1e9, 2)
        PICTURE.unlink()
        log("  deleted the picture intermediate %s (%.1f GB; its JSON is %s)" % (rel(PICTURE), deleted, rel(pj)))
    need_space(tmp.stat().st_size / 1e9 + 0.3, "committing the merged package")
    for k in ("dimensions", "duration", "backgroundColor", "colorManagement"):
        if json.dumps(pic.get(k)) != json.dumps(aud.get(k)):
            raise SystemExit("picture/audio differ in %s: %s vs %s" % (k, pic.get(k), aud.get(k)))
    pids = [L["id"] for L in walk(pic["composition"]["layers"])]
    aids = [L["id"] for L in walk(aud["composition"]["layers"])]
    if max(pids) >= 9000 or min(aids) < 9000 or set(pids) & set(aids):
        raise SystemExit("layer id ranges overlap (picture %d..%d, audio %d..%d)" % (min(pids), max(pids), min(aids), max(aids)))
    alayers = json.loads(json.dumps(aud["composition"]["layers"]))
    n_remap = remap_assets(alayers, amap)
    doc = json.loads(json.dumps(mer))                 # keeps any document fields the merge wrote
    for k in ("dimensions", "duration", "backgroundColor", "colorManagement"):
        doc[k] = pic[k]
    doc["composition"]["layers"] = pic["composition"]["layers"] + alayers
    dp = (pic["composition"].get("dynamics") or {}).get("entries", [])
    da = (aud["composition"].get("dynamics") or {}).get("entries", [])
    doc["composition"]["dynamics"] = {"entries": dp + da}
    FINAL_JSON.write_text(json.dumps(doc, indent=1) + "\n")
    c = json.loads(tsrct("project", "commit", "--project", tmp, "--file", FINAL_JSON).stdout)
    chk = json.loads(tsrct("project", "check", "--project", tmp, check=False).stdout or "{}")
    if chk.get("valid") is not True:
        raise SystemExit("merged project check failed: %s" % json.dumps(chk)[:3000])
    # verify: every asset referenced by the final document is packaged, ids kept
    back = WORK / "final.verify.json"
    tsrct("project", "checkout", "--project", tmp, "--output", back)
    fin = json.loads(back.read_text())
    ids = sorted(L["id"] for L in walk(fin["composition"]["layers"]))
    assets = sorted({L["source"]["assetId"] for L in walk(fin["composition"]["layers"]) if isinstance(L.get("source"), dict)})
    if ids != sorted(pids + aids):
        raise SystemExit("layer ids changed on commit")
    for p in (pj, aj, mj, back):
        p.unlink()
    tmp.replace(final)
    for f in WORK.glob("merge.tmp*"):              # anything the merge/commit left behind
        f.unlink()
    return {"merge_warnings": r.get("warnings", []), "picture_intermediate_deleted_gb": deleted,
            "asset_map_shared": {k: v for k, v in amap.items() if k != v},
            "asset_refs_remapped": n_remap, "commit_warnings": c.get("warnings", []),
            "check": {"valid": chk.get("valid"), "warnings": chk.get("warnings"), "diagnostics": chk.get("diagnostics")},
            "layers": {"picture": len(pids), "audio": len(aids), "picture_max_id": max(pids), "audio_min_id": min(aids)},
            "dynamics": {"picture": len(dp), "audio": len(da)}, "assets_referenced": len(assets)}


# --------------------------------------------------------------------------------------------
# 4. filmstrips
# --------------------------------------------------------------------------------------------
def fms(frame: int) -> int:
    """Request time inside the frame's display interval (ceil of n*1000/30)."""
    return -((-int(frame) * 1000) // FPS)


def filmstrips(final: Path, edit_end_s: float):
    out = []
    ov = CHECKS / "strip_overview.png"
    tsrct("filmstrip", "--project", final, "--start-ms", "0", "--duration-ms", str(int(edit_end_s * 1000) - 1),
          "--interval-ms", "2000", "--items-per-row", "7", "--output", ov)
    out.append(rel(ov))
    rep = json.loads(PIC_REPORT.read_text())
    by_beat = {}
    for s in rep["shots"]:
        by_beat.setdefault(s["beat"], []).append(s)
    for beat, shots in by_beat.items():
        fr = []
        for s in shots:
            a, b = s["edit_frames"]
            n = b - a
            pts = [a - 1, a, a + 2, a + 4, a + 8] if n > 12 else [a, a + n // 2]
            if s.get("x8"):
                pts += list(range(a, min(b, a + 3))) if "in" in s["x8"] else list(range(max(a, b - 3), b))
            if n > 12:
                pts += [a + n // 2, b - 1]
            fr += [p for p in pts if 0 <= p and a - 1 <= p < b]
        fr = sorted(set(fr))
        if len(fr) > 20:                      # keep it readable: thin out evenly, keep the first/last
            step = len(fr) / 20.0
            fr = sorted({fr[int(i * step)] for i in range(20)} | {fr[0], fr[-1]})
        p = CHECKS / ("strip_%s.png" % beat)
        tsrct("filmstrip", "--project", final, "--timestamps-ms", ",".join(str(fms(f)) for f in fr),
              "--items-per-row", "4", "--tile-width", "384", "--tile-height", "216", "--output", p)
        out.append("%s (frames %s)" % (rel(p), ",".join(map(str, fr))))
    return out


# --------------------------------------------------------------------------------------------
# 5. export + delivery
# --------------------------------------------------------------------------------------------
PREVIEW_CRF, PREVIEW_PRESET = 20, "veryfast"


def write_wrapper(crf: int, preset: str = "medium"):
    WRAPPER.write_text('''#!/usr/bin/env python3
"""Tesseract external-FFmpeg backend wrapper (written by tools/build_tesseract.py).
Passes every argument through to %s, except the video bitrate cap `-b:v N`, which becomes
`-crf %d -preset %s` (the master: near-lossless before the 2-pass delivery encode; the preview: one quick pass)."""
import os, sys
a = sys.argv[1:]
out, i = [], 0
while i < len(a):
    if a[i] == "-b:v" and i + 1 < len(a):
        out += ["-crf", "%d", "-preset", "%s"]
        i += 2
        continue
    out.append(a[i])
    i += 1
with open(%r, "a") as f:
    f.write(" ".join(a) + "\\n  -> " + " ".join(out) + "\\n")
os.execv(%r, [%r] + out)
''' % (FFMPEG, crf, preset, crf, preset, str(WORK / "ffmpeg_master.log"), FFMPEG, FFMPEG))
    WRAPPER.chmod(0o755)


def export_master(final: Path, out: Path, crf: int, resolution: str = "1080p", preset: str = "medium"):
    elog = WORK / "export.log"
    flog = WORK / "ffmpeg_master.log"
    if flog.exists():
        flog.unlink()
    ff = FFMPEG
    if crf > 0:
        write_wrapper(crf, preset)
        ff = str(WRAPPER)
    tmp = out.with_name(out.stem + ".tmp.mp4")
    cmd = [TSRCT, "export", "--project", final, "--output", tmp, "--resolution", resolution, "--fps", str(FPS),
           "--format", "mp4", "--encoder-backend", "external-ffmpeg-command", "--ffmpeg-path", ff, "--json"]
    t0 = time.time()
    with open(elog, "w") as ef:
        r = subprocess.run([str(c) for c in cmd], stdout=subprocess.PIPE, stderr=ef, text=True)
    if r.returncode != 0:
        raise SystemExit("export failed (%d); see %s" % (r.returncode, rel(elog)))
    tmp.replace(out)
    return {"seconds": round(time.time() - t0, 1), "command": " ".join(map(str, cmd)).replace(str(tmp), str(out)),
            "result": r.stdout.strip()[-500:], "ffmpeg_calls": flog.read_text() if flog.exists() else None}


def ffprobe(path: Path) -> dict:
    r = run(["ffprobe", "-v", "error", "-show_entries",
             "format=duration,bit_rate,format_name:stream=index,codec_type,codec_name,profile,width,height,pix_fmt,"
             "r_frame_rate,avg_frame_rate,nb_frames,bit_rate,sample_rate,channels,channel_layout,color_space,"
             "color_transfer,color_primaries,color_range", "-of", "json", path])
    return json.loads(r.stdout)


def loudness(path: Path) -> dict:
    """EBU R128 integrated loudness / LRA / true peak of the first audio stream (FFmpeg ebur128)."""
    r = run(["ffmpeg", "-nostdin", "-hide_banner", "-nostats", "-i", path, "-map", "0:a:0",
             "-af", "ebur128=peak=true", "-f", "null", "-"], check=True)
    txt = r.stderr[r.stderr.rfind("Summary:"):]
    get = lambda k: float(re.search(k + r":\s+(-?[\d.]+|-inf)", txt).group(1).replace("-inf", "-999"))
    return {"integrated_lufs": get("I"), "lra_lu": get("LRA"), "true_peak_dbtp": get("Peak")}


def ok_loud(m) -> bool:
    return abs(m["integrated_lufs"] - LUFS_TARGET) <= LUFS_TOL and m["true_peak_dbtp"] <= TP_MAX


def encode_delivery(master: Path, wav: Path, out: Path, edit_end_s: float):
    plog = WORK / "x264_2pass"
    common = ["-c:v", "libx264", "-profile:v", "high", "-preset", "slow", "-b:v", V_BITRATE, "-maxrate", V_MAXRATE,
              "-bufsize", V_BUFSIZE, "-pix_fmt", "yuv420p", "-r", str(FPS), "-fps_mode", "cfr",
              "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709", "-color_range", "tv",
              "-passlogfile", plog]
    t = "%.3f" % edit_end_s
    p1 = ["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", master, "-map", "0:v:0", "-t", t] + common + \
         ["-pass", "1", "-an", "-f", "null", "/dev/null"]
    tmp = out.with_name(out.stem + ".tmp.mp4")
    p2 = ["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", master, "-i", wav, "-map", "0:v:0", "-map", "1:a:0",
          "-t", t] + common + ["-pass", "2", "-c:a", "aac", "-b:a", A_BITRATE, "-ar", A_RATE, "-ac", "2",
                               "-movflags", "+faststart", tmp]
    run(p1)
    run(p2)
    for f in glob.glob(str(plog) + "*"):
        os.unlink(f)
    tmp.replace(out)
    return {"pass1": " ".join(map(str, p1)), "pass2": " ".join(map(str, p2)).replace(str(tmp), str(out))}


def loudnorm_fix(delivery: Path, wav: Path, measured_delivery: dict):
    """Two-pass loudnorm on the delivery's audio only (video stream copied). The AAC encoder can overshoot the
    WAV's true peak at broadband transients (measured +1.5 dB at the B8 S08 glitch), so the result is measured
    after encoding and the true-peak target is lowered step by step until the encoded file passes."""
    attempts = []
    tmp = delivery.with_name(delivery.stem + ".ln.tmp.mp4")
    fixed = WORK / "checks" / "delivery_mix_loudnorm.wav"
    for tp in (LOUDNORM_TP, LOUDNORM_TP - 0.5, LOUDNORM_TP - 1.0, LOUDNORM_TP - 1.5):
        m = run(["ffmpeg", "-nostdin", "-hide_banner", "-i", wav, "-af",
                 "loudnorm=I=%.1f:TP=%.1f:LRA=11:print_format=json" % (LUFS_TARGET, tp), "-f", "null", "-"]).stderr
        js = json.loads(m[m.rfind("{"):m.rfind("}") + 1])
        af = ("loudnorm=I=%.1f:TP=%.1f:LRA=11:measured_I=%s:measured_TP=%s:measured_LRA=%s:measured_thresh=%s:"
              "offset=%s:linear=true:print_format=json" % (LUFS_TARGET, tp, js["input_i"], js["input_tp"],
                                                           js["input_lra"], js["input_thresh"], js["target_offset"]))
        r2 = run(["ffmpeg", "-nostdin", "-hide_banner", "-y", "-i", wav, "-af", af, "-ar", A_RATE, "-c:a", "pcm_f32le",
                  fixed]).stderr
        js2 = json.loads(r2[r2.rfind("{"):r2.rfind("}") + 1])
        run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", delivery, "-i", fixed, "-map", "0:v:0", "-map", "1:a:0",
             "-c:v", "copy", "-c:a", "aac", "-b:a", A_BITRATE, "-ar", A_RATE, "-ac", "2", "-movflags", "+faststart", tmp])
        got = loudness(tmp)
        attempts.append({"tp_target": tp, "pass1_measured": js, "pass2_filter": af,
                         "normalization_type": js2.get("normalization_type"), "encoded_result": got})
        if ok_loud(got):
            tmp.replace(delivery)
            return {"reason": measured_delivery, "attempts": attempts, "pass2_filter": af,
                    "note": "audio only; video stream copied from the 2-pass encode"}
    tmp.unlink()
    return {"reason": measured_delivery, "attempts": attempts, "pass2_filter": None,
            "note": "FAILED: no attempt met the targets; the delivery keeps the unprocessed mix"}


# --------------------------------------------------------------------------------------------
# v03 preview
# --------------------------------------------------------------------------------------------
def preview(args, report: dict, edit_end_s: float):
    h = 720 if args.preview_resolution == "720p" else 1080
    renders = sum(p.stat().st_size for p in (ROOT / "05_GFX/renders").glob("*.mov")) / 1e9
    est = renders * (0.35 if h < 1080 else 1.0)          # ProRes 4444 q9 at 720p is about a third of the renders
    old_pic = PICTURE.stat().st_size / 1e9 if PICTURE.exists() else 0.0
    if free_gb() + old_pic < 3 * est + 0.8:              # proxies + the package (twice while importing) + export cache
        raise SystemExit("not enough disk for the preview: %.1f GB free, about %.1f GB needed" % (free_gb(), 3 * est + 0.8))
    log("[2/3] picture: %s%s" % (rel(PICTURE_SCRIPT), " (beat renders as %dp ProRes 4444 proxies)" % h if h < 1080 else ""))
    r = subprocess.run([sys.executable, str(PICTURE_SCRIPT)] + (["--render-proxy", str(h)] if h < 1080 else []),
                       cwd=str(ROOT))
    if r.returncode != 0:
        raise SystemExit("picture script failed")
    out = EXPORTS / ("RC_GTA-Origin_%s_preview.mp4" % args.version)
    log("[3/3] preview %s: picture %s (single x264 pass, CRF %d %s) + the audio half's mix" % (
        rel(out), args.preview_resolution, PREVIEW_CRF, PREVIEW_PRESET))
    need_space(est + 0.5, "the preview export (Tesseract unpacks the packaged media while exporting)")
    vid = WORK / "preview_video.mp4"
    report["preview_export"] = export_master(PICTURE, vid, PREVIEW_CRF, args.preview_resolution, PREVIEW_PRESET)
    wav = CHECKS / "preview_mix.wav"
    tsrct("export-audio", "--project", AUDIO, "--output", wav)
    EXPORTS.mkdir(exist_ok=True)
    tmp = out.with_name(out.stem + ".tmp.mp4")
    run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", vid, "-i", wav, "-map", "0:v:0", "-map", "1:a:0",
         "-t", "%.3f" % edit_end_s, "-c:v", "copy", "-c:a", "aac", "-b:a", A_BITRATE, "-ar", A_RATE, "-ac", "2",
         "-movflags", "+faststart", tmp])
    tmp.replace(out)
    vid.unlink()
    if not args.keep_picture and PICTURE.exists():
        PICTURE.unlink()                              # a proxy build: never mistaken for the full picture half
    ld = loudness(out)
    pr = ffprobe(out)
    v = next(s_ for s_ in pr["streams"] if s_["codec_type"] == "video")
    report["preview"] = {"path": rel(out), "resolution": args.preview_resolution, "render_proxies": h < 1080,
                         "ffprobe": pr, "loudness": ld, "loudness_ok": ok_loud(ld), "size_bytes": out.stat().st_size,
                         "mix_wav": rel(wav)}
    log("\nPREVIEW %s: %s %dx%d %s fps, %s frames, %.1f MB; mix %.1f LUFS, %.1f dBTP (%s); %.0f s for the export" % (
        rel(out), v["codec_name"], v["width"], v["height"], v["r_frame_rate"], v.get("nb_frames"),
        out.stat().st_size / 1e6, ld["integrated_lufs"], ld["true_peak_dbtp"],
        "OK" if ok_loud(ld) else "outside -14 +-1 LUFS / -1 dBTP: the full build's delivery step corrects it",
        report["preview_export"]["seconds"]))
    (CHECKS / "preview_report.json").write_text(json.dumps(report, indent=1) + "\n")
    log("report: %s" % rel(CHECKS / "preview_report.json"))


# --------------------------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--version", default="v05", help="version tag in the export names (default v05)")
    ap.add_argument("--preview", action="store_true",
                    help="fast client preview: renders as proxies, no merge, no filmstrips, no 2-pass, same mix -> "
                         "07_Exports/RC_GTA-Origin_<version>_preview.mp4")
    ap.add_argument("--preview-resolution", choices=("720p", "1080p"), default="720p")
    ap.add_argument("--keep-picture", action="store_true",
                    help="keep .tesseract-work/picture.tsrct (about 2.3 GB) after the merge")
    ap.add_argument("--force-audio", action="store_true", help="rebuild the audio half even if it is up to date")
    ap.add_argument("--skip-export", action="store_true", help="build, merge and filmstrips only")
    ap.add_argument("--skip-filmstrips", action="store_true")
    ap.add_argument("--master-crf", type=int, default=14,
                    help="x264 CRF of the master via the backend wrapper (0 = Tesseract's own 10 Mbps)")
    args = ap.parse_args()
    if not re.fullmatch(r"[A-Za-z0-9._-]+", args.version):
        raise SystemExit("bad --version")
    CHECKS.mkdir(parents=True, exist_ok=True)
    bm = json.loads((ROOT / "timing/beat_map.json").read_text())
    edit_end_s = float(bm["edit_end_s"])
    report = {"version": args.version, "tsrct": tsrct("--version").stdout.strip(), "edit_end_s": edit_end_s}

    # 1. audio
    why = "forced" if args.force_audio else audio_stale()
    if why:
        log("[1/5] audio: rebuilding (%s)" % why)
        r = subprocess.run([sys.executable, str(AUDIO_SCRIPT)], cwd=str(ROOT))
        if r.returncode != 0:
            raise SystemExit("audio script failed")
    else:
        log("[1/5] audio: %s is up to date" % rel(AUDIO))
    report["audio"] = {"rebuilt": bool(why), "why": why}
    if args.preview:
        return preview(args, report, edit_end_s)

    # 2. picture (the old intermediate is deleted first by the picture script; it needs about the renders' size)
    log("[2/5] picture: running %s" % rel(PICTURE_SCRIPT))
    renders = sum(p.stat().st_size for p in (ROOT / "05_GFX/renders").glob("*.mov")) / 1e9
    old_pic = PICTURE.stat().st_size / 1e9 if PICTURE.exists() else 0.0
    need = 2 * renders + 0.5                        # every import rewrites the package: twice its size at the end
    if free_gb() + old_pic < need and FINAL.exists():
        gb = FINAL.stat().st_size / 1e9             # this build replaces it anyway; make room for the picture half
        FINAL.unlink()
        log("  deleted the previous %s early (%.1f GB; this build writes a new one) to make room" % (rel(FINAL), gb))
    if free_gb() + old_pic < need:
        raise SystemExit("not enough disk for the picture half: %.1f GB free (+%.1f GB old picture.tsrct), about "
                         "%.1f GB needed" % (free_gb(), old_pic, need))
    r = subprocess.run([sys.executable, str(PICTURE_SCRIPT)], cwd=str(ROOT))
    if r.returncode != 0:
        raise SystemExit("picture script failed")

    # 3. merge
    log("[3/5] merge -> %s" % rel(FINAL))
    report["merge"] = merge(FINAL, args.keep_picture)
    m = report["merge"]
    log("  one composition: %d picture layers (ids <= %d) + %d audio layers (ids >= %d), dynamics %d + %d, "
        "%d assets referenced, check valid=%s, shared identical assets %s" % (
            m["layers"]["picture"], m["layers"]["picture_max_id"], m["layers"]["audio"], m["layers"]["audio_min_id"],
            m["dynamics"]["picture"], m["dynamics"]["audio"], m["assets_referenced"], m["check"]["valid"],
            m["asset_map_shared"] or "none"))

    # 4. filmstrips
    if not args.skip_filmstrips:
        log("[4/5] filmstrips")
        report["filmstrips"] = filmstrips(FINAL, edit_end_s)
        for f in report["filmstrips"]:
            log("  " + f)

    # 5. export
    if args.skip_export:
        log("[5/5] export skipped (--skip-export)")
    else:
        EXPORTS.mkdir(exist_ok=True)
        master = EXPORTS / (".master_%s.mp4" % args.version)
        delivery = EXPORTS / ("RC_GTA-Origin_%s_16x9.mp4" % args.version)
        log("[5/5] export master %s (tsrct export, external FFmpeg backend, master CRF %s)" % (
            rel(master), args.master_crf or "off (10 Mbps)"))
        need_space(FINAL.stat().st_size / 1e9 + 0.8, "the export (Tesseract unpacks the packaged media into /tmp "
                                                      "while exporting) + the CRF 14 master (about 0.7 GB)")
        report["master"] = export_master(FINAL, master, args.master_crf)
        log("  master done in %.0f s" % report["master"]["seconds"])
        wav = CHECKS / "delivery_mix.wav"
        tsrct("export-audio", "--project", FINAL, "--output", wav)
        report["mix_wav"] = {"path": rel(wav), "loudness": loudness(wav)}
        log("  mix (tsrct export-audio): %s" % report["mix_wav"]["loudness"])
        log("  delivery encode (2-pass) -> %s" % rel(delivery))
        report["delivery_encode"] = encode_delivery(master, wav, delivery, edit_end_s)
        ld = loudness(delivery)
        report["delivery_loudness_first"] = ld
        if not ok_loud(ld):
            log("  delivery loudness %s misses -14 +-1 LUFS / <= -1 dBTP: two-pass loudnorm on the audio" % ld)
            report["loudnorm"] = loudnorm_fix(delivery, wav, ld)
            ld = loudness(delivery)
        else:
            report["loudnorm"] = None
        report["delivery"] = {"path": rel(delivery), "ffprobe": ffprobe(delivery), "loudness": ld,
                              "loudness_ok": ok_loud(ld), "size_bytes": delivery.stat().st_size}
        pr = report["delivery"]["ffprobe"]
        v = next(s for s in pr["streams"] if s["codec_type"] == "video")
        a = next(s for s in pr["streams"] if s["codec_type"] == "audio")
        log("\nDELIVERY %s" % rel(delivery))
        log("  video: %s %s %dx%d %s %s fps, %s frames, %.2f Mbps, %s/%s/%s %s" % (
            v["codec_name"], v.get("profile"), v["width"], v["height"], v["pix_fmt"], v["r_frame_rate"],
            v.get("nb_frames"), int(v.get("bit_rate", 0)) / 1e6, v.get("color_primaries"), v.get("color_transfer"),
            v.get("color_space"), v.get("color_range")))
        log("  audio: %s %s Hz %s ch (%s), %.0f kbps" % (a["codec_name"], a["sample_rate"], a["channels"],
                                                         a.get("channel_layout"), int(a.get("bit_rate", 0)) / 1e3))
        log("  container: %s, %.3f s, %.2f Mbps total, %.1f MB" % (pr["format"]["format_name"], float(pr["format"]["duration"]),
                                                                   int(pr["format"]["bit_rate"]) / 1e6,
                                                                   delivery.stat().st_size / 1e6))
        log("  loudness: %.1f LUFS integrated, %.1f dBTP true peak, LRA %.1f LU -> %s" % (
            ld["integrated_lufs"], ld["true_peak_dbtp"], ld["lra_lu"],
            "OK (-14 +-1 LUFS, <= -1 dBTP)" if ok_loud(ld) else "OUT OF SPEC"))
        if report["loudnorm"]:
            log("  loudnorm applied: %s" % report["loudnorm"]["pass2_filter"])
    DELIVERY_REPORT.write_text(json.dumps(report, indent=1) + "\n")
    log("\nreport: %s" % rel(DELIVERY_REPORT))


if __name__ == "__main__":
    main()
