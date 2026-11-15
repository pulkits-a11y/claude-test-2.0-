#!/bin/sh
# Capture the X4 "old frame" stills exactly as a beat does it: the stills are registered in x4_stills.json and made by the
# shared tool (snapshot of the composition with the tear disabled and the demo labels hidden, cropped to the container),
# which also records the input hashes in assets/x4/SOURCES.json. Check: python3 ../../tools/make_x4_stills.py . --check
set -e
cd "$(dirname "$0")/.."
python3 ../../tools/make_x4_stills.py .
