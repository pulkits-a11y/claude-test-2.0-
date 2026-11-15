#!/usr/bin/env python3
"""STAND-IN ONLY: draw a head-and-shoulders alpha mask (960 x 1080, white = keep) for the R6.1 placeholder.

The real cut-out comes from `npx hyperframes remove-background` on the real R6.1 clip (tools/make_cutout.sh).
This mask only lets the B6 composition, the L5 cut-out matte (8 px white outline + soft shadow) and the layout be
built and reviewed before the real clip exists. Deterministic (no randomness).

usage: python3 tools/bust_mask.py <out.png>
"""
import sys
from PIL import Image, ImageDraw, ImageFilter

W, H, SS = 960, 1080, 4                     # draw at 4x, then downsample: smooth anti-aliased silhouette edge
img = Image.new("L", (W * SS, H * SS), 0)
d = ImageDraw.Draw(img)
s = lambda *v: [x * SS for x in v]
d.ellipse(s(480 - 128, 330 - 160, 480 + 128, 330 + 160), fill=255)                 # head
d.rounded_rectangle(s(410, 440, 550, 640), radius=40 * SS, fill=255)                # neck
d.ellipse(s(480 - 420, 1150 - 520, 480 + 420, 1150 + 520), fill=255)               # shoulders / torso (cut at the frame bottom)
img = img.filter(ImageFilter.GaussianBlur(6 * SS))                                    # round the neck/shoulder joins
img = img.point(lambda v: 255 if v >= 128 else 0)
img = img.resize((W, H), Image.LANCZOS)
img.save(sys.argv[1])
print(sys.argv[1], img.size)
