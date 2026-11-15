"""Shared helpers: locked-script tokens, whisper alignment, energy pauses."""
import json, re, difflib
import numpy as np, soundfile as sf

ROOT = "/home/user/claude-test-2.0-/RC_GTA-Origin"
NUM = {"6": "six", "1995": "nineteenninetyfive", "1997": "nineteenninetyseven", "18": "eighteen", "30": "thirty"}

def script_tokens():
    s = json.load(open(f"{ROOT}/tools/script_v2.json"))
    toks = []
    for beat, text in s.items():
        for i, w in enumerate(text.split()):
            punct = ""
            m = re.search(r"([\.,\?\!:…;]+)[”\"]*$", w)
            if m: punct = m.group(1)
            toks.append({"beat": beat, "text": w, "punct": punct, "first_in_beat": i == 0})
    return toks

def norm(w):
    w = w.lower().replace("’", "'").replace("“", "").replace("”", "")
    w = re.sub(r"[^a-z0-9']", "", w)
    return NUM.get(w, w)

def expand_script(toks):
    """Race'n'Chase is spoken as 3 words; split it so it aligns with ASR output."""
    out = []
    for i, t in enumerate(toks):
        if norm(t["text"]).startswith("race'n'chase"):
            for j, part in enumerate(["Race", "and", "Chase"]):
                out.append(dict(t, text=part if j < 2 else "Chase,", sub=j, punct=(t["punct"] if j == 2 else ""), src=i,
                                first_in_beat=t["first_in_beat"] and j == 0))
        elif norm(t["text"]) == "simy":
            out.append(dict(t, src=i))
        else:
            out.append(dict(t, src=i))
    return out

def align(script, words):
    a = [norm(t["text"]) for t in script]
    b = [norm(w["text"]) for w in words]
    b = ["simy" if x == "semi" else x for x in b]
    sm = difflib.SequenceMatcher(a=a, b=b, autojunk=False)
    mapping = {}
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal" or (tag == "replace" and i2 - i1 == j2 - j1):
            for k in range(i2 - i1): mapping[i1 + k] = j1 + k
        else:
            print("ALIGN", tag, a[i1:i2], b[j1:j2])
    return mapping

def energy_pauses(path, thr_db=-45.0, min_dur=0.12, hop_s=0.005, win_s=0.02):
    x, sr = sf.read(path)
    if x.ndim > 1: x = x.mean(axis=1)
    hop, win = int(hop_s * sr), int(win_s * sr)
    n = (len(x) - win) // hop
    fr = np.lib.stride_tricks.sliding_window_view(x, win)[::hop][:n]
    db = 20 * np.log10(np.sqrt((fr ** 2).mean(axis=1)) + 1e-12)
    t = np.arange(n) * hop / sr + win / 2 / sr
    sil = db < thr_db
    runs, i = [], 0
    while i < n:
        if sil[i]:
            j = i
            while j < n and sil[j]: j += 1
            s, e = t[i], t[j - 1]
            if e - s >= min_dur: runs.append([float(s), float(e)])
            i = j
        else:
            i += 1
    return runs, len(x) / sr
