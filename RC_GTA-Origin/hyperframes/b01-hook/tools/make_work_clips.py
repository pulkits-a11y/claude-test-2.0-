#!/usr/bin/env python3
"""v05 working clips for the hook (REVISION_v05 Lane 1): speed ramps on the GTA VI shot (R1.2), eased.

  python3 tools/make_work_clips.py            (run from hyperframes/b01-hook; ~3-6 min on 4 CPU cores)

Source: assets/footage/R1.2.mp4 (tools/sync_footage.py window: media 0 = source 8.2 s, 1920x1080, 30 fps).
Method: the needed source span is motion-interpolated to 150 fps (ffmpeg minterpolate, mci), then every output frame
(30 fps) takes the 150 fps frame nearest to its remapped source time media(j) = media(0) + (1/30) * sum of v over the
frames before j, where v = speed (1 = real time). Speed changes are eased (easeInOutSine) over the frames named below.

  assets/work/R1.2_A_logo85.mp4  B1 local 55-93 (+2f): cell 6 -> full frame and the logo shot. v 1.0 (55-63), eased
                                 1.0 -> 0.85 (63-69, the logo slams on 69), 0.85 to the cut on "have" (93). media 0 at 55.
  assets/work/R1.2_C_flip40.mp4  B1 local 114 -> 170 (B2 uses it to its local 36): the SUV flip. v 1.0 (114-121), eased
                                 1.0 -> 0.4 (121-125), 0.4 for 20 frames (125-145 = the 8 source frames 2.4667-2.7333 s
                                 where the truck leaves the ground, lift-off on "cops?" 125), eased 0.4 -> 1.0
                                 (145-149), 1.0 after. media(125) = 2.4667.
Shot B (the 150% crop, local 93-114) plays R1.2.mp4 itself at 100% (media-start = the end of clip A, see MAP below).
Writes assets/work/R1.2_ramps.json (frame -> source media map) for the beat and for b02-bug (it copies clip C).
"""
import json, math, os, shutil, subprocess, sys, tempfile
FPS, HI = 30, 150
SRC = 'assets/footage/R1.2.mp4'
OUT = 'assets/work'

def sio(p): return (1 - math.cos(math.pi * min(max(p, 0), 1))) / 2

def speed_fn(segs):
    # segs: list of (j0, j1, v0, v1): constant when v0 == v1, eased (sine in-out) otherwise
    def v(j):
        for j0, j1, v0, v1 in segs:
            if j0 <= j < j1: return v0 + (v1 - v0) * sio((j + 0.5 - j0) / (j1 - j0))
        return segs[-1][3]
    return v

def remap(n, v, m0):
    t, out = m0, []
    for j in range(n):
        out.append(t); t += v(j) / FPS
    return out

def interp(t0, t1, tmp):
    hi = os.path.join(tmp, 'hi_%.3f.mp4' % t0)
    subprocess.run(['ffmpeg', '-nostdin', '-loglevel', 'error', '-y', '-ss', '%.4f' % t0, '-i', SRC, '-t', '%.4f' % (t1 - t0),
                    '-vf', 'minterpolate=fps=%d:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1' % HI,
                    '-c:v', 'libx264', '-crf', '10', '-preset', 'veryfast', '-pix_fmt', 'yuv420p', hi], check=True)
    return hi

def build(name, times, t0, t1, tmp):
    hi = interp(t0, t1, tmp)
    idx = [int(round((t - t0) * HI)) for t in times]
    n_hi = int(subprocess.run(['ffprobe', '-v', 'error', '-count_frames', '-select_streams', 'v:0', '-show_entries', 'stream=nb_read_frames',
                               '-of', 'csv=p=0', hi], capture_output=True, text=True).stdout.strip())
    idx = [min(i, n_hi - 1) for i in idx]
    # select the chosen frames (strictly increasing here: speed >= 0.4 -> >= 2 hi frames per output frame)
    assert all(b > a for a, b in zip(idx, idx[1:])), 'non-increasing frame picks'
    expr = '+'.join('eq(n\\,%d)' % i for i in idx)
    dst = os.path.join(OUT, name)
    subprocess.run(['ffmpeg', '-nostdin', '-loglevel', 'error', '-y', '-i', hi, '-vf', "select='%s',setpts=N/%d/TB" % (expr, FPS),
                    '-r', str(FPS), '-c:v', 'libx264', '-crf', '12', '-preset', 'medium', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', '-an', dst], check=True)
    return dst

def main():
    os.makedirs(OUT, exist_ok=True)
    tmp = tempfile.mkdtemp(prefix='ramps_')
    # A: local 55 -> 95 (40 frames incl. 2 spare), media 0 at 55
    vA = speed_fn([(0, 8, 1, 1), (8, 14, 1, 0.85), (14, 99, 0.85, 0.85)])
    tA = remap(40, vA, 0.0)
    # C: local 114 -> 170 (56 frames); lift-off media 2.4667 on local 125 (j 11)
    vC = speed_fn([(0, 7, 1, 1), (7, 11, 1, 0.4), (11, 31, 0.4, 0.4), (31, 35, 0.4, 1), (35, 99, 1, 1)])
    pre = remap(12, vC, 0.0)[11]
    tC = remap(56, vC, 2.4667 - pre)
    a = build('R1.2_A_logo85.mp4', tA, 0.0, tA[-1] + 0.1, tmp)
    c = build('R1.2_C_flip40.mp4', tC, round(tC[0] - 0.02, 3), tC[-1] + 0.1, tmp)
    m = {'src': SRC, 'source_offset_s': 8.2, 'fps': FPS,
         'A': {'file': a, 'local0': 55, 'media': [round(t, 4) for t in tA]},
         'B': {'note': 'shot B (150% crop, local 93-114) plays R1.2.mp4 at 100%: media-start = A media at local 93 + its 85% step',
               'media_start': round(tA[38], 4)},
         'C': {'file': c, 'local0': 114, 'media': [round(t, 4) for t in tC]}}
    json.dump(m, open(os.path.join(OUT, 'R1.2_ramps.json'), 'w'), indent=1)
    shutil.rmtree(tmp, ignore_errors=True)
    print('A media 55..95:', tA[0], '->', round(tA[-1], 4), '| B media-start', round(tA[38], 4), '| C media 114..170:', round(tC[0], 4), '->', round(tC[-1], 4))

if __name__ == '__main__':
    main()
