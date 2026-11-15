# B16 Started with a bug: beat notes (b16-bug-origin)

Plan p.27 (B16 build), p.19 (overview row: VHS rewind run -> black glow line, M4 bug chip; T5 -> T7; X1, X7; S17; MU7),
p.16 (into the beat: "B16 X1, then X7"), T5/T7 p.12, X7 p.16, M4 p.17, palette p.10 ("Ink black: black screens (B8, B16)"),
B-roll p.32 (RT1, RT6), music MU7 p.34, silence p.38. STORYBOARD.md B16. Frames are **beat frames** (f0 = "So");
composition local frame = beat frame + 6. Composition: 132 frames (120 + 6f handles),
`05_GFX/renders/b16-bug-origin.mov`. **Fully HyperFrames-owned and opaque** (no Tesseract shots).

## 1. What the viewer sees

The tape rewinds: the B14 chases, then GTA 1's top-down chase, then the 1995 design document fly backwards through VHS noise
and tracking lines, the page settles, dissolves through a warm light leak to black, and a glowing serif line says "The whole
series started with a [bug]." with the pixel bug popping in as "bug" is spoken.

## 2. Assets

| Kind | ID / file | Use |
|---|---|---|
| B-roll (reused B14) | R14.5 (escape + 2013), RT3, R1.3, R14.4, R14.3, R14.2, R14.1 | rewind f-6..12, reversed 8x |
| B-roll (reused B9) | R9.1 GTA 1 police chase | rewind f13-22, reversed 8x |
| B-roll (reused B4) | R4.5 design-document title page (REAL still, `assets/footage/R4.5.png`) | rewind f23-29 (zoom back out), held f30-44 under X7 (0.7 s on screen in all: < 1.5 s, always with camera motion until it stops) |
| Derived clip | `assets/rewind/b16-rewind.mp4` (52 frames) + `b16-rewind.map.json` | built by `tools/make_rewind.py` from the synced footage |
| Textures (stand-ins) | **RT1** VHS overlay -> media-treatment VHS Playback look + drawn tracking lines; **RT6** light leaks -> the kit X7 leak (registry `organic-light-leak-overlay`, retinted to #FFF6E0) | synced in `assets/footage/` but NOT wired (see Pending) |
| SFX | **S17** "Spinback (2)" (1 s) | starts f0 with the rewind |
| Music | **MU7**: cut the music under the 1 s rewind, resume 6 dB lower under the glow line (from f30) | Tesseract |
| Fonts | Inter Medium 500 (T1), Instrument Serif Italic (T5) | kit |
| Kit | T1 `captionPlan`, X7 `leakDissolve`, T5 `glowLine` (+ T7/M4 chip pop), L7 `rc-l7__dim` (B4's dim on the page), M4 `m4-chip` + `svg/motifs-bug.svg` (same asset as B2) | `assets/kit/` |

## 3. Tools and layer stack

HyperFrames only (Tesseract places the render and the audio). Top to bottom:
1. T1 captions (z 20), white + soft shadow
2. `#b16-t5` T5 glow line (z 10) from f53: ink-black ground of its own, the line + two blurred glow copies, the M4 chip,
   its light leak drifting behind
3. `#b16-x7` X7 leak (z 6), Screen blend, f30-44
4. `#b16-track` tracking lines (z 5), f-6..30: two SVG noise bands (white only)
5. `#b16-rewind-wrap` (z 2, faded 1 -> 0 by X7): `#b16-rewind` video with the VHS media treatment, and over it (f23-44) the
   kit L7 dim (#0A0A0A at 65% with B4's spotlight hole on the title), scaled per frame with the page zoom
6. `#b16-ground` ink black #0A0A0A, whole composition

## 4. Step-by-step build (beat frames; seconds from the beat start)

| Beat f | What | Values |
|---|---|---|
| -6..2 | rewind: B14's escape shot (R14.5) running backwards from B14's last frame, 8 edit frames per frame (the head handle continues it backward) | 8x reversed |
| 0 (0.0 s) | T1 "So that's why" hard cut in on "So" (-0.39f) | x 960, y 620 |
| 3..4 | police lights (RT3) reversed | |
| 5..7 | GTA 5 chase (R1.3) reversed | |
| 8..12 | the L10 burst reversed, one frame per game, newest to oldest: 2013, 2008, 2004, 2002, 2001 | |
| 13..22 | B9's GTA 1 chase (R9.1) reversed 8x from B9's last L1 frame | |
| 14 (0.47 s) | T1 "you're always running." on "you're" (-0.46f), stays until "The" (f53) | |
| 23..29 | the design document in B4's framing (1.4 x page px, title centre on (960, 400)) zooms back out 118% -> 100% about (959, 402) = B4's push run backwards at 8x (3.27% per frame); B4's L7 dim + spotlight on the title scales with it | |
| 0..30 | VHS look on the whole run; tracking lines: band A (70-110 px) rolling up through the lower third, band B (14-30 px) rolling down through the upper half, new noise every frame, both clear of the caption line | seeded, frame-exact |
| 30 (1.0 s) | the tape stops (tracking lines off, page held at 100%); **X7**: picture opacity 1 -> 0 linear over 14f while the leak rises to 0.9 at f37 (sine.out) and falls to 0 at f44 (sine.in), Screen blend, layers drifting | silent |
| 44..53 | black #0A0A0A (caption still on until f53) | |
| 53 (1.77 s) | **T5** "The whole series started with a [chip]." fades in over 12f: opacity 0 -> 1 linear, blur 20 -> 0 px and tracking +2% -> 0 (power3.out); glow copies blur 24 px @ 60% and 60 px @ 30%; light leak behind rises to 0.16, settles 0.1, drifts to the end | Instrument Serif Italic 84 px, warm glow #FFF6E0 |
| 101 (3.37 s) | **M4 bug chip** pops in place of "bug" as it is spoken: scale 0 -> 112% (5f, power3.out) -> 100% (3f, power2.inOut) = T7, the only bouncy animation | 72 x 56 chip, 12 px radius, card ink, white 8-bit beetle |
| 109..126 | line + chip hold (tail handle included); on screen f53-120 = 2.2 s (>= 1.5 s) | |

VHS treatment on `#b16-rewind` (CLI `media-treatment`, VHS Playback recipe inside its ranges, tracking/speed at the top for a
rewind): `adjust {contrast -0.04, saturation -0.08}`, `details {grain 0.16, grainSize 0.12, grainRoughness 0.72}`,
`effects {tapeDamage 0.85, tapeTracking 0.9, tapeNoise 0.35, tapeSpeed 0.65, chromaBleed 0.5, chromaticAberration 0.18,
scanlines 0.35, scanlineCount 0.17, scanlineSoftness 1, digitalGlitch 0.32, digitalGlitchLineTear 0.08}` (other glitch
controls 0).

## 5. On-screen text

| Text (exact) | Style | Position / size | On / off (beat f) |
|---|---|---|---|
| So that's why | T1 | x 960, y 620; Inter Medium 46 px, white + soft shadow | 0 -> 14 |
| you're always running. | T1 | same | 14 -> 53 |
| The whole series started with a [bug chip]. | T5 + T7 chip (M4) | one line centred on (960, 540); Instrument Serif Italic 84 px #FFF6E0 with two glow copies; chip 72 x 56 in place of "bug" | line 53 -> 126 (end), chip 101 -> 126 |

T-styles featured: T5 -> T7 (rotation p.13 "B16 T5 -> T7"; B15 = T1 -> T9, B17 = T2 -> T10). B16 is a bug beat, so the
VHS/tape glitch look is allowed; no X9, no X4, no T10 here.

## 6. Audio (Tesseract places them from `cues.json`)

| Cue | Event (beat f) | Placement | Level |
|---|---|---|---|
| S17 "Spinback (2)" (1 s) | `rewind` = 0 | start with the rewind (the rewind runs f0-30) | -12 dBFS |
| MU7 | f0-30 / from f30 | cut the music under the rewind; resume 6 dB lower under the glow line from f30 | - |
| X7, the chip | `chip` = 101 | **no SFX**: silence by design under the B16 glow line (plan p.38) | - |

## 7. Mistakes to avoid

- This is the one quiet, reflective beat: no sound on the chip, no extra motion on the line once it lands.
- Keep the glow line on screen >= 1.5 s (here 2.2 s) and the chip exactly on "bug".
- Don't let the tracking noise cross the caption line; don't add a "REW" or "<<" OSD (not in the plan).
- The design document is a still: on screen < 1.5 s and always moving until the tape stops (f23-30 zoom, held only under the
  dissolve). Show the title page only (no robber-mode pages: accuracy note p.39).
- Rebuild the rewind clip whenever the footage or the B14/B9/B4 in-points change (`python3 tools/make_rewind.py`).

## Interpretations / conflicts

1. **"Reversed at 8x" with ~1 s:** a literal 8x rewind of B14 alone would take 23.5 frames, so the B14 part is compressed: it
   steps back 8 edit frames per frame within each shot and jumps between shots (escape 3f + handle, lights 2f, chase 3f, then
   one frame per burst game, newest to oldest), then 10 frames of B9's R9.1 and the B4 page; the run is beat f0-30 (storyboard
   "~1 s", S17 is 1 s).
2. **Reverse playback** does not exist in HyperFrames (playback rate 0.1-10), so the reversal is baked into
   `assets/rewind/b16-rewind.mp4` by `tools/make_rewind.py` (frame selection, cover-fit scaling and the page zoom only; no
   colour or look baked in). The VHS look is a media treatment on the `<video>` (never a CSS filter).
3. **RT1 (VHS overlay) unavailable:** stand-in = media-treatment VHS Playback (tape damage, tracking tears, chroma bleed,
   scanlines, grain) + hand-drawn tracking lines (SVG noise bands, palette white). The registry has no VHS/tracking item
   (searched "VHS tape rewind tracking lines", "vhs overlay", "tracking noise lines", "tape glitch").
4. **RT6 (light leaks) unavailable:** X7 uses the kit's stand-in (registry `organic-light-leak-overlay` layers retinted to warm
   glow #FFF6E0, 14f inside the plan's 12-16f).
5. **The design document "as B4 showed it":** the rewound page carries B4's L7 dim + title spotlight (kit DOM overlay, B4's
   own hole 715,296,488,212), because the bare white page made "you're always running." unreadable (check: contrast 1.45:1);
   with B4's dim it passes, and the rewind shows the shot the viewer saw. The T9 highlight and the other screens' graphics
   (stars, captions, path diagram) are not replayed: the rewind shows the footage.
6. **Captions:** "you're always running." stays until the next chunk (T5 at f53), over the X7 dissolve and 9 frames of black
   (T1 rule "hard cut out on the next chunk"; kit note "ends at 'The' = T5").
7. **Cue `rewind` = 0:** the storyboard writes "rewind = 0..30"; `cues.json` holds one frame per event, so it carries the
   start (S17) and this note carries the end (f30, MU7 resume).
8. **T5 period after the chip:** kept ("...started with a [bug chip]." = the locked script's "bug." with the chip in place of the
   word).
9. **`check` warnings weighed:** `nested_structure_needs_subcomposition` (kit T5 markup, the tracking SVG), `line_unread` on
   "So that's why" (0.47 s: the caption follows the voice, plan rule).

## Pending real footage

- **Re-run the rewind after real footage arrives:** `python3 ../../tools/sync_footage.py . && python3 tools/make_rewind.py`,
  then re-render. The script reads its in-points live from B14's `tesseract_shots.json` (escape 8.0, RT3 1.0, R1.3 2.0,
  burst a 1.0 / b 5.0 today: stand-in values) and from **B9's R9.1 shot** in `../b09-throughyou/tesseract_shots.json`
  (lane E had not written it yet: default source_in 0.0 at B9 f0 used; the map's `inpoints_from` says which was used).
  B4's R4.5 framing is copied by hand from b04-racenchase (page 1.4x, title (878, 307.5) -> (960, 400), push 1.00 -> 1.18
  about (959, 402) over f0-44; dim hole 715,296,488,212): if lane B changes it, update `DOC` in the script and
  `#b16-docdim` / the `docDimZoom` values in index.html.
- Real R9.1 may be 4:3: the script cover-crops every source to 16:9 (never stretches); check the crop keeps the cars.
- **RT1 / RT6:** when the real files exist, wire RT6 into `#b16-x7` as `<video class="clip rc-x7__footage" src="assets/footage/RT6.mp4" muted playsinline ...>`
  (the kit then drives it instead of its layers) and RT1 as a Screen-blend video over the rewind (f-6..30), and consider
  lowering the drawn tracking lines.
- Check the VHS treatment strength on real footage (faces/HUD readable, no blank borders).

Render: `npx --yes hyperframes@0.9.52 render . --format mov --workers 1 -o ../../05_GFX/renders/b16-bug-origin.mov`
