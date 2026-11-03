"""v0.4 terminals: raw downloads.
1) EIA/NETL OilGasInfrastructure FeatureServer layers 10 (refineries, used only to avoid double-listing), 11 (gas processing plants), 12/13 (gas + HGL hubs), 14 (EIA-815 petroleum product terminals),
   15 (LNG terminals), 20 (crude rail terminals) -> data/ref/eia_infra_raw.json
2) OSM man_made=storage_tank (+ tags) around every EIA anchor in the mapped states, in all-tank boxes for Canadian/hub areas, and fuel-tagged tanks in wide regional boxes
   -> data/ref/tanks_raw/*.json (gitignored) -> clustered (450 m single linkage) -> data/ref/osm_tank_clusters.json (committed)
Footprint area comes from the OSM way geometry; volume is an ESTIMATE (footprint x tag height, else 12 m assumed)."""
import json, math, os, sys, time, urllib.parse, urllib.request, datetime, hashlib
os.makedirs("data/ref/tanks_raw", exist_ok=True)
TODAY = datetime.date.today().isoformat(); UA = {"User-Agent": "swo-pipelines/0.4 (personal research)"}
EIA = "https://services7.arcgis.com/p4qwkH3IF5hxHqd7/ArcGIS/rest/services/OilGasInfrastructure/FeatureServer"
OVS = ["https://maps.mail.ru/osm/tools/overpass/api/interpreter", "https://overpass-api.de/api/interpreter", "https://overpass.private.coffee/api/interpreter"]
def jget(url, params):
    for k in range(5):
        try: return json.load(urllib.request.urlopen(urllib.request.Request(url + "?" + urllib.parse.urlencode(params), headers=UA), timeout=120))
        except Exception as e: print("retry", e, file=sys.stderr); time.sleep(4 * (k + 1))
    raise SystemExit("failed " + url)
def eia():
    out = {"retrieved": TODAY, "service": EIA, "license": "US Government public domain (EIA / NETL)", "layers": {}}
    for lay, nm in ((10, "Petroleum refineries"), (11, "Natural gas processing plants"), (12, "Natural gas market hubs"), (13, "HGL market hubs"), (14, "Petroleum product terminals"), (15, "LNG terminals"), (20, "Crude oil rail terminals")):
        rows = []; off = 0
        while True:
            d = jget(f"{EIA}/{lay}/query", {"where": "1=1", "outFields": "*", "outSR": 4326, "resultOffset": off, "resultRecordCount": 1000, "orderByFields": "OBJECTID" if lay in (10, 14) else "FID", "f": "json"})
            fs = d.get("features", [])
            if not fs: break
            for f in fs:
                a = dict(f["attributes"]); g = f.get("geometry") or {}
                a["_lon"], a["_lat"] = g.get("x"), g.get("y"); rows.append(a)
            off += len(fs)
        print("EIA layer", lay, nm, len(rows)); out["layers"][str(lay)] = {"name": nm, "url": f"{EIA}/{lay}", "rows": rows}
    json.dump(out, open("data/ref/eia_infra_raw.json", "w"))
    return out
STATES = {"NEW YORK", "NEW JERSEY", "PENNSYLVANIA", "CONNECTICUT", "RHODE ISLAND", "MASSACHUSETTS", "MAINE", "NEW HAMPSHIRE", "VERMONT", "DELAWARE", "MARYLAND", "VIRGINIA", "WEST VIRGINIA", "DISTRICT OF COLUMBIA",
          "OHIO", "INDIANA", "ILLINOIS", "MICHIGAN", "WISCONSIN", "MINNESOTA", "KENTUCKY", "MISSOURI", "IOWA", "OKLAHOMA", "TEXAS", "LOUISIANA", "MISSISSIPPI", "ALABAMA", "KANSAS"}
