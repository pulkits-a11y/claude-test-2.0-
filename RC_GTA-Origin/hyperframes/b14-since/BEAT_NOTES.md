# B14 Every GTA since: beat notes (b14-since)

## v02 (REVISION_v02.md, client notes on v01): what changed

Beat **177f** (was 188), composition **189f**, root `data-duration="6.3000000"`. Frames below are v02 beat frames (local =
beat + 6). Everything after this section is the v01 record (v01 frames, Inter fonts). Still a transparent overlay over
Tesseract's footage, except the four X9 frames and the shut slats.

| What | v01 | v02 | Why (note / rule) |
|---|---|---|---|
| Timing | 188f; "that" 62, "The" 96 / 133 / 162, "sirens" 140 | 177f; "that" 59, "The" 91, "wanted" 96, "stars." 108, "The" 126, "sirens." 132, "The" 153, "running." 157 | note 10 |
| L10 burst (Tesseract) | 10 x 6f, f0-60 | 9 x 6f + 1 x 5f, f0-59, ending on "that" (the cut to R1.3 lands on the word); static framing (6f clips, no punches) | re-time, rule E |
| Year tags | 2001 -6..12 ... 2013 48..60 | 2001 -6..12, 2002 12-24, 2004 24-36, 2008 36-48, 2013 48-59 (Coolvetica 22 px, hard cuts with their clips) | re-time, note 12 |
| T1 | "that chase." chunk, f62-96 | word by word: "that chase." (that 59, chase. 66) -> out on "The" 91. Still no captions during the burst (C15) | note 11, rule A |
| M1 hero stars | from "The" f96 | from "The" f91: six stars 120 px centred, pop 3f apart (easeOutQuart), all in by f109 ("stars." 108); out with the cut to the police lights f126 | re-time |
| T4 | three phrases fading in (linear), all staying to the slats | word by word, max 2 words, each group in its spot and replacing the previous one: "The" (top-left) 91 / "wanted stars." (top-left) 96 / "The sirens." (centre-right) 126 / "The running." (bottom-left) 153 -> stays until the slats close (note 11 overrides the plan's "each phrase staying until the beat ends") | note 11, rule A |
| X9 on "sirens" | f140-143, embed media 0.4333 | f132-135 (red 2f, blue 2f, hard), over the embedded R1.6 plate at media 0.4000 (= shot in 129.5 s + 6f, working clip in 129.3) | re-time |
| R1.3 chase (Tesseract) | f60-133, push 100 -> 104% linear | f59-126, framing v2: punch-in 112 -> 101% in 10f (easeOutExpo) on "that", then push 101 -> 107% (easeInOutSine) | rule D |
| Police lights R1.6 (Tesseract) | f133-163, no push | f126-154, framing v2: punch-in 110 -> 100% in 6f (easeOutExpo) on "The", **exactly 100% on f132-136** (the four wash frames, where the overlay embeds the shot at 100%), then push 100 -> 104% (easeInOutSine) into the whip | rule D (keeps the X9 embed frame-exact) |
| X8 whip (Tesseract) | f160-166, mid 163 | f151-157, mid 154 (cue `whip_mid` = 154, S15 starts f152) | re-time |
| Escape R14.5 (Tesseract) | f163-188, push 100 -> 104% linear | f154-177 (+ tail handle under the slats), framing v2: the alternate move, zoom-out 110 -> 101% (easeInOutSine) | rule D |
| X5 close | f180-188, constant speed | f169-177, easeInQuart (kit v02), shut from f177 through the tail handle | rule C |

`cues.json` = `{"sirens": 132, "whip_mid": 154}`. `tesseract_shots.json`: all 13 shots re-timed with framing v2 keys (source,
in-points and crops unchanged). `footage.json`: the R1.6 embed note updated (media start 0.4000 on f132). B16's
`tools/make_rewind.py` reads this file (re-run in v02 after these shots were final).

Checks: `check --json` 0 errors (warnings: 22 px year tags below the 28 px phone floor = the plan's L10 size, `line_unread`
on "The" 5f and on "The running." as "the film's last line", track density). Snapshots `review/v02/a/` + `sheet_a.jpg`
(magenta = transparent): tags, every caption/T4 word, the star pops, the four wash frames, the slats. Render
`05_GFX/renders/b14-since.mov`: ProRes 4444, 1920x1080, 30 fps, **189 frames**, `yuva444p12le` (ffprobe, counted).

---


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
| B-roll (Tesseract + 4f embed) | police lights: **R1.6** (SUBSTITUTE for the missing RT3, see Substitutions) | f133-163; ALSO embedded in this overlay for f140-143 under the X9 wash (`assets/footage/R1.6.mp4`, same crop) |
| B-roll (Tesseract) | **R14.5** escape shot (R14.6 unusable: permanent "Grand Theft Auto" logo + burned-in commentary) | f163-188 (+ tail handle) |
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
7. `#b14-x9-plate` R1.6 police-lights embed (z 1), f140-143 only (makes the overlay opaque there so the Overlay blend has a picture)
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
| 133 (4.43 s) | stars off with the cut; T4 "The sirens." fades in centre-right | hard cut to the police lights (R1.6 for RT3; no push, grade none) |
| 140 (4.67 s) | X9: R1.6 embed on; siren red #E3262E 35% Overlay f140-141, siren blue #2D5BFF f142-143; off f144 | the police lights continue (same source time as the embed) |
| 160-166 | (text stays, screen-space) | X8 whip: 6f horizontal move, 80 px directional blur; cut R1.6 -> R14.5 at the midpoint f163 |
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
- Keep the police-lights shot exactly as specified (R1.6, source_in_s 129.5, crop 1264:711:300:289, full frame 100%, grade none) or update the embed, else the 4 wash
  frames pop against the Tesseract shot.
- Stars: no overshoot (T7's chip is the only bouncy animation); they leave with the cut to the police lights.

## Interpretations / conflicts

1. **C15:** On screen lists T1 "And every GTA since / is built around / that chase." but Watch out says "the year tags are the
   only text during the burst" (p.26): the specific Watch out wins inside the burst (f0-60), so only "that chase." is shown
   (f62). The burst is 10 x 6f ("5-6f each" in the beat build) rather than the L10 library's "hard cut on the music's eighth
   notes" (8.2f at 110 BPM); beat build (priority 2) over library (priority 4).
2. **X9 over Tesseract footage:** an Overlay layer over transparency renders as a flat tint in an alpha MOV
   (KIT_transitions X9 caveat). The overlay therefore carries an embedded copy of the police-lights shot (R1.6 for RT3) for exactly the four wash frames (f140-
   143), frame-locked to the Tesseract shot (R1.6 source 129.5 + 7/30 = 129.733 s = working clip 0.4333 s, same crop; footage pass
   snapshots `review/footage-pass/f146..f149`: red/blue wash over the two LSPD cruisers, transparent again on f144).
3. **X9 colour timing:** red on f140-141, blue on f142-143, both at 35% Overlay (kit choice for the blue: the plan gives 35% once
   for the whole 4f overlay).
4. **X8 whip** is Tesseract's (toolchain p.3): this overlay keeps the text still (screen space) during the whip; direction
   "left" and the cut at the midpoint f163 are choices (plan gives 6f + 80 px blur only).
5. **Stars leave at the cut to the police lights (f133):** the plan ties them to "The wanted stars." over R1.3; only the T4 phrases are told
   to stay until the beat ends.
6. **"The sirens." centre-right** = right-aligned to the title-safe edge (1824) at y 540; "top-left" y 160 and "bottom-left"
   y 920 are the kit's T4 presets (inside title-safe).
7. **The police-lights shot has no push** (30f of constantly flashing lights is not a held shot); R1.3 and the escape push 100 -> 104%.
7b. **T4 exit:** the T4 library ends with "all leave together with a 4f fade" (p.12, priority 4), the B14 build says each
   phrase stays "until the beat ends" (p.26, priority 2): no fade-out; the X5 slats close over the three phrases (f180-188),
   as the storyboard says ("all three T4 phrases stay until the slats close").
8. **`check` warnings weighed:** `text_below_floor` (22 px tags: the plan's explicit L10 size), `line_unread` "last line"
   (this is a segment, not the end of the film; the phrases stay to the slats as the plan says),
   `timeline_track_too_dense` (Studio lane cosmetics for the five tags).

## Footage used (all Tesseract-owned: `tesseract_shots.json` carries `source`, `source_in_s`, `crop`)

| Shot | R-ID | In (s, original) | Beat f | What it shows | Link |
|---|---|---|---|---|---|
| burst 1 "2001" | R14.1 | 60.3 | 0-6 | GTA 3: the Cheetah drifting past an LCPD cruiser in the rain | https://www.youtube.com/watch?v=6lSy09Uruz0&t=60 |
| burst 2 "2001" | R14.1 | 200.8 | 6-12 | GTA 3: the battered Cheetah smashing through the pursuers (5-6 stars) | https://www.youtube.com/watch?v=6lSy09Uruz0&t=200 |
| burst 3 "2002" | R14.2 | 168.0 | 12-18 | Vice City: the police helicopter swooping over Tommy | https://www.youtube.com/watch?v=X4mB41ybSN4&t=168 |
| burst 4 "2002" | R14.2 | 274.0 | 18-24 | Vice City: a VCPD cruiser lunging in, lights on | https://www.youtube.com/watch?v=X4mB41ybSN4&t=274 |
| burst 5 "2004" | R14.3 | 64.0 | 24-30 | San Andreas: CJ tearing down a street on a stolen police bike | https://www.youtube.com/watch?v=obxIhv9YhKY&t=64 |
| burst 6 "2004" | R14.3 | 345.0 | 30-36 | San Andreas: CJ fleeing on a sports bike, stars up | https://www.youtube.com/watch?v=obxIhv9YhKY&t=345 |
| burst 7 "2008" | R14.4 | 124.6 (crop 1116:628:400:0) | 36-42 | GTA 4: LCPD cruiser, light bar on, on the fleeing car as a gunman leans out | https://www.youtube.com/watch?v=WNZMK7KPZWs&t=124 |
| burst 8 "2008" | R14.4 | 155.2 (crop 1116:628:0:0) | 42-48 | GTA 4: POLICE cruiser door to door with the fleeing car | https://www.youtube.com/watch?v=WNZMK7KPZWs&t=155 |
| burst 9 "2013" | R14.5 | 429.6 (crop 1636:920:142:78) | 48-54 | GTA 5: the getaway car tearing down a dirt road at night | https://www.youtube.com/watch?v=vUndgwBLKeY&t=429 |
| burst 10 "2013" | R14.5 | 434.2 (crop 1636:920:142:78) | 54-60 | GTA 5: the getaway car flying off a jump | https://www.youtube.com/watch?v=vUndgwBLKeY&t=434 |
| GTA 5 chase under M1 | R1.3 | 107.0 | 60-133 | GTA 5 five stars: the supercar flat out on the coast highway, passing an LSPD cruiser with lights on (~108.5-109.5); clear centre under the stars | https://www.youtube.com/watch?v=NcTdBgA3Bkg&t=107 |
| police lights | R1.6 (for RT3) | 129.5 (crop 1264:711:300:289) | 133-163 | San Andreas: two LSPD cruisers side by side in pursuit, red/blue light bars lit | https://www.youtube.com/watch?v=flgIZbQHwN8&t=129 |
| escape | R14.5 | 240.6 (crop 1636:920:142:78) | 163-188 | GTA 5: the getaway car drifting along the beach and away, sand flying | https://www.youtube.com/watch?v=vUndgwBLKeY&t=240 |

Crops: R14.4 is a 2276x720 Rockstar Editor movie with "R*" and "ROCKSTAR GAMES / Social Club" marks at y 630-680 (16:9 crops end
above them); R14.5 is letterboxed with the uploader's "RaveNN" mark in the top bar (crop = the picture rows 78-998); R1.6's crop drops
the game's radio subtitle, HUD, minimap and zone name. Game HUD inside the other shots stays as is. Moments B1 already uses (R14.1
44.0-45.5, R14.4 64.0-65.5, R1.3 46.0-47.4) are not repeated.

## Substitutions

* `SUBSTITUTE (Rule 5): R1.6 The Biggest Police Chase in GTA San Andreas History! (100 Cops vs. 1 S... [flgIZbQHwN8] @ 02:09.5-02:10.5 for RT3 (police lights flashing: missing).` R5.4 (FOOTAGE_PASS's first example) was rejected: its night light-bar shots carry LSPDFR mod UI (death-report feed, radio widget) and the clean side view prints a real sheriff's name on the door; R14.6 carries a permanent logo; R1.3's lights are hard to read in daylight. The R1.6 shot is daylight: the light bars read, but it is not a night "lights flashing" close-up like RT3.
* R14.5 note (not a substitution): the plan's GTA 5 "Lose the cops" clip is a cinematic short film with no police on screen; its getaway driving is used for the two "2013" burst clips and the escape, as the plan asks.

## Still pending

* RT3 itself if the user uploads it (then: rid RT3 + its source/in-point in `tesseract_shots.json`, the embed `#b14-x9-plate` src and
  `data-media-start`, `footage.json`, re-render this overlay and re-run B16's `tools/make_rewind.py`).
* Year tags assume the burst cuts land on f12/24/36/48/60; if the editor moves a burst cut, move the matching tag boundary.
* B16's VHS rewind mirrors these shots (its `tools/make_rewind.py` reads this file): re-run it after any change here.

Render: `npx --yes hyperframes@0.9.52 render . --format mov --workers 1 -o ../../05_GFX/renders/b14-since.mov`
