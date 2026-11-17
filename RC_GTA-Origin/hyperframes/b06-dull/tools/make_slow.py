#!/usr/bin/env python3
"""b06-dull v05: bake the "dull." slow-down into the split-screen working clips (REVISION_v05 lane 2, doc 24.4:
"drop the gameplay to 70% speed"). Run from anywhere, after `python3 tools/sync_footage.py hyperframes/b06-dull`:

    python3 hyperframes/b06-dull/tools/make_slow.py

Input : assets/footage/R5.2.mp4, assets/footage/R5.1.mp4 (the B5 windows, 958 x 1080, 30 fps; B6 local 0 = frame 83).
Output: assets/footage/v05/R5.2_slow.mp4, assets/footage/v05/R5.1_slow.mp4, frame n = B6 local frame n (media start 0):
    playback rate 1.0 up to local 46 ("dull."), then an eased change (easeInOutCubic = GSAP power2.inOut, the drain's
    curve and frames) to 0.70 at local 52, then 0.70 to the end. Source frame = 83 + round(integral of the rate), the
    nearest source frame (no frame blending; rounding, not flooring, so the ramp's first frames do not repeat a frame
    while the rate is still ~1). Raw yuv420p in and out (no colour conversion), libx264 crf 10.
"""
import os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
BEAT = os.path.dirname(HERE)
W, H, FPS = 958, 1080, 30
BASE = 83                     # B6 local 0 = working-clip frame 83 (B5 local 83, continuous source time)
K0, K1, SLOW = 46, 52, 0.70   # ramp from "dull." (46) over 6 frames to 70 %
N_OUT = 66                    # B6 shows local 0..63 of the split; 2 spare frames


def ease(x):                  # easeInOutCubic (GSAP power2.inOut)
    return 4 * x ** 3 if x < 0.5 else 1 - (-2 * x + 2) ** 3 / 2


def rate(u):
    if u <= K0:
        return 1.0
    if u >= K1:
        return SLOW
    return 1.0 - (1.0 - SLOW) * ease((u - K0) / (K1 - K0))


def tau(n, steps=400):        # integral of the rate from 0 to n (output frames -> source frames)
    if n <= K0:
        return float(n)
    a = float(K0)
    b = min(float(n), float(K1))
    h = (b - a) / steps
    s = sum(rate(a + (i + 0.5) * h) for i in range(steps)) * h
    t = K0 + s
    if n > K1:
        t += SLOW * (n - K1)
    return t


def source_frames():
    return [BASE + int(round(tau(n))) for n in range(N_OUT)]


def bake(rid):
    src = os.path.join(BEAT, 'assets/footage', rid + '.mp4')
    dst = os.path.join(BEAT, 'assets/footage/v05', rid + '_slow.mp4')
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    fsize = W * H * 3 // 2
    dec = subprocess.Popen(['ffmpeg', '-nostdin', '-loglevel', 'quiet', '-i', src, '-f', 'rawvideo', '-pix_fmt', 'yuv420p', '-'],
                           stdout=subprocess.PIPE)
    enc = subprocess.Popen(['ffmpeg', '-nostdin', '-loglevel', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'yuv420p',
                            '-s', '%dx%d' % (W, H), '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-crf', '10',
                            '-preset', 'medium', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', dst], stdin=subprocess.PIPE)
    want = source_frames()
    idx, cur = -1, None
    for k in want:
        while idx < k:
            buf = dec.stdout.read(fsize)
            if len(buf) < fsize:
                raise SystemExit('%s: ran out of frames at %d (need %d)' % (rid, idx + 1, k))
            cur, idx = buf, idx + 1
        enc.stdin.write(cur)
    enc.stdin.close(); enc.wait(); dec.kill(); dec.wait()
    return dst, want


if __name__ == '__main__':
    for rid in ('R5.2', 'R5.1'):
        dst, want = bake(rid)
        print(rid, '->', os.path.relpath(dst, BEAT), 'source frames', want[0], '..', want[-1],
              '| local 44-56:', want[44:57])
