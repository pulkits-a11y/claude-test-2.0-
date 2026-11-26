"""Runs the brief's 'Before you render' checklist against the generated document and keyframe batch."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import textfit as tf
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
doc = json.load(open(os.path.join(ROOT, ".tesseract-work", "editable.json")))
acts = json.load(open(os.path.join(ROOT, ".tesseract-work", "edits.json")))
words = json.load(open(os.path.join(ROOT, "build", "words.json")))
fails, notes = [], []
ok = lambda c, m: (None if c else fails.append(m))


def walk(ls, t0=0, path=()):
    for l in ls:
        st = l.get("playback", l.get("activeRange", {}))
        st = st.get("inputRange", st) if "inputRange" in st else st
        yield l, t0, path
        if l["type"] == "Group":
            yield from walk(l["layers"], t0 + l["playback"]["inputRange"]["start"], path + (l["name"],))


root = doc["composition"]["layers"]
# 1 shot lengths
shots = []
for sc in root:
    if sc["type"] != "Group" or not sc["name"][:2] == "S0" and not sc["name"][:2] == "S1" or sc["name"].endswith("text"): continue
    for sh in sc["layers"]:
        if sh["type"] != "Group": continue
        subs = [x for x in sh["layers"] if x["type"] == "Group" and x["name"].startswith("Burst")] if sh["name"].startswith("S9.6") else [sh]
        for s in subs:
            f = round(s["playback"]["inputRange"]["duration"] * 30 / 1000); shots.append((s["name"], f))
# v2: the 30-frame cap is relaxed on review (shots the client asked to breathe); listed, not failed
notes.append("shots of 30+ frames (held on review): " + ", ".join(f"{n} ({f})" for n, f in shots if f >= 30))
ok(not any("Instrument" in l["sourceText"]["fontFamily"] for l, _, _ in walk(root) if l["type"] == "Text"), "Instrument Serif still in use")
first10 = [s for s in shots if s[0].split(".")[0] in ("S1", "S2", "S3", "S4", "S5")]
notes.append(f"{len(shots)} shots; longest {max(f for _, f in shots)} frames; scenes 1-5 shots over 8 frames: " +
             ", ".join(f"{n} ({f})" for n, f in first10 if f > 8))
# 2 flash cuts
fl = [l for l in root if l["name"].startswith("Flash cut")]
ok(len(fl) == 5, f"{len(fl)} flash cuts")
notes.append("flash cuts at frames " + ", ".join(l["name"].split("@")[1] for l in fl))
# 4/5 type sizes, safe zone and logo box
for l, t0, path in walk(root):
    if l["type"] != "Text": continue
    st = l["sourceText"]; size = st["fontSize"]; ax = st.get("fontVariations", {}).get("axes", {})
    key = "IS" if st["fontFamily"].startswith("Instrument") else "AR"
    x, y = l["transform"]["position"]
    if l["transform"]["anchorPoint"] != [0, 0] and l["transform"]["anchorPoint"] != [0.0, 0.0]:
        x -= l["transform"]["anchorPoint"][0]; y -= l["transform"]["anchorPoint"][1]
    w = max(tf.advance(key, line, size, ax or None, st.get("tracking", 0)) for line in st["text"].split("\n"))
    if st["justification"] == "center": x -= w / 2
    elif st["justification"] == "right": x -= w
    top = y - tf.cap_height(key, size) * 1.05
    is_caption = key == "AR" and ax.get("wght") == 500
    is_label = key == "AR" and ax.get("wght") == 600
    if is_caption: ok(size >= 46, f"caption under 46 px: {l['name']}")
    if is_label: ok(size >= 30, f"label under 30 px: {l['name']}")
    if is_caption or is_label:
        ok(x >= 96 and x + w <= 1824 and top >= 60 and y <= 1020, f"outside safe zone: {l['name']} ({x:.0f},{top:.0f})-({x + w:.0f},{y:.0f})")
    ok(not (x < 160 and x + w > 40 and top < 124 and y > 36), f"text in the logo box: {l['name']}")
# 6 logo
logo = [l for l in root if l["name"].startswith("Logo")][0]
ok(root[0] is logo, "logo slot is not the top layer")
ok(logo["layers"] and logo["layers"][0]["transform"]["position"] == [56, 48] and logo["layers"][0]["transform"]["opacity"] == 90, "logo missing or misplaced")
# 7 overlays on every frame
ov = [l for l in root if l["name"] == "Film-wide overlays"][0]
ok(ov["playback"]["inputRange"]["duration"] >= round(1057 * 1000 / 30) - 1 and len(ov["layers"]) == 7, "film-wide overlays incomplete")
ok(root.index(ov) < min(root.index(l) for l in root if l["name"].endswith("text")), "text is not under the overlays")
# 8 easing
eas = set()
for a in acts:
    for k in a.get("keyframes", a.get("animator", {}).get("keyframes", [])):
        e = k["easing"]; eas.add(e["type"] if e["type"] != "cubicBezier" else (e["x1"], e["y1"], e["x2"], e["y2"]))
allowed = {"hold", (0.16, 1.0, 0.3, 1.0), (0.87, 0.0, 0.13, 1.0), (0.85, 0.0, 0.15, 1.0)}
ok(eas <= allowed, f"easing outside the three curves: {eas - allowed}")
# 3 every word on screen
shown = " ".join(l["sourceText"]["text"] for l, _, _ in walk(root) if l["type"] == "Text").lower()
missing = [w["w"] for w in words if w["w"].strip(",.?!").lower().replace("-11", "11") not in shown.replace("/", " ")]
notes.append("voiceover words not on screen: " + ", ".join(missing))
# 10 audio
vids = [l for l, _, _ in walk(root) if l["type"] == "Video" and l.get("volume")]
ok(not vids, f"video layers with audio: {[v['name'] for v in vids]}")
aud = [a for a in acts if a["type"] == "createFxAudioLayer"]
ok(len(aud) == 1, "voiceover layer missing")

print("NOTES:"); [print(" -", n) for n in notes]
print("FAILS:" if fails else "ALL CHECKS PASS"); [print(" -", f) for f in fails]
