#!/usr/bin/env bash
# B6 Gary Penn cut-out (plan p.4 "Removing backgrounds for cut-outs (B6 Gary Penn clip): HyperFrames media tools
# (remove-background)"; B6 p.22 "a moving clip of Gary Penn from his BAFTA talk (R6.1), masked out from the background
# on the left").
#
# Output (both modes): assets/footage/R6.1_cutout.webm = 960 x 1080 (8:9 portrait window), VP9 with alpha, 30 fps,
# no audio. index.html shows it in the L5 cut-out prop (#b06-p1, object-fit contain, the kit's white outline + shadow).
#
#   REAL CLIP (when 04_Broll/B06/R6.1__*.mp4 exists):
#     1. set source_in / source_out for R6.1 in 04_Broll/broll_manifest.json (the moment Penn talks to camera,
#        >= 3.7 s long: the cut-out is on screen from beat f61 to the end of the tail handle = 111 frames)
#     2. cd hyperframes/b06-dull && python3 ../../tools/sync_footage.py .        (-> assets/footage/R6.1.mp4, trimmed)
#     3. CROP_X=<left edge of the 960 px window centred on Penn> tools/make_cutout.sh
#        (crop -> remove-background --quality best -> assets/footage/R6.1_cutout.webm)
#     4. re-check, re-snapshot, re-render (see BEAT_NOTES.md "Pending real footage")
#   STAND-IN (now): tools/make_cutout.sh --standin
#     same 960 x 1080 crop of the R6.1 placeholder; the alpha is a drawn head-and-shoulders mask (tools/bust_mask.py),
#     NOT a background removal (the placeholder has no person in it). Clearly a stand-in: the placeholder's
#     "R6.1 ... STAND-IN" label stays visible inside the silhouette.
set -euo pipefail
cd "$(dirname "$0")/.."
CLI="npx --yes hyperframes@0.9.52"
SRC=assets/footage/R6.1.mp4
OUT=assets/footage/R6.1_cutout.webm
CROP_X=${CROP_X:-480}            # PENDING REAL FOOTAGE: placeholder value (window centred on the frame)
[ -f "$SRC" ] || { echo "missing $SRC: run python3 ../../tools/sync_footage.py . first" >&2; exit 1; }
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT
ffmpeg -nostdin -loglevel error -y -i "$SRC" -vf "crop=960:1080:${CROP_X}:0,fps=30" -an \
  -c:v libx264 -crf 12 -preset medium -pix_fmt yuv420p "$TMP/R6.1_crop.mp4"
if [ "${1:-}" = "--standin" ]; then
  python3 -I tools/bust_mask.py "$TMP/mask.png"
  DUR=$(ffprobe -v error -show_entries format=duration -of default=nw=1:nk=1 "$TMP/R6.1_crop.mp4")
  # the looped mask input is limited to the clip's length (alphamerge would otherwise repeat the last frame forever)
  ffmpeg -nostdin -loglevel error -y -i "$TMP/R6.1_crop.mp4" -loop 1 -framerate 30 -t "$DUR" -i "$TMP/mask.png" \
    -filter_complex "[1:v]format=gray[m];[0:v][m]alphamerge,format=yuva420p[o]" -map "[o]" -t "$DUR" -an \
    -c:v libvpx-vp9 -pix_fmt yuva420p -b:v 0 -crf 24 -deadline realtime -cpu-used 8 -row-mt 1 -threads 2 -auto-alt-ref 0 "$OUT"
  echo "STAND-IN (drawn bust mask over the R6.1 placeholder, CROP_X=$CROP_X); replace with tools/make_cutout.sh on the real clip" > assets/footage/R6.1_cutout.SOURCE.txt
else
  $CLI remove-background "$TMP/R6.1_crop.mp4" -o "$OUT" --quality best
  echo "remove-background (hyperframes@0.9.52, --quality best) of assets/footage/R6.1.mp4 cropped 960x1080 at x=$CROP_X" > assets/footage/R6.1_cutout.SOURCE.txt
fi
ffprobe -v error -show_entries stream=codec_name,width,height,pix_fmt,r_frame_rate:stream_tags=alpha_mode -show_entries format=duration -of compact "$OUT"
