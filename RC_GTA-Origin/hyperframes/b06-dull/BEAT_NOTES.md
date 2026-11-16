# B6 It's dull - `b06-dull` (v02: beat 156f = 5.200 s; composition 168f with 6f handles)

## v02 (REVISION_v02.md; client notes 10, 11, 12, 13, 14, 15) - what changed
Re-timed to the v02 beat map (VO 115%: beat 166f -> 156f, composition 178f -> 168f, root `data-duration` 5.6000000) and
the global rules applied. Kept as built: the split screen continuing B5 (same clips/crops, continuous source time: media
start = B5's + 83f = 2.7666667 s), the B&W drain + slow-down to 50% on "dull", T2 "it's dull.", X2 into the L5 card, the
Gary Penn cut-out (the same `remove-background` clip), the T8 quote card and its exact text.
* **Rule A (note 11)**: T1 and T2 rebuilt with `captionPlanV2` / `captionHTMLV2` + `T.captionPops`: "But there's" (local
  6) / "a problem:" (17) / T2 "it's" (38) + keyword "dull." (46: blur punch 30 -> 0 px, 108 -> 100%, 6f easeOutExpo); the
  pair exits over 3f (easeInCubic) ending on the X2 cut (64). Max 2 words on screen, every word on its onset (audit).
  The T8 quote card is a designed card (rule A exemption): it keeps its type-on.
* **Fonts (note 12)**: Coolvetica / Coolvetica Italic. The T8 quote in Coolvetica Italic 110 px is 911 px wide on one
  line (wider than the 816 px column, kit report), so it breaks after "awful…": `“awful…<br>too sim-y.”` (same words,
  same punctuation, 2 lines). Name "Gary Penn" and role "DMA DESIGN · GAMASUTRA, 2011" unchanged.
* **Rule C (note 14)**: the v01 `ease: 'none'` drain is now easeInOutCubic (power2.inOut) on the LUT intensity (still the
  LUT's own intensity, so the B5 contrast grade stays on across the cut); the rate lane (1.0 -> 0.5 over 6f) is the kit's
  `rateRamp` sampled from easeInOutCubic every 1/4 frame (no linear segment); the v01 `S.push ... to: 1.04` calls are gone;
  T8 type-on placed on easeOutQuad timing (kit `quoteType`), name/role fade easeOutCubic. 0 linear tweens (audit).
* **Rule D (note 15)**: split screen: the head handle finishes b05's push (100 -> 108%, same curve), then an eased
  zoom-out 108 -> 100% (easeInOutSine) from the cut (local 6) to the X2 cut (64), under the drain and slow-down. Card:
  push 100 -> 108% easeInOutSine from the X2 cut (64) to the end (168) (v01: 104%). The X2 slide stays (60 px, 20f,
  easeOutQuart); the prop float stays (easeInOutSine legs).
* **Rule F (note 13)**: the Penn cut-out's media treatment lost its grain (0.12) and vignette (0.15): the assembly adds
  the whole-edit grain/vignette. Kept: saturation -0.2 and the warm shadows wheel (archival look, plan p.10).

| element | v01 local f | v02 local f (beat f) |
|---|---|---|
| T1 | But there's 6 / a problem: 18 | But there's 6 (0) / a problem: 17 (11) |
| T2 | it's 40, dull. 49, fade 63-67 | it's 38 (32), dull. 46 (40), exit 61-64 |
| drain + slow to 50% | 49-55 (linear) | 46-52 (40-46), easeInOutCubic |
| X2 cut on "One" | 67 | 64 (58) |
| T8 name + role | 67-73 | 64-70 (58-64) |
| T8 quote type-on | 118-127 (19 chars, 2/f) | 112-120 (106-114; 18 chars, eased timing) |
| end | 178f | 168f |

`cues.json`: `dull` = beat 40 (S05 starts on "dull"; MU3 sits under it). `tesseract_shots.json`: no shots.
Review stills: `review/v02/`. Render `05_GFX/renders/b06-dull.mov` (v02): ffprobe 168 frames (beat 156 + 12), 1920 x 1080,
30 fps, ProRes 4444 `yuva444p12le`, opaque. `check`: 0 errors (warnings: nested T2/T8 kit markup, the 22 px role line,
`line_unread` on voice-timed groups).

---

# v01 reference (superseded where the v02 section above differs; frames below are v01)

## B6 It's dull - `b06-dull` (beat 166f = 5.533 s; composition 178f with 6f handles)

Plan p.22 (B6), p.14 (L5), p.16 (X2), p.11-12 (T1, T2, T8), p.10 (grades), p.4 (background removal). Storyboard B6.
Render: `05_GFX/renders/b06-dull.mov` (ProRes 4444, opaque; no Tesseract shots).

## 1. What the viewer sees
The B5 split screen carries straight on (same two chases, continuous source time, no arrow). On "dull." it drains to
black and white over 6f and slows to half speed while "it's dull." punches in (T2). On "One" it cuts and drifts (X2)
to a flat gray card: Gary Penn, cut out of his BAFTA talk and still talking, on the left inside a white outline; on the
right his name and role fade in, and from "awful" the quote types on, then the card holds to the end (the beat's
deliberate hold).

## 2. Assets
* R5.2, R5.1 (the B5 working clips, continued), R6.1 (Gary Penn, BAFTA Games Mini Masterclass) -> background-removed
  cut-out `assets/footage/R6.1_cutout.webm` (VP9 + alpha, 1200 x 1080, 138f).
* Kit: `.rc-l11`, rate lane (slow to 50 %), B&W LUT (`.media/luts/lut_001.cube`, media-use parametric LUT
  `{"saturation":-1}`), `.rc-l5__ground`, `.rc-l5__prop` + `.rc-l5__cutout` (8 px white outline + soft shadow, -4 deg,
  float +/-6 px), `X.drift` (X2), `T.punchPair` (T2), `T.nameIn` + `T.quoteType` (T8; names now italic per the kit).
* Audio (Tesseract): S05 on "dull"; MU3 (quietest part of the track under "dull" and the quote).

## 3. Tool and layer stack (HyperFrames, top -> bottom)
z31 T2 pair · z30 T1 captions · z4 T8 block (inside the X2 layer) · z3 `#b06-x2` X2 drift layer > `.lc-card-push`
(push-in) > L5 prop (cut-out) + T8 · z2 L5 gray ground (from the X2 cut) · z1 `.rc-l11` split (to the X2 cut).

## 4. Step-by-step build
1. `footage.json`: R5.2/R5.1 = the B5 windows (same crops); R6.1 = 30.0-34.6 s, crop 800:720:120:0 (10:9).
   `python3 tools/sync_footage.py hyperframes/b06-dull`.
2. Cut-out: `tools/make_cutout.sh` = `npx --yes hyperframes@0.9.52 remove-background <R6.1 working clip> -o
   assets/footage/R6.1_cutout.webm --quality best` (HyperFrames media tools, CLI 0.9.52; 138 frames, ~3.5 min CPU).
3. Split: halves play the B5 clips from media 2.9333 s (= B5's 0 + 88f), so B6 local m = B5 local 88 + m.
4. "dull." (local 49 = beat f43): LUT intensity 0 -> 1 over 6f, linear (colour -> B&W; the contrast grade stays on, so
   the B5 -> B6 cut is invisible); rate lanes 1.0 -> 0.5 over the same 6f. Push-in continues B5's to 104 % at the cut.
5. T2: "it's" hard cut on local 40; "dull." 6f blur-in + 108 -> 100 % on local 49; pair fades 4f to the X2 cut (63-67).
6. X2 on "One" (local 67 = beat f61): card content slides 60 px right -> left over 20f, `power3.out`; held-shot
   push-in 100 -> 104 % to the beat end.
7. Cut-out prop: box 960 x 864 at (70, 290) (the clip's 10:9, bottom 74 px below the frame so the source's frame edge
   stays hidden), bottom-anchored, -4 deg, floating +/-6 px over 2 s.
8. T8: name + role fade in over 6f on "One" (67-73); quote types at 2 characters per frame from "awful" (local 118 =
   beat f112), complete on local 127; holds to the end of the tail handle.

## 5. On-screen text (plan: "T1: But there's / a problem: → T2: it's dull. → T8 quote card")
| element | text (exact) | beat f |
|---|---|---|
| T1 | But there's | 0 |
| T1 | a problem: | 12 |
| T2 lead-in / keyword | it's / dull. | 34 / 43 |
| T8 name (Instrument Serif Italic) | Gary Penn | 61 (6f fade) |
| T8 role | DMA DESIGN · GAMASUTRA, 2011 | 61 (6f fade) |
| T8 quote (types 2 chars/f) | “awful… too sim-y.” | 112 -> 121 |

## 6. Audio cues (`cues.json`)
`dull` = beat f43: S05 Music Slow Down starts on "dull" under the drain (plan S05: -14 dBFS, audible until 1.1 s).
MU3: the near-silent section of the track lands on or just after "dull" (storyboard: edit 26.24 s = beat f53).
Quote hold: no SFX.

## 7. Mistakes to avoid
* Quote, name and role exactly as written (curly quotes, one ellipsis character, "sim-y", "DMA DESIGN · GAMASUTRA,
  2011"); it is his recollection in a 2011 interview (plan Watch out). Never shorten or paraphrase.
* The split must not jump at the B5/B6 cut: same clips, same crops, media-start = B5 + 88f, same grade.
* The cut-out must stay a real background removal of R6.1 (no drawn mask); keep the BAFTA corner logo out of the crop.
* The quote hold is the one allowed hold over 2 s (with the B8 black); the card still pushes and the prop floats.

## Footage used
| R-ID | original | window (s) on screen | crop | shows | link |
|---|---|---|---|---|---|
| R5.2 | `04_Broll/_originals/B05/R5.2__Playing GTA 5 As A POLICE OFFICER City Patrol｜ HPD｜｜ GTA 5 Lspdfr Mod｜ [5TAB4i9P1eI].mp4` | 233.43-235.42 (half speed from beat f43) | 814:918:713:162 | B5's left half continued: the SUV chasing the taxi | https://www.youtube.com/watch?v=5TAB4i9P1eI&t=233 |
| R5.1 | `04_Broll/_originals/B05/R5.1__GTA San Andreas - Vigilante [12 Levels] [wy95d3TrAIQ].mp4` | 44.13-46.12 | 819:923:405:0 | B5's right half continued: the red car ahead of the police bike | https://www.youtube.com/watch?v=wy95d3TrAIQ&t=44 |
| R6.1 | `04_Broll/_originals/B06/R6.1__Quarrel Director & Designer Gary Penn ｜ Games Mini Masterclass [QAi3KZxBPI8].mp4` | 30.0-33.7 (cut-out of 30.0-34.6) | 800:720:120:0 | Gary Penn talking to camera in a cinema, one continuous medium shot (shot cuts at 27.12 s and 55.88 s) | https://www.youtube.com/watch?v=QAi3KZxBPI8&t=30 |

Substitutions: none. R6.2 (context) and R6.5 (optional) were not downloaded and are not needed by the build.

## Pending / notes
* Re-fitted from the stand-in: the cut-out is now the real `remove-background` result (the drawn bust mask and its
  `tools/bust_mask.py` are only used by `make_cutout.sh --standin`). Kit refresh applied (T8 name italic).
* A small out-of-focus ceiling light just right of his head survives the matte on some frames (it sits behind the
  hair in the source); left as is.
* check: 0 errors; warnings = nested T2/T8 blocks (kit markup) and the role line at 22 px under the CLI's 28 px phone
  floor (kit T8 size).
* Render `05_GFX/renders/b06-dull.mov`: 178 frames (beat + 12), 1920 x 1080, 30 fps, yuva444p12le (ffprobe, counted).
