"""Generate docs/v03.md from data/swo.json (route accuracy per line, facilities with sources, water audit)."""
import json
d = json.load(open("data/swo.json")); A = json.load(open("data/water_audit_v03.json"))
v = lambda f: (f or {}).get("value", "unknown") if isinstance(f, dict) else f
S = lambda f: " ".join(f"<{s}>" for s in (f or {}).get("sources", [])) if isinstance(f, dict) else ""
o = ["# v0.3: real geometry, lake audit, depots, decommissioned refineries, Montreal, Eastern Seaboard", "",
"## Lake crossing audit (Natural Earth 10m lakes vs. drawn geometry)", "",
"- **Lake Ontario: no pipeline crosses it.** The v0.2 schematic Line 9 (20.6 km) and Sun-Canadian (10.4 km) wrongly cut across the lake. Line 9 runs on land through the north-shore municipalities (CER: <https://apps.cer-rec.gc.ca/PPS/en/pipeline-profiles/enbridge-line-9>). One raw-OSM item enters the lake: unnamed oil way 43937155 (<https://www.openstreetmap.org/way/43937155>), which runs ~1.4 km offshore at the former Shell Oakville refinery site (43.37-43.38 N, 79.71-79.73 W). It ends offshore; it does not cross the lake. It is probably a former marine loading line, but that is unverified. It is shown only in the raw OSM layer, not as a researched line.",
"- **Lake Erie:** the v0.2 NEXUS and Rover routes wrongly crossed it (94 km); both now follow EIA/OSM on land. Real pipes in Lake Erie are the Ontario offshore gas-gathering network (~1,600 km of lines, >2,000 wells), shown only as the OSM/CanVec layer (e.g. way 204190626): <https://inis.iaea.org/records/9mzev-fmt35>, <https://www.searchanddiscovery.com/abstracts/html/2014/90195eastern/abstracts/3.html>.",
"- **Lake Michigan / Huron:** v0.2 Line 5/GLGT (129 km) and Vector (65 km) wrongly crossed open water. Now only the real Straits of Mackinac crossings remain (Line 5 dual lines and GLGT), plus short north-shore segments near Naubinway where the route follows the shore (10m shoreline resolution).",
"", "Remaining open-water segments > 1 km in v0.3:", ""] + [f"- {x[2]}: {x[0]} {x[1]} km" for x in A] + ["",
"## Route accuracy per line", "", "| line | accuracy | matched | datasets | note |", "|---|---|---|---|---|"]
for l in d["lines"]:
    a = l["route_accuracy"]; o.append(f"| {l['name']} | {a['level']} | {'' if a.get('matched_share') is None else str(round(a['matched_share']*100))+'%'} | {', '.join(a.get('datasets', []))} | {a.get('note','')} |")
for title, pred in [("Active refineries", lambda f: f["kind"] == "refinery"), ("Decommissioned refineries", lambda f: f["kind"] == "refinery_decom"), ("Fuel terminals / depots", lambda f: f["kind"] == "terminal")]:
    o += ["", f"## {title}", ""]
    for f in [f for f in d["facilities"] if pred(f)]:
        o.append(f"- **{f['name']}** ({f['region']}) at {f['lat']:.4f}, {f['lon']:.4f}; position: {f.get('pos_source')}. Operator: {v(f.get('operator'))}" + "".join(f"; {k.replace('_',' ')}: {v(f[k])}" for k in ("operator_history", "years", "capacity", "status", "current_use") if k in f and v(f[k]) != "unknown") + f". Sources: {S(f.get('operator')) or S(f.get('status'))}")
o += ["", "## Stations", ""] + [f"- {s['name']} ({s['type']}) {s['lat']}, {s['lon']}: {s['coord_note']} {' '.join('<'+x+'>' for x in s['sources'])}" for s in d["stations"]]
o += ["", f"Totals: {len(d['lines'])} lines, {len(d['facilities'])} facilities, {len(d['stations'])} stations, {len(d['crossings'])} crossings, {len(d['sources'])} distinct source URLs."]
open("docs/v03.md", "w").write("\n".join(o) + "\n"); print(len(o))
