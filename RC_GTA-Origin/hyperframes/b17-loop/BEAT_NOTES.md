# B17 The loop - `b17-loop` (beat 196f = 6.533 s incl. the 46f logo tail; composition 208f with 6f handles)

## v04 (REVISION_v04.md, Frame.io review of v03): what changed

Same beat, composition, words, lockups and cues as v03. The overlay (lockups, stars, "now?", logo, X4) is unchanged; the
kit v04 adds its static scanlines to the black screen (f129-186).

| What | v03 | v04 | Why (note) |
|---|---|---|---|
| Trailer 1 opening (Tesseract, f0-100) | the madebyajit fan edit (pink grade, halftone texture), 2 shots | **Rockstar's official GTA VI Trailer 1** from the client's Drive library (`04_Broll/_originals/Drive2/Grand Theft Auto VI Trailer 1.mp4`, Drive id 1mkXZU995el2fMTAbhDtAaqTbW7NiL6nn, 1920x1080 30 fps, R17.1), whose opening is Lucia in custody: **f0-40 @ 6.60-7.93 s** Lucia in an orange INMATE jumpsuit at a barred window over the prison yard, turning her head (the L2 bars slide in over it, 8f); **f40-61 @ 8.55-9.25 s** the parole officer talking to her, her INMATE back in frame; **f61-100 @ 9.683-10.95 s** Lucia facing camera in the jumpsuit ("already caught."). Full 16:9 picture under the bars (faces inside the band), grade `game` (no neutralize), one band push 100 -> 104% eased split at the cuts | #20 |

Mock-ups `review/v04/mock/` (the v03 overlay composited over the new source frames with the bars): the lockups at y 820
sit on her jumpsuit / the desk, her face stays clear. Checks: `check --json` 0 errors. Snapshots `review/v04/` (black screen
with scanlines, logo). Not rendered.

---

## v03 (REVISION_v03.md, client notes on v02): what changed

Same beat (186f), composition (198f), words and cues (`{"now": 129, "music_stop": 141, "logo_in": 141, "final_hit": 161}`)
as v02; only what the notes ask changed. Frames = beat frames (local = beat + 6). Transparent over the Tesseract shots
(f0-129), opaque from the cut to black on "now?" (f129) as before.

