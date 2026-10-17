/** SWO-PIPELINES v0.3.1: Cesium globe (vendored, keyless) with EIA/NACEI/OSM continental layers, researched SW Ontario detail, flow sim, and My home layer. */
import { makeTerrain } from './terrain.js';
const C = window.Cesium;
const COL = { crude: '#e04040', 'crude/NGL': '#ff8c1a', hgl: '#ff4fd8', products: '#2ecc71', gas: '#3fa7ff' };
const ST_COL = { pump: '#ff8c1a', compressor: '#3fa7ff', terminal: '#ffd700', meter: '#bbbbbb' };
const FAC_COL = { storage: '#c9a0ff', refinery: '#ffd700', cluster: '#ff69b4', terminal: '#ffa94d', refinery_decom: '#6e6e6e' };
const FAC_GRP = { terminal: 'depots', refinery_decom: 'decom' };
const J = u => fetch(u).then(r => { if (!r.ok) throw new Error(u + ' ' + r.status); return r.json(); });
const banner = document.getElementById('banner'), tip = document.getElementById('mapTip');
const esc = v => String(v ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const safeUrl = u => /^https?:\/\//.test(String(u)) ? esc(u) : '#';
const hav = (a, b) => { const r = Math.PI / 180, dl = (b[1] - a[1]) * r, dn = (b[0] - a[0]) * r, h = Math.sin(dl / 2) ** 2 + Math.cos(a[1] * r) * Math.cos(b[1] * r) * Math.sin(dn / 2) ** 2; return 12742 * Math.asin(Math.sqrt(h)); };
const COARSE_KM = 25; // straight runs longer than this are schematic (EIA liquids layer / approximate legs) -> drawn dashed

const imagery = new C.UrlTemplateImageryProvider({ url: 'https://services.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', maximumLevel: 19,
  credit: 'Powered by Esri — Source: Esri, Maxar, Earthstar Geographics, and the GIS User Community' });
const viewer = new C.Viewer('globe', { baseLayer: new C.ImageryLayer(imagery), terrainProvider: makeTerrain(), geocoder: false, baseLayerPicker: false, timeline: false, animation: false,
  homeButton: false, sceneModePicker: false, navigationHelpButton: false, infoBox: false, selectionIndicator: false, fullscreenButton: false, requestRenderMode: false });
viewer.scene.globe.depthTestAgainstTerrain = false; viewer.scene.globe.maximumScreenSpaceError = 1.5; viewer.scene.skyAtmosphere.show = true;
const VIEWS = { na: [-97, 30, 6.5e6, -80], swo: [-82.2, 38.9, 4.5e5, -45], sarnia: [-82.43, 42.70, 2.2e4, -40], mack: [-84.77, 45.55, 2.5e4, -35], lakeont: [-78.9, 41.0, 3.0e5, -45], mtl: [-73.56, 45.36, 3.5e4, -40], east: [-73.0, 36.3, 1.6e6, -70] };
const fly = (k, dur = 2) => { const v = VIEWS[k]; viewer.camera.flyTo({ destination: C.Cartesian3.fromDegrees(v[0], v[1], v[2]), orientation: { heading: 0, pitch: C.Math.toRadians(v[3]) }, duration: dur }); };
fly(VIEWS[(location.hash.match(/view=(\w+)/) || [])[1]] ? location.hash.match(/view=(\w+)/)[1] : 'swo', 0);

const groups = {}; const add = (g, o) => (groups[g] ||= []).push(o);
const searchIndex = [];
const host = s => { try { return new URL(s).hostname.replace('www.', ''); } catch { return String(s).slice(0, 40); } };
function srcLinks(arr) { return (arr || []).map(s => /^https?:/.test(s) ? `<a href="${safeUrl(s)}" target="_blank" rel="noopener">[${esc(host(s))}]</a>` : `[${esc(s)}]`).join(' '); }

// ---------- continental layers (EIA US, OSM Canada, OSM SW Ontario detail) ----------
const CONT = [['us_crude', 'crude'], ['us_hgl', 'hgl'], ['us_products', 'products'], ['us_natgas', 'gas'], ['osm_canada_pipelines', null], ['osm_swo_pipelines', null]];
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
        id: { kind: 'gis', layer: name, cls: c, props: p, src: d.source_url, lic: d.license, source: String(d.source || '').slice(0, 160) },
        attributes: { color: C.ColorGeometryInstanceAttribute.fromColor(C.Color.fromCssColorString(COL[c]).withAlpha(name.startsWith('osm_swo') ? 0.95 : 0.75)) } }));
    }
    const o = p.operator || p.Operator; if (o) ops.add(o);
  }
  for (const [c, inst] of Object.entries(per)) { const prim = viewer.scene.groundPrimitives.add(new C.GroundPolylinePrimitive({ geometryInstances: inst, appearance: new C.PolylineColorAppearance(), asynchronous: true })); add(c, prim); }
  ops.forEach(o => searchIndex.push({ label: `${o} (operator, ${name})`, type: 'op', op: o }));
}

