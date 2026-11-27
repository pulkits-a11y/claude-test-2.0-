"""v8: a waving US flag, drawn from the official proportions and rippled frame by frame, written as a short 30 fps
clip on black (source/flag/us_flag_wave.mp4). Used at 0:14 under "the US".
Run: python build/flag.py (make.py runs it when the clip is missing)."""
import math, os, subprocess
import cv2, numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "source", "flag", "us_flag_wave.mp4")
RED, WHITE, BLUE = (52, 34, 178), (255, 255, 255), (104, 59, 60)        # BGR: #B22234, white, #3C3B6E


def flag(h=520):
    """The flat flag: 13 stripes, the canton over 7 of them, 50 stars in 9 rows (fly 1.9 x hoist)."""
    w = int(round(h * 1.9)); im = np.zeros((h, w, 3), np.uint8); sh = h / 13
    for k in range(13): im[int(round(k * sh)):int(round((k + 1) * sh))] = RED if k % 2 == 0 else WHITE
    cw, ch = int(round(h * .76)), int(round(sh * 7)); im[:ch, :cw] = BLUE
    r = h * .0616 / 2
    for row in range(9):
        for col in range(6 if row % 2 == 0 else 5):
            cx = h * .063 * (2 * col + (1 if row % 2 == 0 else 2)); cy = h * .054 * (row + 1)
            pts = [(cx + (r if i % 2 == 0 else r * .382) * math.sin(i * math.pi / 5), cy - (r if i % 2 == 0 else r * .382) * math.cos(i * math.pi / 5)) for i in range(10)]
            cv2.fillPoly(im, [np.int32(np.round(np.array(pts) * 4))], WHITE, cv2.LINE_AA, shift=2)
    return im


def wave(src, t, W=1200, H=720, ox=90, oy=110):
    """One frame: the flag hung from a pole on the left, rippling (travelling sine, amplitude growing toward the fly)
    and shaded along the folds, on black."""
    h, w = src.shape[:2]; yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    u = (xx - ox) / w                                                     # 0 at the pole, 1 at the fly
    ph = 2 * math.pi * (u * 1.6 - t * 1.25)
    amp = 14 + 34 * np.clip(u, 0, 1)
    dy = amp * np.sin(ph) + 10 * np.clip(u, 0, 1) ** 2                   # a little droop toward the fly
    sx = (xx - ox) * (1 - .04 * np.clip(u, 0, 1) * (1 + np.cos(ph)))     # the fly bunches up slightly in the folds
    sy = yy - oy - dy
    out = cv2.remap(src, sx, sy, cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0).astype(np.float32)
    shade = 1 + .28 * np.cos(ph) * np.clip(u * 1.4, 0, 1)                # light on the crests, shadow in the troughs
    out *= shade[..., None]
    pole = (xx > ox - 16) & (xx < ox - 4) & (yy > oy - 30) & (yy < H - 20)
    out[pole] = (150, 150, 150) * (0.75 + .25 * np.cos((xx[pole] - ox + 10) / 4))[:, None]
    return np.clip(out, 0, 255).astype(np.uint8)


def main(seconds=3.0):
    os.makedirs(os.path.dirname(OUT), exist_ok=True); src = flag()
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", "1200x720", "-r", "30", "-i", "-",
                          "-c:v", "libx264", "-crf", "14", "-pix_fmt", "yuv420p", OUT], stdin=subprocess.PIPE)
    for k in range(int(seconds * 30)): p.stdin.write(wave(src, k / 30).tobytes())
    p.stdin.close(); p.wait()


if __name__ == "__main__":
    main()
