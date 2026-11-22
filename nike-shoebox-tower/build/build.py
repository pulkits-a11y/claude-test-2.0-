"""Build ShoeboxTower.tsrct from scratch: create, import assets and fonts, apply every action batch.

Usage: python3 build.py [--only street,wall,overlay] [--out PATH]
"""
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import ROOT, DUR, W, H, ms  # noqa: E402

TSRCT = os.path.expanduser("~/.local/share/Tesseract/bin/tsrct")
WORK = os.path.join(ROOT, ".tesseract-work")
BATCH = os.path.join(WORK, "batches")
os.makedirs(BATCH, exist_ok=True)

IMAGES = {
    "box_side_orange": "assets/generated/box_side_orange.png",
    "box_lid_orange": "assets/generated/box_lid_orange.png",
    "box_side_grey": "assets/generated/box_side_grey.png",
    "box_lid_grey": "assets/generated/box_lid_grey.png",
    "sidewalk_color": "assets/generated/sidewalk_color.png",
    "sidewalk_rough": "assets/generated/sidewalk_rough.png",
    "asphalt_color": "assets/generated/asphalt_color.png",
    "asphalt_rough": "assets/generated/asphalt_rough.png",
    "swoosh": "assets/logo/swoosh_white_2000.png",
    "grunge353": "assets/textures/grunge-353.jpg",
    "grunge353_dispmap": "assets/generated/grunge353_dispmap.png",
    "grunge352": "assets/textures/grunge-352.jpg",
    "grunge351": "assets/textures/grunge-351-halftone.jpg",
    "paper363": "assets/textures/paper-363.jpg",
}
FONTS = ["assets/fonts/Archivo-SemiCondensed-Black_wdth80_wght900.ttf", "assets/fonts/InstrumentSerif-Regular.ttf",
         "assets/fonts/InstrumentSerif-Italic.ttf", "assets/fonts/Inter-Medium.ttf"]


def run(args, quiet=True):
    r = subprocess.run([TSRCT] + args, capture_output=True, text=True)
    if r.returncode != 0:
        lines = [l for l in r.stderr.splitlines() if "<unknown>" not in l and not l.strip().startswith("at ")]
        head = lines[0][:600] if lines else ""
        cause = "\n".join(lines[lines.index("Caused by:"):lines.index("Caused by:") + 4]) if "Caused by:" in lines else ""
        raise SystemExit(f"tsrct {' '.join(args[:3])} failed:\n{head}\n{cause}")
    return r.stdout


def apply(project, name, actions):
    path = os.path.join(BATCH, f"{name}.json")
    with open(path, "w") as f:
        json.dump(actions, f, separators=(",", ":"))
    out = run(["project", "apply", "--project", project, "--actions", path])
    warn = json.loads(out).get("warnings", []) if out.strip().startswith("{") else []
    print(f"  applied {name}: {len(actions)} actions, {os.path.getsize(path) / 1e6:.2f} MB" + (f", {len(warn)} warnings" if warn else ""))
    for w in warn[:8]:
        print("    warning:", str(w)[:300])


def main():
    only = None
    out = os.path.join(ROOT, "ShoeboxTower.tsrct")
    args = sys.argv[1:]
    if "--only" in args:
        only = set(args[args.index("--only") + 1].split(","))
    if "--out" in args:
        out = os.path.abspath(args[args.index("--out") + 1])
    if os.path.exists(out):
        os.remove(out)
    run(["project", "create", "--project", out, "--width", str(W), "--height", str(H)])
    for aid, rel in IMAGES.items():
        run(["project", "import-asset", "--project", out, "--file", os.path.join(ROOT, rel), "--asset-id", aid, "--kind", "image"])
    fonts = {}
    for rel in FONTS:
        r = json.loads(run(["project", "import-font", "--project", out, "--file", os.path.join(ROOT, rel)]))
        fonts[os.path.basename(rel)] = r
    json.dump(fonts, open(os.path.join(WORK, "fonts.json"), "w"), indent=1)
    apply(out, "00-composition", [{"type": "updateFxComposition", "compositionId": "main", "startTimeMs": 0, "durationMs": ms(DUR)}])
    if not only or "street" in only:
        from street import build_street
        acts, info = build_street(IMAGES)
        json.dump({k: v for k, v in info.items()}, open(os.path.join(WORK, "street_info.json"), "w"), default=str)
        apply(out, "10-street", acts)
    if not only or "wall" in only:
        from wall import build_wall
        apply(out, "20-wall", build_wall())
    if not only or "overlay" in only:
        from overlay import build_overlay
        apply(out, "30-overlay", build_overlay(fonts))
    print("built", out, f"{os.path.getsize(out) / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