ABBR = {"NY": "NEW YORK", "NJ": "NEW JERSEY", "PA": "PENNSYLVANIA", "CT": "CONNECTICUT", "RI": "RHODE ISLAND", "MA": "MASSACHUSETTS", "ME": "MAINE", "NH": "NEW HAMPSHIRE", "VT": "VERMONT", "DE": "DELAWARE", "MD": "MARYLAND", "VA": "VIRGINIA", "WV": "WEST VIRGINIA", "DC": "DISTRICT OF COLUMBIA",
        "OH": "OHIO", "IN": "INDIANA", "IL": "ILLINOIS", "MI": "MICHIGAN", "WI": "WISCONSIN", "MN": "MINNESOTA", "KY": "KENTUCKY", "MO": "MISSOURI", "IA": "IOWA", "OK": "OKLAHOMA", "TX": "TEXAS", "LA": "LOUISIANA", "MS": "MISSISSIPPI", "AL": "ALABAMA", "KS": "KANSAS"}
def st(a): s = (a.get("State") or a.get("STATE") or a.get("state") or "").strip(); return ABBR.get(s.upper(), s.upper())
EXCL = "water|sewage|wastewater|silage|grain|milk|manure|slurry|fertili|wine|beer|biogas"
FUEL = "oil|petrol|fuel|gas|lng|lpg|ngl|diesel|gasoline|crude|propane|butane|kerosene|jet|ethanol|naphtha|bitumen|asphalt"
CA_BOXES = {"Sarnia": (42.75, -82.55, 43.05, -82.25), "Windsor": (42.15, -83.15, 42.35, -82.85), "Nanticoke": (42.72, -80.20, 42.85, -79.95), "Hamilton": (43.20, -79.95, 43.32, -79.70), "Oakville-Burlington": (43.30, -79.85, 43.52, -79.55),
 "Mississauga-Toronto": (43.52, -79.70, 43.80, -79.20), "London": (42.90, -81.35, 43.05, -81.10), "Clarkson-Port Credit": (43.48, -79.65, 43.60, -79.50), "Kingston-Brockville": (44.15, -76.60, 44.65, -75.60), "Montreal East": (45.55, -73.65, 45.72, -73.45),
 "Montreal": (45.40, -73.80, 45.55, -73.50), "Levis-Quebec": (46.68, -71.35, 46.86, -71.05), "Hardisty": (52.60, -111.45, 52.74, -111.15), "Edmonton-Strathcona": (53.50, -113.55, 53.80, -112.95), "Fort Saskatchewan": (53.68, -113.35, 53.80, -113.05),
 "Saint John": (45.18, -66.15, 45.30, -65.95), "Superior WI": (46.58, -92.25, 46.80, -91.80), "Patoka IL": (38.68, -89.20, 38.82, -88.95), "Cushing OK": (35.88, -96.88, 36.10, -96.65), "NY Harbor-North": (40.62, -74.30, 40.78, -74.00), "NY Harbor-South": (40.45, -74.30, 40.62, -74.05),
 "Houston Ship Channel W": (29.60, -95.30, 29.80, -95.05), "Houston Ship Channel E": (29.60, -95.05, 29.85, -94.80), "Texas City": (29.33, -94.98, 29.46, -94.85), "Mont Belvieu": (29.78, -94.99, 29.92, -94.80), "Beaumont-Port Arthur": (29.80, -94.15, 30.12, -93.85),
 "Lake Charles": (30.05, -93.35, 30.30, -93.15), "Corpus Christi": (27.78, -97.55, 27.90, -97.30), "St James LA": (29.95, -90.95, 30.12, -90.70), "Chicago-Joliet": (41.35, -88.30, 41.90, -87.85), "Chicago-Calumet": (41.55, -87.60, 41.75, -87.30),
 "Philadelphia-Marcus Hook": (39.78, -75.55, 39.97, -75.05), "Albany-Rensselaer": (42.55, -73.85, 42.70, -73.65), "Boston-Everett": (42.35, -71.10, 42.45, -70.95), "Portland ME": (43.60, -70.35, 43.70, -70.20), "Detroit-River Rouge": (42.20, -83.25, 42.35, -83.05), "Toledo": (41.60, -83.55, 41.72, -83.40),
 "Buffalo-Tonawanda": (42.85, -78.95, 43.05, -78.80), "Cleveland": (41.40, -81.80, 41.55, -81.60), "Duluth-Superior": (46.70, -92.20, 46.80, -92.00), "Whiting-Hammond": (41.60, -87.55, 41.70, -87.40), "Baltimore": (39.18, -76.65, 39.32, -76.45), "Norfolk-Chesapeake": (36.75, -76.35, 36.95, -76.20)}
