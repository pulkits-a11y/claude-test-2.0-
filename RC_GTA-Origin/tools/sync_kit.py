#!/usr/bin/env python3
"""Re-copy hyperframes/_kit into every beat project's assets/kit (run after any kit change)."""
import glob, os, shutil

ROOT = "/home/user/claude-test-2.0-/RC_GTA-Origin"
for p in sorted(glob.glob(f"{ROOT}/hyperframes/b[0-9][0-9]-*")):
    dst = f"{p}/assets/kit"
    if os.path.isdir(dst):
        shutil.rmtree(dst)
    shutil.copytree(f"{ROOT}/hyperframes/_kit", dst, ignore=shutil.ignore_patterns("demo*", "review"))
    print("synced", os.path.basename(p))
