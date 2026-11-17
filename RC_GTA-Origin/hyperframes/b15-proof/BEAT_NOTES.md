# B15 The proof — `b15-proof` (lane B)

## v05 (REVISION_v05.md lane 4 with the CLIENT OVERRIDE / section U; doc 1:02.0-1:07.0): what changed

Beat / composition unchanged (**data-duration 5.9666667**, 179f). Kit v05, HyperFrames 0.9.52.

| What | v04 | v05 | Why |
|---|---|---|---|
| "Don't believe me?" | T1 line | kit **pill** (text whole on f6, box wipe), out through the pink pixel glitch (pillOut, beat 18) | doc "in a highlight pill"; U3: no punch-in |
| Captions | T1 lines | kit lockups: "Open [GTA Online]* and buy an arcade." (pop on "GTA Online"), "One of the [machines] is called" | U1 / U2 |
| Payoff | 115 % punch-in, 170 % zoom, RACE AND CHASE pill | **removed** (CLIENT OVERRIDE, U3 / U10); the plan's spotlight push 100 -> 118 % kept; the v04 highlighter swipe on "Race" (kit `fx-hl fx-hl--dark`, pink, screen) at 139; **yellow hand-drawn circle** round "RACE AND CHASE: STREET LEGAL" (kit annotate, 124, 9 f) | v04 #18-20, U3, U10 |
| 10-f split (beat 140-150) | | right half = lane 5's shared dark title page (`05_GFX/shared/racenchase_title_page_dark_v05.jpg`, copied to `assets/page/`) framed exactly as B4 shows it (S 1.5, page point (1093, 540) on the half's centre, -4 deg) with B4's pink band on "Race'n'Chase"; 6 px white divider | doc 66.8 "split-screen of the 1995 design doc title" |
| Interior B-roll | | the 4 interior cuts kept (R15.3 @ 229.4 / 156.0 / 232.0 / 160.6 s) | |

`cues.json` (final): events {label 139, zoom_mid 154}; word_pops [0, 25, 51, 57, 63, 69, 94, 98, 102, 121, 124]; key_words
[33, 39, 107]; hit 140. `footage.json`: R15.3, R4.5 (the shared still; `assets/footage/R4.5.png` kept for the credits trail
only), R15.L1 (manifest-free). Check: 0 errors. Snapshots: `review/v05/`. Not rendered.

---

## v04 (REVISION_v04.md, Frame.io review of v03): what changed

Same beat (167f), composition (179f), words, lockups and cues as v03. Frames = beat frames (local = beat + 6).

