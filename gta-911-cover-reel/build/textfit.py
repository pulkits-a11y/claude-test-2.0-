"""Measures text with the same font files the project embeds (HarfBuzz shaping, variable axes),
so word-by-word captions can be laid out as one line and placed one word per layer."""
import os
import uharfbuzz as hb
from fontTools.ttLib import TTFont

FONTS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "source", "fonts")
FILES = {"AR": os.path.join(FONTS, "Archivo[wdth,wght].ttf"), "IS": os.path.join(FONTS, "InstrumentSerif-Regular.ttf")}
_face, _cap = {}, {}


def _hbfont(key):
    if key not in _face:
        blob = hb.Blob.from_file_path(FILES[key])
        _face[key] = hb.Face(blob)
        _cap[key] = TTFont(FILES[key])["OS/2"].sCapHeight / _face[key].upem
    return _face[key]


def advance(key, text, size, axes=None, tracking=0):
    """Advance width in px; tracking is in 1/1000 em, added after every glyph but the last."""
    face = _hbfont(key)
    font = hb.Font(face)
    if axes: font.set_variations(axes)
    buf = hb.Buffer(); buf.add_str(text); buf.guess_segment_properties(); hb.shape(font, buf, {})
    adv = sum(p.x_advance for p in buf.glyph_positions) / face.upem * size
    n = len(buf.glyph_infos)
    return adv + tracking / 1000 * size * max(0, n - 1)


def cap_height(key, size):
    _hbfont(key)
    return _cap[key] * size


def line_layout(key, words, size, axes=None, tracking=0, x=960, align="center"):
    """x positions (baseline-left) for each word of a one-line phrase."""
    space = advance(key, " ", size, axes) + tracking / 1000 * size
    widths = [advance(key, w, size, axes, tracking) for w in words]
    total = sum(widths) + space * (len(words) - 1)
    if align == "center": x0 = x - total / 2
    elif align == "right": x0 = x - total
    else: x0 = x
    xs, cur = [], x0
    for w in widths:
        xs.append(cur); cur += w + space
    return xs, widths, total
