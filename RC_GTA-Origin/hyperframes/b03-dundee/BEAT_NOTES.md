# B3 1995, Dundee - `b03-dundee` (v05: beat 183f = 6.100 s, starts on "It's"; composition 195f with 6f handles. v04: 203f / 215f)

## v05 (REVISION_v05.md "Lane 5" + CLIENT OVERRIDE U1-U3, U7, U11; doc section 3 beat 9 "If the line stays" and section 4 0:12.0-0:17.0; kit v05): read this first; v04 and older below are kept as reference

**Status: complete** (kit v05 components in). Not rendered (the lead renders).

Timing: "Here's how." is cut (cut A, 20f); B3 starts on "It's" (edit f303 as in v04), **v05 local = v04 local - 20**.
Root `data-duration` 6.5000000 (183 + 12 = 195f). Words (local): It's 7, 1995 14, in 37, Dundee, 41, Scotland. 56, DMA 83,
Design, 90, the 115, studio 119, behind 128, Lemmings, 137, starts 155, a 165, new 168, game. 172; beat end 189.

| What changed | Why |
|---|---|
| **The whole beat is HyperFrames** (opaque): `tesseract_shots.json` has no shots (`"timing": "v05"`). The v04 Dundee band (R3.1) is a [DEPTH] shot, the v04 BBC band (R3.7) a kit card insert | [DEPTH] must live in HF (G6); card insert (doc 15.5-17.0) |
| **"It's 1995 in" (0-41), U7**: full-frame 1990s office B-roll (the client's v04 #4), light grade (exposure -0.3, no heavy dim). Angle 1 R3.8 media 8.45 (a staffer at his desk) 0-14 with "It's" (setup, 7); **hard cut on "1995" (14, = v04 11.0)** to angle 2 R3.8 media 14.9 (the developer in black at his CRT, turning to camera) 14-41 | doc beat 9: "cut to a second archival angle at 0:11.00" |
| **[DEPTH] "1995"**: hero `[[1995]]` Coolvetica Italic 420 px, appears on the spoken "1995" (14) with the client's glow flicker (`T.glowFlicker`, 10 steps + 4f settle). Two copies of one lockup plan: plate -> "1995" -> the developer's cut-out (`assets/depth/R3.8_dev_cutout.webm`, `remove-background`) -> "It's" / "in". Box shifted +255 px (ink x ~820-1610, baseline ~643): his head (top ~500-518 from local 20) covers the lower ~45 % of "95", "19" clear (local 14-19 he is still rising into place and covers more) | doc beat 9 [DEPTH]; U1; v04 #3 |
| **[DEPTH] Dundee (41-83)**: one frame of the R3.1 photograph (21.6 s) as the plate, the hill cut-out from a sky colour key of the same frame (`prep/dundee_depth.py`). Push 100 -> 108% (41 -> 83, sine.inOut) on both layers, origin (960, 356) just under the Law's top so the ridge stays put and keeps covering ~1/3 of "nde". "Dundee," (key 190, pops) between plate and cut-out; "Scotland." (setup 54, 56) above | doc 12.0-13.5 |
| **Location tag** (`RCK.fx.locationTag`, from the cut 41): bottom-left (96, 640, 260 x 340), the UK outline (white 3 px) zooms x3 toward the #FF2E7E Dundee pin over 12f (lands 53, before "Scotland." 56); no label ("Scotland." is the caption) | doc 12.0-13.5 |
| **DMA logo (83-115)**: the client's full cut-out (figure + "DMA Design" lettering) pops 140 -> 95 -> 100% over 5f on "DMA" (83). **No pill** | doc 13.5-14.5; U11 (v03 #2) |
| DMA section shots and camera as v04 (re-timed): door plate 83, staffer 90, map 115, Lemmings box 128, Lemmings intro 137; one slow push 100 -> 104% (83 -> 155) | "anything not mentioned stays" |
| **Yellow hand-drawn circle** (`RCK.fx.annotate` circle, inside the DMA camera) round the front walker of the pair as "Lemmings," lands (137, drawn 137-146); `#b03-lemtrack` follows him at his measured walking speed (-10.2 px/f, one hard step per frame) to the cut (155). Lockup lifted to y 500 so the circle clears "Lemmings," | doc 15.0-15.5 |
| **"starts a new game." (155-195)**: the BBC 1996 team shot (R3.7 195.0 s, `R3.7_team.mp4`, crop 1308:980:306:100 = 4:3 below the BBC Archive channel bug: cropped, not blurred) as the **kit card insert** (`RCK.fx.cardInsertHTML`: 1080 x 810, white 15 px border, 3 deg, shadow; background = the same clip at 130 %, blurred 60 px, darkened 50 %); push 100 -> 106% on `#b03-card .fx-card__cam` | doc 15.5-17.0 |
| **Archival look** (`RCK.fx.archivalGrading`: ~2 px aberration + light VHS wobble) on every HF-embedded 1990s / old picture: both office angles + the developer cut-out, the Dundee plate + hill cut-out, door plate, staffer, map, the card's clip (the v04 archival colour stays: temperature +0.06, saturation -0.2, shadows +0.04). Depth edges re-checked at 200 % with it (`review/v05/zoom/`): no halo, no visible misalignment | G7; brief |
| Captions (U2, kit v05 lockups via `prep/gen_captions.cjs`): words appear on their frame, white, setup 54 / key 190; "Dundee," and "Lemmings," pop + blur in (the doc pop); "1995" appears + glow flicker. `cues.json` word_pops / key_words = `T.lockupCues` (+ the logo pop) | U2; G10 |

**Frames (local)**: 0-14 office angle 1, "It's" 7 | 14 cut, "1995" + glow flicker | 37 "in" | 41 cut to Dundee, "Dundee,"
pops, push + location tag start | 53 tag landed | 56 "Scotland." | 83 cut, door plate, logo 140% | 86 95% | 88 100% |
90 staffer | 115 map, "the" | 128 box | 137 Lemmings intro, "Lemmings," pops, circle draws (to 146) and tracks |
155 card insert, "starts" | 165 / 168 / 172 "a" / "new" / "game." | 189 beat end | 195 tail end.

**Known / weighed**:
* "in" (37) is on screen 4f before the cut to Dundee (spoken at 37, the cut is on "Dundee," 41): kept as the tail of
  "It's 1995 in" (craft `line_unread`); it sits on the developer's dark hair.
* craft `line_unread` "last line" on "starts a new game." (a beat segment), `duplicate_media_discovery_risk` (the card and
  its blurred copy), `nested_structure_needs_subcomposition` (lockup markup): by design.
* `cues.json` `archival` is empty on purpose (no Tesseract shots; the HF footage carries the kit's archival grading).

**Assets / recipes** (`assets/depth/` is tracked; `assets/footage/` is git-ignored working copies): `prep/dundee_depth.py`
(-> `assets/depth/R3.1_plate.jpg`, `R3.1_hill_cutout.png`, `R3.1_depth.SOURCE.json`), `assets/depth/R3.8_dev_cutout.webm`
(+ `.SOURCE.txt`), `assets/footage/R3.7_team.mp4` (working copy; re-cut with `prep/R3.7_team.SOURCE.txt`),
`assets/dma/DMA-logo__cutout_full.png` (the client cut-out, as v03/v04), `prep/gen_captions.cjs` (lockups + card insert +
`prep/cues_words.json`; re-run after a kit sync).

**Verification v05**: `check --json` 0 errors. Snapshots `review/v05/a` (0-40), `b` (41-88), `c` (115-194), each with
`sheet.jpg`, and `review/v05/zoom/` (200 %: "1995" over the developer at 30, Dundee at 60), read. Not rendered.

---

# (pre-v05 title) B3 1995, Dundee - `b03-dundee` (v02: beat 203f = 6.767 s; composition 215f with 6f handles. v01: 215f / 227f)

## v04 (REVISION_v04.md, review #4, #3): read this first; v03 and older below are kept as reference

Everything else as v03. Kit refreshed to v04 (`python3 tools/new_beat.py B3 --refresh`, words.json identical; lockup markup unchanged).

| What changed | Why |
|---|---|
| **1990s B-roll behind "It's 1995"** (no blank card any more): R3.8 DMA Design office tour, the wide office with CRT monitors at the desks and two staff (media 14.2 s = source 27.2 s, inside one shot; already in the synced R3.8 window, footage.json note updated), cover-fitted, archival grade as the section's other R3.8 shots + a media-treatment blur control; darkened by an ink overlay (`#b03-yr-dim`: 58 % in the middle to 86 % at the edges). The card has no background and no scanlines (kit `rc-t3--clear rc-noscan`). B-roll, dim and card sit inside the zoom-through wrapper: the zoom-through IN (130 % + 16 px blur -> 100 % sharp, 6-15) now blurs the B-roll through its blur control (`blurMedia`) and the card text through CSS (`blurDom`) | #4, #3 |
| **Glow flicker on "1995"**: `T.glowFlicker(tl, '#b03-t3 .rc-t3__year', L(34), { frames: 11 })`: the digits still roll in from the boundary (6-20, cue `year_digits` unchanged) but dim (the kit's "off" state), and the year catches like a neon tube on the spoken "1995" (34), 11 one-frame steps, settles to the steady glow from 49; "It's" keeps its steady glow | #3 |

**Verification v04**: `check --json` 0 errors (warnings: markup nesting; the known 1.3:1 on "the studio behind" over the Lemmings box
window light; craft "last line"). Snapshots `review/v04/` (0-61: the blurred B-roll in the head handle, the dim year during the roll,
every flicker step, steady, the cut to Dundee; `sheet.jpg`). Not rendered.

---

## v03 (REVISION_v03.md, client notes 1, 2, 11, 12, 13, 16, 17): read this first; v02 and v01 below are kept as reference

Timing, word frames and cues unchanged (beat 203f, composition 215f, local frame = beat frame + 6). Kit refreshed to v03
(`python3 tools/new_beat.py B3 --refresh`: kit only, words.json identical).

| What changed | Why (note) |
|---|---|
| Year card text: **"It's 1995"** (the T3 lead-word slot: `<div class="rc-t3__in">It's</div>`, small italic above-left of the year, like ref 1); the card is the kit's v03 dark card (ink + charcoal lift, white digits with the ref 3 glow). Zoom-through IN kept; card push 100 -> 104 % (sine.inOut, 6 -> 61; was 106 %) | 1, 12, 13 |
| "DMA Design," is NOT spelled out any more: the **DMA Design logo** (your cut-out with transparency, `04_Broll/B03/DMA-logo__cutout_full.png`, copied to `assets/dma/`: figure + "DMA Design" lettering) appears centred over the B-roll (305 x 460 px, downscaled from 456 x 687, ink centred on 960, 540, soft drop shadow 0 4 18 px 55 % so the white lettering reads on the bright office), on "DMA" (103) with the kit's starred-word pop + blur-in (`T.wordPops` on `#b03-logo-pop`: full opacity on 103 at blur 20 px / 92 %, sharp 100 % on 109, expo.out; no zoom, outside the camera), held through "Design," to the hard cut on "the" (135). The v02 kinetic "DMA / Design," type is deleted | 2 |
| DMA section camera: the v02 punch-ins on the cuts (103, 110, 135, 157) and the per-shot pushes (incl. the accelerating 100 -> 120 % on the Lemmings box) are deleted; the cuts stay; only v01's one slow push across the section, 100 -> 104 % (sine.inOut, 103 -> 175) | 13 |
| Captions -> v03 lockups (kit), centred (960, 540): `[Dundee,] Scotland.` (61-103, over the Tesseract Dundee band, on the town below the Law; the monument stays clear) / `the studio behind [Lemmings,]` (135-175, over the map / box / Lemmings intro) / `starts a [new game.]` (175-215, over the Tesseract BBC band, through the tail). Words appear on their spoken frames (hard cuts); no starred word (the logo is the beat's one pop + blur-in). The v02 T4 pair, the kinetic-type layouts (`.b03-kt` / `.b03-kw` CSS) and the T1 groups are deleted | 11, 16, 17 |
| `tesseract_shots.json`: framing back to v01, eased: both L2 bands `keys [{f: 0, scale: 100}, {f: <end>, scale: 104, ease: easeInOutSine}]` (Dundee band f42, was 107 %; BBC band f34, was a 112 -> 100 % punch-in + push); X2 drift and letterbox unchanged; notes updated | 13 |

**v03 frames** (local): 0-6 card at 130 % + blur | 6 boundary, zoom-through in, digits roll 6/8/10/12 | 15 landed | 20 "It's
1995" complete | 61 cut (Tesseract Dundee band), "Dundee," (big) | 76 "Scotland." | 103 cut to the door plate, logo pops |
109 logo sharp | 110 cut to the staffer | 135 cut to the map, "the" | 139 "studio" | 148 cut to the box, "behind" | 157 cut to
the Lemmings intro, "Lemmings," (big) | 175 cut (Tesseract BBC band), "starts" | 185 "a" | 188 / 192 "new game." (big) |
209 beat end | 215 tail end.

Known: over the Lemmings box shot (148-156) the small "the studio behind" sits on the bright window light (check: contrast
1.3:1, 9 frames); it stays readable through the kit glow's dark shadow (`review/v03/f148_behind-box.png`); moving the lockup
would cover the walking lemmings in the next shot, so it stays centred.

**Verification v03**: `check --json` 0 errors (warnings: `nested_structure_needs_subcomposition` = kit T3 / lockup markup; contrast 1.3-1.4:1 on "the studio behind" over the Lemmings box's window light (148-156, see Known above); craft `line_unread` "film's last line" on a beat segment). Snapshots `review/v03/` (27 frames + `sheet.jpg`; `vs_ref.jpg` = ref 3 / ref 2 / ref 1 next to the dark year card, the logo and a lockup), read: "It's 1995" on the dark card, the logo centred with its lettering readable (pop 103, sharp 109, gone on 135), no punch-ins on the cuts, lockup words on their frames, transparent where Tesseract owns the picture (61-102, 175-214). Not rendered.

---

## v02 (REVISION_v02.md, client notes 1, 2, 10-15): read this first; the v01 notes below are kept as reference

**Beat 203f (6.767 s, v01 215f), composition 215f = 7.1666667 s** (root `data-duration`), local frame = beat frame + 6.
v02 words (local): Here's 7, how. 14, It's 27, 1995 34, in 57, Dundee, 61, Scotland. 76, DMA 103, Design, 110, the 135,
studio 139, behind 148, Lemmings, 157, starts 175, a 185, new 188, game. 192 (`tools/new_beat.py B3 --refresh`).

### What changed and why

| What changed | Why (note / rule) |
|---|---|
| All frames re-timed (table below); root 7.5666667 -> 7.1666667 | note 10 |
| **No "Here's how." caption** (v01 T1 on the card) | note 1, rule B |
| **X5 blinds open removed**; the year card arrives with the kit's **zoom-through IN** (`RCK.cam.zoomThroughIn` on the untimed wrapper `#b03-zt`): 130 % + 16 px blur on the boundary (local 6; the head handle holds it), settling to 100 % sharp over 9f, easeOutExpo (CSS blur on the wrapper: it holds no footage). B2 plays the out half | note 1, KIT_transitions v02 |
| T3 digits roll **from the boundary** (local 6, 8, 10, 12, 8f power3.out, land 20) instead of on the spoken "1995" (v01 beat f29): the year rolls in while the zoom settles and holds 41f (1.37 s) before "Dundee," (plan: hold >= 1 s; rolling on "1995" would hold only 13f); "In" is part of the card from the start (v01: hard cut on "It's"). S04 moves with the roll: `year_digits` = beat 0 | notes 1 + 10, KIT_transitions v02 recommendation |
| T3 push 100 -> 104 % linear -> **100 -> 106 %** easeInOutSine (local 6 -> 61) | notes 14 + 15 |
| T4 "Dundee," / "Scotland." = **one group of two pieces** (max 2 words), each word pops on its own onset (61, 76; 5f expo.out, 12 px rise); exits in 3f (power2.in) ending on the cut (103) instead of v01's 4f linear fade | notes 11 + 14, rule A |
| **"DMA Design, the studio behind Lemmings," REDESIGNED** (local 103-175): v01's L12 photo cards, T8 "DMA Design" card + role line and the walking Lemming cut-out are removed; now **full-frame B-roll in fast cuts on the words with punch-ins** and **kinetic typography in three layouts, each word popping on its own onset** (details below) | note 2 |
| T1 "starts a new game." -> **starts / a / new game.** (175, 185, 188/192), white over Tesseract's BBC band, through the tail | note 11, rule A |
| Coolvetica; Coolvetica Italic for "DMA Design," and "Lemmings," | notes 2 + 12 |
| Tesseract shots re-timed (`start_f`/`end_f` beat-relative) with v2 `framing.keys`: Dundee band push 100 -> 107 % (easeInOutSine); BBC band punch-in 112 -> 100 % (9f easeOutExpo) then push -> 104 % (easeInOutSine). Notes ask the assembly to ease the 8f letterbox slide-in (rule C) | notes 14 + 15, REVISION "Tesseract shot framing v2" |
| No grain/vignette/chroma in the beat: the HF footage keeps v01's archival grade (temperature +0.06, saturation -0.2, shadows +0.04) without its vignette 0.12 / grain 0.1 | rule F (the assembly adds them) |

### The DMA section (local 103-175, HF-owned, opaque)

| local (beat) | shot (camera `#b03-dma-cam`, one move at a time) | kinetic type (`#b03-kt-1..3`, groups from `captionPlanV2`) |
|---|---|---|
| 103-110 (97-104) | R3.8 13.4 s: the door plate **"21 DMA Design"** on the black door (handheld; object-position 50 % 80 % lifts the plate above the type); punch-in 122 -> 104 % over 7f (expo.out) | "DMA" (103): Coolvetica Italic 300 px, bottom-left (x 96, baseline 830), **slams** in from 140 % + 14 px blur (6f expo.out, scaling from its left edge) |
| 110-135 (104-129) | R3.8 43.35 s: a young staffer at his desk sweeps his hand to his two CRT monitors and turns to the camera (v01 card-1 moment); punch-in 116 -> 100 % (9f expo.out), then push 100 -> 105 % (119-135, sine.inOut) | "Design," (110): Italic 160 px, staggered under "DMA" (x 330, baseline 979), same slam |
| 135-148 (129-142) | R3.7 51.9 s: BBC 1996, the printed GTA 1 city map on a DMA desk, the presenter's hand on it (v01 card-2 moment); punch-in 118 -> 100 % (12f expo.out) | "the" (135) 100 px + "studio" (139) 260 px, Coolvetica Regular, a centred baseline pair (baseline 700); each **rises** 50 px from 90 % (5f expo.out) |
| 148-157 (142-151) | R3.3 572.3 s: the Lemmings box (v01 card-3 moment); push 100 -> 120 % **accelerating into the cut** (power3.in = easeInQuart) | "behind" (148): Regular 110 px, top-left (x 104, baseline 230), **pops** from 30 % with an overshoot (7f back.out(1.7) = easeOutBack, from its left edge) |
| 157-175 (151-169) | R3.6 16.0 s: the Lemmings Amiga intro, lemmings walking on the grass while one floats down under its umbrella (full frame, crop removes the upload's side borders); punch-in 120 -> 100 % (10f expo.out), then push 100 -> 104 % (167-175) | "Lemmings," (157): Italic 240 px under "behind" (x 96, baseline 470, clear of the floater), same overshoot pop |

Never more than 2 words on screen (each group hard-cuts with the picture cut where the next group starts; the T4 group
exits before 103; "starts" takes over at 175). White type with the kit's soft shadow plus a wider soft shadow
(0 8px 48px, 45 % black) scaled to the 100-300 px sizes: still no outline and no box. All type inside title-safe
(left-aligned words scale from their left edge so the slam / overshoot never cross x 96).

### v02 frames (local; beat = local - 6)

| local | beat | what |
|---|---|---|
| 0-6 | -6-0 | head handle: the year card at 130 % + 16 px blur ("In" visible, digits hidden) |
| 6 | 0 | boundary: zoom-through in starts; digits roll 6/8/10/12 (S04 `year_digits` = 0); card push starts |
| 15 / 20 | 9 / 14 | zoom landed (100 %, sharp) / last digit landed |
| 61 | 55 | hard cut on "Dundee," -> TRANSPARENT (Tesseract B3-dundee-band, `start_f` 55); T4 "Dundee," pops |
| 76 | 70 | "Scotland." pops |
| 100-103 | 94-97 | T4 exit (3f, power2.in); band `end_f` 97 |
| 103-175 | 97-169 | DMA section (above) |
| 175 | 169 | hard cut on "starts" -> TRANSPARENT (Tesseract B3-bbc-team-band, `start_f` 169); "starts" pops |
| 185 / 188 / 192 | 179 / 182 / 186 | "a" / "new" / "game." |
| 209 | 203 | beat end (band `end_f` 203); "new game." continues through the tail handle (209-215) |

`cues.json`: `year_digits` 0 (v01 29). `tesseract_shots.json`: B3-dundee-band 55-97, B3-bbc-team-band 169-203 (v01 58-103,
180-215), both with v2 framing keys.

### Footage v02 (`footage.json`, `python3 tools/sync_footage.py hyperframes/b03-dundee`)

| R-ID | window (s, original) | used | link |
|---|---|---|---|
| R3.8 | 13.0-45.9 (one window, two shots; 384 x 288 4:3, cut to 1440 x 1080, upscaled: soft archive) | 13.4-13.63 door plate (shot 1), 43.35-44.18 staffer at his desk (shot 2) | https://www.youtube.com/watch?v=f14k2j9V33Q&t=13 |
| R3.7 | 51.3-54.0, crop 1440:1080:240:0 (4:3 picture) | 51.9-52.33 the GTA 1 city map (shot 3) | https://www.youtube.com/watch?v=7vWSi44ZTSw&t=51 |
| R3.3 | 572.0-574.7 | 572.3-572.6 the Lemmings box (shot 4) | https://www.youtube.com/watch?v=Ev7FqNa5rD0&t=572 |
| R3.6 | 15.4-17.8, crop 1160:720:59:0 (side borders removed) | 16.0-16.6 lemmings walking + a floater (shot 5) | https://www.youtube.com/watch?v=xSKod9Xmrgo&t=15 |
| R3.1 | unchanged (Tesseract band; reference copy only) | | |

All five are cover-fitted to the frame (cropped, never stretched). The R3.6 moment changed (v01 23.2 s was the source of
the cut-out lemming, which is gone with the T8 card; `assets/lemming/R3.6_lemming.webm` is no longer used).

### Conflicts / interpretations (v02)

1. **Plan B3 build (T8 "DMA Design" + role line "THE STUDIO BEHIND LEMMINGS", L12 tilted cards, the tiny Lemming on the
   underline) vs note 2**: the note wins (REVISION R5): the card, the role line and the cut-out are gone; the spoken words
   are the type, word by word.
2. **Plan "keep 4:3 archive inside the band or the cards" vs note 2 "focus more on the broll"** (full frame): the 4:3
   archive is cropped to 16:9 by a cover fit, never stretched (R3.8 is a 384 x 288 VHS source, so it is soft at full
   frame; the assembly's grain sits on top).
3. **Plan "X5 ... into the T3 year card. Hold it at least 1 s"**: X5 replaced (note 1); the card holds 46f after the
   zoom lands and 41f after the last digit lands.
4. **"In 1995" before the spoken "1995"**: the card (a designed card, not a running caption, rule A) arrives at the
   boundary, so the year shows while "Here's how. It's" is spoken (no "Here's how." caption any more).
5. **Wider soft shadow on the giant type** (kit: 0 2px 12px at 45 %, sized for 46 px captions): the kit shadow is kept and a
   proportional soft shadow is added so white words stay readable over the bright 1990s offices; no outline, no box.
6. The kinetic type is a custom layout, but its timing is the kit's (`captionPlanV2` groups, `captionPops` word pops with
   one preset per group, 1f lead): every word is first visible on its onset frame.

### Verification v02
`check --json` 0 errors (warnings: `nested_structure_needs_subcomposition` kit T3 markup; craft `line_unread` on the
voice-timed 1-word groups "studio", "starts", "a" and the "last line"; layout infos = the T3 digit masks by design).
Snapshots `review/v02/` (36 frames + 3 sheets: the zoom-through in, the roll, the push, T4 words and exit, every cut,
punch-in and word pop of the DMA section, "starts / a / new game.", beat end, tail) read: max 2 words on every frame,
words on their onsets, Coolvetica / Coolvetica Italic, nothing linear, nothing cut off; transparent where Tesseract owns
the picture. Render: `05_GFX/renders/b03-dundee.mov` = prores (4444), 1920x1080, 30 fps, **215 frames** (203 + 12),
yuva444p12le; alpha checked on decoded frames: opaque on the HF sections (card, DMA section), transparent apart from the
caption words on the Tesseract sections (local 61-102, 175-214); decoded frames match the snapshots (mean diff < 1.7/255).

---

Plan: B3 build p.21, overview p.18, T3/T4/T8 p.11-13, L2/L12 p.14-15, X5/X2 p.16, M6 p.18, B-roll p.29, SFX S04 p.36.
Storyboard: STORYBOARD.md B3. Frames are **beat frames** (f0 = "Here's"; composition local frame = beat frame + 6).
Words: Here's@1 how.@8 It's@22 1995@29 in@54 Dundee,@58 Scotland.@74 DMA@103 Design,@111 the@137 studio@142
behind@151 Lemmings,@160 starts@180 a@190 new@193 game.@197.

## 1. What the viewer sees
Black blinds swing open onto a gray year card that reads "Here's how.", then "*In* 1995" with the digits rolling up;
a letterboxed archive view of old Dundee (the Law hill under a storm sky) with "Dundee," on the left and "Scotland."
on the right; a hard cut to a gray card where three tilted archive clips of the DMA Design office drop in, with the
name "*DMA Design*" and the role line "THE STUDIO BEHIND LEMMINGS" below and a tiny Lemming walking along the name's
underline; then the 1996 BBC footage of the team at their computers in the letterbox band with "starts a new game."

## 2. Assets
- B-roll (real footage, see "Footage used"): **R3.1** (L2 Dundee band, Tesseract), **R3.8**, **R3.7**, **R3.3** (L12
  cards 1-3, HF), **R3.6** (the walking Lemming, HF; SUBSTITUTE for R3.5), **R3.7** (L2 BBC band, Tesseract).
  Not used: R3.2 (the plan's alternative to R3.1), R3.4 (listed, no step uses it), R3.5 (missing).
- SFX: **S04** (Countdown, List, Numbers (2), Botanica > Countdown & List). No music event in this beat.
- Fonts: Inter Medium 46 (T1), Inter Black (T3 digits) + Instrument Serif Italic (T3 *In*), Inter Medium 44 (T4),
  Instrument Serif Italic 72 (T8 name, kit: names italic) + Inter Medium 22 tracked +15% (T8 role).
- Graphics: X5 slats, T3 year card (M6), L12 cards (kit `RCK.screens`), T8 underline. Cut-out:
  `assets/lemming/R3.6_lemming.webm` (VP9 with alpha, 240 x 270, 81 frames).
- Grades: L12 cards = archival (media treatment: temperature +0.06, saturation -0.2, shadows +0.04, vignette 0.12,
  grain 0.1); the two L2 bands = Tesseract `archival`.

## 3. Tool and layer stack
TS+HF: Tesseract owns the two L2 footage segments (`tesseract_shots.json`: B3-dundee-band f58-103, B3-bbc-team-band
f180-215); this composition is transparent there except the text. HF owns everything else (opaque). Top to bottom:
1. `#b03-x5` X5 slats (z 60), local 0-15
2. `#b03-cap-1` "Here's how." (card ink) / `#b03-cap-2` "starts a new game." (white) T1 (z 40)
3. `#b03-t4` T4 spread words (z 20), local 64-109
4. `#b03-lem-walk` the Lemming cut-out (z 6), `#b03-t8` T8 name card (z 5), `#b03-cards` L12 cards (z 3),
   `#b03-l12-ground` #E9E9E9 (z 2), local 109-186
5. `#b03-t3` T3 year card on #E9E9E9 (z 1), local 0-64

## 4. Step-by-step build (HTML `index.html`, GSAP timeline `window.__timelines["b03-dundee"]`)
| beat f | what | values / ease |
|---|---|---|
| -6..0 | head handle: slats shut (ink black) over the year card | X5 in half |
| 0-8 | **X5 OPEN** (in half; B2 closed them over its last 8f) | 12 slats rotationY 0 -> 90, linear, gone on f8 |
| 1 / 22 | T1 "Here's how." hard cut (card ink #111111) / out when "In" appears | caption plan |
| 22 | T3 small *In* hard cut on "It's" | |
| 29 | **digits roll** on "1995": each digit rises 40 px from its mask, 8f, 2f stagger (f29, 31, 33, 35), last lands f43 | ease out; S04 starts here (`year_digits` = 29) |
| -6..58 | slow push on the card content | 100 -> 104%, linear |
| 58 | hard cut out of the card on "Dundee," -> Tesseract L2 band (X2: bars 138 px slide in 8f, clip drifts 60 px R->L over 20f) | composition transparent from local 64 |
| 58 / 74 | T4 "Dundee," (left, x 96) / "Scotland." (right, to x 1824), both at y 280 (in the dark sky either side of the Law) | 4f fade + 12 px drift up, power3.out |
| 99-103 | both T4 words fade out together | 4f linear |
| 103 | **hard cut on "DMA"** to L12 on #E9E9E9: cards drop in 8f each at f103 / 111 / 119 (rotations -6 / +3 / -2 deg), slow parallax drift, held stack pushes 100 -> 104% | ease out |
| 103 | T8 name "*DMA Design*" + underline fade in | 6f linear |
| 137 | T8 role "THE STUDIO BEHIND LEMMINGS" fades to 60% on "the studio" | 6f linear |
| 103-180 | the Lemming walks the underline right -> left at its own source speed (1.83 px/frame at 20%: x 1076 -> 935), fades in over 6f | linear |
| 180 | hard cut on "starts" -> Tesseract L2 BBC band; T1 "starts a new game." white at y 620 | composition transparent from local 186 |
Handles: head = slats shut over the card; tail (local 221-227) = transparent + T1 "starts a new game." continued.

## 5. On-screen text (locked-script words; plan's chunks)
| text | style | position | beat frames |
|---|---|---|---|
| Here's how. | T1 on the card (#111111) | centred, y 620 | 1 -> 22 |
| *In* 1995 | T3 year card | centred | 22 (*In*) / 29 (digits) -> 58 |
| Dundee, / Scotland. | T4 | left x 96 / right to x 1824, y 280 | 58 / 74 -> fade 99-103 |
| *DMA Design* + THE STUDIO BEHIND LEMMINGS | T8 (#111111 on the card) | centred, block at y 800 | 103 (name) / 137 (role) -> 180 |
| starts a new game. | T1 white (in the band) | centred, y 620 | 180 -> end (+ tail) |

## 6. Audio cues (`cues.json`)
- **S04** Countdown/List/Numbers (2), 0.47 s, starts on the first digit's move: `year_digits` = **f29**. -16 dBFS.
- No music event (MU2 breakdown sits in B2). Voice only otherwise.

## 7. Mistakes to avoid
- Stretch nothing: 4:3 archive stays 4:3 (L12 cards are 4:3 pictures; the BBC band is `contain` in the band with ink
  pillars; the Dundee crop is a true 16:9 cut of the picture, not a stretch).
- Hold the year card at least 1 s (it holds 58f).
- T4 words in empty space either side of the subject (the Law and its monument are centred; the words sit in the sky).
- One serif word per screen except the T8 card (CONFLICTS C4). T-style rotation: T3 -> T4 -> T8, T1 neutral.
- Don't reuse the band moment for a card (R3.7 card 2 = the city map at 51.3 s; band = the team at 194-201 s; B2's CRT
  plate = 60.4 s).

## Footage used
| R-ID | file | in-out (s, original) | what it shows | link |
|---|---|---|---|---|
| R3.1 | `04_Broll/_originals/B03/R3.1__Old Dundee In Colour [n7QORDefzIE].mp4` | 21.6-23.1 (+ handles; window 21.0-24.0) | "La Hull from Hawkhill" slide: the Law hill with its monument centred against a dark storm sky, town below. Crop 640:360:40:0 (removes the burned-in slide caption and the sides). Tesseract L2 | https://www.youtube.com/watch?v=n7QORDefzIE&t=21 |
| R3.8 | `04_Broll/_originals/B03/R3.8__DMA Design Office Tour [f14k2j9V33Q].mp4` | 43.2-45.8 | DMA office tour (Mike Dailly): a staffer at his desk with two monitors turns to the camera. Card 1 | https://www.youtube.com/watch?v=f14k2j9V33Q&t=43 |
| R3.7 | `04_Broll/_originals/B03/R3.7__GRAND THEFT AUTO 1996 Making Of ... BBC Archive [7vWSi44ZTSw].mp4` | 51.3-53.9 | the printed GTA 1 city map on a desk in the DMA office, the presenter's hand on it (crop 1440:1080:240:0 = 4:3 picture). Card 2 | https://www.youtube.com/watch?v=7vWSi44ZTSw&t=51 |
| R3.3 | `04_Broll/_originals/B03/R3.3__The History of Grand Theft Auto, Lemmings & DMA Design [Ev7FqNa5rD0].mp4` | 572.0-574.6 | /noclip: a Lemmings box (Psygnosis) on a table. Card 3 (object-position 100% to keep the box in the 4:3 card) | https://www.youtube.com/watch?v=Ev7FqNa5rD0&t=572 |
| R3.6 | `04_Broll/_originals/B03/R3.6__Lemmings (Amiga intro) [xSKod9Xmrgo].mp4` | 23.33-25.87 | one lemming walking left along a flat ledge; tracked 240 x 270 crop, matted (the Lemming cut-out) | https://www.youtube.com/watch?v=xSKod9Xmrgo&t=23 |
| R3.7 | same file as card 2 | 195.0-196.4 (+ tail handle) | wide shot of the open-plan DMA office: two developers at their CRT computers, the BBC presenter seated between them (crop 1440:1080:240:0, 4:3 in the band). Tesseract L2 | https://www.youtube.com/watch?v=7vWSi44ZTSw&t=195 |

## Substitutions
- SUBSTITUTE (Rule 5): R3.6 Lemmings (Amiga intro) [xSKod9Xmrgo] @ 00:23-00:26 for R3.5 (missing: Lemmings PC
  gameplay was not downloaded; the plan itself allows "cropped from R3.5 or R3.6", so this is the plan's alternative).
- The tiny Lemming cut-out: `npx hyperframes remove-background` (u2net) returned an empty matte on the pixel-art
  sprite (alpha mean 0.15/255), so the matte was made by differencing each frame of the static shot against a clean
  background plate (per-zone median of frames where no lemming covers the zone), largest component, 0.8 px feather.
  Same pixels as the source, no redraw.

## Interpretations / conflicts
1. **T4 height** (plan: "placed in empty space on either side of the subject"): y 280 instead of the kit's 540, so
   both words sit in the dark sky left and right of the Law's monument (lower down the town fills the frame).
2. **Dundee moment**: R3.1 is a slideshow of colour photographs (one slow push per slide), not moving footage; the
   chosen slide is the one with the clearest empty space either side of a centred subject. Its burned-in caption is
   cropped off; the crop is a 3x upscale (soft, reads as archive).
3. **R3.7 twice**: card 2 (the city map) and the band (the team at their computers) are different moments, as the
   plan wants both from R3.7. B2 also uses an R3.7 moment as its CRT plate (see b02-bug BEAT_NOTES).
4. **Lemming direction**: it walks right -> left along the underline, the direction it walks in the source, at its
   own speed (so the feet don't skate). Plan: "walks along the underline" (no direction).
5. **T8 name italic**: kit change (Style kit: Instrument Serif Italic for quotes and names); the underline span was
   re-measured for the italic face (303.12 px, x 808.44-1111.56).
6. SUGGESTION (not built): none.

## L2 band geometry (assembly change, Tesseract side)
- A narrow (4:3) L2 source is now placed at FULL height, pillarboxed 1440x1080 (never stretched), and the 138 px L2
  bars slide in over its top and bottom, leaving a 1440x804 picture inside the band (before: fitted to the band
  height, 1072x804, so the bars slid over black). Checked for the R3.7 BBC band (4:3): the two developers at their
  computers and the presenter sit in rows ~20-80% of the picture, inside the visible middle 804 rows (12.8-87.2%);
  only ceiling lights (top) and chair legs/feet (bottom) go under the bars. The R3.1 Dundee crop is 16:9, so it
  fills the band width (cover) and the bars cover its top/bottom 138 px: the Law's monument and the sky either side
  (where the T4 words sit at y 280) stay inside the band (checked). No HyperFrames change needed.

## Pending / blocking
- Nothing blocking. If R3.5 (Lemmings PC) is uploaded later, the R3.6 cut-out can stay (plan allows either).
- Tesseract: the L2 band shots use `source`/`source_in_s`/`crop` in `tesseract_shots.json`.

## Verification
- `npx --yes hyperframes@0.9.52 check --json`: 0 errors. Warnings weighed: `nested_structure_needs_subcomposition`
  (kit T3/T8 markup), `contrast_aa_failure` 1.05:1 (the transparent segments are measured against the empty page; the
  text sits on Tesseract footage there), craft warnings (beat segment).
- Snapshots in `review/` (read): slats opening, year card mid-roll, T4 pair over the (transparent) band, card drops,
  T8 name/role; `review/zoom/` the Lemming on the underline at local 129 and 165.
- Render: `cd hyperframes/b03-dundee && npx --yes hyperframes@0.9.52 render . --format mov --workers 1 -o
  ../../05_GFX/renders/b03-dundee.mov` (ffprobe in the lane report).
