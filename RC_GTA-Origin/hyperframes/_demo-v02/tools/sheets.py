"""Labelled contact sheets of the renamed snapshots: one sheet per demo section letter -> review/sheet_<X>.jpg."""
import os, re, sys
from PIL import Image, ImageDraw, ImageFont
src = sys.argv[1]
files = sorted(f for f in os.listdir(src) if re.match(r'f\d{4}_', f))
groups = {}
for f in files:
    groups.setdefault(f.split('_')[1].rstrip('0123456789'), []).append(f)
font = ImageFont.load_default(size=22)
W, H, COLS = 640, 360, 3
for g, fs in groups.items():
    rows = (len(fs) + COLS - 1) // COLS
    sheet = Image.new('RGB', (W * COLS, (H + 30) * rows), (40, 40, 40))
    for i, f in enumerate(fs):
        im = Image.open(os.path.join(src, f)).convert('RGB').resize((W, H), Image.LANCZOS)
        x, y = (i % COLS) * W, (i // COLS) * (H + 30)
        sheet.paste(im, (x, y + 30))
        ImageDraw.Draw(sheet).text((x + 6, y + 3), f[:-4], fill=(255, 220, 80), font=font)
    out = os.path.join(os.path.dirname(src.rstrip('/')), 'sheet_' + g + '.jpg')
    sheet.save(out, quality=88)
    print(out, len(fs))
