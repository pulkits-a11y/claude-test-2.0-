# B13 Grand Theft Auto: beat notes (b13-gta)

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
| B-roll | **R13.1** GTA 1 intro, 1997 (`assets/footage/R13.1.mp4`) | L6 framed clip + its blurred back copy (in this composition) |
| B-roll | **R13.2** GTA 1 PC big-box unboxing | L2 band f190-214, **Tesseract** (`tesseract_shots.json`) |
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
| 83-90 | X3 white flash centred on the cut at f85: 0% f83, 50% f84, 100% f85-86, 75/50/25% f87-89, 0 f90 | linear ramps (kit), silent |
| 85 (2.83 s) | hard cut (under 100% white) to L6: R13.1 framed at 62% over its own blurred, darker copy | L6 push 1.00 -> 1.04 linear f85-190 |
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
7. **X3:** "centred on the cut" = 100% white on the cut frame f85 (and f86), linear ramp/fade (kit choice, plan names no ease);
   the T1 "it ships with" starts on f85 under the flash.
8. **L2 bars on a hard cut:** the unboxing band uses the L2 library's 8f bar slide-in ("when entering a cinematic moment") -
   noted for Tesseract in `tesseract_shots.json`.
9. **Held-shot push (rule 7):** the year card content and the L6 group (back copy, T6, frame) each push 100 -> 104% linear.
10. **`check` warnings weighed:** `duplicate_media_discovery_risk` (the L6 back copy and framed clip share the source: by
    design), `nested_structure_needs_subcomposition` (kit T3/T6 markup), `first_frame_empty` (frame 0 is the head handle on the
    gray card, not a thumbnail), `line_unread` (T1 chunks follow the voice; T6 is not the film's last line).
11. **M6 cross-check:** B3 (lane A) was not built when B13 was finished; both use the kit T3 with its default geometry
    (`--rc-y` 540). If b03-dundee changes the T3 geometry, mirror it here.

## Pending real footage

- **R13.1 in-point:** `data-media-start="2.0"` on BOTH `#b13-l6-bg` and `#b13-l6-clip` (keep them equal) is a stand-in value;
  pick the most recognisable 3.5 s of the 1997 intro for f85-190 (a moment without its own big title text competing with T6).
- **R13.1 aspect / crop:** confirm 4:3 (keep `rc-l6--4x3`) or native 16:9 (remove it); set `--rc-pos` on both videos if the
  subject is off-centre; re-check that T1 at y 620 does not sit on a face (else use `rc-t1--low`, y 860, as T1 allows).
- **R13.1 grade:** re-check the archival treatment strength on the real clip (`npx hyperframes media-treatment --selector ...`).
- **R13.2 (Tesseract):** `source_in_s`, the moment (box opened, art readable) and the crop into the 1920 x 804 band.
- Re-sync and re-render: `python3 ../../tools/sync_footage.py .` then the render command below.

Render: `npx --yes hyperframes@0.9.52 render . --format mov --workers 1 -o ../../05_GFX/renders/b13-gta.mov`
