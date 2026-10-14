/** SWO-PIPELINES v0.2: Cesium globe (vendored, keyless) with EIA/NACEI/OSM continental layers, researched SW Ontario detail, flow sim, and My home layer. */
import { makeTerrain } from './terrain.js';
const C = window.Cesium;
const COL = { crude: '#e04040', 'crude/NGL': '#ff8c1a', hgl: '#ff4fd8', products: '#2ecc71', gas: '#3fa7ff' };
const ST_COL = { pump: '#ff8c1a', compressor: '#3fa7ff', terminal: '#ffd700' };
const FAC_COL = { storage: '#c9a0ff', refinery: '#ffd700', cluster: '#ff69b4' };
const J = u => fetch(u).then(r => { if (!r.ok) throw new Error(u + ' ' + r.status); return r.json(); });
const banner = document.getElementById('banner'), tip = document.getElementById('mapTip');

const imagery = new C.UrlTemplateImageryProvider({ url: 'https://services.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', maximumLevel: 19,
  credit: 'Powered by Esri — Source: Esri, Maxar, Earthstar Geographics, and the GIS User Community' });
const viewer = new C.Viewer('globe', { baseLayer: new C.ImageryLayer(imagery), terrainProvider: makeTerrain(), geocoder: false, baseLayerPicker: false, timeline: false, animation: false,
  homeButton: false, sceneModePicker: false, navigationHelpButton: false, infoBox: false, selectionIndicator: false, fullscreenButton: false, requestRenderMode: false });
viewer.scene.globe.depthTestAgainstTerrain = false; viewer.scene.globe.maximumScreenSpaceError = 1.5; viewer.scene.skyAtmosphere.show = true;
const VIEWS = { na: [-97, 30, 6.5e6, -80], swo: [-82.2, 38.9, 4.5e5, -45], sarnia: [-82.43, 42.70, 2.2e4, -40], mack: [-84.77, 45.55, 2.5e4, -35] };
const fly = (k, dur = 2) => { const v = VIEWS[k]; viewer.camera.flyTo({ destination: C.Cartesian3.fromDegrees(v[0], v[1], v[2]), orientation: { heading: 0, pitch: C.Math.toRadians(v[3]) }, duration: dur }); };
fly('swo', 0);

const groups = {}; const add = (g, o) => (groups[g] ||= []).push(o);
const searchIndex = [];
function srcLinks(arr) { return (arr || []).map(s => `<a href="${s}" target="_blank">[${new URL(s).hostname.replace('www.', '')}]</a>`).join(' '); }

// ---------- continental layers (EIA US, OSM Canada/Mexico, OSM SW Ontario detail) ----------
const CONT = [['us_crude', 'crude'], ['us_hgl', 'hgl'], ['us_products', 'products'], ['us_natgas', 'gas'], ['osm_canada_pipelines', null], ['osm_mexico_pipelines', null], ['osm_swo_pipelines', null]];
const osmClass = s => /gas/.test(s || '') && !/lpg/.test(s) ? 'gas' : /crude|oil/.test(s || '') ? 'crude' : /ngl|lpg|propane|butane|ethylene/.test(s || '') ? 'hgl' : /fuel|petroleum/.test(s || '') ? 'products' : 'gas';
const datasets = [];
async function loadCont(name, cls) {
  let d; try { d = await J(`data/gis/${name}.geojson`); } catch { return; }
  datasets.push({ name, n: d.features.length, src: d.source_url, lic: d.license });
  const per = {}; const ops = new Set();
  for (const f of d.features) {
    const g = f.geometry; if (!g) continue; const p = f.properties || {};
    const c = cls || osmClass(p.substance); const parts = g.type === 'LineString' ? [g.coordinates] : g.type === 'MultiLineString' ? g.coordinates : [];
    for (const ln of parts) {
      if (ln.length < 2) continue;
      const flat = ln.flatMap(q => [q[0], q[1]]);
      (per[c] ||= []).push(new C.GeometryInstance({ geometry: new C.GroundPolylineGeometry({ positions: C.Cartesian3.fromDegreesArray(flat), width: name.startsWith('osm_swo') ? 3 : 2 }),
        id: { kind: 'gis', layer: name, cls: c, props: p, src: d.source_url, lic: d.license, source: d.source.slice(0, 160) },
        attributes: { color: C.ColorGeometryInstanceAttribute.fromColor(C.Color.fromCssColorString(COL[c]).withAlpha(name.startsWith('osm_swo') ? 0.95 : 0.75)) } }));
    }
    const o = p.operator || p.Operator; if (o) ops.add(o);
  }
  for (const [c, inst] of Object.entries(per)) { const prim = viewer.scene.groundPrimitives.add(new C.GroundPolylinePrimitive({ geometryInstances: inst, appearance: new C.PolylineColorAppearance(), asynchronous: true })); add(c, prim); }
  ops.forEach(o => searchIndex.push({ label: `${o} (operator, ${name})`, type: 'op', op: o }));
}