// ---------- researched SW Ontario detail ----------
const D = await J('data/swo.json');
// Optional private home layer: data/private/home.json is gitignored and never published. Absent (or ?nohome) -> layer, view and KPI hidden.
// Only attempted when the page is opened from this machine (localhost), so public/LAN viewers never request it.
const LOCAL = ['localhost', '127.0.0.1', '[::1]'].includes(location.hostname);
const H = (/nohome/.test(location.search) || !LOCAL) ? null : await J('data/private/home.json').catch(() => null);
if (H?.location?.lat) VIEWS.home = [H.location.lon, H.location.lat - 0.0197, 1.8e3, -45];
else document.querySelectorAll('#views button[data-fly=home], #filters button[data-c=home]').forEach(b => b.remove());
const flows = [];
const pts = viewer.scene.primitives.add(new C.PointPrimitiveCollection());
const capMax = { 'bbl/d': 667000, 'Bcf/d': 2.4, 'PJ/d': 7.89 };
const posOf = w => C.Cartesian3.fromDegrees(w[1], w[0], 0);
function pin(id, lon, lat, color, text, payload, group, size = 12, outline = '#000') {
  const e = viewer.entities.add({ id, position: C.Cartesian3.fromDegrees(lon, lat), point: { pixelSize: size, color: C.Color.fromCssColorString(color), outlineColor: C.Color.fromCssColorString(outline), outlineWidth: outline === '#000' ? 1.5 : 3, heightReference: C.HeightReference.CLAMP_TO_GROUND, disableDepthTestDistance: Number.POSITIVE_INFINITY },
    label: { text, font: '12px system-ui', fillColor: C.Color.WHITE, outlineColor: C.Color.BLACK, outlineWidth: 3, style: C.LabelStyle.FILL_AND_OUTLINE, pixelOffset: new C.Cartesian2(10, -10), horizontalOrigin: C.HorizontalOrigin.LEFT, heightReference: C.HeightReference.CLAMP_TO_GROUND, disableDepthTestDistance: Number.POSITIVE_INFINITY, distanceDisplayCondition: new C.DistanceDisplayCondition(0, 6e5) } });
  e.swo = payload; add(group, e); searchIndex.push({ label: text.replace(/^⊘ /, ''), type: 'swo', x: payload.x, e }); return e;
}
const partsOf = ln => ln.geometry ? (ln.geometry.type === 'LineString' ? [ln.geometry.coordinates] : ln.geometry.coordinates) : (ln.waypoints?.length > 1 ? [ln.waypoints.map(w => [w[1], w[0]])] : []);
for (const ln of D.lines) {
  let color = ln.kind === 'project' ? C.Color.WHITE : C.Color.fromCssColorString(COL[ln.commodity]);
  const dia = typeof ln.diameter_in?.value === 'number' ? ln.diameter_in.value : 24;
  const lvl = ln.route_accuracy?.level || '';
  const approx = /approx|unknown/.test(lvl) || !!ln.connector, replaced = !!ln.replaced || /Replaced/.test(ln.status?.value || '');
  if (replaced) color = color.withAlpha(0.45);
  const noFlow = approx || replaced || ln.kind === 'project';
  // split each part into solid runs and coarse straight runs (> COARSE_KM), the latter drawn dashed
  const raw = partsOf(ln), parts = [], coarse = [];
  for (const pt of raw) { let cur = [pt[0]]; for (let i = 1; i < pt.length; i++) { if (!approx && hav(pt[i - 1], pt[i]) > COARSE_KM) { if (cur.length > 1) parts.push(cur); coarse.push([pt[i - 1], pt[i]]); cur = [pt[i]]; } else cur.push(pt[i]); } if (cur.length > 1) parts.push(cur); }
  let e0 = null;
  const all = raw.flat(), rect = all.length ? C.Rectangle.fromDegrees(Math.min(...all.map(q => q[0])) - 0.05, Math.min(...all.map(q => q[1])) - 0.05, Math.max(...all.map(q => q[0])) + 0.05, Math.max(...all.map(q => q[1])) + 0.05) : null;
  if (parts.length > 3) { // batch multi-part (EIA/OSM segment) lines into one primitive
    const prim = viewer.scene.groundPrimitives.add(new C.GroundPolylinePrimitive({ geometryInstances: parts.map(pt => new C.GeometryInstance({ geometry: new C.GroundPolylineGeometry({ positions: C.Cartesian3.fromDegreesArray(pt.flat()), width: replaced ? 2 : 4 }), id: { swo: { kind: 'line', x: ln } }, attributes: { color: C.ColorGeometryInstanceAttribute.fromColor(color) } })), appearance: new C.PolylineColorAppearance(), asynchronous: true }));
    add(ln.commodity, prim); searchIndex.push({ label: ln.name, type: 'swo', x: ln, rect, p: { kind: 'line', x: ln } });
  } else {
    parts.forEach((pt, i) => {
      const e = viewer.entities.add({ id: `L:${ln.id}:${i}`, polyline: { positions: C.Cartesian3.fromDegreesArray(pt.flat()), clampToGround: true, width: replaced ? 2 : ln.region === 'east' ? 4 : 3 + dia / 8,
        material: ln.connector ? new C.PolylineDashMaterialProperty({ color, gapColor: C.Color.WHITE.withAlpha(0.55), dashLength: 24 }) : ln.kind === 'project' || approx ? new C.PolylineDashMaterialProperty({ color, dashLength: 20 }) : new C.PolylineGlowMaterialProperty({ color, glowPower: 0.2 }) } });
      e.swo = { kind: 'line', x: ln }; add(ln.commodity, e); e0 ||= e;
    });
    if (!raw.length && ln.waypoints?.length) e0 = pin('L:' + ln.id, ln.waypoints[0][1], ln.waypoints[0][0], COL[ln.commodity], ln.name + ' (route unknown)', { kind: 'line', x: ln }, ln.commodity, 9);
    else if (e0) searchIndex.push({ label: ln.name, type: 'swo', x: ln, e: e0, rect });
  }
  coarse.forEach((pt, i) => { const e = viewer.entities.add({ id: `LC:${ln.id}:${i}`, polyline: { positions: C.Cartesian3.fromDegreesArray(pt.flat()), clampToGround: true, width: 3, material: new C.PolylineDashMaterialProperty({ color: color.withAlpha(0.8), dashLength: 14 }) } }); e.swo = { kind: 'line', x: ln }; add(ln.commodity, e); });
  if (approx && raw.length) raw.forEach(pt => [pt[0], pt[pt.length - 1]].forEach(q => { const e = viewer.entities.add({ position: C.Cartesian3.fromDegrees(q[0], q[1]), point: { pixelSize: 8, color, outlineColor: C.Color.BLACK, outlineWidth: 1.5, heightReference: C.HeightReference.CLAMP_TO_GROUND, disableDepthTestDistance: Number.POSITIVE_INFINITY } }); e.swo = { kind: 'line', x: ln }; add(ln.commodity, e); }));
  if (noFlow) continue; // no flow animation on approximate / endpoints-only / replaced / proposed lines
  // flow dots along the drawn geometry in coordinate order (= nominal source-described direction for researched SWO lines)
  for (const pt of parts.filter(q => q.length > 1)) {
    const P = pt.map(q => C.Cartesian3.fromDegrees(q[0], q[1], 0)), seg = []; let L = 0; for (let i = 1; i < P.length; i++) { const l = C.Cartesian3.distance(P[i - 1], P[i]); seg.push(l); L += l; }
    if (L < (ln.region === 'east' ? 80000 : 15000)) continue;
    const frac = ln.cap_num && capMax[ln.cap_unit] ? ln.cap_num / capMax[ln.cap_unit] : 0.15; const n = Math.min(60, Math.round((10 + 50 * frac) * Math.min(1, L / 4e5))) || 2, dots = [];
    for (let k = 0; k < n; k++) dots.push({ t: k / n, p: pts.add({ pixelSize: 4 + dia / 10, color: C.Color.WHITE, outlineColor: color, outlineWidth: 2, disableDepthTestDistance: Number.POSITIVE_INFINITY }) });
    flows.push({ ln, P, seg, L, dots, v: 18 + 60 * frac /* km/s visual, ∝ sourced capacity */ });
  }
}
function along(f, t) { let d = t * f.L; for (let i = 0; i < f.seg.length; i++) { if (d <= f.seg[i]) return C.Cartesian3.lerp(f.P[i], f.P[i + 1], d / f.seg[i], new C.Cartesian3()); d -= f.seg[i]; } return f.P[f.P.length - 1]; }
const lift = c => { const g = C.Cartographic.fromCartesian(c); return C.Cartesian3.fromRadians(g.longitude, g.latitude, 400); };

