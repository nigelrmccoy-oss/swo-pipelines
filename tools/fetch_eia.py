"""Download EIA pipeline layers (DOE/NETL-hosted EIA_pipeline_data FeatureServer) to GeoJSON, simplified, with source URL recorded."""
import json, urllib.request, urllib.parse, sys
BASE = "https://arcgis.netl.doe.gov/server/rest/services/Hosted/EIA_pipeline_data/FeatureServer"
LAYERS = {0: "us_hgl", 1: "us_products", 2: "us_crude", 3: "us_natgas"}
for lid, name in LAYERS.items():
    feats, off = [], 0
    while True:
        q = dict(where="1=1", outFields="*", outSR=4326, f="geojson", resultOffset=off, resultRecordCount=2000, maxAllowableOffset=0.003, geometryPrecision=4)
        url = f"{BASE}/{lid}/query?" + urllib.parse.urlencode(q)
        d = json.load(urllib.request.urlopen(url, timeout=120)); fs = d.get("features", [])
        feats += [f for f in fs if f.get("geometry")]; off += len(fs)
        print(name, off, file=sys.stderr)
        if len(fs) < 2000: break
    json.dump({"type": "FeatureCollection", "name": name, "source_url": f"{BASE}/{lid}", "source": "U.S. EIA pipeline layers, hosted by DOE/NETL (EIA_pipeline_data FeatureServer); see https://www.eia.gov/maps/layer_info-m.php",
               "license": "U.S. Government public domain", "retrieved": "2026-10-13", "features": feats}, open(f"data/gis/{name}.geojson", "w"), separators=(",", ":"))
