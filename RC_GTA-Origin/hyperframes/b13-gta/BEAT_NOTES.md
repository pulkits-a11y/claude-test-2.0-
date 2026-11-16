# B13 Grand Theft Auto: beat notes (b13-gta)

## v02 (REVISION_v02.md, client notes on v01): what changed

Beat **205f** (was 214), composition **217f** (205 + 2 x 6f handles), root `data-duration="7.2333333"`. Frames below are
v02 beat frames (local = beat + 6). Everything after this section is the v01 record (v01 frames, Inter fonts).

| What | v01 | v02 | Why (note / rule) |
|---|---|---|---|
| Timing | VO 108%, B13 214f | VO 115%, 205f: "Until" 1, "in" 27, "November" 30, "1997," 45, "it" 80, "Grand" 124, "Auto." 140, voice ends 155; 43f title-hold room tone after "Auto." | note 10 (shared re-time) |
| Fonts | Inter / Instrument Serif | Coolvetica / Coolvetica Italic (kit `base.css`) | note 12 |
| T1 captions | chunk clips "Until finally," / "it ships with" / "a new name:" | word by word, max 2 words (kit `captionPlanV2` + `captionHTMLV2` + `captionPops`): "Until finally," 1 (card ink) / "it ships" 80 / "with" 91 / "a" 98 / "new name:" 101 -> out on "Grand" 124 | note 11, rule A |
| T3 "In Nov 1997" | push 100 -> 104% linear | same card (M6), "In" hard cut on "in" 27, "Nov" on "November" 30, digits roll on "1997," 45 (easeOutQuart, land 59, cue `year_digits` = 45); card push 100 -> 106% easeInOutSine to the cut | rules C, D |
| X3 into L6 | linear ramp/fade | kit v02 eased flash centred on the cut at 80 (ramp easeInQuad 77-80, 100% on 80, fade easeOutQuad 80-85), silent | rule C |
| L6 camera | push 100 -> 104% linear | `#b13-l6` is the camera: punch-in 112 -> 100% over 10f (easeOutExpo) on the cut under the flash fade, then push 100 -> 106% (easeInOutSine) to the cut out at 181 | rule D |
| **THEFT vs the L6 frame** | Inter Black 400 px; THEFT's outer letters peeked out of the 4:3 frame | Coolvetica is narrower (kit report: THEFT hides behind the 62% frame). Restored v01's look: the 4:3 frame is **768 x 576** (53.3%, still exactly 4:3, the 1997 intro is never cropped or stretched; `--rc-l6-w/h` on `#b13-l6`) and T6 is **396 px** (`--rc-t6-size` on `#b13-t6`): the frame covers the middle letters H-E-F, both T's of THEFT show ~70% (v01 ~85%), G and D of GRAND and A, O of AUTO stay clear; the stack's ink stays inside title-safe at the end of the 106% push (measured on the last L6 frame: y 56-1016, x 329-1588) | kit report, plan p.12 "the frame overlaps the middle letters" |
| T6 type-on | a letter every 2f (constant) | same 26f total, start times on easeOutQuad (kit `giantType`: +0 4 7 11 14 16 18 20 22 24 25 25 26 26f) from "Grand" 124 (cue `type_on` = 124), last letter 150, hold 31f (>= 1 s) to the hard cut at 181 | rules C, E; plan "hold 1 s" |
| L2 unboxing (Tesseract) | f190-214, push 100 -> 104% linear | f181-205 (24f = 0.8 s), framing v2 keys: 112% -> 101% in 10f (easeOutExpo) -> 105% at f24 (easeInOutSine); same moment R13.2 @ 101.6 s, crop, archival grade, bars slide in 8f | rules C, D |
| Framed clip treatment | archival grade incl. grain 0.10 + vignette 0.12 (media-treatment) | archival colour only (saturation -0.2, temperature +0.06, shadows +0.04): grain and vignette set to 0 with `media-treatment`, because the assembly now adds the whole-edit grain and vignette (rule F: no beat-level grain/vignette/chroma) | rule F |
| R13.1 window | 48.333-51.80 s | 48.333-51.70 s (same `data-media-start` 0.4333 on the cut: the D-man's impact lands on the cut frame 80) | re-time |

`cues.json` = `{"year_digits": 45, "type_on": 124}`. `tesseract_shots.json`: B13-unboxing-band f181-205 with framing keys. No grain,
vignette or chroma in the beat (the assembly adds them).

Checks: `check --json` 0 errors (warnings as v01: duplicate media by design, nested T3/T6 markup, track density, frame 0 on
the gray card, `line_unread` on the 1-word groups the voice forces ("with" 7f, "a" 3f) and on T6 "as the film's last line",
contrast 2.2:1 on THEFT's "H", which is covered by the frame). Snapshots `review/v02/a/` + `review/v02/sheet_a.jpg` (every
caption word, the digit roll, the flash frames, the punch-in, T6 letters, the hold, the cut out). Render
`05_GFX/renders/b13-gta.mov`: ProRes 4444, 1920x1080, 30 fps, **217 frames**, `yuva444p12le` (ffprobe, counted).

---


Plan p.25 (B13 build), p.18-19 (overview row), p.16 (into the beat: "B13 X1, then X3 into the framed clip"), T3/T6 p.11-12,
L2/L6 p.13-14, X3 p.16, M6 p.18, grade p.10, accuracy p.40 ("November 1997, it ships": fine as written). STORYBOARD.md B13,
CONFLICTS.md C14. Frames below are **beat frames** (f0 = "Until"); composition local frame = beat frame + 6.
Composition: 226 frames (214 + 6f handles), `05_GFX/renders/b13-gta.mov` (ProRes 4444 with alpha).

## 1. What the viewer sees

The gray "In Nov 1997" year card builds with the voice and rolls its digits, a white flash reveals the 1997 GTA 1 intro in a
glowing frame over its own blurred copy, GRAND / THEFT / AUTO types on behind the frame and holds, then a hard cut to the
GTA 1 big-box unboxing in a letterboxed band.

## 2. Assets

| Kind | ID / file | Where |
|---|---|---|
| B-roll | **R13.1** GTA 1 intro, 1997 - REAL: the DMA Design D-man logo animation (`assets/footage/R13.1.mp4`, see Footage used) | L6 framed clip + its blurred back copy (in this composition) |
| B-roll | **R13.2** GTA 1 PC big-box unboxing - REAL: the opened box, jewel case + map (see Footage used) | L2 band f190-214, **Tesseract** (`tesseract_shots.json`: source, source_in_s 101.6, crop) |
| B-roll (not used) | R13.3, R13.4, R13.5, R13.6 (alternates) | only if R13.1 / R13.2 are unusable |
| SFX | **S12** = S04's file "Countdown, List, Numbers (2)" | f48, first digit move |
| SFX | **S13** "v3) Type (A B C )" | f132, first letter |
| Music | no MU cue in B13; f165-214 is "the B13 title hold" (no voice) | Tesseract |
| Fonts | Inter Medium 500 (T1), Inter Bold 700 (T3 year), Instrument Serif Italic (T3 *In*), Inter Black 900 (T6) | kit `base.css` |
| Kit | T3 `yearCard` (M6: same component and geometry as B3), T1 `captionPlan`, T6 `giantType`, L6 `rc-l6 rc-l6--4x3`, X3 `flash`, `S.push`, `S.hard` | `assets/kit/` |
| Cut-outs | none | |

## 3. Tools and layer stack

HyperFrames (this composition) owns f-6..190: the T3 card, X3, L6 + T6, all text. Tesseract owns f190-214 (+ tail handle):
the R13.2 unboxing in the L2 band; this composition is fully transparent there. Tesseract owns all audio.

Top to bottom (z-index):
1. `#b13-x3` X3 white flash (z 40), local 89-96
2. T1 captions (z 20): `#b13-cap-a-1` (card ink), `#b13-cap-b-1`, `#b13-cap-b-2` (white + soft shadow) - under the flash
3. `#b13-l6` L6 group (z 2), pushed 100 -> 104%: (top) `.rc-l6__frame` = 2 px white border + 30 px warm glow + framed R13.1
   (62%, 4:3 frame 892.8 x 669.6 centred) > `#b13-t6` T6 giant type > `.rc-l6__bg` = R13.1 full frame, 50 px blur, 40% darker
4. `#b13-t3` T3 year card (z 1): full-frame #E9E9E9, *In* + "Nov 1997", content pushed 100 -> 104%
5. (f190+) nothing: transparent, Tesseract's R13.2 band shows through

## 4. Step-by-step build (beat frames; seconds from the beat start in brackets)

| Beat f | What | Values / ease |
|---|---|---|
| -6..85 | T3 year card on screen (head handle included: the card continued backward) | card content push 1.00 -> 1.04 linear from local 0 to the cut |
| 1 (0.03 s) | T1 "Until finally," hard cut in on "Until" (captionPlan, +0.04f from the voice) | card ink #111111, no shadow, y 620 |
| 28 (0.93 s) | T1 hard cut out; *In* hard cut in on "in" | Instrument Serif Italic 64 px #111111 |
| 32 (1.07 s) | "Nov" hard cut in on "November" | Inter Bold 220 px, tracking -2% |
| 48 (1.60 s) | digits 1-9-9-7 roll up on "1997": each slides up 40 px from its mask over 8f, 2f stagger | `power3.out`; last digit lands f62 (2.07 s) |
| 83-89 | X3 white flash centred on the cut at f85 (refreshed kit, frames on screen): 33% f83, 67% f84, 100% f85, 80/60/40/20% f86-89, 0 f90 | linear ramps (kit), silent |
| 85 (2.83 s) | hard cut (under 100% white) to L6: R13.1 framed at 62% over its own blurred, darker copy; the DMA D-man's impact frame (source 48.333 s) lands exactly on f85, so the flash reveals him slammed into the ground | L6 push 1.00 -> 1.04 linear f85-190 |
| 85 | T1 "it ships with" on "it" (+0.19f) | white, soft shadow, y 620 |
| 105 (3.50 s) | T1 "a new name:" on "a" (+0.36f) | |
| 132 (4.40 s) | T1 out; T6 GRAND / THEFT / AUTO types on BEHIND the frame, one letter every 2f, no fades | Inter Black 400 px, tracking -4%, 3 stacked lines |
| 158 (5.27 s) | last letter (O of AUTO) | |
| 158-190 | title holds 32f (1.07 s, "let the title breathe for a full second") | push continues |
| 190 (6.33 s) | hard cut: everything off, composition transparent; Tesseract R13.2 unboxing in the L2 band to f214 | |

Media treatments (CLI `media-treatment`, never CSS filters): framed clip `#b13-l6-clip` archival grade (plan p.10:
desaturate ~20%, slight warm lift, subtle grain, light vignette) = `adjust {saturation -0.2, temperature 0.06, shadows 0.04}`,
`details {grain 0.10, grainSize 0.2, grainRoughness 0.6, vignette 0.12}`; back copy `#b13-l6-bg` = L6 `effects.blur 1` (laid out
at 1/2.2, scaled 2.2 = sigma 50 px) + `adjust.exposure -0.737` (40% darker) + the same saturation/temperature.

## 5. On-screen text

| Text (exact) | T-style | Position / size | On / off (beat f) |
|---|---|---|---|
| Until finally, | T1, card ink on the gray card | centred x 960, y 620; Inter Medium 46 px | 1 -> 28 |
| *In* | T3 | above the left edge of the date line; Instrument Serif Italic 64 px #111111 | 28 -> 85 |
| Nov 1997 | T3 | date line centred on x 960, caps centred y 540; Inter Bold 220 px #111111, tracking -2% | Nov 32, digits roll 48 -> 85 |
| it ships with | T1 | x 960, y 620 (inside the framed clip); white + soft shadow | 85 -> 105 |
| a new name: | T1 | same | 105 -> 132 |
| GRAND / THEFT / AUTO | T6 | 3 stacked lines centred, Inter Black 400 px white + soft shadow, behind the L6 frame (frame overlaps the middle letters); ink y 56-1025 at the end of the push (inside title-safe) | 132 (G) ... 158 (O) -> 190 |

T-styles featured: T3 -> T6 (rotation p.13 "B13 T3 -> T6"; neighbours B12 T2 and B14 T4 differ). No glitch, no siren wash.

## 6. Audio (Tesseract places them from `cues.json`)

| Cue | Event (beat f) | Placement | Level |
|---|---|---|---|
| S12 (same file as S04, "so the second year card echoes the first") | `year_digits` = 48 | start on the first digit's move | -16 dBFS |
| S13 "v3) Type (A B C )" (1.3 s) | `type_on` = 132 | start with the first letter; the letters run 132-158 (26f = 0.87 s): if the file does not sit with the letters, slice single keystrokes, one every few letters | -18 dBFS |
| X3 flash | f85 | **silent** (plan p.25) | - |
| Music | f165-214 = "the B13 title hold" (no voice; C14) | let the music come up to about -16 LUFS short-term (plan p.35), ducked again under B14's voice | - |

If it feels busy, cut S12 first (plan p.38).

## 7. Mistakes to avoid

- Don't change the year card's design from B3's (M6): same kit T3, same geometry, same tick sound.
- Don't let the T1 caption overlap the year line (T1 is cut when *In* arrives).
- Don't put text, a logo or a label on the L6 frame: the plan gives B13 no label text (never add facts).
- Don't stretch the 1997 4:3 intro: it sits in the 4:3 L6 frame (cover-cropped, never distorted).
- Don't fade T6 letters (hard type-on) and don't cut the title before it has held a full second (f158 -> f190).
- Keep "November 1997" exactly (accuracy note p.40); the flash is silent.
- Keep both R13.1 copies frame-locked (same `data-media-start`, `data-start`, `data-duration`).

## Interpretations / conflicts

1. **C14 (CONFLICTS.md):** B13 is 214f because the voice gap after "Auto." was opened so typing + 1 s hold + 0.8 s unboxing fit.
2. ***In* on "in" (f28), "Nov" on "November" (f32)** instead of the storyboard's "In/Nov on 'November' @32": keeps every
   on-screen word within +/-2f of its spoken word (plan p.11 rule 5, QA p.42); the T1 "Until finally," cuts out on the next
   text chunk (*In*). Mirrors B3, where *In* appears with the first word of the spoken date phrase.
3. **T3 "hold 1 s" (p.25) / "Hold at least 1 s" (p.11):** digits roll on the spoken year (f48, like B3 on "1995"; S12 = S04
   placement) and land f62; the cut into L6 is on "it" (f85, storyboard). The card is on screen 85f (2.8 s), the complete date
   23f after the landing. Read as "the card holds >= 1 s" (the storyboard's reading for B3: "Card visible 50f (>= 1 s
   hold)"). The kit's stricter reading (>= 1 s after the landing, KIT_type conflict 6) would put the cut at f92+, mid-"ships"
   (not a stressed-syllable cut, rule 6), or roll the digits before "1997" is spoken. Flagged, not silently resolved.
4. **L6 4:3 frame** (892.8 x 669.6): the 1997 intro is 4:3 material ("keep 4:3 inside a band or frame (L2, L6)", p.10) and
   T6 "sits behind ... so the frame overlaps the middle letters" (p.12); the 16:9 frame (1190.4 x 669.6) would hide nearly all
   of THEFT and AUTO. Switch to the 16:9 frame (drop `rc-l6--4x3`) only if the real R13.1 is native 16:9 content.
5. **L6 label** (library p.14: "small label under it"): B13's build (priority 2) gives no label text, so none (never add facts).
6. **T6 timing:** 14 letters at 2f from "Grand" (f132): the last letter is f158 (storyboard "done @160"); the hold to the cut
   (f190) is 32f >= 30f.
7. **X3:** "centred on the cut" = 100% white on the cut frame f85 (ramp 2f, hold 1f, fade 4f, counted in frames on screen: refreshed kit), linear (kit choice, plan names no ease);
   the T1 "it ships with" starts on f85 under the flash.
8. **L2 bars on a hard cut:** the unboxing band uses the L2 library's 8f bar slide-in ("when entering a cinematic moment") -
   noted for Tesseract in `tesseract_shots.json`.
9. **Held-shot push (rule 7):** the year card content and the L6 group (back copy, T6, frame) each push 100 -> 104% linear.
10. **`check` warnings weighed:** `duplicate_media_discovery_risk` (the L6 back copy and framed clip share the source: by
    design), `nested_structure_needs_subcomposition` (kit T3/T6 markup), `first_frame_empty` (frame 0 is the head handle on the
    gray card, not a thumbnail), `line_unread` (T1 chunks follow the voice; T6 is not the film's last line).
11. **M6 cross-check (done against b03-dundee):** same kit T3 component with the default geometry (`--rc-y` 540), *In* as a
    hard cut on the first word of the spoken date phrase (B3 "It's", B13 "in"), digits rolling on the spoken year, content
    push 100 -> 104% from the head handle to the hard cut out. Only the date text differs ("1995" vs "Nov 1997").

## Footage used

| R-ID | File (04_Broll/_originals/...) | In-out (s, original) | Beat frames | What it shows | Link |
|---|---|---|---|---|---|
| R13.1 | `B13/R13.1__Grand Theft Auto Intro (1997) [m2CHL4ACCEs].mp4` | 48.333-51.80 | f85-190 (both L6 copies, `data-media-start 0.4333` in the 47.9-51.9 working clip) | GTA 1 intro (PS1 boot): the DMA Design D-man slams into the ground, smoke, then lies run over with tyre tracks across him (the hold f160-190 ends on him) | https://www.youtube.com/watch?v=m2CHL4ACCEs&t=48 |
| R13.2 | `B13/R13.2__Original GRAND THEFT AUTO from 1997 - PC Big Box Unboxing [BcnDNeEggls].mp4` | 101.6-102.4 (60 fps) | f190-214, Tesseract L2 band | the opened big box: GTA jewel case with its cover art in the insert, the San Andreas map beside it, hands at the edges | https://www.youtube.com/watch?v=BcnDNeEggls&t=101 |

* R13.1 crop `632:474:51:1`: the upload is square-pixel 720x480 with the 4:3 picture pillarboxed at x 46-688 (cropdetect
  642:476:46:0); exact 4:3 so the working clip is 1440x1080 (the 4:3 L6 frame `rc-l6--4x3` stays). Archival treatment unchanged.
* R13.2 crop `1420:799:500:160` (Tesseract): keeps the uploader's facecam picture-in-picture (top-left, x<500, y<352) out of the band.
* Other R13.1 moments rejected: the loading screen 1:02-1:12 shows the GTA logo but prints "Copyright (C)1998 ..." (the PS1 port's
  year, next to "Nov 1997": avoided); PlayStation / Take 2 / Visual Sciences / VISOS logos are not GTA; menus are UI.
* No substitutions in B13.

## Still pending

* Nothing blocking. T6 over the brightest late hold frames (the run-over D-man on white, f175-190) measures 2.5-2.6:1 against the
  blurred, 40%-darker copy (check `contrast_aa_failure` warning); the giant 300+ px letters read clearly in the snapshots. If the lead
  wants more punch: SUGGESTION a stronger darkening of `#b13-l6-bg` only (the plan's "40% darker" is met as the kit measured it).

Render: `npx --yes hyperframes@0.9.52 render . --format mov --workers 1 -o ../../05_GFX/renders/b13-gta.mov`
