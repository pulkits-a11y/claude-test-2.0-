"""Text measurement with HarfBuzz at explicit variable-font axes (matches Tesseract's fontVariations)."""
import uharfbuzz as hb, os
FONTS = {
    "archivo": "/home/user/claude-test-2.0-/nike-reel/Sources/fonts/Archivo[wdth,wght].ttf",
    "serif": "/home/user/claude-test-2.0-/nike-reel/Sources/fonts/InstrumentSerif-Regular.ttf",
    "serif_italic": "/home/user/claude-test-2.0-/nike-reel/Sources/fonts/InstrumentSerif-Italic.ttf",
}
_cache = {}
def _font(key, axes):
    k = (key, tuple(sorted((axes or {}).items())))
    if k not in _cache:
        blob = hb.Blob.from_file_path(FONTS[key]); face = hb.Face(blob); f = hb.Font(face)
        if axes: f.set_variations(axes)
        _cache[k] = (f, face.upem)
    return _cache[k]
def advance(text, key, size, axes=None, tracking=0):
    """Advance width in px of `text` at font size `size`; tracking in 1/1000 em per glyph."""
    f, upem = _font(key, axes)
    buf = hb.Buffer(); buf.add_str(text); buf.guess_segment_properties()
    hb.shape(f, buf, {"kern": True, "liga": True})
    adv = sum(p.x_advance for p in buf.glyph_positions)
    return adv * size / upem + len(buf.glyph_positions) * tracking / 1000 * size
def layout_line(words, specs, gap_em=None):
    """words: list of str; specs: list of (fontkey, size, axes, tracking). Returns x offsets (from 0) and total width."""
    xs, x = [], 0.0
    for i, (w, s) in enumerate(zip(words, specs)):
        xs.append(x)
        x += advance(w, s[0], s[1], s[2], s[3])
        if i + 1 < len(words):
            # inter-word space taken from the larger of the two neighbouring styles
            s2 = specs[i + 1]
            sp = max(advance(" ", s[0], s[1], s[2], s[3]), advance(" ", s2[0], s2[1], s2[2], s2[3]))
            x += sp if gap_em is None else gap_em * max(s[1], s2[1])
    return xs, x
