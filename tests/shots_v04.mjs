// Page-only screenshots for v0.4 (terminals, wells LOD, compact 720p chrome). ?nohome so no private data. Usage: node tests/shots_v04.mjs [prefix] [base-url]
import { createRequire } from 'module'; import { mkdirSync } from 'fs'; const require = createRequire(import.meta.url);
const { chromium } = require(process.env.PW || 'playwright');
const prefix = process.argv[2] || 'v04', base = process.argv[3] || 'http://127.0.0.1:8770/?nohome'; mkdirSync('shots', { recursive: true });
const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
async function page(vp) { const p = await b.newPage({ viewport: vp }); p.errs = []; p.on('pageerror', e => p.errs.push(e.message));
  await p.goto(base, { timeout: 180000, waitUntil: 'domcontentloaded' }); await p.waitForFunction(() => window.SWO && document.getElementById('banner').textContent.includes('Imagery'), null, { timeout: 300000 }); return p; }
const snap = async (p, n, wait = 12000) => { await p.waitForTimeout(wait); await p.screenshot({ path: `shots/${prefix}-${n}.png`, timeout: 240000 }).then(() => console.log('shot', n), e => console.log('FAILED', n, e.message.split('\n')[0])); };
const p = await page({ width: 1600, height: 1000 }); const ev = (f, a) => p.evaluate(f, a);
const view = (lon, lat, h, pitch = -60) => ev(([lon, lat, h, pitch]) => { const C = window.Cesium; window.SWO.viewer.camera.setView({ destination: C.Cartesian3.fromDegrees(lon, lat, h), orientation: { heading: 0, pitch: C.Math.toRadians(pitch) } }); window.SWO.V04.rebuild(); }, [lon, lat, h, pitch]);
const openT = id => ev(id => { const S = window.SWO; S.open({ kind: 'term', x: S.V04.terminals.find(t => t.id === id) }); }, id);
const flyT = id => ev(id => { const S = window.SWO, t = S.V04.terminals.find(t => t.id === id), C = window.Cesium; S.viewer.camera.setView({ destination: C.Cartesian3.fromDegrees(t.lon, t.lat - 0.02, 12000), orientation: { heading: 0, pitch: C.Math.toRadians(-55) } }); }, id);
await ev(() => window.SWO.fly('na', 0)); await snap(p, '01-na-terminals', 15000);
await view(-81.9, 43.0, 4.5e5, -70); await snap(p, '02-swo-terminals', 12000);
await flyT('cushing'); await openT('cushing'); await snap(p, '03-cushing-popup');
await flyT('bayonne'); await openT('bayonne'); await snap(p, '04-nyharbor-bayonne');
await flyT('canaport'); await openT('canaport'); await snap(p, '05-canaport-lng');
await ev(() => document.querySelector('#filters button[data-c=wells]').click()); await view(-90, 42, 3.5e6, -90); await snap(p, '06-wells-clusters-world', 20000);
await view(-82.9, 42.6, 3.0e5, -70); await snap(p, '07-wells-clusters-lake-erie-region', 15000);
await view(-81.85, 42.57, 3.2e4, -60); await snap(p, '08-wells-points-lake-erie-offshore', 15000);
await ev(() => { const W = window.SWO.V04.wells; const o = W.pts.get(0); window.SWO.open(o.id.swo); }); await snap(p, '09-well-popup', 4000);
await view(-84.6, 44.6, 6e5, -80); await snap(p, '10-wells-michigan', 15000);
console.log('errors', p.errs.length, p.errs.slice(0, 3).join(' | ')); await p.close();
const m = await page({ width: 1280, height: 720 }); await m.evaluate(() => window.SWO.fly('swo', 0)); await snap(m, '11-720p-compact-chrome', 12000);
const sm = await page({ width: 390, height: 844 }); await sm.evaluate(() => document.querySelector('#filters button[data-c=wells]').click()); await snap(sm, '12-mobile-wells', 12000); console.log('mobile errors', sm.errs.length); await b.close();
