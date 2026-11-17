# B18 CTA end card — `b18-cta` (NEW in v05: beat 75f = 2.500 s, no voice; composition 87f with 6f handles)

## v05 (doc "NEW 1:17.0-1:19.5 CTA end card"; REVISION_v05.md "Lane 5" + CLIENT OVERRIDE U1, U2, U4, N3; kit v05)

**Status: complete.** Not rendered. Edit frames 2251-2326 (75.033-77.533 s), after B17's GTA VI logo ("now?") hard cut.
Local frame = CTA frame + 6. Root `data-duration` 2.9000000 (75 + 12 = 87f).

| local (CTA f) | what |
|---|---|
| 0-87 | **kit dark card** (`RCK.fx.darkCardHTML` via `prep/gen_b18.cjs`): #0E0E10 + grain + scanlines + B1's police-lightbar footage blurred 40 px at 20 % (U4: dark, not the doc's off-white card) |
| 0-6 (head) | the card alone (the header waits below the frame) |
| 6-14 (0-8) | profile header slides up from the bottom (y +820 -> 0, 8f, expo.out): dark panel 1130 x 260 at (395, 270), monogram avatar 200 px, "Raw Canvas", the Follow button (#FF2E7E). All Coolvetica (U1) |
| 12-21 (6-15) | the cursor (black arrow, white outline) glides in from bottom right to the button, power3.out |
| 24 (18) | **click** (doc 1:17.6): cursor press 2f / release 3f; the button turns grey (#3A3A40) "Following", 96 -> 100% press; `click` in cues.json |
| 30 (24) | `Comment “BUG” for the full story` appears whole (U2: no type-on), Coolvetica Italic 81 px (doc 54 px @720), white + soft shadow, “BUG” #FF2E7E (the keyword comes from PROFILE) |
| 30-42 (24-36) | the cursor leaves (power2.in) |
| 75-81 (69-75) | the last 6 frames **cross to B1's frame 0** (sine.inOut): the lightbar footage at full frame, playing into B1's f0, so the video loops; 81-87 tail = B1's frames 0-5 (unflashed) |

**The loop** (`hyperframes/b01-hook/LOOP_FRAME.json`, lane 1): B1's f0 = frame 6 of its `b01_lightbar.mp4` (R5.4 GTA V night,
crop 1280:720:380:200, contrast 0.15, static full frame). B18 uses the same recipe started 2.5 s earlier
(`assets/footage/b18_lightbar.mp4`, 3 s, git-ignored working copy: `prep/cut_lightbar.sh`), media time = local / 30, so
**local 81 is B1's frame 0**: measured clip frame 81 vs B1's clip frame 6 = 0.9 / 255 mean difference (the next frame:
1.6); B18's render at 82 vs B1's render at its local 7 differs only by B1's "Why" popping in. The same footage, blurred, is
the card's faint loop, so the cross reads as it coming up to full. B1 plays its own 70 % flash on f0 when the video loops.

**Profile data = ONE config object** at the top of the script (`PROFILE`): `name: "Raw Canvas"`, `handle: ""`,
`followers: ""`, `avatar: ""`, `monogram: "RC"`, `keyword: "BUG"`. The avatar, @handle and follower count are not in the
project (N3): never invented; empty handle / followers lines are hidden (the name centres in the text column), an empty
avatar shows the neutral "RC" monogram (dark grey disc, white Coolvetica). Fill the object when the client sends them
(avatar: put the image in `assets/` and give its path).

**Verification v05**: `check --json` 0 errors (warnings: nested markup; craft `first_frame_empty` = the head handle's card,
`line_unread` = the line holds 1.9 s to the comp end, by design). Snapshots `review/v05/` (12 frames + `sheet.jpg`: header
mid-slide 8, landed 14, cursor on the button 21, "Following" 24, the line 30, the cross 75-81) and `review/v05/check/`
(60, 81 after the clip move), read. Not rendered.
