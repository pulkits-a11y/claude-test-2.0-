"""For each B-roll shot: detect source cuts inside the used range and measure motion."""
import json, subprocess, os, sys
import numpy as np
plan = json.load(open('roughcut_plan.json')); FPS = 30
R = '/home/user/claude-test-2.0-/nike-reel'
def frames(path, t0, n, w=160, h=90):
    raw = subprocess.run(['ffmpeg','-v','error','-ss',f'{t0:.3f}','-i',path,'-frames:v',str(n),'-vf',f'fps={FPS},scale={w}:{h}','-f','rawvideo','-pix_fmt','gray','-'],capture_output=True).stdout
    a = np.frombuffer(raw, np.uint8).astype(np.float32)
    return a.reshape(-1, h, w)
rows = []
for sh in plan['shots']:
    if sh['clip'] == 'MISSING': continue
    n = sh['end'] - sh['start']
    if sh['clip'] == 'B79': rows.append((sh['seg'], sh['clip'], sh['src'], n, 'reversed', '', '')); continue
    f = frames(f"{R}/Sources/broll/{sh['clip']}.mp4", sh['src'], n + 1)
    d = np.abs(np.diff(f, axis=0)).mean(axis=(1, 2)) if len(f) > 1 else np.array([0])
    med = float(np.median(d)) if len(d) else 0
    cuts = [i + 1 for i, v in enumerate(d) if v > max(25, 4 * med) and 0 < i + 1 < n]
    motion = 'static' if med < 1.5 else ('low' if med < 4 else 'moving')
    rows.append((sh['seg'], sh['clip'], sh['src'], n, motion, f'{med:.1f}', ('CUT at frame ' + ','.join(map(str, cuts))) if cuts else ''))
for r in rows: print(f'{r[0]:7s} {r[1]:4s} @{r[2]:7.2f} {r[3]:3d}f  {r[4]:8s} {r[5]:>5s}  {r[6]}')
