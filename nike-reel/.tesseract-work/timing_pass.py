"""Timing pass: VO line boundaries in the 1.07x file -> tightened edit timeline (30 fps)."""
import json
FPS = 30
f = lambda t: round(t * FPS)                      # seconds -> nearest frame
tc = lambda fr: f"{fr//FPS//60}:{(fr//FPS)%60:02d}.{fr%FPS:02d}"   # m:ss.ff
# (id, tag, text, src_start, src_end) measured from silencedetect(-42 dB, 80 ms) + Whisper word times
L = [
 (1,"Text Centerpiece","Well, turns out, Nike needed retail more than anyone.",0.000,3.628),
 (2,"B-roll","That was 2021.",4.111,5.338),
 (3,"Full Cover","Nike was soaring at almost 280 billion dollars.",5.693,9.162),
 (4,"Full Cover","Today? Less than 60 billion dollars.",9.553,12.012),
 (5,"Full Cover","Down almost 80 percent.",12.326,13.924),
 (6,"Full Cover","It even got kicked out of the S&P 100.",14.381,16.495),
 (7,"Text Centerpiece","So what happened?",16.952,18.151),
 (8,"B-roll","In 2020, Nike hired eBay's ex-CEO, John Donahoe.",18.616,22.303),
 (9,"Full Cover","His plan? Cut out the middleman.",22.769,24.558),
 (10,"Full Cover","Nike pulled out of stores like DSW and Dillard's, and sent less to Foot Locker.",24.979,29.082),
 (11,"B-roll","Covid made it look genius.",29.436,31.038),
 (12,"B-roll","Then shoppers went back to stores, and found Hoka and On where Nike used to be.",31.355,35.294),
 (13,"B-roll","And at the gym, Alo and Vuori became the new flex.",35.645,38.551),
 ("CLIP_DONAHOE","Half Cover (live clip)","John Donahoe: \"...we had over-rotated away from wholesale a little more than we intended.\"",None,6.0),
 (14,"Text Centerpiece","And that was only half the problem.",38.950,40.482),
 (15,"B-roll","Meanwhile, Nike drowned the market in the same shoes.",40.824,43.907),
 (16,"Full Cover","Dunks.",44.265,44.720),
 (17,"Full Cover","Air Force 1s.",44.883,45.727),
 (18,"Full Cover","Retro Jordans.",45.929,46.910),
 (19,"Special B-roll","Until there was no line, and no hype.",47.181,49.240),
 (20,"B-roll","In 2024, Donahoe was out.",49.719,51.864),
 (21,"B-roll","His replacement, Elliott Hill, put it simply:",52.257,54.426),
 ("CLIP_HILL","Text Centerpiece (live audio)","Elliott Hill: \"We lost our obsession with sport.\"",None,3.0),
 (22,"B-roll","The fix has been brutal.",54.825,56.406),
 (23,"Full Cover","Tariffs.",56.757,57.365),
 (24,"Full Cover","China down 26 percent in one quarter.",57.635,60.236),
 (25,"Full Cover","And Nike says sales keep falling into 2028.",60.559,63.296),
 (26,"B-roll","Nike didn't lose to one brand.",63.764,65.364),
 (27,"Half Cover","It gave up the shelf, the hype and the athlete.",65.664,68.279),
 (28,"Half Cover","All at once.",68.626,69.408),
]
def build(oleary_s):
    items = [("CLIP_OLEARY","Half Cover (live clip)","Kevin O'Leary: \"...They don't need retail.\"",None,oleary_s)] + L
    t = 0; rows = []; prev = None
    for it in items:
        iid, tag, text, s, e = it
        nxt_is_breath = tag.startswith("Text Centerpiece") or iid in ("CLIP_DONAHOE","CLIP_HILL")
        if prev is not None:
            src_gap = None if (s is None or prev[3] is None) else s - prev[4]
            want = 8 if nxt_is_breath else 5          # frames: 6-10 breath before TCs/clips, else 4-6
            gap = want if src_gap is None else min(want, f(src_gap))
            t += gap
        dur = f(e - s) if s is not None else f(e)
        rows.append(dict(id=iid, tag=tag, text=text, src_in=s, src_out=e if s is not None else None,
                         edit_in=t, edit_out=t + dur))
        t += dur; prev = it
    end_vo = t + 4                                   # 4-frame tail after "once." before the hard cut
    endcard = 68                                     # 2.2567 s attached end card = 68 frames (rounded up)
    return rows, end_vo, end_vo + endcard
for label, ol in (("O'Leary full sentence (~5.0 s est.)",5.0),("O'Leary trimmed to 'They don't need retail.' (~1.5 s est.)",1.5)):
    rows, ec_in, total = build(ol)
    print(f"{label}: end card {tc(ec_in)}-{tc(total)}  TOTAL {total/FPS:.2f} s")
rows, ec_in, total = build(5.0)
json.dump(dict(fps=FPS, rows=rows, endcard_in=ec_in, total=total), open(".tesseract-work/timing_pass.json","w"), indent=1)
print()
for r in rows:
    src = f"{r['src_in']:.3f}-{r['src_out']:.3f}" if r['src_in'] is not None else "clip (est.)"
    print(f"{str(r['id']):13s}|{r['tag']:28s}|{src:15s}|{tc(r['edit_in'])}-{tc(r['edit_out'])}|{(r['edit_out']-r['edit_in'])/FPS:5.2f}|{r['text'][:60]}")
