#!/usr/bin/env python3
"""Generate the RC kit TRANSITIONS demo: every transition item (X2 X3 X4 X5 X6 X7 X9) in sequence, built exactly as a
beat would (assets/kit/*.css + RCK.transitions), on the labelled stand-in footage from 04_Broll/_placeholders.

  python3 tools/gen_demo.py            -> index.html (the demo)
  python3 tools/gen_demo.py --stills   -> index.html variant without labels and without the X4 tear layers, used once by
                                          tools/make_stills.sh to capture the X4 "old frame" stills (assets/x4/*.png)

All times are frames on the 30 fps grid; data-start/duration strings are floored to 1e-4 s (frame n is drawn at exactly
n/30, so a value rounded up would start one frame late). After generating, tools/apply_treatments.sh persists the
media-treatment controls with the CLI (blur controls for X6, 6 px channel split for the X4 live views).
"""
import math
import sys

FPS = 30
STILLS = "--stills" in sys.argv


def attr(n):
    return "%.4f" % (math.floor(n * 10000 / FPS + 1e-6) / 10000)


def dur(n0, n1):
    return "%.4f" % ((math.floor(n1 * 10000 / FPS + 1e-6) - math.floor(n0 * 10000 / FPS + 1e-6)) / 10000)


def T(n):
    return "%.6f" % (n / FPS)


els = []      # html lines
js = []       # timeline lines
track = [0]


def clip(tag, id_, cls, n0, n1, inner="", extra="", z=None, self_close=False):
    track[0] += 1
    style = f' style="z-index: {z};"' if z is not None else ""
    a = f'<{tag} id="{id_}" class="clip {cls}" data-start="{attr(n0)}" data-duration="{dur(n0, n1)}" data-track-index="{track[0]}"{extra}{style}>'
    return a if self_close else a + inner + f"</{tag}>"


def video(id_, rid, n0, n1, cls="demo-full", media_n0=0, extra="", z=None):
    ms = f' data-media-start="{attr(media_n0)}"' if media_n0 else ""
    return clip("video", id_, cls, n0, n1, extra=f' src="assets/footage/{rid}.mp4" muted playsinline{ms}{extra}', z=z)


def tag(id_, n0, n1, text, on_card=False):
    if STILLS:
        return ""
    return clip("div", id_, "demo-tag" + (" rc-on-card" if on_card else ""), n0, n1, inner=text, extra=" data-layout-ignore", z=60)


# ------------------------------------------------------------------ A  X2 cut, then drift (B6 into the quote card)
A0, A_CUT, A1 = 0, 30, 75
els += [
    "<!-- A  X2 cut, then drift: B6 'X2 into the quote card' (the L5 card content slides 60 px left over 20f, ease out) -->",
    video("a-out", "R5.1", A0, A_CUT, z=1),
    clip("div", "a-card", "rc-card demo-full", A_CUT, A1, z=1),
    '<div id="a-drift" class="rc-x2" style="z-index: 3;">',
    "  " + video("a-clip", "R6.1", A_CUT, A1, cls="demo-l5 demo-a-clip", z=1),
    "  " + clip("div", "a-t8", "rc-t8 rc-t8--right rc-on-card", A_CUT, A1,
                inner='<div class="rc-t8__block"><div class="rc-t8__quote">“awful… too sim-y.”</div><div class="rc-t8__name">Gary Penn</div><div class="rc-t8__role">DMA DESIGN · GAMASUTRA, 2011</div></div>', z=2),
    "</div>",
    tag("a-tag", A0, A_CUT, "DEMO · X2 cut, then drift (B6): outgoing shot, hard cut at 1.000 s"),
    tag("a-tag2", A_CUT, A1, "DEMO · X2: after the cut the card content slides 60 px left over 20f, ease out (lands 1.667 s)", on_card=True),
]
js.append(f"X.drift(tl, '#a-drift', {T(A_CUT)}, {{ px: 60, dir: 'left' }});")