D.stations.forEach((s, i) => pin('S:' + i, s.lon, s.lat, ST_COL[s.type], `${s.name}`, { kind: 'station', x: s }, 'stations', 10));
D.facilities.forEach(f => pin('F:' + f.id, f.lon + ({ imperial: 0.012, chemvalley: 0.02 }[f.id] || 0), f.lat + ({ imperial: -0.01, chemvalley: 0.012 }[f.id] || 0), FAC_COL[f.kind], (f.kind === 'refinery_decom' ? '⊘ ' : '') + f.name, { kind: 'fac', x: f }, FAC_GRP[f.kind] || 'fac', f.kind === 'terminal' ? 9 : 13, f.kind === 'refinery_decom' ? '#ff3b3b' : '#000'));
D.crossings.forEach((c, i) => pin('X:' + i, c.lon, c.lat, '#00e5ff', `⨯ ${c.name}`, { kind: 'crossing', x: c }, 'crossings', 9));

// ---------- My home layer ----------
function homeLayer() {
  if (!H?.location?.lat) return;
  const L = H.location, path = (H.supply_path || []).filter(p => p.lat).map(p => [p.lon, p.lat]); path.push([L.lon, L.lat]);
  const e = viewer.entities.add({ id: 'HOME:path', polyline: { positions: C.Cartesian3.fromDegreesArray(path.flat()), clampToGround: true, width: 4, material: new C.PolylineDashMaterialProperty({ color: C.Color.fromCssColorString('#ffb020'), dashLength: 18 }) } });
  e.swo = { kind: 'home' }; add('home', e);
  pin('HOME:house', L.lon, L.lat, '#ffffff', '⌂ ' + (H.short_label || 'My home') + ' (OSM geocode)', { kind: 'home' }, 'home', 14);
  const g = H.supply_path?.[2]; if (g?.lat) pin('HOME:gate', g.lon, g.lat, '#ffb020', (g.label_short || 'Local gate station') + ' — APPROXIMATE/SCHEMATIC location', { kind: 'home' }, 'home', 10);
}
homeLayer();
function homePanel() {
  const P = document.getElementById('homePanel'); if (!H) { P.innerHTML = '<h3>My home</h3>No private home data (data/private/home.json) on this machine; layer disabled.'; P.classList.remove('hidden'); return; }
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
    rows = Object.entries(p.props).filter(([, v]) => v != null && v !== '').map(([k, v]) => `<tr><td>${esc(k)}</td><td>${/^https?:\/\//.test(String(v)) ? `<a href="${safeUrl(v)}" target="_blank" rel="noopener">${esc(v)}</a>` : esc(v)}</td></tr>`).join('') +
      `<tr><td>dataset</td><td>${esc(p.layer)}<br>${srcLinks([p.src])}<br><small>${esc(p.lic)}</small></td></tr><tr><td>note</td><td class="sch">Attributes are only what the open dataset carries; diameter/capacity/year/status not in this layer → unknown</td></tr>`;
    fp.innerHTML = `<button style="float:right" id="fpx">✕</button><h3>${esc(p.props.operator || p.props.Operator || p.props.name || p.props.typepipe || 'Pipeline segment')}</h3><table>${rows}</table>`;
  } else {
    const keys = p.kind === 'line' ? ['operator', 'product', 'diameter', 'capacity', 'length', 'route', 'endpoints', 'in_service', 'status'] : p.kind === 'fac' ? ['operator', 'operator_history', 'years', 'product', 'capacity', 'status', 'current_use'] : [];
    rows = keys.map(k => `<tr><td>${k.replace('_', ' ')}</td><td>${val(x[k] ?? (k === 'diameter' ? x.diameter_in : undefined))}</td></tr>`).join('') + (x.incidents || []).map(i => `<tr><td>incident</td><td>${val(i)}</td></tr>`).join('');
    if (p.kind === 'station' || p.kind === 'crossing') rows = Object.entries(x).filter(([k]) => !['sources', 'name'].includes(k)).map(([k, v]) => `<tr><td>${k}</td><td>${v ?? '<span class=unk>unknown</span>'}</td></tr>`).join('') + `<tr><td>sources</td><td>${srcLinks(x.sources)}</td></tr>`;
    if (x.route_accuracy) { const a = x.route_accuracy; rows += `<tr><td>route accuracy</td><td><b class="${/approx|unknown|not drawn|partial/.test(a.level) ? 'sch' : ''}">${esc(a.level)}</b>${a.matched_share != null ? ` · ${Math.round(a.matched_share * 100)}% of legs matched` : ''}${a.drawn_km != null && !x.connector ? `<br>drawn ${a.drawn_km} km${a.stated_km ? ` vs ${a.stated_km} km stated` : ''} · longest straight run ${a.longest_straight_km} km${a.straight_runs_over_25km_km ? ` · ${a.straight_runs_over_25km_km} km in straight runs > 25 km (dashed)` : ''}` : ''}${(a.issues || []).map(t => `<br><span class="sch">⚠ ${esc(t)}</span>`).join('')}<br><small>${esc(a.note)}${a.datasets ? '<br>datasets: ' + a.datasets.join(', ') : ''}</small><br>${srcLinks(a.sources)}</td></tr>`; }
    if (p.kind === 'fac') rows += `<tr><td>position</td><td class="${/approx/.test(x.pos_source) ? 'sch' : ''}">${String(x.pos_source).replace(/(https?:\/\/\S+)/, '<a href="$1" target="_blank">$1</a>')} (${x.lat.toFixed(4)}, ${x.lon.toFixed(4)})</td></tr>`;
    else if (x.waypoints?.length && !x.geometry) rows += `<tr><td>waypoints</td><td class="sch">approximate place coords:<br>${x.waypoints.map(w => `${w[2]} ${w[0]}, ${w[1]}`).join('<br>')}</td></tr>`;
    if (x.flow_note) rows += `<tr><td>flow</td><td>${x.flow_note}</td></tr>`;
    fp.innerHTML = `<button style="float:right" id="fpx">✕</button><h3>${x.name}</h3><table>${rows}</table>`;
  }
  fp.classList.remove('hidden'); document.getElementById('fpx').onclick = () => fp.classList.add('hidden');
}
const payloadOf = picked => picked?.id?.swo || picked?.id?.id?.swo || (picked?.id?.kind === 'gis' ? picked.id : null);
// drillPick so overlapping features resolve predictably: researched in-service lines/points > replaced lines > open-data segments
function pickAt(pos) { let best = null, bs = -1; for (const o of viewer.scene.drillPick(pos, 8)) { const p = payloadOf(o); if (!p) continue; const sc = p.kind === 'gis' ? 1 : p.kind === 'line' && p.x.replaced ? 2 : p.kind === 'line' ? 3 : 4; if (sc > bs) { best = p; bs = sc; } } return best; }
const handler = new C.ScreenSpaceEventHandler(viewer.scene.canvas);
handler.setInputAction(m => open(pickAt(m.position)), C.ScreenSpaceEventType.LEFT_CLICK);
handler.setInputAction(m => { const p = payloadOf(viewer.scene.pick(m.endPosition)); if (!p) { tip.style.display = 'none'; return; }
  tip.style.display = 'block'; tip.style.left = m.endPosition.x + 14 + 'px'; tip.style.top = m.endPosition.y + 96 + 'px';
  tip.textContent = p.kind === 'gis' ? `${p.props.operator || p.props.name || p.props.typepipe || ''} · ${p.cls} · ${p.layer}` : p.kind === 'home' ? 'My home (click for usage)' : `${p.x.name}${p.x.capacity ? ' · ' + (p.x.capacity.value ?? '') : ''}`; }, C.ScreenSpaceEventType.MOUSE_MOVE);

