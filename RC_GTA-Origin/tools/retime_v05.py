#!/usr/bin/env python3
"""v05 re-time: the cuts in "GTA Origin v04 - Edit Instructions for Claude" (REVISION_v05.md, section T).

Cuts are whole frames, so every beat that is not cut keeps its local timing exactly (its words.json, cues.json
and composition frames stay valid; only its place on the edit timeline moves).

  Cut A  58 f (1.9333 s)  "Here's how. It's 1995 in" removed: "...saved it." goes straight to "Dundee, Scotland."
                          (doc beat 9 'Recommended'). Removed span [10.0597, 11.9930) of the v04 VO: it starts in the
                          room tone after "it." (9.915-10.085 s) and ends on the closure of the D in "Dundee" (its burst
                          is at 12.005 s), so no part of "in" survives. 4 ms equal-power crossfade.
  Cut B  39 f (1.3000 s)  the silence after "Grand Theft Auto." goes from 1.686 s to 0.386 s (doc: 0.4 s maximum).
                          Removed span [54.70, 56.00) of the v04 VO: inserted room tone only. 10 ms crossfade.
  Tail   27 f (0.9 s)     the GTA VI logo after "now?" holds 0.9 s (doc 75.5-77.0), then a hard cut to
  B18    75 f (2.5 s)     the new CTA end card (doc: NEW 1:17.0-1:19.5).

Not cut, because the audio does not allow it (doc: "If a caption differs from what's actually said, go with the audio"):
  "In Nov 1997" (the VO says "in November 1997," continuously, 50.227-51.751 s; no 1 s of silence exists there);
  the lone "Of" (a caption fix only: "Of course," appears as one unit); Gary Penn (the 0.24 s before "it 'awful'" is
  the narrator's normal breath; nothing to trim).

In : 01_VO/VO_processed_115.wav, 01_VO/VO_words_115.json, timing/beat_map.json (v02/v04 timing)
Out: 01_VO/VO_processed_v05.wav, 01_VO/VO_words_v05.json, 01_VO/VO_processing_v05.json,
     timing/beat_map_v04.json (copy of the v04 map), timing/beat_map.json (v05), timing/v04_to_v05.json
"""
import json, os, shutil
import numpy as np, soundfile as sf

ROOT = "/home/user/claude-test-2.0-/RC_GTA-Origin"
FPS, HANDLE_F = 30, 6
CUT_A_END = 11.993            # D closure in "Dundee" (v04 VO seconds)
CUT_A_F = 58
CUT_A_START = CUT_A_END - CUT_A_F / FPS          # 10.0597, room tone after "it."
DUNDEE_BURST = 12.005         # audible onset of "Dundee," (v04 VO seconds)
CUT_B_START, CUT_B_F = 54.70, 39
CUT_B_END = CUT_B_START + CUT_B_F / FPS          # 56.00
LOGO_TAIL_F = 27
CTA_F = 75
DROP_B3 = ["Here's", "how.", "It's", "1995", "in"]

BEAT_NAMES = {"B1": "hook", "B2": "bug", "B3": "dundee", "B4": "racenchase", "B5": "copgame", "B6": "dull", "B7": "shutdown",
              "B8": "break", "B9": "throughyou", "B10": "fun", "B11": "flip", "B12": "thirty", "B13": "gta", "B14": "since",
              "B15": "proof", "B16": "bug-origin", "B17": "loop", "B18": "cta"}


def v05(t):
    """v04 seconds -> v05 seconds (None inside a removed span)."""
    if t < CUT_A_START:
        return t
    if t < CUT_A_END:
        return None
    if t < CUT_B_START:
        return t - CUT_A_F / FPS
    if t < CUT_B_END:
        return None
    return t - (CUT_A_F + CUT_B_F) / FPS


def splice(x, sr, a, b, xf_s):
    """Remove x[a:b] (seconds) with an equal-power crossfade of xf_s across the joint."""
    ia, ib, n = int(round(a * sr)), int(round(b * sr)), int(round(xf_s * sr))
    th = np.linspace(0, np.pi / 2, n)
    shape = (n,) + (1,) * (x.ndim - 1)
    fo, fi = np.cos(th).reshape(shape), np.sin(th).reshape(shape)
    joint = x[ia - n:ia] * fo + x[ib - n:ib] * fi       # tail before the cut + the n samples just before the resume point
    return np.concatenate([x[:ia - n], joint, x[ib:]])