# ------------------------------------------------------------------ B  X3 white flash (B10 on "fun", B13 into the framed clip)
B0, B_CUT, B1 = 75, 110, 135
els += [
    "<!-- B  X3 white flash centred on the cut (B10 'fun': flash, S09 and the music drop on the same frame) -->",
    video("b-out", "R9.2", B0, B_CUT, z=1),
    video("b-in", "R10.1", B_CUT, B1, z=1),
    '<div id="b-x3" class="rc-x3" style="z-index: 20;"></div>',
    tag("b-tag", B0, B1, "DEMO · X3 white flash (B10, B13): ramp 2f, hold 1f, fade 4f, centred on the cut at 3.667 s"),
]
js.append(f"X.flash(tl, '#b-x3', {T(B_CUT)});")

# ------------------------------------------------------------------ C  X4 still mode (B8: the stamp card shatters, cuts to black)
C0, C_T, C_N, C1 = 135, 175, 10, 210
els += [
    "<!-- C  X4 pixel-block tear, still mode (B8 on 'breaks': the stamp card shatters, then cut to black #0A0A0A) -->",
    clip("div", "c-card", "rc-card demo-full", C0, C_T + C_N, z=1),
    video("c-clip", "R7.1", C0, C_T + C_N, cls="demo-l5 demo-c-clip", z=2),
    clip("div", "c-black", "rc-ink demo-full", C_T + C_N, C1, z=1),
]
if not STILLS:
    els += ['<div id="c-x4" class="rc-x4" style="z-index: 10;"><img class="rc-x4__still" src="assets/x4/c-old.png" alt=""></div>']
    js.append(f"X.tear(tl, '#c-x4', {T(C_T)}, {{ frames: {C_N}, seed: 8 }});")
els += [
    tag("c-tag", C0, C_T, "DEMO · X4 still mode (B8): stamped L5 card stand-in; tear on 'breaks' at 5.833 s", on_card=True),
    tag("c-tag2", C_T, C1, "DEMO · X4: 10f, 16 x 9 blocks jump ±30 px, some freeze, 6 px RGB split, then cut to black"),
]

# ------------------------------------------------------------------ D  X4 live mode (B2: on the CRT picture only, freezes torn)
D0, D_T, D_N, D1 = 210, 250, 8, 285
SCR = (660, 300, 600, 450)
views = "".join(
    f'<div class="rc-x4__view">{video(f"d-v{i}", "R9.1", D0, D1, cls="demo-view")}</div>' for i in (1, 2, 3))
els += [
    "<!-- D  X4 live mode (B2 on 'broke': the tear stays on the CRT picture; 3 live views + still for frozen blocks; holds) -->",
    video("d-plate", "R3.9", D0, D1, z=1),
    video("d-pic", "R9.1", D0, D1, cls="demo-crtpic", z=2),
]
if not STILLS:
    els += [f'<div id="d-x4" class="rc-x4 demo-crtx4" style="z-index: 10;"><img class="rc-x4__still" src="assets/x4/d-old.png" alt="">{views}</div>']
    js.append(f"X.tear(tl, '#d-x4', {T(D_T)}, {{ frames: {D_N}, end: 'hold', until: {T(D1)}, seed: 2 }});")
els += [
    tag("d-tag", D0, D_T, "DEMO · X4 live mode (B2): picture in a screen region of the CRT plate stand-in"),
    tag("d-tag2", D_T, D1, "DEMO · X4: 8f tear on the screen region only (live views + still), then holds the torn frame"),
]

# ------------------------------------------------------------------ E  X4 still mode, 6f (B17: final tear on the logo, then black)
E0, E_T, E_N, E1 = 285, 315, 6, 330
els += [
    "<!-- E  X4 still mode, 6f (B17: final tear on the GTA 6 logo end card, then black) -->",
    video("e-logo", "R17.4", E0, E_T + E_N, z=1),
    clip("div", "e-black", "rc-ink demo-full", E_T + E_N, E1, z=1),
]
if not STILLS:
    els += ['<div id="e-x4" class="rc-x4" style="z-index: 10;"><img class="rc-x4__still" src="assets/x4/e-old.png" alt=""></div>']
    js.append(f"X.tear(tl, '#e-x4', {T(E_T)}, {{ frames: {E_N}, seed: 17 }});")
els += [tag("e-tag", E0, E1, "DEMO · X4 still mode (B17): 6f tear on the logo end card stand-in (R17.4) at 10.5 s, then black")]

