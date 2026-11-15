#!/usr/bin/env python3
"""Lock the timeline to the processed voiceover.

Inputs : 01_VO/VO_processed_108.wav, 01_VO/transcript.json (HyperFrames transcribe,
         Whisper medium.en, run on the processed file as the document's toolchain says).
Outputs: 01_VO/VO_words_108.json   word list in locked-script spelling with refined times
         timing/beat_map.json       beats B1-B17 + End, frames, composition windows (6f handles)
         07_Exports/RC_GTA-Origin_v01.srt   voiceover captions for accessibility

Refinement: Whisper word timestamps drift by up to ~0.2 s (and run past the file end),
which is outside the document's +/-2 frame caption sync rule. Every pause in the
processed file is measured from the waveform (energy below the speech floor) and
matched to the script boundary it belongs to; words that touch a pause take their
edge from the waveform, and words inside a continuous phrase are spread across the
measured phrase in proportion to Whisper's relative timing.
"""
import json, os, sys
import numpy as np, soundfile as sf

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from align_lib import ROOT, script_tokens, expand_script, align, energy_pauses  # noqa

FPS = 30
HANDLE_F = 6
BEAT_NAMES = {
    "B1": "hook", "B2": "bug", "B3": "dundee", "B4": "racenchase", "B5": "copgame", "B6": "dull",
    "B7": "shutdown", "B8": "break", "B9": "throughyou", "B10": "fun", "B11": "flip", "B12": "thirty",
    "B13": "gta", "B14": "since", "B15": "proof", "B16": "bug-origin", "B17": "loop",
}
LOGO_TAIL_S = 1.5  # brief: "roughly 75 s of voiceover plus a 1.5 s logo tail"


