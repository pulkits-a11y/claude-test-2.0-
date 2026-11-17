# B8 The break - `b08-break` (v04 kit; v03 content; timing v02: beat 59f = 1.967 s; composition 71f with 6f handles)

## v05 phase 1 (REVISION_v05.md lane 2; doc 31.0-33.0) - in progress, phase 2 = kit v05 components
* b07's single article shot continued: `#b08-artCam` plays the push curve 49..88 of 88 (118% on "breaks").
* **Dim + blur** (doc 31.0-32.0, "Then, something"): black over the page 0 -> 70% (= the article at 30%) and blur 0 -> 30 px
  on screen (18.5 layout px at the ~1.6x page scale; page image through its media-treatment blur control with a custom ease
  that follows the px curve, DOM layers by CSS), 7 -> 37, easeInOutSine. X4 still rebuilt (`x4_still.sh`).
* `cues.json` v05: reverse_cymbal ending on "breaks." (33) + glitch_stutter 33 + a 4f dropout ending on it, key_words [33];
  legacy breaks / first_black dropped. Stills: `review/v05/sheet_p1.jpg`. check: 0 errors.
* Phase 2: "breaks." hero 450 px with the kit's pink pixel-glitch entry, the Win95 window flashed 2f behind it, the dark
  card v05 (grain + faint footage) instead of flat black, the landed CANNED stamp on the page, the lockup in kit v05 tiers.

## v04 (kit refresh only)
`python3 tools/new_beat.py B8 --refresh` (kit v04): the full-frame black screen behind T10 "breaks." (`.rc-ink.rc-full`,
local 47-71) now carries the kit's static scanlines (REVISION_v04 note 7: scanlines only inside the dark text cards; 9 px
period, measured 8-10 / 255 on the black). Nothing else changed; the X4 still (frame 39, before the black) is unaffected.
Stills: `review/v04/` (pre-tear, first black, clean T10, last hold frame). `check`: 0 errors.

---

## v03 (REVISION_v03.md; client notes 3, 11, 12, 13, 16, 17) - what changed
Only what the notes ask; everything else is v02 (b07's article shot E continued with the same framing and the same eased
push to "breaks", the X4 tear 39-46 (8f, seed 8), the first black on 47, T10 "breaks." (glitch 47-52, clean 53-64), the
silence, 71f).
* **Dark article (notes 3, 12)**: the page is b07's dark-mode capture (re-synced: `python3 tools/sync_footage.py
  hyperframes/b08-break`) with b07's dark-page highlight (both strokes landed, one group, screen 50%) and the same
  spotlight (pure-black 65% dim). b07 f96 vs this f6 (the cut): mean pixel difference 0.07 / 255 above the lockups.
* **X4 still rebuilt** from this composition's new frame 39 (`sh hyperframes/b08-break/x4_still.sh`):
  `assets/x4/b08-old.png` = the dark page, highlight landed, no caption.
* **Camera (note 13)**: nothing to remove (no zoom of its own; the article push is b07's E move, unchanged).
* **Caption (notes 11, 16, 17)**: the v03 lockup `Then, something` (one small line; "Then," on 7, "something" on 25, hard
  cuts, no animation) below the spotlit sentence (ink centre y 840, as b07's last lockup); it leaves at the tear (39).
  T10 "breaks." is unchanged.

`cues.json` unchanged (`breaks` 33, `first_black` 41). Review stills: `review/v03/` (`sheet_v03.jpg`; the cut from B7,
each word, the tear frames, the black + T10). No render (v03). `check`: 0 errors; warnings = nested markup, the 12f
closing word (plan).

(The v02 section below still applies where this v03 section does not change it.)

---

## v02 (REVISION_v02.md) - what changed and why
Re-timed to the v02 beat map (VO 115%: 63f -> 59f, composition 75f -> 71f, root `data-duration` 2.3666667) and the
global rules. Because B7 was redesigned (client note 3), **the X4 break now breaks what B7 ends on**: the Game Developer
article with the highlighted sentence (https://www.gamedeveloper.com/pc/penn-first-i-grand-theft-auto-i-was-almost-canned-),
no longer the stamped card. Kept: T1 "Then, something", the X4 shatter to black, T10 "breaks." (6f glitch, clean 12f hold,
hard cut), the silence.

### 1. What the viewer sees
B7's last shot simply carries on: the article page, dimmed except the highlighted sentence "It was almost canned. The
publisher, BMG Interactive, wanted to can it", still pushing in, while "Then," and "something" pop in word by word. On
"breaks" the page shatters into jumping, colour-split blocks for 8f and cuts to black; "breaks." glitches for 6f,
settles clean and holds 12f, then a hard cut to B9.

### 2. Assets
* R7.GD (the article still, as b07-shutdown; `footage.json` rids `["R7.GD"]`; the v01 R7.1 working copy is no longer used
  and was removed from `assets/footage/`).
* `assets/x4/b08-old.png` = this composition's own frame at local 39 ("breaks") without the tear, re-made with
  `x4_still.sh` (FRAME 39) from the new picture.
* Kit: the same page framing / spotlight / highlighter strokes as b07, `RCK.cam.push` (with the shared curve),
  `X.tear` (X4, still mode, seed 8), `T.glitch` (T10, seed 8), `.rc-ink`, `captionPlanV2` / `captionPops`.
* Audio (Tesseract): S08 on "breaks"; S07 ends on the first black frame; MU4 15f hard mute from it.

### 3. Tool and layer stack (HyperFrames, top -> bottom)
z40 T1 (white, low line y 860, local 7-39) | z30 T10 "breaks." (47-71) | z20 X4 tear canvas (39-46) | z10 ink black
(47-71) | z2 `#b08-driftE` > `#b08-camE` > `#b08-pageE` (page x 50-1450, y 1564-2351.5) > R7.GD + 2 highlighter strokes
(landed) + spotlight dim (local 0-47).