REGIONS = {"ON-GH-SW": (41.9, -83.2, 44.7, -78.8), "ON-East": (44.0, -78.9, 45.3, -74.0), "QC-South": (45.0, -74.3, 46.9, -71.0), "MI-LP": (41.7, -86.8, 45.9, -82.4), "OH": (38.4, -84.9, 42.0, -80.5), "NY-PA": (39.7, -80.6, 43.4, -73.7), "NJ-DE-MD": (37.9, -77.5, 41.4, -73.8), "New England": (41.0, -73.8, 45.0, -69.9),
 "IL-IN-WI": (37.0, -91.5, 43.0, -84.8), "MN-WI-N": (43.0, -97.0, 47.5, -87.5), "Gulf-TX": (27.0, -98.0, 30.5, -93.5), "Gulf-LA": (28.8, -93.5, 31.2, -88.8), "OK-KS": (34.5, -98.5, 38.0, -94.5)}
def q(body, cache):
    f = f"data/ref/tanks_raw/{hashlib.md5(cache.encode()).hexdigest()[:12]}.json"
    if os.path.exists(f): return json.load(open(f))
    if os.environ.get('CACHE_ONLY'): print('  (not cached, skipped)', cache[:30], flush=True); return {'elements': []}
    for k in range(6):
        ov = OVS[k % len(OVS)]
        try:
            d = json.load(urllib.request.urlopen(urllib.request.Request(ov, data=urllib.parse.urlencode({"data": body}).encode(), headers=UA), timeout=200))
            json.dump(d, open(f, "w")); time.sleep(2); return d
        except Exception as e: print("  retry", ov[8:25], str(e)[:60], file=sys.stderr); time.sleep(8)
    print("FAILED", cache, flush=True); return {"elements": []}
def tankq(sel): return f'way["man_made"="storage_tank"]["content"!~"{EXCL}"]{sel};node["man_made"="storage_tank"]["content"!~"{EXCL}"]{sel};'
def osm_all(anchors):
    els = {}
    def take(d, src):
        for e in d.get("elements", []): els.setdefault((e["type"], e["id"]), e)
    for n, bb in CA_BOXES.items():
        d = q(f'[out:json][timeout:180];({tankq("(%s,%s,%s,%s)" % bb)});out tags geom;', "box" + n); take(d, n); print("box", n, len(d["elements"]), flush=True)
    if os.environ.get('BOXES_ONLY'): return els
    B = 70
    for i in range(0, len(anchors), B):
        part = anchors[i:i + B]; sel = "".join(tankq(f"(around:900,{a[0]:.5f},{a[1]:.5f})") for a in part)
        d = q(f'[out:json][timeout:240];({sel});out tags geom;', "anch" + json.dumps(part)); take(d, "anch"); print("anchors", i, len(d["elements"]), flush=True)
    for n, bb in REGIONS.items():
        d = q(f'[out:json][timeout:240];(way["man_made"="storage_tank"]["content"~"{FUEL}",i]({",".join(map(str, bb))});node["man_made"="storage_tank"]["content"~"{FUEL}",i]({",".join(map(str, bb))}););out tags geom;', "reg" + n); take(d, n); print("region", n, len(d["elements"]), flush=True)
    return els
def area_m2(pts):
    if len(pts) < 4: return 0.0
    la0 = sum(p["lat"] for p in pts) / len(pts); kx = 111320 * math.cos(math.radians(la0)); ky = 110574
    a = 0.0
    for p, r in zip(pts, pts[1:] + pts[:1]): a += (p["lon"] * kx) * (r["lat"] * ky) - (r["lon"] * kx) * (p["lat"] * ky)
    return abs(a) / 2
def num(v):
    try: return float(str(v).split()[0].replace(",", "."))
    except Exception: return None