// ---------- controls ----------
function goTo(h) { if (!h) return; if (h.type === 'op') return openOp(h); if (h.rect && (h.p || h.x?.geometry)) viewer.camera.flyTo({ destination: h.rect, duration: 2 }); else if (h.e && h.e.position) viewer.flyTo(h.e, { duration: 2, offset: new C.HeadingPitchRange(0, -0.75, 9000) }); else if (h.rect) viewer.camera.flyTo({ destination: h.rect, duration: 2 }); open(h.p || h.e.swo); }
const show = {}; document.querySelectorAll('#filters button').forEach(b => { show[b.dataset.c] = true; b.onclick = () => { show[b.dataset.c] = !show[b.dataset.c]; b.classList.toggle('on'); apply(); }; });
function setFilter(c, on) { show[c] = on; document.querySelectorAll(`#filters button[data-c="${c}"]`).forEach(b => b.classList.toggle('on', on)); apply(); }
function apply() { for (const [g, arr] of Object.entries(groups)) for (const o of arr) o.show = show[g] !== false; for (const f of flows) { const vis = show[f.ln.commodity] !== false; f.dots.forEach(d => d.p.show = vis && !f.stopped); } }
let speed = 1; document.querySelectorAll('#speed button').forEach(b => b.onclick = () => { speed = +b.dataset.speed; document.querySelectorAll('#speed button').forEach(x => x.classList.toggle('on', x === b)); });
document.querySelectorAll('#views button').forEach(b => b.onclick = () => b.dataset.fly === 'home' ? (fly('home'), homePanel()) : fly(b.dataset.fly));
let l5off = false; document.getElementById('l5off').onchange = e => { l5off = e.target.checked; kpis(); };
const se = document.getElementById('search'), dl = document.getElementById('searchList');
function openOp(h) { fp.innerHTML = `<button style="float:right" id="fpx">✕</button><h3>${esc(h.op)}</h3>Operator named in the open GIS layers. Hover/click its segments on the map for attributes (the view is not moved: segments may be anywhere in North America).`; fp.classList.remove('hidden'); document.getElementById('fpx').onclick = () => fp.classList.add('hidden'); }
// ranked search: exact > prefix > whole-word > substring; researched features before operators
function findSearch(q) {
  q = String(q || '').trim().toLowerCase(); if (!q) return null;
  const words = q.split(/\s+/), rank = s => { const l = s.label.toLowerCase(); const r = l === q ? 0 : l.startsWith(q) && !/\w/.test(l[q.length] || '') ? 1 : words.every(w => new RegExp(`\\b${w.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\b`).test(l)) ? 2 : l.startsWith(q) ? 3 : l.includes(q) ? 4 : 9; return r * 2 + (s.type === 'op' ? 1 : 0); };
  let best = null, br = 99; for (const s of searchIndex) { const r = rank(s); if (r < br || (r === br && best && s.label.length < best.label.length)) { best = s; br = r; } } return br < 18 ? best : null;
}
const sMsg = document.getElementById('searchMsg');
se.onchange = () => { if (!se.value.trim()) { if (sMsg) sMsg.textContent = ''; return; } const h = findSearch(se.value); if (sMsg) sMsg.textContent = h ? '' : `No match for "${se.value}"`; if (h) goTo(h); };
function fillSearch() { const seen = new Set(); dl.innerHTML = searchIndex.filter(s => !seen.has(s.label) && seen.add(s.label)).map(s => `<option value="${esc(s.label)}">`).join(''); }

