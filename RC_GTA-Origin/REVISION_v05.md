# REVISION v05: "GTA Origin v04 — Edit Instructions for Claude" (16 pages, Nov 17 2026, @Raw Canvas)

Source (read your sections in full): `00_Brief/refs_v05/GTA_Origin_v04_Edit_Instructions_for_Claude.pdf`
(text: `00_Brief/refs_v05/GTA_Origin_v04_Edit_Instructions_for_Claude.txt`). What the doc's author saw in v04 at
each of its timestamps: `00_Brief/refs_v05/v04_preview_at_doc_timestamps.jpg`.

The doc is the newest instruction: where it conflicts with the plan or with v02-v04 notes, the doc wins (list in
section X). "Anything not mentioned stays as it is." The doc's own checklist (section 5) is the acceptance test.

## 0. Units, timing, ownership

* **Sizes**: the doc's px are for 1280x720. Our compositions are 1920x1080: **multiply every doc px by 1.5**
  (34-38 px -> 51-57 px, 110-140 -> 165-210, 220-400 -> 330-600, 4 px -> 6 px, 24 px glow -> 36 px ...).
* **Timestamps**: the doc's times are the v04 preview's. v05 timing (done, `tools/retime_v05.py`):
  * Cut A, 58 f: "Here's how. It's 1995 in" is gone; "...saved it." goes straight to "Dundee, Scotland." (doc beat 9,
    "Recommended"; section 5 counts it). v04 t >= 11.993 s -> v05 = t - 1.9333 s.
  * Cut B, 39 f: the silence after "Grand Theft Auto." is 0.386 s (was 1.686 s; doc: 0.4 s max). v04 t >= 56.00 s ->
    v05 = t - 3.2333 s.
  * GTA VI logo after "now?": 27 f (0.9 s, doc 75.5-77.0), hard cut to **B18 = NEW CTA end card, 75 f (2.5 s)**.
  * Edit: 2288 f = 76.267 s (story ends f2213 = 73.767 s). Map: `timing/v04_to_v05.json`. VO: `01_VO/VO_processed_v05.wav`,
    words `01_VO/VO_words_v05.json`, beat map `timing/beat_map.json` (v04's kept as `timing/beat_map_v04.json`);
    every beat's `words.json` is refreshed.
  * Because the cuts are whole frames, beats keep their local frames except: B2 168 f (v04 169: its last frame went
    with the old zoom-through into "Here's how"), **B3 now starts at "Dundee," (v05 local = v04 local - 57 f)**, B13 166 f
    (-39 f off the title hold), B17 168 f (-18 f off the logo tail), B18 new (b18-cta, scaffolded).
  * Not cut (the audio does not allow it; doc: "If a caption differs from what's actually said, go with the audio"):
    "In Nov 1997" (the VO says "in November 1997," continuously 50.23-51.75 s v04: no silent second to cut; the
    calendar rip fills it), the lone "Of" (caption fix only: "Of course," appears as one unit), Gary Penn (the narrator
    reads the quote; the 0.24 s before "it" is a normal breath).
* **Owners**: kit (`_kit`) / assembly (`tools/build_tesseract*.py`, audio, finish, preview) / lane 1 B1-B2 (the hook) /
  lane 5 B3-B4 + B18 CTA / lane 2 B5-B8 / lane 3 B9-B12 / lane 4 B13-B17.

## G. Global style system (doc section 2), applied everywhere

* **G1 Colour**: accent **#FF2E7E** only (word-entry flash, highlight pills, highlighter sweeps, glitch transitions);
  annotation yellow **#FFD23F** only for hand-drawn arrows / circles / underlines; danger red **#E3262B** only for the
  rubber stamp, the red cells of the 18->30 grid and the "cop" strike-through; siren flicker red #E3262B / blue
  #2E6BFF ("cops?", "chased.", "now?"). Text white #FFFFFF with a soft drop shadow **0 6px 18px rgba(0,0,0,.45)**.
  Any other red/yellow accent still in a beat (old highlights, glows) becomes pink or goes.
* **G2 Type, three tiers** (@1080):
  * A setup words: **Inter SemiBold**, **51-57 px**, sentence case, tracking 0 (doc: "Inter SemiBold or Helvetica
    Neue Medium"; this replaces Coolvetica Regular, see X5).
  * B key word (the punch word of a line): **Coolvetica Italic** (kept, "the video's identity"), **165-210 px**, as now
    with the period.
  * C hero (6-8 in the whole video): tier B font, or **Playfair Display Black** for years/dates/numbers, **330-600 px**,
    may run off-frame, behind the subject where there is one ([DEPTH]).
  * Quote/document: **Playfair Display Italic**, 90-120 px, in a highlight pill or on paper.
  * Pills: **Montserrat ExtraBold**, uppercase, tracking +2%, 66-78 px (name pill 45/30 px).
  * Fonts are in `06_Fonts/` (Playfair Display 900 + italics, Montserrat 700/800, VT323 for the VCR timestamp, Arimo =
    the Arial-metric face for the "dull." gag, Inter, Coolvetica).
* **G3 Layout**: the setup line sits directly above the key word, **left-aligned to it**, key word 3.2-3.8x the setup
  size ("small over big"). The block as a whole stays centred in frame wherever the doc does not place it
  (client v03: "keep the captions in the center as much as you can").
* **G4 Word entry (every caption word, except "dull.")**: f0 opacity 0, scale 112%, blur 9 px (6 px @720), colour
  #FF2E7E; f0-2 opacity -> 100%; f0-4 scale 112->100% and blur -> 0, cubic-bezier(0.2,0.8,0.2,1); f2-6 colour pink ->
  white; **key/hero words hold pink to f4, white by f8**. Whole life of a caption block: slow drift scale 100->104%.
  Exit: cut with the shot; if it must leave before the cut, 3-frame blur-out (0->12 px) + opacity 0. Never a slow fade.
  **f0 = the VO syllable onset (words.json), never early; 1-2 f late is fine.**
* **G5 Hero words (8)**: "Why" (B1, 450 px), "1995" (B2, Playfair Black 480 px), "broke." (B2, 390 px), "breaks."
  (B8, 450 px), "fun." (B10, 450 px), "30" (B12 counter, Playfair 330 px), "bug." (B16, 450 px), "now?" (B17, 330 px).
  Big but not counted: "18" (B4, Playfair 330 px), "NOV 1997" (B13 calendar, Playfair 300 px), "cops?" (240 px).
* **G6 Motion-graphics kit (doc 2.4; build once, reuse; identical every time it appears)**: highlight pill (box wipes
  0->100% from the left over 6 f, 15 px radius, #FF2E7E 92%, 4.5 px white inner stroke inset 9 px, outer glow 36 px
  40%, text typed on ~30 chars/s, exits with the pixel glitch); pink pixel-glitch transition (6-8 f, blocky #FF2E7E +
  white rectangles tearing horizontally, RGB split 9 px on f2-5); rubber stamp (#E3262B grunge, rough edge, -12 deg,
  scale 180->95->100% over 5 f, 1-frame white flash, 6 px camera shake 4 f); Win95-style error window (crisp, scalable,
  the dialog visible on the CRT at 8.0 s: "This program has performed an illegal operation and will be shut down.") +
  window-trail cascade (+36/+27 px per copy, 2-f stagger) + snap-shut (scale 0 over 3 f, staggered reverse order);
  card insert (white 15 px border, 2-4 deg tilt, shadow 0 27px 60px rgba(0,0,0,.5), on the same clip scaled 130%,
  blurred 60 px, darkened 50%; or on off-white paper; never on flat black); highlighter sweep (#FF2E7E 55%, multiply on
  light pages / screen on dark pages, wipes left->right over 8 f, 100->110% push on the page); hand-drawn annotation
  (yellow marker arrow / circle / underline, drawn on over 8-10 f by stroke trim, slight jitter); flash-star burst
  (white 4-point star flare at a cut, 4-6 f; only on the logo slams and "fun."); plus: siren red/blue flicker entry,
  RGB split (never fully settles on "bug"), 1-frame white flash, camera shake, logo slam (150/160 -> 94 -> 100% over
  6 f + flash + flash-star + shake; **B1, B13 and B17 use the same function**), 3D Y-flip (180 deg / 10 f, perspective
  2250 px, motion blur), whip-zoom / zoom-through with motion blur, slot-machine digit counter, tear-off calendar
  page, UK-outline location tag with pink pin, VCR timestamp (VT323), name pill (Montserrat), marker strike-through.
* **G7 Depth masking [DEPTH]**: the hero word sits between the plate and the subject. Cut the subject out with
  `npx --yes hyperframes@0.9.52 remove-background <clip> -o <out>.webm` (local model; `NODE_USE_ENV_PROXY=1`; trim
  the clip to the shot first; WebM keeps it small) or, for a hill/sky, a luminance/colour key. The shot then lives
  in HyperFrames as plate video -> word -> cut-out video. Check the edge at 200%.
* **G8 Texture/grade (doc 2.6)**: keep the dark vignette; global grain 3-5% (monochrome, size 1.2; lighter than v04);
  **archival 1990s camera footage only** (BBC making-of CRT plate, DMA office tours, the office B-roll, old Dundee,
  the interview) gets 1.5-3 px chromatic aberration + a light VHS line wobble; modern GTA V/VI gameplay is clean (the
  global chromatic aberration goes). Dark text cards: near-black **#0E0E10** + grain + a darkened, blurred loop of
  relevant footage behind at 15-25%; the frame is never flat black for more than 0.5 s (cards 0.8 s max).
* **G9 Sound (doc 2.7)**: every caption word: a soft tick/click (3 alternating samples, about -24 dB); every key/hero
  word: a short whoosh into it + a low thump (about -14 dB); every hard cut in the hook (B1-B2): a whoosh/swipe; the
  specific moments below. **Music bed stays off** (client v04 note 1, "remove Bg music"); the doc's music automation
  (duck 6-8 dB under VO, 2-6 f dropouts before "Because", "broke.", "dull.", "breaks.", the GTA logo, full level from
  "fun.") is built into the mix so it works the moment a bed is switched on; with the bed off, risers/ambience obey the
  same dropouts. Final mix -14 LUFS integrated, true peak <= -1 dBTP.
* **G10 Pacing (doc section 5)**: 0-4.5 s a full-frame visual change every 0.4-0.7 s, no inset on black, no half-built
  grid; 4.5-12 s no shot longer than 1.2 s; after that no shot longer than 2.0 s unless it pushes >= 8% and gets a new
  text/graphic event every <= 0.7 s; plain cards 0.8 s max with grain + faint footage; silence <= 0.5 s; callbacks look
  identical (Win95 window B2 7.6 s / B8 32.0 s / B16 69.0 s; siren flicker "cops?" / "chased." / "now?"; logo slam
  2.15 s / 53.5 s / 75.5 s, v04 times).
* **G11 Captions must tell the story with the sound off**: every spoken word is on screen (in lockups).

## S. Sound cues: `cues.json` v05 (lanes write it, assembly reads it; beat frames, f0 = beat start)

```json
{"events": {"...": 0},          // legacy S01-S19 events: keep only the ones whose sound you still want
 "word_pops": [12, 19],         // entry frame of every caption word that is not key/hero  -> tick (-24 dB)
 "key_words": [27],             // entry frame of every key (tier B) and hero word          -> whoosh-in + thump (-14 dB)
 "hook_cuts": [18, 49],         // B1-B2 only: every hard cut                               -> swipe
 "sfx": [{"f": 0, "name": "siren_whoop"}, {"f": 0, "name": "sub_hit", "gain_db": -8}],
 "dropouts": [{"f": 135, "frames": 4}],   // silence music/ambience for N frames ending at f (hit on the word)
 "archival": [[0, 18]],         // beat-frame ranges where archival footage is full frame (for the assembly finish)
 "note": "..."}
```
SFX names (assembly provides them in `03_SFX/v05/`, original or synthesized; levels are defaults, override with
`gain_db`): `tick` (3 variants), `whoosh_in`, `thump_low`, `swipe`, `siren_whoop`, `sub_hit`, `metal_crunch`,
`keyboard_clatter`, `error_chord` (an original "critical stop"-style chord, not Microsoft's file), `glitch_stutter`,
`stamp_thud`, `reverse_cymbal` (ends on its `f`), `impact_boom`, `sub_drop`, `paper_rip`, `flatline_beep`, `ding`,
`click`, `type_on` (per typed burst), `whoosh_flip`, `whip`, `hit` (3 variants), `riser`, `rewind` (= S17 spinback),
`glitch_impact` (= S08a).

## X. Where the doc reverses earlier notes (doc wins; told to the client)

X1 "CANNED" rubber stamp (v02: "I don't really like the cancelled stamp"). X2 literal 3D flip on "flips" (v02: "instead
of a flip animation, add a glitch"). X3 every word animates in (v03: "just have the text appear - no opening
animation"). X4 off-white paper for the Race'n'Chase page and the CTA card, white card-insert borders (v03: dark
aesthetic everywhere; all other cards stay dark). X5 setup words in Inter SemiBold (v02: regular text in Coolvetica
Regular). X6 the "It's 1995" line and its card are cut (v03/v04 notes on that card become moot). X7 pushes/punch-ins
the doc specifies (v03: "remove the random zooms": these are not random). X8 a sound on every caption/key word
(plan: "never a pop on every caption"). Kept from the client's notes: music off (v04 #1), glow flicker on "1995" and
"NOV 1997" (v04 #6/#15, layered on the new entry), the DMA logo itself (v03 #2), the Trailer 1 Lucia shot (v04 #20).

## N. Adapted / not possible

N1 "In Nov 1997" 2.0 -> 1.0 s, the lone "Of", the Gary Penn silence: see section 0 (audio). N2 the optional re-recorded
opening lines: no re-record. N3 CTA profile header: name "Raw Canvas"; the avatar, @handle and follower count are not in
the project (asked of the client; neutral stand-ins until then); keyword "BUG" as the doc gives it. N4 Win95 dialog:
recreated as a generic 1990s dialog (no Microsoft marks), text as on the CRT. N5 Section 5 "watch on a phone at 50%
brightness": checked on stills at phone size.

## L. Per-lane checklists (doc sections 3-4, v04 times; v05 frames from words.json)

**Lane 1, B1-B2 (doc section 3, beats 1-8; v05 times = v04 times)**
* Frame 0 rule: brightest, most saturated, full-bleed; no black, no inset (doubles as the feed preview).
* Beat 1 "Why does" 0-0.6: full-bleed police lightbar close-up flashing red/blue (GTA VI or V, night; Drive library
  `04_Broll/_originals/Drive2/`), f0 1-frame white flash 70%, punch-in 120->100% over 12 f ease-out; "Why" hero 450 px
  Coolvetica Italic centred, pink->white entry; "does" tier A 54 px tucked under its right edge; SFX siren_whoop + sub_hit
  on f0. Record the clip/in-point/scale of f0 in `hyperframes/b01-hook/LOOP_FRAME.json` (B18 crosses back to it).
* Beat 2 "every GTA," 0.6-1.65: full 2x3 grid edge to edge, 6 px black gutters, tiles slam in on a 2-f stagger TL->BR
  (each 108->100%), year label per tile tier C serif 60 px bottom-left (1997, 2001, 2002, 2004, 2008, 2013 = the games
  shown), "every GTA," centred on a 60%-black pill, "GTA," key 180 px; SFX six ticks rising in pitch.
* Beat 3 "even [GTA VI logo] have you running" 1.65-3.6: logo slam at 2.15 (150->94->100% / 6 f, 1-f white flash, 9 px
  shake 6 f, flash-star behind); gameplay 85% while the logo is up, 100% from 3.0; "even" tier A left of the logo; 2.85
  "have you" tier A + "running" tier B 195 px [DEPTH] behind the foreground shooter's head/shoulder; hard cut at 3.00 to
  a 150% crop of the same shot.
* Beat 4 "from the cops?" 3.6-4.5: keep the SUV flip; 40% speed for the 8 frames it leaves the ground; "cops?" 240 px
  centred-low, entry colour alternates #E3262B / #2E6BFF every 2 f for 8 f then white; SFX metal_crunch on the flip,
  4-f dropout before "Because".
* Beat 5 "Because back in 1995," 4.5-6.45: 4.5-5.1 CRT over-shoulder 112->116% + keyboard_clatter; 5.1 hard cut to the
  CRT screen cropped to fill the frame + scanline texture; "1995" hero Playfair Black 480 px white (+ the client's glow
  flicker), VHS timestamp "PLAY ▶ MAR 22 1995" VT323 42 px bottom-right; "Because back in" tier A above it.
* Beat 6 "a game about chasing criminals" 6.45-7.6: zoom-through into the monitor 100->400% / 8 f with motion blur,
  land on full-screen GTA 1 top-down cop-chasing-car footage (fills the frame); yellow arrows "you" (cop) and
  "criminal"; "a game about" tier A, "chasing criminals" with "criminals" tier B.
* Beat 7 "broke." 7.6-8.8: freeze at 7.6, RGB split 12 px, pink pixel-glitch tear across 30% of the frame; error
  window slams in centred at ~60% frame width; from 7.8 ten duplicate windows, 2-f stagger, +36/+27 px each, cascading
  off frame; "broke." hero 390 px lower third, jitter +/-4.5 px every frame; SFX error_chord then glitch_stutter.
* Beat 8 "And that bug saved it." 8.8-10.0: cascade stays; "And that" tier A, "bug" tier B 225 px, RGB split 6 px that
  never settles; 9.30 all windows snap shut (3 f, reverse stagger), 1-f white flash, clean full-colour gameplay of a
  cop ramming the player; 9.30-10.0 pill types "THAT BUG SAVED IT", exits with the pink pixel-glitch into B3.
* Hook cuts -> `hook_cuts`; 0-4.5 s change every 0.4-0.7 s; 4.5-10 s no shot over 1.2 s.

**Lane 5, B3-B4 + B18 (doc section 4, v04 12.0-20.0 -> v05 10.07-18.07; NEW 1:17.0 -> v05 73.77)**
* B3 (now starts at "Dundee,") 12.0-13.5 Dundee: push 100->108%, [DEPTH] "Dundee," tier B behind the hill's ridge (the
  hilltop overlaps the bottom of the letters), "Scotland." tier A, location tag bottom-left: small UK outline (white,
  3 px stroke) zooming toward a #FF2E7E pin on Dundee over 12 f.
* 13.5-14.5 DMA logo pops 140->95->100% over 5 f; the small "DMA Design" label under it becomes a small highlight pill.
* 15.0-15.5 Lemmings: keep; yellow hand-drawn circle around one lemming as "Lemmings," lands.
* 15.5-17.0 "starts a new game.": the 4:3 interview becomes a card insert (white border, 3 deg tilt, shadow, on a blurred
  darkened copy of itself), card push 100->106%, "new game." tier B.
* B4 17.0-18.0: no black; the Race'n'Chase Game Design page full frame on off-white paper texture, tilted 4 deg, push
  100->115%; 17.2 pink highlighter sweep across "Race'n'Chase"; 17.6 yellow circle around "March 22, 1995".
* 18.0-20.0: the 18-cell grid over the 1995 office footage (blurred 45 px, darkened to 25%), cells ~72 px with 9 px
  gaps, one cell fills every 2 f (tick per cell), "18" Playfair 330 px left of the grid, "months." tier B, hard cut or
  110% punch-in at 19.0.
* B18 CTA (75 f): off-white card with grain; profile header (avatar, name/handle, follower count) slides up from the
  bottom over 8 f; a cursor clicks "Follow" at CTA +18 f (v04 1:17.6), button turns grey + `click`; line
  `Comment "BUG" for the full story` in Playfair Italic 81 px, "BUG" in #FF2E7E, typed on; last 6 f cross to B1's frame 0
  (lightbar, `b01-hook/LOOP_FRAME.json`) so the loop is seamless. Handle/avatar/followers: neutral stand-ins (N3).

**Lane 2, B5-B8 (v04 20.0-33.0 -> v05 18.07-31.07)**
* 20.0-25.0 keep the split-screen; centre divider: 6 px white line wiping top->bottom over 6 f at the start.
* 23.0 "But there's a problem:" 6-f dropout before "dull."; 24.4 "dull." anti-style gag: desaturated (keep), gameplay at
  70% speed, "dull." in Arimo (Arial) Regular grey #8A8A8A 180 px, **no entry animation**, flatline_beep.
* 25.0-27.6 Gary Penn: push 100->112% across the hold; 25.1 name pill lower-left "GARY PENN" Montserrat ExtraBold 45 px
  + "DMA Design · Gamasutra, 2011" 30 px, typed on; 25.2 giant pink opening quote mark (“, 540 px, #FF2E7E 25%) fades in
  behind his shoulder [DEPTH]; "awful…" and "too sim-y" in Playfair Italic 135 / 90 px on the syllables; 26.3 cut to a
  140% crop (eyes and mouth) for "too sim-y". Caption "One developer later calls it" too (tier A).
* 28.0-29.5 archival office: card insert; yellow hand-drawn arrow pointing up at the managers on "above".
* 29.5-32.0 article: push 100->118%; 29.6 pink highlighter sweep on the headline "First Grand Theft Auto Was 'Almost
  Canned'"; ~30.0 cut or whip-pan to the body copy, sweep "It was almost canned."; 30.3 on "shut it down" slam the red
  "CANNED" stamp (-12 deg, ~45% frame width, stamp_thud, 1-f flash, 6 px shake); 31.0-32.0 "Then, something" article
  dims to 30% and blurs 0->30 px, reverse_cymbal into "breaks.".
* 32.0-33.0 "breaks." hero 450 px entering with the pink pixel-glitch; the Win95 window flashes 2 f behind it; glitch_stutter.

**Lane 3, B9-B12 (v04 33.0-49.5 -> v05 31.07-47.57)**
* 33.0-36.5: on "stop" freeze the cop car 4 f with a red outline glow, then release; on "straight" a whip-zoom with
  motion blur; yellow "you" arrow on the player's car from 35.5.
* 37.0-38.0 "They ram.": no black half: a second ram angle or full frame. 38.0-40.5: keep the lightning; each sentence
  its own shot (~0.7 s) with `hit` on "ram.", "chase." and "let go.".
* 41.0 "fun." hero 450 px + flash-star + 1-f white flash on the explosion (music would return here).
* 42.0 "flips": literal 3D flip, the whole frame 180 deg on Y over 10 f, perspective 2250 px, motion blur, whoosh_flip,
  from the daytime cop split-screen to the night "being chased" split-screen.
* 44.2 "cop" struck through with a #E3262B marker line drawn over 6 f. 45.0-46.3 "chased." with the siren flicker
  entry (identical to "cops?"); keep the yellow "you" arrow.
* B12: blurred darkened office or GTA 1 footage (25%) behind the whole stretch; the 18-month grid again, centred and
  larger; slot-machine counter "18" -> "30" Playfair 330 px, digits blur-roll 14 f, land on "30" with a thump; the 12
  extra cells fill #E3262B row by row, one row every 3 f, accelerating ticks; "thirty." tier B; "Of course," one unit.

**Lane 4, B13-B17 (v04 49.5-77.6 -> v05 47.57-73.77)**
* B13: blurred darkened office/GTA 1 footage (25%) behind; "Until finally," 0.5 s over footage; "In November 1997":
  tear-off calendar page rips "MAR 1995" -> "NOV 1997" (paper_rip), Playfair 300 px (+ the client's glow flicker on
  NOV 1997); "it ships with a new name:" tier A 57 px; dropout 6 f before the logo; 53.5 GTA logo slam 160->94->100% /
  6 f + flash-star + 1-f flash + 12 px shake 8 f + impact_boom + sub_drop; 0.386 s silence filled by the boom's tail, then
  reverse_cymbal into the box art = card insert, 3 deg tilt + shadow.
* B14 56.0-58.0 montage (III, VC, SA, IV): keep the 0.5 s cuts, year label serif 60 px bottom-left (2001, 2002, 2004,
  2008) like B1's tiles, `whip`/whoosh on every cut; 58.0-61.5 stars appear one by one 3 f apart (keep the client's
  glitch-in), a `ding` each; every phrase on its own cut.
* B15 61.5-62.5 "Don't believe me?": 115% punch-in on the character, the line in a highlight pill (fourth wall); 66.2
  yellow hand-drawn circle around the "RACE AND CHASE: STREET LEGAL" listing; 66.4 zoom 100->170% into it; 66.6 pill
  types "RACE AND CHASE"; 66.8 a split-screen of the 1995 design-doc title page (same look as B4) beside it for 10 f.
* B16 67.5-69.0 keep the VHS rewind; 69.0-71.4 no black: the hook's Win95 cascade over GTA 1 top-down footage, "The
  whole series started with a" tier A, "bug." hero 450 px with RGB split; on "bug." the windows snap shut (like B2) and
  the frame cuts straight to GTA VI.
* B17 71.5-72.3 "GTA 6?" [DEPTH] behind Lucia's silhouette in the window light; 72.5-74.4 "Lucia" tier B partly behind
  her shoulder [DEPTH], "already caught." with "caught." pink (held), push 100->110%; 74.5-75.4 "So who's chasing" two
  shots ~0.4 s each, whoosh between; 75.5 GTA VI logo slam identical to B1 + "now?" hero 330 px siren flicker entry;
  hard cut out to B18 (no fade).

## Process

Kit first (lanes prep footage / cut-outs / speed ramps / cues meanwhile), then lanes build on kit v05 (no renders by
lanes: snapshots only), then renders (`tools/render_all.sh`), `tools/build_tesseract.py --version v05 --preview`, the
doc's QA checklist on the preview, delivery.
