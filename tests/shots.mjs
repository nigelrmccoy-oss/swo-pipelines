// Page-only screenshots (no desktop capture) of key views/popups for release QA. Uses ?nohome so no private data appears. Usage: node tests/shots.mjs [prefix] [base-url]
import { createRequire } from 'module'; import { mkdirSync } from 'fs'; const require = createRequire(import.meta.url);
const { chromium } = require(process.env.PW || 'playwright');
const prefix = process.argv[2] || 'shot', base = process.argv[3] || 'http://127.0.0.1:8770/?nohome'; mkdirSync('shots', { recursive: true });
const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
async function page(vp) { const p = await b.newPage({ viewport: vp }); p.errs = []; p.on('pageerror', e => p.errs.push(e.message));
  await p.goto(base, { timeout: 180000, waitUntil: 'domcontentloaded' }); await p.waitForFunction(() => window.SWO && document.getElementById('banner').textContent.includes('Imagery'), null, { timeout: 300000 }); return p; }
const snap = async (p, n, wait = 15000) => { await p.waitForTimeout(wait); await p.screenshot({ path: `shots/${prefix}-${n}.png`, timeout: 240000 }).then(() => console.log('shot', n), e => console.log('FAILED', n, e.message.split('\n')[0])); };
const p = await page({ width: 1600, height: 1000 });
const ev = (f, a) => p.evaluate(f, a);
const fly = v => ev(v => window.SWO.fly(v, 0), v);
const openLine = id => ev(id => window.SWO.open({ kind: 'line', x: window.SWO.D.lines.find(l => l.id === id) }), id);
const view = (lon, lat, h, pitch = -50) => ev(([lon, lat, h, pitch]) => { const C = window.Cesium; window.SWO.viewer.camera.setView({ destination: C.Cartesian3.fromDegrees(lon, lat, h), orientation: { heading: 0, pitch: C.Math.toRadians(pitch) } }); }, [lon, lat, h, pitch]);
await fly('swo'); await snap(p, '01-swo', 20000);
await view(-82.42, 42.80, 9e4, -60); await openLine('line78'); await snap(p, '02-sarnia-line78-ends');
await ev(() => { const C = window.Cesium; window.SWO.viewer.camera.setView({ destination: C.Rectangle.fromDegrees(-82.6, 42.4, -79.6, 43.6) }); }); await openLine('line7'); await snap(p, '03-line7-endpoints-only');
await openLine('line6b'); await snap(p, '04-line6b-replaced', 8000);
await view(-87.5, 41.9, 1.2e6, -70); await openLine('line6'); await snap(p, '05-line6-eia-straight-runs-dashed');
await fly('mack'); await ev(() => { const c = document.getElementById('l5off'); c.checked = true; c.dispatchEvent(new Event('change')); document.getElementById('faceplate').classList.add('hidden'); }); await snap(p, '06-mack-line5-shut');
await ev(() => { const c = document.getElementById('l5off'); c.checked = false; c.dispatchEvent(new Event('change')); }); await fly('lakeont'); await snap(p, '07-lakeont');
await fly('mtl'); await openLine('tnpi'); await snap(p, '08-mtl-tnpi-partial');
await fly('east'); await openLine('colonial'); await snap(p, '09-east-colonial');
await ev(() => { const s = document.getElementById('search'); s.value = 'Enbridge Line 7'; s.onchange(); }); await snap(p, '10-search-line7');
await ev(() => { const s = document.getElementById('search'); s.value = 'nonexistent pipeline'; s.onchange(); }); await snap(p, '11-search-nomatch', 5000);
console.log('errors', p.errs.length, p.errs.slice(0, 3).join(' | ')); await p.close();
const m = await page({ width: 390, height: 844 }); await m.evaluate(() => window.SWO.fly('swo', 0)); await snap(m, '12-mobile');
await m.evaluate(() => window.SWO.open({ kind: 'line', x: window.SWO.D.lines.find(l => l.id === 'line7') })); await snap(m, '13-mobile-popup', 6000);
console.log('mobile errors', m.errs.length); await b.close();
