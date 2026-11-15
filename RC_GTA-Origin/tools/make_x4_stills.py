#!/usr/bin/env python3
"""Capture or check the X4 "old frame" stills of a HyperFrames beat project (transitions kit: KIT_transitions.md, X4).

An X4 pixel-block tear in still mode (B2, B8, B17) tears a STILL of the old frame (assets/x4/*.png): a snapshot of the
composition itself. It goes stale whenever anything under the tear changes: footage synced by tools/sync_footage.py
(placeholder -> real clip), the look (grades, CRT treatment), the layout, the kit. A stale still puts the OLD picture
(e.g. a placeholder slate) into the torn frames of the final film. So: re-capture after every footage sync and every
change under the tear, and check before every render.

  python3 tools/make_x4_stills.py hyperframes/b08-break           # (re-)capture every still the beat registers
  python3 tools/make_x4_stills.py hyperframes/b08-break --check   # exit 1 while a still is missing or stale
  python3 tools/make_x4_stills.py --all [--check]                 # every hyperframes/bNN-* project with x4_stills.json

The beat registers its stills in <beat>/x4_stills.json:
  {"stills": [
    {"png": "assets/x4/b08-old.png",  the file the .rc-x4__still <img> loads
     "frame": 41,                     composition-local frame of the first torn frame (the tear's `at` x 30)
     "crop": [x, y, w, h],            optional: the .rc-x4 container's box in frame px (region tears); default full frame
     "hide": ["#b08-t10"],            optional: selectors hidden for the capture (text or labels drawn above the tear)
     "flatten": ["#b02-push"]}        optional: wrappers that hold the tear container and carry a GSAP push-in; their
  ]}                                  transform is reset to none for the capture (the still is in their local space)

Capture: copies the project to a temporary sibling folder, injects `RCK.x4Capture = true` (RCK.transitions.tear and
tearInit then add nothing) and a style that hides every .rc-x4 container plus `hide` (opacity 0 !important) and resets
`flatten` (transform none !important), snapshots every registered frame at frame/30 + 0.05 ms with
`npx --yes hyperframes@0.9.52 snapshot --at ... --no-end`, crops, and writes each PNG atomically. Then it records in
assets/x4/SOURCES.json the sha256 of every input: index.html, x4_stills.json, compositions/** and every file under
assets/ except assets/x4/**, *.md and assets/footage/SOURCES.json. --check recomputes them and lists what changed.
"""
import base64
import datetime
import glob
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = "/home/user/claude-test-2.0-/RC_GTA-Origin"
CLI = "hyperframes@0.9.52"
FPS = 30
PIXEL = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==")


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def manifest(proj):
    p = os.path.join(proj, "x4_stills.json")
    if not os.path.exists(p):
        raise SystemExit(f"{proj}: no x4_stills.json (register the beat's X4 stills there, see KIT_transitions.md X4)")
    m = json.load(open(p))
    stills = m.get("stills", [])
    for s in stills:
        if "png" not in s or "frame" not in s:
            raise SystemExit(f"{p}: every still needs 'png' and 'frame'")
        s.setdefault("crop", None)
        s.setdefault("hide", [])
        s.setdefault("flatten", [])
    return stills


def input_files(proj):
    out = []
    for name in ("index.html", "x4_stills.json"):
        if os.path.exists(os.path.join(proj, name)):
            out.append(name)
    for top in ("assets", "compositions"):
        for dirpath, dirnames, filenames in os.walk(os.path.join(proj, top)):
            rel = os.path.relpath(dirpath, proj)
            dirnames[:] = sorted(d for d in dirnames if not d.startswith(".") and os.path.join(rel, d) != os.path.join("assets", "x4"))
            for f in sorted(filenames):
                r = os.path.join(rel, f)
                if f.startswith(".") or f.endswith(".md") or r == os.path.join("assets", "footage", "SOURCES.json"):
                    continue
                out.append(r)
    return out


def input_hashes(proj):
    return {r: sha(os.path.join(proj, r)) for r in input_files(proj)}


def at_of(frame):
    return "%.5f" % (frame / FPS + 0.00005)


