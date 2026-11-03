/** v0.4 layers: large oil & gas terminals (data/terminals.json) and "Wells & field infrastructure" (data/wells/*.bin + data/field_infra.json).
 *  Wells are ~275k records, so they are lazy-loaded and drawn with view-dependent clustering: a grid-cell cluster per camera view when more than
 *  WELL_CAP wells fall in view, individual points otherwise. Rebuilt on camera moveEnd. */
export const TERM_COL = { crude: '#e04040', products: '#2ecc71', lng: '#7fe8ff', ngl: '#ff4fd8' };
export const TERM_NAME = { crude: 'Crude oil terminal / tank farm', products: 'Refined-product terminal', lng: 'LNG terminal', ngl: 'NGL / LPG terminal' };
export const WELL_T = [['Oil', '#ff4f9a'], ['Gas', '#7dff6b'], ['Oil + gas / condensate', '#ffe14d'], ['Storage (gas / LPG / cavern)', '#b78bff'], ['Injection / disposal / brine', '#ffffff'], ['Dry / test / observation / other', '#9aa7b3']];
export const WELL_S = ['Active / producing', 'Inactive (shut-in, suspended, capped)', 'Plugged / abandoned', 'Permitted / drilling', 'Orphan', 'Status unknown / not in source'];
const S_ALPHA = [1, 0.85, 0.5, 0.95, 0.9, 0.75];
export const WELL_CAP = 30000;
const fmt = n => Number(n).toLocaleString('en-CA');
export function createV04(ctx) {
  const { C, viewer, pin, esc, srcLinks, safeUrl, J, add, searchIndex } = ctx;
  const W = { man: null, regions: [], loading: null, on: false, tOn: WELL_T.map(() => true), sOn: [true, true, false, true, true, true], pts: null, cl: null, lab: null, timer: null, shown: { mode: 'none', n: 0, drawn: 0 }, field: null };
  let termList = [];
  const info = { terminals: 0, field_points: 0, field_lines: 0 };
  // ---------------- terminals ----------------
  async function loadTerminals() {
    let T; try { T = await J('data/terminals.json'); } catch { return null; }
    T.terminals.forEach(t => {
      const big = t.capacity?.bbl || t.est_volume_bbl || 0, size = Math.max(9, Math.min(19, 7 + 2.2 * Math.log10(Math.max(big, 1e4) / 1e4)));
      pin('T:' + t.id, t.lon, t.lat, TERM_COL[t.kind] || '#ccc', t.name, { kind: 'term', x: t }, 'terminals', size, '#ffffff');
    });
    termList = T.terminals; info.terminals = T.terminals.length; return T;
  }
  const bblTxt = (m3, bbl) => `${fmt(Math.round(m3))} m³ (${fmt(Math.round(bbl))} bbl)`;
  function termPopup(t) {
    const rows = []; const r = (k, v) => v != null && v !== '' && rows.push(`<tr><td>${k}</td><td>${v}</td></tr>`);
    r('type', `<b style="color:${TERM_COL[t.kind]}">${esc(TERM_NAME[t.kind] || t.kind)}</b>${t.hub ? ' · hub' : ''}`);
    r('operator', esc(t.operator || '') || '<span class="unk">unknown</span>');
    const c = t.capacity;
    if (c) r('capacity', `${c.basis === 'ESTIMATE' ? '<span class="est"><b>ESTIMATE</b></span> ' : '<b>sourced</b> '}${esc(c.text)}${c.as_of ? ` <small>(as of ${esc(c.as_of)})</small>` : ''}${c.note ? `<br><small>${esc(c.note)}</small>` : ''}<br>${srcLinks(c.sources)}`);
    if (t.est_volume_m3) r('tank-farm size', `<span class="est"><b>ESTIMATE</b></span> ≈ ${bblTxt(t.est_volume_m3, t.est_volume_bbl)} shell volume from ${t.tanks} mapped tanks (${fmt(t.area_m2)} m² footprint × ${t.n_height_tagged ? 'tagged height where given, else ' : ''}12 m assumed height; OSM footprints only: missing/small tanks are not counted)`);
    if (t.regas) r('send-out / liquefaction', esc(t.regas));
    (t.eia || []).slice(0, 4).forEach((e, i) => r(i ? '' : 'EIA-815 / EIA listing', `${esc(e.company)} — ${esc(e.site)}${e.city ? ', ' + esc(e.city) : ''} <small>(${esc(e.layer)}, ${esc(e.period || '')})</small>`));
    if ((t.eia || []).length > 4) r('', `+${t.eia.length - 4} more listed within 1.2 km`);
    r('region', esc(t.region || ''));
    r('position', `<span class="${/approx|place/.test(t.pos_source) ? 'sch' : ''}">${esc(t.pos_source)}</span> (${t.lat.toFixed(4)}, ${t.lon.toFixed(4)})`);
    if (t.note) r('note', `<span class="sch">${esc(t.note)}</span>`);
    r('sources', srcLinks(t.sources));
    return { title: esc(t.name), html: `<table>${rows.join('')}</table>` };
  }
  // ---------------- wells ----------------
  async function loadWells() {
    if (W.loading) return W.loading;
    W.loading = (async () => {
      W.man = await J('data/wells/wells.json');
      await Promise.all(W.man.regions.map(async (m, k) => {
        const buf = await fetch('data/wells/' + m.file).then(r => r.arrayBuffer());
        const reg = { m, n: buf.byteLength / 16, i32: new Int32Array(buf), u8: new Uint8Array(buf), u16: new Uint16Array(buf), tc: Uint8Array.from(m.types.map(t => t[1])), sc: Uint8Array.from(m.statuses.map(t => t[1])), names: null };
        if (m.names_file) J('data/wells/' + m.names_file).then(a => { reg.names = a; });
        W.regions[k] = reg;
      }));
      info.wells = W.regions.reduce((a, r) => a + r.n, 0);
    })();
    return W.loading;
  }
  function ensurePrims() {
    if (W.pts) return;
    W.pts = viewer.scene.primitives.add(new C.PointPrimitiveCollection()); W.cl = viewer.scene.primitives.add(new C.PointPrimitiveCollection()); W.lab = viewer.scene.primitives.add(new C.LabelCollection());
    viewer.camera.moveEnd.addEventListener(schedule); viewer.camera.percentageChanged = 0.1; viewer.camera.changed.addEventListener(schedule);
  }
  const colT = WELL_T.map(([, c]) => C.Color.fromCssColorString(c)), colS = S_ALPHA;
  function schedule() { if (!W.on) return; clearTimeout(W.timer); W.timer = setTimeout(rebuild, 120); }
  function viewBox() {
    const h = viewer.camera.positionCartographic.height; let r; try { r = h < 2.5e6 ? viewer.camera.computeViewRectangle(viewer.scene.globe.ellipsoid) : null; } catch { r = null; }
    const d = C.Math.toDegrees; if (!r) return [-180, -90, 180, 90];
    const pad = 0.1 * Math.max(r.east - r.west, r.north - r.south); return [d(r.west - pad), d(r.south - pad), d(r.east + pad), d(r.north + pad)];
  }
  function rebuild() {
    if (!W.on || !W.regions.length) return; ensurePrims(); const t0 = performance.now();
    W.pts.removeAll(); W.cl.removeAll(); W.lab.removeAll();
    const [w, s, e, n] = viewBox(); const sel = []; let N = 0;
    for (let k = 0; k < W.regions.length; k++) {
      const R = W.regions[k]; if (!R) continue; const { i32, u8, u16, tc, sc } = R;
      for (let i = 0; i < R.n; i++) {
        const lon = i32[4 * i] * 1e-5; if (lon < w || lon > e) continue; const lat = i32[4 * i + 1] * 1e-5; if (lat < s || lat > n) continue;
        const t = tc[u8[16 * i + 12]], st = sc[u8[16 * i + 13]]; if (!W.tOn[t] || !W.sOn[st]) continue;
        sel.push(k, i, t, st); N++;
      }
    }
    if (N <= WELL_CAP) {
      for (let q = 0; q < sel.length; q += 4) {
        const R = W.regions[sel[q]], i = sel[q + 1]; const c = colT[sel[q + 2]].withAlpha(colS[sel[q + 3]]);
        W.pts.add({ position: C.Cartesian3.fromDegrees(R.i32[4 * i] * 1e-5, R.i32[4 * i + 1] * 1e-5, 0), pixelSize: sel[q + 3] === 2 ? 4 : 6, color: c, outlineColor: C.Color.BLACK.withAlpha(0.6), outlineWidth: 1, disableDepthTestDistance: 5e4, id: { swo: { kind: 'well', r: sel[q], i } } });
      }
      W.shown = { mode: 'points', n: N, drawn: N };
    } else {
      let cell = 2; for (const c of [0.004, 0.008, 0.016, 0.03, 0.06, 0.12, 0.25, 0.5, 1, 2]) { const set = new Set(); for (let q = 0; q < sel.length; q += 4) { const R = W.regions[sel[q]], i = sel[q + 1]; set.add(Math.floor(R.i32[4 * i] * 1e-5 / c) * 100003 + Math.floor(R.i32[4 * i + 1] * 1e-5 / c)); if (set.size > 3500) break; } if (set.size <= 3500) { cell = c; break; } }
      const M = new Map();
      for (let q = 0; q < sel.length; q += 4) {
        const R = W.regions[sel[q]], i = sel[q + 1], lon = R.i32[4 * i] * 1e-5, lat = R.i32[4 * i + 1] * 1e-5, key = Math.floor(lon / cell) * 100003 + Math.floor(lat / cell);
        let g = M.get(key); if (!g) M.set(key, g = { n: 0, x: 0, y: 0, t: new Array(6).fill(0), s: new Array(6).fill(0), gx: Math.floor(lon / cell), gy: Math.floor(lat / cell) }); g.n++; g.x += lon; g.y += lat; g.t[sel[q + 2]]++; g.s[sel[q + 3]]++;
      }
      const arr = [...M.values()].sort((a, b) => b.n - a.n);
      arr.forEach((g, j) => {
        let best = 0; for (let t = 1; t < 6; t++) if (g.t[t] > g.t[best]) best = t;
        const sz = Math.min(30, 8 + 5 * Math.log10(g.n)), rect = C.Rectangle.fromDegrees(g.gx * cell, g.gy * cell, (g.gx + 1) * cell, (g.gy + 1) * cell);
        W.cl.add({ position: C.Cartesian3.fromDegrees(g.x / g.n, g.y / g.n, 0), pixelSize: sz, color: colT[best].withAlpha(0.8), outlineColor: C.Color.WHITE, outlineWidth: 1.5, disableDepthTestDistance: Number.POSITIVE_INFINITY, id: { swo: { kind: 'wellcluster', n: g.n, t: g.t, s: g.s, rect, cell } } });
        if (j < 250 && g.n >= 5) W.lab.add({ position: C.Cartesian3.fromDegrees(g.x / g.n, g.y / g.n, 0), text: g.n >= 1000 ? (g.n / 1000).toFixed(g.n >= 10000 ? 0 : 1) + 'k' : String(g.n), font: '11px system-ui', fillColor: C.Color.WHITE, outlineColor: C.Color.BLACK, outlineWidth: 3, style: C.LabelStyle.FILL_AND_OUTLINE, verticalOrigin: C.VerticalOrigin.CENTER, horizontalOrigin: C.HorizontalOrigin.CENTER, pixelOffset: new C.Cartesian2(0, 0), disableDepthTestDistance: Number.POSITIVE_INFINITY });
      });
      W.shown = { mode: 'clusters', n: N, drawn: arr.length, cell };
    }
    W.shown.ms = Math.round(performance.now() - t0); W.shown.total = info.wells;
    const el = document.getElementById('wellsInfo'); if (el) el.textContent = infoText();
  }
  const infoText = () => W.on && W.shown.mode !== 'none' ? `${fmt(W.shown.n)} wells in view (of ${fmt(info.wells)}) · ${W.shown.mode === 'points' ? 'individual points' : `${fmt(W.shown.drawn)} clusters (${W.shown.cell}° cells), zoom in to see wells`}` : 'off: toggle the “Wells & field” button';
  function wellPopup(p) {
    const R = W.regions[p.r], m = R.m, i = p.i, I = R.i32, ti = R.u8[16 * i + 12], si = R.u8[16 * i + 13], oi = R.u16[8 * i + 7];
    const typ = m.types[ti], st = m.statuses[si], lon = I[4 * i] * 1e-5, lat = I[4 * i + 1] * 1e-5, id = I[4 * i + 2] >>> 0, rows = []; const r = (k, v) => rows.push(`<tr><td>${k}</td><td>${v}</td></tr>`);
    const nm = R.names?.[i]; if (nm) r('name', esc(nm));
    r('type', `${esc(typ[0])} <small>(${esc(WELL_T[typ[1]][0])})</small>`); r('status', `${esc(st[0])} <small>(${esc(WELL_S[st[1]])})</small>`);
    if (m.operator_is_county) r('state / county', esc(m.operators[oi])); else r('operator', oi ? esc(m.operators[oi]) : '<span class="unk">not in public record</span>');
    r(esc(m.id_label || 'ID'), id || '<span class="unk">n/a</span>'); r('position', `${lat.toFixed(5)}, ${lon.toFixed(5)} <small>(surface-hole / mapped location as published; accuracy varies by record)</small>`);
    r('dataset', `${esc(m.source)}<br><small>${esc(m.license)} · retrieved ${esc(W.man.retrieved)}</small><br>${srcLinks([m.url, m.service])}`);
    return { title: esc(nm || `${typ[0]} ${id || ''}`), html: `<table>${rows.join('')}</table>` };
  }
  function clusterPopup(p) {
    const rows = WELL_T.map(([n, c], k) => p.t[k] ? `<tr><td><i style="display:inline-block;width:10px;height:10px;background:${c};border:1px solid #000"></i> ${n}</td><td>${fmt(p.t[k])}</td></tr>` : '').join('');
    const st = WELL_S.map((n, k) => p.s[k] ? `<tr><td>${n}</td><td>${fmt(p.s[k])}</td></tr>` : '').join('');
    return { title: `${fmt(p.n)} wells (cluster, ${p.cell}° cell)`, html: `<table>${rows}</table><br><table>${st}</table><p class="sch">Zooming in to the cluster…</p>` };
  }
  // ---------------- field infrastructure ----------------
  async function loadField() {
    if (W.field) return W.field; let F; try { F = await J('data/field_infra.json'); } catch { W.field = { points: [], lines: [] }; return W.field; }
    const LC = { processing: '#ffd166', compressor: '#3fa7ff', storage: '#b78bff', wellsite: '#ff4f9a', facility: '#bbbbbb' };
    F.points.forEach(f => pin('FI:' + f.id, f.lon, f.lat, LC[f.kind] || '#bbb', f.name, { kind: 'field', x: f }, 'wells', f.kind === 'processing' ? 10 : 7, '#000'));
    if (F.lines.length && C.GroundPolylinePrimitive.isSupported(viewer.scene)) {
      const col = C.ColorGeometryInstanceAttribute.fromColor(C.Color.fromCssColorString('#7fd1ff').withAlpha(0.8));
      W.lineP = viewer.scene.groundPrimitives.add(new C.GroundPolylinePrimitive({ asynchronous: true, appearance: new C.PolylineColorAppearance(),
        geometryInstances: F.lines.map(l => new C.GeometryInstance({ geometry: new C.GroundPolylineGeometry({ positions: C.Cartesian3.fromDegreesArray(l.pts.flat()), width: 2 }), attributes: { color: col } })) }));
    }
    W.field = F; info.field_points = F.points.length; info.field_lines = F.lines.length; return F;
  }
  function fieldPopup(f) {
    const rows = []; const r = (k, v) => v != null && v !== '' && rows.push(`<tr><td>${k}</td><td>${v}</td></tr>`);
    r('type', esc(f.type_label || f.kind)); r('operator / owner', esc(f.operator || '') || '<span class="unk">unknown</span>');
    if (f.capacity) r('capacity', `${esc(f.capacity)}${f.capacity_basis ? ` <small>(${esc(f.capacity_basis)})</small>` : ''}`);
    if (f.status) r('status', esc(f.status)); if (f.detail) r('detail', esc(f.detail));
    r('position', `${esc(f.pos_source)} (${f.lat.toFixed(4)}, ${f.lon.toFixed(4)})`); r('sources', srcLinks(f.sources));
    return { title: esc(f.name), html: `<table>${rows.join('')}</table>` };
  }
  return {
    info, loadTerminals, loadField, wells: W, rebuild, get terminals() { return termList; },
    popup(p) { return p.kind === 'term' ? termPopup(p.x) : p.kind === 'well' ? wellPopup(p) : p.kind === 'wellcluster' ? clusterPopup(p) : p.kind === 'field' ? fieldPopup(p.x) : null; },
    async sync(show) { const on = show.wells !== false; if (on === W.on) return; W.on = on; if (on) { await loadWells(); await loadField(); if (W.lineP) W.lineP.show = true; ensurePrims(); rebuild(); } else { if (W.lineP) W.lineP.show = false; W.pts?.removeAll(); W.cl?.removeAll(); W.lab?.removeAll(); } },
    setClass(kind, k, v) { (kind === 't' ? W.tOn : W.sOn)[k] = v; rebuild(); },
    state: () => ({ tOn: W.tOn.slice(), sOn: W.sOn.slice(), shown: W.shown, on: W.on }),
    rebuild,
    legend() {
      return `<b>Wells &amp; field infrastructure</b> <small id="wellsInfo" style="color:#8696a6">${esc(infoText())}</small>` +
        WELL_T.map(([n, c], k) => `<div data-wt="${k}"><i style="background:${c}"></i><label><input type="checkbox" ${W.tOn[k] ? 'checked' : ''}> ${n}</label></div>`).join('') +
        WELL_S.map((n, k) => `<div data-ws="${k}" style="padding-left:20px"><label><input type="checkbox" ${W.sOn[k] ? 'checked' : ''}> ${n}</label></div>`).join('') +
        `<div><i style="background:#ffd166"></i>gas processing plant (EIA-757)</div><div><i style="background:#3fa7ff"></i>compressor site</div><div><i style="background:#b78bff"></i>gas storage field / site</div>` +
        `<b>Large terminals</b>` + Object.entries(TERM_COL).map(([k, c]) => `<div><i style="background:${c};outline:2px solid #fff"></i>${TERM_NAME[k]}</div>`).join('');
    },
  };
}
