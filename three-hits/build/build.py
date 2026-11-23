"""Build ThreeHits.tsrct from scratch: create, import assets and fonts, apply every action batch.

Usage: python3 build.py [--only stage,overlay] [--out PATH]
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
    "box_side_orange": "assets/generated/box_side_orange.png",     # same cardboard as the Shoebox Tower (Paper 363)
    "box_lid_orange": "assets/generated/box_lid_orange.png",
    "swoosh": "assets/logo/swoosh_white_2000.png",                  # Wikimedia Commons vector, native proportions
    "tariff_ink": "assets/generated/tariff_ink.png",
    "dust_puff": "assets/generated/dust_puff.png",
    "stamp_wood": "assets/generated/stamp_wood.png",
    "stamp_rubber": "assets/generated/stamp_rubber.png",
    "grunge353_dispmap": "assets/generated/grunge353_dispmap.png",
    "grunge352": "assets/textures/grunge-352.jpg",
}
FONTS = ["assets/fonts/Archivo-SemiCondensed-Black_wdth80_wght900.ttf", "assets/fonts/InstrumentSerif-Regular.ttf",
         "assets/fonts/InstrumentSerif-Italic.ttf"]


def run(args):
    r = subprocess.run([TSRCT] + args, capture_output=True, text=True)
    if r.returncode != 0:
        lines = [l for l in r.stderr.splitlines() if "<unknown>" not in l and not l.strip().startswith("at ")]
        head = lines[0][:600] if lines else ""
        cause = "\n".join(lines[lines.index("Caused by:"):lines.index("Caused by:") + 4]) if "Caused by:" in lines else ""
        raise SystemExit(f"tsrct {' '.join(args[:3])} failed:\n{head}\n{cause}\n{r.stdout[:600]}")
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
    args = sys.argv[1:]
    only = set(args[args.index("--only") + 1].split(",")) if "--only" in args else None
    out = os.path.abspath(args[args.index("--out") + 1]) if "--out" in args else os.path.join(ROOT, "ThreeHits.tsrct")
    if os.path.exists(out):
        os.remove(out)
    run(["project", "create", "--project", out, "--width", str(W), "--height", str(H)])
    for aid, rel in IMAGES.items():
        run(["project", "import-asset", "--project", out, "--file", os.path.join(ROOT, rel), "--asset-id", aid, "--kind", "image"])
    fonts = {}
    for rel in FONTS:
        fonts[os.path.basename(rel)] = json.loads(run(["project", "import-font", "--project", out, "--file", os.path.join(ROOT, rel)]))
    json.dump(fonts, open(os.path.join(WORK, "fonts.json"), "w"), indent=1)
    apply(out, "00-composition", [{"type": "updateFxComposition", "compositionId": "main", "startTimeMs": 0, "durationMs": ms(DUR)}])
    if not only or "stage" in only:
        from stage import build_stage
        acts, info = build_stage()
        apply(out, "10-stage", acts)
    if not only or "overlay" in only:
        from overlay import build_overlay
        apply(out, "30-overlay", build_overlay(fonts))
    print("built", out, f"{os.path.getsize(out) / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
