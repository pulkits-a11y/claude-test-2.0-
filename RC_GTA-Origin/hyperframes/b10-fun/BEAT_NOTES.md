# B10 It's fun - `b10-fun` (beat 57f = 1.900 s; composition 69f with 6f handles)

Plan: B10 build p.24, overview p.18, T2 p.11, X3 p.15, L1/L3 p.14, B-roll p.31 (R10.1, R10.2), SFX S09 p.37, music
MU5 p.34, QA "the flash, the sub drop and the music drop on the same frame". Storyboard: STORYBOARD.md B10.
Frames are **beat frames** (f0 = "And"; local frame = beat frame + 6). Words: And@0 suddenly,@5 it's@29 fun.@37.

## 1. What the viewer sees
B9's three strips keep running while their phrases fade and "And suddenly, it's" appears; a white flash blows out
the frame on "fun" and clears onto full-colour GTA 1 kill-frenzy chaos (cars exploding in a chain of fireballs) as
"*fun.*" lands in big serif italic.

## 2. Assets
- B-roll (real, see "Footage used"): **R9.1** (strip 1, GTA 1 ram; SUBSTITUTE for R9.2), **R9.3** (strip 2),
  **R9.5** (strip 3) continuing from b09-throughyou; **R10.1** (L1 kill frenzy, Tesseract). R10.2 (listed in the
  plan's B10 B-roll) not placed: the build step uses R10.1 only (B11 uses R10.2).
- SFX: **S09** Sub Drop (PRISFX > Hits). Music: **MU5** (the drop).
- Fonts: Inter SemiBold 42 (T2 lead-in) + Instrument Serif Italic 140 (T2 keyword "fun."), Inter Medium 44 (T4 out).
- Graphics: X3 white flash (kit), L3 strips (kit). Strip grade: 60% saturation (B9's look, until "fun").

## 3. Tool and layer stack
HF-owned (opaque) local 0-43 (strips); TS+HF from f37: Tesseract L1 R10.1 (`tesseract_shots.json`
B10-killfrenzy-L1) under this composition, transparent except the flash and the T2 pair. Top to bottom:
1. `#b10-x3` X3 flash (z 50), local 41-49
2. `#b10-t2` T2 pair (z 35), local 6-63
3. `#b10-t4` B9's T4 phrases (z 30), local 0-10 (fading out)
4. `#b10-grid` L3 strips (z 2), local 0-43 (ends under the 100% white)

## 4. Step-by-step build (HTML `index.html`, GSAP timeline `window.__timelines["b10-fun"]`)
| beat f | what | values / ease |
|---|---|---|
| -6..37 | strips continue from B9: same windows, media-start 82/30, 58/30, 31/30 s (continuous source time), B9's slow push continued (115% x 1 -> 1.04 at f37) | linear |
| 0-4 | T4 phrases fade out | 4f linear |
| 0 | T2 lead-in "And suddenly, it's" hard cut on "And" (centred pair at y 540) | |
| 35-41 | **X3** white flash centred on "fun": 33% f35, 67% f36, **100% f37**, 80/60/40/20% f38-41, 0 f42 | kit `X.flash`, linear |
| 37 | hard cut under the white: strips end, Tesseract L1 R10.1 starts (full colour +10% sat, full speed) | `data-start` boundary |
| 37-43 | T2 keyword "*fun.*" blur-in | blur 30 -> 0 px, scale 108 -> 100%, 6f power3.out |
| 53-57 | T2 out: the pair fades | 4f linear, gone on f57 |
Handles: head = B9's strips + T4 continued backward; tail (local 63-69) = transparent (Tesseract footage only).

## 5. On-screen text
| text | style | position | beat frames |
|---|---|---|---|
| And suddenly, it's | T2 lead-in, Inter SemiBold 42 white + shadow | centred pair, y 540 | 0 -> 57 |
| *fun.* | T2 keyword, Instrument Serif Italic 140 | baseline-aligned after the lead-in | 37 -> 57 |
| (They ram. / They chase. / They don't let go.) | B9's T4, fading out | strips | -6 -> 4 |
T-style rotation: B9 T1 -> T4, B10 T2, B11 T1: holds.

## 6. Audio cues (`cues.json`)
- `fun` = **f37**: **S09** Sub Drop starts on "fun" (-8 dBFS, trim at 2.5 s with a 20f fade), **MU5** the music drop
  lands on the same frame (+3 dB for 2 s after it), and it is the X3 flash's 100% frame. The flash is silent.

## 7. Mistakes to avoid
- The flash, the sub drop and the music drop on the same frame (f37 = 100% white = S09 = MU5).
- Full colour only from "fun" (the strips stay at B9's 60% until the cut under the white).
- One serif word on screen ("fun."). No push on the 20f L1 shot (not a held shot).
- Keep the strips' source time continuous with b09-throughyou (same footage.json windows, media-start 82/58/31f).

## Footage used
| R-ID | file | in-out (s, original) | what it shows | link |
|---|---|---|---|---|
| R9.1 | `04_Broll/_originals/B02/R9.1__GTA 1 Police Chase 001 [HX8infRFBTc].mp4` | 320.83-322.27 (strip 1, crop 276:414:274:40) | GTA 1: the player escaping after the ram, cops behind, camera pulled out | https://www.youtube.com/watch?v=HX8infRFBTc&t=320 |
| R9.3 | `04_Broll/_originals/B09/R9.3__GTA2 5 Stars Gameplay [LNqEGdO9HDI].mp4` | 57.53-58.97 (strip 2, crop 288:480:247:0) | GTA 2: police cars swarming the player | https://www.youtube.com/watch?v=LNqEGdO9HDI&t=57 |
| R9.5 | `04_Broll/_originals/B09/R9.5__Grand Theft Auto London 1969 Rampage (NO COMMENTARY) [3f0Zmrg9NUk].mp4` | 567.03-568.47 (strip 3, crop 288:480:96:0) | London 1969: the blue van on the pavement after the player | https://www.youtube.com/watch?v=3f0Zmrg9NUk&t=567 |
| R10.1 | `04_Broll/_originals/B10/R10.1__Grand Theft Auto 1 Kill Frenzy⧸Rampages： Vice City chapter 1 (Bent Cop [-3NOxHFcNaM].mp4` | 49.6-50.27 (+ 6f tail to 50.47), crop 640:360:0:0 | GTA 1 kill frenzy: a chain of cars exploding in big fireballs on the road, the player on the pavement, score pop-ups (Tesseract L1, b10-pop) | https://www.youtube.com/watch?v=-3NOxHFcNaM&t=49 |

## Substitutions
- SUBSTITUTE (Rule 5): R9.1 GTA 1 Police Chase 001 [HX8infRFBTc] @ 05:20-05:22 for R9.2 (missing: GTA 1 full game not
  downloaded), continuing B9's strip 1 (see b09-throughyou BEAT_NOTES).

## Interpretations / conflicts
1. **X3 frames**: the kit's `X.flash` (plan: "ramp to 100% over 2f, hold 1f, fade out over 4f") gives 100% on f37
   only; the KIT_transitions table shows a 2-frame 100% hold (C, C+1), the code holds 1 frame as the plan says.
   The code (= plan) is what renders; the kit doc table is out of date (report, not edited: kit is shared).
2. **R10.1 framing**: the 4:3 game picture is cut to 16:9 (top 360 px) so L1 fills the frame (L1 is full frame with
   soft edges); nothing is stretched.
3. SUGGESTION (not built): none.

## Pending / blocking
- Nothing blocking.

## Verification
- `npx --yes hyperframes@0.9.52 check --json`: 0 errors (warnings: caption-lane density, craft on a beat segment).
- Snapshots in `review/` (read): local 0, 6, 8, 20 (strips + T4 fade + lead-in), 41-49 (flash ramp/hold/fade, keyword
  blur-in), 58, 62, 68 (T2 out, tail).
- Render: `cd hyperframes/b10-fun && npx --yes hyperframes@0.9.52 render . --format mov --workers 1 -o
  ../../05_GFX/renders/b10-fun.mov` (ffprobe in the lane report).
