#!/usr/bin/env python3
"""v02 re-time: the voiceover at 115% (your revision: "make the voiceover a bit faster").

The 115% file comes from `tools/process_vo.py --speed 1.15` with the same pause edits as v01 (verified: the
tightened signal is sample-identical), so every word time maps exactly: t115 = t108(no gap) * 1.08 / 1.15.
Then the B13 title-hold gap is recomputed for the new timing (T6 type-on 28f + hold 30f + unboxing 24f = 82f
from "Grand" to B14's first word, CONFLICTS.md C14), inserted after "Auto." with that pause's own room tone.

In : 01_VO/VO_words_108.json, 01_VO/VO_processing_108.json (v01 gap), 01_VO/VO_processed_115.wav (no gap)
Out: 01_VO/VO_processed_115_nogap.wav, 01_VO/VO_processed_115.wav (locked v02 VO), 01_VO/VO_words_115.json,
     timing/beat_map.json (v01 kept as timing/beat_map_v01.json), 01_VO/VO_processing_115.json (gap recorded)
"""
import json, os, shutil
import numpy as np, soundfile as sf

ROOT = "/home/user/claude-test-2.0-/RC_GTA-Origin"
FPS, HANDLE_F, LOGO_TAIL_S = 30, 6, 1.5
K = 1.08 / 1.15
NEED_F = 28 + 30 + 24

BEAT_NAMES = {"B1": "hook", "B2": "bug", "B3": "dundee", "B4": "racenchase", "B5": "copgame", "B6": "dull", "B7": "shutdown",
              "B8": "break", "B9": "throughyou", "B10": "fun", "B11": "flip", "B12": "thirty", "B13": "gta", "B14": "since",
              "B15": "proof", "B16": "bug-origin", "B17": "loop"}