function kpis() {
  const cap = id => D.lines.find(l => l.id === id)?.cap_num || 0;
  const dawn = D.facilities.find(f => f.id === 'dawn'), dawnWg = (String(dawn?.capacity?.value || '').match(/([\d.,]+)\s*PJ working/) || [])[1];
  const crude = (l5off ? 0 : cap('line5')) + cap('line78');
  document.getElementById('kpis').innerHTML = `<div><span>Crude/NGL capacity into Sarnia (L5 + L78B):</span><b class="${l5off ? 'bad' : ''}">${crude.toLocaleString()} bbl/d</b></div>` +
    `<div><span>Line 9 out of Sarnia:</span>${cap('line9').toLocaleString()} bbl/d</div><div><span>Vector+NEXUS+GLGT nameplate:</span>${(() => { const b = ['vector', 'nexus', 'glgt'].reduce((a, i) => a + cap(i), 0); return `${b.toFixed(1)} Bcf/d (≈${(b * 28.3168).toFixed(0)} million m³/d)`; })()}</div>` +
    (dawnWg ? `<div><span>Dawn working gas (Enbridge storage report):</span>${dawnWg} PJ</div>` : '') + (H ? `<div><span>My home gas (derived):</span>${H.gas.derived_rate_m3_per_day} m³/d</div>` : '') + (l5off ? '<div class="bad">LINE 5 SHUT — flow stopped (nameplate arithmetic only)</div>' : '');
}
kpis();

