"""Build data/routes.json for researched lines (see tools/route_match.py)."""
import json, re, sys
sys.path.insert(0, "tools"); from route_match import route, multi
T = lambda p, *k: " ".join(str(p.get(x) or "") for x in k)
OP = lambda rx: (lambda p: re.search(rx, T(p, "operator", "opername"), re.I))
NM = lambda rx: (lambda p: re.search(rx, T(p, "name", "pipename"), re.I))
AND = lambda *fs: (lambda p: all(f(p) for f in fs)); OR = lambda *fs: (lambda p: any(f(p) for f in fs))
SUB = lambda rx: (lambda p: re.search(rx, p.get("substance") or "", re.I))
WESTOF = lambda lon: (lambda p: p.get("_maxlon", -999) < lon)
P = dict(Superior=(-92.10, 46.69), StraitsN=(-84.76, 45.84), McGulpin=(-84.78, 45.785), Marysville=(-82.48, 42.91), Sarnia=(-82.40, 42.95), Griffith=(-87.42, 41.53),
 Flanagan=(-88.86, 40.88), Stockbridge=(-84.18, 42.45), Joliet=(-88.08, 41.53), StClairX=(-82.478, 42.789), Dawn=(-82.15, 42.70), Kensington=(-80.95, 40.74), Ypsilanti=(-83.61, 42.24),
 Emerson=(-97.21, 49.0), Kirkwall=(-80.15, 43.33), Parkway=(-79.75, 43.53), Dover=(-82.40, 42.42), Lakeshore=(-82.75, 42.30), Ojibway=(-83.09, 42.26),  # town/area points only (no valve-site coordinates)
 London=(-81.25, 42.98), Westover=(-80.10, 43.30), Hamilton=(-79.87, 43.25), Burlington=(-79.82, 43.36), OakvilleN=(-79.72, 43.47), MississaugaN=(-79.65, 43.62), TorontoN=(-79.42, 43.79),
 Oshawa=(-78.86, 43.95), Belleville=(-77.38, 44.19), Kingston=(-76.52, 44.29), Brockville=(-75.70, 44.61), Cornwall=(-74.75, 45.04), Hawkesbury=(-74.62, 45.60), Mirabel=(-74.08, 45.65),
 Terrebonne=(-73.63, 45.70), MontrealEast=(-73.52, 45.64), TorontoW=(-79.52, 43.70))
v = lambda *n: [P[x] for x in n]
ENB_OIL = OR(AND(OP("enbridge|lakehead"), SUB("oil|crude")), AND(OP("ENBRIDGE"), NM("Lakehead|Mainline")))
spec = {
 "line5": (v("Superior", "StraitsN", "McGulpin", "Marysville", "Sarnia"), [("osm_swo_pipelines", NM("line 5|lakehead")), ("us_crude", AND(OP("ENBRIDGE"), NM("Lakehead"))), ("osm_canada_pipelines", NM("line 5"))]),
 "line5_straits": (v("StraitsN", "McGulpin"), [("osm_swo_pipelines", NM("line 5|lakehead"))]),
 "line6": (v("Superior", "Griffith"), [("us_crude", OP("ENBRIDGE")), ("osm_swo_pipelines", ENB_OIL)]),
 "line78": (v("Flanagan", "Griffith", "Stockbridge", "Marysville", "Sarnia"), [("osm_swo_pipelines", OR(NM("line 78|line 79|6b|line 5|lakehead"), AND(ENB_OIL, WESTOF(-82.42), lambda p: not re.search(r"line 9|ligne 9|line 17", T(p, "name"), re.I)))), ("us_crude", AND(OP("ENBRIDGE"), NM("Lakehead|Mainline|Chicap|Southern Access")))]),
 "line6b": (v("Griffith", "Stockbridge", "Marysville", "Sarnia"), [("osm_swo_pipelines", OR(NM("line 78|line 79|6b|line 5|lakehead"), AND(ENB_OIL, WESTOF(-82.42), lambda p: not re.search(r"line 9|ligne 9|line 17", T(p, "name"), re.I)))), ("us_crude", AND(OP("ENBRIDGE"), NM("Lakehead|Mainline")))]),
 "line9": (v("Sarnia", "London", "Westover", "Burlington", "MississaugaN", "TorontoN", "Oshawa", "Belleville", "Kingston", "Brockville", "Cornwall", "Hawkesbury", "Mirabel", "Terrebonne", "MontrealEast"),
           [("osm_canada_pipelines", OR(NM("line 9|ligne 9"), AND(OP("enbridge"), SUB("oil")))), ("osm_swo_pipelines", OR(NM("line 9"), AND(OP("enbridge"), SUB("oil"))))]),
 "vector": (v("Joliet", "StClairX", "Dawn"), [("us_natgas", OP("vector")), ("osm_swo_pipelines", OP("vector"))]),
 "nexus": (v("Kensington", "Ypsilanti"), [("us_natgas", OP("nexus")), ("osm_swo_pipelines", OP("nexus"))]),
 "glgt": (v("Emerson", "StClairX"), [("us_natgas", OP("great lakes gas")), ("osm_swo_pipelines", OR(OP("great lakes gas"), NM("GLGT|great lakes")))]),
 "dawnparkway": (v("Dawn", "Kirkwall", "Parkway"), [("osm_swo_pipelines", NM("dawn to parkway")), ("osm_canada_pipelines", NM("dawn to parkway"))]),
 "panhandle": (v("Dawn", "Dover", "Lakeshore", "Ojibway"), [("osm_swo_pipelines", AND(OP("enbridge|union gas"), SUB("gas"), lambda p: True))]),
 "suncanadian": (v("Sarnia", "London", "Hamilton", "Burlington", "OakvilleN", "TorontoW"), [("osm_canada_pipelines", NM("sun-canadian|sun canadian")), ("osm_swo_pipelines", NM("sun-canadian|sun canadian"))]),
}
MULTI = {"rover": [("us_natgas", OP("rover")), ("osm_swo_pipelines", OP("rover"))]}
out = {}
for k, (vias, rules) in spec.items():
    keep = (lambda a, b: max(a[0], b[0]) < -86.9 or min(a[1], b[1]) < 41.75) if k == "line6" else None  # Line 6 runs south around Lake Michigan, never through Michigan/UP
    r = route(vias, rules, snap_km=25, bridge_km=4.0 if k in ("line9", "glgt", "line5") else 3.0, keep=keep); out[k] = r
    print(f"{k:13s} matched {r['matched_share']:.0%} legs={r['legs']} segs={r['n_segments']} {r['datasets']}")
for k, rules in MULTI.items(): out[k] = multi(rules); print(k, "multi", out[k]["n_segments"])
json.dump(out, open("data/routes_raw.json", "w"))
