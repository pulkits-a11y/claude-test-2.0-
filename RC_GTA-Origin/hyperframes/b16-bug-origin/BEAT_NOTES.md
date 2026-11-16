# B16 Started with a bug: beat notes (b16-bug-origin)

## v02 (REVISION_v02.md, client notes on v01): what changed

Beat **113f** (was 120), composition **125f**, root `data-duration="4.1666667"`. Frames below are v02 beat frames (local =
beat + 6). Everything after this section is the v01 record (v01 frames, Inter fonts, the bug chip).

| What | v01 | v02 | Why (note / rule) |
|---|---|---|---|
| **"bug"** | the M4 bug chip popped in place of the word (T7) | **the word "bug."** in the T5 line, no chip, no icon | **note 8** |
| T5 glow line | whole line faded in over 12f (linear opacity) from "The" f53 | word by word, max 2 words, one line per group: "The" 51 / "whole series" 55 / "started with" 74 / "a bug." 94 ("bug." 95); each word blurs in (14 -> 0 px easeOutExpo, opacity easeOutCubic, 6f) in the text and both glow copies; the warm leak drifts behind from "The" to the end (kit, sine eases). T5 on screen f51-119 (2.27 s incl. the tail handle, >= 1.5 s) | note 11, rules A, C |
| T1 | "So that's why" / "you're always running." | word by word: "So that's" 1 / "why you're" 12 / "always running." 22 -> out on "The" 51. Grouping note: the kit's split inside the plan chunks gives "why" alone for 2 frames (f12-14); "why" is grouped with the word after it instead (rule A: a short function word goes with the word after it) | note 11, rule A |
| VHS rewind | beat -6..30 (~1 s), 52-frame clip | beat -6..28 (local 0-33; the tape stops on beat 28), 48-frame clip rebuilt by `tools/make_rewind.py` (v02): B14's v02 shots read live (escape from B14's last frame f177, lights f150/142, chase f118/110/102, burst 52/44/28/20/4), then 9 frames of B9's v02 R9.1 shot (f120 -> f56, read live from b09-throughyou), then the design document | re-time |
| Design document zoom-out in the rewind | 118% -> 100% linear (B4's linear push at 8x) | B4's v02 push (b04-racenchase: beat f0-40, 100 -> 118%, easeInOutSine) sampled backwards every 8 frames: 118, 116.3, 111.8, 106.2, 101.7, 100% (local 28-33, eased), held at 100% under X7; the DOM dim (B4's L7 spotlight, same hole) follows with one value per frame | rule C |
| X7 light-leak dissolve | 14f, picture/leak opacity linear | 12f (beat 28-40, local 34-46), picture fades easeInCubic, RT6 leak container sine.out / sine.in (kit v02); black beat 40-51 | rules C, E |
| VHS media treatment on the rewind | VHS Playback recipe incl. grain 0.16 and chromaticAberration 0.18 | grain and chromatic aberration set to 0 with `media-treatment` (the assembly's whole-edit finish adds both; rule F); the tape-specific VHS controls stay (tape damage/tracking/noise/speed, chroma bleed, scanlines, glitch line tear), so the rewind still reads as a VHS tape | rule F |
| Tracking lines, RT1 | to beat 30 | to beat 28 (RT1 second piece local 16-33) | re-time |

`cues.json` = `{"rewind": 0, "rewind_end": 28, "bug": 95}` (`rewind_end` added: the assembly reads it for MU7's end; the v01
`chip` cue is now `bug`, the frame the word "bug." appears, no SFX). No Tesseract shots (fully HyperFrames-owned and opaque).

Checks: `check --json` 0 errors (warnings: nested T5/tracking markup, `line_unread` on "why you're" 10f, "The" 4f and on "a bug."
as "the film's last line"). Snapshots `review/v02/a/` + `sheet_a.jpg`: every rewind section, each caption word, the doc zoom,
X7, black, every T5 word. Render `05_GFX/renders/b16-bug-origin.mov`: ProRes 4444, 1920x1080, 30 fps, **125 frames**, `yuva444p12le` (ffprobe, counted).

Sync: the rewind mirrors B14 v02 (this lane), B9 v02 (R9.1 shot f0-120, in 314.1 s, crop 536:302:260:108, read live) and B4 v02
(push f0-40 eased, `DOC` in `tools/make_rewind.py`, checked against b04-racenchase's v02 index.html). Re-run
`python3 tools/make_rewind.py` and re-render after any change to those shots.

---


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
| B-roll (reused B14) | R14.5 (escape + 2013), R1.6 (police lights, B14's RT3 substitute), R1.3, R14.4, R14.3, R14.2, R14.1 - frames taken from the ORIGINALS with B14's in-points and crops | rewind f-6..12, reversed 8x |
| B-roll (reused B9) | R9.1 GTA 1 police chase = B9's L1 shot (source 318.13 -> 315.73 s, B9's crop 536:302:260:108: the uploader's "Sakura240" watermark cropped out, plan Rule 5), read live from `../b09-throughyou/tesseract_shots.json` | rewind f13-22, reversed 8x |
| B-roll (reused B4) | R4.5 design-document title page (REAL still, `assets/footage/R4.5.png`) | rewind f23-29 (zoom back out), held f30-44 under X7 (0.7 s on screen in all: < 1.5 s, always with camera motion until it stops) |
| Derived clip | `assets/rewind/b16-rewind.mp4` (52 frames) + `b16-rewind.map.json` | built by `tools/make_rewind.py` from the synced footage |
| Textures (REAL) | **RT1** VHS overlay (Screen blend over the rewind, f-6..30) + the media-treatment VHS look + drawn tracking lines; **RT6** light leak inside the kit X7 container (f30-44) | `assets/footage/RT1.mp4`, `RT6.mp4` |
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
| 3..4 | police lights (R1.6, B14's RT3 substitute) reversed | |
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
3. **RT1 (VHS overlay), real:** the pack's transition 4 (VHS noise bands, glitch blocks, a tape-crease streak), Screen blend over
   the rewind f-6..30, on top of the media-treatment VHS Playback look and under the drawn tracking lines (plan: "the VHS overlay
   (RT1) and tracking lines"). Cropped `1632:918:0:0` to drop the pack's burned-in number badge; played in two pieces that skip the
   pack's two full-white flash frames (source 13.53-13.57), which under Screen read as an X3 white flash (seen in review, removed).
4. **RT6 (light leaks), real:** one orange leak burst (rises from black at 4.00 s, peaks 4.20, gone by 4.48 = 14 frames) inside the
   kit's X7 container (`.rc-x7__footage`; the kit drives the container 0 -> 0.9 -> 0, Screen, and adds no drawn layers). The leak's
   own orange is footage colour (the palette rule covers drawn graphics).
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

## Footage used

| R-ID | File (04_Broll/_originals/...) | Source (s) | Beat f | What it shows | Link |
|---|---|---|---|---|---|
| R14.5 | `B14/R14.5__GTA V - Lose The Cops #2 - Cinematic - Short Film [vUndgwBLKeY].mp4` (crop 1636:920:142:78) | 243.03 -> 240.90 (8x reverse) | -6..2 | B14's escape: the getaway car on the beach | https://www.youtube.com/watch?v=vUndgwBLKeY&t=240 |
| R1.6 | `B01/R1.6__The Biggest Police Chase in GTA San Andreas History! (100 Cops vs. 1 S [flgIZbQHwN8].mp4` (crop 1264:711:300:289) | 130.27, 130.00 | 3..4 | B14's police lights (RT3 substitute) | https://www.youtube.com/watch?v=flgIZbQHwN8&t=129 |
| R1.3 | `B01/R1.3__GTA V - ＂5 Stars＂ Police Chase [NcTdBgA3Bkg].mp4` | 109.40, 109.13, 108.87 | 5..7 | B14's GTA 5 chase under the stars | https://www.youtube.com/watch?v=NcTdBgA3Bkg&t=107 |
| R14.5 / R14.4 / R14.3 / R14.2 / R14.1 | B14's burst files, crops as in B14 | 429.73 / 155.27 / 64.13 / 274.07 / 60.43 | 8..12 | one frame per burst game, 2013 -> 2001 | see b14-since BEAT_NOTES |
| R9.1 | `B02/R9.1__GTA 1 Police Chase 001 [HX8infRFBTc].mp4` (crop 536:302:260:108 = B9's L1 crop: x 260-796, y 108-410, excludes the uploader's "Sakura240" watermark at x 100-258, y 352-385, plan Rule 5; was 736:414:59:40, which showed it) | 318.13 -> 315.73 (8x reverse; B9 f127 -> f55) | 13..22 | GTA 1 top-down, B9's chase run backwards: the police car pulls back off the player's purple Beast GTS, which then sits by the kerb | https://www.youtube.com/watch?v=HX8infRFBTc&t=315 |
| R4.5 | `04_Broll/B04/R4.5__design-doc-1995_title-page.png` (real still) | B4's push run back 118% -> 100% | 23..45 | the 1995 Race'n'Chase design-document title page as B4 showed it | (plan p.29 sources) |
| RT1 | `B16/RT1__Retro VHS Transitions Glitch 5-Pack Video Overlays (4K) [QV4F0CygC3U].mp4` (crop 1632:918:0:0) | 13.00-13.50 + 13.60-14.23 | -6..30 | VHS noise bands / glitch / tape crease (Screen) | https://www.youtube.com/watch?v=QV4F0CygC3U&t=13 |
| RT6 | `B16/RT6__FREE Light Leak Transitions Pack - 4K (ULTRA HD) [b-jt77qrRoA].mp4` | 3.98-4.45 | 30..44 | orange light-leak burst (X7) | https://www.youtube.com/watch?v=b-jt77qrRoA&t=3 |

`tools/make_rewind.py` (footage pass): every rewind frame is pulled from the ORIGINAL at the shot's source time with the shot's
crop (the same `source` / `source_in_s` / `crop` the Tesseract assembly uses, read live from `../b14-since/tesseract_shots.json`
and, when it exists, `../b09-throughyou/tesseract_shots.json`), then cover-fitted 16:9; `assets/rewind/b16-rewind.map.json`
lists every output frame's source and `inpoints_from`. Working clips: only R4.5, RT1, RT6 (`footage.json`).

## Substitutions

* None in B16 itself. It reuses B14's `SUBSTITUTE (Rule 5): R1.6 ... for RT3` (see b14-since BEAT_NOTES).

## Still pending

* Resolved: **B9's R9.1 shot** exists (`../b09-throughyou/tesseract_shots.json`, `inpoints_from` names it): the rewind's 10 GTA 1
  frames are B9 f127 -> f55 (source 318.13 -> 315.73 s) with B9's L1 crop. That crop is now 536:302:260:108, which cuts the
  uploader's "Sakura240" watermark out (plan Rule 5: a watermarked clip is unusable); the rewind was rebuilt with
  `python3 tools/make_rewind.py` (only local frames 19-28 changed), re-checked (`check --json` 0 errors; warnings as in
  interpretation 9) and re-rendered (ffprobe prores 1920x1080, 30 fps, 132 frames, yuva444p12le). Snapshots read at
  local 19, 22, 24, 25, 28 (`review/footage-pass/r91-recrop-L19-28.jpg`, `f024_b018_R9.1.png` re-shot): new crop, no
  watermark.
* Re-run `tools/make_rewind.py` and re-render after any change to B9's L1 shot, B14's shots (e.g. if RT3 arrives) or B4's
  R4.5 framing.

Render: `npx --yes hyperframes@0.9.52 render . --format mov --workers 1 -o ../../05_GFX/renders/b16-bug-origin.mov`
