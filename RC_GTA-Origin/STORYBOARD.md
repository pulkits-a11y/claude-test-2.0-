# Storyboard: the plan's beat builds pinned to the processed voiceover

Frames are **beat-relative** (f0 = the beat's first word, see `timing/beat_map.json`; composition local frame = beat frame + 6). Word frames are listed per beat (`word@frame`). **Owner**: `HF` = drawn opaque by the beat's HyperFrames composition; `TS+HF` = Tesseract footage underneath (listed in the beat's `tesseract_shots.json`) with a transparent HyperFrames overlay on top; `TS` = Tesseract only. Every decision traces to the plan (page refs to `00_Brief/GTA_VI_Edit_Plan.pdf`); where the plan is silent or self-contradictory the choice is marked **[interp]** or **[conflict Cxx]**, and builders note anything further in their `BEAT_NOTES.md`.

Cue events: every builder writes `hyperframes/<comp>/cues.json` = `{"events": {"name": beatFrame, ...}}` for the SFX/music sync points listed under **Cues** (the Tesseract assembly reads them).

Lanes (one builder per lane, beats built in order so continuity is shared): **A** B1 B2 B3 · **B** B4 B12 B15 · **C** B5 B6 B11 · **D** B7 B8 B17 · **E** B9 B10 · **F** B13 B14 B16.

---

## B1 Hook (143f) · words: Why@1 does@9 every@21 GTA,@36 even@52 GTA@67 6,@79 have@92 you@98 running@106 from@115 the@122 cops?@127 (ends @136)
Plan p.19-20. T1 -> T2. Opens cold: **no fade from black, no logo**; f0 already moving and already shows "Why does".
| frames | owner | picture | text |
|---|---|---|---|
| 0-21 | HF | L4 frosted 4x3 tiles over a police moment from official GTA 6 footage (R1.2, or R17.1). One tile clears per spoken word (3f each, seeded random order): "Why"@1, "does"@9 [interp: plan says "tiles clear one per word"; the L3 cut comes on "every", so 2 tiles clear]. Push-in 100->104%. | T1 "Why does" from f0 |
| 21-52 | HF | Cut on "every": L3 3x2 grid, 8 px gutters, cells pop L->R, top->bottom, 3f apart (f21,24,27,30,33,36; each pop 4f, 96->100% + fade): GTA 1 R1.5, GTA 3 R14.1, Vice City R1.7, San Andreas R1.6, GTA 4 R14.4, GTA 5 R1.3 | T1 "every GTA," @21 |
| 52-143 | HF | On "even": cell 6 switches to official GTA 6 footage (R17.1 or R17.3) and scales to full frame over 6f ease out (f52-58) [interp: "On 'even GTA 6'" read as the phrase onset]. Full frame GTA 6 to the end with push-in. M1: five stars 40 px top-right (x 1700, y 80) pop 3f apart from "have": f92, 95, 98, 101, 104. X9 siren wash on "cops" f127-131. | T1 "even GTA 6," @52 · T1 "have you running" @92 · T2 lead-in "from the" @115, keyword "cops?" blur-in @127 (6f), T2 out = 4f fade f139-143 |
**Cues**: `gta6_cell_full` = 58 (S01 lands here), `cops` = 127 (S02, X9). MU1 = edit 0.
**Handoff to B2**: B2 opens with X6 OUT on this same GTA 6 shot (same R-ID, continuous source time). Stars and T2 do not carry over.

## B2 The bug (180f) · Because@1 back@13 in@22 1995,@26 a@58 game@60 about@66 chasing@73 criminals@87 broke.@101 And@133 that@145 bug@150 saved@157 it.@165
Plan p.20. T7. Bug beat (glitch allowed).
| frames | owner | picture | text |
|---|---|---|---|
| 0-8 | HF | X6 OUT: the GTA 6 frame (continuing B1's footage) shrinks from 600% into the screen of the 1990s CRT monitor (L8, plate from R3.9) over 8f with motion blur | T1 "Because back" @1 |
| 8-26 | HF | GTA 6 picture plays inside the CRT (L8 bulge, scanlines, fringe, flicker); slow push on the plate | T1 "in 1995," @22 |
| 26-101 | HF | Hard cut of the CRT picture to GTA 1 top-down police footage (R9.1) on "1995" [interp: the plan says the picture cuts after the shrink; landed on the key word] | T1 "a game about" @58 · "chasing criminals" @73 |
| 101-133 | HF | On "broke": X4 tear on the CRT picture only (8f, f101-109), picture freezes on the torn frame [interp], then the Windows 95-style error box hard-pops on top at f109 (title "Race'n'Chase", text "This program has performed an illegal operation and will be shut down."; generic, no date, no path) | T1 "broke." @101 |
| 133-172 | HF | Same, slow push-in continues | T7: "And that" @133, bug chip (M4) pops @150 (8f back.out), "saved it." @157 |
| 172-180 | HF | X5 blinds CLOSE over the whole frame (8f) - the out half of B3's transition | (T7 stays under the slats) |
**Cues**: `tear` = 101 (S03 error sound starts 3f before; glitch layered on this frame), `bug_chip` = 150.

## B3 1995, Dundee (215f) · Here's@1 how.@8 It's@22 1995@29 in@54 Dundee,@58 Scotland.@74 DMA@103 Design,@111 the@137 studio@142 behind@151 Lemmings,@160 starts@180 a@190 new@193 game.@197
Plan p.21. T3 -> T4 -> T8 (T1 neutral).
| frames | owner | picture | text |
|---|---|---|---|
| 0-8 | HF | X5 blinds OPEN onto the T3 year card (#E9E9E9) | T1 "Here's how." @1 (#111111 on the card [interp: T1 on a gray card uses card ink]) |
| 8-58 | HF | T3 year card: small *In* + "1995"; digits roll on "1995" @29 (8f each, 2f stagger). Card visible 50f (>= 1 s hold); slow push | T3 "In 1995" (In visible from f22 "It's") |
| 58-103 | TS+HF | X2 into L2 letterboxed old Dundee (R3.1, or R3.2): bars 138 px slide in 8f, clip drifts 60 px sideways over 20f; archival grade | T4 "Dundee," left @58, "Scotland." right @74 (fade 4f + 12 px drift up); both leave together with a 4f fade ending at f103 |
| 103-180 | HF | Hard cut on "DMA": L12 stacked cards on #E9E9E9: R3.8, R3.7, R3.3 drop in 8f each (f103, 111, 119), rotations -6, +3, -2 deg, slow parallax. T8 sits on top; a tiny Lemming (crop of R3.5/R3.6) walks along the underline of "DMA Design" | T8 name "DMA Design" fades in @103 (6f); role "THE STUDIO BEHIND LEMMINGS" fades in @137 ("the studio") [interp: synced to the spoken words]; #111111 on the gray card |
| 180-215 | TS+HF | On "starts a new game": the BBC 1996 footage of the team at their computers (R3.7) in the L2 band, archival grade | T1 "starts a new game." @180 (white, inside the band) |
**Cues**: `year_digits` = first digit move (~29) (S04).

## B4 Race'n'Chase (108f) · It's@1 called@7 Race@18 and@26 Chase,@31 and@46 it's@50 planned@57 to@69 take@76 eighteen@81 months.@88
Plan p.21. T9 -> T2. No SFX (silence by design, plan p.38).
| frames | owner | picture | text |
|---|---|---|---|
| 0-44 | HF | L7: the 1995 design-document title page (R4.5 still - allowed for < 1.5 s, here 44f = 1.47 s, always pushing in 100 -> 118% toward the title), dimmed to 35% except a rounded spotlight on the title | T9 highlight swipes across "Race'n'Chase" on "Race" @18 (8f) |
| 44-108 | HF | Cut to the L9 calendar on the gray card (M3): 18 squares fill L->R, 2f apart, starting @46 so the 18th lands @80, just before "eighteen" [interp]. NO dates on the calendar | T2 above the grid: lead-in "planned to take" @57, keyword "18 months." @81 (#111111 on the card) |
**Cues**: none.

## B5 The cop game (88f) · In@0 it,@3 you@14 play@19 a@26 police@28 officer@37 chasing@50 criminals.@61
Plan p.22. T1. No SFX (the wash is visual only).
| frames | owner | picture | text |
|---|---|---|---|
| 0-88 | HF | L11 split screen (two 958 px halves, 4 px black divider): left a police car in pursuit seen from the cop side (R5.4, or R5.2); right the car being chased (R5.1). M2 yellow arrow + "you" draws on over 8f on "you" @14, pointing at the police car. X9 siren wash on "police officer" @28 (4f). Both cars clearly visible. **This exact frame is reused by B6 and B11.** | T1 "In it," @0 · "you play" @14 · "a police officer" @26 · "chasing criminals." @50 |

## B6 It's dull (166f) · But@0 there's@3 a@12 problem:@13 it's@34 dull.@43 One@61 developer@66 later@84 calls@93 it@108 awful@112 too@131 sim-y.@137
Plan p.22. T2 -> T8. Deliberate hold on the quote (2-second rule exception).
| frames | owner | picture | text |
|---|---|---|---|
| 0-43 | HF | The B5 split screen continues (same clips, continuous source time, arrow gone) | T1 "But there's" @0 · "a problem:" @12 |
| 43-61 | HF | On "dull": the split screen drains to black and white over 6f and slows to 50% | T2 lead-in "it's" @34, keyword "dull." @43 |
| 61-166 | HF | X2 into the L5 gray card on "One": Gary Penn moving clip from the BAFTA talk (R6.1), background removed, on the left; quote card at the right. Props float +/-6 px | T8 name "Gary Penn" + role "DMA DESIGN · GAMASUTRA, 2011" fade in @61 (6f); quote "“awful… too sim-y.”" types on at 2 chars/frame from "awful" @112; holds to the end. Keep quote marks, name and attribution exactly. |
**Cues**: `dull` = 43 (S05). MU3 lands at edit 26.24 s (beat f53).

## B7 Shut it down (96f) · So@0 the@2 people@7 above@17 the@26 team@30 keep@37 trying@44 to@55 shut@59 it@66 down.@70
Plan p.23. T1.
| frames | owner | picture | text |
|---|---|---|---|
| 0-96 | HF | L5 gray card with the early-1990s office clip (R7.1) in a white-bordered frame. CANCELLED stamps (Inter Black 120 px, #E3262E, rough mask) slam on "keep" @37 (-8 deg), "shut" @59 (-4 deg), "down" @70 (+6 deg), offset ~30 px each; each 130 -> 100% over 2f + 4 px camera shake 4f | T1 "So the people" @0 · "above the team" @17 · "keep trying" @37 · "to shut it down." @55 |
**Cues**: `stamp1` = 37, `stamp2` = 59, `stamp3` = 70 (S06 hits start 3f/8f/4f before each; S07 riser from stamp2 to B8 `first_black`).

## B8 The break (63f) · Then,@0 something@20 breaks.@35 (ends @50)
Plan p.23. T10. Bug beat. The only fully silent moment besides the very end: do not fill it.
| frames | owner | picture | text |
|---|---|---|---|
| 0-35 | HF | The B7 stamped card held (its final state, slow push) | T1 "Then, something" @0 |
| 35-45 | HF | On "breaks": the stamp card shatters with X4 (10f) and cuts to black #0A0A0A | (T1 out at 35) |
| 45-63 | HF | Black. T10 "breaks." glitches 6f (45-51), settles clean and holds 12f (51-63), then the hard cut to B9 | T10 "breaks." |
**Cues**: `breaks` = 35 (S08), `first_black` = 45 (S07 ends here; MU4 15f hard mute starts here).

## B9 Straight through you (215f) · The@0 police@5 cars@15 stop@22 following@29 you@49 and@52 start@56 trying@65 to@73 drive@77 straight@84 through@100 you.@108 They@127 ram.@136 They@151 chase.@158 They@178 don't@185 let@196 go.@202
Plan p.23-24. T1 -> T4. No SFX.
| frames | owner | picture | text |
|---|---|---|---|
| 0-127 | TS+HF | L1: GTA 1 top-down police chase (R9.1) at ~60% saturation (grade `b9-sat60`), 105%, soft edges, push 100->104%. Path diagram on top (HF): white dot = player's car; dotted yellow line (#FFE14D, 4 px dots) draws the normal chase path curving behind it (from "stop" @22); on "straight" @84 a solid red arrow (#E3262E, 10 px) shoots straight at the dot and through it over 8f; the dot shakes. Diagram on screen >= 1.5 s | T1 "The police cars" @0 · "stop following you" @22 · "and start trying" @52 · "to drive straight" @73 · "through you." @100 |
| 127-215 | HF | On "They ram.": L3 three vertical strips (8 px gutters): GTA 1 ram (R9.2), GTA 2 chase (R9.3), London 1969 (R9.5); one strip pops per phrase with a 4f punch-in to 115%: @127, @151, @178 | T4 "They ram." @127 · "They chase." @151 · "They don't let go." @178 (each over its strip) |
**Handoff to B10**: the strips keep playing under B10's lead-in until "fun".

## B10 It's fun (57f) · And@0 suddenly,@5 it's@29 fun.@37
Plan p.24. T2. The flash, S09 and the music drop land on the SAME frame (f37).
| frames | owner | picture | text |
|---|---|---|---|
| 0-37 | HF | B9's three strips continue (T4 phrases fade out 4f at f0) | T2 lead-in "And suddenly, it's" @0 |
| 35-41 | HF | X3 white flash centred on "fun": ramp 35-37, hold 37, fade 38-41 (silent) | |
| 37-57 | TS+HF | L1 full-colour GTA 1 kill-frenzy chaos (R10.1) at full speed, saturation +10% (grade `b10-pop`) | T2 keyword "fun." blur-in @37; T2 out 4f fade at the end |
**Cues**: `fun` = 37 (S09, MU5, X3 hold frame).

## B11 The flip (162f) · So@0 the@4 team@10 flips@18 the@28 whole@39 game.@49 You're@63 not@70 the@74 cop@78 anymore.@82 Now@103 you're@108 the@118 one@123 being@129 chased.@137
Plan p.24-25. T1. Cover frame comes from here (plan p.39).
| frames | owner | picture | text |
|---|---|---|---|
| 0-18 | HF | The B5 split screen returns in full colour (identical size/position) | T1 "So the team" @0 |
| 18-28 | HF | On "flips": the whole split screen rotates 180 deg on Y over 10f with motion blur | T1 "flips the whole game." @18 |
| 28-162 | HF | Back side: left the player's getaway car fleeing (R10.2, or R9.1); right police cars chasing (R5.4). On "Now" @103 the M2 arrow redraws over 8f and points at the getaway car | T1 "You're not the cop" @63 · "anymore." @82 · "Now you're the one" @103 · "being chased." @129 |
**Cues**: `flip_start` = 18, `flip_mid` = 23 (S10 peak meets the midpoint).

## B12 Eighteen becomes thirty (83f) · Of@0 course,@4 the@21 eighteen@27 months@40 turn@53 into@65 thirty.@69
Plan p.25. T2. Reuse the exact B4 L9 composition.
| frames | owner | picture | text |
|---|---|---|---|
| 0-83 | HF | The B4 calendar returns with 18 squares filled and the counter "18" (Inter Bold 120 px) at its top-left. On "turn" @53, 12 more squares fill siren red 2f apart (53-75) while the counter rolls 18 -> 30, landing on "thirty" @69. Optional R12.1 clock time-lapse at 10% behind the card (skip while it is a stand-in) | T1 "Of course," @0 (#111111) · T2 lead-in "turn into" @53, keyword "thirty." @69 |
**Cues**: `thirty` = 69 (S11 hit).

## B13 Grand Theft Auto (214f) · Until@1 finally,@10 in@28 November@32 1997,@48 it@85 ships@88 with@97 a@105 new@107 name:@112 Grand@132 Theft@138 Auto.@149 (voice ends @165; no voice 165-214 = the title hold)
Plan p.25. T3 -> T6. Chapter close: the title breathes a full second. [conflict C14: voice gap opened]
| frames | owner | picture | text |
|---|---|---|---|
| 0-85 | HF | T3 year card, same design as B3 (M6): small *In* + "Nov 1997", digits roll on "1997" @48 (same tick sound as B3); card on screen from f0 | T1 "Until finally," @0 (#111111) · T3 "In Nov 1997" (In/Nov on "November" @32, digits @48) |
| 83-89 | HF | X3 white flash centred on the cut at f85 ("it") into L6 | |
| 85-190 | HF | L6: the GTA 1 intro (R13.1) at 62%, 2 px white border, 30 px warm glow, over its own 50 px blurred, 40% darker copy; T6 "GRAND / THEFT / AUTO" types on BEHIND the frame from "Grand" @132, one letter every 2f (14 letters: done @160), holds 1 s (160-190) | T1 "it ships with" @85 · "a new name:" @105 · T6 from @132 |
| 190-214 | TS | Hard cut to the GTA 1 big-box unboxing (R13.2) in the L2 band for the last 0.8 s (24f) | none |
**Cues**: `year_digits` = ~48 (S12, same as S04), `type_on` = 132 (S13). The flash itself is silent.

## B14 Every GTA since (188f) · And@0 every@9 GTA@18 since@28 is@34 built@38 around@49 that@62 chase.@70 The@96 wanted@101 stars.@114 The@133 sirens.@140 The@162 running.@166
Plan p.26. T4. [conflict C15: "the year tags are the only text during the burst" vs T1 captions on the same sentence: the burst carries only the year tags; T1 resumes with "that chase."]
| frames | owner | picture | text |
|---|---|---|---|
| 0-60 | TS+HF | L10 burst: 10 chase clips x 6f in release order (GTA 3 R14.1 x2 "2001", Vice City R14.2 x2 "2002", San Andreas R14.3 x2 "2004", GTA 4 R14.4 x2 "2008", GTA 5 R14.5 x2 "2013"), hard cuts (X1) | tiny year tag per clip (L10 tag: Inter Medium 22 px, top-left) - the only text during the burst |
| 60-133 | TS+HF | GTA 5 five-star chase (R1.3), push-in. M1: six stars fill in, centred, 120 px, on "The wanted stars." (pops 3f apart from @96) | T1 "that chase." @62 · T4 "The wanted stars." top-left @96 |
| 133-160 | TS+HF | Police lights flashing (RT3); X9 siren wash on "sirens" @140 (4f) | T4 "The sirens." centre-right @133 |
| 160-188 | TS+HF | X8 whip pan (6f, 80 px directional blur, f160-166) into an escape shot (R14.5, or R14.6). Last 8f (180-188): X5 blinds CLOSE (HF slats over the footage) - out half of B15's transition | T4 "The running." bottom-left @162; all three T4 phrases stay until the slats close |
**Cues**: `sirens` = 140 (S14), `whip_mid` = 163 (S15 starts 2f before).

## B15 The proof (178f) · Don't@0 believe@5 me?@13 Open@27 GTA@35 Online@41 and@54 buy@61 an@67 arcade.@73 One@100 of@104 the@108 machines@114 is@129 called@132 Race@148 and@151 Chase.@157 (ends @170)
Plan p.26-27. T1 -> T9. Capture the cabinet in GTA Online if possible (the one shot viewers can check).
| frames | owner | picture | text |
|---|---|---|---|
| 0-8 | HF | X5 blinds OPEN onto L7 | T1 "Don't believe me?" @0 |
| 8-160 | HF | L7: arcade interior in GTA Online (R15.3, or R15.4) dimmed to 35% except a rounded spotlight box on the Race and Chase cabinet; slow push-in. T9 label "RACE AND CHASE" pops next to the cabinet on "Race" @148 (4f) | T1 "Open GTA Online" @27 · "and buy an arcade." @54 · "One of the machines" @100 · "is called" @129 · T9 label @148 |
| 160-168 | HF | X6 IN: zoom through the cabinet's screen 100 -> 600% over 8f with motion blur | (label goes with the zoom) |
| 168-178 | HF | Full-frame Race and Chase arcade gameplay (R15.1) | |
**Cues**: `label` = 148 (MU6 low-pass/-6 dB runs from f0 until here), `zoom_mid` = 164 (S16 peak at the zoom midpoint).

## B16 Started with a bug (120f) · So@0 that's@2 why@12 you're@14 always@23 running.@31 The@53 whole@58 series@68 started@79 with@92 a@100 bug.@101 (ends @113)
Plan p.27. T5 -> T7. Bug beat. The one quiet, reflective beat.
| frames | owner | picture | text |
|---|---|---|---|
| 0-30 | HF | VHS rewind (~1 s): the B14 clips, then B9's GTA 1, then the 1995 design document, all reversed at 8x with a VHS look and tracking lines (RT1 not available: media-treatment tape/VHS + drawn tracking lines, labelled stand-in) | T1 "So that's why" @0 · "you're always running." @14 |
| 30-44 | HF | X7 light-leak dissolve (14f) to black #0A0A0A | |
| 44-120 | HF | T5 glow line on black: "The whole series started with a" fades in 12f from "The" @53; the M4 bug chip pops in place of the word "bug" as it is spoken @101 (T7 chip, 8f). On screen >= 1.5 s (f53-120 = 2.2 s) | T5 + T7 chip |
**Cues**: `rewind` = 0..30 (S17 starts at 0; MU7 cuts the music under 0-30, resumes -6 dB from 30), `chip` = 101.

## B17 The loop (196f) · And@1 GTA@8 6?@15 It@38 opens@41 with@51 Lucia@57 already@66 caught.@79 So@103 who's@106 chasing@116 who@131 now?@137 (voice ends @150; 46f logo tail)
Plan p.27-28. T2 -> T10. Bug beat (final X4). Official Rockstar/PlayStation footage only; don't name or imply any voice actor. [B17 wording: open question 5 - the recording says "It opens with Lucia already caught"; Trailer 1 stays on screen so "it" reads as the trailer]
| frames | owner | picture | text |
|---|---|---|---|
| 0-103 | TS+HF | L2 letterbox (bars slide in 8f) on the opening seconds of Trailer 1, Lucia in custody (R17.1). M1: five stars blink at the top-right (40 px, x 1700, y 80 - inside the band edge? keep them inside title-safe) | T1 "And GTA 6?" @1 · "It opens with" @38 · "Lucia already caught." @57 |
| 107-137 | TS+HF | On "So who's chasing who": three fast GTA 6 chase shots, 10f each (plan: 8-10f each): R17.2 @7.2 s, R17.4 @47.2 s, R17.2 @11.9 s (R17.2 = SUBSTITUTE (Rule 5) for the missing R17.3) | T1 "So who's" @103 · T2 lead-in "chasing who" @116 |
| 137-150 | HF | On "now?": hard cut to black with the T2 text | T2 keyword "now?" blur-in @137 |
| 150-170 | HF | The GTA 6 logo (end card of R17.4) pushes in 100 -> 115% over 20f with motion blur; T2 stays on screen | T2 |
| 170-176 | HF | Final hit: X4 tear on the logo and T10 on "now?" (the word breaks apart) | T10 |
| 176-196 | HF | Black; the tail rides S19's decay | none |
**Cues**: `now` = 137, `music_stop` = 150 (MU8 at the end of "now?"), `logo_in` = 150 (S18 rises into the hit), `final_hit` = 170 (S19 = S08's files; the ending echoes the break).