// ---------- researched SW Ontario detail ----------
const D = await J('data/swo.json');
const H = await J('data/home.json').catch(() => null);
const flows = [];
const pts = viewer.scene.primitives.add(new C.PointPrimitiveCollection());
const capMax = { 'bbl/d': 667000, 'Bcf/d': 2.4, 'PJ/d': 7.89 };
const posOf = w => C.Cartesian3.fromDegrees(w[1], w[0], 0);
for (const ln of D.lines) {
  const color = ln.kind === 'project' ? C.Color.WHITE : C.Color.fromCssColorString(COL[ln.commodity]);
  const dia = typeof ln.diameter_in.value === 'number' ? ln.diameter_in.value : 24;
  const e = viewer.entities.add({ id: 'L:' + ln.id, polyline: { positions: ln.waypoints.map(posOf), clampToGround: true, width: 4 + dia / 6,
    material: ln.kind === 'project' ? new C.PolylineDashMaterialProperty({ color, dashLength: 24 }) : new C.PolylineGlowMaterialProperty({ color, glowPower: 0.25 }) } });
  e.swo = { kind: 'line', x: ln }; add(ln.commodity, e);
  searchIndex.push({ label: ln.name, type: 'swo', x: ln, e });
  // flow dots along the schematic route in waypoint order (= nominal source-described direction)
  const P = ln.waypoints.map(posOf), seg = []; let L = 0; for (let i = 1; i < P.length; i++) { const l = C.Cartesian3.distance(P[i - 1], P[i]); seg.push(l); L += l; }
  const frac = ln.cap_num && capMax[ln.cap_unit] ? ln.cap_num / capMax[ln.cap_unit] : 0.15; const n = Math.round(10 + 50 * frac), dots = [];
  for (let k = 0; k < n; k++) dots.push({ t: k / n, p: pts.add({ pixelSize: 4 + dia / 10, color: C.Color.WHITE, outlineColor: color, outlineWidth: 2, disableDepthTestDistance: Number.POSITIVE_INFINITY }) });
  flows.push({ ln, P, seg, L, dots, v: 18 + 60 * frac /* km/s visual, ∝ sourced capacity */ });
}
function along(f, t) { let d = t * f.L; for (let i = 0; i < f.seg.length; i++) { if (d <= f.seg[i]) return C.Cartesian3.lerp(f.P[i], f.P[i + 1], d / f.seg[i], new C.Cartesian3()); d -= f.seg[i]; } return f.P[f.P.length - 1]; }
const lift = c => { const g = C.Cartographic.fromCartesian(c); return C.Cartesian3.fromRadians(g.longitude, g.latitude, 400); };

