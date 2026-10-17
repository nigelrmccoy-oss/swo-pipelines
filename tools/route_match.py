"""Replace schematic routes with real geometry: match open-GIS pipeline segments (OSM by operator/name, EIA by operator/pipename),
then chain them between ordered via-points with Dijkstra over the matched network. Unmatched legs fall back to approximate
land via-points. Writes data/routes.json: {line_id: {coords:[[lon,lat]...], multi:[...], accuracy, matched_share, datasets, sources, note}}."""
import json, re, math, heapq, collections
from shapely.geometry import LineString
from shapely.prepared import prep
from water_audit import LAKES
from shapely.ops import unary_union
WATER = prep(unary_union(list(LAKES.values())))
STRAITS = (-84.86, 45.74, -84.64, 45.89)  # sourced real crossing (Line 5 / GLGT at Straits of Mackinac)
def wet(a, b):
    """True if segment a-b crosses >3 km of Great Lakes open water outside the Straits of Mackinac."""
    s = LineString([a, b])
    if not WATER.intersects(s): return False
    if all(STRAITS[0] <= q[0] <= STRAITS[2] and STRAITS[1] <= q[1] <= STRAITS[3] for q in (a, b)): return False
    return s.intersection(unary_union(list(LAKES.values()))).length * 83 > 3.0
