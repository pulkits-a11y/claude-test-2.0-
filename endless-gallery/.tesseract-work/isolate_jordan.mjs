// Keep only the left Jordan (shoe, sole, laces): drop the right shoe and both box parts,
// clear the left shoe's placement on the box so it sits at the origin, then prune unused data.
import { NodeIO } from '@gltf-transform/core';
import { ALL_EXTENSIONS } from '@gltf-transform/extensions';
import { prune } from '@gltf-transform/functions';
const [src, dst] = process.argv.slice(2);
const io = new NodeIO().registerExtensions(ALL_EXTENSIONS);
const doc = await io.read(src);
const root = doc.getRoot();
for (const n of root.listNodes()) {
  if (['Nike_AJ1_R', 'BoxBottom', 'BoxTop'].includes(n.getName())) n.dispose();
}
const left = root.listNodes().find(n => n.getName() === 'Nike_AJ1_L');
left.setTranslation([0, 0, 0]).setRotation([0, 0, 0, 1]).setScale([1, 1, 1]);
await doc.transform(prune());
await io.write(dst, doc);
console.log('meshes:', root.listMeshes().map(m => m.getName()).join(', '));
console.log('textures:', root.listTextures().length, 'materials:', root.listMaterials().map(m=>m.getName()).join(', '));