def capture(proj):
    proj = os.path.abspath(proj)
    stills = manifest(proj)
    if not stills:
        print(os.path.basename(proj), "no stills registered")
        return
    tmp = tempfile.mkdtemp(prefix=".x4cap-", dir=os.path.dirname(proj))
    try:
        dst = os.path.join(tmp, os.path.basename(proj))
        shutil.copytree(proj, dst, ignore=shutil.ignore_patterns("review", ".hyperframes", "node_modules", ".git", ".snap-tmp*", ".stills-tmp*", ".x4cap-*"))
        for s in stills:   # first capture: the <img> must load something (the container is hidden anyway)
            p = os.path.join(dst, s["png"])
            if not os.path.exists(p):
                os.makedirs(os.path.dirname(p), exist_ok=True)
                open(p, "wb").write(PIXEL)
        hide = sorted({".rc-x4"} | {h for s in stills for h in s["hide"]})
        flat = sorted({f for s in stills for f in s["flatten"]})
        inject = ('<script>window.RCK = window.RCK || {}; window.RCK.x4Capture = true;</script>\n'
                  '<style id="rck-x4-capture">' + ", ".join(hide) + " { opacity: 0 !important; }"
                  + ((" " + ", ".join(flat) + " { transform: none !important; }") if flat else "") + "</style>\n")
        html_p = os.path.join(dst, "index.html")
        html = open(html_p, encoding="utf-8").read()
        if "</head>" not in html:
            raise SystemExit(f"{proj}/index.html has no </head>")
        open(html_p, "w", encoding="utf-8").write(html.replace("</head>", inject + "</head>", 1))
        frames = sorted({int(s["frame"]) for s in stills})
        out = os.path.join(tmp, "snaps")
        cmd = ["npx", "--yes", CLI, "snapshot", ".", "--at", ",".join(at_of(f) for f in frames), "--no-end", "-o", out]
        r = subprocess.run(cmd, cwd=dst, capture_output=True, text=True, timeout=900)
        pngs = sorted(glob.glob(os.path.join(out, "frame-*-at-*.png")))
        if r.returncode != 0 or len(pngs) != len(frames):
            print(r.stdout[-3000:], r.stderr[-3000:])
            raise SystemExit(f"{proj}: snapshot failed ({len(pngs)} of {len(frames)} frames)")
        by_frame = dict(zip(frames, pngs))   # frame-00.., frame-01.. follow the --at order
        try:
            from PIL import Image
        except ImportError:
            Image = None
        rec = {}
        for s in stills:
            src, dest = by_frame[int(s["frame"])], os.path.join(proj, s["png"])
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            part = dest + ".part.png"
            c = s["crop"]
            if c and Image:
                Image.open(src).crop((c[0], c[1], c[0] + c[2], c[1] + c[3])).save(part)
            elif c:
                subprocess.run(["ffmpeg", "-nostdin", "-loglevel", "error", "-y", "-i", src, "-vf", "crop=%d:%d:%d:%d" % (c[2], c[3], c[0], c[1]), part], check=True)
            else:
                shutil.copyfile(src, part)
            os.replace(part, dest)
            rec[s["png"]] = {"frame": int(s["frame"]), "at_s": float(at_of(int(s["frame"]))), "crop": c, "hide": s["hide"],
                             "flatten": s["flatten"], "sha256": sha(dest)}
            print(f"  {s['png']}  <- frame {s['frame']}" + (f" crop {c}" if c else ""))
        json.dump({"tool": "tools/make_x4_stills.py", "cli": CLI,
                   "captured_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                   "stills": rec, "inputs": input_hashes(proj)},
                  open(os.path.join(proj, "assets", "x4", "SOURCES.json"), "w"), indent=1)
        print(os.path.basename(proj), f"captured {len(stills)} X4 still(s); inputs recorded in assets/x4/SOURCES.json")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def check(proj):
    proj = os.path.abspath(proj)
    stills = manifest(proj)
    name = os.path.basename(proj)
    src_p = os.path.join(proj, "assets", "x4", "SOURCES.json")
    if not os.path.exists(src_p):
        print(f"{name}: STALE - X4 stills never captured with tools/make_x4_stills.py")
        return False
    rec = json.load(open(src_p))
    problems = []
    for s in stills:
        p, r = os.path.join(proj, s["png"]), rec.get("stills", {}).get(s["png"])
        if not os.path.exists(p):
            problems.append(f"{s['png']} missing")
        elif not r:
            problems.append(f"{s['png']} not captured by the tool")
        else:
            if sha(p) != r.get("sha256"):
                problems.append(f"{s['png']} replaced by hand")
            for k in ("frame", "crop", "hide", "flatten"):
                if r.get(k) != (int(s[k]) if k == "frame" else s[k]):
                    problems.append(f"{s['png']}: {k} changed in x4_stills.json")
    old, now = rec.get("inputs", {}), input_hashes(proj)
    changed = sorted(k for k in now if k in old and old[k] != now[k])
    added = sorted(k for k in now if k not in old)
    removed = sorted(k for k in old if k not in now)
    for label, lst in (("changed", changed), ("new", added), ("removed", removed)):
        if lst:
            problems.append(f"{label} since capture: " + ", ".join(lst[:12]) + (" ..." if len(lst) > 12 else ""))
    if problems:
        where = os.path.relpath(proj, ROOT) if proj.startswith(ROOT + os.sep) else proj
        print(f"{name}: STALE X4 stills -> run: python3 tools/make_x4_stills.py {where}")
        for p in problems:
            print("   ", p)
        return False
    print(f"{name}: X4 stills current ({len(stills)})")
    return True


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    do_check = "--check" in sys.argv
    if "--all" in sys.argv:
        projs = sorted(os.path.dirname(p) for p in glob.glob(f"{ROOT}/hyperframes/b[0-9][0-9]-*/x4_stills.json"))
    elif args:
        projs = args
    else:
        raise SystemExit(__doc__)
    ok = True
    for p in projs:
        if do_check:
            ok = check(p) and ok
        else:
            capture(p)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
