// Deep links on a fresh load (QA P1-4): #view=…&open=…&l5off=1 must open the popup and switch the Line 5 scenario. Usage: node tests/deeplink.mjs [base-url]
import { createRequire } from 'module'; const require = createRequire(import.meta.url);
const { chromium } = require(process.env.PW || 'playwright');
const base = process.argv[2] || 'http://127.0.0.1:8770/?nohome';
const b = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] }); const p = await b.newPage({ viewport: { width: 1200, height: 800 } });
const errs = []; p.on('pageerror', e => errs.push('pageerror ' + e.message)); p.on('console', m => m.type() === 'error' && errs.push('console ' + m.text()));
await p.goto(base + '#view=sarnia&open=' + encodeURIComponent('Enbridge Line 9') + '&l5off=1', { timeout: 180000, waitUntil: 'domcontentloaded' });
await p.waitForFunction(() => window.SWO && document.getElementById('banner').textContent.includes('Imagery'), null, { timeout: 300000 }); await p.waitForTimeout(2000);
const r = await p.evaluate(() => ({ fp: document.querySelector('#faceplate:not(.hidden) h3')?.textContent || null, l5: document.getElementById('l5off').checked, kpiShut: /SHUT/.test(document.getElementById('kpis').textContent) }));
console.log('deeplink', JSON.stringify(r), 'errors', errs.length, errs.slice(0, 5).join(' | '));
const ok = /Line 9/.test(r.fp || '') && r.l5 && r.kpiShut && !errs.length; console.log(ok ? 'PASS' : 'FAIL'); await b.close(); process.exit(ok ? 0 : 1);
