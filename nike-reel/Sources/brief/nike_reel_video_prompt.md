# Build the Nike Reel: finished 9:16 Instagram video

## 0. Your job

Edit and render a finished vertical video (1080×1920) for RawCanvas's Instagram: **"How Nike lost 80% of its value."** It's a voiceover + B-roll montage + motion-graphics reel, not a talking-head video. It should look and feel like the two reference reels from metromedia.house:

- https://www.instagram.com/p/Df2Q7Gso5UL/ (Peter Thiel)
- https://www.instagram.com/p/DfNWN82R0wR/ (Palmer Luckey)

**Key style reference for graphics and typography:** https://www.instagram.com/p/Df7j97Hux5C/
This one uses a different format from ours, so don't copy its structure or pacing. Copy its **look**:
- **Half Cover graphics** should follow its motion-graphics style.
- **Typography** across the whole video should feel like this reel: captions, Text Centerpieces and overlays alike. Match its type scale, weight contrast, spacing and how its words animate on. Do it using only the patterns in the typography guide, in our fonts and dark theme.
- The **Full Cover motion graphics** being made separately follow this same style. So everything you build (Half Covers, Text Centerpieces) has to look like it belongs next to them.

Watch this reference closely before designing any text or overlay. If you can't open it, stop and ask me for screenshots instead of guessing at the style.

If you can't open them, here's what matters about them. Both open cold on a real interview clip of the subject talking, with its own audio, **before** any voiceover. The 16:9 footage sits letterboxed in the middle of the vertical frame on black. Bold word-by-word captions sit over the footage, and a small logo watermark sits top-left the whole time. After the hook, a voiceover drives a fast montage of archival footage and photo "cards", with motion graphics for the big numbers. The pace never lets up.

**Use the Tesseract skill (by Mirage).** It's installed in this conversation. Load it before you do anything else and follow its workflow for assembling, animating and rendering the video. Where Tesseract has its own way of doing something, its way wins over any tool choice I suggest below. The creative rules in this prompt and the attached guides still apply.


> ## ⚠️ ASK, DON'T ASSUME. This is the most important rule in this prompt.
> **If you have any question or doubt at any point, stop and ask me before going further.** That covers anything at all: a file that won't open, a clip that doesn't match its description, an unclear tag, a color, a font weight, a timing, a style choice, or a rule that seems to conflict with another.
> Don't guess, don't fill gaps with your own assumptions, and don't "pick something reasonable and keep going." A wrong assumption costs far more to fix later than a quick question now.
> When you ask, be specific: say what you're unsure about, the options you see, and which one you'd lean towards. Then **wait for my answer** before building that part.

---

## 1. What's attached (check every item before starting)

| # | File | What it's for |
|---|---|---|
| 1 | `ElevenLabs_..._Hope_-_upbeat_and_clear_..._v4.mp3` | The recorded voiceover (74.4 s at normal speed). The master clock for the whole edit. |
| 2 | `Nike_Reel-Script_Broll_placement.pdf` | The B-roll list: every script line with its tag and the clips (B04–B82) that go under it, plus what to grab from each. |
| 3 | `Transition_Guide___Nike_Reel.pdf` | Rules for every cut and transition. |
| 4 | `Typography_Guide_-_Nike_Reel.pdf` | The only allowed text animations, lockups and exits, by name. |
| 5 | **B-roll footage: Google Drive folder** https://drive.google.com/drive/folders/1GRBbLKL2ugHDsTlG3L7fe0-WotcQ9e8x?usp=sharing | The actual downloaded B-roll files (folders Act1–Act4). File names start with the clip ID: `B04_L02-that-was-2021__<title> [<youtube id>].mp4`. Pull all footage from here. The PDF's YouTube links are **reference only**, telling you what each clip is and which moment to use. Don't download from YouTube. |
| 6 | `CLIP_OLeary.mp4`, `CLIP_Donahoe.mp4`, `CLIP_Hill.mp4` | The three live-audio clips (section 4). |
| 7 | Logo file | RawCanvas logo, used **only** for the subtle top-left watermark. |
| 7b | End card (already made) | The finished end card. Drop it in as-is at the end. Don't rebuild, restyle or add to it. |
| 8 | Brand site: https://www.rawcanvas.co/ | Source of the brand green (section 6). |
| 9 | Font files: `Archivo[wdth,wght].ttf` (variable: width + weight axes) and Instrument Serif (regular + italic) | All on-screen text (section 7). |
| 10 | (Optional) music track and SFX | If attached, use them (section 9). If not, don't invent any; leave the beds silent and list them as missing. |

