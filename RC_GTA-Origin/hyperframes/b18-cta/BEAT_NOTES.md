# B18 CTA end card — `b18-cta` (NEW in v05: beat 75f = 2.500 s, no voice; composition 87f with 6f handles)

## v05 (doc "NEW 1:17.0-1:19.5 CTA end card"; REVISION_v05.md "Lane 5" + CLIENT OVERRIDE U1, U2, U4, N3)

**Status: phase 1** (layout skeleton + all timing; kit v05 dark card and B1's loop frame still to drop in). Not rendered.
Edit frames 2251-2326 (75.033-77.533 s), after B17's GTA VI logo ("now?") hard cut. Local frame = CTA frame + 6. Root
`data-duration` 2.9000000 (75 + 12 = 87f).

| local (CTA f) | what |
|---|---|
| 0-6 (head) | the empty dark card (the header waits below the frame) |
| 6-14 (0-8) | profile header slides up from the bottom (y +820 -> 0, 8f, expo.out): dark panel 1130 x 260 at (395, 270), monogram avatar 200 px, "Raw Canvas", the Follow button (pink #FF2E7E) |
| 12-21 (6-15) | the cursor (black arrow, white outline) glides in from bottom right to the button, power3.out |
| 24 (18) | **click** (doc 1:17.6): cursor press 2f / release 3f; the button turns grey (#3A3A40) "Following", 96 -> 100% press; `click` in cues.json |
| 30 (24) | `Comment “BUG” for the full story` appears whole (U2: no type-on), Coolvetica Italic 81 px (doc 54 px @720), white + soft shadow, “BUG” #FF2E7E |
| 30-42 (24-36) | the cursor leaves (power2.in) |
| 75-81 (69-75) | the last 6 frames cross (sine.inOut) to B1's frame 0 so the video loops; 81-87 tail = that frame |

**Profile data = ONE config object** at the top of the script (`PROFILE`): `name: "Raw Canvas"`, `handle: ""`,
`followers: ""`, `avatar: ""`, `monogram: "RC"`, `keyword: "BUG"`. The avatar, @handle and follower count are not in the
project (N3): never invented; empty handle / followers lines are hidden (the name centres in the text column), an empty
avatar shows the neutral "RC" monogram (dark grey disc, white Coolvetica). Fill the object when the client sends them
(avatar: put the image in `assets/` and give its path).

**Overrides applied**: U4 dark card (#0E0E10), not the doc's off-white card with grain; U1 everything in Coolvetica (name,
handle, followers, button: Regular; the line: Italic); U2 the line appears whole, no type-on.

**TODO**:
* **B1's loop frame (lane 1)**: `hyperframes/b01-hook/LOOP_FRAME.json` does not exist yet, so `#b18-loop` is a PLACEHOLDER
  (a red / blue gradient). When it exists: add B1's police-lightbar clip to `footage.json` (cut like B1's working copy) and
  put it in `#b18-loop` as a `<video>` with `data-media-start` = B1's in-point - 6/30 s at B1's f0 scale, so local 81 shows
  exactly B1's frame 0 (B1's own 1-frame flash then plays at the loop point).
* Kit v05 dark card: grain + the faint blurred footage (15-25 %) in `#b18-faint`; use the same lightbar clip so the final
  cross reads as that footage coming up to full.

**Verification v05**: `check --json` 0 errors (warnings: kit-style nested markup; craft `first_frame_empty` = the head
handle's empty card, and `line_unread` = the line holds 1.9 s to the comp end, by design). Snapshots `review/v05/`
(12 frames + `sheet.jpg`) read: header mid-slide on 8 and landed by 14, cursor on the button 21-23, "Following" on 24, the
line on 30, the cross 75-81. Not rendered.