def main():
    v01 = json.load(open(f"{ROOT}/01_VO/VO_words_108.json"))
    gap01 = json.load(open(f"{ROOT}/01_VO/VO_processing_108.json"))["title_hold_gap"]
    at01, g01 = gap01["inserted_at_s"], gap01["inserted_s"]
    words = []
    for w in v01["words"]:
        nw = dict(w)
        for k in ("start", "end", "whisper_start", "whisper_end"):
            t = w[k]
            if t > at01:
                t -= g01
            nw[k] = t * K
        nw["pause_after"] = round(w["pause_after"] * K, 4)
        words.append(nw)
    # gap needed after "Auto." so that B14's first word is >= 82f after "Grand"
    grand = next(w for w in words if w["beat"] == "B13" and w["text"].startswith("Grand"))
    auto = next(w for w in words if w["beat"] == "B13" and w["text"] == "Auto.")
    nxt = next(w for w in words if w["beat"] == "B14")
    gf = int(np.floor(grand["start"] * FPS + 1e-6))
    gap_f = 0
    while int(np.floor((nxt["start"] + gap_f / FPS) * FPS + 1e-6)) - gf < NEED_F:
        gap_f += 1
    gap_s = gap_f / FPS
    mid = (auto["end"] + nxt["start"]) / 2
    # audio: keep the no-gap file, insert room tone (same method as tools/vo_title_hold.py)
    src_nogap = f"{ROOT}/01_VO/VO_processed_115_nogap.wav"
    dst = f"{ROOT}/01_VO/VO_processed_115.wav"
    if not os.path.exists(src_nogap):
        shutil.copy2(dst, src_nogap)
    x, sr = sf.read(src_nogap, dtype="float64")
    a, b = auto["end"], nxt["start"]
    tone = x[int((a + 0.2 * (b - a)) * sr):int((a + 0.8 * (b - a)) * sr)]
    need = int(round(gap_s * sr)); xf = int(0.02 * sr)
    fill = np.zeros(0)
    while len(fill) < need + xf:
        seg = tone.copy()
        if len(fill) >= xf:
            r = np.sin(np.linspace(0, np.pi / 2, xf)) ** 2
            fill[-xf:] = fill[-xf:] * (1 - r) + seg[:xf] * r
            fill = np.concatenate([fill, seg[xf:]])
        else:
            fill = np.concatenate([fill, seg])
    fill = fill[:need]
    cut = int(mid * sr)
    out = np.concatenate([x[:cut], fill, x[cut:]])
    sf.write(dst, out, sr, subtype=sf.info(src_nogap).subtype)
    for w in words:
        for k in ("start", "end", "whisper_start", "whisper_end"):
            if w[k] > mid:
                w[k] += gap_s
            w[k] = round(w[k], 3)
        w["start_frame"] = int(np.floor(w["start"] * FPS + 1e-6))
        w["end_frame"] = int(np.ceil(w["end"] * FPS - 1e-6))
    rep = json.load(open(f"{ROOT}/01_VO/VO_processing_115.json"))
    rep["title_hold_gap"] = {"after_word": "Auto. (B13)", "inserted_at_s": round(mid, 4), "inserted_s": round(gap_s, 4), "frames": gap_f,
                             "reason": "B13 build: T6 type-on (28f) + hold 1 s + 0.8 s unboxing after 'Grand'; CONFLICTS.md C14 (recomputed for 115%)",
                             "room_tone_rms_dbfs": round(20 * np.log10(np.sqrt(np.mean(tone ** 2)) + 1e-12), 1)}
    rep["final_file"] = "01_VO/VO_processed_115.wav"
    rep["final_duration_s"] = round(len(out) / sr, 4)
    rep["word_times"] = "mapped from VO_words_108.json: identical pause edits, t115 = t108(no gap) * 1.08/1.15, then the 115 gap"
    json.dump(rep, open(f"{ROOT}/01_VO/VO_processing_115.json", "w"), indent=1)
    json.dump({"source": "01_VO/VO_processed_115.wav", "fps": FPS, "duration_s": round(len(out) / sr, 3),
               "method": "v01 words (whisper medium.en on the 108% file, edges snapped to measured pauses) mapped to 115% exactly (same pause edits); B13 title gap recomputed",
               "words": words}, open(f"{ROOT}/01_VO/VO_words_115.json", "w"), indent=1)
    # beat map (same rules as tools/build_timing.py)
    if not os.path.exists(f"{ROOT}/timing/beat_map_v01.json"):
        shutil.copy2(f"{ROOT}/timing/beat_map.json", f"{ROOT}/timing/beat_map_v01.json")
    old = json.load(open(f"{ROOT}/timing/beat_map_v01.json"))
    script = {bt["id"]: bt["voiceover"] for bt in old["beats"]}
    beats = []
    ids = list(script.keys())
    for bi, bid in enumerate(ids):
        ws = [w for w in words if w["beat"] == bid]
        start_f = 0 if bi == 0 else ws[0]["start_frame"]
        beats.append({"id": bid, "name": BEAT_NAMES[bid], "voiceover": script[bid], "start_frame": start_f, "words": ws})
    vo_end_f = int(np.ceil(words[-1]["end"] * FPS))
    end_f = vo_end_f + int(round(LOGO_TAIL_S * FPS))
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
        bt["doc_target_start_s"] = next(o["doc_target_start_s"] for o in old["beats"] if o["id"] == bt["id"])
        bt["v01_dur_frames"] = next(o["dur_frames"] for o in old["beats"] if o["id"] == bt["id"])
    json.dump({"fps": FPS, "canvas": [1920, 1080], "handle_frames": HANDLE_F, "vo_end_s": round(words[-1]["end"], 3),
               "edit_end_frame": end_f, "edit_end_s": round(end_f / FPS, 4), "logo_tail_s": LOGO_TAIL_S, "version": "v02 (VO 115%)",
               "vo_file": "01_VO/VO_processed_115.wav", "beats": beats}, open(f"{ROOT}/timing/beat_map.json", "w"), indent=1)
    print(f"gap {gap_f}f at {mid:.3f}s; VO {len(out)/sr:.3f}s; edit {end_f}f = {end_f/FPS:.3f}s")
    for bt in beats:
        print(f"  {bt['id']:4} start {bt['start_s']:7.3f}s f{bt['start_frame']:5d}  dur {bt['dur_frames']:4d}f (v01 {bt['v01_dur_frames']})  {bt['composition']['id']}")
    fun = next(w for w in words if w["beat"] == "B10" and w["text"].startswith("fun"))
    print(f"fun onset {fun['start']:.3f}s frame {fun['start_frame']}")


if __name__ == "__main__":
    main()