// legend
const lg = document.getElementById('mapLegend'); let legendCollapsed = innerWidth < 700;
function legend() {
  lg.innerHTML = '<button id="lgToggle" title="Collapse/expand legend">Legend ▾</button><div id="lgBody"><b>Product (lines)</b>' + Object.entries(COL).map(([k, c]) => `<div><i style="background:${c}"></i>${k}</div>`).join('') +
    '<b>Researched lines (click)</b>' + D.lines.map(l => `<div data-s="${esc(l.name)}"><i ${/approx|unknown/.test(l.route_accuracy?.level || '') ? 'class="dash" ' : ''}style="${/approx|unknown/.test(l.route_accuracy?.level || '') ? 'color' : 'background'}:${l.kind === 'project' ? '#fff' : COL[l.commodity]}"></i>${esc(l.name)}${l.replaced ? ' (replaced)' : ''}</div>`).join('') +
    `<b>Points</b><div><i style="background:#ff8c1a"></i>pump</div><div><i style="background:#3fa7ff"></i>compressor / interconnect</div><div><i style="background:#bbb"></i>meter / unclassified pipeline facility (OSM)</div><div><i style="background:#ffd700"></i>refinery (active)</div><div><i style="background:#6e6e6e;outline:2px solid #ff3b3b"></i>⊘ decommissioned refinery</div><div><i style="background:#ffa94d"></i>fuel terminal / depot (OSM)</div><div><i style="background:#c9a0ff"></i>storage</div><div><i style="background:#00e5ff"></i>river/strait crossing (NACEI)</div>${H ? '<div><i style="background:#fff"></i>My home</div>' : ''}` +
    `<b>Line styles</b><div><i class="dash"></i>dashed = approximate route, endpoints only (route unknown), or a straight run &gt; 25 km in the source data (schematic)</div><div><i style="background:#888;opacity:.45"></i>faded thin = replaced line (Line 6B)</div><div>flow dots only on lines with sourced geometry; never on approximate/unknown routes</div>` +
    `<b>Datasets</b>${datasets.map(d => `<div>${esc(d.name)}: ${d.n.toLocaleString()} <a href="${safeUrl(d.src)}" target="_blank" rel="noopener">src</a></div>`).join('')}<small style="color:#8696a6">${D.lines.length} researched lines · ${D.stations.length} stations · ${D.facilities.length} facilities · ${D.crossings.length} crossings · ${D.sources.length} research sources</small></div>`;
  const body = lg.querySelector('#lgBody'), tg = lg.querySelector('#lgToggle'); if (legendCollapsed) body.style.display = 'none';
  tg.onclick = () => { legendCollapsed = !legendCollapsed; body.style.display = legendCollapsed ? 'none' : ''; tg.textContent = legendCollapsed ? 'Legend ▸' : 'Legend ▾'; };
  lg.querySelectorAll('div[data-s]').forEach(d => d.onclick = () => goTo(searchIndex.find(s => s.label === d.dataset.s)));
}
legend(); fillSearch();
banner.innerHTML = 'Loading continental GIS layers…';
await Promise.all(CONT.map(([n, c]) => loadCont(n, c)));
legend(); fillSearch(); apply();
banner.innerHTML = `Imagery: Esri World Imagery · Terrain: <a href="https://registry.opendata.aws/terrain-tiles/" target="_blank">AWS Terrain Tiles</a> · Pipelines: U.S. EIA (via DOE/NETL), NACEI (NRCan), © OpenStreetMap contributors (ODbL) · Researched lines: OSM/EIA operator-matched geometry where available, dashed = approximate, endpoints-only or schematic straight runs (see route accuracy in popups). Not surveyed. Unofficial. v0.3.1`;

