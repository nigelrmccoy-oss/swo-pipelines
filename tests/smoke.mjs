// Headless smoke: load app, wait for layers, click a researched line, open home panel, toggle scenario; fail on page errors. Usage: node tests/smoke.mjs [url]
import { createRequire } from 'module';
const require = createRequire(import.meta.url);
const { chromium } = require(process.env.PW || '/home/nig/qa-2026-10-08/pw/node_modules/playwright');
const url = process.argv[2] || 'http://localhost:8770/';
const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] }); const p = await b.newPage({ viewport: { width: 1600, height: 1000 } });
const errs = []; p.on('pageerror', e => errs.push('pageerror ' + e.message)); p.on('console', m => m.type() === 'error' && errs.push('console ' + m.text()));
await p.goto(url); await p.waitForFunction(() => window.SWO && document.getElementById('banner').textContent.includes('Imagery'), null, { timeout: 180000 });
const ds = await p.evaluate(() => window.SWO.datasets.map(d => d.name + ':' + d.n)); console.log('datasets', ds.join(' '));
await p.waitForTimeout(6000); await p.screenshot({ path: 'shots/smoke-swo.png' });
await p.evaluate(() => document.querySelector('#mapLegend div[data-s="Enbridge Line 5"]').click()); await p.waitForTimeout(4000);
console.log('faceplate:', (await p.textContent('#faceplate h3')));
await p.evaluate(() => { const c = document.getElementById('l5off'); c.checked = true; c.dispatchEvent(new Event('change')); }); console.log('kpi:', (await p.textContent('#kpis')).slice(0, 90));
if (await p.evaluate(() => !!document.querySelector('#views button[data-fly=home]'))) { await p.evaluate(() => document.querySelector('#views button[data-fly=home]').click()); await p.waitForTimeout(6000); console.log('home layer: present (private file), panel:', (await p.textContent('#homePanel h3')).length > 0 ? 'ok' : 'EMPTY'); } else console.log('home layer: absent (no private file) - hidden OK');
for (const v of ['na', 'swo', 'sarnia', 'mack', 'lakeont', 'mtl', 'east']) { await p.evaluate(v => document.querySelector(`#views button[data-fly=${v}]`).click(), v); await p.waitForTimeout(5000); await p.screenshot({ path: `shots/smoke-view-${v}.png`, timeout: 60000 }).catch(() => console.log("  (screenshot timed out under swiftshader)")); console.log('view', v, 'ok'); }
for (const c of ['crude', 'gas', 'products', 'depots', 'decom', 'stations']) { const r = await p.evaluate(c => { const b = document.querySelector(`#filters button[data-c="${c}"]`); b.click(); const off = window.SWO.show[c]; b.click(); return [off, window.SWO.show[c], (window.SWO.groups[c] || []).length]; }, c); console.log('toggle', c, r); }
for (const q of ['Trans-Northern Pipeline (TNPI)', 'Shell Oakville refinery (former)', 'Suncor Montreal refinery', 'Iroquois Gas Transmission System', 'Enbridge Line 9']) { const t = await p.evaluate(q => { const h = window.SWO.searchIndex.find(s => s.label.startsWith(q)); if (!h) return 'NOT FOUND'; window.SWO.goTo(h); return document.querySelector('#faceplate h3').textContent + ' | ' + (document.querySelector('#faceplate').textContent.match(/route accuracy.{0,60}|position.{0,60}/) || [''])[0]; }, q); console.log('search', q, '->', t); }
await p.waitForTimeout(3000);
console.log('errors:', errs.length, errs.slice(0, 8).join('\n')); await b.close(); process.exit(errs.filter(e => !/Failed to load resource/.test(e)).length ? 1 : 0);
