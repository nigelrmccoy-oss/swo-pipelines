"""Overpass: (a) fuel/petroleum depots, terminals, tank farms, refineries in SW Ontario + Golden Horseshoe; (b) pipeline-tagged objects near researched stations (snapping)."""
import json, urllib.request, urllib.parse, sys
import os
BB = "41.6,-83.3,44.6,-78.6"; MTL = "45.35,-73.95,45.75,-73.40"; OV = os.environ.get("OV", "https://overpass-api.de/api/interpreter")
def run(q, out):
    req = urllib.request.Request(OV, data=urllib.parse.urlencode({"data": q}).encode(), headers={"User-Agent": "swo-pipelines/0.3 (personal research)"})
    d = json.load(urllib.request.urlopen(req, timeout=300)); res = []
    for e in d["elements"]:
        c = e.get("center") or {"lat": e.get("lat"), "lon": e.get("lon")}
        if c.get("lat") is None or e.get("tags", {}).get("man_made") == "pipeline": continue
        res.append({"osm": f"https://www.openstreetmap.org/{e['type']}/{e['id']}", "lat": round(c["lat"], 6), "lon": round(c["lon"], 6), "tags": e.get("tags", {})})
    json.dump({"source_url": OV, "query": q, "license": "ODbL 1.0 (c) OpenStreetMap contributors", "retrieved": "2026-10-13", "items": res}, open(out, "w"), indent=0); print(out, len(res))
which = sys.argv[1]
if which == "depots":
    run(f'[out:json][timeout:240];(nwr["industrial"~"oil|fuel|refinery|terminal|depot|petroleum|tank_farm"]({BB});nwr["industrial"~"oil|fuel|refinery|terminal|depot|petroleum|tank_farm"]({MTL});nwr["landuse"="industrial"]["operator"~"Imperial|Suncor|Shell|Esso|Petro|Sunoco|Enbridge|Trans-Northern|NuStar|Ultramar|Valero|Parkland|Energir|Énergir|Montreal Pipe",i]({MTL}););out tags center;', "data/ref/osm_depots_raw.json")
else:
    D = json.load(open("data/swo.json"))
    q = "[out:json][timeout:240];(" + "".join(f'nwr["pipeline"="substation"](around:8000,{s["lat"]},{s["lon"]});nwr["operator"~"Enbridge|Union Gas|TC Energy|TransCanada|NEXUS|Nexus",i]["man_made"!="pipeline"](around:8000,{s["lat"]},{s["lon"]});' for s in D["stations"]) + ");out tags center;"
    run(q, "data/ref/station_candidates.json")
