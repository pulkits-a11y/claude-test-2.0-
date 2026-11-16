#!/usr/bin/env python3
"""Automated parts of the plan's final QA checklist (QA.md). Run from RC_GTA-Origin/:

  python3 tools/qa_checks.py captions            # QA 2: every T1 caption vs the voiceover words (+/-2f, <= 4 words)
  python3 tools/qa_checks.py styles              # QA 3 + 4: featured T-styles per beat, glitch / siren motif use
  python3 tools/qa_checks.py video <file.mp4>    # QA 1, 5, 6, 11, 13 on an export: first frames, still runs,
                                                 # the "fun" frame, loudness, export settings
Writes 07_Exports/qa/<check>.json and prints a summary.
"""
import glob, html, json, os, re, subprocess, sys

ROOT = "/home/user/claude-test-2.0-/RC_GTA-Origin"
FPS = 30
OUT = f"{ROOT}/07_Exports/qa"


def norm(w):
    return re.sub(r"[^a-z0-9']", "", w.lower().replace("\u2019", "'"))


def beats():
    return json.load(open(f"{ROOT}/timing/beat_map.json"))["beats"]


def elements(src, cls):
    """(attrs, text) of every div whose class list contains `cls` (static markup)."""
    out = []
    for m in re.finditer(r'<div\b([^>]*\bclass="[^"]*\b%s\b[^"]*"[^>]*)>(.*?)</div>' % re.escape(cls), src, re.S):
        attrs, inner = m.group(1), m.group(2)
        g = lambda k: (re.search(r'\b%s="([^"]*)"' % k, attrs) or [None, None])[1]
        out.append({"id": g("id") or "?", "start": float(g("data-start") or "nan"), "dur": float(g("data-duration") or "nan"),
                    "text": html.unescape(re.sub(r"<[^>]+>", " ", inner)).split()})
    return out


def check_captions():
    rep, problems = {}, []
    for b in beats():
        comp = b["composition"]["id"]
        src = open(f"{ROOT}/hyperframes/{comp}/index.html").read()
        words = b["words"]
        wn = [norm(w["text"]) for w in words]
        caps = sorted(elements(src, "rc-t1"), key=lambda c: c["start"])
        covered, rows = set(), []
        beat_end_local = (6 + b["dur_frames"]) / FPS
        for c in caps:
            toks = [norm(t) for t in c["text"] if norm(t)]
            row = {"id": c["id"], "text": " ".join(c["text"]), "start_f_local": round(c["start"] * FPS, 2),
                   "end_f_local": round((c["start"] + c["dur"]) * FPS, 2), "n_words": len(toks)}
            cands = [j for j in range(len(words)) if toks and wn[j] == toks[0] and wn[j:j + len(toks)] == toks]
            if not cands:
                row["error"] = "text does not match the voiceover words of this beat"
            else:
                j = min(cands, key=lambda k: abs(words[k]["comp_t"] - c["start"]))
                covered.update(range(j, j + len(toks)))
                word_f = words[j]["comp_t"] * FPS
                row["word_f_local"] = round(word_f, 2)
                if c["start"] * FPS <= 6.001:                          # starts in the head handle: visible from the cut
                    off = 6 - word_f if word_f > 6 else 0.0
                else:
                    off = c["start"] * FPS - word_f
                row["offset_f"] = round(off, 2)
                if abs(off) > 2.0:
                    row["error"] = "starts %.2f frames from its first word" % off
            if len(toks) > 4:
                row["error"] = (row.get("error", "") + "; " if row.get("error") else "") + "more than 4 words"
            rows.append(row)
            if "error" in row:
                problems.append("%s %s: %s (%r)" % (b["id"], c["id"], row["error"], row["text"]))
        last = rows[-1] if rows else None
        uncovered = [words[k]["text"] for k in range(len(words)) if k not in covered]
        rep[b["id"]] = {"composition": comp, "captions": rows, "words_not_in_T1": uncovered,
                        "last_caption_end_vs_beat_end_f": round(last["end_f_local"] - beat_end_local * FPS, 2) if last else None}
    os.makedirs(OUT, exist_ok=True)
    json.dump({"problems": problems, "beats": rep}, open(f"{OUT}/captions.json", "w"), indent=1)
    for bid, r in rep.items():
        print("%-4s %2d captions; words shown by other styles or not shown: %s; last T1 ends %s f vs beat end"
              % (bid, len(r["captions"]), " ".join(r["words_not_in_T1"]) or "-", r["last_caption_end_vs_beat_end_f"]))
    print("PROBLEMS:" if problems else "no caption problems", *problems, sep="\n  ")