# ------------------------------------------------------------------ F  X5 blinds (B2 -> B3 into the T3 year card; B14 -> B15)
F0, F_B, F_N, F1 = 330, 375, 8, 420
els += [
    "<!-- F  X5 blinds wipe split on a beat boundary at frame 375: OUT half = last 8f of the outgoing comp (f-close),",
    "     IN half = first 8f of the incoming comp (f-open, shut on the boundary frame) -->",
    video("f-out", "R1.3", F0, F_B, z=1),
    clip("div", "f-close", "rc-x5", F_B - F_N, F_B, z=20),
    clip("div", "f-t3", "rc-t3", F_B, F1, inner='<div class="rc-t3__block"><div class="rc-t3__in">In</div><div class="rc-t3__year"><span class="rc-t3__num">1995</span></div></div>', z=1),
    clip("div", "f-open", "rc-x5", F_B, F_B + F_N, z=20),
    tag("f-tag", F0, F_B, "DEMO · X5 OUT half (end of B2 / B14): 12 slats rotate shut over the last 8f (constant speed)"),
    tag("f-tag2", F_B, F1, "DEMO · X5 IN half (start of B3 / B15): shut on the boundary frame 12.5 s, open over 8f", on_card=True),
]
js.append(f"X.blindsClose(tl, '#f-close', {T(F_B)});")
js.append(f"X.blindsOpen(tl, '#f-open', {T(F_B)});")
js.append(f"RCK.type.yearCard(tl, '#f-t3', {T(F_B + 10)});")

# ------------------------------------------------------------------ G  X6 OUT (B2: the GTA 6 frame shrinks into the CRT screen)
G0, G_T, G_N, G1 = 420, 435, 8, 495
G_PIC = (1040, 360, 320, 180)        # 16:9 picture letterboxed in a 4:3 CRT screen stand-in (1040, 330, 320, 240)
els += [
    "<!-- G  X6 OUT (B2): B1's last full-frame GTA 6 shot (g-b1) continues inside the world at 600% and shrinks into the",
    "     CRT screen over 8f. Picture rect 320 x 180 = exactly 1/6 of the frame, so 600% is the full frame (seamless). -->",
    video("g-b1", "R17.1", G0, G_T, z=1),
    '<div id="g-world" class="rc-x6" style="z-index: 2;">',
    "  " + video("g-plate", "R3.9", G_T, G1, extra=' style="--hf-color-grading-blur: 0"'),
    "  " + clip("div", "g-crt", "demo-screen", G_T, G1, extra=' data-layout-ignore style="left: 1040px; top: 330px; width: 320px; height: 240px;"'),
    f'  <div id="g-box" class="rc-x6__screen">{video("g-pic", "R17.1", G_T, G1, cls="demo-pic", media_n0=G_T - G0, extra=" style=\"--hf-color-grading-blur: 0\"")}</div>',
    "</div>",
    tag("g-tag", G0, G_T, "DEMO · X6 OUT (B2): B1's last frames, full-frame GTA 6 stand-in (R17.1)"),
    tag("g-tag2", G_T, G1, "DEMO · X6 OUT: 600% -> 100% into the CRT screen over 8f (log-scale ease out), motion blur via media-treatment"),
]
js.append(f"X.zoomFit('#g-box', {{ rect: [{G_PIC[0]}, {G_PIC[1]}, {G_PIC[2]}, {G_PIC[3]}] }}, {{ res: 6 }});")
js.append(f"X.zoom(tl, '#g-world', {T(G_T)}, {{ screen: {{ rect: [{G_PIC[0]}, {G_PIC[1]}, {G_PIC[2]}, {G_PIC[3]}] }}, dir: 'out' }});")

