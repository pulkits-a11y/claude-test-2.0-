# B10 It's fun - `b10-fun` (v02: beat 54f = 1.800 s; composition 66f with 6f handles)

## v05 (REVISION_v05.md lane 3, doc 41.0). Read this first

Beat 54 f, composition 66 f (root `data-duration="2.2000000"`): unchanged. Everything not listed is v04 / v03 below.

| Change | Doc |
|---|---|
| **"fun." = HERO**: Coolvetica Italic 450 px (`[[fun.]]*`, hero 450; the doc asks 300 px @720) under "And suddenly," / "it's" (Coolvetica Regular 54), kit v05 lockup, centred. And 7, suddenly, 11 and it's 34 appear on their frames; "fun." pops + blurs in from local 41 | doc 41.0, U1, U2 |
| **1-frame white flash + flash-star** on the cut to the explosion (local 41 = beat 35): kit `fx.flash` (`#b10-flash`, local 41 only, z 50, over everything) + `fx.flashStar` (`#b10-star`, 1000 px at (960, 600), 41-46, z 34 behind the hero). They replace the 7-frame X3 flash of v02-v04 | doc 41.0 |
| Head handle follows B9 v05: the strips land on 178 / 180 / 182 on B9's clock (`LAND_B9`), the push is x 1.08 (`PUSH` = b09's), and B9's v05 lockup "They don't [let go.]" is held over local 0-6 | B9 v05 |

**cues.json v05**: events `fun` 35 (the legacy S09 sub drop, same frame), word_pops 1 / 5 / 28, key_words 35, sfx
`impact_boom` 35. `tesseract_shots.json` has `"timing": "v05"` (R10.1 static 100%, frames as written). Its `"enter": "X3"`
is only a label: the picture builder acts on X2 / X8 only.

**Verification (v05)**: `check --json` 0 errors. Warnings: kit lockup nesting, `line_unread` on the 6 f head handle and
the voice-timed words. Snapshots in `review/v05/` (read):
* `sheet_a.jpg`: the head 0 / 5, And 7, suddenly, 11, it's 34, the frame before the cut 40, then 41 (white flash + star 0), 42-46 (the pop and the star), "fun." held 50, 59, and the tail 60.
* `comp/`: the hero + star over the R10.1 source frame.

Local 0 = b09 local 202, pixel-identical. Not rendered.

## v04 (REVISION_v04.md). Read this first

No change asked for B10. Kit refreshed (v04); nothing it changed is used here. B9's glow flashes end 8f after each pop, so
the head handle (= b09 local 202-208) is unchanged. `check --json` 0 errors; `review/v04/sheet_a.jpg` (0, 34, 47).

## v03 (REVISION_v03.md notes 11, 12, 13, 16, 17). Read this first

Change only what the notes ask; everything else is the v02 section below (timing, flash, cues `fun` 35, footage).

| Change | Note |
|---|---|
| **Zooms removed.** R10.1 L1 (`tesseract_shots.json`): framing back to v01's static 100% (v01: "No push on the 20f L1 shot"), keys `[{f:0, scale:100}, {f:19, scale:100, ease:easeInOutSine}]`; v02's 125 -> 101% burst out of the flash and the drift to 102% are gone. B9's strips: the continued held push is v01's x 1.04 (was x 1.06), same curve as b09-throughyou | 13 |
| **Caption lockup** "And suddenly, \| it's [fun.]*" (kit `T.lockups`, ref 1, centred): And 7, suddenly, 11, it's 34 hard-cut in; the starred keyword "fun." pops + blurs in on local 41 = the X3 flash's 100% frame = S09 + the MU5 drop (under the flash, as v02); holds to the beat end (60), hard cut (no exit). `\|` keeps "And suddenly," on one line (the auto balance put "And" alone) | 11, 16, 17 |
| Head handle: B9's last lockup "They don't [let go.]" held (local 0-6), hard cut out on beat f0; v02's exit tween removed | 11 |
| Dark: nothing to change (footage) | 12 |

**Verification (v03)**: `check --json` 0 errors (warnings: kit lockup nesting, `line_unread` on the 6f head handle and
the voice-timed words). Snapshots `review/v03/` (read, `sheet_a.jpg`): head 0/5, the cut 6, every word 7/11/34, the
flash 38-46 with the "fun." pop 41-46, settled 47, 59, tail 60; `comp/*_over-L1.jpg` = after the flash over the R10.1
source frame (look check); `vs_ref.jpg` = next to ref 1. Local 0 / 5 = b09-throughyou local 202 / 207 pixel-identical.
Not rendered.

