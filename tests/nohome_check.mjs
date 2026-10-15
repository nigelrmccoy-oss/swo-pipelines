// Fresh-clone check: app must load with no data/private/home.json (home layer hidden, no page errors). Usage: node tests/nohome_check.mjs [url]
import { createRequire } from 'module'; const require = createRequire(import.meta.url);
const { chromium } = require(process.env.PW || '/home/nig/qa-2026-10-08/pw/node_modules/playwright');
const url = process.argv[2] || 'http://localhost:8770/?nohome';
const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] }); const p = await b.newPage({ viewport: { width: 1200, height: 800 } });
const errs = []; p.on('pageerror', e => errs.push('pageerror ' + e.message)); p.on('console', m => m.type() === 'error' && errs.push('console ' + m.text()));
await p.goto(url); await p.waitForFunction(() => window.SWO && document.getElementById('banner').textContent.includes('Imagery'), null, { timeout: 300000 });
const r = await p.evaluate(() => ({ homeBtn: !!document.querySelector('#views button[data-fly=home]'), homeFilter: !!document.querySelector('#filters button[data-c=home]'), H: !!window.SWO.H, kpiHome: /home/i.test(document.getElementById('kpis').textContent), lines: window.SWO.D.lines.length }));
console.log(JSON.stringify(r)); const bad = errs.filter(e => !/404|Failed to load resource/.test(e)); console.log('errors(non-404):', bad.length, bad.join('\n'), '| 404s:', errs.length - bad.length);
await b.close(); process.exit(bad.length || r.homeBtn || r.H ? 1 : 0);
