# Nike Reel: timing pass (provisional)

Voiceover: `Sources/voiceover/VO_1.07x.wav` (ffmpeg `atempo=1.07`, pitch preserved), 69.52 s. 30 fps.
Source in/out = the line's speech in the 1.07x file (silence-detect at -42 dB + Whisper word times).
Edit in/out = position in the final video after tightening pauses (5 frames between lines, 8-frame breath before Text Centerpieces and clips).
Live-clip lengths are the prompt's estimates until the clips arrive; everything after a clip shifts with its real length.

| # | Tag | Line | Source in-out (s) | Edit in-out (s) | Len (s) |
|---|---|---|---|---|---|
| CLIP_OLEARY | Half Cover (live clip) | Kevin O'Leary: "...They don't need retail." | clip (est.) | 0.00-5.00 | 5.00 |
| 1 | Text Centerpiece | Well, turns out, Nike needed retail more than anyone. | 0.00-3.63 | 5.27-8.90 | 3.63 |
| 2 | B-roll | That was 2021. | 4.11-5.34 | 9.07-10.30 | 1.23 |
| 3 | Full Cover | Nike was soaring at almost 280 billion dollars. | 5.69-9.16 | 10.47-13.93 | 3.47 |
| 4 | Full Cover | Today? Less than 60 billion dollars. | 9.55-12.01 | 14.10-16.57 | 2.47 |
| 5 | Full Cover | Down almost 80 percent. | 12.33-13.92 | 16.73-18.33 | 1.60 |
| 6 | Full Cover | It even got kicked out of the S&P 100. | 14.38-16.50 | 18.50-20.60 | 2.10 |
| 7 | Text Centerpiece | So what happened? | 16.95-18.15 | 20.87-22.07 | 1.20 |
| 8 | B-roll | In 2020, Nike hired eBay's ex-CEO, John Donahoe. | 18.62-22.30 | 22.23-25.93 | 3.70 |
| 9 | Full Cover | His plan? Cut out the middleman. | 22.77-24.56 | 26.10-27.90 | 1.80 |
| 10 | Full Cover | Nike pulled out of stores like DSW and Dillard's, and sent less to Foot Locker. | 24.98-29.08 | 28.07-32.17 | 4.10 |
| 11 | B-roll | Covid made it look genius. | 29.44-31.04 | 32.33-33.93 | 1.60 |
| 12 | B-roll | Then shoppers went back to stores, and found Hoka and On where Nike used to be. | 31.36-35.29 | 34.10-38.03 | 3.93 |
| 13 | B-roll | And at the gym, Alo and Vuori became the new flex. | 35.65-38.55 | 38.20-41.10 | 2.90 |
| CLIP_DONAHOE | Half Cover (live clip) | John Donahoe: "...we had over-rotated away from wholesale a little more than we intended." | clip (est.) | 41.37-47.37 | 6.00 |
| 14 | Text Centerpiece | And that was only half the problem. | 38.95-40.48 | 47.63-49.17 | 1.53 |
| 15 | B-roll | Meanwhile, Nike drowned the market in the same shoes. | 40.82-43.91 | 49.33-52.40 | 3.07 |
| 16 | Full Cover | Dunks. | 44.27-44.72 | 52.57-53.03 | 0.47 |
| 17 | Full Cover | Air Force 1s. | 44.88-45.73 | 53.20-54.03 | 0.83 |
| 18 | Full Cover | Retro Jordans. | 45.93-46.91 | 54.20-55.17 | 0.97 |
| 19 | Special B-roll | Until there was no line, and no hype. | 47.18-49.24 | 55.33-57.40 | 2.07 |
| 20 | B-roll | In 2024, Donahoe was out. | 49.72-51.86 | 57.57-59.70 | 2.13 |
| 21 | B-roll | His replacement, Elliott Hill, put it simply: | 52.26-54.43 | 59.87-62.03 | 2.17 |
| CLIP_HILL | Text Centerpiece (live audio) | Elliott Hill: "We lost our obsession with sport." | clip (est.) | 62.30-65.30 | 3.00 |
| 22 | B-roll | The fix has been brutal. | 54.83-56.41 | 65.47-67.03 | 1.57 |
| 23 | Full Cover | Tariffs. | 56.76-57.37 | 67.20-67.80 | 0.60 |
| 24 | Full Cover | China down 26 percent in one quarter. | 57.63-60.24 | 67.97-70.57 | 2.60 |
| 25 | Full Cover | And Nike says sales keep falling into 2028. | 60.56-63.30 | 70.73-73.47 | 2.73 |
| 26 | B-roll | Nike didn't lose to one brand. | 63.76-65.36 | 73.63-75.23 | 1.60 |
| 27 | Half Cover | It gave up the shelf, the hype and the athlete. | 65.66-68.28 | 75.40-78.00 | 2.60 |
| 28 | Half Cover | All at once. | 68.63-69.41 | 78.17-78.93 | 0.77 |
| END | End card (as-is) | attached CTA, 2.26 s | - | 79.07-81.33 | 2.27 |

## Full Cover placeholders (blank #121212 + VO + watermark)

| Placeholder | Lines | Edit in-out (s) | Len (s) |
|---|---|---|---|
| FC1 | 3-6 | 10.47-20.87 | 10.40 |
| FC2 | 9-10 | 26.10-32.33 | 6.23 |
| FC3 | 16-18 | 52.57-55.33 | 2.77 |
| FC4 | 23-25 | 67.20-73.63 | 6.43 |

**Runtime:** 81.33 s with the full O'Leary sentence (est. 5.0 s); 77.83 s if O'Leary is trimmed to "They don't need retail." (est. 1.5 s).