| What | v03 | v04 | Why (note) |
|---|---|---|---|
| Arcade interior (f-6..124) | one 4.3 s take (R15.3 @ 229.4-233.73) | **four cuts** from R15.3, same total length, cut on the voice: f-6..25 @ 229.40 s (down the stairs onto the floor) / f25-63 @ 156.00 s (running past the PENETRATOR cabinet, rows of cabinets; the game's help text "Your Arcade daily earnings are stored in the safe" shows top-left) / f63-94 @ 232.00 s (the row of Street Crimes cabinets) / f94-124 @ 160.60 s (past the jukebox to the Street Crimes cabinets by the MANAGER'S OFFICE). One push 100 -> 104% (eased) across the section as before. Working clip window 155.9-234.1 (re-cut by `sync_footage.py`; the catalogue plate's media start moved to 35.1333 = the same 191.033 s) | #18 |
| Catalogue (L7, f124-150) | spotlight on RACE AND CHASE: STREET LEGAL | + a **highlighter swipe** over the game's "RACE AND CHASE:" heading (kit dark-surface highlight `.rc-t9-hl`: yellow band, 50% Screen; source x 402-543, y 801-829 around the text measured at x 408-537, y 806-824), wiping left -> right on "Race" (f139, 8f easeOutQuart); it sits inside the 1.4x reframe, so it pushes with the page and takes the X6 zoom blur | #19 |

Checks: `check --json` 0 errors. Snapshots `review/v04/` (19 frames + `sheet.jpg`: each cut's first / last frame, the catalogue
cut, the highlight frames, the zoom, the landing). Not rendered.

---

## v03 (REVISION_v03.md, client notes on v02): what changed

Same beat (167f), composition (179f), words and cues (`{"label": 139, "zoom_mid": 154}`) as v02; only what the notes ask
changed. Frames = beat frames (local = beat + 6).

| What | v02 | v03 | Why (note) |
|---|---|---|---|
| X5 blinds open (f0-8) | slats open onto the arcade | **removed** (no `.rc-x5`, no `blindsOpen`): hard cut from B14 on f0; the head handle shows the arcade interior at 100% | note 6 |
| **Proof shot (R15.1)** | labelled stand-in (Race and Chase gameplay missing) | **R15.L1**, a real clip from the client's Drive library: `04_Broll/_originals/Drive2/Grand Theft Auto VI An Extended Look   Now Playing   Netflix.mp4` (Drive id 1hQEweZ2KaM0rARQbyRiPiDbLsSfq6tjN; Rockstar's official GTA VI "An Extended Look", 3840x2160 30 fps), **in 14.10 s, out 14.87 s** (working clip 14.10-15.10): GTA 6 gameplay, a dirt-bike race up a dusty hill, the player's green bike in a pack of riders, the game's race HUD (LAP 1/2, position 11/12, race timer, minimap); no captions, no watermark. Cut in exactly like the stand-in: inside the cabinet screen during the X6 zoom (fades in f150-153), then full frame from the landing f158 (handoff at the same media time) to the tail end | note 7 |
| Camera | interior push 100 -> 108% + keyword punches on "arcade." / "machines" (nested wrapper); full-frame push 100 -> 106% | interior push 100 -> 104% (f0 -> f124) and full-frame push 100 -> 104% (f158 -> end), both easeInOutSine; no punches, no nested wrapper. The L7 spotlight push 100 -> 118% and the X6 zoom (1379%) are the plan's moves and stay | note 13 |
| Captions | T1 word by word, max 2 words, y 620, eased 3f exit on "Race" | v03 lockups (centred, ref 1; words hard-cut in on their frames): "Don't believe me?" (solo) f0-25 / "Open [GTA Online]* and buy an arcade." f25-94 (the keyword pops + blurs in: GTA f33, Online f39) / "One of the [machines] is called" f94-139, hard cut out on "Race". "Race and Chase." still has no caption (as v02: the game's own RACE AND CHASE: STREET LEGAL heading in the spotlight is the proof; v02 note 7 removed the label) | notes 11, 16, 17 |

Why this clip: the library has no Race and Chase arcade footage; the brief asked for GTA gameplay of a chase or a race,
without captions or watermark. Checked: `vice city game play panzer.mp4` (Vice City tank rampage at Fort Baxter: a
rampage, not a race or chase; mission subtitle / help box burned in at times), `gta city.mp4` (vertical night aerial,
no gameplay), `fast clip.mp4` (2 s fan edit), the Vice City 10th Anniversary trailer and the Vice City DE fan trailer
(cutscenes / fan CGI with title cards), GTA VI Trailers 1 and 2 (cinematics, news overlays), the fan edits and montages
in `Drive2/` (burned-in captions, logos, watermarks). The race shot of the official GTA VI gameplay video reads as "Race"
in the ~0.8 s it is on screen (race HUD, pack of riders) and is not used anywhere else (B17 uses other moments of the
same video: 7.2 s and 11.9 s). Only the chosen file was kept in `Drive2/`; the others were deleted after the look.
`footage.json`: R15.L1 is manifest-free (not in `broll_manifest.json`), so it is recorded under `moments` but not in
`rids` (`tools/sync_footage.py` would stop on an unknown R-ID); its working clip was cut by hand with sync_footage's recipe
(command in the note). R15.1's stand-in copy was removed from `assets/footage/`.

Checks: `check --json` **0 errors** (warnings: nested lockup markup, `line_unread` on the lockups the voice forces and
"last line"). Snapshots `review/v03/` (26 frames + `sheet.jpg`: head handle without slats, every lockup word, the
"GTA Online" pop, the cut to the catalogue, the spotlight push, the X6 zoom frames with the race picture in the cabinet
screen, the landing and the full-frame proof shot) and `review/v03/clip/` (the zoom + landing on the new clip). Not
rendered (v03: snapshots only).

---

## v02 (REVISION_v02.md, client notes on v01): what changed

Beat **167f** (was 178), composition **179f**, root `data-duration="5.9666667"`. Frames below are v02 beat frames (local =
beat + 6). Everything after this section is the v01 record (v01 frames, Inter fonts, the T9 label).

| What | v01 | v02 | Why (note / rule) |
|---|---|---|---|
| **T9 "RACE AND CHASE" label** | yellow label popped beside the cabinet on "Race" (f148) | **removed** (element, pop and its X6 blur entry). The proof is the game's own "RACE AND CHASE: STREET LEGAL" heading inside the spotlight | **note 7** |
| Timing | 178f; "called" f132, "Race" 148 | 167f; "Open" 25, "arcade." 69, "machines" 107, "called" 124, "Race" 139, "Chase." 147 | note 10 |
| T1 captions | 5 chunk clips (up to 4 words) | word by word, max 2 words: Don't 0 / believe me? 5 / Open 25 / GTA Online 33 / and buy 51 / an arcade. 63 / One of 94 / the machines 102 / is called 121 -> eased 3f exit (easeInCubic) ending on "Race" 139; above the slats (z 60), outside the camera wrappers | note 11, rule A |
| X5 open | f0-8, constant speed | f0-8, easeOutQuart (kit v02) | rule C |
| Arcade floor (R15.3 @ 229.4-233.73 s) | f-6..132, push 100 -> 104% linear | f-6..123, push 100 -> 108% (easeInOutSine) on `#b15-int-wrap`; keyword punches on a nested wrapper `#b15-int-key` on "arcade." (f69) and "machines" (f107): 106% in 3f (easeOutExpo), back in 9f (easeInOutSine) | rule D |
| Cut to the catalogue (L7) | X1 on "called" f133 | X1 on "called" f124; R15.3 catalogue @ 191.035 s plays in real time f124-158 (34 of its 35 static frames) | re-time |
| L7 spotlight push | 100 -> 118% f133-160, linear | 100 -> 118% f124-150, easeInOutSine (kit `spotPush` v02) about the STREET LEGAL card | rule C |
| X6 zoom into the cabinet screen | f160-168, cue `zoom_mid` 164 | f150-158 (3f after "Chase."), same geometry and scale 'fill' (1379%, log-space easeInQuad); motion blur as per-frame steps (the plate's local blur loop now uses step cuts, was 1-frame linear tweens); the R15.1 picture fades into the cabinet screen over f150-153 easeOutCubic (was linear); cue `zoom_mid` = 154 | rules C, D |
| R15.1 full frame (STAND-IN, still missing) | f168-178, push 100 -> 104% linear | landing f158 (handoff at the same media time 5.4666 s), push 100 -> 106% (easeInOutSine) to the tail end | rule D |

`cues.json` = `{"label": 139, "zoom_mid": 154}`: `label` keeps its v01 name because the assembly reads it as MU6's end (low-pass
and -6 dB from "Don't believe me?" until here); with the label removed it is now the frame "Race" is spoken. No Tesseract
shots (`"shots": []`, the beat carries its own footage).

Checks: `check --json` 0 errors (warnings: `line_unread` on the short groups the voice forces and on "is called" as "the film's
last line", track density). Snapshots `review/v02/a/` + `sheet_a.jpg`: slats, every caption word, both keyword punches, the cut
on "called", the spotlight push, the zoom frames, the landing. Render `05_GFX/renders/b15-proof.mov`: ProRes 4444, 1920x1080, 30 fps, **179 frames**, `yuva444p12le` (ffprobe, counted).

Still pending (unchanged from v01): **R15.1** (Race and Chase gameplay, the proof shot) is missing; the labelled stand-in stays
inside the cabinet screen and full frame (f150-167).

---


Beat: edit frames 1978-2156 (65.933-71.867 s), **178f**; composition **190f** (6f handle each end; local frame = beat frame + 6).
Render: `05_GFX/renders/b15-proof.mov` (ProRes 4444, 1920x1080, 30 fps, 190 frames, `yuva444p12le`, no audio stream; opaque).
Golden rule: Master Edit Plan p.26-27 (B15 build), p.19 (overview), p.16 (X5, X6, into each beat), p.14 (L7), p.13 (T9), p.11 (T1),
p.29 (no stills as B-roll), p.31-32 (R15.x), p.34 (MU6), p.37 (S16), p.40 (accuracy). STORYBOARD.md B15, CONFLICTS.md C13.

## 1. What the viewer sees

Blinds open on a real GTA Online arcade floor (the player walking past rows of glowing cabinets) under "Don't believe me? / Open GTA
Online / and buy an arcade. / One of the machines / is called"; on "called" a hard cut to the game's own Arcade Games catalogue, dimmed
except a spotlight on the RACE AND CHASE: STREET LEGAL cabinet; a yellow RACE AND CHASE label pops beside it on "Race" and the camera
zooms through the cabinet's screen into the Race and Chase gameplay shot (still a labelled stand-in: R15.1 is missing).

## 2. Assets

| ID | What | Status |
|---|---|---|
| R15.3 | GTA Online arcade business guide: arcade floor walk-through + the in-game Arcade Games catalogue (see "Footage used") | **real**, one working clip `assets/footage/R15.3.mp4` (window 190.9-234.1 s) |
| R15.1 | Race and Chase arcade gameplay (the proof shot): in the cabinet screen during the zoom, then full frame | **MISSING - labelled stand-in** `04_Broll/_placeholders/R15.1.mp4` |
| R15.4 | all GTA Online arcade games (alternative arcade shot) | **MISSING** (not downloaded) |
| R15.2 | Race and Chase arcade music (plan: reference) | real, not used: the whole video is one static key-art image (no gameplay, no cabinet on screen) |
| S16 | Data_Whoosh (PRISFX > Extra), -12 dBFS, peak at 0.96 s | Tesseract (cue `zoom_mid`) |
| MU6 | low-pass ~800 Hz and -6 dB from "Don't believe me?" until the label lands | Tesseract (cue `label`) |

Fonts: Inter Medium 500 (T1), Inter Bold 700 (T9 label). Kit: X5 `blindsOpen`, L7 `spotPush`, T9 `label`, X6 `zoomFit` + `zoom`
(`scale:'fill'`, `handoff`) + `zoomGeometry`/`zoomPlan`/`blurValue`, rule-7 `push`. No cut-outs.

## 3. Tool and layer stack

HyperFrames only; opaque the whole beat (the composition carries its own footage; `tesseract_shots.json`: `"shots": []`).

Top to bottom:
1. T1 captions `#b15-cap-1..5` (z 60, screen space, above the slats).
2. X5 slats `#b15-x5` (z 50), f-6..8.
3. `#b15-full-wrap` > `#b15-full` full-frame R15.1 stand-in (z 3), f168-184 (X6 handoff; pushed 100 -> 104%).
4. `#b15-world` (X6 zoom, z 2) > `#b15-l7` (L7 push) > T9 label `#b15-t9` > dim `#b15-dim` > screen picture box `#b15-screen`
   (R15.1, hidden until f160) > static reframe `#b15-catframe` (1.4x about 241, 1080) > `#b15-plate` (R15.3 catalogue), f133-167.
5. `#b15-int-wrap` (rule-7 push) > `#b15-int` R15.3 arcade floor (z 1), f-6..132.

## 4. Step-by-step build (beat frames; seconds = (frame + 6) / 30)

1. **f-6..0** head handle: X5 slats shut (12 x 160 px ink black #0A0A0A) over the arcade floor at push 100%.
2. **f0-8 X5 in half**: `blindsOpen` at f0 (slats 0 -> -90 deg, 8f, constant speed), removed on f8. B14 closes them over its last 8f.
3. **f0 T1** "Don't believe me?" hard cut in on the first syllable, above the slats.
4. **f-6..132 the arcade floor** (R15.3 @ 3:49.4-3:54.0, one continuous take, no game cuts): the player walks down the stairs past
   rows of upright cabinets ("Choose Your Side", "Street Crimes: Gang Wars Edition"...). Rule-7 push 100% (f0) -> 104% (f133) about
   the centre. Game grade via media-treatment: `adjust.contrast +0.15` (HUD colours untouched).
5. **T1 chunks** (unchanged), each hard cut in on its first word and out on the next chunk: f27 "Open GTA Online", f54 "and buy an
   arcade.", f100 "One of the machines" (over the rows of machines), f129 "is called" (out f148, where T9 takes over).
6. **f133 X1 hard cut on "called"** (word onset f132.2) to **L7 on the catalogue**: R15.3 @ 3:11.035-3:12.170, the game's own Arcade
   Games page on the arcade's laptop, resting on the row RACE AND CHASE: STREET LEGAL / GET TRUCKIN / CROTCH ROCKETS (the page is
   static for exactly these 35 frames, so it plays in real time f133-167 and never holds a frame). Static reframe `#b15-catframe`
   `scale(1.4)` about (241, 1080): the source's bottom edge stays on the frame bottom (the row sits at the bottom of the recording),
   the row grows and the game's help-text box (top-left) leaves the frame. Dim #0A0A0A at 65% (35% shows) with a rounded 20 px
   feathered hole `data-hole="366,681,548,430"` (r 16) on the STREET LEGAL card (heading + cabinets; source x 330-722, y 795-1080;
   the bottom runs off-frame). `spotPush` 1.00 (f133) -> 1.18 (f160), linear, about the hole centre (640, 896).
7. **f148 T9 label** "RACE AND CHASE" pops over 4f (96 -> 100% + fade, `power3.out`, lands f152) inside the pushed L7, right of the
   card, centred on the cabinet screen: layout top-left (930, 871) -> on screen ~959-1390 x 868-940.
8. **f160-168 X6 IN** through the yellow STREET LEGAL cabinet's main screen: the 16:9 picture rect inside it = source (595.5, 932.9,
   84 x 47.25) -> frame (737, 874, 118 x 66.375) at push 100% -> (754.46, 870.04, 139.24 x 78.32) on f160. `X.zoom(..., scale:'fill')`
   = **1379%** (13.79x) log-space `power1.in`, origin so the screen centre lands on the frame centre; the R15.1 box (`zoomFit`, laid out
   1920 px wide, res 16.27) fades in over f160-163 on top of the real cabinet screen; motion blur: kit plan on the screen picture,
   dim and label (blurRef 540/1.18, blurMax 24/1.18), and the same plan divided by the extra 1.4x on the plate (local code). The label
   goes with the zoom.
9. **f168** landing: `handoff` = plain full-frame R15.1 at the same media time (5.8 s), **f169-178** full frame, push 100 -> 104% to
   the tail-handle end. Tail handle = the shot continued.

## 5. On-screen text

| Text (exact) | Style | Position / size | Frames |
|---|---|---|---|
| `Don't believe me?` | T1 Inter Medium 46 px, white, soft shadow | centred x 960, y 620 | f0-27 |
| `Open GTA Online` | T1 | same | f27-54 |
| `and buy an arcade.` | T1 | same | f54-100 |
| `One of the machines` | T1 (4 words, the maximum) | same | f100-129 |
| `is called` | T1 | same (above the spotlight from f133) | f129-148 |
| `RACE AND CHASE` | T9 label: Inter Bold 40 px caps, #111111 on #FFE14D, 12 x 20 px padding, 4 px radius | right of the cabinet card | f148 pop (4f) -> carried off by the zoom f160-168 |

The catalogue itself shows the game's own "RACE AND CHASE: STREET LEGAL" heading inside the spotlight (the checkable proof).

## 6. Audio

* **S16** Data_Whoosh, -12 dBFS, peak at 0.96 s: start **f135** so the peak meets the zoom midpoint **f164** (`zoom_mid`; CONFLICTS C13).
* **MU6**: low-pass ~800 Hz and -6 dB from "Don't believe me?" (f0) until the label lands (`label` = **f148**), then open it again.
* No sound on the X1 cut at f133 or on X5. `cues.json`: `{"events": {"label": 148, "zoom_mid": 164}}` (unchanged, still true).

## 7. Mistakes to avoid

* Never spotlight or label a cabinet that is not Race and Chase: the R15.3 arcade floor has none (all its machines are other games).
* Do not hold the catalogue page longer than its 35 static frames (plan p.29: no static images as B-roll; stills < 1.5 s).
* Keep the screen-picture rect 16:9 and centred on the real cabinet screen, or the X6 landing will not match the full-frame clip.
* Keep the label inside the zoom world and the captions outside it. No glitch, no siren wash in B15; slats ink black.
* Never CSS-filter the footage (grade and blur only via media-treatment).

## Footage used

| R-ID | File (04_Broll/_originals/...) | In-out (s, original) | Beat frames | What it shows | Link |
|---|---|---|---|---|---|
| R15.3 | `B15/R15.3__Complete Arcade Business Guide & Buyers Guide ｜ GTA Online Diamond Cas [E0TK4V7YjFo].mp4` | 229.40-234.00 | f-6..132 | GTA Online arcade floor, player walking past rows of cabinets (HUD: minimap, cash, one kill-feed line with a masked gamertag) | https://www.youtube.com/watch?v=E0TK4V7YjFo&t=229 |
| R15.3 | same | 191.035-192.170 | f133-167 | the game's Arcade Games catalogue on the arcade laptop: RACE AND CHASE: STREET LEGAL / GET TRUCKIN / CROTCH ROCKETS (prices, not owned) | https://www.youtube.com/watch?v=E0TK4V7YjFo&t=191 |
| R15.1 | stand-in `04_Broll/_placeholders/R15.1.mp4` (labelled slate) | 0-6.33 (stand-in) | f160-184 | placeholder for Race and Chase gameplay | (plan: https://www.youtube.com/watch?v=xGN6cKeZdN8) |

Working clip: `footage.json` moment R15.3 190.9-234.1 (both moments in one window), `python3 tools/sync_footage.py hyperframes/b15-proof`.

## Substitutions

* `SUBSTITUTE (Rule 5): R15.3 Complete Arcade Business Guide & Buyers Guide | GTA Online Diamond Casino [E0TK4V7YjFo] @ 03:11-03:12 for R15.4 (missing) and for the Race and Chase cabinet inside the arcade interior (the R15.3 arcade floor shows no Race and Chase cabinet: its owner bought only upright cabinets; the three Race and Chase cabinets appear only in the game's own Arcade Games catalogue, unbought).` Consequence [interp, flagged]: the arcade interior carries f0-132 without a spotlight (no target in it), and L7 (dim + spotlight + push 118% + label) runs on the catalogue f133-160, cut on "called".
* R15.1 (Race and Chase gameplay) is **missing** and has **no substitute**: R15.2 is one static key-art image for its whole 94 s; R15.3 never plays the game. The labelled stand-in stays for f160-184 (inside the cabinet screen during the zoom, then full frame). **BLOCKING for the final proof shot.**

## Interpretations / conflicts

* **X6 scale 1379% ('fill') instead of 600%**: the real cabinet screen is 118 px wide at push 100% (139 px on f160); 600% would leave
  it 835 px wide, so it would not "become the frame" (X6's purpose, p.16). The kit's `scale:'fill'` is used: the zoom ends exactly
  when the screen's picture is the frame. A 3.2x reframe would have kept 600% but turned the spotlight into the whole frame.
* **L7 push 100 -> 118% over 27f** (f133-160): the L7 library number (p.14) is kept although the shot is short; B15's "slow push-in"
  (p.26) cannot be slow in 0.9 s. It leads into the zoom.
* **R15.1 picture fades into the cabinet screen over the zoom's first 3 frames** (the real cabinet screen shows during L7).
* T1 above the X5 slats; label right of the card; game grade contrast +0.15 [values = SUGGESTION]; "Don't" straight apostrophe.
* Check warnings kept: craft `line_unread` (voice timing governs) and on the label as "the film's last line"; lint `timeline_track_too_dense`.

## Still pending

* **R15.1** (the proof shot, missing): when it arrives, add a moment for R15.1 in `footage.json` (a readable Race and Chase moment, >= 6.4 s
  from the in-point: the screen picture plays media 0-5.8 s, the full frame 5.8-6.33 s), re-sync, re-check, re-render. No geometry change.
* **SUGGESTION** (plan p.27 Watch out): capture the cabinet in GTA Online yourself - an arcade with a Race and Chase cabinet bought, a
  frontal moment of it on the floor, then its gameplay. That replaces both the catalogue substitute and the R15.1 stand-in and restores
  the plan's single interior L7 shot (re-fit `data-hole`, `SCREEN_100`, the reframe and the label spot).
* R15.4 (missing) could also show the cabinet on an arcade floor; same re-fit if used.

## Kit problems worked around

* X6 blur model sizes the blur by the zoom scale only: the world is also pushed 1.18x (blurRef/blurMax / 1.18) and the plate has an
  extra static 1.4x (its blur values are computed locally with `X.zoomPlan` / `X.blurValue` divided by 1.4).

## Verified (snapshots `review/`, contact sheets `contact-sheet-1.jpg`, `contact-sheet-2.jpg`)

* f-6, f0 (slats shut + T1), f4, f8 (interior), f100, f132 (last interior frame), f133 (cut: spotlight on STREET LEGAL), f148 / f152
  (label), f159, f160-167 (zoom: picture lands inside the yellow cabinet's screen), f168 / f169 (landing = stand-in, same media
  time), f183.
* `check --json`: 0 errors; warnings as listed. Render: 190 frames, `yuva444p12le` (ffprobe).
