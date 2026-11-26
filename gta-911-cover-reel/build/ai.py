"""v6: the client's AI-generated plates (source/ai/) with Bliss's real art composited in.

The plates were generated with blank paper pieces and a blank screen on purpose: the real art is warped onto each
piece here and multiplied by the plate's own paper shading, so the lamp light, texture and cut lines stay.
- cutting_mat.png: the European cover painting (the one he actually cut up) across the 3x3 block + 3 loose pieces
- light_table.png: the US cover's panels, one per piece, in a 4x3 grid (the last one under the hand)
- crt_desk.png: the European cover open on the CRT screen; the calendar's red X marks as a flicker mask
Corner coordinates were read off the plates by hand (plate pixels).
"""
import os
import cv2, numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "source", "ai")

MAT = [  # 3x3 block, row by row, then the loose pieces; each TL, TR, BR, BL
    [(210, 350), (448, 300), (472, 490), (235, 520)], [(448, 300), (672, 258), (705, 437), (472, 474)], [(672, 258), (900, 213), (942, 384), (706, 434)],
    [(235, 520), (472, 476), (502, 660), (265, 708)], [(474, 472), (706, 436), (746, 620), (505, 658)], [(708, 433), (942, 386), (992, 576), (746, 621)],
    [(265, 708), (506, 660), (545, 872), (288, 910)], [(508, 660), (748, 622), (784, 838), (545, 872)], [(750, 621), (972, 588), (1018, 795), (786, 833)],
    [(1012, 196), (1247, 252), (1213, 407), (971, 343)], [(1157, 418), (1275, 540), (1128, 673), (1005, 548)], [(1047, 714), (1315, 735), (1312, 912), (1045, 893)]]
TABLE = [
    [(258, 225), (515, 224), (513, 433), (245, 435)], [(523, 224), (768, 224), (768, 432), (512, 433)], [(776, 224), (1021, 222), (1023, 432), (772, 432)],
    [(1028, 216), (1272, 214), (1288, 428), (1035, 432)], [(242, 443), (505, 441), (502, 642), (233, 645)], [(512, 441), (768, 441), (768, 642), (505, 643)],
    [(775, 441), (1028, 440), (1033, 640), (775, 642)], [(1038, 439), (1287, 434), (1296, 632), (1045, 640)], [(230, 654), (497, 652), (495, 885), (217, 885)],
    [(504, 652), (767, 652), (767, 886), (500, 887)], [(775, 652), (1030, 650), (1035, 885), (775, 885)], [(1042, 656), (1300, 634), (1308, 870), (1056, 886)]]
SCREEN = [(285, 172), (832, 185), (845, 585), (290, 592)]
CALENDAR = (965, 215, 350, 130)       # the two rows of red X marks


