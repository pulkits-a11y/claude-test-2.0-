# Remove unused vertex attributes (e.g. TEXCOORD_2) from every primitive of a GLB.
# Geometry, textures and the binary buffer are untouched; only the JSON references go.
import json, struct, sys
src, dst, *drop = sys.argv[1:]
b = open(src, 'rb').read()
clen, ctype = struct.unpack('<II', b[12:20])
j = json.loads(b[20:20+clen]); rest = b[20+clen:]
n = 0
for m in j['meshes']:
    for pr in m['primitives']:
        for a in drop:
            if a in pr['attributes']:
                del pr['attributes'][a]; n += 1
js = json.dumps(j, separators=(',', ':')).encode()
js += b' ' * ((4 - len(js) % 4) % 4)
out = struct.pack('<4sII', b'glTF', 2, 12 + 8 + len(js) + len(rest)) + struct.pack('<II', len(js), 0x4E4F534A) + js + rest
open(dst, 'wb').write(out)
print(dst.split('/')[-1], 'removed', n, 'attribute refs')
