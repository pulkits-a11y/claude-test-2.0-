#!/bin/sh
# Persist the media-treatment controls the demo needs (run after tools/gen_demo.py). CLI pinned to hyperframes@0.9.52.
set -e
cd "$(dirname "$0")/.."
HF="npx --yes hyperframes@0.9.52"
# X6 motion blur: every medium inside a zoomed world gets a (non-neutral) blur control; the inline
# style="--hf-color-grading-blur: 0" keeps it sharp at rest and RCK.transitions.zoom animates it per frame.
for s in "#g-plate" "#g-pic" "#h-plate" "#h-pic"; do
  $HF media-treatment --selector "$s" --grading '{"effects":{"blur":0.01}}' --apply --json >/dev/null
done
# X4 live views: 6 px RGB split (red +6 px, blue -6 px). Measured on 0.9.52: px = chromaticAberration * W / 50 with W the
# DISPLAYED media width (object-fit: cover of 16:9 footage in the 600 x 450 view = 800 px), so 6 px = 6 * 50 / 800 = 0.375,
# chromaticAngle 0.5 (red right, blue left).
for s in "#d-v1" "#d-v2" "#d-v3"; do
  $HF media-treatment --selector "$s" --grading '{"effects":{"chromaticAberration":0.375,"chromaticAngle":0.5}}' --apply --json >/dev/null
done
echo "treatments applied"