# ------------------------------------------------------------------ H  X6 IN (B15: zoom through the cabinet screen into full-frame gameplay)
H0, H_T, H_N, H1 = 495, 530, 8, 570
H_PIC = (1200, 400, 320, 180)
els += [
    "<!-- H  X6 IN (B15): zoom through the cabinet screen 100% -> 600% over 8f; at 600% the screen picture IS the frame,",
    "     so the plain full-frame R15.1 (h-full, same media time) takes over invisibly one frame after the landing -->",
    '<div id="h-world" class="rc-x6" style="z-index: 2;">',
    "  " + video("h-plate", "R15.3", H0, H_T + H_N + 1, extra=' style="--hf-color-grading-blur: 0"'),
    "  " + clip("div", "h-bezel", "demo-screen", H0, H_T + H_N + 1, extra=' data-layout-ignore style="left: 1184px; top: 384px; width: 352px; height: 212px;"'),
    f'  <div id="h-box" class="rc-x6__screen">{video("h-pic", "R15.1", H0, H_T + H_N + 1, cls="demo-pic", extra=" style=\"--hf-color-grading-blur: 0\"")}</div>',
    "</div>",
    video("h-full", "R15.1", H_T + H_N + 1, H1, media_n0=H_T + H_N + 1 - H0, z=1),
    tag("h-tag", H0, H1, "DEMO · X6 IN (B15): cabinet screen + bezel stand-in on the arcade plate (R15.3); 100% -> 600% over 8f at 17.667 s"),
]
js.append(f"X.zoomFit('#h-box', {{ rect: [{H_PIC[0]}, {H_PIC[1]}, {H_PIC[2]}, {H_PIC[3]}] }}, {{ res: 6 }});")
js.append(f"X.zoom(tl, '#h-world', {T(H_T)}, {{ screen: {{ rect: [{H_PIC[0]}, {H_PIC[1]}, {H_PIC[2]}, {H_PIC[3]}] }}, dir: 'in' }});")

# ------------------------------------------------------------------ I  X7 light-leak dissolve (B16 into the T5 glow line on black)
I0, I_T, I_N, I1 = 570, 600, 14, 645
els += [
    "<!-- I  X7 light-leak dissolve (B16): the rewind run dissolves to black through the leak (Screen), 14f; then T5 -->",
    clip("div", "i-black", "rc-ink demo-full", I0, I1, z=1),
    video("i-out", "R14.1", I0, I_T + I_N, z=2),
    '<div id="i-x7" class="rc-x7" style="z-index: 5;"></div>',
    clip("div", "i-t5", "rc-t5", I_T + I_N + 6, I1, inner='<div class="rc-t5__text">The whole series started with a bug.</div>', z=3),
    tag("i-tag", I0, I1, "DEMO · X7 (B16): 14f dissolve to black #0A0A0A through the light leak (Screen; RT6 stand-in) at 20.0 s, then T5"),
]
js.append(f"X.leakDissolve(tl, '#i-x7', {T(I_T)}, {{ frames: {I_N}, from: '#i-out' }});")
js.append(f"RCK.type.glowLine(tl, '#i-t5', {T(I_T + I_N + 6)});")

# ------------------------------------------------------------------ J  X9 siren wash (B1 "cops", B5 "police officer")
J0, J_W1, J_S, J_W2, J1 = 645, 670, 690, 700, 720
els += [
    "<!-- J  X9 siren wash: B1 on 'cops' over the full-frame GTA 6 shot, B5 on 'police officer' over the split screen -->",
    video("j-a", "R1.2", J0, J_S, z=1),
    video("j-l", "R5.4", J_S, J1, cls="demo-half demo-left", z=1),
    video("j-r", "R5.1", J_S, J1, cls="demo-half demo-right", z=1),
    '<div id="j-x9" class="rc-x9" style="z-index: 20;"></div>',
    tag("j-tag", J0, J_S, "DEMO · X9 (B1 'cops'): 4f overlay at 22.333 s, #E3262E 35% Overlay 2f, then #2D5BFF 2f"),
    tag("j-tag2", J_S, J1, "DEMO · X9 (B5 'police officer'): the same wash over the L11 split-screen stand-in at 23.333 s"),
]
js.append(f"X.sirenWash(tl, '#j-x9', {T(J_W1)});")
js.append(f"X.sirenWash(tl, '#j-x9', {T(J_W2)});")