def warp_onto(plate, art, quad, ref, keep):
    """Warp art (cropped to the quad's aspect) onto a quad of the plate; shade it with the plate's paper (luminance
    / ref) inside keep (the paper pixels), feathering the quad edge by a pixel."""
    h, w = plate.shape[:2]; q = np.float32(quad)
    qw = (np.linalg.norm(q[1] - q[0]) + np.linalg.norm(q[2] - q[3])) / 2; qh = (np.linalg.norm(q[3] - q[0]) + np.linalg.norm(q[2] - q[1])) / 2
    ah, aw = art.shape[:2]; r = qw / qh
    if aw / ah > r: cw = int(ah * r); art = art[:, (aw - cw) // 2:(aw - cw) // 2 + cw]
    else: ch = int(aw / r); art = art[(ah - ch) // 2:(ah - ch) // 2 + ch]
    ah, aw = art.shape[:2]
    M = cv2.getPerspectiveTransform(np.float32([[0, 0], [aw, 0], [aw, ah], [0, ah]]), q)
    a = cv2.warpPerspective(art, M, (w, h), flags=cv2.INTER_CUBIC).astype(np.float32)
    m = np.zeros((h, w), np.float32); cv2.fillConvexPoly(m, np.int32(np.round(q)), 1.0, cv2.LINE_AA)
    m = cv2.GaussianBlur(m, (0, 0), 0.8) * keep
    shade = np.clip(plate.astype(np.float32) / ref, 0, 1.25)     # the paper's own light and colour, per channel
    out = plate.astype(np.float32) * (1 - m[..., None]) + np.clip(a * shade, 0, 255) * m[..., None]
    return out.astype(np.uint8)


def punch(im, c=1.3, sat=1.25):
    """The European cover is a frame grab of a box in a video: lift its contrast and colour back towards print."""
    f = im.astype(np.float32); f = (f - 128) * c + 128 - 12
    hsv = cv2.cvtColor(np.clip(f, 0, 255).astype(np.uint8), cv2.COLOR_BGR2HSV).astype(np.float32); hsv[..., 1] *= sat
    return cv2.cvtColor(np.clip(hsv, 0, 255).astype(np.uint8), cv2.COLOR_HSV2BGR)


def paper_mask(plate, lo, hi, smax):
    hsv = cv2.cvtColor(plate, cv2.COLOR_BGR2HSV)
    k = ((hsv[..., 2] > lo) & (hsv[..., 2] < hi) & (hsv[..., 1] < smax)).astype(np.float32)
    return cv2.GaussianBlur(k, (0, 0), 1.0)


def cutting_mat(euro):
    plate = cv2.imread(os.path.join(SRC, "cutting_mat.png"))
    keep = paper_mask(plate, 25, 256, 90)
    euro = punch(euro)
    # the painting below its title: a 3x3 block from y 400-1000, the loose pieces from the strip below it
    cells = [euro[400 + r * 200:600 + r * 200, c * 300:(c + 1) * 300] for r in range(3) for c in range(3)]
    cells += [euro[950:1150, c * 300:(c + 1) * 300] for c in range(3)]      # above the rating and logos
    ref = np.array([150, 175, 200], np.float32)       # the lit paper's colour (BGR), so the art takes the lamp's warmth
    for quad, art in zip(MAT, cells): plate = warp_onto(plate, art, quad, ref, keep)
    return plate


def light_table(cov, panels):
    plate = cv2.imread(os.path.join(SRC, "light_table.png"))
    keep = paper_mask(plate, 60, 222, 45)          # grey paper only: not the light gaps, not the hand
    for quad, (x0, y0, x1, y1) in zip(TABLE, panels): plate = warp_onto(plate, cov[y0:y1, x0:x1], quad, np.float32(165), keep)
    last = np.zeros(plate.shape[:2], np.uint8); cv2.fillConvexPoly(last, np.int32(TABLE[-1]), 255)
    last = (last.astype(np.float32) / 255 * keep * 255).astype(np.uint8)
    return plate, last


def crt_desk(euro):
    plate = cv2.imread(os.path.join(SRC, "crt_desk.png")); h, w = plate.shape[:2]
    q = np.float32(SCREEN); sw, sh = 820, 600
    screen = np.full((sh, sw, 3), (58, 52, 50), np.uint8)                 # the app's dark canvas
    ch = int(sh * 0.9); cw = int(euro.shape[1] * ch / euro.shape[0]); x0 = (sw - cw) // 2; y0 = (sh - ch) // 2
    screen[y0:y0 + ch, x0:x0 + cw] = cv2.resize(euro, (cw, ch), interpolation=cv2.INTER_AREA)
    screen[::3] = (screen[::3] * 0.72).astype(np.uint8)                       # scan lines
    M = cv2.getPerspectiveTransform(np.float32([[0, 0], [sw, 0], [sw, sh], [0, sh]]), q)
    s = cv2.warpPerspective(screen, M, (w, h), flags=cv2.INTER_CUBIC).astype(np.float32)
    m = np.zeros((h, w), np.float32); cv2.fillConvexPoly(m, np.int32(q), 1.0, cv2.LINE_AA); m = cv2.GaussianBlur(m, (0, 0), 2.5)
    glow = cv2.GaussianBlur(s, (0, 0), 14) * 0.35                              # phosphor bloom
    out = plate.astype(np.float32) * (1 - m[..., None]) + (s * 0.82 + glow * 0.5) * m[..., None]
    out += cv2.GaussianBlur(s * m[..., None], (0, 0), 40) * 0.06               # light spill on the bezel
    # the calendar's red X marks
    x, y, cw_, ch_ = CALENDAR; hsv = cv2.cvtColor(plate, cv2.COLOR_BGR2HSV)
    red = (((hsv[..., 0] < 12) | (hsv[..., 0] > 165)) & (hsv[..., 1] > 70) & (hsv[..., 2] > 90)).astype(np.uint8) * 255
    xm = np.zeros_like(red); xm[y:y + ch_, x:x + cw_] = red[y:y + ch_, x:x + cw_]
    xm = cv2.dilate(xm, np.ones((3, 3), np.uint8))
    return np.clip(out, 0, 255).astype(np.uint8), xm
