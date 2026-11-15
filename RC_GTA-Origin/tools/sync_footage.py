#!/usr/bin/env python3
"""Copy the current footage for each R-ID a beat uses into its HyperFrames project.

  python3 tools/sync_footage.py hyperframes/b03-dundee      # reads <proj>/footage.json {"rids": [...]}
  python3 tools/sync_footage.py --all                        # every beat project

For each R-ID: a real clip in 04_Broll/<Bxx or Textures>/ named "<RID>__*.mp4|mov|png|jpg" or "<RID>.<ext>"
wins; otherwise the stand-in 04_Broll/_placeholders/<RID>.mp4 is used. If the manifest gives
source_in/source_out for the R-ID, the real clip is trimmed to that window (1080p, 30 fps, no audio).
The result is assets/footage/<RID>.mp4 (or .png/.jpg for R4.5 stills) and assets/footage/SOURCES.json.
"""
import glob, json, os, shutil, subprocess, sys

ROOT = "/home/user/claude-test-2.0-/RC_GTA-Origin"


def find_real(entry):
    rid = entry["rid"]
    hits = []
    for d in sorted(set([entry["folder"]] + [f"04_Broll/B{int(b[1:]):02d}" for b in entry["beats"].split(",") if b.startswith("B")] + ["04_Broll/Textures"])):
        for pat in (f"{rid}__*", f"{rid}.*", f"{rid}_*"):
            hits += [h for h in glob.glob(f"{ROOT}/{d}/{pat}") if not h.endswith((".part", ".ytdl", ".json"))]
    return sorted(set(hits))


def sync(proj):
    proj = os.path.abspath(proj)
    spec = json.load(open(f"{proj}/footage.json"))
    man = {e["rid"]: e for e in json.load(open(f"{ROOT}/04_Broll/broll_manifest.json"))["clips"]}
    out_dir = f"{proj}/assets/footage"
    os.makedirs(out_dir, exist_ok=True)
    report = {}
    for rid in spec.get("rids", []):
        e = man[rid]
        real = find_real(e)
        if real:
            src = real[0]
            ext = os.path.splitext(src)[1].lower()
            if ext in (".png", ".jpg", ".jpeg", ".webp"):
                for i, r in enumerate(real):
                    dst = f"{out_dir}/{rid}{'' if i == 0 else '_' + str(i + 1)}{os.path.splitext(r)[1].lower()}"
                    shutil.copy2(r, dst)
                report[rid] = {"kind": "still", "files": real}
                continue
            dst = f"{out_dir}/{rid}.mp4"
            cmd = ["ffmpeg", "-nostdin", "-loglevel", "error", "-y"]
            if e.get("source_in") is not None:
                cmd += ["-ss", str(e["source_in"])]
            cmd += ["-i", src]
            if e.get("source_out") is not None and e.get("source_in") is not None:
                cmd += ["-t", str(float(e["source_out"]) - float(e["source_in"]))]
            cmd += ["-an", "-vf", "fps=30,scale=w='if(gt(iw/ih,16/9),1920,-2)':h='if(gt(iw/ih,16/9),-2,1080)',setsar=1",
                    "-c:v", "libx264", "-crf", "14", "-preset", "medium", "-pix_fmt", "yuv420p", dst]
            subprocess.run(cmd, check=True)
            report[rid] = {"kind": "real", "source": os.path.relpath(src, ROOT), "in": e.get("source_in"), "out": e.get("source_out")}
        else:
            ph = f"{ROOT}/04_Broll/_placeholders/{rid}.mp4"
            if not os.path.exists(ph):
                raise SystemExit(f"no footage and no placeholder for {rid}")
            shutil.copy2(ph, f"{out_dir}/{rid}.mp4")
            report[rid] = {"kind": "placeholder", "source": os.path.relpath(ph, ROOT)}
    json.dump(report, open(f"{out_dir}/SOURCES.json", "w"), indent=1)
    print(os.path.basename(proj), {k: v["kind"] for k, v in report.items()})


if __name__ == "__main__":
    if sys.argv[1] == "--all":
        for p in sorted(glob.glob(f"{ROOT}/hyperframes/b[0-9][0-9]-*")):
            if os.path.exists(f"{p}/footage.json"):
                sync(p)
    else:
        sync(sys.argv[1])