const pin = (id, lon, lat, color, text, payload, group, size = 12) => {
  const e = viewer.entities.add({ id, position: C.Cartesian3.fromDegrees(lon, lat), point: { pixelSize: size, color: C.Color.fromCssColorString(color), outlineColor: C.Color.BLACK, outlineWidth: 1.5, heightReference: C.HeightReference.CLAMP_TO_GROUND, disableDepthTestDistance: Number.POSITIVE_INFINITY },
    label: { text, font: '12px system-ui', fillColor: C.Color.WHITE, outlineColor: C.Color.BLACK, outlineWidth: 3, style: C.LabelStyle.FILL_AND_OUTLINE, pixelOffset: new C.Cartesian2(10, -10), horizontalOrigin: C.HorizontalOrigin.LEFT, heightReference: C.HeightReference.CLAMP_TO_GROUND, disableDepthTestDistance: Number.POSITIVE_INFINITY, distanceDisplayCondition: new C.DistanceDisplayCondition(0, 6e5) } });
  e.swo = payload; add(group, e); searchIndex.push({ label: text, type: 'swo', x: payload.x, e }); return e;
};
D.stations.forEach((s, i) => pin('S:' + i, s.lon, s.lat, ST_COL[s.type], `${s.name}`, { kind: 'station', x: s }, 'stations', 10));
D.facilities.forEach(f => pin('F:' + f.id, f.waypoints[0][1] + ({ imperial: 0.012, suncor: -0.012, chemvalley: 0.02 }[f.id] || 0), f.waypoints[0][0] + ({ imperial: -0.01, chemvalley: 0.012 }[f.id] || 0), FAC_COL[f.kind], f.name, { kind: 'fac', x: f }, 'fac', 14));
D.crossings.forEach((c, i) => pin('X:' + i, c.lon, c.lat, '#00e5ff', `⨯ ${c.name}`, { kind: 'crossing', x: c }, 'crossings', 9));

// ---------- My home layer ----------
function homeLayer() {
  if (!H?.location?.lat) return;
  const L = H.location, path = H.supply_path.filter(p => p.lat).map(p => [p.lon, p.lat]); path.push([L.lon, L.lat]);
  const e = viewer.entities.add({ id: 'HOME:path', polyline: { positions: C.Cartesian3.fromDegreesArray(path.flat()), clampToGround: true, width: 4, material: new C.PolylineDashMaterialProperty({ color: C.Color.fromCssColorString('#ffb020'), dashLength: 18 }) } });
  e.swo = { kind: 'home' }; add('home', e);
  pin('HOME:house', L.lon, L.lat, '#ffffff', '⌂ [private address] (OSM geocode)', { kind: 'home' }, 'home', 14);
  const g = H.supply_path[2]; pin('HOME:gate', g.lon, g.lat, '#ffb020', 'Kitchener gate station — APPROXIMATE/SCHEMATIC location', { kind: 'home' }, 'home', 10);
}
homeLayer();
function homePanel() {
  const P = document.getElementById('homePanel'); if (!H) { P.innerHTML = '<h3>My home</h3>data/home.json not found.'; return; }
  const g = H.gas, w = H.water, el = H.electricity;
  P.innerHTML = `<button style="float:right" onclick="this.parentNode.classList.add('hidden')">✕</button><h3>${H.name}</h3>
  <div>Location: ${H.location.lat.toFixed(5)}, ${H.location.lon.toFixed(5)} · ${H.location.source} ${srcLinks([H.location.source_url])}</div>
  <div>Gas utility: ${H.utility.gas} ${srcLinks(H.utility.sources)}</div><div style="color:#8696a6">${H.utility.supply_note} ${srcLinks(H.utility.supply_sources)}</div>
  <h4>Supply path</h4><ol>${H.supply_path.map(s => `<li>${s.step} <span class="sch">(${s.label})</span></li>`).join('')}</ol>
  <h4>Gas — meter ${g.meter} (${g.appliance})</h4><table class="t">${g.readings.map(r => `<tr><td>${r.t.replace('T', ' ')}</td><td>${r.m3} m³</td><td>${r.note}</td></tr>`).join('')}</table>
  <div>Derived from readings: <b>${g.derived_rate_m3_per_day} m³/day</b> <span class="sch">${g.derived_note}</span></div><div>${g.user_stated_rate || ''}</div>
  <div class="est">Annual: ~${g.annual_estimate_m3.value} m³/yr — ${g.annual_estimate_m3.label}</div><div>Bills: ${g.bills ?? g.bills_note}</div>
  <h4>Water</h4><table class="t">${w.readings.map(r => `<tr><td>${r.date}</td><td>${r.m3} m³</td></tr>`).join('')}</table><div>Derived: ${w.derived_m3_per_day} m³/day</div>
  <h4>Electricity (${H.utility.electricity})</h4><div class="sch">${el.label}</div><table class="t"><tr><td>date</td>${Object.keys(el.plugs).map(k => `<td>${k}</td>`).join('')}</tr>
  ${[...new Set(Object.values(el.plugs).flat().map(r => r.date))].sort().map(dt => `<tr><td>${dt}</td>${Object.values(el.plugs).map(a => `<td>${a.find(r => r.date === dt)?.kwh ?? '—'} kWh</td>`).join('')}</tr>`).join('')}</table>
  <div style="color:#8696a6">Last daily counter value logged per plug per day (today_kwh); first/last days are partial.</div>`;
  P.classList.remove('hidden');
}

