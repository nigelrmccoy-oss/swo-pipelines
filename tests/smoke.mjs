// Headless smoke: load app, wait for layers, click a researched line, open home panel, toggle scenario; fail on page errors. Usage: node tests/smoke.mjs [url]
import { createRequire } from 'module'; import { mkdirSync } from 'fs'; mkdirSync('shots', { recursive: true });
const require = createRequire(import.meta.url);
const { chromium } = require(process.env.PW || 'playwright');
const url = process.argv[2] || 'http://127.0.0.1:8770/';
const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] }); const p = await b.newPage({ viewport: { width: 1600, height: 1000 } });
const errs = []; p.on('pageerror', e => errs.push('pageerror ' + e.message)); p.on('console', m => m.type() === 'error' && errs.push('console ' + m.text()));
await p.goto(url); await p.waitForFunction(() => window.SWO && document.getElementById('banner').textContent.includes('Imagery'), null, { timeout: 180000 });
const ds = await p.evaluate(() => window.SWO.datasets.map(d => d.name + ':' + d.n)); console.log('datasets', ds.join(' '));
await p.waitForTimeout(6000); await p.screenshot({ path: 'shots/smoke-swo.png', timeout: 90000 }).catch(() => console.log('  (screenshot timed out under swiftshader)'));
await p.evaluate(() => document.querySelector('#mapLegend div[data-s="Enbridge Line 5"]').click()); await p.waitForTimeout(4000);
console.log('faceplate:', (await p.textContent('#faceplate h3')));
await p.evaluate(() => { const c = document.getElementById('l5off'); c.checked = true; c.dispatchEvent(new Event('change')); }); console.log('kpi:', (await p.textContent('#kpis')).slice(0, 90));
if (await p.evaluate(() => !!document.querySelector('#views button[data-fly=home]'))) { await p.evaluate(() => document.querySelector('#views button[data-fly=home]').click()); await p.waitForTimeout(6000); console.log('home layer: present (private file), panel:', (await p.textContent('#homePanel h3')).length > 0 ? 'ok' : 'EMPTY'); } else console.log('home layer: absent (no private file) - hidden OK');
for (const v of ['na', 'swo', 'sarnia', 'mack', 'lakeont', 'mtl', 'east']) { await p.evaluate(v => document.querySelector(`#views button[data-fly=${v}]`).click(), v); await p.waitForTimeout(5000); await p.screenshot({ path: `shots/smoke-view-${v}.png`, timeout: 60000 }).catch(() => console.log("  (screenshot timed out under swiftshader)")); console.log('view', v, 'ok'); }
for (const c of ['crude', 'gas', 'products', 'depots', 'decom', 'stations']) { const r = await p.evaluate(c => { const b = document.querySelector(`#filters button[data-c="${c}"]`); b.click(); const off = window.SWO.show[c]; b.click(); return [off, window.SWO.show[c], (window.SWO.groups[c] || []).length]; }, c); console.log('toggle', c, r); }
for (const q of ['Trans-Northern Pipeline (TNPI)', 'Shell Oakville refinery (former)', 'Suncor Montreal refinery', 'Iroquois Gas Transmission System', 'Enbridge Line 9']) { const t = await p.evaluate(q => { const h = window.SWO.searchIndex.find(s => s.label.startsWith(q)); if (!h) return 'NOT FOUND'; window.SWO.goTo(h); return document.querySelector('#faceplate h3').textContent + ' | ' + (document.querySelector('#faceplate').textContent.match(/route accuracy.{0,60}|position.{0,60}/) || [''])[0]; }, q); console.log('search', q, '->', t); }

// v0.3.1 checks: search ranking, Line 7 endpoints-only/no flow, no Mexico layer, accuracy fields, deep links on a fresh load
const chk = await p.evaluate(() => { const S = window.SWO, f = q => S.findSearch(q)?.label || null;
  return { line7: f('Enbridge Line 7'), line78: f('Enbridge Line 78'), line9: f('line 9'), empty: f(''), none: f('zzqqxx'), l7flows: S.flows.filter(x => x.ln.id === 'line7' || x.ln.id === 'line11').length, l6bflows: S.flows.filter(x => x.ln.id === 'line6b').length,
    mexico: S.datasets.some(d => /mexico/.test(d.name)), l7acc: S.D.lines.find(l => l.id === 'line7').route_accuracy.level, version: S.version, ver: S.D.version }; });
console.log('v031', JSON.stringify(chk));
const fails = [];
if (!/^Enbridge Line 7 /.test(chk.line7 || '')) fails.push('search Line 7'); if (!/Line 78/.test(chk.line78 || '')) fails.push('search Line 78'); if (chk.empty || chk.none) fails.push('empty/no-match search');
if (chk.l7flows || chk.l6bflows) fails.push('flow on endpoints-only/replaced line'); if (chk.mexico) fails.push('mexico layer'); if (!/unknown route/.test(chk.l7acc)) fails.push('line7 accuracy');
await p.evaluate(() => { const s = document.getElementById('search'); s.value = 'zzqqxx'; s.onchange(); }); const msg = await p.textContent('#searchMsg'); console.log('no-match msg:', msg); if (!/No match/.test(msg)) fails.push('no-match feedback');
console.log('v031 checks:', fails.length ? 'FAIL ' + fails.join(', ') : 'PASS');
await p.waitForTimeout(3000);
console.log('errors:', errs.length, errs.slice(0, 8).join('\n')); await b.close(); process.exit(errs.filter(e => !/Failed to load resource/.test(e)).length || fails.length ? 1 : 0);