// ---------- sim loop ----------
let last = performance.now();
viewer.scene.preRender.addEventListener(() => {
  const now = performance.now(), dt = Math.min(0.1, (now - last) / 1000) * speed; last = now;
  for (const f of flows) {
    f.stopped = (l5off && (f.ln.id === 'line5' || f.ln.id === 'line5_straits')) || f.ln.kind === 'project' || /Replaced/.test(f.ln.status?.value || '');
    const vis = show[f.ln.commodity] !== false && !f.stopped;
    for (const d of f.dots) { d.p.show = vis; if (!vis) continue; d.t = (d.t + dt * f.v * 1000 / f.L) % 1; d.p.position = lift(along(f, d.t)); }
  }
});
function onHash() { const m = location.hash.match(/view=(\w+)/); if (m && VIEWS[m[1]]) { fly(m[1]); if (m[1] === 'home') homePanel(); } const q = location.hash.match(/open=([^&]+)/); if (q) { const qq = decodeURIComponent(q[1]); goTo(searchIndex.find(s => s.label === qq) || findSearch(qq)); } const t = location.hash.match(/l5off=(\d)/); if (t) { const c = document.getElementById('l5off'); c.checked = t[1] === '1'; c.dispatchEvent(new Event('change')); } }
window.addEventListener('hashchange', onHash);
// deep links on first load (QA P1-4): view is applied at startup; open= and l5off= are applied once layers/search index exist
if (/open=|l5off=/.test(location.hash)) onHashInit(); else if (/view=home/.test(location.hash) && H) homePanel();
function onHashInit() { const q = location.hash.match(/open=([^&]+)/); if (q) { const t = decodeURIComponent(q[1]); goTo(searchIndex.find(s => s.label === t) || findSearch(t)); } const t = location.hash.match(/l5off=(\d)/); if (t) { const c = document.getElementById('l5off'); c.checked = t[1] === '1'; c.dispatchEvent(new Event('change')); } }
window.SWO = { goTo, viewer, D, H, groups, datasets, fly, open, show, apply, setFilter, searchIndex, findSearch, pickAt, flows, version: '0.3.1' };
function layout() { const h = document.getElementById('top').offsetHeight + document.getElementById('kpis').offsetHeight; document.querySelector('main').style.top = h + 'px'; fp.style.top = document.getElementById('homePanel').style.top = (h + 8) + 'px'; }
window.addEventListener('resize', layout); layout(); new ResizeObserver(layout).observe(document.getElementById('kpis'));