def check_styles():
    rep = {}
    for b in beats():
        comp = b["composition"]["id"]
        src = open(f"{ROOT}/hyperframes/{comp}/index.html").read()
        styles = sorted(set(re.findall(r'\brc-(t(?:[2-9]|10))\b', src)), key=lambda s: int(s[1:]))
        motifs = {k: bool(re.search(p, src, re.I)) for k, p in
                  {"X4": r"X\.tear|rc-x4|\bx4\b", "T10": r"rc-t10", "rgb_split": r"rgb[-_ ]?split|chromaticAberration\"?:\s*0\.[1-9]",
                   "X9": r"X\.siren|rc-x9|siren[-_ ]?wash"}.items()}
        rep[b["id"]] = {"composition": comp, "featured_T": styles, "motifs": motifs}
        print("%-4s %-28s %s" % (b["id"], ",".join(styles) or "-", " ".join(k for k, v in motifs.items() if v)))
    os.makedirs(OUT, exist_ok=True)
    json.dump(rep, open(f"{OUT}/styles.json", "w"), indent=1)


def ffprobe(path, *entries):
    r = subprocess.run(["ffprobe", "-v", "error", *entries, "-of", "json", path], capture_output=True, text=True)
    return json.loads(r.stdout)


def check_video(path):
    rep = {}
    v = ffprobe(path, "-show_entries", "stream=codec_name,profile,width,height,r_frame_rate,avg_frame_rate,pix_fmt,bit_rate,"
                "sample_rate,channels,nb_frames,color_primaries,color_transfer,color_space:format=duration,bit_rate")
    rep["probe"] = v
    # loudness (integrated, true peak)
    r = subprocess.run(["ffmpeg", "-nostdin", "-hide_banner", "-i", path, "-vn", "-af", "ebur128=peak=true:framelog=quiet",
                        "-f", "null", "-"], capture_output=True, text=True)
    tail = r.stderr[r.stderr.rfind("Summary:"):]
    num = lambda pat: float(re.search(pat, tail).group(1)) if re.search(pat, tail) else None
    rep["loudness"] = {"I_LUFS": num(r"I:\s+(-?[\d.]+) LUFS"), "LRA_LU": num(r"LRA:\s+(-?[\d.]+) LU"),
                       "true_peak_dBFS": num(r"Peak:\s+(-?[\d.]+) dBFS")}
    # per-frame difference to the previous frame (luma, 160x90): still runs + first frames
    w, h = 160, 90
    p = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-i", path, "-vf", f"scale={w}:{h},format=gray", "-f", "rawvideo", "-"],
                       capture_output=True)
    raw = p.stdout
    n = len(raw) // (w * h)
    diffs = []
    prev = None
    for i in range(n):
        fr = raw[i * w * h:(i + 1) * w * h]
        if prev is not None:
            diffs.append(sum(abs(a - b) for a, b in zip(fr[::7], prev[::7])) / len(fr[::7]))
        prev = fr
    rep["frames"] = n
    rep["frame0_vs_1_mean_abs_diff"] = round(diffs[0], 3) if diffs else None
    # still runs: consecutive frames with mean abs luma diff < 0.6 (on 0-255)
    runs, start = [], None
    for i, d in enumerate(diffs, start=1):
        if d < 0.6:
            start = i - 1 if start is None else start
        else:
            if start is not None and i - start >= 45:
                runs.append((start, i - 1))
            start = None
    if start is not None and n - start >= 45:
        runs.append((start, n - 1))
    bm = beats()
    def beat_of(f):
        return next((b["id"] for b in bm if b["start_frame"] <= f < b["end_frame"]), "tail")
    rep["still_runs_ge_1.5s"] = [{"from_f": a, "to_f": z, "seconds": round((z - a + 1) / FPS, 2), "beat": beat_of(a)} for a, z in runs]
    # the "fun" frame (B10): edit frame of the word "fun"
    fun = next(w for b in bm if b["id"] == "B10" for w in b["words"] if norm(w["text"]) == "fun")
    ff = b10_start = next(b["start_frame"] for b in bm if b["id"] == "B10")
    fun_f = round(fun["start"] * FPS)
    p = subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-i", path, "-vf",
                        f"select='between(n\\,{fun_f - 3}\\,{fun_f + 3})',scale=64:36,format=gray", "-vsync", "0",
                        "-f", "rawvideo", "-"], capture_output=True)
    fr = p.stdout
    means = [round(sum(fr[k * 64 * 36:(k + 1) * 64 * 36]) / (64 * 36), 1) for k in range(len(fr) // (64 * 36))]
    rep["fun"] = {"word_start_s": fun["start"], "edit_frame": fun_f, "luma_mean_frames_-3..+3": means}
    os.makedirs(OUT, exist_ok=True)
    json.dump(rep, open(f"{OUT}/video_{os.path.basename(path)}.json", "w"), indent=1)
    s = [x for x in v["streams"]]
    print(json.dumps({"streams": s, "format": v.get("format")}, indent=0)[:1500])
    print("loudness", rep["loudness"])
    print("frames", n, "frame0 vs 1 diff", rep["frame0_vs_1_mean_abs_diff"])
    print("still runs >= 1.5 s:", rep["still_runs_ge_1.5s"] or "none")
    print("fun:", rep["fun"])


def check_captions_v2():
    """v02 (your note 11): every caption word is its own span (.rc-w, data-rc-f = local onset frame); a group holds
    at most 2 words; every word appears within 1 frame of its spoken onset; plus a static scan for linear eases."""
    rep, problems = {}, []
    for b in beats():
        comp = b["composition"]["id"]
        src = open(f"{ROOT}/hyperframes/{comp}/index.html").read()
        words = b["words"]
        groups = []
        for m in re.finditer(r'<div\b([^>]*\bclass="[^"]*\bclip\b[^"]*"[^>]*)>((?:(?!<div\b).)*?rc-w.*?)</div>', src, re.S):
            ws = re.findall(r'<span class="rc-w[^"]*"[^>]*data-rc-f="(-?\d+)"[^>]*>(.*?)</span>', m.group(2), re.S)
            if ws:
                idm = re.search(r'\bid="([^"]+)"', m.group(1))
                groups.append({"id": idm.group(1) if idm else "?", "words": [(int(f), html.unescape(re.sub(r"<[^>]+>", "", t)).strip()) for f, t in ws]})
        used = set()
        for g in groups:
            if len(g["words"]) > 2:
                problems.append(f"{b['id']} {g['id']}: {len(g['words'])} words in one group")
            for f, t in g["words"]:
                cands = [j for j, w in enumerate(words) if norm(w["text"]) == norm(t) and j not in used]
                if not cands:
                    problems.append(f"{b['id']} {g['id']}: '{t}' is not a spoken word of this beat"); continue
                j = min(cands, key=lambda k: abs(words[k]["comp_t"] * FPS - f))
                used.add(j)
                off = f - words[j]["comp_t"] * FPS
                if abs(off) > 1.5:
                    problems.append(f"{b['id']} {g['id']}: '{t}' pops at local f{f}, spoken at f{words[j]['comp_t'] * FPS:.1f}")
        lin = re.findall(r"ease\s*:\s*['\"](?:none|linear)['\"]", src)
        if lin:
            problems.append(f"{b['id']}: {len(lin)} linear ease(s) in index.html")
        shown = sorted({j for j in used})
        rep[b["id"]] = {"groups": len(groups), "words_shown": len(shown), "words_spoken": len(words),
                        "not_shown_as_caption_words": [words[k]["text"] for k in range(len(words)) if k not in used]}
    os.makedirs(OUT, exist_ok=True)
    json.dump({"problems": problems, "beats": rep}, open(f"{OUT}/captions_v02.json", "w"), indent=1)
    for bid, r in rep.items():
        print("%-4s %2d groups, %2d/%2d words as pop-in caption words; not: %s" % (bid, r["groups"], r["words_shown"], r["words_spoken"],
              " ".join(r["not_shown_as_caption_words"]) or "-"))
    print("PROBLEMS:" if problems else "no v02 caption problems", *problems, sep="\n  ")


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "captions":
        check_captions()
    elif cmd == "captions2":
        check_captions_v2()
    elif cmd == "styles":
        check_styles()
    elif cmd == "video":
        check_video(sys.argv[2])
