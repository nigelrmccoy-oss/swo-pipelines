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
await p.evaluate(() => document.querySelector('#views button[data-fly=home]').click()); await p.waitForTimeout(6000); await p.screenshot({ path: 'shots/smoke-home.png' });
console.log('home:', (await p.textContent('#homePanel h3')));
console.log('errors:', errs.length, errs.slice(0, 8).join('\n')); await b.close(); process.exit(errs.filter(e => !/Failed to load resource/.test(e)).length ? 1 : 0);
