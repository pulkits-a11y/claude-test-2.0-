// Stand-in only: drop KHR_materials_unlit from the scanned Dunk so it reacts to scene lights.
import { NodeIO } from '@gltf-transform/core';
import { ALL_EXTENSIONS } from '@gltf-transform/extensions';
const [src, dst] = process.argv.slice(2);
const io = new NodeIO().registerExtensions(ALL_EXTENSIONS);
const doc = await io.read(src);
for (const ext of doc.getRoot().listExtensionsUsed()) if (ext.extensionName === 'KHR_materials_unlit') ext.dispose();
for (const m of doc.getRoot().listMaterials()) { m.setRoughnessFactor(0.6); m.setMetallicFactor(0); }
await io.write(dst, doc);
console.log('wrote', dst);