// ---------- #tour: scripted click-through of every quick view / toggle / popup (used for on-display QA screenshots) ----------
if (/tour/.test(location.hash)) {
  const btn = q => document.querySelector(q), click = q => btn(q)?.click(), closeFp = () => fp.classList.add('hidden'), closeHome = () => document.getElementById('homePanel').classList.add('hidden');
  const S = [['na', () => click('#views button[data-fly=na]')], ['swo', () => click('#views button[data-fly=swo]')], ['sarnia', () => click('#views button[data-fly=sarnia]')],
    ['mack', () => { click('#views button[data-fly=mack]'); goTo(searchIndex.find(s => s.label === 'Enbridge Line 5')); setTimeout(() => fly('mack'), 2500); }],
    ['l5off', () => { const c = btn('#l5off'); c.checked = true; c.dispatchEvent(new Event('change')); closeFp(); }],
    ['lakeont', () => { const c = btn('#l5off'); c.checked = false; c.dispatchEvent(new Event('change')); click('#views button[data-fly=lakeont]'); }],
    ['oakville-decom', () => { goTo(searchIndex.find(s => s.label.startsWith('Shell Oakville'))); }],
    ['mtl', () => { closeFp(); click('#views button[data-fly=mtl]'); }],
    ['mtl-popup', () => { open({ kind: 'line', x: D.lines.find(l => l.id === 'tnpi') }); }],
    ['east', () => { closeFp(); click('#views button[data-fly=east]'); }],
    ['east-gasonly', () => { ['crude', 'products', 'hgl', 'crude/NGL'].forEach(c => setFilter(c, false)); open({ kind: 'line', x: D.lines.find(l => l.id === 'iroquois') }); }],
    ...(H ? [['home', () => { closeFp(); click('#views button[data-fly=home]'); }]] : []),
    ['search', () => { closeHome(); Object.keys(show).forEach(c => setFilter(c, true)); se.value = 'Suncor Montreal'; se.onchange(); }],
    ['line7', () => { goTo(searchIndex.find(s => s.label.startsWith('Enbridge Line 7'))); }],
    ['end', () => { closeFp(); Object.keys(show).forEach(c => setFilter(c, true)); const c = btn('#l5off'); c.checked = false; c.dispatchEvent(new Event('change')); fly('swo'); }]];
  let i = 0; const step = () => { const [n, f] = S[i]; console.log('TOUR', n); document.title = 'TOUR ' + n; try { f(); } catch (e) { console.error('tour', n, e); document.title = 'TOUR ERR ' + n + ' ' + e.message; } if (++i < S.length) setTimeout(step, 20000); };
  setTimeout(step, 4000);
}
