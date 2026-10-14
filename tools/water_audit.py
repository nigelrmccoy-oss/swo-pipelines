"""Audit: which pipeline geometries cross Great Lakes open water (Natural Earth 10m lakes)."""
import json, glob, shapefile, sys
from shapely.geometry import shape, LineString
from shapely.ops import unary_union
from shapely.prepared import prep
r = shapefile.Reader("data/ref/ne_10m_lakes.shp")
LAKES = {}
for s, rec in zip(r.shapes(), r.records()):
    n = rec.as_dict().get("name") or ""
    if any(k in n for k in ["Ontario", "Erie", "Huron", "Michigan", "Superior", "St. Clair"]): LAKES.setdefault(n, []).append(shape(s.__geo_interface__))
LAKES = {k: unary_union(v) for k, v in LAKES.items()}
def audit(geom, label, out, minkm=1.0):
    for n, poly in LAKES.items():
        if not geom.intersects(poly): continue
        km = geom.intersection(poly).length * 111 * 0.75
        if km >= minkm: out.append((n, round(km, 1), label))
if __name__ == "__main__":
    out = []
    for f in sorted(glob.glob("data/gis/*.geojson")):
        if "nacei" in f: continue
        for i, ft in enumerate(json.load(open(f))["features"]):
            g = ft.get("geometry");
            if g: p = ft["properties"]; audit(shape(g), f"{f.split('/')[-1]}#{i} {p.get('operator') or p.get('opername') or ''} {p.get('name') or p.get('pipename') or ''} {p.get('osm','')}", out)
    D = json.load(open(sys.argv[1] if len(sys.argv) > 1 else "data/swo.json"))
    for l in D["lines"]:
        g = l.get("geometry") or {"type": "LineString", "coordinates": [[w[1], w[0]] for w in l["waypoints"]]}
        audit(shape(g), f"SWO {l['id']}", out)
    for o in sorted(out): print(*o, sep=" | ")
