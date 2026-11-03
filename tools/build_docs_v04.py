"""Generate docs/v04.md from data/terminals.json, data/wells/wells.json and data/field_infra.json."""
import json
T = json.load(open("data/terminals.json")); W = json.load(open("data/wells/wells.json")); F = json.load(open("data/field_infra.json"))
o = ["# v0.4: large terminals, wells and field infrastructure", "",
 f"Generated {T['retrieved']}. Terminals: **{len(T['terminals'])}** ({', '.join(f'{v} {k}' for k, v in T['counts'].items())}). Wells: **{sum(r['n'] for r in W['regions']):,}**. Field points: **{len(F['points'])}**.", "",
 "## Method (terminals)", "",
 "- **Sourced capacities** (19 entries): Cushing, Hardisty, Edmonton, Superior, Patoka, Nederland, St. James, Mont Belvieu, Bayonne, Perth Amboy/Port Reading, Linden, Canaport LNG and the EIA LNG terminals. Each capacity links its source and date; conflicting sources are noted (Edmonton: 4.79 million bbl in a 2006 CER filing vs 13.11 million bbl in Oil Sands Magazine).",
 "- **Every other terminal is an OSM tank farm**: `man_made=storage_tank` ways/nodes (content not water/sewage/grain etc.) in tiled boxes around the Sarnia, Windsor, Golden Horseshoe, Montreal/Quebec, Maritime, Great Lakes, Gulf Coast, Eastern Seaboard and hub areas (`tools/fetch_terminals.py`), clustered at 450 m (single linkage, >= 3 tanks). **Shell volume is an ESTIMATE**: sum of mapped footprint area x tagged height (else an assumed 12 m). Tanks under 80 m2 are ignored and OSM is incomplete, so these are rough.",
 f"- Listed when estimated volume >= {T['min_estimated_volume_m3']:,.0f} m3 (about {T['min_estimated_volume_m3'] * 6.2898 / 1e3:,.0f} thousand bbl). Dropped: {T['dropped']['small']} smaller clusters, {T['dropped']['refinery']} inside EIA refineries (already mapped), {T['dropped']['v03']} on existing v0.3 depots/refineries.",
 "- Kind comes from OSM `content` (LPG/propane/NGL, LNG, crude/oil), else proximity to an EIA crude rail terminal, else refined products (EIA-815 listing). Names/operators: OSM tags, else EIA-815 company within 1.2 km.",
 "- LNG: EIA layer 15 (8 sites, **dated Apr 2020**; newer plants such as Plaquemines and Golden Pass are not in it) plus Canaport. Bcf converted at 28.3168 million m3/Bcf and labelled converted.", "",
 "## Terminals", "", "| Terminal | Kind | Region | Capacity (sourced) / tank-farm ESTIMATE | Sources |", "|---|---|---|---|---|"]
for t in T["terminals"]:
    c = t.get("capacity"); cap = (c["text"] + f" ({c.get('as_of') or 'undated'})") if c else ""
    if t.get("est_volume_m3"): cap += (" / " if cap else "") + f"ESTIMATE ~{t['est_volume_m3']:,} m3 ({t['est_volume_bbl']:,} bbl), {t['tanks']} tanks"
    src = " ".join(f"<{s}>" for s in (c["sources"] if c else [])) or " ".join(f"<{s}>" for s in t["sources"][:2])
    o.append(f"| {t['name']} | {t['kind']} | {t['region']} | {cap} | {src} |")
o += ["", "## Wells", ""]
for r in W["regions"]:
    o.append(f"- **{r['id']}** ({r['n']:,} wells{', ' + str(r['offshore']) + ' offshore (Lake Erie)' if r.get('offshore') else ''}): {r['source']}; <{r['url']}>; service {r['service']}; licence: {r['license']}.")
o += ["", "Plugged/abandoned wells are hidden by default (toggle in the legend). Never-drilled records (permits/locations/'Not Drilled') are excluded. OH/PA/NY come from EIA layers with type and county only (no status, no operator).", "",
 "## Field infrastructure", "", f"- {sum(1 for p in F['points'] if p['kind'] == 'processing')} EIA-757 gas processing plants (continental US; locations approximate), {sum(1 for p in F['points'] if p['kind'] == 'compressor')} OSM compressor sites and {sum(1 for p in F['points'] if p['kind'] == 'facility')} OSM oil/gas industrial and field-gathering sites in SW Ontario/Lake Erie and Michigan.",
 "- Generic metering/regulating/valve-type pipeline sites are deliberately not published. OSM `petroleum_well` nodes are not duplicated (the wells layer has them).",
 f"- Gathering lines: **{len(F['lines'])} found**. OSM has no mapped underwater/offshore pipelines in the Lake Erie box, so the Lake Erie gas-gathering network is not drawn (public Ontario data has wells, not lines). The line-drawing code is in place if data is added to `data/field_infra.json`.", ""]
open("docs/v04.md", "w").write("\n".join(o)); print("docs/v04.md", len(o), "lines")
