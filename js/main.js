/** SWO-PIPELINES v0.1: three.js schematic map of pipelines driven by data/pipelines.json, with animated flow and a Line 5 shutdown scenario. */
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

const LAT0 = 43.0, LON0 = -82.5;
const KX = Math.cos(LAT0 * Math.PI / 180) * 11.132, KZ = 11.054; // 1 unit = 10 km
const proj = (lat, lon) => [(lon - LON0) * KX, -(lat - LAT0) * KZ];
const COL = { 'crude/NGL': '#ff8c1a', crude: '#e04040', gas: '#3fa7ff', products: '#2ecc71' };
const FAC_COL = { storage: '#c9a0ff', refinery: '#ffd700', cluster: '#ff69b4' };
const D = await (await fetch('data/pipelines.json')).json();
const show = { 'crude/NGL': true, crude: true, gas: true, products: true, fac: true };
let speed = 1, l5off = false;
const DEP_L5 = ['line5', 'line5_straits']; // segments that stop when Line 5 is shut at the Straits

const canvas = document.getElementById('map3d');
const r = new THREE.WebGLRenderer({ canvas, antialias: true, preserveDrawingBuffer: true }); r.setPixelRatio(Math.min(devicePixelRatio, 2));
const scene = new THREE.Scene(); scene.background = new THREE.Color('#0d1217');
const cam = new THREE.PerspectiveCamera(50, 1, 0.5, 5000); cam.position.set(-20, 120, 110);
const ctl = new OrbitControls(cam, canvas); ctl.target.set(-15, 0, -5); ctl.maxPolarAngle = Math.PI * 0.47; ctl.enableDamping = true;
scene.add(new THREE.HemisphereLight('#cfe8ff', '#1b2a1b', 1.1));
const grid = new THREE.GridHelper(600, 60, '#24352a', '#1c2a20'); scene.add(grid);
// lat/lon graticule labels
function label(text, x, z, color = '#8696a6', size = 26) {
  const c = document.createElement('canvas'); c.width = 512; c.height = 64; const g = c.getContext('2d');
  g.font = `${size}px system-ui`; g.fillStyle = color; g.fillText(text, 4, 40);
  const s = new THREE.Sprite(new THREE.SpriteMaterial({ map: new THREE.CanvasTexture(c), depthTest: false, transparent: true }));
  s.scale.set(24, 3, 1); s.position.set(x + 11, 1.5, z); scene.add(s); return s;
}
const places = {};
for (const x of [...D.lines, ...D.facilities]) for (const w of x.waypoints) places[w[2]] = w;
for (const [n, w] of Object.entries(places)) { const [x, z] = proj(w[0], w[1]); label(n.replace('_N', ' N shore'), x, z); const m = new THREE.Mesh(new THREE.SphereGeometry(0.4), new THREE.MeshBasicMaterial({ color: '#8696a6' })); m.position.set(x, 0.2, z); scene.add(m); }
// Ontario-Michigan border hint: St. Clair River / Detroit River line (approx)
{ const pts = [[43.0, -82.42], [42.6, -82.55], [42.33, -83.05], [42.05, -83.15]].map(p => { const [x, z] = proj(...p); return new THREE.Vector3(x, 0.05, z); });
  scene.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints(pts), new THREE.LineDashedMaterial({ color: '#2f8fd8', dashSize: 1, gapSize: 1 })).computeLineDistances()); }

