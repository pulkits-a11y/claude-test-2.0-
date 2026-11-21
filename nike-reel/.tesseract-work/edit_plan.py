"""Nike reel edit plan: script lines, timing rules, segments and B-roll shots.

All VO times are seconds in Sources/voiceover/VO_1.07x.wav (ffmpeg atempo=1.07).
Edit times are integer frames at 30 fps. Re-run with real clip lengths when the
live clips arrive; every cut is derived from the VO word times, so the B-roll
moves with its line.
"""
FPS = 30

# id, tag, text, src_in, src_out   (speech onset/offset in the 1.07x VO)
LINES = [
    (1, "TC", "Well, turns out, Nike needed retail more than anyone.", 0.000, 3.628),
    (2, "FC", "That was 2021.", 4.111, 5.338),
    (3, "FC", "Nike was soaring at almost 280 billion dollars.", 5.693, 9.162),
    (4, "FC", "Today? Less than 60 billion dollars.", 9.553, 12.012),
    (5, "FC", "Down almost 80 percent.", 12.326, 13.924),
    (6, "FC", "It even got kicked out of the S&P 100.", 14.381, 16.495),
    (7, "TC", "So what happened?", 16.952, 18.151),
    (8, "BROLL", "In 2020, Nike hired eBay's ex-CEO, John Donahoe.", 18.616, 22.303),
    (9, "FC", "His plan? Cut out the middleman.", 22.769, 24.558),
    (10, "FC", "Nike pulled out of stores like DSW and Dillard's, and sent less to Foot Locker.", 24.979, 29.082),
    (11, "BROLL", "Covid made it look genius.", 29.436, 31.038),
    (12, "BROLL", "Then shoppers went back to stores, and found Hoka and On where Nike used to be.", 31.355, 35.294),
    (13, "BROLL", "And at the gym, Alo and Vuori became the new flex.", 35.645, 38.551),
    (14, "TC", "And that was only half the problem.", 38.950, 40.482),
    (15, "BROLL", "Meanwhile, Nike drowned the market in the same shoes.", 40.824, 43.907),
    (16, "FC", "Dunks.", 44.265, 44.720),
    (17, "FC", "Air Force 1s.", 44.883, 45.727),
    (18, "FC", "Retro Jordans.", 45.929, 46.910),
    (19, "SPECIAL", "Until there was no line, and no hype.", 47.181, 49.240),
    (20, "BROLL", "In 2024, Donahoe was out.", 49.719, 51.864),
    (21, "BROLL", "His replacement, Elliott Hill, put it simply:", 52.257, 54.426),
    (22, "BROLL", "The fix has been brutal.", 54.825, 56.406),
    (23, "FC", "Tariffs.", 56.757, 57.365),
    (24, "FC", "China down 26 percent in one quarter.", 57.635, 60.236),
    (25, "FC", "And Nike says sales keep falling into 2028.", 60.559, 63.296),
    (26, "BROLL", "Nike didn't lose to one brand.", 63.764, 65.364),
    (27, "HALF", "It gave up the shelf, the hype and the athlete.", 65.664, 68.279),
    (28, "HALF", "All at once.", 68.626, 69.408),
]
LINE = {l[0]: l for l in LINES}

# Order of the edit: VO line ids and live-clip slots.
ORDER = ["CLIP_OLEARY", 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, "CLIP_DONAHOE", 14, 15, 16, 17, 18, 19, 20, 21,
         "CLIP_HILL", 22, 23, 24, 25, 26, 27, 28]
BREATH_BEFORE = {1, 7, 14, "CLIP_DONAHOE", "CLIP_HILL"}   # 8-frame breath before TCs and clips; 5 frames elsewhere
END_TAIL_FRAMES = 4                                      # after "once." before the hard cut to the end card
ENDCARD_FRAMES = 67                                      # attached CTA: 67 video frames at 30 fps


def timeline(clip_frames):
    """Return {item: (edit_in_frame, edit_out_frame)} and the end-card in-frame."""
    t, prev, out = 0, None, {}
    for it in ORDER:
        if prev is not None:
            want = 8 if it in BREATH_BEFORE else 5
            if isinstance(it, int) and isinstance(prev, int):
                src_gap = round((LINE[it][3] - LINE[prev][4]) * FPS)
                want = min(want, src_gap)
            t += want
        dur = clip_frames[it] if isinstance(it, str) else round((LINE[it][4] - LINE[it][3]) * FPS)
        out[it] = (t, t + dur)
        t += dur
        prev = it
    return out, t + END_TAIL_FRAMES


# Segments: (name, kind, first item, label)
SEGMENTS = [
    ("A1_OLEARY", "CLIP", "CLIP_OLEARY", "LIVE CLIP: Kevin O'Leary (Half Cover)"),
    ("TC1", "TC", 1, "Text Centerpiece: Well, turns out, Nike needed retail more than anyone."),
    ("FC1", "FC", 2, "FULL COVER placeholder FC1 (lines 2-6)"),
    ("TC2", "TC", 7, "Text Centerpiece: So what happened?"),
    ("B_L8", "BROLL", 8, None),
    ("FC2", "FC", 9, "FULL COVER placeholder FC2 (lines 9-10)"),
    ("B_L11", "BROLL", 11, None),
    ("A2_DONAHOE", "CLIP", "CLIP_DONAHOE", "LIVE CLIP: John Donahoe (Half Cover)"),
    ("TC3", "TC", 14, "Text Centerpiece: And that was only half the problem."),
    ("B_L15", "BROLL", 15, None),
    ("FC3", "FC", 16, "FULL COVER placeholder FC3 (lines 16-18)"),
    ("S_L19", "SPECIAL", 19, None),
    ("B_L20", "BROLL", 20, None),
    ("TC4_HILL", "CLIP", "CLIP_HILL", "Text Centerpiece + LIVE AUDIO: Elliott Hill"),
    ("B_L22", "BROLL", 22, None),
    ("FC4", "FC", 23, "FULL COVER placeholder FC4 (lines 23-25)"),
    ("B_L26", "BROLL", 26, None),
    ("H_L27", "HALF", 27, None),
]

