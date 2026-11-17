# B7 Shut it down - `b07-shutdown` (v03; v02 redesign; beat 90f = 3.000 s; composition 102f with 6f handles)

## v05 phase 1 (REVISION_v05.md lane 2; doc 28.0-31.0) - in progress, phase 2 = kit v05 components
* **The article is ONE shot** from the cut on "keep" (41) to b08's "breaks" (b08 39 = this 129, 88f): one page element
  (`#b07-page`) under `#b07-artCam`. Push 100 -> 118% about the frame centre, easeInOutSine (doc 29.5), shared with b08.
* **Whip-pan** to the body copy (doc ~30.0): 57 -> 61, easeInOutQuart, from the headline framing (page x 23.5-1723.5,
  y 0-956) to the article column (x 50-1450, y 1564-2351.5); motion blur as per-frame values 0 / 9 / 21 / 9 / 0 layout px
  (page image via its media-treatment blur control, DOM layers by CSS). Spotlight hole: headline until 59, then the
  sentence. b07 f96 = b08 f6 (mean difference 0.2 / 255, sub-pixel text rendering inside the highlight).
* **Sweeps** (timing final, look = yellow T9 placeholders until the kit's pink sweep): the headline "First Grand Theft Auto
  Was 'Almost Canned'" on 49 (doc 29.6), "It was almost canned." on 61 (doc ~30.0), "The publisher, BMG Interactive,
  wanted to can it" on 82 (after the stamp: the event before b08's "Then," 97).
* A-C (office): one slow push 100 -> 104% over 0-41 (the A-D push is gone with D).
* `cues.json` v05: whip 51 (the whip-pan's first frame), stamp_thud 66 ("down." = local 72, the stamp, doc 30.3),
  key_words [16 above, 56 shut], archival [[0, 35]] (the office B-roll); legacy stamp1-3 dropped.
  Stills: `review/v05/sheet_p1.jpg`. check: 0 errors.
* Phase 2: card insert for the office shots (doc 28.0), yellow annotation arrow on "above" (22), the pink sweeps, the
  CANNED rubber stamp on "down." (72, -12 deg, ~45% width, 1-f flash, 6 px shake), the lockups in kit v05 tiers.

## v04 (kit refresh only)
Kit refreshed to v04 (`python3 tools/new_beat.py B7 --refresh`); no element of this beat uses the new scanline surfaces:
sample frames are pixel-identical to the v03 stills (mean difference 0.000). `check`: 0 errors. Everything below is current.

---

## v03 (REVISION_v03.md; client notes 3, 11, 12, 13, 16, 17) - what changed
Only what the notes ask; everything else is v02 (the same five shots and cuts, the article headline / sentence framings,
the spotlight, both highlighter swipes landing on "shut" and "down.", the E push shared with b08-break, 102f).
* **No red (note 3)**: the three siren-red multiply layers and their flashes are removed; no red tint anywhere. The S06
  hit sounds stay where they were: `cues.json` unchanged, `stamp1` = 35 (the cut to the headline on "keep"), `stamp2` =
  56 (swipe 1 lands on "shut"), `stamp3` = 66 (swipe 2 lands on "down.").
* **Dark article (note 12)**: `04_Broll/B07/R7.GD__…png` is now the browser's dark-mode capture (same layout, same rects
  in the .json); re-synced with `python3 tools/sync_footage.py hyperframes/b07-shutdown`. The paper behind the headline
  crop is the page's own black. Highlighter = the kit's v03 dark-page T9 (#FFE14D, screen blend, 50%): the black under the
  line becomes a muted yellow band, the light text brightens to near white on it; the two strokes are opaque inside one
  group that blends once (`.b07-hlgroup`; no seam where they meet, hl1 overlaps hl2 by 2 px). Spotlight (L7 look, 65%
  dim, feathered hole) still works on dark: the spotlit headline / sentence stay at full brightness, the rest of the
  page drops to ~35%; the dim is pure black here (was #0A0A0A), so the hole leaves no visible box on the #000 page.
* **Camera (note 13)**: the v02 push 100 -> 108% (A), zoom-out 112 -> 100% (B), push 100 -> 108% (C) and the punch-in
  112 -> 100% on the headline (D) are gone. A-D share ONE slow push 100 -> 104%, easeInOutSine, from local 0 to the cut to
  the sentence (58): scale(L) = 1 + 0.04 x sine.inOut(L / 58) (22: 101.26%, 31: 102.22%, 41: 103.21%, 58: 104%), each
  shot's wrapper playing its own segment of the curve (D about the headline centre). E keeps the article push-in the v02
  note asked for (the L7 spotlight push: 100 -> 118% + drift, easeInOutSine, one move on the edit clock shared with
  b08-break; unchanged).
* **Captions (notes 11, 16, 17)**: v03 lockups (kit `lockups` + `lockupsWire`): centred over the office B-roll and the
  headline; on the sentence shot the frame centre is the spotlit sentence, so the last lockup sits below it (y 840):

| lockup | spec | words (local f; * = pop + blur) | on screen |
|---|---|---|---|
| 1 | `So the people [above]* the team` | So 6, the 9, people 13; above* 22 (the cut to B); the 31, team 35 | 6-41 (shots A, B, C) |
| 2 | `keep trying` (one small line) | keep 41, trying 48 | 41-58 (the headline) |
| 3 | `to [shut]* it down.`, ink centre y 840 | to 58; shut* 62 (swipe 1 lands); it 68, down. 72 (swipe 2 lands) | 58-102 (through the tail handle) |

Review stills: `review/v03/` (`sheet_v03.jpg`; every word, the cuts, the headline, both swipes, the clean highlight, the
B8 continuity frame 96). No render (v03). `check`: 0 errors; warnings = nested markup (dims, highlight group, lockups),
`line_unread` on voice-timed lockups.

(The v02 section below still applies where this v03 section does not change it.)

---

## v02 (REVISION_v02.md) - what changed and why
Client note 3: "at 0:31 the motion graphic is really bad again ... I don't really like the cancelled stamp as well, it
looks amateur ... so just make it turn red or something. Or pull an article broll talking about it's cancellation (if
that exists) and highlight the text which says it." -> **the L5 gray card, the framed clip and all three CANCELLED stamps
are gone.** The article exists and is used: Game Developer (formerly Gamasutra), Jan 31 2011, "Penn: First Grand Theft
Auto Was 'Almost Canned'", https://www.gamedeveloper.com/pc/penn-first-i-grand-theft-auto-i-was-almost-canned-
(manifest R-ID `R7.GD`, a live screenshot of the page, 2232 x 2352 PNG, never edited; the same Gamasutra interview as the
B6 quote). Plus notes 10 (fast pace), 11 (captions word by word, max 2), 12 (Coolvetica), 14 (nothing linear), 15
(zooms), 13 (no grain/vignette/chroma in the beat). Re-timed to the v02 beat map (VO 115%: 96f -> 90f).

### 1. What the viewer sees
Fast full-frame cuts through the office B-roll: a woman with a headset typing in an early-1990s office (push in), the
open-plan office on "above" (zoom out), a DMA Design developer at his desk in 1990, joystick in hand, a game on the CRT,
on "the team" (push in). On "keep" the picture flashes siren red and cuts to the real Game Developer article: the
headline "Penn: First Grand Theft Auto Was 'Almost Canned'" spotlit (the rest of the page dimmed), punching in. On "to"
it cuts to the article body: the sentence "It was almost canned. The publisher, BMG Interactive, wanted to can it"
spotlit while the camera pushes in and drifts to it; a yellow highlighter swipes across "It was almost canned." landing
on "shut" (the picture turns red), then across "The publisher, BMG Interactive, wanted to can it" landing on "down."
(red again). B8 carries the same shot on until it breaks.

### 2. Assets
* R7.1 early-1990s office (archival stock, PublicDomainFootage): window 0.4-9.0 s, crop 576:324:32:0 (16:9 above the
  burned-in watermark band y 335-365).
* R7.3 DMA Design office tour, 1990 (plan B7 B-roll): window 62.6-64.2 s, crop 384:216:0:24 (16:9 of the 384 x 288 VHS).
* R7.GD the article still (`04_Broll/B07/R7.GD__gamedeveloper-2011_penn-gta-almost-canned.png` + `.json` rects; added to
  `footage.json` rids, copied by `tools/sync_footage.py` to `assets/footage/R7.GD.png`).
* Kit: `RCK.cam` push / zoomOut / punchIn, `.rc-t9-hl` + `T.highlight` (T9 highlighter as B4), `X.flash` (the X3 flash
  curve, used on a siren-red multiply layer), the L7 spotlight look (#0A0A0A 65% with a rounded feathered hole, drawn in
  page pixels so it moves with the page), `captionPlanV2` / `captionHTMLV2` / `captionPops`.
* Look: R7.1 / R7.3 archival media treatment (plan p.10): temperature +0.06, saturation -0.2, warm shadows wheel (hue 35,
  0.08, +0.03); no grain / vignette (rule F). The article: no treatment.
* Audio (Tesseract): S06 x3 on the red hits, S07 riser into B8 (unchanged logic).

### 3. Tool and layer stack (HyperFrames, top -> bottom)
z40 T1 captions (white + soft shadow, low line y 860) | z30 three red-hit layers (#E3262E, mix-blend multiply, opacity
only) | z5 E: `#b07-driftE` (translate) > `#b07-camE` (scale) > `#b07-pageE` (static page framing: page x 50-1450, y
1564-2351.5, the article column only) > R7.GD + the two highlighter strokes + the spotlight dim (hole on the sentence) |
z4 D: `#b07-camD` > `#b07-pageD` (page x 23.5-1723.5, y 0-956) > white paper + R7.GD (clip-path crops the "Latest News"
sidebar out: x >= 1495 from y 395) + dim (hole on the headline) | z3 C `#b07-camC` > R7.3 | z2 B `#b07-camB` > R7.1 |
z1 A `#b07-camA` > R7.1. Fully opaque.

### 4. Step-by-step build (local frames; beat f = local - 6)
| shot | local f | picture | camera (all eased) |
|---|---|---|---|
| A | 0-22 | R7.1 @ 0:00.4, woman with headset typing | push 100 -> 108%, easeInOutSine |
| B | 22-31 ("above") | R7.1 @ 0:08.0, the open-plan office | zoom-out 112 -> 100%, easeInOutSine |
| C | 31-41 ("the team") | R7.3 @ 1:03.0, DMA developer at his desk | push 100 -> 108%, easeInOutSine |
| D | 41-58 ("keep trying") | article headline, spotlit | punch-in 112 -> 100% over 10f, easeOutExpo |
| E | 58-102 ("to shut it down.") | article sentence, spotlit + highlighted | push 100 -> 118% + drift (-93, -53) px, easeInOutSine, ONE move on the edit clock from local 58 to b08's "breaks" (b08 local 39); this beat plays its first 44 of 71 frames |
* Highlighter: swipe 1 over "It was almost canned." (page rect 247-605 x 1987-2035) from "to" (58) to 66, easeOutQuart
  (kit T9: 94% across on "shut", 62); swipe 2 over "The publisher, BMG Interactive, wanted to can it" (605-1389) from
  "it" (68) to 76 (94% on "down.", 72).
* Red hits (note 3 "just make it turn red"): kit X3 flash curve on a siren-red multiply layer, peak on "keep" (41),
  "shut" (62), "down." (72): C-3 0 | C-2 11% | C-1 44% | **C 100%** (easeInQuad) | C+1 73% ... C+6 2% | C+7 0
  (easeOutQuad). The first one ramps in over shot C and peaks on the cut to the headline.

### 5. On-screen text (plan: "T1: So the people / above the team / keep trying / to shut it down.")
| group | local f (beat f) |
|---|---|
| So | 6 (0) |
| the people | 9 (3) |
| above | 22 (16) |
| the team | 31 (25) |
| keep trying | 41 (35) |
| to shut | 58 (52) |
| it down. | 68 (62), held through the tail handle |
Each word pops on its own onset (kit T1 pop). Audit: max 2 words on screen, every word first visible on its onset frame,
Coolvetica. The article's own text is the page itself (not a caption).

### 6. Audio cues (`cues.json`, beat frames)
`stamp1` = 35 ("keep"), `stamp2` = 56 ("shut"), `stamp3` = 66 ("down.") = the red-hit peaks (the old stamp words; the
names are kept so the S06 mapping still works: Hit 1/2/3 start 3f / 8f / 4f before so their peaks land here). S07
riser: unchanged logic (`B8.first_black`, from `B7.stamp2`); B8's first black is now its beat f41.

### 7. Mistakes to avoid
* Never edit the article: no retouching, no text changes; only crops (the sidebar) and the camera. Highlight only the
  sentence that says it ("It was almost canned. The publisher, BMG Interactive, wanted to can it").
* Keep the E framing inside the article column (page x <= 1450; the sidebar starts at 1504) and above the PNG bottom
  (2352): the camera numbers are checked for every frame of the 71f move (page x 50-1450, y 1564-2351.5).
* b08-break continues shot E with the same page framing and the same camera function: change both together and re-run
  `hyperframes/b08-break/x4_still.sh`.
* No watermark: keep R7.1's crop above y 324.
* Red only on the three hits (REVISION_v02 G: the red is allowed here because note 3 asks for it).

### Footage used (v02)
| R-ID | original | window (s) on screen | crop | shows | link |
|---|---|---|---|---|---|
| R7.1 | `04_Broll/_originals/B07/R7.1__Early 1990's office workers archival stock footage [HtJSL-bGo_Y].mp4` | 0.4-1.13 (A), 8.0-8.3 (B) (window 0.4-9.0) | 576:324:32:0 | A: woman with a headset typing, colleagues behind; B: the open-plan office after the pan | https://www.youtube.com/watch?v=HtJSL-bGo_Y |
| R7.3 | `04_Broll/_originals/B07/R7.3__(1990) DMA Design Office Tour [iSoYy4Go_sg].mp4` | 63.0-63.33 (window 62.6-64.2) | 384:216:0:24 | a DMA Design developer with glasses at his desk, joystick in hand, a game on the CRT (1990) | https://www.youtube.com/watch?v=iSoYy4Go_sg&t=63 |
| R7.GD | `04_Broll/B07/R7.GD__gamedeveloper-2011_penn-gta-almost-canned.png` (live screenshot, captured 2026-11-16) | still, local 41-102 (+ b08) | sidebar cropped out | Game Developer, Jan 31 2011: headline "Penn: First Grand Theft Auto Was 'Almost Canned'"; body "It was almost canned. The publisher, BMG Interactive, wanted to can it, as it didn't seem to be going anywhere." | https://www.gamedeveloper.com/pc/penn-first-i-grand-theft-auto-i-was-almost-canned- |
Substitutions: none (R7.1 and R7.3 are the plan's B7 B-roll; R7.GD answers note 3).

### Checks (v02)
* `check`: 0 errors (warnings: track density, nested dim/highlight markup, `line_unread` on voice-timed groups).
* Headless audit (GSAP timeline): 26 tweens, all eased (sine.inOut, expo.out, power1.in/out, power3.out, two segments
  of sine.inOut), 0 linear; captions: max 2 words on screen, all 12 words first visible on their onset frame; Coolvetica.
* Render `05_GFX/renders/b07-shutdown.mov`: ffprobe 102 frames (beat 90 + 12), 1920 x 1080, 30 fps, ProRes 4444
  `yuva444p12le`, opaque. Review stills: `review/v02/` (every word, cut, zoom, red hit and both swipes).

---

# v01 reference (SUPERSEDED by the v02 redesign above: no L5 card, no CANCELLED stamps any more)

## B7 Shut it down - `b07-shutdown` (beat 96f = 3.200 s; composition 108f with 6f handles)

Plan p.23 (B7), p.14 (L5), p.17 (stamp motif), p.10 (archival grade). Storyboard B7. CONFLICTS C10, C17.
Render: `05_GFX/renders/b07-shutdown.mov` (ProRes 4444, opaque; no Tesseract shots).

## 1. What the viewer sees
A flat gray card with a tilted, white-bordered early-1990s office clip floating on it: a woman with a headset typing at
her desk, CRT monitors, colleagues in the cubicles behind. Three red CANCELLED stamps slam onto the picture, on "keep",
"shut" and "down", each harder-looking, with a short camera shake; after the third the camera in the clip starts to pan
across the open-plan office. T1 captions in card ink under the picture.

## 2. Assets
* R7.1 early-1990s office workers (archival stock). R7.3 (DMA Design office tour, 1990) is a plan alternative, not
  used: the build names R7.1. R7.2 (green-screen stamp) not used: the kit's CANCELLED stamp is the plan's spec.
* Kit: `.rc-l5__ground`, `.rc-l5__prop` + `.rc-l5__frame` (8 px white border, soft shadow), `M.stampTriple` (Inter
  Black 120 px, #E3262E, rough mask, 130 -> 100 % over 2f, 4 px shake for 4f), `S.push`, `S.propFloat`, `.rc-t1--low`.
* Archival media treatment on R7.1 (plan p.10: desaturate ~20 %, slight warm lift, subtle grain, light vignette).
* Audio (Tesseract): S06 x3, S07 riser.

## 3. Tool and layer stack (HyperFrames, top -> bottom)
z40 T1 captions (card ink, y 860) · z2 `#b07-cam` (push-in + shakes) > `#b07-prop` (tilt -4 deg, float) > white frame,
R7.1 (800 x 600, 4:3), stamp1-3 · z1 L5 gray ground (outside the camera, never shows a shaken edge).

## 4. Step-by-step build
1. `footage.json`: R7.1 3.6-9.2 s, crop 440:330:110:0 (4:3 from the top 330 px: the burned-in
   "www.PublicDomainFootage.com" watermark at y 335-365 is left out) -> `python3 tools/sync_footage.py`.
2. Video media-start 0 (= original 0:03.6); b08-break plays it on from 3.2 s.
3. Camera push: 100 % at B7 f0 -> 104 % at B8 f35 (the shatter), linear on the edit clock (shared with b08-break).
4. Stamps land on "keep" (local 43), "shut" (65), "down" (76): slam starts 2f before, 130 -> 100 %, shake 4 px for 4f;
   on-screen rotations -8 / -4 / +6 deg (prop -4 deg + stamp -4 / 0 / +10), offsets ~30 px.
5. T1 chunks: "So the people" 6 · "above the team" 23 · "keep trying" 43 · "to shut it down." 61 (local), the last holds
   through the tail handle.

## 5. On-screen text (plan: "T1: So the people / above the team / keep trying / to shut it down.")
| chunk | beat f |
|---|---|
| So the people | 0 |
| above the team | 17 |
| keep trying | 37 |
| to shut it down. | 55 |
CANCELLED x3 (stamp motif) at beat f37, f59, f70.

## 6. Audio cues (`cues.json`)
`stamp1` = 37, `stamp2` = 59, `stamp3` = 70 (beat frames). S06 Hit 1/2/3 (-12, -10, -8 dBFS) start 3f, 8f and 4f
before each landing (peaks 0.09 / 0.26 / 0.12 s). S07 riser: its end lands on B8's first black frame (B8 f45); the
assembly starts it at B7 f77 (C17: the 2.133 s file cannot start on the second stamp and still end on the black).

## 7. Mistakes to avoid
* No watermark: keep the 330 px crop if the R7.1 window changes.
* Never stretch the 4:3 archive into 16:9; the frame is 800 x 600.
* B8 continues this exact card: same layout, push/float functions of the edit frame, R7.1 continuous source time
  (B8 media-start = 3.2 s); re-run `hyperframes/b08-break/x4_still.sh` after any change here.

## Footage used
| R-ID | original | window (s) on screen | crop | shows | link |
|---|---|---|---|---|---|
| R7.1 | `04_Broll/_originals/B07/R7.1__Early 1990's office workers archival stock footage [HtJSL-bGo_Y].mp4` | 3.6-7.2 (window 3.6-9.2; B8 continues 6.8-8.5) | 440:330:110:0 | woman with a headset typing at her desk, CRT monitors, colleagues behind; the camera starts panning right across the office at ~6.5 s | https://www.youtube.com/watch?v=HtJSL-bGo_Y&t=3 |

Substitutions: none.

## Pending / notes
* Nothing pending. check: 0 errors; warnings = T1/stamp lines under the CLI's reading floor (voice timing) and track
  density.
* Render `05_GFX/renders/b07-shutdown.mov`: 108 frames (beat + 12), 1920 x 1080, 30 fps, yuva444p12le (ffprobe, counted).
