#!/usr/bin/env bash
# Adds the media-treatment blur control to the zoom-through's outgoing footage (#c-v), as a beat must do for any
# <video>/<img> inside a camera wrapper that zooms through with blur (footage is never CSS-filtered).
# Run from _demo-v02 after tools/gen_demo.cjs.
set -euo pipefail
npx --yes hyperframes@0.9.52 media-treatment --selector "#c-v" --grading '{"effects":{"blur":0.01}}' --apply --json