// ---------- faceplate ----------
const fp = document.getElementById('faceplate');
const val = f => { if (f == null) return '<span class="unk">unknown</span>'; if (typeof f !== 'object' || !('value' in f)) return String(f); const v = Array.isArray(f.value) ? f.value.join(' → ') : f.value; return `${v === 'unknown' ? '<span class="unk">unknown</span>' : v}<br>${srcLinks(f.sources)}`; };
function open(p) {
  if (!p) return; if (p.kind === 'home') return homePanel();
  const x = p.x; let rows = '';
  if (p.kind === 'gis') {
    rows = Object.entries(p.props).filter(([, v]) => v != null && v !== '').map(([k, v]) => `<tr><td>${k}</td><td>${String(v).startsWith('http') ? `<a href="${v}" target="_blank">${v}</a>` : v}</td></tr>`).join('') +
      `<tr><td>dataset</td><td>${p.layer}<br>${srcLinks([p.src])}<br><small>${p.lic || ''}</small></td></tr><tr><td>note</td><td class="sch">Attributes are only what the open dataset carries; diameter/capacity/year/status not in this layer → unknown</td></tr>`;
    fp.innerHTML = `<button style="float:right" id="fpx">✕</button><h3>${p.props.operator || p.props.Operator || p.props.name || p.props.typepipe || 'Pipeline segment'}</h3><table>${rows}</table>`;
  } else {
    const keys = p.kind === 'line' ? ['operator', 'product', 'diameter_in', 'capacity', 'length', 'route', 'endpoints', 'in_service', 'status'] : p.kind === 'fac' ? ['operator', 'product', 'capacity', 'status'] : [];
    rows = keys.map(k => `<tr><td>${k.replace('_in', ' (in)').replace('_', ' ')}</td><td>${val(x[k])}</td></tr>`).join('') + (x.incidents || []).map(i => `<tr><td>incident</td><td>${val(i)}</td></tr>`).join('');
    if (p.kind === 'station' || p.kind === 'crossing') rows = Object.entries(x).filter(([k]) => !['sources', 'name'].includes(k)).map(([k, v]) => `<tr><td>${k}</td><td>${v ?? '<span class=unk>unknown</span>'}</td></tr>`).join('') + `<tr><td>sources</td><td>${srcLinks(x.sources)}</td></tr>`;
    if (x.waypoints) rows += `<tr><td>waypoints</td><td class="sch">schematic, approx. place coords:<br>${x.waypoints.map(w => `${w[2]} ${w[0]}, ${w[1]}`).join('<br>')}</td></tr>`;
    if (x.flow_note) rows += `<tr><td>flow</td><td>${x.flow_note}</td></tr>`;
    fp.innerHTML = `<button style="float:right" id="fpx">✕</button><h3>${x.name}</h3><table>${rows}</table>`;
  }
  fp.classList.remove('hidden'); document.getElementById('fpx').onclick = () => fp.classList.add('hidden');
}
const payloadOf = picked => picked?.id?.swo || (picked?.id?.kind === 'gis' ? picked.id : null);
const handler = new C.ScreenSpaceEventHandler(viewer.scene.canvas);
handler.setInputAction(m => open(payloadOf(viewer.scene.pick(m.position))), C.ScreenSpaceEventType.LEFT_CLICK);
handler.setInputAction(m => { const p = payloadOf(viewer.scene.pick(m.endPosition)); if (!p) { tip.style.display = 'none'; return; }
  tip.style.display = 'block'; tip.style.left = m.endPosition.x + 14 + 'px'; tip.style.top = m.endPosition.y + 96 + 'px';
  tip.textContent = p.kind === 'gis' ? `${p.props.operator || p.props.name || p.props.typepipe || ''} · ${p.cls} · ${p.layer}` : p.kind === 'home' ? 'My home (click for usage)' : `${p.x.name}${p.x.capacity ? ' · ' + (p.x.capacity.value ?? '') : ''}`; }, C.ScreenSpaceEventType.MOUSE_MOVE);