### 4. Step-by-step build (local frames; beat f = local - 6)
1. Camera: b07's article push is ONE easeInOutSine move on the edit clock (b07 local 58 = edit 897 -> this local 39 =
   edit 968; scale 100 -> 118% about the sentence centre + drift (-93.257, -53.029) px). This composition plays its frames
   32..71 (segment of the same curve, not restarted): b07 f96 and this f6 (the cut) are the same picture (measured mean
   pixel difference 0.035 / 255 outside the caption band).
2. T1 "Then, something" (kit captionPlanV2): "Then," pops on 7, "something" on 25; the group ends at the tear (39).
3. X4 on "breaks" (39 = beat 33): **8f** (39-46; v01 10f): the kit default inside the plan's 6-10f, so the plan's "T10
   ... settles clean and holds 12f" still fits the 4f-shorter v02 beat. 16 x 9 blocks jumping +/-30 px, some frozen on
   the old frame, 6 px RGB split, seed 8. Hard cut to black on 47 (beat 41).
4. T10 "breaks." on 47: 6f glitch (47-52, hard per-frame cuts), clean from 53, holds 12f to the hard cut at 65 (beat
   59); the tail handle 65-70 holds the clean word.

### 5. On-screen text
| element | text | local f (beat f) |
|---|---|---|
| T1 | Then, / Then, something (one group, word by word) | 7 (1) / 25 (19), out at 39 (33) |
| T10 (Coolvetica, white, on black) | breaks. | glitch 47-52 (41-46), clean 53-64 (47-58) |

### 6. Audio cues (`cues.json`, beat frames)
`breaks` = 33: S08 (glitch impact + power-down, both start on this frame). `first_black` = 41: S07 riser ends here
(it starts from B7's `stamp2` logic, unchanged); MU4 hard-mutes the music for 15f from here. Nothing else.

### 7. Mistakes to avoid
* The picture before the break must be exactly b07's last state (page framing, highlights, spotlight, the camera
  function); after any change there re-run `sh hyperframes/b08-break/x4_still.sh` so the X4 still matches.
* B8 and B17 are the same break (seed 8, same T10 glitch); note B8's tear is now 8f (see 4.3).
* Glitch only on the bug beats; nothing added to the silence.

### Footage used (v02)
| R-ID | original | window on screen | crop | shows | link |
|---|---|---|---|---|---|
| R7.GD | `04_Broll/B07/R7.GD__gamedeveloper-2011_penn-gta-almost-canned.png` (live screenshot, captured 2026-11-16) | still, local 0-47 | article column (page x 50-1450), sidebar outside the frame | Game Developer, Jan 31 2011: "It was almost canned. The publisher, BMG Interactive, wanted to can it" (highlighted) | https://www.gamedeveloper.com/pc/penn-first-i-grand-theft-auto-i-was-almost-canned- |

### Checks (v02)
* `check`: 0 errors (warnings: nested dim/highlight markup, the 12f closing word under the CLI's 2 s floor: the plan
  sets 12f).
* Headless audit: 0 linear tweens (the camera segments are eased; the X4 counter and the T10 glitch are hard per-frame
  cuts); captions max 2 words, "Then," / "something" first visible on their onset frames; Coolvetica.
* Continuity with b07: b07 f96 vs this f6 (the cut), mean pixel difference 0.035 / 255 above the caption band.
* Render `05_GFX/renders/b08-break.mov`: ffprobe 71 frames (beat 59 + 12), 1920 x 1080, 30 fps, ProRes 4444
  `yuva444p12le`, opaque. Review stills: `review/v02/`.

