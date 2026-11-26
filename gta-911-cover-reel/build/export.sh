#!/bin/bash
# Renders the reel in two parallel segments (software Vulkan renderer here), joins them losslessly and muxes the
# voiceover straight from the processed WAV. Output: GTA911_CoverReel.mp4 (1920x1080, 30 fps, H.264 + AAC, VO only).
cd "$(dirname "$0")/.."
X=~/.local/share/Tesseract/bin/tsrct; E=.tesseract-work/export
seg() { $X export --project GTA911_CoverReel.tsrct --output $E/seg$1.mp4 --resolution 1080p --fps 30 --start-ms $2 --duration-ms $3 \
        --encoder-backend external-ffmpeg-command --ffmpeg-path "$(command -v ffmpeg)" > $E/seg$1.log 2>&1; echo "seg$1 exit $?"; }
seg 1 0 17600 & seg 2 17600 17633 & wait
printf "file 'seg1.mp4'\nfile 'seg2.mp4'\n" > $E/list.txt
ffmpeg -v error -y -f concat -safe 0 -i $E/list.txt -c copy -an $E/video.mp4
ffmpeg -v error -y -i $E/video.mp4 -i source/audio/GTA911_VO_tight_118.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 256k -shortest -movflags +faststart GTA911_CoverReel.mp4
ffprobe -v error -show_entries stream=codec_name,width,height,r_frame_rate,nb_frames:format=duration -of compact GTA911_CoverReel.mp4
echo EXPORT_DONE
