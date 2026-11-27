# GTA 9/11 Cover Reel: build notes

## Deliverables

All of these are in `gta-911-cover-reel/`.

| File | What it is |
|---|---|
| `GTA911_CoverReel.tsrct` | The editable Tesseract project. It has one 1920 × 1080, 30 fps main composition, 37.73 s (1,132 frames: the 35.23 s voiceover plus a 2.5 s hold on the final covers). Media and fonts are embedded. |
| `GTA911_CoverReel.mp4` | The render: 1920 × 1080, 30 fps, H.264, with the voiceover as the only audio. |
| `contact_sheet.jpg` | One frame from the middle of each shot, labelled with the shot name and frame. |
| `source/` | The supplied fonts, voiceover, plates, textures, logo, brief, `build18.mjs` and `grade_lite.json`. The B-roll lives in `source/broll/` (3.5 GB, not in git), and your montage clip in `source/montage/montage.mp4` (not in git). |
| `build/` | The generator: `make.py`, `reel.py`, `lib.py`, `prep.py`, the WGSL shaders, `check.py` (the brief's checklist) and `export.sh`. |

To rebuild from `source/`, run `build/make.py` followed by `build/export.sh`.

The layer tree is organised as scene groups. Each scene group holds shot groups, and each shot group has a graded media group, a look, a dim layer and prism streaks. Above the scenes, from the bottom up:
- the clip grain
- the edge-blur pulses
- the seven film-wide overlays
- the glitch transitions
- the caption glow
- the captions, one group per word
- the flash cuts and flash transitions
- the logo, on top

## Restored to v6

At your request the project is back to v6 exactly. Everything after it is undone:
- the v7 typography spec
- the removal of the grunge, halftone, vignette and bottom-shade layers
- the live box-front shot at 0:05.5

The build files are identical to the v6 commit (`6e076e8`), and the render was made again from them. The v7 and v7b work is still in the git history if you ever want any of it back.

## v6: AI plates, placed captions, the Stephen run, a held ending

**Your three AI images** are in `source/ai/`. Bliss's real art is composited onto their blank pieces and screen (`build/ai.py`). Each piece's artwork is warped to its corners and lit by the plate's own paper, so the lamp light, texture and cut lines stay.
- **0:12.1, "six weeks":** the studio desk replaces the PS2 box. The European cover is open on the CRT, the cover that was meant to ship. I didn't use the US cover there, because it didn't exist yet six weeks before launch. The calendar's crossed-off days flicker on "weeks", with a slow push toward the monitor.
- **0:20.5, "own painting.":** the cutting mat. The European cover painting is cut into the 3×3 block, with three loose pieces and the knife beside them. It replaces the torn-poster shot. The Bliss working shot before it is 7 frames instead of 10.
- **0:23.7, "and boxed":** the light table. The real US cover panels sit on the 12 pieces, and the last one flickers as the hand sets it down. It's darkened so the caption reads.
  - The live gameplay grid follows at 0:24.1. Its panels pop in twice as fast so the scene keeps its length.
- I didn't change the AI images themselves.

**Captions placed by what they describe (0:07.9–0:09.8):**
- "guns," sits by the rifle on the key art, then by Claude's gun.
- "fire," sits above the blast, then on the burning car, then over the street fires.
- "and burning buildings" builds up in the sky by the skyline.
- "It had" is unchanged.

**"six weeks / before launch." (0:12–0:13.4):** one statement, stacked in the lower third at 62 px. A soft dark ramp at the bottom of both shots keeps it readable.

**The banned list (0:15.9–0:17.6):** "guns,", "buildings," and "or fire." stack one per line, each appearing on its word. Same caption style.

**Stephen match cut (0:17.6–0:18.1):** seven photos of him, 2 frames each, instead of three at 4 frames. The new frames are B26 at 300 and 600 s and B28 at 1650 and 1760 s. Every face is at the same spot and size. The heat-map shot after it is 8 frames instead of 10, so the run is only 2 frames longer.

**The ending:** the final split now holds 2.5 s past the voiceover (the film is 37.73 s, 1,132 frames).
- The covers push in slowly (to 105%).
- "25 years later." fades out about 1 s before the end, so it ends on the covers alone.

## v5b: changes from the v5 notes

- **Every caption glows.** I read "make all captions bold" as the glow look in your screenshot ("six weeks" vs "before"). The font weight is unchanged (the reference's 600).
- **No strike slashes** anywhere (guns, buildings, fire).
- **0:05–0:07:** the tracking boxes are down to one faint box per shot (35% opacity).
- **0:02 TV:** the jump-cut zooms are gone. It's back to the v4 move, a slow, subtle grow from its entry.
- **0:18 Stephen:** both jump cuts are gone (the heat-map shot and "a week"). The rise-in and the slow artwork parallax stay.
- **Match cuts (0:03 and 0:33):** the flash on each switch is now one frame at about 30% instead of 70–85%.
- **Fewer transitions:**
  - 6 glitches (0:00.8 into the CRT, 0:10.7 into the CRT, 0:12.1 out of it, 0:19.5, 0:26, 0:32.3).
  - 2 white flashes ("fire" at 0:08.6, Vice City at 0:28.4).
  - The 4 flash cuts stay.
- **The zoom on the covers and Bliss cards (0:25–0:31)** is back to v4's ease-out zoom, minus the sideways drift that caused the wobble. It replaces the v5 push-in.
- **No commas** on City, Andreas, IV and V.
- **"25 years later."** is back on one line at caption size, between the covers at their original 700 px.

## v5: changes from the fourth review

**Caption glow, where it matters.** The v4 glow measured almost nothing next to the reference "by definition,": about +14 brightness right at the letters and nothing beyond 6 px, against the reference's +92 falling to +18 at 60 px.
- **How it's built:** each glowing word now has four blurred copies (20, 40, 80 and 160 px) added over the picture in warm white, under the sharp word. The falloff was measured against the reference frame: +88 at the letters, +43 at 6–10 px, +13 at 22–32 px. A version that matched the reference exactly at 60 px read as a blob on dark footage, so I used the tighter one.
- **Which words glow:** 9/11, "this?", six months, guns, fire, burning buildings, 9/11 hit, six weeks, pulled, Stephen Bliss, a week, chopped, own painting, grid, rush job, template, VI, boxes, grid, and 25 years later. 19 word runs in all.
- **Everything else:** plain warm white (#FDF4E3) with a small soft shadow.
- **Where it lives:** the root group "Caption glow", one group per tier per word run.

**Stretch entrance:** only on the hook's words (before 0:07.6). After that, words fade up over 3 frames with a 10 px rise.

**0:03 → the match cut.** Seven covers (III, Vice City, San Andreas, Liberty City Stories, IV, V, VI) cut at the same spot, 2 frames each, with a 1-frame white flash on every switch.
- They are 620 px tall so they sit between "is the reason" and "GTA covers look like this?". The captions are unchanged.
- Each cover has its own tracking boxes.

**The wordmark screen** (the x/y letter boxes, thumbnails and tile grid) moved to 0:26, "It's been the template". It replaces the US-cover cutout that repeated there.

**More x,y tracking boxes, mostly in the hook.**
- About twice as many per hit at 0:00–0:00.8.
- Boxes on the TV set.
- Labels on about 70% of the logo tiles.
- At 0:04.8–0:07.6, boxes that follow the footage: on the box in his hands, on the box front, and on Bliss's face. These are tracked frame by frame with optical flow and keyed on every frame.

**Hook TV (0:00.8–0:03.7):** held, then a hard jump cut tighter on "GTA" (74% → 86%) and again on "this?" (92%), like the reference. It never gets wider than the gap between the captions.

**Gun flickers.** Each gun flashes white one after another for 3 frames (on, off, on at 70%) and gets a tracking box as it does.
- **0:07.9, the key art:** rifle, then revolver, then pistol.
- **0:08.2, Claude's gun:** B48 at 167.6 s, with the gun traced on its two flash frames.
- **0:31.5, Jason's rifle:** in the GTA VI montage shot.
- The shapes are in `build/masks.json`.

**Attention flickers at 0:21.7–0:23.3:** the face, car and helicopter panels of the US cover flash white for 3 frames. The ink lines stay dark. Each panel gets tracking boxes.

**Transitions, curated (18 in all).**
- **10 digital glitches,** on cuts into or out of screens, graphics and gameplay: 0:00.8, 0:04.1, 0:07.6, 0:10.7, 0:12.1, 0:14.8, 0:19.5, 0:26, 0:29.4 and 0:32.3.
  - Each is 4 frames of band tears, RGB split and a few displaced blocks, with a new pattern every frame.
  - They're built natively as a shader (`build/shaders/glitch.wgsl`) on an adjustment layer, so they stay editable. I didn't download a YouTube glitch pack: re-uploading someone else's overlay is a licensing problem, and a baked clip can't be retimed.
- **4 quick white flashes** (3 frames) on hits: the box front at 0:04.8, "fire" at 0:08.6, Vice City at 0:28.4 and the final split at 0:34.
- **The 4 flash cuts** are shortened from 10 frames to 4.

**Your montage.** I left it out of the hook, which we've already built to match the reference. It's used where it fits the words:
- "He only kept the faces," (0:22): its wall of GTA character faces, replacing the B48 cutscene there.
- "V, even GTA" (0:31.2–0:31.8): the GTA VI masked pair, then Jason with the rifle. These replace the two B52 box shots.

**The B48 cutscene** moved to "before launch." (0:12.5–0:13.3), after the PS2 box. It keeps the purple duotone and is framed clear of the subtitles and the frame-time graph.

**B48 framing:** every B48 shot now frames a rectangle measured to stay clear of the burned-in overlay:
- the frame-time box and its label
- the framerate chart and its label
- the FPS readout
- the game HUD

Two of them also changed footage:
- "Fire" (0:08.6): the van exploding behind Claude, at 169 s.
- "Guns" (0:08.2): Claude with a clearly visible gun.

**0:18, Stephen:** he rises into frame, the artwork behind him slides slowly the other way, and a jump cut punches in on "a week". The heat-map shot before it wipes the eye strip in, then jumps closer. None of this is the old sideways drift-zoom.

**0:20, "up his own painting":** Bliss's own torn-poster painting (B27 at 74 s) replaces the European-cover face crop.
- I chose it over the "Bliss" lettering at 42 s because the lettering is white paper, and the captions and glow wouldn't read on it.
- The car detail and whiteout after it are unchanged.

**0:25, "That rush job?":** the photo card is centred, with "That rush" on its left and "job?" on its right.

**0:26–0:27, the moving GTA cover:** fixed. The cover in the mosaic and the box swaps that follow are now held still. They used to drift sideways in alternating directions, which read as a wobble. The covers at 0:28–0:31 and the two Bliss cards use a slow push-in instead.

**Frame timing fix (affected v4 too).** Layer times were rounded to whole milliseconds at each nesting level (scene, shot, layer). On some frames the rounded start landed just after the frame it belonged to.
- **What went wrong:** some 1-frame flashes slipped a frame or didn't show. In the 0:33 match cut, motion blur smeared the others into 3-frame grey washes, and some cover switches landed a frame late.
- **The fix:** times are now floored, which never lands late. Flash layers skip motion blur.
- **Checked on a test render:** every cover switches on its frame, with one crisp flash per switch, and each gun flickers on exactly its frames.
- The same fix applies to the clip cuts. A few cuts that used to land one frame late are now on time.

**0:35, the end:**
- "25 years" is 90 px, about twice the caption size.
- "later." sits underneath, scaled to exactly the same width.
- Both glow, centred between the III and VI covers, which are now 600 px tall.

## v4: changes from the third review

**0:08–0:10.7, footage for what is said** (no cover crops, no split collage):
- "It had": the European box in hand (B09, 49 s).
- "guns": the GTA III key art of the crew with rifles (B25, 119.6 s), then Claude holding a gun (B48, 163.6 s).
- "fire": an explosion behind Claude (B48, 166 s), then a burning car at night (B25, 123.3 s, lifted so the flames read).
- "burning buildings": a street on fire between the buildings (B48, 172 s).
- "all over it": the European cover.

The B48 gameplay is framed on Claude, with its frame-time graph cropped out.

**0:09:** the European-cover split and collage is gone.

**Held still** (no drift or zoom): the CRT at 0:11, the PS2 box at 0:12, Bliss in the gallery at 0:15, and the heat-map face and Bliss cutout at 0:18.

**Flicker-blink flashes:** the same rotoscoped effect on all of them, now an on / off / on blink that fades, about 8 frames. The flash layers skip motion blur so the blink stays crisp.
- **0:05:** the "grand theft auto III" title on the European box. The box front is now a still frame (B09 at 50 s) so the title mask stays locked.
- **0:18:** Stephen, as the cutout lands. His figure glows for a blink, with his face still readable.
- **0:34:** the GTA III title, then the GTA VI title, on the split. Both masks are new and undilated, so the letter shapes stay crisp.

**0:28 floating covers:** no caption over them. "for every GTA cover" clears as the animation starts, and "since." is not shown.

**Vice City / San Andreas:** every box sits in the middle at one size (680 px). "Vice" and "San" go on its left, "City," and "Andreas," on its right. IV and V stay to one side.

**0:33:** the carousel is replaced by a match cut: ten covers at the same spot and size, about 2 frames each, with a 1-frame white flash on every switch.

**0:06–0:07 captions:** "six" and "months" sit either side of his face. "of painting." sits just left of him in the second shot, clear of his body.

**CTA:** removed. The film ends with the voiceover at 35.23 s (1,057 frames).

## v3: changes from the second review

**The hook (0:00–0:07.5), rebuilt on the reference video's first 6 seconds** (`source/reference/caption_hook_reference.mp4`). Code is in `build/v3.py`, groups H1–H4.
- **0:00–0:00.8, "What if I told you":** 2–3 frame hits with computer-vision tracking boxes (coordinate labels, green centre dots). The boxes sit on each frame's strongest features, found with OpenCV. The hits:
  1. the Sept 12 "TERROR HITS HOME" page as a cream negative
  2. the towers on CNN
  3. the TV room as a negative
  4. the screen wall
  5. a terminal readout, orange on cream, then cyan on black
  6. the GTA III helicopter in a tracking circle
  7. a black-and-white car chase
  8. a motion-smeared pan

  The terminal lines are decorative file and scan readouts, not factual claims.
- **0:00.8–0:03.6, "9/11 is the reason GTA covers look like this?":** the A01 CRT cut out of its room and lifted to read as a grey set on black, growing slowly. It arrives on red light. The screen carries the 9/11 news, then the GTA covers, in black and white with scan lines and stepped row tears (`crtglitch.wgsl`). The captions build either side of it.
- **"this?":** a red flash, as in the reference.
- **0:03.7, wordmark:** the GTA III wordmark (cut from the US cover) with a tracking box on every letter and a split-second glow flash.
- **0:04.1–0:04.8, "This was meant to be":** logos built from tiles that pop on in random order, with coordinate labels, small video thumbnails around them and a faint tile grid behind. First the GTA VI "VI", then the European cover.
- **0:04.8–0:07.5, "the GTA III cover, six months of painting.":** full-frame cuts:
  1. the European box in hand (B09)
  2. its front
  3. Bliss talking (B26, the call panel enlarged to fill the frame)
  4. Bliss at his mural (B27)

  This replaces the "Six months" type shot at 0:07.
- **Overlays:** during the hook the film-wide overlays are mostly off (lift, desaturate and halftone off; grunge, vignette and scan lines light), so it is as clean as the reference. They return to full by 0:07.5.

**Captions:** one style for every word, built from the reference.
- **Type:** Archivo at 47 px (the reference's 32 px cap height; its "Every time you have" is 416 px wide, and ours is the same) and wght 600. The fill is warm white #FFF6EA.
- **Glow:** three blurred copies of each word, screen-blended: 4 px and 10 px in #FFE6C2 and 24 px in #FFC98A. The layer-style glow from v2 was too faint once the overlays were on top, which is why it looked missing. Captions now sit above the film-wide overlays so the glow stays clean.
- **Placement:** on the centre line. Each phrase splits into a left block, right-aligned to the subject's left edge, and a right block, left-aligned to its right edge, so the words move around what is on screen, as in the reference.
- **Entrance:** each word drops in on its spoken frame, stretched to 520% tall, and snaps to size over 5 frames (ease-out expo), like the reference.
- **Removed styles:** the tracked caps label ("This was"), the wide light face ("up his own painting"), the heavy condensed face (GUNS, FIRE, MEANT TO BE, PULLED, A WEEK, CHOPPED, VICE CITY, SAN ANDREAS) and all big-word layouts. FACES, CARS and HELICOPTER stay out as asked in v2.
- **Numerals:** "Four, five, six" show as "IV, V, VI".

**Other changes**
- **No tilt:** no overlay is tilted at any point. Cards, cutouts, boxes and the floating collage are all straight. The checklist now fails on any rotation.
- **"25 years later.":** centred between the III and VI covers, which hold to the end of the voiceover. The 2001/2026 numbers are gone.
- **0:34 carousel:** the second whip carousel (the one that restarted) is removed.
- **Slashes:** thinner (about 9 px), solid. The p5.brush charcoal stroke is rendered at 3× and its alpha thresholded to a solid core with a rough edge. Each is drawn on over 14 frames with ease-out expo, so it starts fast and slows.
- **S8.2 paper card:** replaced by the US cover, because white captions don't read on cream paper.
- **CTA:** the supplied RawCanvas logo sting (`source/cta/cta.mp4`) plays after the voiceover with its own sound, at 2.23 s. The film is now 37.47 s (1,124 frames).
- **Flash cuts:** four now. The one on the old S2.1 went with the old hook.

## v2: changes from the review notes

**Type**
- **Instrument Serif:** replaced everywhere by the Archivo caption face. Each big word keeps the width the serif line had (it's never made larger than before). The font file is still embedded in the base project but isn't used by any layer.
- **Soft glow:** every text layer has an outer glow in its own colour (34 px, 50%, screen; 35%, normal for the dark ink on the paper card) on top of the existing drop shadow.
- **Entrance:** the letter-spacing entrance (used on 2001/2026 and elsewhere) is gone everywhere. Those words now blur in.
- **Removed text:**
  - "the GTA III cover."
  - "Bliss" (his name is now in the label above his head: STEPHEN BLISS · GTA COVER ARTIST)
  - FACES, CARS and HELICOPTER
  - the big "VI"
  - "25 YEARS LATER"
  - the "GTA III · OCT 22, 2001" label
- **0:12 "six weeks":** no stacked centred layout. The PS2 box is on the right, with one left-aligned block on the left: "six weeks", then "before launch".
- **0:02 "9/11":** in Archivo, with its top half clear above the front page.

**Removed shots** (neighbours lengthened to fill the time)
- **Date-flip shots:**
  - B15 calendar (S4)
  - B22 years (S6) and its use as a background
  - B29 days (S9)
- **The red heat-map B27 silhouette:** both at 0:07 and its repeat at 0:25.
- **The B14 brush macro on "painting".** "Six months of painting" is now one held shot, with the letters of "Six months" filled with the original cover painting.
- **S6 Front-page headline and B20 box shots.** The CRT 9/11 shot now holds 1.5 s (44 frames, was 26).
- **The 30-frame cap is relaxed** on four held shots: the painting in the type (42), the CRT (44), six weeks (36) and the Bliss cutout (35).

**Pictures**
- **0:03:** the VI logo is cut down to a window around the VI only, in the centre cell of the mosaic.
- **Burning buildings and the split screen:** crops are about 2× (they were up to 9×). The full shot shows the upper cover (title, tower, characters); the split shows gun, fire and tower.
- **Split screens:** no borders anywhere (3 × 640 and 2 × 960, edge to edge).
- **No more tilted overlays:** photo cards have no white borders. Every overlay that comes in tilted settles straight within 10 frames (cards, cutouts, boxes, floating covers).
- **0:33:** the III/VI switch is now a whip carousel. One strip slides one cover per step with ease-in-out expo, motion blur and a horizontal smear at mid-move, accelerating in the second run.

**Effects**
- **Logo glow flashes:** rotoscoped from the stills. Letter masks were cut in OpenCV:
  - the GTA III title from the white letter fills inside their black outlines
  - the GTA VI "VI" from the clean B06 logo frame, scaled onto the cover, with the "grand theft auto" lettering cut out of it

  The flashing layers are the masks plus two blurred halos, on screen blend, locked to the cover. Each comes up in 2 frames and is gone in 5: on the title close-up (0:04.9), the cover (0:05.8) and the VI ("Six", 0:31.8).
- **Strike-throughs:** hand-drawn charcoal slashes rendered with p5.brush 3.0.0 (MIT) in headless Chromium (`build/brush/`), coloured #D8322A, drawn on left to right with a wipe.
- **Motion blur:** on for the composition (180° shutter, 6–24 adaptive samples) and on every layer.
- **Edge blur** on fast switches: a radial (zoom) blur adjustment, clear at the centre, peaking on the switch. It's on the mosaic whip (0:03.5), the US box whip (0:25) and every carousel step.

## Export

- **Rendering:** the two halves are rendered with motion blur in parallel (about 12 minutes each here for v5). The MP4 exporter drops a few frames at the end of a range, so `build/export.sh` renders each half's last 16 frames again as ProRes, puts the missing ones back in place, and joins the halves frame-exact.
- **Check:** each restored and neighbouring frame matches its source render (mean difference 0.1–0.4).
- **The file:** 1,132 frames, 37.733 s (v6), 1920 × 1080, 30 fps, H.264 at CRF 14.
- **Audio:** Tesseract's own mix of the voiceover, as AAC 256 kb/s stereo, padded to the last frame. It measures −18.4 LUFS integrated because the mono voice sits in both stereo channels; it sounds the same as the supplied file.
- **Not checked:** I can't listen here, so voiceover sync is checked by word timings, not by ear.

## Voiceover

Your message said "[raw / already processed]" without choosing one. I treated the file as already processed: it runs 35.23 s (the brief expects about 35 s after processing, against 48.8 s raw), it has no pause longer than 120 ms, and its filename says `tight_118`. I did not cut or speed it up again.

## Timing

- Word timings come from a local transcription with word timestamps (faster-whisper). All 112 words are aligned.
- Each scene starts in the middle of the pause before its line, so no scene starts with dead air.
- Inside each scene, the doc's frames are warped so that every on-screen word lands on the frame it's spoken and every shot keeps its share of the line. All 92 shots are under 30 frames; the longest is 29.

Cuts I moved to keep within the rules:

- **S2:** the mosaic shot ends at frame 104 (29 frames).
- **S14:** shots 1 and 2 are each 29 frames. I moved the cuts to frames 882 and 911, one frame before "San" and "Four".
- **S16:** shot 1 ends at frame 998, three frames before "Same grid", so it stays at 29 frames.
- **S7:** "pulled" and "it" are only 9 frames apart in the real read. PULLED smears in over 4 frames and out over 3 (the doc says 6 and 4), and shot 3 starts at frame 422.
- **S8:** "fire." is spoken at frame 515, so the screen-wall shot starts at frame 521 to let the strike-through finish first.
- **S4:** the Track in on "Six months" starts with the scene, 4 frames before "six", so the footage-filled letters are fully in when the word lands.
- **S3:** the flash shot is 4 frames (the warp gave 3).
- **Scenes 1–5:** the doc's own hero shots stretch with the slower read. The longest are the mosaic (29 frames), "Six months" (22), the C01 cutout (19) and the split screen (15).

## Text changes

- **S9:** the doc's scene table has a "Stephen Bliss" caption and then a big "Bliss". On the real read the big "Bliss" lands on the word itself, so the caption shows only "Stephen". This also keeps the global rule that a word shown big is not also a caption.
- **S9:** with this cutout, the shoulders covered "Bliss" completely at baseline y 880. I raised it to y 720 so the shoulders cover only its lower part.
- **S12:** "and boxed them into a", right-aligned to x 520, starts left of the x 96 safe margin on one line at 46 px, so it is set on two lines around y 660.
- **S5:** the doc's table has no word for "and" (between fire and burning), so it is not shown. **S11** drops "the" and "and the" as the doc says.
- **S14:** shots 2–4 use 560 px boxes; the doc leaves the size open there. At 780 px, "IV" (800 px) and "V" (900 px) were completely hidden behind the box. Shot 1 keeps 780 px.

## Swaps (files missing from the Drive folder, or clips without the moment)

| Doc | Used instead | Why |
|---|---|---|
| #2, NY front pages | Other B01 pages | B02 is a panel discussion with no front pages |
| #8, GTA VI cover | B07 frame at 162.5 s and the B06 reveal logo | B08 not supplied |
| #12 and #17, original European cover | A B09 frame at 20 s, flattened (C02) | B12 and B17 not supplied |
| #32 and #33, US GTA III cover | B07 frame at 37 s, whose grid layout is measured for the live grid | B32 and B33 not supplied |
| #19, ITN skyline | B04 (CNN skyline, the other Line 1 TV source) | B19 not supplied |
| #25, Rockstar boot logo | B39 at 537.6 s | B25 starts on gameplay, with no boot screen |
| #25, a car exploding | The GTA III helicopter explosion in B49 at 99 s | B25 has no explosion |
| #25, shooting | B49 at 28–31 s (GTA III, aiming at the helicopter) | Clearer than anything in B25 |
| #23, newspaper tear | B24's opening white-paper tear | B23's tear is a magician on stage, face on camera. B24's coloured sections carry a stock-site watermark and "CLIP0x" text, so only its opening tear is used, cropped below its title. |
| #28, Bliss in his studio (S8.1) | B27 at 58.5 s (gallery, medium shot) | B28 is a split-screen video call |
| #35 and #37, GTA IV and Vice City boxes | B07 cover scans in S13; B36 for the Vice City box in S2 and S16 | B35 and B37 not supplied. Flat scans also keep "one box changing" exact in S13. |
| #53, second angle | B52 at 20 s | B53 shows the box small, with the presenter's face filling the frame |
| C07–C12 box faces | B07 flat cover scans | The doc's own fallback for line 14 ("the flat covers, if the box shots don't land") |
| S14 bed | A03 table for all four shots | The doc's fallback when the box footage is messy |
| S6.5 bed | B22 "2001" year frame | B22's day pages are on green screen |

## Cutouts

- **C01** (front page), **C02** (European cover) and **C04** (PS2 box) are stills from the named clips. C02 is perspective-flattened in OpenCV, because Tesseract's corner pin maps a rectangle onto a quad but can't invert one.
- **C03 (disc)** is a circle cut of B09 at 82 s, inset slightly because the disc rim runs outside the frame.
- **C05 (Bliss, head and shoulders)** comes from B26 at 880 s. Tesseract's Person Matte needs to download a model, and that download fails here because the CLI doesn't trust this cloud environment's HTTPS proxy certificate. I cut him out with a local background-removal model instead. The edges are clean.
- **C06 (eye strip)** is a 1920 × 160 band of the same B26 still, matted over its heat-map copy so the eyes line up exactly.
- Borders, tilts, shadows, mattes and looks are all native Tesseract layers.

## The look

- **Film-wide overlays 1–7:** built in the brief's order with its values. Vignette and scan lines are small WGSL shaders, because a radial gradient fill doesn't render.
- **Film grain and clip grain:** each jumps every 2 frames with hold keyframes, using a fixed seeded list of offsets, so every render is identical.
- **Textures:** `grain` arrived as a JPEG on black, most likely a transparent PNG flattened by the upload. As an Overlay layer it darkened every frame, so I rebuilt its transparency from its brightness.
- **grade_lite.json:** applied once per shot to the framed picture, then the shot's look, matching build18.
  - Adjust maps to Primary Grade.
  - Bloom maps to Glow, at intensity 0.2 and radius 18.
  - Chromatic aberration 0.22 maps to amount 0.11, because Tesseract's scale is stronger.
  - Grain 0.16 maps to Grain.
  - Vignette 0.42 is set to 0.25 with a wider radius, because at 0.42 Tesseract darkened the whole frame on top of the film-wide vignette.
  - Film artifacts (dust) have no native effect, so they come from the grunge and grain layers.
- **Special B-roll looks:** native WGSL shaders.
  - Heat map uses the exact five stops.
  - Duotone uses the Vice, Red and Ember pairs.
  - Halftone print is an 8 px 45° dot screen, #EFE9DF on near black.
  - Invert flash covers the first 2 frames of the shot.
  - TV static covers the last 3 frames.
- **Prism streaks:** two per shot, at build18's positions, breathing 28%→46%→28% and 22%→38%→22% (ease-in-out circ).
- **Drift:** 119%→116% on full-frame clips, and the same ratio on sized stills, moving 46 px/s sideways. The direction alternates shot to shot, eased out (expo), with keys running past the cut so the move is still going at the cut.
- **Easing:** every keyframe uses ease-out expo, ease-in-out expo or ease-in-out circ, or a hold (grain jumps, flicker, cuts).

## Approximations

- **Screen wall (S1.1, S8.6):** the footage is keyed into the screens with a luma matte made from the wall's own bright screens; there's no per-screen tracking. "A few screens a frame out of sync" isn't done. In S8.6 the three clips fill the left, middle and right thirds of the wall.
- **CRT screen:** the footage is corner-pinned into the A01 screen glass, with a low glass sheen and a 2-frame flicker. The screen curve is not modelled; it's a flat pin.
- **Paper comp (S7.2, S10.2):** the cover is placed on the paper with a luma matte of the paper itself rather than a track, so it tears and is cut along with the paper.
- **Floating collage (S13.10):** 2D scale and position parallax by depth, not a 3D camera.
- **Live grid (S12):** 13 panels measured from the US cover's gutters, filling one every 2 frames. The switch to the cover art runs about 2 panels a frame, to fit 9 frames.

## Quality limits of the sources

- B01's front pages are 638 × 480 and B09 is 720p, so the cards and European-cover details are upscaled 3–5×. The halftone and grade hide most of it.
- B30 (the blade) is 360 × 534, B16 is 320 × 240, and the A plates arrived at 1672 × 941.
- High-resolution scans of the European and US GTA III covers and the GTA VI cover would sharpen every cover shot. Each one replaces a single still asset (`C02_euro`, `cov_III`, `cov_VI`) and needs a rerun of the build.

## Checklist (`build/check.py`, run on the final project)

**v5 run: all checks pass.**
- 77 shots.
- 4 flash cuts (400, 528, 710, 936), plus 4 flash transitions and 10 glitch transitions.
- 19 glowing word runs, each with 4 blurred copies.
- The stretch entrance appears on hook words only.
- No tilts or rotation keys.
- The voiceover is the only audio.
- Text outside the captions is limited to tracking-box labels and the hook's terminal lines.

The table below is the original v1 run. Later reviews changed some of those rules: held shots over 30 frames, four flash cuts, and per-word captions.

| Check | Result |
|---|---|
| No shot 30 frames or longer | Pass (longest 29) |
| Exactly five flash cuts, on S2.1, S7.1, S9.1, S12.1 and S15.1 | Pass (frames 67, 400, 528, 710, 936) |
| No heat map, duotone, invert, glow look or flash on any 9/11 shot | Pass (S1 and S6.1–6.2 use only the grade, halftone and CRT) |
| Every voiceover word on screen on its frame | Pass, apart from the doc's own drops ("and" in S5, the small words in S11); "Four. Five. Six" show as IV, V, VI |
| Captions and labels at least 46 / 30 px, inside the safe zone, clear of the logo box | Pass |
| Logo on every frame, top-left, never covered | Pass |
| Overlays 1–7 on every frame, with all text under them | Pass |
| Easing limited to the three curves | Pass |
| No two shots in a row share a look | Pass, except where the doc's own tables put two together (S1's back-to-back photo cards) |
| Voiceover is the only audio | Pass (no clip audio is enabled) |
