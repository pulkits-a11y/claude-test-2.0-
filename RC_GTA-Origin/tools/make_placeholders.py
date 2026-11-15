#!/usr/bin/env python3
"""Labelled stand-in clips for B-roll that could not be downloaded (YouTube bot check).

One 12 s moving background is rendered once; each R-ID gets a copy with its label burned in.
Output: 04_Broll/_placeholders/<RID>.mp4 (1920x1080, 30 fps, H.264, no audio).
Stand-ins are clearly marked and are replaced by real clips (tools/sync_footage.py prefers real files).
"""
import json, os, subprocess, textwrap

ROOT = "/home/user/claude-test-2.0-/RC_GTA-Origin"
OUT = f"{ROOT}/04_Broll/_placeholders"
FONT_B = f"{ROOT}/06_Fonts/Inter-Bold.ttf"
FONT_M = f"{ROOT}/06_Fonts/Inter-Medium.ttf"
DUR = 12


def esc(s):
    return s.replace("\\", "\\\\").replace(":", "\\:").replace("'", "’").replace("%", "\\%").replace(",", "\\,")


def main():
    os.makedirs(OUT, exist_ok=True)
    bg = f"{OUT}/.bg.mp4"
    if not os.path.exists(bg):
        # slow diagonal stripes drifting right + a soft vignette, so scale/position moves read on screen
        vf = ("geq=lum='38+10*gt(mod((X+Y+T*90)/1.0,160),80)+6*gt(mod((X-Y)/1.0,320),300)':cb=128:cr=128,"
              "format=yuv420p")
        subprocess.run(["ffmpeg", "-nostdin", "-loglevel", "error", "-y", "-f", "lavfi", "-i", f"color=c=black:s=1920x1080:r=30:d={DUR}",
                        "-vf", vf, "-c:v", "libx264", "-crf", "20", "-preset", "veryfast", "-pix_fmt", "yuv420p", bg], check=True)
    man = json.load(open(f"{ROOT}/04_Broll/broll_manifest.json"))["clips"]
    n = 0
    for e in man:
        if e["role"] in ("avoid", "unused-listed", "reference"):
            continue
        dst = f"{OUT}/{e['rid']}.mp4"
        if os.path.exists(dst):
            continue
        desc = textwrap.wrap(e["desc"], 58)[:2]
        lines = [f"drawbox=x=0:y=0:w=1920:h=1080:color=0x000000@0.0:t=fill",
                 f"drawbox=x=40:y=40:w=1840:h=1000:color=0xFFFFFF@0.35:t=3",
                 f"drawtext=fontfile={FONT_B}:text='{esc(e['rid'])}':fontsize=150:fontcolor=white@0.92:x=(w-tw)/2:y=300",
                 ]
        y = 490
        for d in desc:
            lines.append(f"drawtext=fontfile={FONT_M}:text='{esc(d)}':fontsize=46:fontcolor=white@0.85:x=(w-tw)/2:y={y}")
            y += 62
        lines.append(f"drawtext=fontfile={FONT_M}:text='STAND-IN  ·  real clip pending (YouTube download blocked here)':fontsize=30:fontcolor=white@0.7:x=(w-tw)/2:y={y + 40}")
        lines.append(f"drawtext=fontfile={FONT_M}:text='{esc('beats ' + e['beats'] + '  ·  ' + e['role'])}':fontsize=30:fontcolor=white@0.6:x=(w-tw)/2:y={y + 90}")
        lines.append(f"drawtext=fontfile={FONT_M}:text='src %{{pts\\:hms}}':fontsize=28:fontcolor=white@0.6:x=w-tw-70:y=h-90")
        subprocess.run(["ffmpeg", "-nostdin", "-loglevel", "error", "-y", "-i", bg, "-vf", ",".join(lines), "-an",
                        "-c:v", "libx264", "-crf", "20", "-preset", "veryfast", "-pix_fmt", "yuv420p", "-r", "30", dst], check=True)
        n += 1
    print("made", n, "placeholders in", OUT)


if __name__ == "__main__":
    main()
