// node render.js '<json list of specs with name>' outdir
const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const specs = JSON.parse(process.argv[2]); const out = process.argv[3];
  const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
  const p = await b.newPage();
  p.on('pageerror', e => console.log('PAGEERR', e.message));
  for (const s of specs) {
    await p.goto('file://' + path.resolve(__dirname, 'stroke.html') + '?n=' + s.name + '#' + encodeURIComponent(JSON.stringify(s)));
    await p.waitForFunction('window.DONE === true', null, { timeout: 30000 });
    await p.waitForTimeout(300);
    const data = await p.evaluate(() => document.querySelector('canvas').toDataURL('image/png'));
    require('fs').writeFileSync(path.join(out, s.name + '.png'), Buffer.from(data.split(',')[1], 'base64'));
    console.log('wrote', s.name);
  }
  await b.close();
})();