If you can't open the Drive folder (access or connector), stop and tell me. Don't fall back to YouTube. If anything on this list is missing or won't open, **stop and tell me which item** before building. Don't substitute stock or made-up assets for the logo, fonts or footage.

The PDFs are reference rules and data. Read all three in full; don't skim. Where this prompt and a PDF disagree, this prompt wins.

---

## 2. Hard requirements

1. **Speed the voiceover up slightly: 1.07× tempo, pitch preserved** (e.g. ffmpeg `atempo=1.07`). It should feel tighter and faster without anyone noticing it was sped up: no chipmunk pitch, no artifacts. Listen back to the first and last 10 seconds. If it sounds obviously fast, drop to 1.05×. Time every cut, caption and graphic to the **sped-up** voiceover, never the original.
2. **Logo watermark, top-left, in every frame of the video** (including clips and placeholder screens, but not the attached end card). This is the **only** place the logo is used. Keep it subtle: about 7–8% of frame width, about 60–70% opacity, with a safe margin of about 48 px from the top and left edges. No animation on it.
3. **Full Covers are blank placeholders for now.** Every line tagged [Full Cover] gets a plain screen in the base dark (#121212, section 6), held for exactly as long as those lines run in the voiceover, with the voiceover playing over it and the logo watermark on top. No text, no graphics and no B-roll on these screens. We'll drop the real motion graphics in later, so keep each placeholder as its own clean segment on the timeline, with its start and end times listed in the cut list (section 11).
4. **Text Centerpieces are built for real.** Center-screen text on the plain base dark (#121212), with green as the only accent, animated using the typography guide. They are not placeholders.
5. **Don't change the script wording.** The voiceover is final; captions must match it word for word.
6. **Runtime: under 1:20.** See section 5 for the trims that get it there.
7. **Format:** 1080×1920, 30 fps (the typography guide's frame timings assume 30 fps), H.264 MP4, AAC audio, loudness about −14 LUFS integrated with peaks under −1 dBTP.

---

## 3. The script, with edit tags

A tag applies to every line under it until the next tag. What the tags mean:

- **[B-roll]** (the default): fast montage of clips from the B-roll list, muted.
- **[Full Cover]**: full-screen motion graphic. **For now: blank placeholder** (requirement 3).
- **[Text Centerpiece]**: centered text on a plain background, to emphasize a line.
- **[Half Cover]**: footage plays, with a big text graphic covering about half the frame on top of it.
- **[Special B-roll]**: B-roll with a visual treatment (here: freeze, then drain to black and white).

```
[Half Cover]        LIVE CLIP: CNBC anchor + Kevin O'Leary (own audio)
                    Overlay text on one half: THEY DON'T NEED RETAIL

[Text Centerpiece]  Well, turns out, Nike needed retail more than anyone.

[B-roll]            That was 2021.

[Full Cover]        Nike was soaring at almost 280 billion dollars.
                    Today? Less than 60 billion dollars.
                    Down almost 80 percent.
                    It even got kicked out of the S&P 100.

[Text Centerpiece]  So what happened?

[B-roll]            In 2020, Nike hired eBay's ex-CEO, John Donahoe.

[Full Cover]        His plan? Cut out the middleman.
                    Nike pulled out of stores like DSW and Dillard's, and sent less to Foot Locker.

[B-roll]            Covid made it look genius.
                    Then shoppers went back to stores, and found Hoka and On where Nike used to be.
                    And at the gym, Alo and Vuori became the new flex.

[Half Cover]        LIVE CLIP (BREAK): John Donahoe (own audio)
                    Overlay text on one half: "a little more than we intended"

[Text Centerpiece]  And that was only half the problem.

[B-roll]            Meanwhile, Nike drowned the market in the same shoes.

[Full Cover]        Dunks.
                    Air Force 1s.
                    Retro Jordans.

[Special B-roll]    Until there was no line, and no hype.
                    (a release-day line shot that freezes and drains to black and white on "no hype")

[B-roll]            In 2024, Donahoe was out.
                    His replacement, Elliott Hill, put it simply:

[Text Centerpiece]  LIVE AUDIO (MICRO-BREAK): Elliott Hill
                    "We lost our obsession with sport." in big quote marks, with a small photo of Hill

[B-roll]            The fix has been brutal.

[Full Cover]        Tariffs.
                    China down 26 percent in one quarter.
                    And Nike says sales keep falling into 2028.

[B-roll]            Nike didn't lose to one brand.

[Half Cover]        It gave up the shelf, the hype and the athlete.
                    All at once.
                    (B-roll underneath, one shot per word: SHELF / HYPE / ATHLETE, then "All at once")

[End card]          Hard cut to the attached end card (already made; use as-is)
```

---

## 4. The three live-audio clips

These play with their **own audio**. The voiceover and music stop completely while they run. Each is letterboxed 16:9 in the center of the frame on black, with captions of what the person says.

| Clip | File | Source | Use | Half Cover overlay |
|---|---|---|---|---|
| Intro | `CLIP_OLeary.mp4` | CNBC, Jun 25 2021: https://youtu.be/nnQIdKhxkGs | Kevin O'Leary: "This is why you should be worried about the future of a Walmart or Foot Locker. They don't need retail." | THEY DON'T NEED RETAIL |
| Break | `CLIP_Donahoe.mp4` | CNBC "Why Nike Is Struggling": https://youtu.be/jUzNEoI9PpE | John Donahoe: "...we had over-rotated away from wholesale a little more than we intended." | "a little more than we intended" |
| Micro-break | `CLIP_Hill.mp4` | Same CNBC video | Elliott Hill: "We lost our obsession with sport." (earnings-call audio) | None: this is a Text Centerpiece; use only the audio |

Trim each clip tightly: start on the first word, cut right after the last. No dead air. The intro ends on "They don't need retail". Hard-cut straight into the Text Centerpiece "Well, turns out…", which is the punchline answering him. Name captions in the lower third the first time each person appears: Kevin O'Leary, CNBC, June 2021 / John Donahoe, Nike CEO, April 2024.

---

## 5. Timing and runtime

**Find the line timings yourself from the sped-up audio.** If you can transcribe with word-level timestamps, do that and align it to the script. If you can't, match the pauses in the audio to the script lines. As a cross-check, here are the line starts in the **original 1.0× file** (divide by 1.07 for the sped-up version):

```
0.0  Well, turns out...          19.9 In 2020, Nike hired...      47.4 Dunks.
4.4  That was 2021.              24.4 His plan?...                 48.0 Air Force 1s.
6.1  Nike was soaring...         26.8 Nike pulled out...           49.2 Retro Jordans.
11.1 Today? Less than...         31.5 Covid made it...             50.5 Until there was no line...
13.2 Down almost 80...           33.6 Then shoppers...             53.2 In 2024, Donahoe...
15.4 It even got kicked...       38.2 And at the gym...            55.9 His replacement...
18.2 So what happened?           [BREAK clip after 41.2]           [HILL audio after 58.2]
41.7 And that was only half...   43.7 Meanwhile, Nike drowned...   58.7 The fix has been brutal.
60.7 Tariffs.                    61.7 China down 26...             64.8 And Nike says sales...
68.2 Nike didn't lose...         70.3 It gave up the shelf...      73.4 All at once.   (end 74.2)
```

**Runtime target: 1:15–1:20.** The voiceover at 1.07× is about 69.5 s. Add the clips: O'Leary about 5 s (trimmed to the key sentence), Donahoe about 6 s (starting at "we had over-rotated"), Hill about 3 s, end card about 2 s. That lands at about 1:25. Tighten it with:

- Cut silences between voiceover lines down to 4–6 frames, except before Text Centerpieces and the clips, where a 6–10 frame breath helps.
- If it's still over 1:20, trim the O'Leary clip to just "They don't need retail."
- Don't cut any script lines. Tell me if you can't get under 1:20.

---

## 6. Brand colors (dark theme only)

The whole edit uses a **dark theme with exactly two brand tones**. Leave out the site's white sections and any other colors.

- **Base dark:** a neutral off-black, **not** pure #000 like the website and not grey either. Start from **#121212**. Allowed range: #101010 to #161616, neutral with no blue or brown cast. Use it for every background: Text Centerpieces, Full Cover placeholders, the end card, and the bars around letterboxed footage, so the whole video sits on one consistent dark (the attached end card stays exactly as it was made).
- **Brand green:** RawCanvas's own green. Sample it from https://www.rawcanvas.co/ (the logo and green UI elements; open the site and pick the color, or read it from the site's CSS). Report the hex before using it. If you can't get it from the site, stop and ask me. Don't guess a generic green.
- **Text:** off-white (about #EDEDED) for body text and captions, so it reads on the dark. This is a text color, not a third brand color: no white backgrounds or panels anywhere.
- **Green is the only accent.** Use it for caption keyword highlights, the Highlight-box wipe (dark text on green), accent bars, Half Cover overlay keywords, and key numbers. Use it sparingly, so it stays special.
- **Logo watermark:** use the version that reads on the dark base (light or green).
- Don't use Nike's colors or the Swoosh as a design element.

---

## 7. Typography

Follow the typography guide exactly. Only use its named entrances, lockups and exits, and pick **one whole-video look** before planning anything else. For this reel, use **Stepped**: motion updates every 3rd frame, with a light film-grain texture over the whole frame and a slow drift on held text. It suits the punchy, archival feel of the references. Never mix in Smooth.

Fonts (both attached). Use both throughout the video, in the right variant:

- **Archivo** (variable font: weight and width axes): the workhorse. Captions, filler words, lower thirds, numbers. Captions in SemiBold to Bold (wght about 600–700) at normal width; lower thirds in Medium (about 500); big numbers or a punchy all-caps word can go ExtraBold/Black (800–900), and slightly condensed if a long word needs to fit. Set the variable axes explicitly; don't fall back to a default instance.
- **Instrument Serif** (regular + italic): keywords and display text. The big word in Text Centerpieces, Half Cover overlay keywords, and the Hill quote. Use italic for tone and irony (*only half*, *we intended*, *obsession*), and regular for hard statements (NEEDED RETAIL). Also use the italic for small connector words in a "Connector + keyword" lockup.

Never more than two type styles in one line (the guide's rule).

**Captions:** word-by-word captions for every spoken word, both voiceover and live clips, in the "Caption line" lockup. Captions use quiet entrances only (Ghost-to-solid or Blur-to-sharp), with the key word of each line in the accent color (Highlight-box wipe allowed on that one word). Place them on or just below the letterboxed footage band, centered and inside the safe area: keep clear of the top 220 px and bottom 380 px, where Instagram's UI sits. Keep the normal captions running over the Full Cover placeholders too, since the voiceover still plays there.

**Text Centerpieces:** one keyword per centerpiece gets the loud treatment, and only one loud entrance per scene. Suggested keywords: NEEDED RETAIL / WHAT HAPPENED? / HALF / OBSESSION. Use "Size-contrast build" or "Connector + keyword". The transition guide allows a blur-fade into big single words. Never use the same loud entrance twice in a row.

---

## 8. Footage and transitions

Follow the transition guide. Adapted to this video:

- **There's no A-roll speaker.** Treat the three live clips as A-roll. Everything else is B-roll or a motion graphic (Full Cover placeholder or Text Centerpiece).
- **Every switch between footage types is a hard cut,** landed on the word that introduces the new idea. No dissolves, no preset transitions, no overshoot or elastic easing.
- **Into a Text Centerpiece:** frame 1 is nearly empty; elements build in one at a time (scale about 80→100% with blur clearing, 6–10 frames each, staggered).
- **B-roll:** cut on the voiceover's rhythm. Aim for 0.4–0.8 s per shot, with stretches up to about 1.2 s for a hero shot, and one 2–3-frame burst per act at most. Pick moving shots; add a directional or zoom blur on the first and last 2 frames of static ones.
- **Using the B-roll list:** each script line lists its clips (B##) and what to grab, with timestamps in the original YouTube video for reference. Use the matching file from the Drive folder, matched by B## ID. Clips are trimmed downloads with about 3 s of handle, so the useful moment is near the start. Take several **different** moments from one source if you need more shots, but **never reuse the same moment twice** in the video. B77 is the same source video as B51; use a different moment from it.
- **Framing:** all footage is letterboxed 16:9 in the center of the frame on black, like the references. Punch in 10–20% where a clip has burned-in tickers, lower thirds or channel logos, so they're cropped out. No CNBC/Fox/Bloomberg bugs or tickers should be visible.
- **Special B-roll ("no line, and no hype"):** a release-day line shot (B51 or B52) that freezes on "no" and drains to black and white by "hype". The desaturation runs over about 8–12 frames.
- **"It gave up the shelf, the hype and the athlete":** one shot per word (shelf, then hype, then athlete), each cut on its word, with the word itself as the Half Cover overlay. On "All at once", hard cut to the end-of-video beat.
- **Text on B-roll:** kinetic keyword overlays are allowed on B-roll stretches (Half Cover style), but keep them to the lines tagged Half Cover plus at most two others. Captions carry the rest.

---

## 9. Audio

- **Voiceover:** sped up 1.07× (requirement 1). Light cleanup only: gentle compression, a de-esser if it's sibilant, no reverb.
- **Live clips:** level-match them to the voiceover. Use clean cuts at the clip edges, with a 2–4 frame audio fade to avoid pops.
- **Music:** if a track is attached, keep it about 14–18 dB under the voiceover and duck it further under speech. It should **cut to silence** for each live clip and come back on a hit after. If no track is attached, leave music out and list it in the report.
- **SFX:** only if attached. A whoosh or hit on hard cuts into Text Centerpieces and on the "−80%" moment. Don't overdo it.
- **Mastering:** about −14 LUFS integrated, true peak under −1 dBTP.

---

## 10. End card

The end card is **already made and attached**. On "All at once", hard-cut straight to it and play it as-is: no extra text, logo animation or effects on top. The watermark comes off for the end card. Keep the voiceover's last word clean before the cut. The end card's length counts toward the runtime.

---

## 11. Process and deliverables

Work in this order, and show me the checkpoints:

1. **Pre-flight:** confirm every attachment from section 1, the brand green hex from section 6, the font files and their variants, and which clips are missing from the Drive folder (compare its B## IDs against the B-roll list).
2. **Timing pass:** speed up the voiceover and produce a table of every script line with its start and end time in the sped-up audio, plus where each live clip and placeholder sits. **Show me this table before building.**
3. **Rough cut:** footage and placeholders in place, with no text yet. Send me a contact sheet (one frame every 1 s) and a low-res preview.
4. **Full build:** captions, Text Centerpieces, Half Cover overlays, lower thirds, the watermark and the Special B-roll effect, then the attached end card.
5. **Self-check before delivering:**
   - Runtime is under 1:20.
   - The voiceover doesn't sound sped up.
   - Every caption matches the voiceover word for word and is in sync to within 2 frames.
   - The logo is present on every frame except the end card.
   - No source tickers or channel bugs are visible.
   - No B-roll moment is used twice.
   - Every Full Cover placeholder is blank and exactly as long as its lines.
   - Only named typography patterns are used, in one look (Stepped).
   - Loudness is on target.
6. **Deliver:**
   - The final MP4.
   - A cut list: every cut with its time, footage type, clip ID and source timestamp, text and animation name.
   - A placeholder list: each Full Cover segment's start and end, and the lines it covers, so the motion graphics can be dropped in later.
   - A short list of anything missing or anything you had to decide on your own.

Don't invent facts, footage or brand assets. If something can't be done as written, or anything is unclear, **pause and ask me. Never assume.** (See the rule at the top.)