def main():
    vo = f"{ROOT}/01_VO/VO_processed_108.wav"
    words = json.load(open(f"{ROOT}/01_VO/transcript.json"))
    info = sf.info(vo)
    dur = info.duration
    sc = expand_script(script_tokens())
    m = align(sc, words)
    assert len(m) == len(sc), "script/ASR alignment incomplete"

    # pauses in the processed file. Quiet parts gained ~+14 dB in processing, so the raw
    # -45 dBFS silence threshold maps to about -31 dBFS here.
    proc = json.load(open(f"{ROOT}/01_VO/VO_processing_108.json"))
    gain = proc["pre_gain_db"] + proc["post_gain_db"]
    thr = -45.0 + gain
    pauses, _ = energy_pauses(vo, thr_db=thr, min_dur=0.08)
    inner = [p for p in pauses if p[0] > 0.03 and p[1] < dur - 0.03]

    # monotonic DP: pauses -> script boundaries (prefer punctuation)
    cands = [(k, (words[m[k]]["end"] + words[m[k + 1]]["start"]) / 2) for k in range(len(sc) - 1)]
    P, C = len(inner), len(cands)
    dp = np.full((P + 1, C + 1), 1e9); dp[0, :] = 0
    take = np.zeros((P + 1, C + 1), dtype=bool)
    for p in range(1, P + 1):
        for c in range(1, C + 1):
            pm = (inner[p - 1][0] + inner[p - 1][1]) / 2
            k = cands[c - 1][0]
            plen = inner[p - 1][1] - inner[p - 1][0]
            pen = 0.0 if sc[k]["punct"] else (0.35 if plen < 0.6 else 2.0)  # long pauses follow punctuation
            v = dp[p - 1, c - 1] + abs(pm - cands[c - 1][1]) + pen
            if v < dp[p, c - 1]: dp[p, c] = v; take[p, c] = True
            else: dp[p, c] = dp[p, c - 1]
    assign = {}; p, c = P, C
    while p > 0 and c > 0:
        if take[p, c]: assign[p - 1] = c - 1; p -= 1; c -= 1
        else: c -= 1
    boundary_pause = {cands[ci][0]: inner[pi] for pi, ci in assign.items()}

    # speech onset / offset of the whole file
    x, sr = sf.read(vo)
    hop = int(0.005 * sr)
    rms_db = 20 * np.log10(np.sqrt(np.convolve(x ** 2, np.ones(hop) / hop, mode="same")) + 1e-12)
    onset = int(np.argmax(rms_db > thr)) / sr
    offset = (len(x) - int(np.argmax(rms_db[::-1] > thr))) / sr

    # phrases = runs of words between measured pauses
    phrases, cur = [], [0]
    for k in range(len(sc) - 1):
        if k in boundary_pause:
            phrases.append(cur); cur = [k + 1]
        else:
            cur.append(k + 1)
    phrases.append(cur)
    refined = [None] * len(sc)
    for pi, ph in enumerate(phrases):
        first, last = ph[0], ph[-1]
        t0 = onset if first == 0 else boundary_pause[first - 1][1]
        t1 = offset if last == len(sc) - 1 else boundary_pause[last][0]
        a0, a1 = words[m[first]]["start"], words[m[last]]["end"]
        span = max(a1 - a0, 1e-3)
        for k in ph:
            ws, we = words[m[k]]["start"], words[m[k]]["end"]
            s = t0 + (ws - a0) / span * (t1 - t0)
            e = t0 + (we - a0) / span * (t1 - t0)
            refined[k] = (s, e)
        refined[first] = (t0, refined[first][1])
        refined[last] = (refined[last][0], t1)

    out_words = []
    for k, t in enumerate(sc):
        s, e = refined[k]
        out_words.append({"i": k, "beat": t["beat"], "text": t["text"], "asr": words[m[k]]["text"],
                          "start": round(s, 3), "end": round(e, 3),
                          "start_frame": int(np.floor(s * FPS + 1e-6)), "end_frame": int(np.ceil(e * FPS - 1e-6)),
                          "punct": t["punct"], "pause_after": (round(boundary_pause[k][1] - boundary_pause[k][0], 3) if k in boundary_pause else 0.0),
                          "whisper_start": words[m[k]]["start"], "whisper_end": words[m[k]]["end"]})
    os.makedirs(f"{ROOT}/timing", exist_ok=True)
    json.dump({"source": "01_VO/VO_processed_108.wav", "fps": FPS, "duration_s": round(dur, 3),
               "method": "HyperFrames transcribe (whisper medium.en) on the processed VO; word edges snapped to measured pauses",
               "silence_threshold_dbfs": round(thr, 1), "words": out_words}, open(f"{ROOT}/01_VO/VO_words_108.json", "w"), indent=1)

    # beats
    script = json.load(open(f"{ROOT}/tools/script_v2.json"))
    beats = []
    ids = list(script.keys())
    for bi, b in enumerate(ids):
        ws = [w for w in out_words if w["beat"] == b]
        start_f = 0 if bi == 0 else ws[0]["start_frame"]
        beats.append({"id": b, "name": BEAT_NAMES[b], "voiceover": script[b], "start_frame": start_f, "words": ws})
    vo_end_f = int(np.ceil(out_words[-1]["end"] * FPS))
    end_f = vo_end_f + int(round(LOGO_TAIL_S * FPS))
    for bi, bt in enumerate(beats):
        bt["end_frame"] = beats[bi + 1]["start_frame"] if bi + 1 < len(beats) else end_f
        bt["dur_frames"] = bt["end_frame"] - bt["start_frame"]
        bt["start_s"] = round(bt["start_frame"] / FPS, 4)
        bt["end_s"] = round(bt["end_frame"] / FPS, 4)
        bt["dur_s"] = round(bt["dur_frames"] / FPS, 4)
        bt["start_tc"] = f"{int(bt['start_s'] // 60)}:{bt['start_s'] % 60:04.1f}"
        num = int(bt["id"][1:])
        bt["composition"] = {
            "id": f"b{num:02d}-{bt['name']}",
            "edit_start_frame": bt["start_frame"] - HANDLE_F,  # may be negative for B1 (handle before 0:00)
            "frames": bt["dur_frames"] + 2 * HANDLE_F,
            "duration_s": round((bt["dur_frames"] + 2 * HANDLE_F) / FPS, 4),
            "beat_starts_at_local_frame": HANDLE_F,
            "note": "local time 0 = beat start - 6f handle; beat occupies local frames 6 .. 6+dur_frames",
        }
        # word times relative to the beat start and to the composition (local) clock
        for w in bt["words"]:
            w["beat_t"] = round(w["start"] - bt["start_s"], 3)
            w["comp_t"] = round(w["start"] - bt["start_s"] + HANDLE_F / FPS, 3)
            w["comp_end_t"] = round(w["end"] - bt["start_s"] + HANDLE_F / FPS, 3)
    doc_starts = {"B1": 0.0, "B2": 3.8, "B3": 9.2, "B4": 14.9, "B5": 18.5, "B6": 21.5, "B7": 26.9, "B8": 30.8, "B9": 32.4,
                  "B10": 39.4, "B11": 41.0, "B12": 46.8, "B13": 49.6, "B14": 54.8, "B15": 60.2, "B16": 66.6, "B17": 71.0}
    for bt in beats:
        bt["doc_target_start_s"] = doc_starts[bt["id"]]
    json.dump({"fps": FPS, "canvas": [1920, 1080], "handle_frames": HANDLE_F, "vo_end_s": round(out_words[-1]["end"], 3),
               "edit_end_frame": end_f, "edit_end_s": round(end_f / FPS, 4), "logo_tail_s": LOGO_TAIL_S,
               "vo_file": "01_VO/VO_processed_108.wav", "beats": beats}, open(f"{ROOT}/timing/beat_map.json", "w"), indent=1)

    # SRT (voiceover captions, sentence-ish cues up to ~42 chars per line)
    def tc(t):
        ms = int(round(t * 1000)); h, ms = divmod(ms, 3600000); mi, ms = divmod(ms, 60000); s, ms = divmod(ms, 1000)
        return f"{h:02d}:{mi:02d}:{s:02d},{ms:03d}"
    cues, cur = [], []
    for w in out_words:
        cur.append(w)
        text = " ".join(x["text"] for x in cur)
        if w["punct"] in (".", "?", "!") or len(text) > 38 or (w["punct"] in (",", ":", "…") and len(text) > 22):
            cues.append(cur); cur = []
    if cur: cues.append(cur)
    # merge Race/and/Chase back into the script spelling
    lines = []
    for i, cu in enumerate(cues, 1):
        txt = " ".join(x["text"] for x in cu).replace("Race and Chase,", "Race'n'Chase,") if cu[0]["beat"] == "B4" else " ".join(x["text"] for x in cu)
        end = cu[-1]["end"] if i == len(cues) else min(cues[i][0]["start"], cu[-1]["end"] + 0.6)
        lines.append(f"{i}\n{tc(cu[0]['start'])} --> {tc(end)}\n{txt}\n")
    os.makedirs(f"{ROOT}/07_Exports", exist_ok=True)
    open(f"{ROOT}/07_Exports/RC_GTA-Origin_v01.srt", "w").write("\n".join(lines))

    print(f"pauses measured {len(inner)}, matched {len(assign)}; speech {onset:.3f}-{offset:.3f}s; file {dur:.3f}s")
    print(f"{'beat':5} {'start':>7} {'frames':>6} {'dur_s':>6} {'doc':>6}  first words")
    for bt in beats:
        print(f"{bt['id']:5} {bt['start_s']:7.3f} {bt['start_frame']:6d} {bt['dur_s']:6.2f} {bt['doc_target_start_s']:6.1f}  {' '.join(w['text'] for w in bt['words'][:5])}")
    print("edit end", end_f, "frames =", round(end_f / FPS, 3), "s")
    drift = [abs(w["start"] - w["whisper_start"]) for w in out_words]
    print("whisper vs refined start: median %.3f s, max %.3f s" % (np.median(drift), max(drift)))


if __name__ == "__main__":
    main()
