"""NACEI border-crossing points (NRCan MapServer) + OSM pipelines (Overpass) for Canada and Mexico, to GeoJSON with source URLs."""
import json, urllib.request, urllib.parse, sys, os
N = "https://geoappext.nrcan.gc.ca/arcgis/rest/services/NACEI/energy_infrastructure_of_north_america_en/MapServer"
if os.environ.get("NACEI","1")=="1":
 for lid, name in {2: "nacei_border_gas", 3: "nacei_border_liquids"}.items():
     u = f"{N}/{lid}/query?where=1%3D1&outFields=*&outSR=4326&f=geojson"
     d = json.load(urllib.request.urlopen(u, timeout=120))
     d.update(name=name, source_url=f"{N}/{lid}", source="North American Cooperation on Energy Information (NACEI), Aug 2017", retrieved="2026-10-13")
     json.dump(d, open(f"data/gis/{name}.geojson", "w"), separators=(",", ":")); print(name, len(d["features"]), file=sys.stderr)
import os; OV = os.environ.get("OV","https://overpass-api.de/api/interpreter")
for iso, name in {k:v for k,v in {"CA": "osm_canada_pipelines", "MX": "osm_mexico_pipelines"}.items() if k in os.environ.get("ISO","CA,MX")}.items():
    q = f'[out:json][timeout:600];{"" if iso=="MX" else chr(97)+"rea[\"ISO3166-1\"=\""+iso+"\"][admin_level=2]->.a;"}way["man_made"="pipeline"]["substance"~"^(gas|oil|fuel|natural_gas|crude_oil|ngl|lpg|petroleum)$"]{"(14.5,-118.5,32.7,-86.7)" if iso=="MX" else "(area.a)"};out tags geom;'
    req = urllib.request.Request(OV, data=urllib.parse.urlencode({"data": q}).encode(), headers={"User-Agent": "swo-pipelines/0.2 (personal research)"})
    d = json.load(urllib.request.urlopen(req, timeout=900)); feats = []
    for e in d["elements"]:
        g = e.get("geometry");
        if not g: continue
        c = [[round(p["lon"], 4), round(p["lat"], 4)] for p in g][::1]
        t = e.get("tags", {})
        feats.append({"type": "Feature", "geometry": {"type": "LineString", "coordinates": c}, "properties": {"osm_id": e["id"], "substance": t.get("substance"), "operator": t.get("operator"), "name": t.get("name"), "diameter": t.get("diameter"), "location": t.get("location")}})
    json.dump({"type": "FeatureCollection", "name": name, "source_url": OV, "source": f"OpenStreetMap contributors via Overpass API; query: {q}", "license": "ODbL 1.0 (c) OpenStreetMap contributors", "retrieved": "2026-10-13", "features": feats}, open(f"data/gis/{name}.geojson", "w"), separators=(",", ":"))
    print(name, len(feats), file=sys.stderr)
