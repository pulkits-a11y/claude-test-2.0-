#!/bin/bash
# Live-clip sources (full videos) and the six B-roll clips missing from Drive (needed range only).
R="$(cd "$(dirname "$0")/.." && pwd)"
F='bv*[height<=1080][vcodec^=avc1]+ba[ext=m4a]/bv*[height<=1080]+ba/b[height<=1080]'
dl() { # out url [section]
  for try in 1 2 3; do
    if [ -n "$3" ]; then yt-dlp --no-warnings -q --no-progress -f "$F" --merge-output-format mp4 --download-sections "$3" -o "$1" "$2" && break
    else yt-dlp --no-warnings -q --no-progress -f "$F" --merge-output-format mp4 -o "$1" "$2" && break; fi
    echo "retry $try $1"; sleep $((try*20))
  done
  [ -f "$1" ] && echo "ok $1 $(ffprobe -v error -show_entries format=duration -of csv=p=0 "$1")s" || echo "FAILED $1"
  sleep 8
}
dl "$R/Sources/liveclips/SRC_CNBC_Why-Nike-Is-Struggling_jUzNEoI9PpE.mp4" "https://www.youtube.com/watch?v=jUzNEoI9PpE"
dl "$R/Sources/liveclips/SRC_CNBC_OLeary_2021-06-25_nnQIdKhxkGs.mp4" "https://www.youtube.com/watch?v=nnQIdKhxkGs"
dl "$R/Sources/broll/B20.mp4" "https://www.youtube.com/watch?v=i6oXZQX8EdU" "*0-35"
dl "$R/Sources/broll/B36.mp4" "https://www.youtube.com/watch?v=73O81rxazoQ" "*0-28"
dl "$R/Sources/broll/B80.mp4" "https://www.youtube.com/watch?v=LA-C4-ba9Rw" "*0-125"
dl "$R/Sources/broll/B81.mp4" "https://www.youtube.com/watch?v=gWtX92CTjd4" "*0-150"
dl "$R/Sources/broll/B82.mp4" "https://www.youtube.com/watch?v=LFsXnUn4k90" "*0-65"
dl "$R/Sources/broll/B55.mp4" "https://www.youtube.com/watch?v=K_p5mXd2VKc" "*0-240"
echo DONE