TOTAL = J1
html = f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1920, height=1080" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
    <link rel="stylesheet" href="assets/kit/base.css" />
    <link rel="stylesheet" href="assets/kit/type.css" />
    <link rel="stylesheet" href="assets/kit/motifs.css" />
    <link rel="stylesheet" href="assets/kit/transitions.css" />
    <link rel="stylesheet" href="assets/kit/screens.css" />
    <style>
      /* demo-only: base.css lists "Neue Haas Grotesk" as an Inter fallback; HyperFrames lint fails any family without an
         @font-face (font_family_without_font_face). Alias it to the kit's own Inter file (never shown: Inter loads first).
         Reported to the kit owner: base.css should drop the name or carry this alias. */
      @font-face {{ font-family: "Neue Haas Grotesk"; src: url("assets/kit/fonts/Inter-Medium.ttf") format("truetype"); font-weight: 500; font-style: normal; font-display: block; }}
      html, body {{ margin: 0; width: 1920px; height: 1080px; overflow: hidden; background: #0A0A0A; }}
      #root {{ position: relative; width: 1920px; height: 1080px; overflow: hidden; background: #0A0A0A; }}
      /* demo-only scaffolding: stand-ins for screens owned by other kit areas (not part of the transitions kit) */
      .demo-full {{ position: absolute; left: 0; top: 0; width: 1920px; height: 1080px; object-fit: cover; }}
      .demo-tag {{ position: absolute; left: 96px; top: 54px; height: 28px; font-family: var(--sans); font-weight: 500; font-size: 20px;
        line-height: 28px; color: var(--white); opacity: 0.85; white-space: nowrap; text-shadow: var(--text-shadow); }}
      .demo-tag.rc-on-card {{ color: var(--card-ink); text-shadow: none; }}
      .demo-l5 {{ position: absolute; box-sizing: border-box; border: 8px solid var(--white); box-shadow: 0 12px 30px rgba(0, 0, 0, 0.25); object-fit: cover; }}
      .demo-a-clip {{ left: 120px; top: 250px; width: 860px; height: 580px; }}
      .demo-c-clip {{ left: 410px; top: 190px; width: 1100px; height: 700px; }}
      .demo-crtpic {{ position: absolute; left: {SCR[0]}px; top: {SCR[1]}px; width: {SCR[2]}px; height: {SCR[3]}px; object-fit: cover; }}
      .demo-crtx4 {{ left: {SCR[0]}px; top: {SCR[1]}px; width: {SCR[2]}px; height: {SCR[3]}px; }}
      .demo-view {{ position: absolute; left: 0; top: 0; width: 100%; height: 100%; object-fit: cover; }}
      .demo-screen {{ position: absolute; background: var(--ink-black); }}
      .demo-pic {{ position: absolute; left: 0; top: 0; width: 100%; height: 100%; object-fit: cover; }}
      .demo-half {{ position: absolute; top: 0; width: 958px; height: 1080px; object-fit: cover; }}
      .demo-left {{ left: 0; }}
      .demo-right {{ left: 962px; }}
    </style>
  </head>
  <body>
    <!-- RC kit TRANSITIONS demo (X2 X3 X4 X5 X6 X7 X9), built exactly as a beat would: assets/kit + RCK.transitions.
         Footage = labelled stand-ins from 04_Broll/_placeholders. Rebuild: python3 tools/gen_demo.py && sh tools/apply_treatments.sh
         Segment times: A X2 0-2.5 s | B X3 2.5-4.5 | C X4 still 4.5-7 | D X4 live 7-9.5 | E X4 6f 9.5-11 | F X5 11-14 |
         G X6 out 14-16.5 | H X6 in 16.5-19 | I X7 19-21.5 | J X9 21.5-24 -->
    <div id="root" data-composition-id="transitions-demo" data-start="0" data-duration="{T(TOTAL)[:-2]}" data-width="1920" data-height="1080">
      {chr(10).join('      ' + e for e in els if e).lstrip()}
    </div>
    <script src="assets/kit/type.js"></script>
    <script src="assets/kit/motifs.js"></script>
    <script src="assets/kit/transitions.js"></script>
    <script src="assets/kit/screens.js"></script>
    <script>
      window.__timelines = window.__timelines || {{}};
      const tl = gsap.timeline({{ paused: true }});
      const X = RCK.transitions;
      {chr(10).join('      ' + j for j in js).lstrip()}
      tl.to({{}}, {{ duration: {T(TOTAL)} }}, 0);
      window.__timelines["transitions-demo"] = tl;
    </script>
  </body>
</html>
"""
open("index.html", "w").write(html)
print("wrote index.html", "(stills variant)" if STILLS else "", f"{TOTAL} frames = {TOTAL / FPS:.3f} s")
