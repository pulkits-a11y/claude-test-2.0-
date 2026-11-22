// Make a reduced-detail copy of a shoe for distant rows: drop normal maps and tangents,
// weld, simplify, recompute smooth normals, and shrink textures.
import { NodeIO } from '@gltf-transform/core';
import { ALL_EXTENSIONS } from '@gltf-transform/extensions';
import { weld, simplify, normals, prune, dedup, textureCompress } from '@gltf-transform/functions';
import { MeshoptSimplifier } from 'meshoptimizer';
import sharp from 'sharp';
const [src, dst, ratio, error, tex, keepNormalMap] = process.argv.slice(2);
const io = new NodeIO().registerExtensions(ALL_EXTENSIONS);
const doc = await io.read(src);
const root = doc.getRoot();
if (keepNormalMap !== 'keep') {
  for (const m of root.listMaterials()) m.setNormalTexture(null);
  for (const mesh of root.listMeshes()) for (const p of mesh.listPrimitives()) {
    for (const a of ['TANGENT', 'NORMAL']) { const acc = p.getAttribute(a); if (acc) p.setAttribute(a, null); }
  }
}
await MeshoptSimplifier.ready;
await doc.transform(
  dedup(),
  weld(),
  simplify({ simplifier: MeshoptSimplifier, ratio: Number(ratio), error: Number(error) }),
  normals({ overwrite: false }),
  textureCompress({ encoder: sharp, resize: [Number(tex), Number(tex)] }),
  prune(),
);
await io.write(dst, doc);
let tris = 0;
for (const mesh of root.listMeshes()) for (const p of mesh.listPrimitives()) tris += (p.getIndices()?.getCount() ?? p.getAttribute('POSITION').getCount()) / 3;
console.log(dst.split('/').pop(), 'tris', tris);