| What | v02 | v03 | Why (note) |
|---|---|---|---|
| Captions | T1 word by word on the low line (y 860) + T2 "chasing who" / "now?" (140 px, y 925) | v03 lockups (ref 1; every word a hard cut on its frame): "And [GTA 6?]" f1-36 and "It opens with [Lucia] already caught." f36-97, ink centre **y 820** (centring would cover Lucia's face in the upper band; mock-ups `review/v03/mock/`: the lockups sit on her shirt / the yard, her face stays clear); "So who's chasing who" (one centred line) f97-129 over the chase cuts; **"[now?]*"** alone f129-169: Coolvetica Italic 170 px, ink centre y 960 (clear of the logo's bottom tips at 115%, checked on f160 / local 166), starred = pop + blur-in on its frame (the cut to black) | notes 11, 16, 17 |
| T10 break on "now?" | inside the T2 keyword | kept: `T.glitch` on `#b17-key`, a span inside the lockup's keyword word; slices re-cut for the 170 px row (cap region 33-147 px, cuts at 71 / 109 px), seed 8, 6f, no settle, with the X4 tear (8f, seed 8) at f161, black from f169 | (unchanged look) |
| Tesseract framing | band 112 -> 101% punch-in + 101 -> 107% push; chase cuts: punch-in / push 106% / accelerating push 110% | v01's: one band push 100 -> 104% across the Trailer 1 opening (f0-100), eased (easeInOutSine), split at the client clip's own cut f10 (shot 1: 100 -> 100.1%, shot 2: 100.1 -> 104%; anchor kept at the band's top edge); chase cuts static 100% | note 13 |
| Logo push 100 -> 115% (f141-161) | | unchanged (the plan's move) | |
| M1 stars (pop + blink, top right) | | unchanged (note 5 is B14's stars) | |

The madebyajit Lucia shots (client clip, credit madebyajit) stay as they were (sources, in-points, crops, `neutralize`
grade). `x4_still.sh`'s capture mode now hides `.rc-lk` (was `.rc-cap`); the X4 still `assets/x4/b17-old.png` is unchanged
(the logo frame at 115% did not change).

Checks: `check --json` **0 errors** (warnings: nested lockup markup, frame 0 transparent by design, `line_unread` on "So
who's chasing who" and "now?" as "the film's last line": the voice timing). Snapshots `review/v03/` (26 frames + `sheet.jpg`,
magenta = transparent: every lockup word, the "now?" pop, the logo push, the X4 + T10 frames, the black tail) and
`review/v03/mock/` (the overlay composited over the shots' Tesseract working copies: the Lucia band and the chase cuts).
Not rendered (v03: snapshots only).

---

## v02 (REVISION_v02.md, client notes on v01): what changed

Beat **186f** (was 196; incl. the 45f logo tail after "now?"), composition **198f**, root `data-duration="6.6000000"`. Frames
below are v02 beat frames (local = beat + 6). Everything after this section is the v01 record (v01 frames, Inter fonts,
the R17.1 stand-in).

**Substitution (client note 9):** the Trailer 1 opening (the R17.1 stand-in `trailer1-band`) is replaced by the client's clip
`04_Broll/_originals/Drive2/Video by madebyajit [0-29s].mp4` (1500x1078, 25 fps, a fan edit of GTA 6 Trailer 1's opening;
**credit: madebyajit, Instagram**). Clip map (frames at 25 fps): n0-11 the guard's face, n10-54 the prison yard behind the
chain-link fence with the guard in the white "Let Freedom Reign!" shirt in the right foreground and Lucia walking toward camera
in the background, n55-131 Lucia walking toward camera (medium), n132+ another scene (never used, nor the clip's "madebyajit"
end card). Two Tesseract shots (same source, `grade: "neutralize"` so the assembly tones down the heavy pink grade):

| Shot | Beat | Source (s) | Crop | Framing v2 (anchor = the band's top edge 960, 138) | Why |
|---|---|---|---|---|---|
| `B17-trailer1-band` | 0-10 | 1.86-2.16 (n46-54: the guard + Lucia walking in the yard) | `1500:844:0:0` (16:9, full width, top rows) | 112% -> 101% over 10f, easeOutExpo (punch-in on the cut from B16's black) | 16:9 so the L2 bars visibly slide in over the picture (8f, as v01). In-point: at 1.0-1.8 s the guard's white shirt fills the T1 caption spot (white on off-white is unreadable); from 1.86 s "And" / "GTA 6?" sit on the dark yard left of it (mock-ups checked) |
| `B17-trailer1-band-2` | 10-100 | 2.22-5.22 (n56-130: Lucia walking toward camera) | `1500:628:0:0` (2.39:1, full width, top rows) | 101% -> 107%, easeInOutSine | in this edit Lucia's head touches the top of the frame: a 16:9 crop puts her eyes on the top bar's edge; a crop wider than 16:9 is fitted by the assembly exactly into the band (1920x804 at y 138), so her whole head stays in (face at band y ~290-540). Bars already in (an L2 shot ends where it starts) |

No stretching (16:9 = 1500x844, 1.7773; the band crop 1500x628 = 2.389:1, the band's own aspect). "It" (beat 36) reads as the
trailer: Trailer 1 stays on screen through "It opens with Lucia already caught." (Accuracy p.39). No voice actor named or implied.

| What | v01 | v02 | Why (note / rule) |
|---|---|---|---|
| Timing | 196f; "who's" 106, "chasing" 116, "now?" 137, end of "now?" 150 | 186f; "And" 1, "GTA" 7, "It" 36, "Lucia" 54, "caught." 74, "So" 97, "who's" 100, "chasing" 109, "who" 123, "now?" 129, end of "now?" 141 | note 10 |
| T1 | 4 chunk clips (low line y 860) | word by word, max 2 words, low line: "And" 1 / "GTA 6?" 7 / "It opens" 36 / "with Lucia" 48 / "already caught." 62 / "So who's" 97 -> out on "chasing" 109. Grouping note: the kit's split inside the plan chunk "It opens with" leaves "with" alone; it goes with the word after it ("with Lucia", rule A) | note 11, rule A |
| T2 | "chasing who" + "now?" on screen together; the pair dropped 45 px on the cut (an `ease: 'none'` tween) | word by word, max 2: "chasing who" (lead, `--rc-y` 880, over the chase shots) 109 -> "now?" alone (keyword blur punch 30 -> 0 px, 108 -> 100%, 6f easeOutExpo, on black at `--rc-y` 925 = the v01 dropped line, clear of the logo's bottom tip at 115%) 129; no drop tween any more | note 11, rules A, C |
| X4 + T10 final break | f170: X4 6f + T10 6f, then black f176 | f161: **X4 8f, seed 8, still mode = B8's v02 break** (coordinator: B8 and B11 moved to the kit's 8f; B17's final break echoes B8's) on the logo, T10 on "now?" 6f (seed 8 = B8's slice pattern, hard per-frame cuts, breaks apart, no settle; its last broken frame holds while the tear finishes), then black from f169 (the logo and the keyword run to f169) | re-time, plan "B17 echoes B8" |
| M1 stars | pop on "GTA", blink to f107 | pop on "GTA" (7), blink (hard) to the first chase cut f100; row centred on (1700, 80) on the top bar (C34) | re-time |
| Chase shots (Tesseract) | f107-117-127-137, static 100% | chase-1 R17.2 @ 7.2 f100-109 (9f, punch-in 112 -> 100% easeOutExpo, on "who's") / chase-2 R17.4 @ 47.2 f109-119 (push 100 -> 106% easeInOutSine, on "chasing") / chase-3 R17.2 @ 11.9 f119-129 (push 102 -> 110% easeInQuart, accelerating into the hard cut to black on "now?") | rules D, E |
| Logo end card (R17.4, HF) | f150-176, push 100 -> 115% over 20f | f141-169 (local 147-175): the same push, log-space easeInCubic with per-frame motion blur, landing on the final hit f161, torn f161-168 | re-time |
| X4 still | `assets/x4/b17-old.png` at local 176 | re-made from B17's own frame by `x4_still.sh` at local 167 (FRAME updated): identical pixels (same logo frame at 115%, no text) | re-time |

`cues.json` = `{"now": 129, "music_stop": 141, "logo_in": 141, "final_hit": 161}`. `footage.json`: only R17.4's end card is
synced here; the client clip is Tesseract-owned.

Checks: `check --json` 0 errors (warnings: frame 0 transparent by design, `line_unread` on "And" 6f and on "now?" as "the film's
last line", nested T2 markup, track density). Snapshots `review/v02/a/` + `sheet_a.jpg` (magenta = transparent): every caption
word, star pops, the cut to black, the keyword blur, the logo push, the tear + T10 frames (`review/v02/x4/`, 8f), the black tail; plus a mock-up of the
overlay on the cropped client clip (band, captions legible over the dark yard and Lucia's shirt). Render
`05_GFX/renders/b17-loop.mov`: ProRes 4444, 1920x1080, 30 fps, **198 frames**, `yuva444p12le` (ffprobe, counted); transparent
over the Tesseract shots (beat f0-129), opaque from the cut to black on "now?" (f129) to the end.

---


Plan p.27-28 (B17), p.39 (accuracy: B17 wording, official GTA 6 footage only, no voice actor), p.16 (X4), p.12 (T2,
T10), p.17 (M1), p.36-38 (MU8, S18, S19). Storyboard B17. Bug beat (final X4; echoes B8).
Render: `05_GFX/renders/b17-loop.mov` (ProRes 4444): transparent over the Tesseract shots (beat f0-137), opaque from
the hard cut to black on "now?" (f137) to the end.

## 1. What the viewer sees
Letterbox bars slide in over the opening of GTA 6 Trailer 1, Lucia in custody (Tesseract), while five wanted stars
pop in and blink at the top right and T1 asks "And GTA 6? / It opens with / Lucia already caught.". On "who's" three
fast official GTA 6 chase cuts (10f each): a shooter leaning out of a sedan with police closing in, a police car
drifting round a corner after a green sports car, a pursuing police car slamming into a pole. On "now?" hard cut to
black: "chasing who now?" with "now?" blurring in, the official GTA VI logo end card appears and pushes in to 115 % with
motion blur, the logo tears apart (X4) as "now?" breaks apart (T10), then black, riding the hit's decay.

## 2. Assets
* Tesseract shots (`tesseract_shots.json`): R17.1 Trailer 1 opening (STAND-IN, see BLOCKING), R17.2 x2 and R17.4
  (chase cuts; R17.2 substitutes for the missing R17.3).
* HyperFrames: R17.4 end card (`assets/footage/R17.4.mp4`, the official logo, never drawn), M1 stars (kit `hud`
  preset), T1, T2 pair with the T10 glitch inside the keyword, X4 (`X.tear`, still mode, seed 8 = B8's) with
  `assets/x4/b17-old.png` (this composition at local 176 without text or tear, re-made from the real end card),
  `X.zoom` (push 100 -> 115 % over 20f, `power2.in`, media-treatment motion blur).
* Audio (Tesseract): MU8 stop, S18 riser, S19 (= S08's files).

## 3. Tool and layer stack
Tesseract (under): L2 band f0-107 (bars 138 px, slide in 8f), chase cuts f107-117-127-137 (full frame, X1).
HyperFrames (top -> bottom): z40 T1 (y 860) and the T2 pair (`--rc-y` 880, dropping 45 px on the cut to black) · z30
X4 canvas (local 176-181) · z20 M1 stars (row centred on x 1700, y 80; local 0-113) · z3 `#b17-world` > R17.4 end card
(local 156-182) · z1 ink black (local 143-208). Transparent elsewhere.

## 4. Step-by-step build
1. Tesseract shots: `source` = the originals below (R17.1: the placeholder), `source_in_s` in the original's seconds.
2. M1: stars pop in on "GTA" (3f each, 3f apart), then blink 6f on / 6f off until the first chase cut (local 113).
3. T1 chunks (kit `captionPlan`): "And GTA 6?" 7 · "It opens with" 44 · "Lucia already caught." 63 · "So who's"
   109-123 (local). T2: lead-in "chasing who" hard cut at local 123 (beat f117, the same frame as chase-2); keyword
   "now?" 6f blur-in + 108 -> 100 % on "now?" (local 143 = beat f137), where the picture hard-cuts to black and the pair
   drops 45 px (so "now?" stays clear of the logo's bottom tip at 115 %).
4. Logo: R17.4 end card from original 1:16.7 (logo settled, before the city fades in), plays local 156-182; push
   100 -> 115 % over 20f from local 156 (beat f150, end of "now?") to 176, accelerating, with motion blur.
5. Final hit (local 176 = beat f170): X4 tear on the logo (6f, seed 8) + T10 on "now?" (6f, seed 8, breaks apart, no
   settle); local 182 (beat f176) black to the end (logo tail 46f incl. this).

## 5. On-screen text (plan: "T1: And GTA 6? / It opens with / Lucia already caught. / So who's → T2: chasing who now?" + T10 on "now?")
| element | text | beat f |
|---|---|---|
| T1 | And GTA 6? | 1 |
| T1 | It opens with | 38 |
| T1 | Lucia already caught. | 57 |
| T1 | So who's | 103 |
| T2 lead-in | chasing who | 117 |
| T2 keyword (Instrument Serif Italic) | now? | 137 (blur-in), T10 break 170-176 |
No voice actor is named or implied anywhere.

## 6. Audio cues (`cues.json`)
`now` = 137, `music_stop` = 150 (MU8: the music stops dead at the end of "now?"), `logo_in` = 150 (S18 Riser Faster,
1.1 s, rising to -10 dBFS, its end on the logo hit), `final_hit` = 170 (S19 = S08's files, -4 dBFS, on the logo hit;
the tail rides its decay). No SFX before "now?" (silence by design).

## 7. Mistakes to avoid
* GTA 6 footage only from official uploads (R1.2, R17.2, R17.4, R17.6); never R1.1 or R17.5.
* Keep Trailer 1 on screen through "It opens with Lucia already caught." so "it" reads as the trailer (p.39).
* B8 and B17 must read as the same break: same X4 settings/seed, same T10 glitch family.
* Re-run `sh hyperframes/b17-loop/x4_still.sh` after any change to the end card window or framing.

## Footage used
| shot | R-ID | original | window (s) | shows | link |
|---|---|---|---|---|---|
| B17-trailer1-band (TS, f0-107) | R17.1 | STAND-IN `04_Broll/_placeholders/R17.1.mp4` | - | labelled stand-in (no original) | https://www.youtube.com/watch?v=QdBZY2fkU-0 |
| B17-chase-1 (TS, f107-117) | R17.2 | `04_Broll/_originals/B17/R17.2__Grand Theft Auto VI： An Extended Look ｜ Now Playing ｜ Netflix [uphThaa97ig].mp4` | 7.20-7.53 (shot 6.80-7.87) | gameplay chase: shooter leaning out of the player's sedan, a police car and a police SUV with lights closing in (game HUD: wanted stars, minimap) | https://www.youtube.com/watch?v=uphThaa97ig&t=7 |
| B17-chase-2 (TS, f117-127) | R17.4 | `04_Broll/_originals/B17/R17.4__Grand Theft Auto VI Launch Trailer [rz1B4B2yBZY].mp4` | 47.20-47.53 (shot 46.33-48.23) | a police car drifting round a street corner after the green sports car (trailer letterbox kept) | https://www.youtube.com/watch?v=rz1B4B2yBZY&t=47 |
| B17-chase-3 (TS, f127-137) | R17.2 | (as chase-1) | 11.90-12.23 (shot 11.63-12.80) | shot at from the player's convertible, a pursuing police car slams into a pole (sparks) | https://www.youtube.com/watch?v=uphThaa97ig&t=11 |
| logo (HF, f150-176) | R17.4 | `04_Broll/_originals/B17/R17.4__Grand Theft Auto VI Launch Trailer [rz1B4B2yBZY].mp4` | 76.70-77.57 (window 76.7-77.6) | the official GTA VI logo end card, static on the navy card (trailer letterbox bars kept, pushed out by the 115 % push) | https://www.youtube.com/watch?v=rz1B4B2yBZY&t=76 |

### Substitutions
* SUBSTITUTE (Rule 5): R17.2 Grand Theft Auto VI: An Extended Look | Now Playing | Netflix [uphThaa97ig] @ 00:07.2-00:07.5 for R17.3 (GTA 6 Trailer 2, not downloaded; official alternate listed by the plan, a police chase in gameplay)
* SUBSTITUTE (Rule 5): R17.2 Grand Theft Auto VI: An Extended Look | Now Playing | Netflix [uphThaa97ig] @ 00:11.9-00:12.2 for R17.3 (GTA 6 Trailer 2, not downloaded; a second, different chase moment for the third cut)
* Chase-2 stays on R17.4 as the plan lists it.

## BLOCKING (v01; resolved in v02 by the client's madebyajit clip, see the v02 section)
* **R17.1 (GTA 6 Trailer 1, Lucia in custody) is missing and no substitute exists.** Searched every shot of the
  official R17.4 launch trailer (30 cuts, 0-1:30), R17.2 "An Extended Look" (13 cuts) and R17.6 "Pre-Load Now" (sheets
  every 0.5 s): none shows Lucia in custody (no cell, booking room, prison clothing or police holding her). The labelled
  stand-in stays for `B17-trailer1-band` (f0-107). The B17 line ("It opens with Lucia already caught", Trailer 1 on
  screen so "it" reads as the trailer) needs R17.1: when it arrives, set that shot's `source` to the original and
  `source_in_s` to the first custody shot after any ident; nothing in this composition changes (it is transparent there).

## Pending / notes
* Built by the previous builder on stand-ins; this pass: real end card, T2 line lowered on the cut to black, X4 still
  re-made, chase shots and substitutions written, these notes. `music_stop`/`logo_in` both at f150 as the storyboard.
* check: 0 errors; warnings = frame 0 transparent (Tesseract footage underneath, by design), T1/T2 reading-floor
  heuristics (voice timing), nested T2 markup, track density.
* Render `05_GFX/renders/b17-loop.mov`: 208 frames (beat + 12), 1920 x 1080, 30 fps, yuva444p12le (ffprobe, counted).
* B17 alpha (rendered): local 0-142 transparent except captions/stars; opaque from local 143 (beat f137, the cut to black).