const objs = []; const flows = [];
const capMax = { 'bbl/d': 667000, 'Bcf/d': 2.4, 'PJ/d': 7.89 };
D.lines.forEach((ln, i) => {
  const lift = 0.5 + (i % 6) * 0.35; // offset overlapping corridors
  const pts = ln.waypoints.map(w => { const [x, z] = proj(w[0], w[1]); return new THREE.Vector3(x, lift, z); });
  const curve = new THREE.CatmullRomCurve3(pts, false, 'centripetal', 0.2);
  const dia = typeof ln.diameter_in.value === 'number' ? ln.diameter_in.value : 24;
  const color = ln.kind === 'project' ? '#ffffff' : COL[ln.commodity];
  const mat = new THREE.MeshLambertMaterial({ color, transparent: ln.kind === 'project', opacity: ln.kind === 'project' ? 0.45 : 1, emissive: color, emissiveIntensity: 0.25 });
  const tube = new THREE.Mesh(new THREE.TubeGeometry(curve, Math.max(20, pts.length * 24), 0.08 + dia / 120, 8, false), mat);
  tube.userData = ln; scene.add(tube); objs.push(tube);
  const frac = ln.cap_num && capMax[ln.cap_unit] ? ln.cap_num / capMax[ln.cap_unit] : 0.15;
  const n = Math.round(6 + 30 * frac), dots = [];
  for (let k = 0; k < n; k++) { const s = new THREE.Mesh(new THREE.SphereGeometry(0.12 + dia / 100), new THREE.MeshBasicMaterial({ color: '#ffffff' })); scene.add(s); dots.push({ s, t: k / n }); }
  flows.push({ ln, tube, curve, dots, v: 0.01 + 0.04 * frac, len: curve.getLength() });
});
D.facilities.forEach(f => {
  const [x, z] = proj(f.waypoints[0][0], f.waypoints[0][1]);
  const off = { imperial: [0.8, -0.8], suncor: [-0.8, 0.8], chemvalley: [1.6, 0.4], shell: [0, 0], dawn: [0, 0], tecumseh: [0, 0] }[f.id] || [0, 0];
  const g = f.kind === 'storage' ? new THREE.CylinderGeometry(1.6, 1.6, 2, 20) : new THREE.BoxGeometry(1.2, 2.4, 1.2);
  const m = new THREE.Mesh(g, new THREE.MeshLambertMaterial({ color: FAC_COL[f.kind], emissive: FAC_COL[f.kind], emissiveIntensity: 0.3 }));
  m.position.set(x + off[0], 1.2, z + off[1]); m.userData = f; scene.add(m); objs.push(m);
});

// legend
const lg = document.getElementById('mapLegend');
lg.innerHTML = '<b>Lines (click)</b>' + D.lines.map(l => `<div data-id="${l.id}"><i style="background:${l.kind === 'project' ? '#fff' : COL[l.commodity]}"></i>${l.name}</div>`).join('') +
  '<b>Facilities</b>' + D.facilities.map(f => `<div data-id="${f.id}"><i style="background:${FAC_COL[f.kind]}"></i>${f.name}</div>`).join('') +
  `<small style="color:#8696a6">${D.lines.length} lines · ${D.facilities.length} facilities · ${D.sources.length} sources</small>`;
lg.onclick = e => { const d = e.target.closest('div[data-id]'); if (d) open([...D.lines, ...D.facilities].find(x => x.id === d.dataset.id)); };

// faceplate
const fp = document.getElementById('faceplate');
const val = f => { if (!f) return '<span class="unk">unknown</span>'; const v = Array.isArray(f.value) ? f.value.join(' → ') : f.value; return `${v === 'unknown' ? '<span class="unk">unknown</span>' : v}<br>${(f.sources || []).map((s, i) => `<a href="${s}" target="_blank">[${new URL(s).hostname.replace('www.', '')}]</a>`).join('')}`; };
function open(x) {
  const rows = ['operator', 'product', 'diameter_in', 'capacity', 'length', 'route', 'endpoints', 'in_service', 'status'].filter(k => x[k]).map(k => `<tr><td>${k.replace('_in', ' (in)').replace('_', ' ')}</td><td>${val(x[k])}</td></tr>`).join('');
  const inc = (x.incidents || []).map(i => `<tr><td>incident</td><td>${val(i)}</td></tr>`).join('');
  const wp = `<tr><td>waypoints (approx)</td><td>${x.waypoints.map(w => `${w[2]} ${w[0]}, ${w[1]}`).join('<br>')}</td></tr>`;
  fp.innerHTML = `<button style="float:right" id="fpx">✕</button><h3>${x.name}</h3><table>${rows}${inc}${wp}</table>`; fp.classList.remove('hidden');
  document.getElementById('fpx').onclick = () => fp.classList.add('hidden');
}
const ray = new THREE.Raycaster(), mouse = new THREE.Vector2(), tip = document.getElementById('mapTip');
function pick(e) { const b = canvas.getBoundingClientRect(); mouse.set(((e.clientX - b.left) / b.width) * 2 - 1, -((e.clientY - b.top) / b.height) * 2 + 1); ray.setFromCamera(mouse, cam); const h = ray.intersectObjects(objs.filter(o => o.visible)); return h[0]?.object.userData; }
canvas.addEventListener('pointermove', e => { const u = pick(e); if (u) { tip.style.display = 'block'; tip.style.left = e.offsetX + 12 + 'px'; tip.style.top = e.offsetY + 12 + 'px'; tip.textContent = `${u.name} · ${u.capacity?.value ?? ''}`; } else tip.style.display = 'none'; });
canvas.addEventListener('click', e => { const u = pick(e); if (u) open(u); });

