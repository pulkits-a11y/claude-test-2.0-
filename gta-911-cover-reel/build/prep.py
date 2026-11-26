"""Prepares selects and stills from the source media and imports them into base.tsrct.

Selects: each source moment is cut to an H.264 30 fps file (max 1080 high) with a 0.5 s
handle before it, so the edit can slip frames. Stills: frames grabbed from the clips;
perspective flattening (which Tesseract's corner pin cannot invert) and simple crops are
done here; masks, borders, mattes and looks are built in Tesseract."""
import json, os, subprocess, sys
import cv2, numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "source")
BR = os.path.join(SRC, "broll")
OUT = os.path.join(ROOT, "build", "assets")
X = os.path.expanduser("~/.local/share/Tesseract/bin/tsrct")
BASE = os.path.join(ROOT, "build", "base.tsrct")
REG = os.path.join(ROOT, "build", "assets.json")
HANDLE = 0.5
os.makedirs(os.path.join(OUT, "sel"), exist_ok=True)
os.makedirs(os.path.join(OUT, "img"), exist_ok=True)
reg = json.load(open(REG)) if os.path.exists(REG) else {}


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode: raise RuntimeError(" ".join(cmd) + "\n" + r.stderr[-2000:])
    return r.stdout


def srcfile(b):
    return os.path.join(BR, b + ".mp4") if not os.path.isabs(b) else b


def sel(b, t, dur, name=None):
    """A select of clip b from t seconds for dur seconds (plus handles). Returns asset id;
    the wanted moment starts at HANDLE seconds into the select (or at t if t < HANDLE)."""
    name = name or f"{b}_{int(round(t * 1000)):07d}"
    if name in reg: return name
    p = os.path.join(OUT, "sel", name + ".mp4")
    lead = min(HANDLE, t)
    if not os.path.exists(p):
        run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t - lead:.3f}", "-i", srcfile(b), "-t", f"{dur + lead + 0.6:.3f}",
             "-vf", "fps=30,scale='min(iw,trunc(iw*1080/ih/2)*2)':'min(ih,1080)'", "-c:v", "libx264", "-crf", "17",
             "-preset", "veryfast", "-pix_fmt", "yuv420p", "-an", p])
    out = json.loads(run([X, "project", "import-video", "--project", BASE, "--file", p, "--asset-id", name]))
    reg[name] = {"kind": "video", "path": p, "lead": lead, "dur": out["durationMs"], "w": out["width"], "h": out["height"]}
    save()
    return name


def frame(b, t):
    tmp = os.path.join(OUT, "_f.png")
    run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.3f}", "-i", srcfile(b), "-frames:v", "1", tmp])
    return cv2.imread(tmp, cv2.IMREAD_UNCHANGED)


def img(name, im=None, path=None):
    if name in reg: return name
    p = path or os.path.join(OUT, "img", name + ".png")
    if im is not None: cv2.imwrite(p, im)
    run([X, "project", "import-asset", "--project", BASE, "--file", p, "--asset-id", name, "--kind", "image"])
    i = cv2.imread(p, cv2.IMREAD_UNCHANGED)
    reg[name] = {"kind": "image", "path": p, "w": i.shape[1], "h": i.shape[0]}
    save()
    return name


def still(name, b, t, crop=None, warp=None, size=None):
    if name in reg: return name
    im = frame(b, t)
    if warp is not None:
        (w, h), q = size, np.float32(warp)
        M = cv2.getPerspectiveTransform(q, np.float32([[0, 0], [w, 0], [w, h], [0, h]]))
        im = cv2.warpPerspective(im, M, (w, h), flags=cv2.INTER_CUBIC)
    elif crop is not None:
        x, y, w, h = crop
        im = im[y:y + h, x:x + w]
    return img(name, im)


def audio(name, path):
    if name in reg: return name
    run([X, "project", "import-asset", "--project", BASE, "--file", path, "--asset-id", name, "--kind", "audio"])
    reg[name] = {"kind": "audio", "path": path}
    save()
    return name


def save():
    json.dump(reg, open(REG, "w"), indent=1)


def init_base():
    if os.path.exists(BASE): return
    run([X, "project", "create", "--project", BASE, "--width", "1920", "--height", "1080"])
    for f in ["Archivo[wdth,wght].ttf", "InstrumentSerif-Regular.ttf"]:
        out = json.loads(run([X, "project", "import-font", "--project", BASE, "--file", os.path.join(SRC, "fonts", f)]))
        reg["font:" + f] = {"kind": "font", "assetId": out["assetId"], "family": out["fontFamily"]}
    save()
