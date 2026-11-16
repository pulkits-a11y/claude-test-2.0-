# REVISION v03: your notes on v02 (they override the plan and v02 where they conflict)

Same rule as before: change only what these notes ask; keep everything else as in v02. Your reference images are in `00_Brief/refs_v03/` (1 = "to their PhDs at Stanford," caption lockup over drone footage; 2 = the DMA Design logo; 3 = "so they approached" dark text card with scanlines; 4 = v02 B13 GRAND/THEFT/AUTO (disliked); 5 = v02 B1 frosted grid).

## The notes (verbatim, v02 timestamps)

1. 0:11 "the captions are wrong, it's supposed to say 'It's 1995'" (B3 year card: "In 1995" -> "It's 1995").
2. 0:14 "Do not spell out 'DMA design' through words, add the logo of DMA design ... Use it without the black background." (B3: the logo, cut out, replaces the words "DMA Design,".)
3. "when the article page shows up, there are random red blinks which look really shitty ... Remove it." (B7: no red hits at all.)
4. 0:55 "I don't really like the text GTA behind the screen concept ... Come up with something completely different." (B13 title.)
5. 0:59 "make the wanted stars to glitch in instead of the current opening animation." (B14 M1 stars.)
6. 1:01 "remove the curtain transition, it's really bad, if you've used it anywhere else then remove it." (X5 blinds: B14 close / B15 open -> hard cut. Nowhere else.)
7. 1:07 "there's another missing clip ... just use this massive library of GTA VI / GTA clips" (B15 R15.1 stand-in -> a clip from the Drive library; any other stand-in too.)
8. 0:00 "make the boxes which have gaussian blur dark ... (not pure black, but whatever dark color that we use for the plain background + text)" (B1 L4 grid: the blurred tiles become the dark ink colour; only the two centre tiles show footage.)
9. 0:26 "remove the sliding animation that the guy has and remove his outline as well, and make the background dark ... the quote text ... pop in + blur in animation on a word by word basis" (B6.)
10. 0:19 "instead of showing 'it's planned to take' and then show '18 months', just make the words appear on top the 18 months." (B4: "planned to take" stays, stacked above "18 months.")
11. Captions: "Don't have the pop in zoom in animation / Don't have the Zoom in opening animation / or whatever other variation ... Only have pop in + blur in animation for certain captions where you deem fit - everywhere else, just have the text appear - no opening animation."
12. "Make the whole animation dark aesthetic - make everywhere there's a white background with text, make it a dark background with text." (ref 3)
13. "I regret telling you add zoom ins ... Remove the random zooms throughout the video ... revert that aspect back to how it was without the random zooms."
14. "I want the vignette to be even darker / harder."
15. "I also want [CRT] scanlines instead of the dotted texture, remove that. Keep the noise filter but for some reason it's move so please remove it." (Remove the dust overlay; add CRT scanlines; keep the grain but make it static, not moving.)
16. "Keep the captions in the center as much as you can ... the text which says 'to their PHDs...', I want the captions to be both Centered + Have that layout (only wherever possible ... break the no more than 2 words rule ... the look is what ultimately matters, only treat it as a guideline)."
17. "Make the captions slightly bigger than the size that they are now."
18. "I want a faster result - don't render the video and find a way to show it to me if possible or don't go through the QA check."

## Decisions (v03)

* **Captions (11, 16, 17)**: centred lockups like ref 1: small Coolvetica words + (where a phrase has one) one big Coolvetica Italic keyword, stacked/offset and centred in frame; words simply appear on their spoken frame (hard cut, no animation); only chosen keywords get a pop + blur-in. Bigger than v02. A lockup may hold more than 2 words (guideline). Lockups replace each other with a hard cut.
* **Dark (12)**: every text card that was white/grey (year cards, calendar cards, B6 quote card, B13 "Until finally," card, any plain card) becomes a dark card like ref 3 (near-black, soft glow on white text); the article (B7/B8) is re-captured in the browser's dark mode; the 1995 design document (B4, B16 rewind) is shown as a dark (inverted) page with the highlight re-coloured to stay visible.
* **Zoom (13)**: remove every v02 addition (punch-ins on cuts, keyword punches, zoom-outs, extra Tesseract framing keys). Back to v01's camera: only the plan's own moves (e.g. B4 push 100->118%, L7 spotlight push, the logo push 100->115%) and the slow push on held shots 100->104%, still eased (sine.inOut; nothing linear). The 0:10 zoom-through transition stays (it replaced the curtain you disliked).
* **B13 (4)**: no T6 stack, no L6 frame. The GTA 1 intro footage (R13.1, the D-man) plays full frame, darkened; the caption lockup "it ships with / a new name:" then the title "Grand Theft Auto." big in Coolvetica Italic, each word popping + blurring in on its spoken frame, centred; the 1 s title hold; then the L2 unboxing as before.
* **B14 (5, 6)**: the six hero stars glitch in (RGB split, slice jitter, flicker) one after another instead of the scale pop; no X5 close: hard cut into B15.
* **B15 (6, 7)**: no X5 open (hard cut from B14); the proof shot uses a clip from your Drive library (`04_Broll/_originals/Drive2/`).
* **B1 (8)**: blurred tiles -> dark ink tiles; the two centre tiles keep the footage.
* **B6 (9)**: no float/slide, no white outline on the cut-out, dark card, the quote words pop + blur in on their spoken frames.
* **B4 (10)**: lockup "planned to take" (small, stays) over "18 months." (big italic).
* **B3 (1, 2)**: year card says "It's 1995"; the DMA Design logo (cut out from your image, transparent) replaces the words "DMA Design," over the B-roll.
* **B7 (3)**: no red hits (the S06 hit sounds stay on the headline cut and the two highlighter landings).
* **Finish (14, 15)**: vignette much darker and harder; dust overlay removed; CRT scanlines across the whole edit; grain kept but static (the same grain every frame); chromatic aberration unchanged.
* **Delivery (18)**: no QA pass; preview stills of every change first, then a quick export.