def main():
    src = f"{ROOT}/01_VO/VO_processed_115.wav"
    x, sr = sf.read(src, dtype="float64", always_2d=False)
    # cut B first (later in time) so cut A's sample positions are unaffected
    y = splice(x, sr, CUT_B_START, CUT_B_END, 0.010)
    y = splice(y, sr, CUT_A_START, CUT_A_END, 0.004)
    dst = f"{ROOT}/01_VO/VO_processed_v05.wav"
    sf.write(dst, y, sr, subtype=sf.info(src).subtype)

    w115 = json.load(open(f"{ROOT}/01_VO/VO_words_115.json"))
    words, i = [], 0
    for w in w115["words"]:
        if w["beat"] == "B3" and w["text"] in DROP_B3 and w["start"] < CUT_A_END:
            continue
        nw = dict(w)
        if w["beat"] == "B3" and w["text"] == "Dundee,":
            nw["start"] = DUNDEE_BURST
            nw["whisper_start"] = max(w["whisper_start"], CUT_A_END)
        for k in ("start", "end", "whisper_start", "whisper_end"):
            t = v05(max(nw[k], CUT_A_END) if CUT_A_START <= nw[k] < CUT_A_END else nw[k])
            assert t is not None, (w["text"], k, nw[k])
            nw[k] = round(t, 3)
        nw["start_frame"] = int(np.floor(nw["start"] * FPS + 1e-6))
        nw["end_frame"] = int(np.ceil(nw["end"] * FPS - 1e-6))
        nw["i"] = i
        i += 1
        words.append(nw)
    auto = next(w for w in words if w["beat"] == "B13" and w["text"] == "Auto.")
    nxt = next(w for w in words if w["beat"] == "B14")
    auto["pause_after"] = round(nxt["start"] - auto["end"], 4)
    it = next(w for w in words if w["beat"] == "B2" and w["text"] == "it.")
    it["pause_after"] = round(next(w for w in words if w["beat"] == "B3")["start"] - it["end"], 4)

    rep = json.load(open(f"{ROOT}/01_VO/VO_processing_115.json"))
    rep["v05_cuts"] = [
        {"name": "A", "v04_span_s": [round(CUT_A_START, 4), CUT_A_END], "frames": CUT_A_F, "removed": "Here's how. It's 1995 in",
         "why": "doc beat 9 (Recommended): go straight from 'saved it.' to 'Dundee, Scotland.'", "crossfade_ms": 4},
        {"name": "B", "v04_span_s": [CUT_B_START, round(CUT_B_END, 4)], "frames": CUT_B_F, "removed": "room tone after 'Auto.'",
         "why": "doc 54.5-56.2 silence: 1.65 s -> 0.4 s maximum (now %.3f s)" % auto["pause_after"], "crossfade_ms": 10}]
    rep["final_file"] = "01_VO/VO_processed_v05.wav"
    rep["final_duration_s"] = round(len(y) / sr, 4)
    json.dump(rep, open(f"{ROOT}/01_VO/VO_processing_v05.json", "w"), indent=1)
    json.dump({"source": "01_VO/VO_processed_v05.wav", "fps": FPS, "duration_s": round(len(y) / sr, 3),
               "method": "VO_words_115.json mapped through the two v05 cuts (whole frames); 'Dundee,' starts at its burst",
               "words": words}, open(f"{ROOT}/01_VO/VO_words_v05.json", "w"), indent=1)

    old_path = f"{ROOT}/timing/beat_map.json"
    if not os.path.exists(f"{ROOT}/timing/beat_map_v04.json"):
        shutil.copy2(old_path, f"{ROOT}/timing/beat_map_v04.json")
    old = json.load(open(f"{ROOT}/timing/beat_map_v04.json"))
    script = {bt["id"]: bt["voiceover"] for bt in old["beats"]}
    script["B3"] = "Dundee, Scotland. DMA Design, the studio behind Lemmings, starts a new game."
    beats = []
    for bi, bid in enumerate(list(script.keys())):
        ws = [w for w in words if w["beat"] == bid]
        start_f = 0 if bi == 0 else ws[0]["start_frame"]
        beats.append({"id": bid, "name": BEAT_NAMES[bid], "voiceover": script[bid], "start_frame": start_f, "words": ws})
    vo_end_f = int(np.ceil(words[-1]["end"] * FPS))
    story_end_f = vo_end_f + LOGO_TAIL_F
    beats.append({"id": "B18", "name": "cta", "voiceover": "", "start_frame": story_end_f, "words": []})
    end_f = story_end_f + CTA_F
    for bi, bt in enumerate(beats):
        bt["end_frame"] = beats[bi + 1]["start_frame"] if bi + 1 < len(beats) else end_f
        bt["dur_frames"] = bt["end_frame"] - bt["start_frame"]
        bt["start_s"] = round(bt["start_frame"] / FPS, 4)
        bt["end_s"] = round(bt["end_frame"] / FPS, 4)
        bt["dur_s"] = round(bt["dur_frames"] / FPS, 4)
        bt["start_tc"] = f"{int(bt['start_s'] // 60)}:{bt['start_s'] % 60:04.1f}"
        num = int(bt["id"][1:])
        bt["composition"] = {"id": f"b{num:02d}-{bt['name']}", "edit_start_frame": bt["start_frame"] - HANDLE_F,
                             "frames": bt["dur_frames"] + 2 * HANDLE_F, "duration_s": round((bt["dur_frames"] + 2 * HANDLE_F) / FPS, 4),
                             "beat_starts_at_local_frame": HANDLE_F,
                             "note": "local time 0 = beat start - 6f handle; beat occupies local frames 6 .. 6+dur_frames"}
        for w in bt["words"]:
            w["beat_t"] = round(w["start"] - bt["start_s"], 3)
            w["comp_t"] = round(w["start"] - bt["start_s"] + HANDLE_F / FPS, 3)
            w["comp_end_t"] = round(w["end"] - bt["start_s"] + HANDLE_F / FPS, 3)
        o = next((o for o in old["beats"] if o["id"] == bt["id"]), None)
        bt["v04_start_frame"] = o["start_frame"] if o else None
        bt["v04_dur_frames"] = o["dur_frames"] if o else None
        bt["doc_target_start_s"] = o["doc_target_start_s"] if o else None
        bt["v01_dur_frames"] = o["v01_dur_frames"] if o else None
    beats[-1]["note"] = "NEW in v05: CTA end card (doc 'NEW 1:17.0-1:19.5'); last 6 frames cross to b01-hook frame 0 (loop)"
    json.dump({"fps": FPS, "canvas": [1920, 1080], "handle_frames": HANDLE_F, "vo_end_s": round(words[-1]["end"], 3),
               "story_end_frame": story_end_f, "edit_end_frame": end_f, "edit_end_s": round(end_f / FPS, 4),
               "logo_tail_s": round(LOGO_TAIL_F / FPS, 4), "cta_frames": CTA_F, "version": "v05 (doc cuts A/B, CTA)",
               "vo_file": "01_VO/VO_processed_v05.wav", "beats": beats}, open(old_path, "w"), indent=1)
    json.dump({"note": "map a v04 preview timestamp (the doc's timestamps) to v05: subtract shift_s; spans in 'removed' are gone",
               "removed": [[round(CUT_A_START, 4), CUT_A_END], [CUT_B_START, round(CUT_B_END, 4)]],
               "segments": [{"v04_from": 0.0, "v04_to": round(CUT_A_START, 4), "shift_s": 0.0, "shift_f": 0},
                            {"v04_from": CUT_A_END, "v04_to": CUT_B_START, "shift_s": round(CUT_A_F / FPS, 4), "shift_f": CUT_A_F},
                            {"v04_from": round(CUT_B_END, 4), "v04_to": 77.6, "shift_s": round((CUT_A_F + CUT_B_F) / FPS, 4),
                             "shift_f": CUT_A_F + CUT_B_F}],
               "v04_logo_tail_end_s": 77.6, "v05_story_end_s": round(story_end_f / FPS, 4), "v05_cta": [round(story_end_f / FPS, 4), round(end_f / FPS, 4)]},
              open(f"{ROOT}/timing/v04_to_v05.json", "w"), indent=1)
    print(f"VO {len(x)/sr:.3f}s -> {len(y)/sr:.3f}s; edit {end_f}f = {end_f/FPS:.3f}s (story ends f{story_end_f})")
    for bt in beats:
        print(f"  {bt['id']:4} start {bt['start_s']:7.3f}s f{bt['start_frame']:5d}  dur {bt['dur_frames']:4d}f (v04 {bt['v04_dur_frames']})  {bt['composition']['id']}")


if __name__ == "__main__":
    main()
