#!/usr/bin/env python3
"""v0.4 field infrastructure: EIA gas processing plants (EIA-757) + OSM field facilities/lines in SW Ontario (incl. Lake Erie) and Michigan. One Overpass query per box, cached.
Writes data/field_infra.json {points:[], lines:[]}."""
import json, sys, os, datetime
sys.path.insert(0, os.path.dirname(__file__)); import fetch_terminals as F
TODAY = datetime.date.today().isoformat()
BOX = {"ON-LakeErie": (41.55, -83.6, 43.45, -79.5), "MI": (41.7, -86.8, 45.9, -82.4)}
def sel(bb):
    b = ",".join(map(str, bb))
    return (f'way["man_made"="pipeline"]["substance"~"gas|oil|natural_gas"]["location"~"underwater|offshore"]({b});'
            f'node["pipeline"="substation"]({b});way["pipeline"="substation"]({b});node["man_made"="petroleum_well"]({b});way["man_made"="petroleum_well"]({b});'
            f'way["industrial"~"^(oil|gas|wellsite|gas_plant|oil_gas)$"]({b});node["industrial"~"^(oil|gas|wellsite)$"]({b});')
pts, lines = [], []
E = json.load(open("data/ref/eia_infra_raw.json"))["layers"]["11"]
for r in E["rows"]:
    if r["_lat"] is None: continue
    cap = f"{r['Cap_MMcfd']:g} MMcf/d (about {r['Cap_MMcfd'] * 0.0283168:.2f} million m3/d, converted)" if r.get("Cap_MMcfd") else None
    pts.append(dict(id=f"gp{r['FID']}", name=r["Plant_Name"], kind="processing", type_label="Natural gas processing plant", operator=r.get("Operator") or r.get("Owner"), capacity=cap, capacity_basis=f"EIA-757 processing capacity, survey year {r.get('Period')}" if cap else None,
                    detail=f"{r.get('City') or ''}, {r.get('County') or ''} County, {r.get('State')}".strip(", "), lat=round(r["_lat"], 5), lon=round(r["_lon"], 5), pos_source="EIA listing (location approximate, from public information)", sources=[F.EIA + "/11"] if hasattr(F, "EIA") else []))
n_osm = 0
for n, bb in BOX.items():
    d = F.q(f'[out:json][timeout:180];({sel(bb)});out tags geom;', "field" + n); print("field", n, len(d.get("elements", [])), flush=True)
    for e in d.get("elements", []):
        t = e.get("tags", {}); url = f"https://www.openstreetmap.org/{e['type']}/{e['id']}"
        if t.get("man_made") == "pipeline":
            g = e.get("geometry") or []
            if len(g) >= 2: lines.append(dict(id=f"osm{e['id']}", name=t.get("name") or "Offshore/underwater pipeline (OSM)", substance=t.get("substance"), operator=t.get("operator"), pts=[[round(p["lon"], 5), round(p["lat"], 5)] for p in g], sources=[url]))
            continue
        if e["type"] == "node": la, lo = e["lat"], e["lon"]
        else:
            g = e.get("geometry") or []
            if not g: continue
            la = sum(p["lat"] for p in g) / len(g); lo = sum(p["lon"] for p in g) / len(g)
        if t.get("man_made") == "petroleum_well": continue  # individual wells come from the wells layer (EGLE/OPDS/EIA); OSM copies would duplicate them
        elif t.get("pipeline") == "substation":
            if t.get("substation") not in ("compression", "compressor", "field_gathering", "gathering", "processing"): continue  # generic metering/regulating/valve-type sites are not published (security)
            kind, lab = ("compressor" if "compress" in (t.get("substation") or "") else "facility"), "Pipeline substation: " + (t.get("substation") or "unspecified") + " (OSM)"
        else: kind, lab = "facility", f"Oil/gas industrial site (OSM industrial={t.get('industrial')})"
        pts.append(dict(id=f"osm{e['id']}", name=t.get("name") or lab, kind=kind, type_label=lab, operator=t.get("operator"), status=None, lat=round(la, 5), lon=round(lo, 5), pos_source="OSM mapped geometry", sources=[url, "https://www.openstreetmap.org/copyright"])); n_osm += 1
json.dump(dict(version="0.4.0", retrieved=TODAY, sources=dict(eia_757=F.EIA + "/11" if hasattr(F, "EIA") else "", osm="https://www.openstreetmap.org/copyright (ODbL)"), points=pts, lines=lines), open("data/field_infra.json", "w"), separators=(",", ":"))
import collections; print("points", collections.Counter(p["kind"] for p in pts), "lines", len(lines), "km", round(sum(sum(((a[0]-b[0])*80)**2+((a[1]-b[1])*111)**2 for a, b in zip(l["pts"], l["pts"][1:])) ** 0.5 for l in lines)))
