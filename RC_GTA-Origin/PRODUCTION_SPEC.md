# RC_GTA-Origin: production spec (how the Master Edit Plan is executed here)

The **Master Edit Plan** is the golden rule: `00_Brief/GTA_VI_Edit_Plan.pdf` (43 pages, read pages as images with the Read tool's `pages` param) and its text copy `00_Brief/GTA_VI_Edit_Plan.txt` (grep it). This file only records **how** the plan is carried out with this toolchain and the decisions already taken. If this file and the plan disagree, the plan wins, except where a conflict is listed below with the plan's own priority order applied.

Plan priority order on conflicts: (1) Locked script v2, (2) Beat-by-beat build, (3) Beat plan overview, (4) T, L and X libraries, (5) everything else. Every conflict is flagged in `CONFLICTS.md`, never resolved silently. Never add facts, dates, numbers or claims that aren't in the plan. Never add anything new silently: anything new is a clearly labelled suggestion in your notes.

## Folder contract (all paths relative to `RC_GTA-Origin/`)

| Path | What |
|---|---|
| `00_Brief/` | the plan (PDF + text) |
| `01_VO/VO_processed_108.wav` | **the locked voiceover** (81.011 s, 48 kHz; the speed-up result plus the B13 title-hold gap, CONFLICTS.md C14). Every cue is timed to this file |
| `01_VO/VO_words_108.json` | word timings (locked-script spelling) |
| `timing/beat_map.json` | **beat clock**: B1-B17 frames, words with `beat_t` (s from beat start) and `comp_t` (s on the composition clock) |
| `02_Music/` | Black Vertigo (pick), ES Conundrums (backup) + derivatives |
| `03_SFX/` | cue files renamed `S01_...` to `S19_...` |
| `04_Broll/broll_manifest.json` | every R-ID: URL, beats, role, file/status. `04_Broll/Bxx/` real clips, `04_Broll/_placeholders/` stand-ins |
| `05_GFX/` | reusable pieces rendered/exported + `05_GFX/renders/bNN-name.mov` beat renders |
| `06_Fonts/` | Inter (Medium/SemiBold/Bold/Black/Regular) and Instrument Serif (Italic/Regular), OFL |
| `07_Exports/` | exports, `.srt`, cover |
| `hyperframes/_kit/` | the shared HyperFrames style kit (fonts, palette, T1-T10, motifs, transitions) |
| `hyperframes/bNN-name/` | **one HyperFrames project per beat** (the plan: "HyperFrames project folders") |
| `RC_GTA-Origin.tsrct` | the Tesseract project (final assembly, audio, render) |
| `tools/` | scripts (VO processing, timing, placeholders, sync, assembly) |

## Toolchain and who does what (plan p.3-4, applied)

* **Tesseract** (`/root/.local/share/Tesseract/bin/tsrct`, v0.7.0, Linux build with Mesa lavapipe Vulkan; H.264 export needs `--encoder-backend external-ffmpeg-command --ffmpeg-path /usr/bin/ffmpeg`): voiceover (done), the rough cut of **plain footage shots** (L1 full-frame soft edges, L2 letterboxed band, L10 montage burst, any plain full-frame footage), X1 hard cuts and X2 cut-then-drift between those shots, X8 whip, music MU1-MU8, SFX S01-S19, ducking, mix, grade on its own footage, the whole-edit grain, final assembly, export, and the editable `.tsrct`.
* **HyperFrames** (`npx --yes hyperframes@0.9.52 ...`, skills `/hyperframes`, `/hyperframes-cli`, `/hyperframes-registry`, `/media-use`): typography T1-T10 and all captions, graphic screens L3-L9, L11 (incl. the flip), L12, T3 year cards, M1-M4, the error box, the B9 path diagram, transitions X3, X4, X5, X6, X7, X9, background removal (B6 cut-out).
* Handoff (plan p.4): one HyperFrames composition per beat, named `b01-hook`, `b02-bug`, ... (ids in `timing/beat_map.json`), 1920 x 1080 at 30 fps, lasting the beat's length **plus 6f handle at each end**. Composition local time 0 = beat start - 6f; the beat occupies local frames 6 .. 6+dur. Handles hold the opening/closing state continued so the cut can be trimmed.
* **Alpha is supported** (open question 1 answered): HyperFrames 0.9.52 renders ProRes 4444 MOV with alpha and Tesseract composites it correctly (tested). Every beat renders as `05_GFX/renders/bNN-name.mov` (`--format mov`): transparent wherever Tesseract footage shows through, opaque on HyperFrames-owned screens. Audio inside compositions is muted (Tesseract owns all audio).
* For each beat, the builder also writes `hyperframes/bNN-name/tesseract_shots.json` listing the Tesseract-owned footage shots under its overlay (schema below). The Tesseract assembly reads these.
* Lint and preview every composition (`npx hyperframes lint`, `check`, `snapshot`) before `render`.
* Same fonts and colours in both tools: CSS variables in the kit; Tesseract imports the same TTF files.

### `tesseract_shots.json` schema

```json
{"beat":"B3","composition":"b03-dundee","render":"05_GFX/renders/b03-dundee.mov",
 "shots":[{"id":"B3-dundee-band","rid":"R3.1","screen":"L2","start_f":64,"end_f":118,
   "source_in_s":0.0,"speed":1.0,"reverse":false,
   "framing":{"scale_from":100,"scale_to":104,"anchor":"center"},
   "enter":"X2","x2_drift_px":60,"x2_dir":"left","exit":"X1",
   "letterbox":{"bars_px":138,"slide_in_f":8},
   "grade":"archival","notes":"why / what moment to find"}]}
```
`start_f`/`end_f` are **beat-relative frames** (0 = beat start). Since the real footage arrived (see `FOOTAGE_PASS.md`), each shot also carries `"source"` (the original download, `04_Broll/_originals/...`), `"source_in_s"` in seconds of that original file, and an optional `"crop"` (`w:h:x:y`, e.g. to remove a 4:3 pillarbox); the Tesseract assembly cuts its own H.264 working copies from the originals. `grade` is one of `archival` (desaturate ~20%, slight warm lift, subtle grain, light vignette), `game` (punchy contrast, HUD colours untouched), `b9-sat60`, `b10-pop` (full colour, +10% saturation for 1 s), `none`. Screens: `L1`, `L2`, `L10`, `full`.

## Timing rules (plan: Units, Style kit, What good looks like)

* 30 fps. Frame = 1/30 s. "Ease out" = GSAP `power3.out` (cubic-bezier 0.2,0,0,1); T7 overshoot = `back.out(1.7)`; hard cuts = `data-start` boundaries with no tween.
* Captions (T1) hard-cut in **on the first syllable** of the chunk's first word (`comp_t` from `beat_map.json`), hard-cut out when the next chunk starts; 1-3 words per chunk, **never more than 4 words on screen**; within **+/-2 frames** of the voice. Use the chunks exactly as written in each beat's "On screen" line (slashes separate chunks).
* On-screen text matches the spoken words unless a beat says otherwise. Spelling on screen follows the locked script (e.g. `Race'n'Chase`, `sim-y`, numerals exactly as the beat's On-screen line writes them).
* Something changes at least every 2 s (except the B6 quote hold and the B8 black frame). Every held shot gets a slow push-in 100% -> 104%.
* Hard cuts land on the stressed syllable of a key word (or a music downbeat).
* T-style rotation (plan p.13) must hold: no two neighbouring beats feature the same T-style (T1 is neutral).
* Motif discipline: glitch visuals (X4, T10, RGB split, glitch) only in B2, B8, B16, B17; the X9 siren wash only on "cops" (B1), "police officer" (B5), "The sirens." (B14). No other red/blue flashes anywhere.
* Text on footage: soft shadow `0 2px 12px rgba(0,0,0,.45)`; no outlines, no caption boxes (the T9 label is the only box). Text inside title-safe: 96 px from left/right, 54 px from top/bottom.
* Sans carries information; Instrument Serif Italic for the one emotional word (T2 keyword), the small *In* on year cards, the T5 glow line, T8 quotes and names (see CONFLICTS.md C4).
* Palette (CSS vars in the kit): ink black `#0A0A0A`, card gray `#E9E9E9`, card ink `#111111`, white `#FFFFFF`, warm glow `#FFF6E0`, highlighter yellow `#FFE14D` (85%, Multiply), siren red `#E3262E`, siren blue `#2D5BFF`. Use nothing else (placeholder slates are exempt and are replaced by footage).

## Beat clock (from `timing/beat_map.json`; edit total 82.400 s = 2472 frames)

| Beat | start s | start f | dur f | composition |
|---|---|---|---|---|
| B1 | 0.000 | 0 | 143 | b01-hook |
| B2 | 4.767 | 143 | 180 | b02-bug |
| B3 | 10.767 | 323 | 215 | b03-dundee |
| B4 | 17.933 | 538 | 108 | b04-racenchase |
| B5 | 21.533 | 646 | 88 | b05-copgame |
| B6 | 24.467 | 734 | 166 | b06-dull |
| B7 | 30.000 | 900 | 96 | b07-shutdown |
| B8 | 33.200 | 996 | 63 | b08-break |
| B9 | 35.300 | 1059 | 215 | b09-throughyou |
| B10 | 42.467 | 1274 | 57 | b10-fun |
| B11 | 44.367 | 1331 | 162 | b11-flip |
| B12 | 49.767 | 1493 | 83 | b12-thirty |
| B13 | 52.533 | 1576 | 214 | b13-gta |
| B14 | 59.667 | 1790 | 188 | b14-since |
| B15 | 65.933 | 1978 | 178 | b15-proof |
| B16 | 71.867 | 2156 | 120 | b16-bug-origin |
| B17 | 75.867 | 2276 | 196 | b17-loop (incl. 1.5 s logo tail; VO ends 80.868 s) |

Beat boundaries = the first word of each beat (the cut lands on its first syllable). Transitions that span a boundary are split: the **outgoing** composition plays the "out" half up to the boundary frame, the **incoming** composition plays the "in" half from it (e.g. X5: slats shut over the last 8f of the old beat, open over the first 8f of the new beat; X3: ramp 2f before the cut, hold 1f, fade 4f after).

## Footage

YouTube refuses downloads from this container (bot check), so the listed B-roll is not available yet. Each R-ID has a labelled stand-in `04_Broll/_placeholders/<RID>.mp4` (1920x1080, 30 fps, 12 s, moving pattern + label). Beat projects get their footage through `python3 tools/sync_footage.py <beat-project-dir>`, which copies the current file for each R-ID the beat lists into `assets/footage/<RID>.mp4` (real clip if present in `04_Broll/Bxx/`, else the placeholder). Compositions reference `assets/footage/<RID>.mp4` only, so swapping in real footage is: drop the clip in, re-sync, re-render. Never fake a real logo, screenshot or person; the GTA 6 logo comes only from R17.4's end card.

R4.5 (the 1995 design-document scans) is fetched from the three listed web pages; stills are allowed only there, under 1.5 s, always with a push-in or pan.

## Quality gates for every beat composition

1. `npx --yes hyperframes@0.9.52 check --json` clean (fix every error; weigh warnings).
2. Snapshots at every text change and transition, read them (contact sheet in `hyperframes/bNN-name/review/`).
3. Captions = locked-script words, chunked as the beat's "On screen" line, timed from `beat_map.json` within +/-2f.
4. T-style rotation, motif discipline, palette, fonts, safe areas, shadow rule, 2-second rule.
5. Render: `npx --yes hyperframes@0.9.52 render . --format mov --workers 2 -o ../../05_GFX/renders/<id>.mov`, then `ffprobe` (1920x1080, 30 fps, frames = beat + 12, alpha `yuva444p12le`).
6. Beat notes in the plan's 7-part answer structure (what the viewer sees; assets; tool + layer stack; step-by-step build; on-screen text; audio cues with sync frame and level; mistakes to avoid) in `hyperframes/bNN-name/BEAT_NOTES.md`.
