"""Small tiled Overpass queries (more reliable): fuel/oil terminals, depots, tank farms, refineries per city box, and pipeline facilities near stations."""
import json, urllib.request, urllib.parse, time, sys
OVS = ["https://overpass.private.coffee/api/interpreter", "https://maps.mail.ru/osm/tools/overpass/api/interpreter", "https://overpass-api.de/api/interpreter", "https://overpass.kumi.systems/api/interpreter"]
BOXES = {"Sarnia": "42.75,-82.55,43.05,-82.25", "Windsor": "42.15,-83.15,42.35,-82.85", "Nanticoke": "42.72,-80.20,42.85,-79.95", "Hamilton": "43.20,-79.95,43.32,-79.70",
 "Oakville-Burlington": "43.30,-79.85,43.52,-79.55", "Mississauga-Toronto": "43.52,-79.70,43.80,-79.20", "London": "42.90,-81.35,43.05,-81.10", "MontrealEast": "45.55,-73.65,45.72,-73.45",
 "Montreal": "45.40,-73.80,45.55,-73.50", "Kingston-Brockville": "44.15,-76.60,44.65,-75.60"}
def q(body):
    for k in range(6):
        ov = OVS[k % len(OVS)]
        try:
            req = urllib.request.Request(ov, data=urllib.parse.urlencode({"data": body}).encode(), headers={"User-Agent": "swo-pipelines/0.3 (personal research)"})
            return json.load(urllib.request.urlopen(req, timeout=100)), ov
        except Exception as e: print("retry", e, file=sys.stderr); time.sleep(10)
    return None, None
items = []
for name, bb in BOXES.items():
    body = f'[out:json][timeout:90];(nwr["industrial"~"oil|fuel|refinery|terminal|depot|petroleum|tank_farm"]({bb});nwr["landuse"="industrial"]["operator"]["name"~"terminal|tank|petroleum|oil|fuel|refiner|imperial|suncor|shell|esso|petro|sunoco|enbridge|trans-northern|nustar|ultramar|valero|parkland|husky|irving|energir|pipe",i]({bb});nwr["man_made"="pumping_station"]({bb});nwr["pipeline"="substation"]({bb}););out tags center;'
    d, ov = q(body)
    if not d: print("FAILED", name); continue
    for e in d["elements"]:
        c = e.get("center") or {"lat": e.get("lat"), "lon": e.get("lon")}
        if c.get("lat") is None: continue
        items.append({"area": name, "osm": f"https://www.openstreetmap.org/{e['type']}/{e['id']}", "lat": round(c["lat"], 6), "lon": round(c["lon"], 6), "tags": e.get("tags", {}), "query_endpoint": ov})
    print(name, len(d["elements"])); time.sleep(3)
json.dump({"source": "OpenStreetMap contributors via Overpass API", "license": "ODbL 1.0", "retrieved": "2026-10-13", "boxes": BOXES, "items": items}, open("data/ref/osm_tiles_raw.json", "w"), indent=0)
