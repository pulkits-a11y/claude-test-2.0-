# REVISION v02: your notes on v01 (these override the Master Edit Plan where they conflict)

The Master Edit Plan stays the golden rule for everything these notes do not touch. Where a note below contradicts the plan, the note wins (it is the client's later, explicit instruction) and the change is logged in `CONFLICTS.md` under "v02 revision". **"Don't change anything else in the video apart from what I've asked of you to be changed."** So: no new ideas, sounds, texts, colours or shots beyond what is needed to carry out these notes.

## The notes (verbatim, with timestamps of v01)

1. "the transition on 0:10 is so fucking bad" + "Remove the Here's How" (B2 -> B3: X5 slats close/open into the T3 year card; T1 "Here's how." on the card).
2. "at 0:15, I don't really like the motion graphic that is on here. it's too basic and simple. Use something else, Focus more on the broll, it looks like a poster rather than a fast paced cut. The typography is also very slow, I want some unique layouts there. With each word popping up as he says it." (B3: the L12 photo cards + T8 "DMA Design" card.)
3. "at 0:31 the motion graphic is really bad again, I don't really like this and it's similar to 0:15 ... and I don't really like the cancelled stamp as well, it looks amateur as fuck, so just make it turn red or something. Or pull an article broll talking about it's cancellation (if that exists) and highlight the text which says it." (B7: L5 gray card + framed office clip + CANCELLED stamps.)
4. "Remove the 0:38 overlayed arrow and other animations, the broll is perfect." (B9: the path diagram: dot, dotted path, red arrow.)
5. "at 0:45, instead of a flip animation, add a glitch animation there. for what you used when the voice over said 'it breaks'" (B11: the L11 flip -> the X4 glitch used in B8.)
6. "at 0:52, I want the motion graphic to have a opening animation (it's really fucking good but just add a opening animation where it comes into the screen ... and move it a bit more above to the center." (B12: the calendar 18 -> 30.)
7. "at 1:10 - remove the text with the yellow background which says 'race and chase'" (B15: the T9 label.)
8. "whenever he says 'bug', don't use that bug icon, just use the word" (B2 T7 chip, B16 T5 chip -> the word "bug".)
9. "although r17.1 is missing, go through this link and use a fitting BROLL" (B17 opening: Trailer 1, Lucia in custody.)
10. "Make the video a lot more fast paced, make the voiceover a bit more faster too"
11. "Make all the captions appear word by word and I want only 2 words on screen at a time"
12. "Use the font that I attached (Coolvetica) ... replace the regular text with the regular coolvetica, and for instrument serif, use italic coolvetica."
13. "Add the texture pack and the overlay that i've attached. (... a subtle chromatic animation, a pretty visible / obvious noise or grain filter, a fairly visible vignette throughout the whole video)"
14. "I want every single animation to have easing functions and curves - no animation should be linear ... https://easings.net/ - i want you to follow this."
15. "The entire animation needs more zoom in and zoom outs so add that as well throughout, wherever you deem fit."

## What is already done (shared)

* **Voiceover 115%** (was 108%): `01_VO/VO_processed_115.wav` (locked v02 VO, 76.23 s), same pause edits as v01, same voice chain (-16.4 LUFS, -3.4 dBTP). Word times `01_VO/VO_words_115.json`; **`timing/beat_map.json` is now v02** (v01 kept as `timing/beat_map_v01.json`). B13 title-hold gap recomputed (43f). **Edit = 77.600 s = 2328 frames.** Every beat is ~6% shorter: re-time everything from the new beat map (each beat's `words.json` comes from `python3 tools/new_beat.py Bn --refresh`).
* **Fonts**: `_kit/base.css` now maps `--sans` to Coolvetica Regular and `--serif` to Coolvetica Italic (`06_Fonts/Coolvetica-*.otf`), one face each, `font-synthesis: none`. Every T-style follows automatically; check layouts (Coolvetica's widths differ from Inter/Instrument Serif).
* **Subtitles**: `07_Exports/RC_GTA-Origin_v02.srt`.

## Global rules for v02 (every beat)

**A. Captions (note 11).** Every on-screen text that transcribes the voiceover (T1 captions, T2 lead-in + keyword, T4 phrases, T5 line, T10) appears **word by word, each word popping in on its own first syllable** (comp_t from `words.json`, within +/-1f), and **never more than 2 words on screen at a time**. A caption group holds at most 2 words; it hard-cuts (or exits in <= 3f, eased) when the next group's first word starts. Split the plan's chunks into groups of 1-2 words that read naturally (a short function word goes with the word after it: "a / police officer" not "a police / officer"). Use the kit's caption helper (it does this). Designed cards that are not running captions keep their design (T3 year card, T6 GRAND / THEFT / AUTO, T8 quote card, the calendar counter, the design-document page), but every one of their animations is eased (rule C).

**B. "Here's how."** No caption for it (note 1).

**C. Easing (note 14): nothing linear.** No `ease: 'none'`/`'linear'`, no linear keyframes, no constant-rate opacity ramps, in HyperFrames or Tesseract. Hard cuts (a `data-start` boundary) are not animations. Use easings.net curves (GSAP names / CSS cubic-bezier):

| Motion | easings.net | GSAP | cubic-bezier |
|---|---|---|---|
| Slow push / zoom across a held shot, drifts, float loops | easeInOutSine | `sine.inOut` | 0.37, 0, 0.63, 1 |
| Entrances, pops, landings, punch-ins settling | easeOutExpo / easeOutQuart / easeOutBack | `expo.out` / `power3.out` / `back.out(1.7)` | 0.16,1,0.3,1 / 0.25,1,0.5,1 / 0.34,1.56,0.64,1 |
| Exits, accelerating into a cut, zoom-throughs | easeInExpo / easeInQuart | `expo.in` / `power3.in` | 0.7,0,0.84,0 / 0.5,0,0.75,0 |
| Fade in / fade out | easeOutCubic / easeInCubic | `power2.out` / `power2.in` | 0.33,1,0.68,1 / 0.32,0,0.67,0 |
| Moves between two rests, slides | easeInOutCubic / easeInOutQuint | `power2.inOut` / `power4.inOut` | 0.65,0,0.35,1 / 0.83,0,0.17,1 |
| White flash ramp / fade | easeInQuad / easeOutQuad | `power1.in` / `power1.out` | 0.11,0,0.5,0 / 0.5,1,0.89,1 |
| Number rolls, counters | easeInOutQuad | `power1.inOut` | 0.45,0,0.55,1 |
| Type-ons (letters/characters) | easeOutQuad timing over the same total length | stagger with `ease: 'power1.out'` | |

**D. Zoom in / zoom out (note 15).** More camera movement everywhere it fits, always eased:
* Held footage: push 100 -> 106-110% across the shot (sine.inOut) instead of v01's linear 104%; alternate with slow zoom-outs (110 -> 100%) so it doesn't feel mechanical.
* Cuts into a new shot: often a punch-in that settles (112-118% -> 100-102% over 8-12f, expo.out).
* Emphasis words (keywords, key nouns): a quick frame punch (content 100 -> 105-108% in 3-4f expo.out, back over 8-10f sine.inOut).
* Transitions: zoom-throughs (outgoing 100 -> 130-150% + blur over 4-6f expo.in; incoming 125-140% -> 100% over 8-10f expo.out).
* Keep captions steady and readable (zoom the picture, not the caption layer), and no more than about one punch per second.

**E. Fast pace (note 10).** Faster VO (done), snappier animations (shorter, strongly eased), quicker B-roll cuts where a beat has several clips. Don't remove plan holds that the notes don't touch (B6 quote, B8 black, B13 title hold, logo tail), but make their entrances/exits snappy.

**F. Whole-edit finish (note 13), in the Tesseract assembly, not in the beats:** the attached dust/particle overlay (`04_Broll/Textures/dust_overlay.jpg`, Screen blend, drifting), a clearly visible grain, a fairly visible vignette, a subtle animated chromatic aberration. Beats must not add their own grain/vignette/chroma on top.

**G. Glitch + red are now allowed where the notes ask** (B11 glitch, B7 red), overriding the plan's motif discipline only there.

## Per-beat notes (v02 frames come from the new beat map)

* **B1**: re-time; global rules (captions word by word, 2 words; easing; zooms).
* **B2**: "And that bug saved it." -> the word **bug** (no chip): captions word by word. The **0:10 transition** (B2's X5 slat close into B3) is replaced: a fast zoom-through (B2's last frame scales up into the cut with blur, expo.in; B3's year card arrives scaling down from ~130%, expo.out). No new sound.
* **B3**: no "Here's how." caption; the year card arrives with the new zoom-through (not X5 blinds). **Redesign the "DMA Design, the studio behind Lemmings, starts a new game." section** (v01 0:14-0:17, the L12 photo cards + T8 card): **full-frame B-roll, fast cuts** (R3.8 DMA office, R3.7 the 1996 BBC team / map, R3.3 Lemmings box, R3.6 the Lemmings intro with the walking lemming), cut on the words, punch-ins; **kinetic typography in unique layouts, each word popping in as he says it** (max 2 words on screen; varied sizes/positions inside title-safe; Coolvetica + Coolvetica Italic for "DMA Design" / "Lemmings"). Keep "It's 1995 in Dundee, Scotland." and "starts a new game." as built, re-timed (the T4 Dundee/Scotland words now also pop word by word).
* **B4**: re-time; global rules (the design-doc push + highlight and the calendar fill stay as they are, eased).
* **B5, B6**: re-time; global rules. B6's T8 quote card stays (eased).
* **B7**: **no L5 card, no CANCELLED stamps.** Full-frame office B-roll (R7.1; R7.3 the 1990 DMA office tour if it fits), fast cuts with zooms, and on "keep trying" / "shut" / "down" (the old stamp words, same S06 hits) **the picture turns red** (siren red `#E3262E` tint/flash, eased in 2-3f and out). If a real article about the game nearly being cancelled / shut down exists (a credible outlet's page that says it), screenshot it and use it on "to shut it down" with a highlighter swipe over that sentence and a push-in; otherwise red only. Never fake an article.
* **B8**: re-time; the X4 break now breaks whatever B7 ends on (rebuild the X4 still from it). T10 "breaks." stays.
* **B9**: **remove the path diagram entirely** (dot, dotted path, red arrow). Keep the L1 footage, the strips and the captions (word by word).
* **B10**: re-time; global rules ("fun" flash/drop frame = the new "fun" frame).
* **B11**: **the flip is replaced by the X4 glitch** (same look as B8's break) from the front split screen (B5's) to the back (the chased roles). The glitch sound replaces the flip whoosh. Keep everything else (the arrow on "Now", the captions).
* **B12**: the calendar gets an **opening animation** (it comes into the screen: e.g. rises/scales in with expo.out / back.out) and sits **higher, nearer the centre**. Keep the 18 -> 30 fill and counter.
* **B13, B14**: re-time; global rules.
* **B15**: **remove the T9 "RACE AND CHASE" label.** Keep the spotlight, the zoom into the cabinet, captions.
* **B16**: "The whole series started with a bug." -> the word **bug** (no chip), word by word, max 2 words.
* **B17**: the Trailer 1 opening (R17.1 stand-in) is replaced by the client's clip `04_Broll/_originals/Drive2/Video by madebyajit [0-29s].mp4` @ ~1.0-5.0 s: Lucia in the prison yard behind the fence (the Trailer 1 opening). It has a heavy pink fan-edit grade: use grade `neutralize` in `tesseract_shots.json` (the assembly tones it down). Credit: madebyajit.
* **Cover**: re-snapshot with Coolvetica.

## Tesseract shot framing v2 (`tesseract_shots.json`)

```json
"framing": {"anchor": "center", "keys": [{"f": 0, "scale": 114}, {"f": 10, "scale": 101, "ease": "easeOutExpo"},
                                          {"f": 54, "scale": 107, "ease": "easeInOutSine"}]}
```
`f` = frame relative to the shot start; `ease` = the easings.net curve used to arrive at that key. Optional `x`/`y` (px) per key for drifts. The old `scale_from`/`scale_to` form still works and now eases with `easeInOutSine` (add `"ease"` to override). `grade` may also be `neutralize` (B17's fan-edit clip).

## Per-beat procedure

1. `python3 tools/new_beat.py Bn --refresh` (kit + new words), read the beat's index.html, BEAT_NOTES.md, footage.json, tesseract_shots.json, cues.json, the plan's beat page and this file.
2. Re-time every frame constant, clip `data-start`/`data-duration`, footage window, caption, Tesseract shot (`start_f`/`end_f`, beat-relative) and cue (`cues.json`, beat-relative frames) to the new beat length (`dur_frames` in the beat map; composition = beat + 6f handles). Root `data-duration` with 7 decimals.
3. Apply the global rules A-E and the beat's notes.
4. `npx --yes hyperframes@0.9.52 check --json` 0 errors; snapshots at every caption word, cut, transition and zoom into `review/` and LOOK at them (Coolvetica layouts, max 2 words, nothing linear).
5. Render: `npx --yes hyperframes@0.9.52 render . --format mov --workers 1 -o ../../05_GFX/renders/<id>.mov`; ffprobe: frames = new beat + 12, yuva444p12le.
6. Update BEAT_NOTES.md (v02 section: what changed and why, with the note number) and keep `cues.json` truthful.