// ---------- controls ----------
const show = {}; document.querySelectorAll('#filters button').forEach(b => { show[b.dataset.c] = true; b.onclick = () => { show[b.dataset.c] = !show[b.dataset.c]; b.classList.toggle('on'); apply(); }; });
function apply() { for (const [g, arr] of Object.entries(groups)) for (const o of arr) o.show = show[g] !== false; for (const f of flows) { const vis = show[f.ln.commodity] !== false; f.dots.forEach(d => d.p.show = vis && !f.stopped); } }
let speed = 1; document.querySelectorAll('#speed button').forEach(b => b.onclick = () => { speed = +b.dataset.speed; document.querySelectorAll('#speed button').forEach(x => x.classList.toggle('on', x === b)); });
document.querySelectorAll('#views button').forEach(b => b.onclick = () => b.dataset.fly === 'home' ? (fly('home'), homePanel()) : fly(b.dataset.fly));
let l5off = false; document.getElementById('l5off').onchange = e => { l5off = e.target.checked; kpis(); };
const se = document.getElementById('search'), dl = document.getElementById('searchList');
se.onchange = () => { const h = searchIndex.find(s => s.label === se.value) || searchIndex.find(s => s.label.toLowerCase().includes(se.value.toLowerCase())); if (!h) return;
  if (h.type === 'swo') { viewer.flyTo(h.e, { duration: 2 }); open(h.e.swo); } else { show[Object.keys(COL).find(() => true)]; fp.innerHTML = `<button style="float:right" id="fpx">✕</button><h3>${h.op}</h3>Operator in open GIS layers. Hover/click its segments on the map for attributes.`; fp.classList.remove('hidden'); document.getElementById('fpx').onclick = () => fp.classList.add('hidden'); fly('na'); } };
function fillSearch() { const seen = new Set(); dl.innerHTML = searchIndex.filter(s => !seen.has(s.label) && seen.add(s.label)).map(s => `<option value="${s.label.replace(/"/g, '&quot;')}">`).join(''); }

