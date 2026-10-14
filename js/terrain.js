/** Keyless high-detail terrain: AWS Terrain Tiles (Terrarium PNG, Mapzen/Tilezen, open data) decoded into a Cesium CustomHeightmapTerrainProvider. */
const C = window.Cesium;
export const TERRAIN_URL = 'https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x}/{y}.png';
const MAXZ = 15, N = 65, cache = new Map();
async function tile(z, x, y) {
  const k = `${z}/${x}/${y}`; if (cache.has(k)) return cache.get(k);
  const p = fetch(TERRAIN_URL.replace('{z}', z).replace('{x}', x).replace('{y}', y)).then(r => { if (!r.ok) throw new Error(r.status); return r.blob(); })
    .then(createImageBitmap).then(b => { const c = new OffscreenCanvas(256, 256), g = c.getContext('2d'); g.drawImage(b, 0, 0); return g.getImageData(0, 0, 256, 256).data; });
  cache.set(k, p); if (cache.size > 600) cache.delete(cache.keys().next().value); return p;
}
export function makeTerrain() {
  return new C.CustomHeightmapTerrainProvider({
    width: N, height: N, tilingScheme: new C.WebMercatorTilingScheme(), credit: 'Terrain: AWS Terrain Tiles (Mapzen/Tilezen; SRTM, USGS NED, GMTED, ETOPO1 et al.)',
    callback: async (x, y, level) => {
      const z = Math.min(level, MAXZ), d = level - z, s = 2 ** d;
      const tx = x >> d, ty = y >> d, ox = (x - tx * s) * 256 / s, oy = (y - ty * s) * 256 / s, span = 256 / s;
      let px; try { px = await tile(z, tx, ty); } catch { return new Float32Array(N * N); }
      const out = new Float32Array(N * N);
      for (let j = 0; j < N; j++) for (let i = 0; i < N; i++) {
        const u = Math.min(255, Math.round(ox + i / (N - 1) * span)), v = Math.min(255, Math.round(oy + j / (N - 1) * span)), o = (v * 256 + u) * 4;
        const h = px[o] * 256 + px[o + 1] + px[o + 2] / 256 - 32768; out[j * N + i] = Math.max(h, -50);
      }
      return out;
    },
  });
}
