#!/usr/bin/env python3
"""Scaffold (or refresh) the HyperFrames project for one beat.

  python3 tools/new_beat.py B3            # creates hyperframes/b03-dundee/ if missing
  python3 tools/new_beat.py B3 --refresh  # only re-copies the kit and words.json

Creates: hyperframes/<id>/ via `npx hyperframes init`, then
  index.html      skeleton root composition (id, 1920x1080, beat + 6f handles), kit + GSAP wired
  assets/kit/     copy of hyperframes/_kit (re-sync with tools/sync_kit.py)
  words.json      this beat's words with comp_t (seconds on the composition clock)
  footage.json    the R-IDs this beat uses (edit it, then run tools/sync_footage.py)
  review/         snapshots / contact sheets
Never overwrites an existing index.html.
"""
import json, os, shutil, subprocess, sys

ROOT = "/home/user/claude-test-2.0-/RC_GTA-Origin"
HF = f"{ROOT}/hyperframes"
CLI = "hyperframes@0.9.52"

SKELETON = """<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1920, height=1080" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
    <link rel="stylesheet" href="assets/kit/base.css" />
    <link rel="stylesheet" href="assets/kit/type.css" />
    <link rel="stylesheet" href="assets/kit/motifs.css" />
    <link rel="stylesheet" href="assets/kit/transitions.css" />
    <link rel="stylesheet" href="assets/kit/screens.css" />
    <style>
      html, body {{ margin: 0; width: 1920px; height: 1080px; overflow: hidden; background: transparent; }}
      #root {{ position: relative; width: 1920px; height: 1080px; overflow: hidden; }}
    </style>
  </head>
  <body>
    <!-- {beat} {comp_id}: beat {dur_f}f ({dur_s:.3f}s) + 6f handle each end = {frames}f.
         Local time 0 = beat start - 6f; the beat runs local {hs:.4f}s .. {he:.4f}s.
         Word timings: words.json (comp_t). Spec: ../../PRODUCTION_SPEC.md. Plan: ../../00_Brief/. -->
    <div id="root" data-composition-id="{comp_id}" data-start="0" data-duration="{dur:.7f}" data-width="1920" data-height="1080">
    </div>
    <script src="assets/kit/type.js"></script>
    <script src="assets/kit/motifs.js"></script>
    <script src="assets/kit/transitions.js"></script>
    <script src="assets/kit/screens.js"></script>
    <script>
      window.__timelines = window.__timelines || {{}};
      const tl = gsap.timeline({{ paused: true }});
      // Build the beat here (kit helpers: see assets/kit/KIT.md).
      window.__timelines["{comp_id}"] = tl;
    </script>
  </body>
</html>
"""


def copy_kit(proj):
    dst = f"{proj}/assets/kit"
    if os.path.isdir(dst):
        shutil.rmtree(dst)
    shutil.copytree(f"{HF}/_kit", dst, ignore=shutil.ignore_patterns("demo*", "*.md~", "review"))


def main():
    beat = sys.argv[1].upper()
    refresh = "--refresh" in sys.argv
    bm = json.load(open(f"{ROOT}/timing/beat_map.json"))
    bt = next(b for b in bm["beats"] if b["id"] == beat)
    comp = bt["composition"]
    proj = f"{HF}/{comp['id']}"
    if not os.path.isdir(proj):
        if refresh:
            raise SystemExit(f"{proj} does not exist")
        r = subprocess.run(["npx", "--yes", CLI, "init", comp["id"], "--skip-skills", "--skill=hyperframes", "--non-interactive"],
                           cwd=HF, capture_output=True, text=True)
        if r.returncode != 0:
            print(r.stdout[-2000:], r.stderr[-2000:]); raise SystemExit("init failed")
        frames = comp["frames"]
        html = SKELETON.format(beat=beat, comp_id=comp["id"], dur_f=bt["dur_frames"], dur_s=bt["dur_s"], frames=frames,
                               dur=frames / 30, hs=6 / 30, he=(6 + bt["dur_frames"]) / 30)
        open(f"{proj}/index.html", "w").write(html)
        os.makedirs(f"{proj}/review", exist_ok=True)
        if not os.path.exists(f"{proj}/footage.json"):
            json.dump({"beat": beat, "rids": []}, open(f"{proj}/footage.json", "w"), indent=1)
    copy_kit(proj)
    words = [{"text": w["text"], "comp_t": w["comp_t"], "comp_end_t": w["comp_end_t"], "beat_t": w["beat_t"],
              "start_frame_local": int(round(w["comp_t"] * 30)), "punct": w["punct"]} for w in bt["words"]]
    json.dump({"beat": beat, "composition": comp["id"], "fps": 30, "handle_frames": 6, "beat_frames": bt["dur_frames"],
               "composition_frames": comp["frames"], "edit_start_s": bt["start_s"], "voiceover": bt["voiceover"], "words": words},
              open(f"{proj}/words.json", "w"), indent=1)
    print(proj)


if __name__ == "__main__":
    main()