function kpis() {
  const cap = id => D.lines.find(l => l.id === id).cap_num;
  const crude = (l5off ? 0 : cap('line5')) + cap('line78');
  document.getElementById('kpis').innerHTML = `<div><span>Crude/NGL capacity into Sarnia (L5 + L78B):</span><b class="${l5off ? 'bad' : ''}">${crude.toLocaleString()} bbl/d</b></div>` +
    `<div><span>Line 9 out of Sarnia:</span>${cap('line9').toLocaleString()} bbl/d</div><div><span>Vector+NEXUS+GLGT nameplate:</span>${['vector', 'nexus', 'glgt'].reduce((a, i) => a + cap(i), 0).toFixed(1)} Bcf/d</div>` +
    `<div><span>Dawn working gas:</span>189.5 PJ</div>` + (H ? `<div><span>My home gas (derived):</span>${H.gas.derived_rate_m3_per_day} m³/d</div>` : '') + (l5off ? '<div class="bad">LINE 5 SHUT — flow stopped (nameplate arithmetic only)</div>' : '');
}
kpis();

// legend
const lg = document.getElementById('mapLegend');
function legend() {
  lg.innerHTML = '<b>Product (lines)</b>' + Object.entries(COL).map(([k, c]) => `<div><i style="background:${c}"></i>${k}</div>`).join('') +
    '<b>Researched SW Ontario lines (click)</b>' + D.lines.map(l => `<div data-s="${l.name}"><i style="background:${l.kind === 'project' ? '#fff' : COL[l.commodity]}"></i>${l.name}</div>`).join('') +
    `<b>Points</b><div><i style="background:#ff8c1a"></i>pump</div><div><i style="background:#3fa7ff"></i>compressor / interconnect</div><div><i style="background:#ffd700"></i>terminal / refinery</div><div><i style="background:#c9a0ff"></i>storage</div><div><i style="background:#00e5ff"></i>river/strait crossing (NACEI)</div><div><i style="background:#fff"></i>My home</div>` +
    `<b>Datasets</b>${datasets.map(d => `<div>${d.name}: ${d.n.toLocaleString()} <a href="${d.src}" target="_blank">src</a></div>`).join('')}<small style="color:#8696a6">${D.lines.length} researched lines · ${D.stations.length} stations · ${D.crossings.length} crossings · ${D.sources.length} research sources</small>`;
  lg.querySelectorAll('div[data-s]').forEach(d => d.onclick = () => { const h = searchIndex.find(s => s.label === d.dataset.s); viewer.flyTo(h.e, { duration: 2 }); open(h.e.swo); });
}
legend(); fillSearch();
banner.innerHTML = 'Loading continental GIS layers…';
await Promise.all(CONT.map(([n, c]) => loadCont(n, c)));
legend(); fillSearch(); apply();
banner.innerHTML = `Imagery: Esri World Imagery · Terrain: <a href="https://registry.opendata.aws/terrain-tiles/" target="_blank">AWS Terrain Tiles</a> · Pipelines: U.S. EIA (via DOE/NETL), NACEI (NRCan), © OpenStreetMap contributors (ODbL) · Researched lines are schematic (place waypoints), not surveyed routes. Unofficial.`;

// ---------- sim loop ----------
let last = performance.now();
viewer.scene.preRender.addEventListener(() => {
  const now = performance.now(), dt = Math.min(0.1, (now - last) / 1000) * speed; last = now;
  for (const f of flows) {
    f.stopped = (l5off && (f.ln.id === 'line5' || f.ln.id === 'line5_straits')) || f.ln.kind === 'project' || /Replaced/.test(f.ln.status.value);
    const vis = show[f.ln.commodity] !== false && !f.stopped;
    for (const d of f.dots) { d.p.show = vis; if (!vis) continue; d.t = (d.t + dt * f.v * 1000 / f.L) % 1; d.p.position = lift(along(f, d.t)); }
  }
});
window.SWO = { viewer, D, H, groups, datasets };
function layout() { const h = document.getElementById('top').offsetHeight + document.getElementById('kpis').offsetHeight; document.querySelector('main').style.top = h + 'px'; fp.style.top = document.getElementById('homePanel').style.top = (h + 8) + 'px'; }
window.addEventListener('resize', layout); layout(); new ResizeObserver(layout).observe(document.getElementById('kpis'));
