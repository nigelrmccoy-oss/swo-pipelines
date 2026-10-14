"""Detailed OSM pipelines + pipeline stations + refineries/storage for the SW Ontario / Michigan focus box."""
import json, urllib.request, urllib.parse
OV = "https://overpass-api.de/api/interpreter"; BB = "41.5,-87.5,46.5,-79.0"
q = f'[out:json][timeout:300];(way["man_made"="pipeline"]["substance"~"gas|oil|fuel|ngl|lpg|crude|petroleum|ethylene|propane|butane"]({BB});nwr["pipeline"="substation"]({BB});nwr["industrial"="refinery"]({BB});nwr["man_made"="pumping_station"]["substance"]({BB}););out tags center geom;'
req = urllib.request.Request(OV, data=urllib.parse.urlencode({"data": q}).encode(), headers={"User-Agent": "swo-pipelines/0.2 (personal research)"})
d = json.load(urllib.request.urlopen(req, timeout=400)); lines, pts = [], []
for e in d["elements"]:
    t = e.get("tags", {}); props = {"osm": f"https://www.openstreetmap.org/{e['type']}/{e['id']}", **{k: t.get(k) for k in ["name","operator","substance","diameter","location","substation","industrial","pipeline","man_made","ref"] if t.get(k)}}
    if e["type"] == "way" and t.get("man_made") == "pipeline" and e.get("geometry"):
        lines.append({"type":"Feature","geometry":{"type":"LineString","coordinates":[[round(p["lon"],5),round(p["lat"],5)] for p in e["geometry"]]},"properties":props})
    else:
        c = e.get("center") or ({"lat":e["lat"],"lon":e["lon"]} if "lat" in e else None)
        if c: pts.append({"type":"Feature","geometry":{"type":"Point","coordinates":[c["lon"],c["lat"]]},"properties":props})
meta = dict(source_url=OV, source=f"OpenStreetMap contributors via Overpass; query: {q}", license="ODbL 1.0 (c) OpenStreetMap contributors", retrieved="2026-10-13")
json.dump({"type":"FeatureCollection","name":"osm_swo_pipelines",**meta,"features":lines}, open("data/gis/osm_swo_pipelines.geojson","w"), separators=(",",":"))
json.dump({"type":"FeatureCollection","name":"osm_swo_facilities",**meta,"features":pts}, open("data/gis/osm_swo_facilities.geojson","w"), separators=(",",":"))
print(len(lines), len(pts)); from collections import Counter; print(Counter((p["properties"].get("substation") or p["properties"].get("industrial") or p["properties"].get("man_made")) for p in pts))
