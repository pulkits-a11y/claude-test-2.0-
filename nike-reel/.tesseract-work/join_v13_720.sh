#!/bin/bash
set -e
cd "$(dirname "$0")/../Previews/v13_720"
printf "file '%s'\n" a.mp4 b.mp4 c.mp4 d.mp4 > list.txt
ffmpeg -hide_banner -y -f concat -safe 0 -i list.txt -i mix.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 256k -shortest -movflags +faststart ../NikeReel_v13_720p.mp4
