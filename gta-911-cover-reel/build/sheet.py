"""Contact sheet: one frame per shot (the shot's middle frame), labelled, from the editable document.
Usage: python build/sheet.py [source.mp4|--preview] [out.jpg] [scene numbers...]"""
import json, os, subprocess, sys
import cv2, numpy as np
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
X = os.path.expanduser("~/.local/share/Tesseract/bin/tsrct")
doc = json.load(open(os.path.join(ROOT, ".tesseract-work", "editable.json")))
FONT = os.path.join(ROOT, "source", "fonts", "Archivo[wdth,wght].ttf")


def shots():
    out = []
    for sc in doc["composition"]["layers"]:
        if sc.get("type") != "Group" or sc["name"][:2] not in ("S0", "S1", "H1", "H2", "H3", "H4"): continue
        s0 = sc["playback"]["inputRange"]["start"]
        for sh in sc["layers"]:
            if sh.get("type") != "Group": continue
            a = s0 + sh["playback"]["inputRange"]["start"]; d = sh["playback"]["inputRange"]["duration"]
            if sh["name"].startswith("S9.6"):
                for sub in sh["layers"]:
                    b = a + sub["playback"]["inputRange"]["start"]; out.append((sub["name"], b, sub["playback"]["inputRange"]["duration"]))
                continue
            out.append((sh["name"], a, d))
    return sorted(out, key=lambda x: x[1])


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else "--preview"
    dst = sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, "contact_sheet.jpg")
    only = set(sys.argv[3:])
    tiles = []; tmp = os.path.join(ROOT, ".tesseract-work", "checks"); os.makedirs(tmp, exist_ok=True)
    for name, a, d in shots():
        if only and name.split(".")[0][1:] not in only: continue
        t = (a + d / 2) / 1000; f = int(round(t * 30))
        p = os.path.join(tmp, f"shot_{f:04d}.png")
        if src == "--preview":
            subprocess.run([X, "preview", "--project", os.path.join(ROOT, "GTA911_CoverReel.tsrct"), "--time", f"{t:.4f}", "--output", p], capture_output=True)
        else:
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.4f}", "-i", src, "-frames:v", "1", p])
        im = cv2.imread(p)
        if im is None: im = np.zeros((1080, 1920, 3), np.uint8)
        im = cv2.resize(im, (384, 216))
        lab = np.zeros((26, 384, 3), np.uint8)
        cv2.putText(lab, f"{name[:40]}  f{f}", (4, 18), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (220, 230, 240), 1, cv2.LINE_AA)
        tiles.append(np.vstack([lab, im]))
    cols = 6
    while len(tiles) % cols: tiles.append(np.zeros_like(tiles[0]))
    rows = [np.hstack(tiles[i:i + cols]) for i in range(0, len(tiles), cols)]
    cv2.imwrite(dst, np.vstack(rows), [cv2.IMWRITE_JPEG_QUALITY, 88])
    print(dst, len(tiles))


if __name__ == "__main__":
    main()
