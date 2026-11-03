#!/usr/bin/env python3
"""Build data/terminals.json (v0.4): large oil & gas terminals.
Inputs: data/ref/osm_tank_clusters.json (tools/fetch_terminals.py), data/ref/eia_infra_raw.json, tools/terminals_curated.json, data/swo.json.
Rules: LNG sites from EIA layer 15 + curated; curated hubs snap to OSM clusters; every other OSM tank cluster whose ESTIMATED shell volume is >= MIN_M3
is listed with kind from OSM content tags / EIA-815 / rail-terminal proximity. Clusters near EIA refineries or v0.3 facilities are dropped (already mapped)."""
import json, math, re, sys, datetime
BBL = 6.2898; MIN_M3 = float(sys.argv[1]) if len(sys.argv) > 1 else 100000.0
TODAY = datetime.date.today().isoformat()
E = json.load(open("data/ref/eia_infra_raw.json"))["layers"]; CL = json.load(open("data/ref/osm_tank_clusters.json")); CUR = json.load(open("tools/terminals_curated.json"))["hubs"]; S = json.load(open("data/swo.json"))
EIA_URL = "https://services7.arcgis.com/p4qwkH3IF5hxHqd7/ArcGIS/rest/services/OilGasInfrastructure/FeatureServer"
def fl(x):
    try: return float(str(x).strip())
    except Exception: return 0.0
def dm(a, b, c, d): return math.hypot((b - d) * 111320 * math.cos(math.radians((a + c) / 2)), (a - c) * 110574)
def title(s): return re.sub(r"\b(Llc|Lp|Inc|Co|Llp|Usa|Ii|Iii)\b", lambda m: m.group(1).upper() if len(m.group(1)) < 4 else m.group(1), (s or "").strip().title())
def region(la, lo):
    if 27 < la < 28.6 and -98 < lo < -96.5: return "Gulf Coast - South Texas"
    if 38.5 < la < 40.2 and -76 < lo < -75.0: return "Eastern Seaboard - Delaware Valley"
    if 30 < la < 36 and -82.5 < lo < -78: return "Eastern Seaboard - Southeast"
    if la > 41.5 and -83.6 < lo < -81.6 and la < 43.2: return "SW Ontario / Windsor-Sarnia" if lo < -81.5 and la > 42.0 else "Great Lakes (US)"
    if 42.0 < la < 44.2 and -81.6 <= lo < -78.9: return "Golden Horseshoe / SW Ontario"
    if 44.0 < la < 46 and -78.9 <= lo < -74: return "Eastern Ontario"
    if 45 < la < 47.5 and -74.5 < lo < -70.5: return "Montreal / Quebec"
    if la > 44.4 and lo > -68 or (la > 44.0 and -67 < lo < -64): return "Eastern Canada (Maritimes)"
    if 51 < la < 56 and lo < -108: return "Hubs - Western Canada"
    if la < 31.5 and -98.5 < lo < -88: return "Gulf Coast - Houston / Beaumont" if lo < -92.5 else "Gulf Coast - Louisiana"
    if 34 < la < 39 and -99 < lo < -94: return "Hubs - Mid-Continent"
    if 36.5 < la < 43 and -75.8 < lo < -69: return "Eastern Seaboard - NY Harbor" if la < 41.2 and lo < -73.7 else "Eastern Seaboard"
    if 37 < la < 40 and -77.5 <= lo < -74: return "Eastern Seaboard"
    if 36 < la < 38.5 and lo < -75.5 and lo > -77.5: return "Eastern Seaboard"
    if 41 < la < 47.6 and -93 < lo < -82: return "Great Lakes (US)"
    if 37 < la < 42.5 and -91.5 < lo < -80: return "Great Lakes (US)"
    if 39 < la < 45 and -80.6 < lo < -73.7: return "Eastern Seaboard" if lo > -77.5 else "Great Lakes (US)"
    return "Other (mapped area)"