G = {n: json.load(open(f"data/gis/{n}.geojson")) for n in ["osm_swo_pipelines", "osm_canada_pipelines", "us_crude", "us_hgl", "us_products", "us_natgas"]}
SRC = {n: d["source_url"] + ("" if n.startswith("us_") else "") for n, d in G.items()}
def hav(a, b):
    R = 6371.0; la1, la2 = math.radians(a[1]), math.radians(b[1]); dl = math.radians(b[0] - a[0]); dp = la2 - la1
    return 2 * R * math.asin(math.sqrt(math.sin(dp / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin(dl / 2) ** 2))
def parts(g): return [g["coordinates"]] if g["type"] == "LineString" else g["coordinates"] if g["type"] == "MultiLineString" else []
def pick(rules):
    segs = []
    for layer, fn in rules:
        for f in G[layer]["features"]:
            if not f.get("geometry"): continue
            pr = dict(f["properties"] or {}); pr["_maxlon"] = max(q[0] for pp in parts(f["geometry"]) for q in pp) if parts(f["geometry"]) else 0
            if fn(pr):
                for p in parts(f["geometry"]):
                    if len(p) > 1: segs.append((layer, [tuple(map(float, q[:2])) for q in p], f["properties"]))
    return segs
MAX_EDGE_KM = 25.0  # OSM edges longer than this are bogus. EIA liquids layers are schematic (straight runs up to hundreds of km): allowed but reported as coarse in route_accuracy
def graph(segs, bridge_km=3.0, keep=None):
    adj = collections.defaultdict(list); key = lambda q: (round(q[0], 4), round(q[1], 4)); ends = []
    for layer, pts, _ in segs:
        for a, b in zip(pts, pts[1:]):
            d = hav(a, b)
            if (layer.startswith("osm") and d > MAX_EDGE_KM) or (d > 2 and wet(a, b)) or (keep and not keep(a, b)): continue
            adj[key(a)].append((key(b), d, layer)); adj[key(b)].append((key(a), d, layer))
        ends += [key(pts[0]), key(pts[-1])]
    nodes = list(adj); grid = collections.defaultdict(list)
    for n in nodes: grid[(int(n[0] * 20), int(n[1] * 20))].append(n)
    for e in set(ends):
        gx, gy = int(e[0] * 20), int(e[1] * 20)
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                for n in grid[(gx + dx, gy + dy)]:
                    if n != e:
                        d = hav(e, n)
                        if d < bridge_km: adj[e].append((n, d * 3 + 0.05, "bridge")); adj[n].append((e, d * 3 + 0.05, "bridge"))
    return adj, grid
def nearest(grid, p, maxkm):
    best = None
    for dx in range(-6, 7):
        for dy in range(-6, 7):
            for n in grid.get((int(p[0] * 20) + dx, int(p[1] * 20) + dy), []):
                d = hav(p, n)
                if d < maxkm and (best is None or d < best[0]): best = (d, n)
    return best[1] if best else None
def seg_dist_km(p, a, b):
    """Approximate distance (km) from point p to segment a-b (equirectangular, fine at leg scale)."""
    k = math.cos(math.radians((a[1] + b[1]) / 2)); ax, ay, bx, by, px, py = a[0] * k, a[1], b[0] * k, b[1], p[0] * k, p[1]
    dx, dy = bx - ax, by - ay; L = dx * dx + dy * dy; t = 0 if L == 0 else max(0, min(1, ((px - ax) * dx + (py - ay) * dy) / L))
    return math.hypot(px - (ax + t * dx), py - (ay + t * dy)) * 111.2
def dijkstra(adj, s, t, goal=None, snap_km=25, corridor=None):
    dist = {s: 0}; prev = {}; pq = [(0, s)]
    while pq:
        d, u = heapq.heappop(pq)
        if u == t: break
        if d > dist[u]: continue
        for v, w, lay in adj[u]:
            if corridor and seg_dist_km(v, corridor[0], corridor[1]) > corridor[2]: continue  # v0.3.1: stay near the leg
            nd = d + w
            if nd < dist.get(v, 1e18): dist[v] = nd; prev[v] = (u, lay); heapq.heappush(pq, (nd, v))
    if t not in dist:
        # target snapped onto a disconnected piece: use the reachable node nearest the via-point instead
        if goal is None: return None
        cand = [(hav(n, goal), n) for n in dist if hav(n, goal) < snap_km]
        if not cand: return None
        t = min(cand)[1]
    path, layers = [t], []; u = t
    while u != s: u, lay = prev[u]; path.append(u); layers.append(lay)
    return path[::-1], layers[::-1]
def route(vias, rules, snap_km=20, bridge_km=3.0, keep=None):
    segs = pick(rules); adj, grid = graph(segs, bridge_km, keep) if segs else ({}, {})
    coords, km_match, km_total, used, legs = [], 0.0, 0.0, set(), []
    for a, b in zip(vias, vias[1:]):
        sa, sb = (nearest(grid, a, snap_km), nearest(grid, b, snap_km)) if segs else (None, None)
        chord = hav(a, b); corr = (a, b, max(12.0, 0.35 * chord))
        r = dijkstra(adj, sa, sb, goal=b, snap_km=snap_km, corridor=corr) if sa and sb and sa != sb else None
        if r:  # v0.3.1 guards: reject detours (path >> chord) and paths ending far from the via-point
            plen = sum(hav(x, y) for x, y in zip(r[0], r[0][1:])) + hav(a, r[0][0]) + hav(r[0][-1], b)
            if plen > 1.8 * chord + 15 or hav(r[0][-1], b) > snap_km: print(f"  rejected leg {a}->{b}: path {plen:.0f} km vs chord {chord:.0f} km"); r = None
        if r:
            p, lays = r; leg = [a] + list(p) + [b]
            for (x, y), lay in zip(zip(p, p[1:]), lays):
                d = hav(x, y); km_total += d
                if lay != "bridge": km_match += d; used.add(lay)
            km_total += hav(a, p[0]) + hav(p[-1], b); legs.append("matched")
        else:
            leg = [a, b]
            if wet(a, b): print("  WARNING approximate leg crosses water", a, b)
            km_total += hav(a, b); legs.append("approximate")
        coords += leg if not coords else leg[1:]
    share = km_match / km_total if km_total else 0
    return dict(coords=[[round(x, 5), round(y, 5)] for x, y in coords], matched_share=round(share, 3), datasets=sorted(used), legs=legs, n_segments=len(segs))
def multi(rules):
    segs = pick(rules); return dict(multi=[[[round(x, 5), round(y, 5)] for x, y in p] for _, p, _ in segs], datasets=sorted({l for l, _, _ in segs}), n_segments=len(segs))