## v02 (REVISION_v02.md; client notes 10, 11, 12, 14, 15). Read this first

The v01 sections below are kept as reference; where they disagree with this section (frames, eases, fonts), this
section wins.

**What changed and why**
| Change | Client note / rule |
|---|---|
| Re-timed to the v02 beat map (VO 115%): beat 54f (was 57), edit 1196-1250 (39.867-41.667 s); composition 66f, root `data-duration="2.2000000"`. **"fun" = beat f35 = local 41 = edit frame 1231 = 41.040 s** | note 10 |
| T2 "And suddenly, it's fun." word by word, max 2 words (kit `captionPlanV2` style t2, key 1): "And suddenly," (And 7, suddenly, 11) / "it's fun." (it's 34, keyword **fun.** 41: on screen at full opacity on its own frame with the kit's blur punch 30 -> 0 px + 108 -> 100%, 6f expo.out); the last group exits 3f (power2.in) ending on the beat end | note 11, rule A |
| Coolvetica / Coolvetica Italic (keyword) | note 12 |
| Nothing linear: the strips' v01 `ease: 'none'` push is replaced by the second half of B9's single easeInOutSine strip push (same function of the edit frame as b09-throughyou; B9 local 202 / 207 and B10 local 0 / 5 measured pixel-identical); B9's T4 phrases no longer fade linearly (v02 B9 ends on "let go.", whose 3f eased exit is finished here in the head handle); X3 = kit eased flash (ramp easeInQuad, fade easeOutQuad) | note 14, rule C |
| R10.1 L1 (Tesseract) framing keys: bursts out of the flash 125 -> 101% over f0-10 (easeOutExpo; f0 is under 100% white), then 101 -> 102% to the cut (easeInOutSine) | note 15, rule D |

**New frames (beat frames; local = beat + 6)**
| What | beat f | local |
|---|---|---|
| head handle: B9's strips + "let go." finishing its exit | -6..0 | 0..6 |
| "And suddenly," | 1 (suddenly, 5) | 7 (11) |
| "it's fun." | 28 | 34 |
| X3 flash: 0 / 11.1 / 44.4 / **100%** / 64 / 36 / 16 / 4 / 0 % | 32 .. 40 (100% on 35) | 38 .. 46 (100% on 41) |
| **"fun"** = flash 100% = keyword lands = strips end under the white = Tesseract R10.1 starts = S09 + MU5 drop | **35** | **41** |
| "it's fun." exit | 51-54 | 57-60 |
| tail handle: transparent (Tesseract footage only) | 54-60 | 60-66 |

`cues.json`: `{"events": {"fun": 35}}` (S09 Sub Drop starts here, MU5's drop lands here, = the flash's 100% frame).
`tesseract_shots.json`: B10-killfrenzy-L1 `start_f` 35, `end_f` 54 (was 37-57), `framing.keys` as above, grade b10-pop.
`footage.json`: windows unchanged; strip media-starts 76/30, 53/30, 28/30 s (B9 local 202 minus each strip's B9 start).

**Verification (v02)**
* `check --json`: 0 errors. Warnings: `nested_structure_needs_subcomposition` (kit T2 markup), craft `line_unread` on
  the head-handle "let go." and the beat-segment "it's" / "fun." (voice timing).
* Snapshots `review/v02/` (read, `sheet_a.jpg`): head handle 0/3/5 (exit), 6, every word (7, 11, 34, 41), the flash
  38-46, 50, the exit 57/59, 60, 65. Max 2 words on screen; "fun." lands on the flash's 100% frame; Coolvetica Italic.
* Render (v02): `cd hyperframes/b10-fun && npx --yes hyperframes@0.9.52 render . --format mov --workers 2 -o
  ../../05_GFX/renders/b10-fun.mov`: ffprobe prores 4444, 1920x1080, 30 fps, **66 frames** (= 54 + 12), `yuva444p12le`.
  Checked on the render: frame 41 ("fun") pure white and opaque, frame 42 white at alpha 64.5%, frame 50 transparent
  except the T2 "it's fun.".

---

# v01 reference (beat 57f; superseded where the v02 section above says otherwise)


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
