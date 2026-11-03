// v0.4 checks: Code Critic P2/P3 fixes, terminals layer, wells layer (LOD cluster<->point), URL hash. Usage: node tests/v04.mjs [base-url]   (uses ?nohome)
import { createRequire } from 'module'; const require = createRequire(import.meta.url);
const { chromium } = require(process.env.PW || 'playwright');
const base = process.argv[2] || 'http://127.0.0.1:8770/?nohome';
const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
const errs = [], fails = [], ok = (c, m) => { if (!c) { fails.push(m); console.log('  FAIL', m); } };
async function load(vp, hash = '') {
  const p = await b.newPage({ viewport: vp }); p.on('pageerror', e => errs.push('pageerror ' + e.message)); p.on('console', m => m.type() === 'error' && errs.push('console ' + m.text()));
  await p.goto(base + hash, { timeout: 180000, waitUntil: 'domcontentloaded' }); await p.waitForFunction(() => window.SWO && document.getElementById('banner').textContent.includes('Imagery'), null, { timeout: 300000 }); await p.waitForTimeout(1500); return p;
}
const search = (p, q) => p.evaluate(q => { const s = document.getElementById('search'); s.value = q; s.onchange(); }, q);
const fpTitle = p => p.evaluate(() => { const f = document.getElementById('faceplate'); return f.classList.contains('hidden') ? null : (f.querySelector('h3')?.textContent || ''); });
const hash = p => p.evaluate(() => decodeURIComponent(location.hash));
// ---- P2/P3 at 1280x720
let p = await load({ width: 1280, height: 720 });
const lay = await p.evaluate(() => ({ sh: document.documentElement.scrollHeight, ih: innerHeight, head: document.getElementById('top').offsetHeight + document.getElementById('kpis').offsetHeight, legendHidden: document.getElementById('lgBody').style.display === 'none' }));
console.log('layout', JSON.stringify(lay)); ok(lay.legendHidden, 'legend not collapsed at 720p'); ok(lay.sh <= lay.ih, 'document taller than viewport'); ok(lay.head / lay.ih < 0.2, 'header+KPIs take >= 20% of 720p height');
for (const q of ['Line 6B', '6B', 'line 6b']) { await search(p, q); const t = await fpTitle(p); console.log('search', q, '->', t); ok(/Line 6B/i.test(t || '') && !/Marshall/i.test(t || ''), `search ${q} opens line 6B (got ${t})`); }
await search(p, 'Enbridge'); const eb = await p.evaluate(() => document.getElementById('faceplate').textContent); console.log('Enbridge ->', eb.slice(0, 70)); ok(/Operator named/.test(eb), 'Enbridge opens operator panel');
await search(p, 'Enbridge Line 9'); ok(/\/?Line 9/.test(await fpTitle(p) || ''), 'Line 9 opens'); ok(/open=/.test(await hash(p)), 'hash written on open: ' + await hash(p));
await search(p, 'zzqqxx'); ok(await fpTitle(p) === null, 'failed search closes faceplate');
await p.evaluate(() => window.SWO.fly('mtl')); await p.waitForTimeout(500); ok(/view=mtl/.test(await hash(p)), 'hash written on fly: ' + await hash(p));
await p.evaluate(() => { const c = document.getElementById('l5off'); c.checked = true; c.dispatchEvent(new Event('change')); }); ok(/l5off=1/.test(await hash(p)), 'hash written on l5off'); await p.close();
p = await load({ width: 1280, height: 720 }, '#view=sarnia&open=' + encodeURIComponent('Enbridge Line 9')); ok(/view=sarnia/.test(await hash(p)) && /Line 9/.test(await fpTitle(p) || ''), 'view+open keeps view: ' + await hash(p)); await p.close();
p = await load({ width: 1280, height: 720 }, '#open=bad-id'); const nf = await fpTitle(p); console.log('bad-id ->', nf); ok(/not found/i.test(nf || ''), '#open=bad-id shows not found'); await p.close();
p = await load({ width: 1600, height: 1000 }); const l6 = await p.evaluate(() => { window.SWO.open({ kind: 'line', x: window.SWO.D.lines.find(l => l.id === 'line6') }); return document.getElementById('faceplate').textContent; });
ok(!/98% legs matched/.test(l6), 'Line 6 popup legs-matched wording'); console.log('line6 wording:', (l6.match(/\d+% of the route length[^.]*/) || [''])[0].slice(0, 120));
// ---- terminals
const T = await p.evaluate(() => { const S = window.SWO, ts = S.V04.terminals || []; return { n: S.V04.info.terminals, kinds: ts.reduce((a, t) => (a[t.kind] = (a[t.kind] || 0) + 1, a), {}), sourced: ts.filter(t => t.capacity).length, est: ts.filter(t => t.est_volume_m3).length, badsrc: ts.filter(t => !t.sources || !t.sources.length).length, nopos: ts.filter(t => !t.pos_source).length }; });
console.log('terminals', JSON.stringify(T)); ok(T.n >= 60, 'terminals >= 60'); for (const k of ['crude', 'products', 'lng', 'ngl']) ok(T.kinds[k] > 0, 'terminal kind ' + k); ok(T.sourced >= 10, 'sourced capacities >= 10'); ok(!T.badsrc && !T.nopos, 'every terminal has sources and a position source');
const tp = await p.evaluate(() => { const S = window.SWO, t = S.V04.terminals.find(t => t.id === 'cushing'); S.open({ kind: 'term', x: t }); return document.getElementById('faceplate').textContent; });
ok(/97,742,000 bbl|97\.742 million bbl/.test(tp) && /ESTIMATE/.test(tp) && /sourced/.test(tp), 'Cushing popup: sourced capacity + ESTIMATE of tank farm'); ok(/m³/.test(tp), 'terminal popup shows metric');
await p.evaluate(() => document.querySelector('#filters button[data-c=terminals]').click()); ok(await p.evaluate(() => window.SWO.groups.terminals.every(o => o.show === false)), 'terminals toggle hides pins'); await p.evaluate(() => document.querySelector('#filters button[data-c=terminals]').click());
// ---- wells + LOD
await p.evaluate(() => document.querySelector('#filters button[data-c=wells]').click());
await p.waitForFunction(() => window.SWO.V04.state().shown.mode !== 'none', null, { timeout: 120000 });
const fi = await p.evaluate(() => window.SWO.V04.info.field_points); console.log('field points', fi); ok(fi >= 400, 'field infrastructure points (gas plants, compressors, field sites) >= 400');
const wstate = () => p.evaluate(() => window.SWO.V04.state().shown);
let s = await wstate(); console.log('wells initial', JSON.stringify(s)); ok(s.total > 250000, 'wells total > 250k'); ok(s.mode === 'clusters' && s.drawn < 4000, 'wide view uses clusters (<4000 prims)');
const go = async (lon, lat, h) => { await p.evaluate(([lon, lat, h]) => { const C = window.Cesium; window.SWO.viewer.camera.setView({ destination: C.Cartesian3.fromDegrees(lon, lat, h), orientation: { heading: 0, pitch: -1.55 } }); window.SWO.V04.rebuild(); }, [lon, lat, h]); await p.waitForTimeout(6000); return wstate(); };
s = await go(-81.9, 42.55, 2.5e4); console.log('wells zoomed (Lake Erie coast)', JSON.stringify(s)); ok(s.mode === 'points' && s.drawn > 0 && s.drawn <= 30000, 'zoomed view uses individual points');
const wp = await p.evaluate(() => { const W = window.SWO.V04.wells; const pr = W.pts && W.pts.length ? W.pts.get(0) : null; if (!pr) return null; window.SWO.open(pr.id.swo); return document.getElementById('faceplate').textContent; });
console.log('well popup:', (wp || '').replace(/\s+/g, ' ').slice(0, 220)); ok(wp && /status/i.test(wp) && /type/i.test(wp) && /operator/i.test(wp), 'well popup has status/type/operator');
await p.evaluate(() => { const C = window.Cesium; window.SWO.viewer.camera.setView({ destination: C.Cartesian3.fromDegrees(-88, 44, 4e6) }); window.SWO.V04.rebuild(); }); await p.waitForTimeout(6000); s = await wstate(); console.log('wells world view', JSON.stringify(s)); ok(s.mode === 'clusters' && s.drawn < 4000, 'world view back to clusters');
await p.evaluate(() => document.querySelector('#filters button[data-c=wells]').click()); await p.waitForTimeout(500); ok((await wstate()).mode === 'none' || !(await p.evaluate(() => window.SWO.V04.wells.on)), 'wells toggle off clears');
console.log('errors', errs.length, errs.filter(e => !/Failed to load resource/.test(e)).slice(0, 5).join(' | ')); await b.close();
console.log(fails.length ? 'v04 checks: FAIL ' + fails.join('; ') : 'v04 checks: PASS'); process.exit(fails.length || errs.filter(e => !/Failed to load resource/.test(e)).length ? 1 : 0);
