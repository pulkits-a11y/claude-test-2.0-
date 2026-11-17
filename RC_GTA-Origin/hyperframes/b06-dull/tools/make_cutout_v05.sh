#!/bin/sh
# b06-dull v05 [DEPTH]: the cut-out of Gary Penn that sits OVER the giant pink quote mark (REVISION_v05 lane 2, doc 25.2).
# Made from the exact frames of the full-frame working clip (assets/footage/R6.1.mp4 = footage.json R6.1, crop
# 1024:576:256:0, 1920 x 1080, 30 fps), so it overlays the plate pixel for pixel; only the alpha differs.
#   1. trim to the frames the beat shows (media 0-3.6 s = local 64-172, 108 frames)
#   2. hyperframes remove-background (local model, CLI 0.9.52), WebM VP9 + alpha, quality best (~4 min on CPU)
# Run after `python3 tools/sync_footage.py hyperframes/b06-dull`. tools/make_cutout.sh (v02-v04 bust cut-out) is obsolete.
set -e
cd "$(dirname "$0")/.."
mkdir -p assets/footage/v05
ffmpeg -nostdin -loglevel error -y -i assets/footage/R6.1.mp4 -t 3.6 -an -c:v libx264 -crf 12 -preset medium \
  -pix_fmt yuv420p -movflags +faststart assets/footage/v05/R6.1_trim.mp4
NODE_USE_ENV_PROXY=1 npx --yes hyperframes@0.9.52 remove-background assets/footage/v05/R6.1_trim.mp4 \
  -o assets/footage/v05/R6.1_cut.webm --quality best
