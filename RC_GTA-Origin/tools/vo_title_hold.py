#!/usr/bin/env python3
"""Open the B13 title hold in the processed voiceover (see CONFLICTS.md C14).

B13's build needs, after "Grand": T6 types 14 letters at 2f each (28f), holds 1 s (30f), then the
L2 unboxing shot runs for the last 0.8 s (24f) = 82f, but only 41f remain before B14's first word.
The plan also lists "the B13 title hold" among the moments with no voiceover. So the silence after
"Auto." is lengthened by 41 frames (1.3667 s), inside the existing pause, using that pause's own
near-silent room tone (looped with equal-power crossfades). No word is touched.

In : 01_VO/VO_processed_108_nogap.wav (the speed-up result)
Out: 01_VO/VO_processed_108.wav (the locked edit voiceover)
"""
import json, os, shutil
import numpy as np, soundfile as sf

ROOT = "/home/user/claude-test-2.0-/RC_GTA-Origin"
EXTRA = 41 / 30

src = f"{ROOT}/01_VO/VO_processed_108_nogap.wav"
dst = f"{ROOT}/01_VO/VO_processed_108.wav"
if not os.path.exists(src):
    shutil.copy2(dst, src)
x, sr = sf.read(src, dtype="float64")
words = json.load(open(f"{ROOT}/01_VO/VO_words_108.json"))["words"]
auto = next(w for w in words if w["beat"] == "B13" and w["text"] == "Auto.")
nxt = next(w for w in words if w["beat"] == "B14")
a, b = auto["end"], nxt["start"]
mid = (a + b) / 2
# room tone: the quiet middle 60% of the existing pause
tone = x[int((a + 0.2 * (b - a)) * sr):int((a + 0.8 * (b - a)) * sr)]
need = int(round(EXTRA * sr))
xf = int(0.02 * sr)
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
info = sf.info(src)
sf.write(dst, out, sr, subtype=info.subtype)
rep = json.load(open(f"{ROOT}/01_VO/VO_processing_108.json"))
rep["title_hold_gap"] = {"after_word": "Auto. (B13)", "inserted_at_s": round(mid, 4), "inserted_s": round(EXTRA, 4),
                         "frames": 41, "reason": "B13 build: T6 type-on (28f) + hold 1 s + 0.8 s unboxing after 'Grand'; plan lists a VO-free B13 title hold. CONFLICTS.md C14.",
                         "room_tone_rms_dbfs": round(20 * np.log10(np.sqrt(np.mean(tone ** 2)) + 1e-12), 1)}
rep["final_file"] = "01_VO/VO_processed_108.wav"
rep["final_duration_s"] = round(len(out) / sr, 4)
json.dump(rep, open(f"{ROOT}/01_VO/VO_processing_108.json", "w"), indent=1)
print(f"inserted {EXTRA:.4f}s at {mid:.3f}s (pause {a:.3f}-{b:.3f}); room tone {rep['title_hold_gap']['room_tone_rms_dbfs']} dBFS; new length {len(out)/sr:.3f}s")
