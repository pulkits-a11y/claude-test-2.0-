import { NodeIO } from '@gltf-transform/core';
import { ALL_EXTENSIONS } from '@gltf-transform/extensions';
const [src, dst] = process.argv.slice(2);
const io = new NodeIO().registerExtensions(ALL_EXTENSIONS);
const doc = await io.read(src);
for (const e of doc.getRoot().listExtensionsUsed()) if (e.extensionName === 'KHR_materials_unlit') e.dispose();
for (const m of doc.getRoot().listMaterials()) { m.setEmissiveTexture(null); m.setEmissiveFactor([0,0,0]); m.setRoughnessFactor(0.55); m.setMetallicFactor(0); }
await io.write(dst, doc);