fac = [(f["lat"], f["lon"], f["name"]) for f in S["facilities"] if f.get("kind") in ("refinery", "refinery_decom", "terminal", "storage")]
refs = [(r["_lat"], r["_lon"], r["Site"]) for r in E["10"]["rows"] if r["_lat"]]
eia14 = [r for r in E["14"]["rows"] if r["_lat"]]
rail = [r for r in E["20"]["rows"] if r["_lat"]]
def near(lst, la, lo, R): return [x for x in lst if abs(x[0] - la) < 0.03 and dm(x[0], x[1], la, lo) <= R]
used = set(); out = []
def mk(**k): k.setdefault("tanks", 0); out.append(k); return k
def eia_list(la, lo, R=1200):
    L = []
    for r in eia14:
        if abs(r["_lat"] - la) < 0.03 and dm(r["_lat"], r["_lon"], la, lo) <= R: L.append(dict(company=title(r["Company"]), site=title(r["Site"]), city=title(r["City"]), layer="EIA-815 petroleum product terminals", period=r["Period"]))
    return L
# 1) curated hubs
for h in CUR:
    cs = [i for i, c in enumerate(CL["clusters"]) if i not in used and dm(c["lat"], c["lon"], h["lat"], h["lon"]) <= h["radius_m"]]
    cap = dict(h["capacity"]); 
    if "m3" in cap and "bbl" not in cap: cap["bbl"] = cap["m3"] * BBL
    if "bbl" in cap and "m3" not in cap: cap["m3"] = cap["bbl"] / BBL
    cap["bbl"] = round(cap["bbl"]) if cap.get("bbl") else None; cap["m3"] = round(cap["m3"])
    if h["kind"] == "lng": cap["bbl"] = None  # gas-equivalent m3, not liquid barrels
    t = dict(id=h["id"], name=h["name"], kind=h["kind"], operator=h["operator"], hub=True, region=h["region"], capacity=cap, regas=h.get("regas"), note=h.get("note"), sources=list(cap["sources"]))
    if cs:
        V = sum(CL["clusters"][i]["est_volume_m3"] for i in cs); w = [CL["clusters"][i]["est_volume_m3"] for i in cs]
        t.update(lat=round(sum(CL["clusters"][i]["lat"] * x for i, x in zip(cs, w)) / sum(w), 5), lon=round(sum(CL["clusters"][i]["lon"] * x for i, x in zip(cs, w)) / sum(w), 5),
                 est_volume_m3=V, est_volume_bbl=round(V * BBL), tanks=sum(CL["clusters"][i]["n"] for i in cs), area_m2=sum(CL["clusters"][i]["area_m2"] for i in cs), n_height_tagged=sum(CL["clusters"][i]["n_height_tagged"] for i in cs),
                 pos_source=f"OSM storage_tank clusters ({len(cs)}) within {h['radius_m'] / 1000:.0f} km of the approximate hub centre; point = volume-weighted centre (all operators in that area)")
        used.update(cs)
    else: t.update(lat=h["lat"], lon=h["lon"], pos_source="approximate: hub area centre (no OSM tank cluster found nearby)")
    t["sources"].append("https://www.openstreetmap.org/copyright (tank-farm geometry, ODbL)") if cs else None
    t["eia"] = eia_list(t["lat"], t["lon"], 2500) if h["kind"] != "lng" else []
    mk(**t)
# 2) EIA LNG layer
for r in E["15"]["rows"]:
    if r["_lat"] is None: continue
    if any(dm(r["_lat"], r["_lon"], o["lat"], o["lon"]) < 3000 for o in out if o["kind"] == "lng"): continue
    stor = r.get("Stora_Bcf"); rg = fl(r.get("Regas_Bcfd")); lq = fl(r.get("Liq_Bcfd"))
    cap = None
    if stor: cap = dict(text=f"{stor} Bcf storage (about {stor * 28.3168:.0f} million m3 of gas, converted)", m3=round(stor * 28.3168e6), bbl=None, basis="sourced: EIA (converted from Bcf)", as_of=r["Period"], sources=[EIA_URL + "/15"])
    rgt = "; ".join(x for x in [f"regasification {rg} Bcf/d (about {rg * 28.3168:.0f} million m3/d, converted)" if rg else "", f"liquefaction {lq} Bcf/d (about {lq * 28.3168:.1f} million m3/d, converted)" if lq else ""] if x)
    cs = [i for i, c in enumerate(CL["clusters"]) if dm(c["lat"], c["lon"], r["_lat"], r["_lon"]) <= 1500]; used.update(cs)
    mk(id="lng-" + re.sub(r"\W+", "-", r["Facility"].lower()).strip("-"), name=re.sub(r"\s+LNG\s+LNG", " LNG", f"{r['Facility']} LNG") + (f" ({', '.join(x for x in [r.get('City'), r.get('State')] if x and str(x).strip())})" if r.get('City') or r.get('State') else ""), kind="lng", operator=r.get("Operator") or r.get("Owner"), hub=False, region=region(r["_lat"], r["_lon"]), capacity=cap, regas=rgt or None,
       lat=round(r["_lat"], 5), lon=round(r["_lon"], 5), pos_source="EIA listing: approximate location from public information", note=f"Function: {r.get('Functions')}. EIA layer is dated {r['Period']}: newer plants/expansions are not in it.", sources=[EIA_URL + "/15"], eia=[])