# Burned-in bug positions: tr = top-right (CNBC / WSJ / Bloomberg), br = bottom-right (ABC7, WSJ Live, CNBC breaking).
BUG = {"WN": "tr", "B04": "tr", "B19": "tr", "B21": "tr", "B31": "tr", "B35": "tr", "B41": "tr", "B59": "tr", "B74": "tr",
       "B32": "tr", "B60": "tr", "B62": "tr", "B78": "tr", "B33": "tr", "B37": "tr", "B44": "tr", "B61": "tr",
       "B39": "tr", "B43": "tr", "B58": "br", "B18": "br", "B51": "br"}

# B-roll shots per segment: (cut line, cut time in VO seconds or None = segment start, clip, clip source second, note)
SHOTS = {
    "B_L8": [(8, None, "B19", 13.4, "Donahoe on CNBC set, 2020"),
             (8, 19.53, "B21", 10.3, "Donahoe portrait (Nike hired)"),
             (8, 20.16, "B21", 13.7, "eBay sign"),
             (8, 20.70, "B18", 34.2, "Donahoe as eBay CEO, WSJ 2014"),
             (8, 21.564, "B21", 17.0, "Donahoe at FN Achievement Awards")],
    "B_L11": [(11, None, "B30", 0.6, "shuttered shop, empty street (Covid)"),
              (11, 29.78, "B32", 16.7, "shopping on a phone (e-commerce boom)"),
              (11, 30.32, "B31", 13.30, "Nike quote card lands; '82 percent' highlight wipes on"),
              (12, None, "B37", 36.0, "store reopening, 'practice social distancing'"),
              (12, 32.28, "B39", 3.3, "Foot Locker storefront"),
              (12, 33.00, "B39", 8.7, "shoe wall with shoppers"),
              (12, 33.48, "B35", 20.85, "Hoka held up to camera"),
              (12, 34.08, "B39", 11.0, "On shoe close-up"),
              (12, 34.48, "B38", 54.4, "Hoka shelf, HOKA NYC flagship"),
              (13, None, "B80", 164.5, "athleisure racks, Alo NYC"),
              (13, 36.537, "B80", 13.4, "Alo storefront logo"),
              (13, 37.04, "B82", 27.8, "inside the new Vuori store"),
              (13, 37.68, "B80", 23.7, "Alo storefront mannequins")],
    "B_L15": [(15, None, "B43", 11.3, "SB Dunk on the floor"),
              (15, 41.507, "B41", 3.40, "stacked orange Nike boxes"),
              (15, 41.96, "B42", 1.6, "Panda Dunk on a Nike box (restocked 15 times)"),
              (15, 43.02, "B54", 1.0, "worker beside walls of stacked Nike boxes (same shoes)")],
    "S_L19": [(19, None, "B52", 21.3, "huge release-day line (Concord 11)"),
              (19, 47.68, "B52", 60.0, "release-day line along the wall, freezes on 'no' (hype) and drains to B&W")],
    "B_L20": [(20, None, "B58", 4.55, "BREAKING NEWS slam"),
              (20, 50.847, "B19", 4.80, "Donahoe portrait"),
              (20, 51.48, "B57", 11.0, "Nike store exterior"),
              (21, None, "B59", 20.7, "Hill intern-to-CEO photo collage"),
              (21, 53.047, "B60", 10.5, "Hill walking"),
              (21, 53.80, "B59", 25.6, "Hill studying the athlete wall in a Nike space")],
    "B_L22": [(22, None, "B54", 39.3, "camera moves through a warehouse of boxes (inventory)"),
              (22, 55.28, "B57", 19.1, "outlet shelves of shoe boxes"),
              (22, 55.84, "B62", 21.0, "Elliott Hill close-up")],
    "B_L26": [(26, None, "B74", 12.9, "rivals' stock chart vs Nike"),
              (26, 64.74, "B75", 350.0, "Foot Locker wall of mixed brands")],
    "H_L27": [(27, None, "B76", 286.9, "SHELF: near-empty wall, Nike store NYC"),
              (27, 67.02, "B51", 28.0, "HYPE: release line on the street (B77 = other moment of B51)"),
              (27, 67.94, "B78", 3.1, "ATHLETE: WNBA All-Star game action"),
              (28, None, "B79", 13.6, "ALL AT ONCE: Swoosh shattering (B79 reversed 13.6s -> 11.4s)")],
}
# 2-3 frame burst inside "in the same" (Act 3's one burst): clip, source second, frames
BURST = [("B42", 2.0, 3), ("B41", 9.25, 2), ("B42", 6.9, 3), ("B57", 24.0, 2)]
FREEZE = {"S_L19": {"freeze_vo": 48.66, "drain_end_vo": 48.94, "clip": "B52", "src": 60.0}}   # second "no" -> "hype"
REVERSE = {"B79": (13.6, 11.4)}

# Live clips: (file, source in s, source out s, linear gain to match the VO)
CLIPS = {"CLIP_OLEARY": ("oleary_fast.mov", 253.90, 254.40, 261.60, 0.944, 1.15),
         "CLIP_DONAHOE": ("donahoe_fast.mov", 472.12, 472.62, 476.38, 0.457, 1.15),
         "CLIP_HILL": ("hill.wav", 527.83, 528.33, 530.12, 0.55, 1.0)}   # (file, file start in source s, in, out, gain, speed)
