# B3 1995, Dundee - `b03-dundee` (beat 215f = 7.167 s; composition 227f with 6f handles)

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
