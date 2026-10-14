"""Overpass: candidate OSM facility objects near each researched station (for snapping)."""
import json, urllib.request, urllib.parse
D = json.load(open("data/swo.json")); parts = []
for s in D["stations"]:
    a = f"(around:12000,{s['lat']},{s['lon']})"
    parts += [f'nwr["pipeline"]{a};', f'nwr["man_made"~"pumping_station|compressor|works|storage_tank"]["operator"]{a};', f'nwr["operator"~"Enbridge|Union Gas|TC Energy|TransCanada|NEXUS|Nexus|Lakehead",i]["pipeline"!~"."]["man_made"!="pipeline"]{a};', f'nwr["industrial"~"oil|gas|refinery|terminal"]{a};']
q = "[out:json][timeout:300];(" + "".join(parts) + ");out tags center;"
req = urllib.request.Request("https://overpass-api.de/api/interpreter", data=urllib.parse.urlencode({"data": q}).encode(), headers={"User-Agent": "swo-pipelines/0.3 (personal research)"})
d = json.load(urllib.request.urlopen(req, timeout=400)); out = []
for e in d["elements"]:
    c = e.get("center") or ({"lat": e.get("lat"), "lon": e.get("lon")})
    if c.get("lat") is None or e.get("tags", {}).get("man_made") == "pipeline": continue
    out.append({"osm": f"https://www.openstreetmap.org/{e['type']}/{e['id']}", "lat": c["lat"], "lon": c["lon"], "tags": e.get("tags", {})})
json.dump({"source_url": "https://overpass-api.de/api/interpreter", "query": q, "license": "ODbL 1.0", "retrieved": "2026-10-13", "candidates": out}, open("data/ref/station_candidates.json", "w"), indent=0)
print(len(out))
