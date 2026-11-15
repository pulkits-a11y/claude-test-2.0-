# B14 Every GTA since: beat notes (b14-since)

Plan p.26 (B14 build), p.19 (overview row: L10 burst -> M1 six stars -> siren -> whip into an escape; T4; X1, X9, X8;
S14, S15), p.16 (into the beat: "B14 X1, X9 and X8 inside the beat"; X5 is B15's way in), T4 p.12, L10 p.15, X5/X8/X9 p.16,
M1/M5 p.17. STORYBOARD.md B14, CONFLICTS.md C15. Frames are **beat frames** (f0 = "And"); composition local frame = beat + 6.
Composition: 200 frames (188 + 6f handles), `05_GFX/renders/b14-since.mov` (ProRes 4444 with alpha). A **transparent
overlay** over Tesseract's footage, except the four X9 frames (f140-143) and the shut X5 slats (f188+).

## 1. What the viewer sees

A 2-second burst of chase clips from every GTA since 2001, each with a tiny year tag, lands on a GTA 5 five-star chase where
six white wanted stars fill in; police lights flash red and blue on "The sirens.", a whip pan throws us into an escape, and
the three spoken phrases sit around the frame until the blinds shut.

## 2. Assets

| Kind | ID | Where / who |
|---|---|---|
| B-roll (Tesseract) | **R14.1** GTA 3 (2001), **R14.2** Vice City (2002), **R14.3** San Andreas (2004), **R14.4** GTA 4 (2008), **R14.5** GTA 5 (2013) | L10 burst f0-60, 2 clips each x 6f |
| B-roll (Tesseract) | **R1.3** GTA 5 five-star chase | f60-133, push-in |
| B-roll (Tesseract + 4f embed) | **RT3** police lights | f133-163; ALSO embedded in this overlay for f140-143 under the X9 wash |
| B-roll (Tesseract) | **R14.5** (or alternate R14.6) escape shot | f163-188 (+ tail handle) |
| Not used | RT7 (green-screen stars: M1 is built), R14.6 (alternate), R14.7 | |
| SFX | **S14** = S02's file and slice ("Siren", 0.5-1.3 s, 6f fade out, high-pass 300 Hz) | f140 |
| SFX | **S15** "23 Whip Hit" (only 0.2 s audible) | starts f161 (2f before the whip midpoint f163) |
| Music | no MU cue; "no sound on the burst cuts; the music carries them"; the burst has voice ("And every GTA since"), so normal ducking | Tesseract |
| Fonts | Inter Medium 500 (T1, T4, L10 tags) | kit |
| Kit | `rc-l10-tag`, T1 `captionPlan`, M1 `starsPopIn` (preset hero), T4 `spreadWords`, X9 `sirenWash`, X5 `blindsClose` | `assets/kit/` |

## 3. Tools and layer stack

Tesseract: every footage shot (13 shots in `tesseract_shots.json`), the X1 cuts, the X8 whip (f160-166), grades, all audio.
HyperFrames (this overlay), top to bottom:
1. `#b14-x5` X5 slats (z 50), f180-188 closing, shut f188 -> end of tail handle (opaque ink black)
2. `#b14-t4` T4 phrases (z 21): "The wanted stars." top-left, "The sirens." centre-right, "The running." bottom-left
3. `#b14-cap-1` T1 "that chase." (z 20)
4. `.rc-l10-tag` year tags (z 6)
5. `#b14-stars` M1 six stars, 120 px, centred (z 4)
6. `#b14-x9` X9 siren wash, Overlay blend 35% (z 2), f140-143
7. `#b14-x9-plate` RT3 embed (z 1), f140-143 only (makes the overlay opaque there so the Overlay blend has a picture)
8. transparent: Tesseract footage

## 4. Step-by-step build (beat frames; seconds from the beat start)

| Beat f | Overlay (HF) | Footage (Tesseract) |
|---|---|---|
| -6..12 | tag "2001" (also in the head handle) | R14.1 a f0-6, b f6-12 (hard cuts) |
| 12 / 24 / 36 / 48 (0.4/0.8/1.2/1.6 s) | tags "2002" / "2004" / "2008" / "2013", hard cut with their clips | R14.2, R14.3, R14.4, R14.5, 2 x 6f each |
| 60 (2.0 s) | tags off (the burst ends) | R1.3 GTA 5 chase, push 100 -> 104% linear to f133 |
| 62 (2.07 s) | T1 "that chase." hard cut in on "that" (+0.14f) | |
| 96 (3.2 s) | T1 out; T4 "The wanted stars." fades in 4f + 12 px drift up (opacity linear, drift power3.out); M1 star 1 pops | |
| 96..111 | stars pop 3f apart, each scale 0 -> 100% over 3f, power3.out, no overshoot; 6th lands f114 = "stars." | |
| 133 (4.43 s) | stars off with the cut; T4 "The sirens." fades in centre-right | hard cut to RT3 police lights (no push, grade none) |
| 140 (4.67 s) | X9: RT3 embed on; siren red #E3262E 35% Overlay f140-141, siren blue #2D5BFF f142-143; off f144 | RT3 continues (same source time as the embed) |
| 160-166 | (text stays, screen-space) | X8 whip: 6f horizontal move, 80 px directional blur; cut RT3 -> R14.5 at the midpoint f163 |
| 162 (5.4 s) | T4 "The running." fades in bottom-left | R14.5 escape, push 100 -> 104% |
| 180-188 | X5 blinds CLOSE: 12 ink-black slats rotate +90 -> 0 deg over 8f (constant 11.25 deg/f), above all text | |
| 188 -> +6 | slats shut (B15 opens them) | escape continues under the slats through the handle |

## 5. On-screen text

| Text (exact) | Style | Position / size | On / off (beat f) |
|---|---|---|---|
| 2001 / 2002 / 2004 / 2008 / 2013 | L10 year tag ("the only text during the burst; keep them tiny") | top-left (96, 54), Inter Medium 22 px, white + soft shadow | -6..12 / 12..24 / 24..36 / 36..48 / 48..60 |
| that chase. | T1 | x 960, y 620, Inter Medium 46 px | 62 -> 96 |
| The wanted stars. | T4 | top-left: x 96, y 160 (centre), Inter Medium 44 px | 96 -> slats (188) |
| The sirens. | T4 | centre-right: right edge 1824, y 540 | 133 -> slats |
| The running. | T4 | bottom-left: x 96, y 920 | 162 -> slats |
| (M1) six stars | M1 | 6 x 120 px + 24 px gaps, row centred (960, 540), x 540-1380, y 480-600 | 96 -> 133 |

T-style featured: T4 (rotation p.13 "B14 T4"; B13 = T3 -> T6, B15 = T1 -> T9). M1 and M5 (X9) are the motif payoffs.

## 6. Audio (Tesseract places them from `cues.json`)

| Cue | Event (beat f) | Placement | Level |
|---|---|---|---|
| S14 (S02's file and slice) | `sirens` = 140 | start on "sirens" (same frame as the X9 wash) | -14 dBFS |
| S15 "23 Whip Hit" | `whip_mid` = 163 | start 2f before the whip's midpoint (f161) | -12 dBFS |
| Burst cuts f0-60 | - | no SFX: "the music carries them" | - |

If it feels busy, cut S15 before S05 (plan p.38 order: S12, then S15, then S05).

## 7. Mistakes to avoid

- No captions during the burst: the year tags are the only text there, and they stay tiny (22 px).
- The siren wash only on "sirens" (motif M5): no other red/blue flashes; no glitch (not a bug beat).
- The T4 phrases never fade out: they stay until the slats close.
- Keep the RT3 shot exactly as specified (source_in_s 1.0, full frame 100%, grade none) or update the embed, else the 4 wash
  frames pop against the Tesseract shot.
- Stars: no overshoot (T7's chip is the only bouncy animation); they leave with the cut to the police lights.

## Interpretations / conflicts

1. **C15:** On screen lists T1 "And every GTA since / is built around / that chase." but Watch out says "the year tags are the
   only text during the burst" (p.26): the specific Watch out wins inside the burst (f0-60), so only "that chase." is shown
   (f62). The burst is 10 x 6f ("5-6f each" in the beat build) rather than the L10 library's "hard cut on the music's eighth
   notes" (8.2f at 110 BPM); beat build (priority 2) over library (priority 4).
2. **X9 over Tesseract footage:** an Overlay layer over transparency renders as a flat tint in an alpha MOV
   (KIT_transitions X9 caveat). The overlay therefore carries an embedded copy of RT3 for exactly the four wash frames (f140-
   143), frame-locked to the Tesseract shot (media start 1.0 + 7/30 = 1.2333 s; verified on snapshots by the stand-in's burned
   timecode: 1.233 ... 1.333 then the Tesseract frame 1.367).
3. **X9 colour timing:** red on f140-141, blue on f142-143, both at 35% Overlay (kit choice for the blue: the plan gives 35% once
   for the whole 4f overlay).
4. **X8 whip** is Tesseract's (toolchain p.3): this overlay keeps the text still (screen space) during the whip; direction
   "left" and the cut at the midpoint f163 are choices (plan gives 6f + 80 px blur only).
5. **Stars leave at the cut to RT3 (f133):** the plan ties them to "The wanted stars." over R1.3; only the T4 phrases are told
   to stay until the beat ends.
6. **"The sirens." centre-right** = right-aligned to the title-safe edge (1824) at y 540; "top-left" y 160 and "bottom-left"
   y 920 are the kit's T4 presets (inside title-safe).
7. **RT3 has no push** (30f of constantly flashing lights is not a held shot); R1.3 and the escape push 100 -> 104%.
7b. **T4 exit:** the T4 library ends with "all leave together with a 4f fade" (p.12, priority 4), the B14 build says each
   phrase stays "until the beat ends" (p.26, priority 2): no fade-out; the X5 slats close over the three phrases (f180-188),
   as the storyboard says ("all three T4 phrases stay until the slats close").
8. **`check` warnings weighed:** `text_below_floor` (22 px tags: the plan's explicit L10 size), `line_unread` "last line"
   (this is a segment, not the end of the film; the phrases stay to the slats as the plan says),
   `timeline_track_too_dense` (Studio lane cosmetics for the five tags).

## Pending real footage

- All 13 Tesseract shots: `source_in_s` values in `tesseract_shots.json` are stand-ins; pick two different fast chase moments
  per game for the burst, a centre that stays readable under the six stars for R1.3, and the car breaking away for the
  escape (R14.5 or R14.6).
- **RT3:** if the real clip's `source_in_s` changes, update `#b14-x9-plate` `data-media-start` (= source_in_s + 0.2333) and keep
  the shot unpushed and ungraded (or apply the same push/grade to the embed).
- Year tags assume the burst cuts land on f12/24/36/48/60; if the editor moves a burst cut, move the matching tag boundary.
- The B16 rewind (b16-bug-origin) re-uses these in-points: keep `tools/make_rewind.py` there in sync.
- Re-sync and re-render: `python3 ../../tools/sync_footage.py .` then the render command below.

Render: `npx --yes hyperframes@0.9.52 render . --format mov --workers 1 -o ../../05_GFX/renders/b14-since.mov`
