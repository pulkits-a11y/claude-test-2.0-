# B17 The loop - `b17-loop` (beat 196f = 6.533 s incl. the 46f logo tail; composition 208f with 6f handles)

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

## BLOCKING
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