def tanks(els):
    out = []
    for (t, i), e in els.items():
        tg = e.get("tags", {})
        if t == "node": lat, lon, A = e["lat"], e["lon"], 0.0
        else:
            g = e.get("geometry") or []
            if not g: continue
            lat = sum(p["lat"] for p in g) / len(g); lon = sum(p["lon"] for p in g) / len(g); A = area_m2(g)
        d = num(tg.get("diameter"))
        if A < 5 and d: A = math.pi * (d / 2) ** 2
        if A < 80: continue
        h = num(tg.get("height")); out.append(dict(id=f"{t}/{i}", lat=lat, lon=lon, A=A, h=h if h and 3 <= h <= 30 else None, c=(tg.get("content") or "").lower(), op=tg.get("operator") or "", nm=tg.get("name") or "", prod=tg.get("product") or "", ind=tg.get("industrial") or ""))
    return out
def cluster(ts, R=450):
    kx = 111320 * math.cos(math.radians(40)); cell = {}
    for k, t in enumerate(ts): cell.setdefault((int(t["lon"] * 111320 * math.cos(math.radians(t["lat"])) / R), int(t["lat"] * 110574 / R)), []).append(k)
    par = list(range(len(ts)))
    def f(x):
        while par[x] != x: par[x] = par[par[x]]; x = par[x]
        return x
    def dist(a, b): return math.hypot((a["lon"] - b["lon"]) * 111320 * math.cos(math.radians(a["lat"])), (a["lat"] - b["lat"]) * 110574)
    for (cx, cy), ks in cell.items():
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                for j in cell.get((cx + dx, cy + dy), []):
                    for k in ks:
                        if k < j and dist(ts[k], ts[j]) <= R: par[f(k)] = f(j)
    g = {}
    for k in range(len(ts)): g.setdefault(f(k), []).append(ts[k])
    return list(g.values())
if __name__ == "__main__":
    E = eia() if not os.path.exists("data/ref/eia_infra_raw.json") or "--eia" in sys.argv else json.load(open("data/ref/eia_infra_raw.json"))
    anchors = []
    for lay in ("14", "15", "20", "11"):
        for r in E["layers"][lay]["rows"]:
            if r["_lat"] is not None and st(r) in STATES: anchors.append((round(r["_lat"], 3), round(r["_lon"], 3)))
    anchors = sorted(set(anchors)); print("anchors", len(anchors), flush=True)
    els = osm_all(anchors); ts = tanks(els); print("tanks >=80 m2:", len(ts), flush=True)
    cl = []
    for g in cluster(ts):
        if len(g) < 3: continue
        A = sum(t["A"] for t in g); V = sum(t["A"] * (t["h"] or 12.0) for t in g)
        from collections import Counter
        cc = Counter(t["c"] for t in g if t["c"]); ops = Counter(t["op"] for t in g if t["op"]); nms = Counter(t["nm"] for t in g if t["nm"])
        cl.append(dict(lat=round(sum(t["lat"] for t in g) / len(g), 5), lon=round(sum(t["lon"] for t in g) / len(g), 5), n=len(g), area_m2=round(A), est_volume_m3=round(V), n_height_tagged=sum(1 for t in g if t["h"]),
                       content=dict(cc.most_common(4)), operators=[o for o, _ in ops.most_common(3)], names=[o for o, _ in nms.most_common(3)], osm=[t["id"] for t in sorted(g, key=lambda t: -t["A"])[:6]],
                       tanks=[[round(t["lat"], 5), round(t["lon"], 5), round(t["A"])] for t in g]))
    json.dump(dict(source="OpenStreetMap contributors via Overpass API", license="ODbL 1.0", retrieved=TODAY, assumption="volume ESTIMATE = sum(footprint area x tagged height, else 12 m); tanks < 80 m2 footprint ignored; clusters = single linkage 450 m, >= 3 tanks", clusters=cl), open("data/ref/osm_tank_clusters.json", "w"), separators=(",", ":"))
    print("clusters", len(cl), "largest est m3", sorted((c["est_volume_m3"] for c in cl), reverse=True)[:5])