# 3) remaining OSM clusters
dropped = dict(small=0, refinery=0, v03=0); k = 0
for i, c in sorted(enumerate(CL["clusters"]), key=lambda x: (-x[1]["est_volume_m3"])):
    if i in used: continue
    if c["est_volume_m3"] < MIN_M3: dropped["small"] += 1; continue
    if near(refs, c["lat"], c["lon"], 1000): dropped["refinery"] += 1; continue
    if near(fac, c["lat"], c["lon"], 1200): dropped["v03"] += 1; continue
    eia = eia_list(c["lat"], c["lon"]); txt = " ".join(c["content"]).lower()
    nm = next((n for n in c["names"] if len(n) > 3 and not n.strip().isdigit()), "")
    if re.search(r"lpg|propane|butane|ngl|ethane", txt): kind = "ngl"
    elif re.search(r"\blng\b|liquefied natural", txt): kind = "lng"
    elif re.search(r"crude|(?<!fuel_)\boil\b|bitumen", txt) or near([(r["_lat"], r["_lon"]) for r in rail], c["lat"], c["lon"], 1500): kind = "crude"
    else: kind = "products"
    ops = [o for o in c["operators"]] or sorted({e["company"] for e in eia})[:3]
    name = nm or (f"{ops[0]} tank farm" if ops else (f"{eia[0]['company']} - {eia[0]['site']}" if eia else ""))
    if not name:
        nc = [r for r in eia14 if abs(r["_lat"] - c["lat"]) < 0.06 and dm(r["_lat"], r["_lon"], c["lat"], c["lon"]) <= 5000]
        name = f"Tank farm near {title(nc[0]['City'])}" if nc else f"Tank farm ({c['lat']:.3f}, {c['lon']:.3f})"
    k += 1
    note = [] ; 
    if not c["content"]: note.append("product not tagged in OSM; kind from EIA listing or default (refined products)" if kind == "products" else "kind from nearby EIA rail-terminal listing")
    if kind == "ngl": note.append("LPG/NGL kind from OSM content tag")
    mk(id=f"t{k:03d}-{kind}", name=name, kind=kind, operator=", ".join(ops) if ops else None, hub=False, region=region(c["lat"], c["lon"]), capacity=None, lat=c["lat"], lon=c["lon"], est_volume_m3=c["est_volume_m3"], est_volume_bbl=round(c["est_volume_m3"] * BBL), tanks=c["n"], area_m2=c["area_m2"], n_height_tagged=c["n_height_tagged"],
       pos_source="OSM storage_tank cluster centre (mapped tank geometry)", note="; ".join(note) or None, eia=eia, sources=[f"https://www.openstreetmap.org/{o}" for o in c["osm"][:3]] + ([EIA_URL + "/14"] if eia else []))
out.sort(key=lambda t: (t["region"], -(t["capacity"] or {}).get("bbl", 0) if t["capacity"] and t["capacity"].get("bbl") else -t.get("est_volume_bbl", 0)))
for t in out:
    t.setdefault("capacity", None); t["lat"] = round(t["lat"], 5); t["lon"] = round(t["lon"], 5)
doc = dict(version="0.4.0", retrieved=TODAY, min_estimated_volume_m3=MIN_M3, method="Sourced capacities for hubs/LNG; every other terminal is an OSM tank cluster whose shell volume is an ESTIMATE (sum of footprint area x tagged height, else 12 m assumed).",
           dropped=dropped, counts={k: sum(1 for t in out if t["kind"] == k) for k in ("crude", "products", "lng", "ngl")}, terminals=out)
json.dump(doc, open("data/terminals.json", "w"), separators=(",", ":"), ensure_ascii=False)
print(len(out), "terminals", doc["counts"], "dropped", dropped, "sourced-capacity", sum(1 for t in out if t["capacity"]))
