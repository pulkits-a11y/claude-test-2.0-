#!/bin/sh
# Usage: sh tools/strip.sh <name> <cols> <frame> ...  -> review/<name>_strip.jpg (labelled thumbnails of review/<name>_fNNN.png)
set -e
cd "$(dirname "$0")/.."
NAME=$1; COLS=$2; shift 2
ARGS=""; FIL=""; i=0
for f in "$@"; do
  ARGS="$ARGS -i review/${NAME}_f$(printf %03d $f).png"
  FIL="$FIL[$i]scale=480:-1,drawtext=fontfile=assets/kit/fonts/Inter-Bold.ttf:text='f$f':fontsize=26:fontcolor=white:box=1:boxcolor=0x000000@0.6:x=8:y=8[v$i];"
  i=$((i+1))
done
N=$i; ROWS=$(( (N + COLS - 1) / COLS ))
L=""; j=0; while [ $j -lt $N ]; do L="$L[v$j]"; j=$((j+1)); done
ffmpeg -nostdin -loglevel error -y $ARGS -filter_complex "${FIL}${L}xstack=inputs=$N:grid=${COLS}x${ROWS}:fill=black" -frames:v 1 "review/${NAME}_strip.jpg" 2>/dev/null || \
ffmpeg -nostdin -loglevel error -y $ARGS -filter_complex "${FIL}${L}concat=n=$N:v=1:a=0,tile=${COLS}x${ROWS}" -frames:v 1 "review/${NAME}_strip.jpg"
echo "review/${NAME}_strip.jpg"
