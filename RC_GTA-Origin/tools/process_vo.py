#!/usr/bin/env python3
"""Voiceover processing per the Master Edit Plan "Speed-up instruction".

Steps (in the document's order):
 1. Trim the silence at the start (the real leading silence; see CONFLICT note).
 2. Tighten pauses: cap every pause at ~0.30 s, cutting only inside silence.
    Keep three deliberate pauses: 0.30 s after "broke" (B2), 0.50 s before and
    after "Then, something breaks." (B8).
 3. Speed up to SPEED (default 1.08) with pitch preserved (rubberband).
 4. Raise to about -16 LUFS short-term, then the voice chain:
    HPF 80 Hz, light de-essing, ~3:1 compression with 4-6 dB gain reduction,
    sit around -16 LUFS short-term with peaks no higher than -3 dBFS.

CONFLICT (flagged): the document says "Speech starts at 1.97 s" and "Trim the
1.97 s of silence at the start". In the attached file speech starts at 0.10 s
("Why does every GTA," = 0.11-1.71 s); 1.97 s is the end of the first comma
pause. Trimming 1.97 s would delete four words of the locked script (Rule 1, the
highest-priority section), so only the real leading silence is trimmed and the
first word lands one frame (1/30 s) into the processed file.

Outputs (in 01_VO/): VO_tightened_raw.wav (step 2), VO_processed_<pct>.wav
(steps 3-4), VO_processing_<pct>.json (recipe, edit list, time map, metrics).
"""
import argparse, json, subprocess, sys, os
import numpy as np, soundfile as sf

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from align_lib import ROOT, energy_pauses, script_tokens, expand_script, align  # noqa

SR = 48000
FRAME = 1 / 30


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr[-3000:])
        raise SystemExit(f"command failed: {' '.join(cmd)}")
    return r


