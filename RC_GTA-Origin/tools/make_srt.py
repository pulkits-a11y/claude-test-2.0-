#!/usr/bin/env python3
"""Voiceover .srt for accessibility (plan: "Also upload an .srt of the voiceover for accessibility").

Cues follow sentences (split at clause punctuation only when a sentence would exceed two lines),
two lines of at most 42 characters, text = locked-script spelling, times = 01_VO/VO_words_108.json.
"""
import json

ROOT = "/home/user/claude-test-2.0-/RC_GTA-Origin"
MAXL = 42


def tc(t):
    ms = int(round(t * 1000)); h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def text_of(ws):
    t = " ".join(w["text"] for w in ws)
    return t.replace("Race and Chase,", "Race'n'Chase,") if ws and ws[0]["beat"] == "B4" else t


def two_lines(t):
    if len(t) <= MAXL:
        return [t]
    words = t.split(" ")
    best = None
    for i in range(1, len(words)):
        a, b = " ".join(words[:i]), " ".join(words[i:])
        if len(a) <= MAXL and len(b) <= MAXL:
            # prefer breaking after punctuation, then balanced lines
            score = abs(len(a) - len(b)) - (15 if a[-1] in ",.:?!…" else 0)
            if best is None or score < best[0]:
                best = (score, [a, b])
    return best[1] if best else None


def main():
    words = json.load(open(f"{ROOT}/01_VO/VO_words_108.json"))["words"]
    sentences, cur = [], []
    for w in words:
        cur.append(w)
        if w["punct"] in (".", "?", "!") or w["text"].endswith(("?”", ".”")):
            sentences.append(cur); cur = []
    if cur: sentences.append(cur)
    cues = []
    for s in sentences:
        if two_lines(text_of(s)):
            cues.append(s); continue
        # split at clause punctuation into pieces that fit
        piece = []
        for w in s:
            piece.append(w)
            if w["punct"] in (",", ":", "…") and two_lines(text_of(piece)) and len(text_of(piece)) > 20:
                cues.append(piece); piece = []
        if piece: cues.append(piece)
    # anything still longer than two lines: split at the most balanced word boundary (recursively)
    def split_fit(c):
        if two_lines(text_of(c)) or len(c) < 2:
            return [c]
        best = min(range(1, len(c)), key=lambda i: abs(len(text_of(c[:i])) - len(text_of(c[i:]))))
        return split_fit(c[:best]) + split_fit(c[best:])
    cues = [p for c in cues for p in split_fit(c)]
    out = []
    for i, c in enumerate(cues):
        start = c[0]["start"]
        end = c[-1]["end"] + 0.4
        if i + 1 < len(cues):
            end = min(end, cues[i + 1][0]["start"] - 0.001)
        lines = two_lines(text_of(c)) or [text_of(c)]
        out.append(f"{i + 1}\n{tc(start)} --> {tc(end)}\n" + "\n".join(lines) + "\n")
    open(f"{ROOT}/07_Exports/RC_GTA-Origin_v01.srt", "w").write("\n".join(out))
    n = sum(len(text_of(c).split()) for c in cues)
    print(len(cues), "cues,", n, "words (Race'n'Chase counted as one)")


if __name__ == "__main__":
    main()
