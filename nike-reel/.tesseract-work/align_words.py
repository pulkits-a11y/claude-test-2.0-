"""Align script words (exact wording) to Whisper word times on the 1.07x VO; snap onsets after pauses."""
import json, re, difflib
from edit_plan import LINES
W = json.load(open('vo_107_words.json'))['words']
sil = []
for l in open('vo_107_silences.txt'):
    a, b = l.split()[0].split('-'); sil.append((float(a), float(b)))
def norm(t):
    t = t.lower().replace('$', '').replace('%', ' percent').replace('&', 'and')
    t = re.sub(r"[^a-z0-9' ]", ' ', t)
    return t.split()
out = {}
for lid, tag, text, s_in, s_out in LINES:
    words = text.split()
    wh = [w for w in W if w['e'] > s_in - 0.15 and w['s'] < s_out + 0.15 and w['p'] > 0.05]
    # token streams with back-references
    st, sref = [], []
    for i, w in enumerate(words):
        for tok in norm(w): st.append(tok); sref.append(i)
    wt, wref = [], []
    for j, w in enumerate(wh):
        for tok in norm(w['w']): wt.append(tok); wref.append(j)
    times = [None] * len(words)
    sm = difflib.SequenceMatcher(a=st, b=wt, autojunk=False)
    for blk in sm.get_matching_blocks():
        for k in range(blk.size):
            i, j = sref[blk.a + k], wref[blk.b + k]
            ws, we = wh[j]['s'], wh[j]['e']
            if times[i] is None: times[i] = [ws, we]
            else: times[i][1] = max(times[i][1], we)
    # interpolate unmatched words between neighbours (by character share)
    for i in range(len(words)):
        if times[i] is None:
            j = i
            while j < len(words) and times[j] is None: j += 1
            a = times[i - 1][1] if i > 0 else s_in
            b = times[j][0] if j < len(words) else s_out
            if b <= a and i > 0:  # previous word absorbed this one: split it by characters
                ps, pe = times[i - 1]; cs = [len(words[k]) for k in range(i - 1, j)]
                tot = sum(cs); t = ps
                for k, c in zip(range(i - 1, j), cs):
                    d = (pe - ps) * c / tot; times[k] = [t, t + d]; t += d
            else:
                cs = [len(words[k]) for k in range(i, j)]; tot = sum(cs); t = a
                for k, c in zip(range(i, j), cs):
                    d = (b - a) * c / tot; times[k] = [t, t + d]; t += d
    # several script words matched to one Whisper token ("80%" -> "80 percent"): split its span by characters
    i = 0
    while i < len(words):
        j = i
        while j + 1 < len(words) and times[j + 1] == times[i]: j += 1
        if j > i:
            ps, pe = times[i]; cs = [len(words[k]) for k in range(i, j + 1)]; tot = sum(cs); t = ps
            for k, c in zip(range(i, j + 1), cs):
                d = (pe - ps) * c / tot; times[k] = [t, t + d]; t += d
        i = j + 1
    # snap: first word to the measured line onset; only the first word after each pause to the pause end
    times[0][0] = s_in
    for a, b in sil:
        if not (s_in < b < s_out) or b - a < 0.08: continue
        cand = [k for k in range(1, len(words)) if times[k][0] >= a - 0.05 and abs(times[k][0] - b) <= 0.15]
        if cand:
            k = min(cand, key=lambda k: times[k][0])
            times[k][0] = b
            if times[k - 1][1] > a: times[k - 1][1] = a
    times[-1][1] = s_out
    out[lid] = [{'w': w, 's': round(t[0], 3), 'e': round(t[1], 3)} for w, t in zip(words, times)]
json.dump(out, open('vo_words_aligned.json', 'w'), indent=1)
for lid in out:
    print(lid, ' '.join(f"{x['w']}@{x['s']:.2f}" for x in out[lid]))