def ebur128(path):
    r = subprocess.run(["ffmpeg", "-nostdin", "-hide_banner", "-i", path, "-af", "ebur128=peak=true:framelog=info", "-f", "null", "-"],
                       capture_output=True, text=True)
    st, integ, tp = [], None, None
    for line in r.stderr.splitlines():
        if " t:" in line and " S:" in line:
            try:
                s = float(line.split(" S:")[1].split()[0])
                if s > -70: st.append(s)
            except Exception:
                pass
        if line.strip().startswith("I:") and "LUFS" in line: integ = float(line.split()[1])
        if line.strip().startswith("Peak:") and "dBFS" in line: tp = float(line.split()[1])
    st = np.array(st)
    return {"integrated_lufs": integ, "true_peak_dbfs": tp,
            "short_term_median_lufs": float(np.median(st)) if len(st) else None,
            "short_term_p90_lufs": float(np.percentile(st, 90)) if len(st) else None}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--speed", type=float, default=1.08)
    ap.add_argument("--raw", default=f"{ROOT}/01_VO/ElevenLabs_2026-11-15T08_04_46_Clara_-_Corporate__Training_Trusted_Professional_pvc_s20_sim50_v4.mp3")
    ap.add_argument("--asr", required=True, help="whisper transcript.json of the RAW file (word order + approx times)")
    ap.add_argument("--comp-threshold-db", type=float, default=-27.0)
    a = ap.parse_args()
    pct = int(round(a.speed * 100))
    out_dir = f"{ROOT}/01_VO"
    work = f"{ROOT}/01_VO/.work"; os.makedirs(work, exist_ok=True)

    # 0. decode raw to 48 kHz mono float
    raw48 = f"{work}/raw48.wav"
    run(["ffmpeg", "-nostdin", "-loglevel", "error", "-y", "-i", a.raw, "-ac", "1", "-ar", str(SR), "-c:a", "pcm_f32le", raw48])
    x, sr = sf.read(raw48)
    dur = len(x) / sr

    # pauses from the energy envelope (-45 dBFS, >= 0.12 s) and their script position
    pauses, _ = energy_pauses(raw48, thr_db=-45.0, min_dur=0.12)
    words = json.load(open(a.asr))
    sc = expand_script(script_tokens())
    m = align(sc, words)
    cands = [(k, (words[m[k]]["end"] + words[m[k + 1]]["start"]) / 2) for k in range(len(sc) - 1) if k in m and k + 1 in m]
    inner = [p for p in pauses if p[0] > 0.05 and p[1] < dur - 0.05]
    # monotonic DP assignment of pauses to word boundaries (prefer punctuation)
    P, C = len(inner), len(cands)
    INF = 1e9
    dp = np.full((P + 1, C + 1), INF); dp[0, :] = 0
    take = np.zeros((P + 1, C + 1), dtype=bool)
    for p in range(1, P + 1):
        for c in range(1, C + 1):
            pm = (inner[p - 1][0] + inner[p - 1][1]) / 2
            k = cands[c - 1][0]
            v = dp[p - 1, c - 1] + abs(pm - cands[c - 1][1]) + (0.0 if sc[k]["punct"] else 0.35)
            if v < dp[p, c - 1]:
                dp[p, c] = v; take[p, c] = True
            else:
                dp[p, c] = dp[p, c - 1]
    assign = {}; p, c = P, C
    while p > 0 and c > 0:
        if take[p, c]: assign[p - 1] = c - 1; p -= 1; c -= 1
        else: c -= 1

    # 1. leading silence: first sample above -45 dBFS (5 ms RMS) minus one frame
    hop = int(0.005 * sr)
    rms_db = 20 * np.log10(np.sqrt(np.convolve(x ** 2, np.ones(hop) / hop, mode="same")) + 1e-12)
    onset = int(np.argmax(rms_db > -45.0))
    head = max(0, onset - int(FRAME * sr))
    # tail: keep 0.15 s after the last speech sample
    last = len(x) - int(np.argmax(rms_db[::-1] > -45.0))
    tail = min(len(x), last + int(0.15 * sr))

    # 2. pause edits
    edits = []
    for pi, pz in enumerate(inner):
        k = cands[assign[pi]][0]
        after, before = sc[k]["text"], sc[k + 1]["text"]
        d = pz[1] - pz[0]
        rule = "cap"
        target = min(d, 0.30)
        if after.startswith("broke"): target, rule = 0.30, "deliberate: 0.3 s after 'broke' (B2)"
        elif before.startswith("Then"): target, rule = 0.50, "deliberate: 0.5 s before 'Then, something breaks.' (B8)"
        elif after.startswith("breaks"): target, rule = 0.50, "deliberate: 0.5 s after 'Then, something breaks.' (B8)"
        if target > d + 1e-6:
            # deliberate pause longer than the recorded silence would need padding; never invent audio
            target = d; rule += " (recorded pause shorter; kept as recorded)"
        edits.append({"after": after, "before": before, "punct": sc[k]["punct"], "start": round(pz[0], 4), "end": round(pz[1], 4),
                      "dur": round(d, 4), "target": round(target, 4), "removed": round(d - target, 4), "rule": rule})

    # build the tightened signal: remove the middle of each pause (keep half the target on each side)
    keep = []  # (src_start, src_end) in samples
    cur = head
    for e in edits:
        if e["removed"] <= 0.0005:
            continue
        s, en = int(e["start"] * sr), int(e["end"] * sr)
        half = int(e["target"] / 2 * sr)
        cut_a, cut_b = s + half, en - (int(e["target"] * sr) - half)
        keep.append((cur, cut_a)); cur = cut_b
    keep.append((cur, tail))
    xf = int(0.010 * sr)
    out = np.zeros(0)
    for (s0, s1) in keep:
        seg = x[s0:s1].copy()
        if len(out) >= xf and len(seg) >= xf:
            ramp = np.sin(np.linspace(0, np.pi / 2, xf)) ** 2
            out[-xf:] = out[-xf:] * (1 - ramp) + seg[:xf] * ramp
            out = np.concatenate([out, seg[xf:]])
        else:
            out = np.concatenate([out, seg])
    tight = f"{out_dir}/VO_tightened_raw.wav"
    sf.write(tight, out, sr, subtype="FLOAT")

    # time map raw -> tightened (piecewise) for later checks
    tmap, t_out = [], 0.0
    for i, (s0, s1) in enumerate(keep):
        tmap.append({"raw_start": s0 / sr, "raw_end": s1 / sr, "out_start": t_out})
        t_out += (s1 - s0) / sr - (xf / sr if i > 0 else 0)

    # 3. speed with pitch preserved
    stretched = f"{work}/stretched_{pct}.wav"
    run(["ffmpeg", "-nostdin", "-loglevel", "error", "-y", "-i", tight, "-af",
         f"rubberband=tempo={a.speed}:pitch=1:transients=mixed:detector=compound:phase=laminar:window=standard:formant=preserved:pitchq=quality:channels=together",
         "-ar", str(SR), "-c:a", "pcm_f32le", stretched])

    # 4. loudness: +gain to ~-16 LUFS short-term, then HPF 80 Hz, light de-essing, ~3:1 compression, final gain, limiter -3 dBFS
    m0 = ebur128(stretched)
    pre_gain = -16.0 - m0["short_term_median_lufs"]
    pre_chain = f"volume={pre_gain:.2f}dB,highpass=f=80:poles=2,deesser=i=0.25:m=0.5:f=0.5:s=o"
    run(["ffmpeg", "-nostdin", "-loglevel", "error", "-y", "-i", stretched, "-af", pre_chain, "-c:a", "pcm_f32le", f"{work}/pre_comp_{pct}.wav"])
    pre, _ = sf.read(f"{work}/pre_comp_{pct}.wav")

    def gain_reduction(post):
        # makeup=1, so the level difference per 400 ms speech window is pure reduction
        w = int(0.4 * SR); nwin = min(len(pre), len(post)) // w
        gr = []
        for i in range(nwin):
            a_ = np.sqrt(np.mean(pre[i * w:(i + 1) * w] ** 2)) + 1e-12; b_ = np.sqrt(np.mean(post[i * w:(i + 1) * w] ** 2)) + 1e-12
            if 20 * np.log10(a_) > -40: gr.append(20 * np.log10(a_) - 20 * np.log10(b_))
        return np.array(gr)

    # calibrate the threshold so the median speech gain reduction is ~5 dB (document: 4-6 dB at ~3:1)
    stage = f"{work}/chain_a_{pct}.wav"
    best = None
    for thr in np.arange(-30.0, -9.0, 1.0):
        comp = f"acompressor=threshold={thr:.1f}dB:ratio=3:attack=8:release=150:knee=2.8:makeup=1:detection=rms"
        run(["ffmpeg", "-nostdin", "-loglevel", "error", "-y", "-i", f"{work}/pre_comp_{pct}.wav", "-af", comp, "-c:a", "pcm_f32le", stage])
        post, _ = sf.read(stage)
        gr = gain_reduction(post)
        med = float(np.median(gr))
        if best is None or abs(med - 5.0) < abs(best[1] - 5.0):
            best = (thr, med, comp)
        if med < 4.0:
            break
    thr, _, comp = best
    chain_a = f"{pre_chain},{comp}"
    run(["ffmpeg", "-nostdin", "-loglevel", "error", "-y", "-i", f"{work}/pre_comp_{pct}.wav", "-af", comp, "-c:a", "pcm_f32le", stage])
    post, _ = sf.read(stage)
    gr = gain_reduction(post)
    m1 = ebur128(stage)
    post_gain = -16.0 - m1["short_term_median_lufs"]
    final = f"{out_dir}/VO_processed_{pct}.wav"
    lim = 0.6457  # -3.8 dBFS sample peak so the true (inter-sample) peak stays <= -3 dBFS
    for _ in range(4):
        run(["ffmpeg", "-nostdin", "-loglevel", "error", "-y", "-i", stage, "-af",
             f"volume={post_gain:.2f}dB,alimiter=limit={lim:.4f}:attack=2:release=50:level=false",
             "-ar", str(SR), "-c:a", "pcm_s24le", final])
        m2 = ebur128(final)
        if m2["true_peak_dbfs"] is not None and m2["true_peak_dbfs"] <= -3.0:
            break
        lim *= 10 ** (-0.3 / 20)
    fdur = sf.info(final).duration
    report = {
        "speed": a.speed, "raw_file": os.path.basename(a.raw), "raw_duration_s": round(dur, 3),
        "trim_head_s": round(head / sr, 4), "speech_onset_s": round(onset / sr, 4), "trim_tail_at_s": round(tail / sr, 4),
        "pause_edits": edits, "total_removed_in_pauses_s": round(sum(e["removed"] for e in edits), 3),
        "tightened_duration_s": round(len(out) / sr, 3), "processed_duration_s": round(fdur, 3),
        "keep_segments": tmap, "crossfade_s": xf / sr,
        "rubberband": "tempo=%.2f pitch=1 formant=preserved pitchq=quality (pitch preserved)" % a.speed,
        "loudness_before_chain": m0, "pre_gain_db": round(pre_gain, 2), "chain": chain_a,
        "compressor_gain_reduction_db": {"median_speech": round(float(np.median(gr)), 2), "p90_speech": round(float(np.percentile(gr, 90)), 2), "max": round(float(gr.max()), 2)},
        "compressor_threshold_db": round(float(thr), 1),
        "post_gain_db": round(post_gain, 2), "limiter": f"alimiter limit={20*np.log10(lim):.2f} dBFS sample peak (true peak checked <= -3 dBFS)",
        "final_metrics": m2,
    }
    json.dump(report, open(f"{out_dir}/VO_processing_{pct}.json", "w"), indent=1)
    print(json.dumps({k: report[k] for k in ("trim_head_s", "total_removed_in_pauses_s", "tightened_duration_s", "processed_duration_s",
                                            "pre_gain_db", "compressor_threshold_db", "compressor_gain_reduction_db", "post_gain_db", "limiter", "final_metrics")}, indent=1))


if __name__ == "__main__":
    main()