// controls
document.querySelectorAll('#filters button').forEach(b => b.onclick = () => { show[b.dataset.c] = !show[b.dataset.c]; b.classList.toggle('on'); apply(); });
document.querySelectorAll('#speed button').forEach(b => b.onclick = () => { speed = +b.dataset.speed; document.querySelectorAll('#speed button').forEach(x => x.classList.toggle('on', x === b)); });
document.getElementById('l5off').onchange = e => { l5off = e.target.checked; kpis(); };
function apply() { for (const o of objs) o.visible = o.userData.kind === 'storage' || o.userData.kind === 'refinery' || o.userData.kind === 'cluster' ? show.fac : show[o.userData.commodity]; for (const f of flows) f.dots.forEach(d => d.s.visible = f.tube.visible); }

// KPIs: nameplate (sourced) capacities only; scenario simply removes Line 5's sourced 540,000 bbl/d
function kpis() {
  const into = id => D.lines.find(l => l.id === id).cap_num;
  const crude = (l5off ? 0 : into('line5')) + into('line78');
  const gas = ['vector', 'nexus', 'glgt'].reduce((a, id) => a + into(id), 0);
  document.getElementById('kpis').innerHTML =
    `<div><span>Crude/NGL capacity into Sarnia (L5 + L78B):</span><b class="${l5off ? 'bad' : ''}">${crude.toLocaleString()} bbl/d</b></div>` +
    `<div><span>Line 9 out of Sarnia:</span>${into('line9').toLocaleString()} bbl/d</div>` +
    `<div><span>US gas pipelines toward St. Clair/Dawn (Vector+NEXUS+GLGT nameplate):</span>${gas.toFixed(1)} Bcf/d</div>` +
    `<div><span>Dawn working gas:</span>189.5 PJ</div>` + (l5off ? `<div class="bad">LINE 5 SHUT: Straits segment + Line 5 flow stopped (illustrative, nameplate arithmetic only)</div>` : '');
}
kpis(); apply();

function resize() { const w = canvas.clientWidth, h = canvas.clientHeight; r.setSize(w, h, false); cam.aspect = w / h; cam.updateProjectionMatrix(); }
window.addEventListener('resize', resize); resize();
let last = performance.now();
function frame(now) {
  requestAnimationFrame(frame); const dt = Math.min(0.1, (now - last) / 1000) * speed; last = now;
  for (const f of flows) {
    const stopped = (l5off && DEP_L5.includes(f.ln.id)) || f.ln.kind === 'project' || /Replaced/.test(f.ln.status.value);
    f.tube.material.emissiveIntensity = stopped ? 0.02 : 0.25;
    for (const d of f.dots) { if (!stopped) d.t = (d.t + dt * f.v * 60 / f.len) % 1; d.s.visible = f.tube.visible && !stopped; d.s.position.copy(f.curve.getPointAt(d.t)); }
  }
  ctl.update(); r.render(scene, cam);
}
requestAnimationFrame(frame);
window.SWO = { D, scene, cam };