---

# v01 reference (SUPERSEDED where the v02 section above differs: B8 no longer shows B7's stamped card or R7.1)

## B8 The break - `b08-break` (beat 63f = 2.100 s; composition 75f with 6f handles)

Plan p.23 (B8), p.16 (X4), p.12 (T10), p.36 (MU4). Storyboard B8. CONFLICTS C10, C17. Bug beat (glitch allowed).
Render: `05_GFX/renders/b08-break.mov` (ProRes 4444, opaque; no Tesseract shots).

## 1. What the viewer sees
B7's stamped card simply carries on (same tilted office clip, still panning, three CANCELLED stamps, slow push) under
"Then, something". On "breaks" the whole card shatters into jumping, colour-split blocks for 10f and cuts to black.
On black, "breaks." glitches for 6f, settles clean and holds 12f, then a hard cut to B9. The only fully silent
moment besides the very end (music hard-muted).

## 2. Assets
* R7.1 (continued from B7, continuous source time). Kit: B7's L5 card (same layout, same motion functions), `X.tear`
  (X4, still mode, seed 8), `T.glitch` (T10, seed 8), `.rc-ink`.
* `assets/x4/b08-old.png` = this composition's own frame at local 41 (beat f35) without the tear (made by
  `x4_still.sh`, re-made for the real R7.1).
* Audio (Tesseract): S08 on "breaks"; S07 ends on the first black frame; MU4 15f hard mute.

## 3. Tool and layer stack (HyperFrames, top -> bottom)
z40 T1 (card ink, y 860, local 6-41) · z30 T10 "breaks." (local 51-75) · z20 X4 tear canvas (local 41-50) ·
z10 ink black (local 51-75) · z2 camera > prop > frame + R7.1 + three landed stamps (local 0-51) · z1 gray ground.

## 4. Step-by-step build
1. `footage.json` = B7's R7.1 window; the video plays from media 3.2 s (B7's 0 + 96f) = original 0:06.8.
2. Card motion: push `1 + 0.04 (e - 900) / 131` and float phase `1.6 pi` on the edit clock = B7's functions, so B7's
   last frame and B8's first frame match.
3. Stamps set landed (B7 rotations/offsets).
4. X4 on "breaks" (local 41 = beat f35): 10f tear, 16 x 9 blocks jumping +/-30 px, some frozen on the old frame,
   6 px RGB split; hard cut to black on local 51 (beat f45).
5. T10 "breaks." on local 51: 6f glitch (51-56), clean from 57, holds 12f to the hard cut at local 69 (beat f63);
   tail handle holds the clean word.
6. T1 "Then, something" local 6-41 (out at the tear).

## 5. On-screen text (plan: "T1: Then, something → T10: breaks.")
| element | text | beat f |
|---|---|---|
| T1 | Then, something | 0-35 |
| T10 (Inter Black, white, on black) | breaks. | 45 (glitch to 51), clean 51-63 |

## 6. Audio cues (`cues.json`)
`breaks` = beat f35: S08 (Glitch + Impact + PowerDown 0.5 s, -6 dBFS, all starting on this frame).
`first_black` = beat f45: S07 riser (from B7) ends here; MU4 hard-mutes the music for 15f from here, then un-mutes in
place (C10). Nothing else: do not fill the silence.

## 7. Mistakes to avoid
* The card before the break must be exactly B7's final state (layout, R7.1 time, stamps, push, float); if B7 or the R7.1
  window changes, re-run `sh hyperframes/b08-break/x4_still.sh` so the X4 still matches.
* B8 and B17 are the same break: same X4 settings and seed 8, same T10 glitch (b17-loop uses 6f on "now?").
* Glitch only here, B2, B16, B17 (motif discipline).

## Footage used
| R-ID | original | window (s) on screen | crop | shows | link |
|---|---|---|---|---|---|
| R7.1 | `04_Broll/_originals/B07/R7.1__Early 1990's office workers archival stock footage [HtJSL-bGo_Y].mp4` | 6.8-8.5 (B7's window 3.6-9.2, +3.2 s) | 440:330:110:0 | the office clip continuing its pan right across the open-plan office (watermark band cropped off) | https://www.youtube.com/watch?v=HtJSL-bGo_Y&t=6 |

Substitutions: none.

## Pending / notes
* Nothing pending. check: 0 errors; 1 warning (closing line under the CLI's 2 s floor: the plan sets 12f).
* Render `05_GFX/renders/b08-break.mov`: 75 frames (beat + 12), 1920 x 1080, 30 fps, yuva444p12le (ffprobe, counted).
