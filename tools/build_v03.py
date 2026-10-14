"""Build data/swo.json v0.3: researched lines with real geometry + accuracy, Montreal and Eastern Seaboard lines,
active / decommissioned refineries, OSM depots and terminals, and stations snapped to OSM where possible."""
import json, re, sys
sys.path.insert(0, "tools"); from route_match import multi, hav
from build_routes import OP, NM, AND, OR, SUB
D = json.load(open("research/pipelines.json")); R = json.load(open("data/routes_raw.json")); OLD = json.load(open("data/ref/swo_v02.json"))
F = lambda v, *s: {"value": v, "sources": list(s)}; U = "unknown"
EIA = "https://arcgis.netl.doe.gov/server/rest/services/Hosted/EIA_pipeline_data/FeatureServer"; OSMS = "https://www.openstreetmap.org/copyright"
def accuracy(lid, r):
    if lid == "glt": return dict(level="approximate", note="Proposed tunnel; drawn along the existing Straits crossing alignment (OSM). The actual tunnel alignment is not in open data.")
    if lid == "line7": return dict(level="unknown", note="Route/endpoint not found in open sources; shown as Sarnia start point only.")
    if "multi" in r: return dict(level="EIA/OSM segments (operator-matched)", note=f"{r['n_segments']} segments drawn as-is; no single chained route.", datasets=r["datasets"])
    s = r["matched_share"]; ds = r["datasets"]; eia = any(d.startswith("us_") for d in ds); osm = any(d.startswith("osm_") for d in ds)
    lvl = "approximate" if s < 0.2 else ("OSM + EIA" if eia and osm else "OSM" if osm else "EIA (~300 m simplified)")
    if 0.2 <= s < 0.9: lvl = "partial: " + lvl
    return dict(level=lvl, matched_share=s, datasets=ds, legs=r["legs"], note="Matched by operator/name tags then chained between via-points; unmatched legs are approximate land via-points (checked against Great Lakes water).")
lines = []
for l in OLD["lines"]:
    r = R.get(l["id"]) or (R["line5_straits"] if l["id"] == "glt" else None)
    l = dict(l); l["route_accuracy"] = accuracy(l["id"], r or {})
    if l["id"] == "line7": l["geometry"] = None
    elif r and "coords" in r: l["geometry"] = {"type": "LineString", "coordinates": r["coords"]}
    elif r: l["geometry"] = {"type": "MultiLineString", "coordinates": r["multi"]}
    srcs = [SRC for d in l["route_accuracy"].get("datasets", []) for SRC in ([EIA] if d.startswith("us_") else [OSMS])]
    l["route_accuracy"]["sources"] = sorted(set(srcs)); l["region"] = "swo"; lines.append(l)
for l in lines:
    if l["id"] == "line9": l["route_accuracy"]["note"] += " Toronto-Hawkesbury middle section is approximate: via-points follow the CER-listed municipalities (Mississauga, Toronto, Oshawa, Belleville, Kingston, Brockville, Cornwall, Hawkesbury) on land north of Lake Ontario."; l["route_accuracy"]["sources"].append("https://apps.cer-rec.gc.ca/PPS/en/pipeline-profiles/enbridge-line-9")
    if l["id"] == "suncanadian": l["route_accuracy"]["note"] = "No OSM/EIA geometry found. Approximate land via-points Sarnia-London-Hamilton-Burlington-Oakville-Toronto (served cities per source); intermediate points are not sourced."
    if l["id"] == "panhandle": l["route_accuracy"]["note"] = "No reliably tagged OSM geometry; approximate via Dawn - Dover TS - Lakeshore valve site - Ojibway (endpoints from OEB/Enbridge sources)."
# ---- Montreal + Eastern Seaboard lines (EIA/OSM operator-matched geometry) ----
W = lambda t: "https://en.wikipedia.org/wiki/" + t
CERM = "https://apps.cer-rec.gc.ca/PPS/en/pipeline-profiles/montreal"; CERT = "https://apps.cer-rec.gc.ca/PPS/en/pipeline-profiles/trans-northern"
CERQ = "https://apps.cer-rec.gc.ca/PPS/en/pipeline-profiles/trans-quebec-maritimes-tqm"; TCQ = "https://www.tcenergy.com/operations/natural-gas/trans-quebec-and-maritimes-pipeline/"
CERML = "https://apps.cer-rec.gc.ca/PPS/en/pipeline-profiles/transcanada-canadian-mainline-tc"; PH = "https://www.pressherald.com/2016/03/09/75-year-old-portland-to-montreal-pipeline-shuts-down/"
IRQ = "https://www.iroquois.com/site/assets/files/1051/corporate_fact_sheet_8_28_2024.pdf"; OGJI = "https://www.ogj.com/general-interest/companies/article/17218826/northeast-us-gas-1-canadian-gas-imports-to-new-york-new-england-surging-in-1992"
TE = "https://infopost.enbridge.com/bu/TE"; EGTS = "https://www.bhegts.com/our-businesses/EGTS"; EGTSF = "https://www.bhegts.com/documents/1077600000072205.pdf"
PNG = "https://www.businesswire.com/news/home/20240815543857/en/Portland-Natural-Gas-Transmission-System-to-Operate-as-a-Standalone-Company-Under-Industry-Veteran"
LAU = "https://www.puc.pa.gov/pcdocs/1611828.pdf"; LAU2 = "https://www.palegis.us/legislation/bills/text/PDF/2017/0/HR0531/PN2542"; CERTN = "https://docs2.cer-rec.gc.ca/ll-eng/llisapi.dll/Open/268719"
FERCM = "https://www.ferc.gov/sites/default/files/2020-08/CP16-486.pdf"
EAST = [
 ("portland_montreal", "Portland-Montreal Pipe Line", "crude", "east", F("Portland Pipe Line Corp. (US) / Montreal Pipe Line Ltd. (Canada, parent Suncor)", W("Portland–Montreal_pipeline"), CERM), F("Crude oil", CERM), F("24 (only operating line; 12-in deactivated 1982, 18-in 2011)", W("Portland–Montreal_pipeline"), CERM),
  F("about 223,000 bbl/d (CER)", CERM), F("236 mi (380 km); Canadian segment 232 km CER-regulated", W("Portland–Montreal_pipeline"), CERM), F("South Portland ME -> Highwater QC border -> Montreal", CERM), F(1941, CERM),
  F("Mothballed / minimal flow: flows to Montreal dropped to zero Jan 2016 after Line 9 reversal; kept wet", PH, W("Portland–Montreal_pipeline")), [("us_crude", OP("PORTLAND")), ("osm_canada_pipelines", NM("montreal pipe|portland"))], [F("Flow ceased 2016 after Line 9B reversal; 2008 reversal proposal (to export oil-sands crude) not implemented", PH, "https://www.ogj.com/pipelines-transportation/article/17267514/reversed-line-would-haul-canadian-oil-to-maine")]),
 ("tnpi", "Trans-Northern Pipeline (TNPI)", "products", "mtl", F("Trans-Northern Pipelines Inc. (Imperial, Shell, Suncor)", CERT), F("Refined products (gasoline, diesel, jet, heating fuel)", CERT), F("10-16 (Montreal-Farran's Point upgraded to 16-in 2004)", CERTN),
  F("Montreal-Farran's Pt 132 Mb/d; Nanticoke-Oakville 105 Mb/d; Belleville-N. Toronto 63 Mb/d", CERT), F("919 km (CER)", CERT), F("Nanticoke - Oakville - Toronto ... Kingston - Belleville - Ottawa - Cornwall - Montreal/Dorval", CERT), F(1952, CERT), F("Operating", CERT),
  [("osm_canada_pipelines", OP("trans-?northern|transnorthern"))], []),
 ("tqm", "Trans Québec & Maritimes (TQM)", "gas", "mtl", F("TQM Pipeline (TC Energy 50% / Énergir 50%), operated by TC Energy", TCQ, CERQ), F("Natural gas", CERQ), F(U),
  F("about 1.0 Bcf/d at Saint-Lazare & Sabrevois; 0.4 Bcf/d at East Hereford", CERQ), F("649 km operating (655 km CER-regulated)", TCQ, CERQ), F("TC Mainline at Saint-Lazare/Les Cèdres -> Lévis; Terrebonne -> East Hereford (PNGTS)", CERQ, TCQ), F(1982, CERQ, TCQ), F("Operating; supplies ~50% of Énergir's gas", TCQ),
  [("osm_canada_pipelines", OR(OP("trans-quebec|tqm"), NM("tqm|trans qu")))], []),
 ("tc_mainline_east", "TC Canadian Mainline (Ontario/Quebec segments)", "gas", "mtl", F("TransCanada PipeLines Ltd. (TC Energy)", CERML), F("Natural gas", CERML), F(U), F("Eastern Triangle 2015 capacity 5.2 Bcf/d; at Iroquois ~0.6 Bcf/d", "https://www.cer-rec.gc.ca/en/data-analysis/facilities-we-regulate/2016/group1-companies/natural-gas/canadas-pipeline-transportation-system-2016-transcanada-mainline.html", CERML),
  F("14,123 km total system (CER)", CERML), F("AB/SK border -> SK, MB, ON -> portion of Quebec; Eastern Triangle serves ON/QC/export", CERML), F(1958, CERML), F("Operating", CERML), [("osm_canada_pipelines", AND(OP("tc energy|transcanada"), lambda p: True))], []),
 ("mne", "Maritimes & Northeast Pipeline", "gas", "east", F("Maritimes & Northeast Pipeline (Enbridge-operated)", W("Maritimes_&_Northeast_Pipeline")), F("Natural gas", W("Maritimes_&_Northeast_Pipeline")), F(30, W("Maritimes_&_Northeast_Pipeline")), F(U), F("1,300 km mainline", W("Maritimes_&_Northeast_Pipeline")),
  F("Goldboro NS (former Sable Offshore gas plant) -> NB -> ME -> NH -> Dracut MA", W("Maritimes_&_Northeast_Pipeline")), F("1999 (US joint facilities in service March 1999)", "https://exa.ai/library/legal/opinion/0fq4drg8zvx"), F("Operating", W("Maritimes_&_Northeast_Pipeline")), [("us_natgas", OP("maritimes")), ("osm_canada_pipelines", OR(OP("maritimes"), NM("maritimes")))], []),
 ("pngts", "Portland Natural Gas Transmission System (PNGTS)", "gas", "east", F("PNGTS (standalone company since 2024; previously TC Energy / Énergir subsidiary)", PNG), F("Natural gas", PNG), F(U), F(U), F("295 mi", PNG), F("Near Pittsburg NH (TQM interconnect) -> ME -> shared facilities Westbrook-Dracut MA", PNG), F(1999, "https://exa.ai/library/legal/opinion/0fq4drg8zvx"), F("Operating", PNG), [("us_natgas", OP("portland natural|pngts"))], []),
 ("iroquois", "Iroquois Gas Transmission System", "gas", "east", F("Iroquois Gas Transmission System, L.P.", IRQ), F("Natural gas", IRQ), F("24 (Connecticut section)", "https://exa.ai/library/legal/opinion/mtjs80y05rb"), F("1.7 Bcf/d physical capability", IRQ), F("414 mi", IRQ),
  F("US-Canada border at Waddington NY (TC Energy) -> NY -> western CT -> Long Island Sound -> Commack NY; Huntington -> Bronx", IRQ), F("Dec 1991 / Jan 1992", IRQ, OGJI), F("Operating", IRQ), [("us_natgas", OP("iroquois"))], [F("Crosses Long Island Sound, St. Lawrence, Hudson and Housatonic rivers", "https://www.ogj.com/home/article/17238181/construction-under-way-on-iroquois-system")]),
 ("tennessee", "Tennessee Gas Pipeline", "gas", "east", F("Tennessee Gas Pipeline Co. (Kinder Morgan)", W("Tennessee_Gas_Pipeline")), F("Natural gas", W("Tennessee_Gas_Pipeline")), F("up to 32 (infobox)", W("Tennessee_Gas_Pipeline")), F(U), F("11,900 mi", W("Tennessee_Gas_Pipeline")), F("Texas-Louisiana Gulf Coast -> ... -> WV, NJ, NY, New England", W("Tennessee_Gas_Pipeline")), F(1943, W("Tennessee_Gas_Pipeline")), F("Operating", W("Tennessee_Gas_Pipeline")), [("us_natgas", OP("^tennessee gas"))], []),
 ("algonquin", "Algonquin Gas Transmission", "gas", "east", F("Algonquin Gas Transmission (Enbridge)", W("Algonquin_Gas_Transmission_Pipeline")), F("Natural gas", W("Algonquin_Gas_Transmission_Pipeline")), F(U), F("about 20 bcm per year", W("Algonquin_Gas_Transmission_Pipeline")), F("1,100 mi", W("Algonquin_Gas_Transmission_Pipeline")), F("Connects Texas Eastern and M&NE; delivers to New England", W("Algonquin_Gas_Transmission_Pipeline")), F(U), F("Operating", W("Algonquin_Gas_Transmission_Pipeline")), [("us_natgas", OP("algonquin"))], []),
 ("transco", "Transcontinental Gas Pipe Line (Transco)", "gas", "east", F("Williams Companies", W("Transcontinental_Pipeline")), F("Natural gas", W("Transcontinental_Pipeline")), F("up to 42 (infobox)", W("Transcontinental_Pipeline")), F(U), F("10,500 mi", W("Transcontinental_Pipeline")), F("Gulf Coast (TX, LA, MS, AL) -> GA, SC, NC, VA, MD, PA -> NJ / NYC / Long Island", W("Transcontinental_Pipeline")), F(1950, W("Transcontinental_Pipeline")), F("Operating", W("Transcontinental_Pipeline")), [("us_natgas", OP("transcontinental"))], []),
 ("texas_eastern", "Texas Eastern Transmission", "gas", "east", F("Enbridge Inc. (100%)", TE), F("Natural gas", TE), F(U), F("12.04 Bcf/d peak day; ~74 Bcf storage", TE), F("8,532 mi", TE), F("Texas / Gulf Coast -> northeastern US", TE), F(U), F("Operating", TE), [("us_natgas", OP("texas eastern"))], []),
 ("millennium", "Millennium Pipeline", "gas", "east", F("Millennium Pipeline Company, L.L.C.", FERCM), F("Natural gas", FERCM), F(U), F(U), F(U), F("Corning NY compressor station -> Ramapo NY (Algonquin interconnect), southern-tier NY", FERCM), F(U), F("Operating; 2016 Eastern System Upgrade (+223,000 Dth/d) filed at FERC", FERCM), [("us_natgas", OP("millennium"))], []),
 ("eastern_gas", "Eastern Gas Transmission & Storage (ex-Dominion Transmission)", "gas", "east", F("BHE GT&S (Berkshire Hathaway Energy) since Nov 1 2020; formerly Dominion / CNG", EGTS), F("Natural gas + storage", EGTS), F(U), F("9.5 Bcf/d delivery; 420 Bcf working gas storage", EGTSF), F("nearly 4,000 mi", EGTS), F("MD, NY, OH, PA, VA, WV", EGTS), F(U), F("Operating", EGTS), [("us_natgas", OP("dominion transmission"))], []),
 ("colonial", "Colonial Pipeline", "products", "east", F("Colonial Pipeline Company", W("Colonial_Pipeline")), F("Refined products", W("Colonial_Pipeline")), F(U), F("3 million bbl/d", W("Colonial_Pipeline")), F("5,500 mi (three tubes)", W("Colonial_Pipeline")), F("Texas -> New York Harbor (Linden NJ)", W("Colonial_Pipeline")), F("1962 construction start (company founded 1961)", W("Colonial_Pipeline")), F("Operating", W("Colonial_Pipeline")), [("us_products", OP("colonial"))], [F("May 2021 ransomware attack shut the pipeline (see source)", W("Colonial_Pipeline"))]),
 ("buckeye", "Buckeye Pipe Line system", "products", "east", F("Buckeye Partners", W("Buckeye_Partners")), F("Refined products / HGL", W("Buckeye_Partners")), F(U), F(U), F(U), F("East & Midwest US (NY Harbor, PA, NY, CT, ME ...)", W("Buckeye_Partners")), F(U), F("Operating", W("Buckeye_Partners")), [("us_products", AND(OP("buckeye"), NM("^buckeye$|connecticut|portland"))), ("us_hgl", OP("buckeye"))], []),
 ("laurel", "Laurel Pipe Line", "products", "east", F("Laurel Pipe Line Company (Buckeye affiliate)", LAU), F("Refined products", LAU), F("12-24", LAU), F(U), F("about 350 mi", LAU, LAU2), F("Philadelphia area -> west across PA -> west of Pittsburgh", LAU2), F("1957 PUC certificate", LAU2), F("Operating; 2016-18 partial westward reversal (Broadway II) contested", LAU, LAU2), [("us_products", NM("laurel"))], []),
]
for (lid, name, com, region, op, prod, dia, cap, length, rt, ins, st, rules, inc) in EAST:
    m = multi(rules)
    lines.append(dict(id=lid, name=name, kind="pipeline", region=region, commodity=com, operator=op, product=prod, diameter_in=dia, capacity=cap, cap_num=None, cap_unit=None, length=length, route=rt, endpoints=None, in_service=ins, status=st, incidents=inc,
        waypoints=[], geometry={"type": "MultiLineString", "coordinates": m["multi"]} if m["multi"] else None,
        route_accuracy=dict(level=("EIA (~300 m simplified)" if all(d.startswith("us_") for d in m["datasets"]) else "OSM" if all(d.startswith("osm") for d in m["datasets"]) else "EIA + OSM") if m["multi"] else "not drawn (no open geometry matched)", note=f"{m['n_segments']} operator-matched segments; US geometry from EIA, Canadian from OSM where tagged.", datasets=m["datasets"], sources=sorted({EIA if d.startswith("us_") else OSMS for d in m["datasets"]}))))
    print(f"{lid:18s} segs={m['n_segments']} {m['datasets']}")

# ---- merge fragmented segments ----
from shapely.geometry import MultiLineString, LineString
from shapely.ops import linemerge
for l in lines:
    g = l.get("geometry")
    if g and g["type"] == "MultiLineString":
        m = linemerge(MultiLineString([c for c in g["coordinates"] if len(c) > 1])).simplify(0.002)
        parts = [list(m.coords)] if m.geom_type == "LineString" else [list(p.coords) for p in m.geoms]
        g["coordinates"] = [[[round(x, 5), round(y, 5)] for x, y in p] for p in parts if len(p) > 1]
        if "segments" in l["route_accuracy"].get("note", ""): l["route_accuracy"]["note"] = re.sub(r"^\d+ operator-matched segments", f"Operator-matched EIA/OSM segments merged into {len(g['coordinates'])} parts", l["route_accuracy"]["note"])
    elif g:
        g["coordinates"] = [[round(x, 5), round(y, 5)] for x, y in LineString(g["coordinates"]).simplify(0.0005).coords]
tm = next(l for l in lines if l["id"] == "tc_mainline_east"); tm["geometry"]["coordinates"] = [c for c in tm["geometry"]["coordinates"] if min(x for x, y in c) > -84.6]
tm["route_accuracy"]["note"] += " Filtered to segments east of Sault Ste. Marie (lon > -84.6)."
# Portland-Montreal Canadian leg: no open geometry -> approximate
pm = next(l for l in lines if l["id"] == "portland_montreal")
pm["geometry"]["coordinates"].append([[-72.25, 45.01], [-72.6, 45.2], [-73.1, 45.4], [-73.35, 45.55], [-73.5245, 45.6438]])
pm["route_accuracy"].update(level="EIA (US) + approximate (Canada)", note="US segment from EIA crude layer (South Portland ME to the border). Canadian 232-km segment (border near Highwater QC to Montreal East) has no open geometry: drawn as approximate land via-points, unsourced intermediate points.")
# ---- facilities ----
OSMN = lambda kind, i: f"https://www.openstreetmap.org/{kind}/{i}"
DEP = json.load(open("data/ref/osm_depots_raw.json")); TIL = json.load(open("data/ref/osm_tiles_raw.json"))
_have = {i["osm"] for i in DEP["items"]}; DEP["items"] += [i for i in TIL["items"] if i["osm"] not in _have]
def osm_at(name):
    for i in DEP["items"]:
        if (i["tags"].get("name") or "") == name: return i
facs = []
for f in OLD["facilities"]:
    f = dict(f); f["region"] = "swo"; f["lat"], f["lon"] = f["waypoints"][0][0], f["waypoints"][0][1]; f["pos_source"] = "approximate: named town/place"
    o = {"suncor": "Suncor Sarnia Refinery", "shell": "Shell Corunna Refinery"}.get(f["id"]) and osm_at({"suncor": "Suncor Sarnia Refinery", "shell": "Shell Corunna Refinery"}[f["id"]])
    if o: f["lat"], f["lon"], f["pos_source"] = o["lat"], o["lon"], "OSM " + o["osm"]
    facs.append(f)
def fac(id, name, kind, region, lat, lon, pos, op, years, cap, status, use=None, hist=None, src=(), **kw):
    d = dict(id=id, name=name, kind=kind, region=region, lat=lat, lon=lon, pos_source=pos, operator=F(op, *src), capacity=F(cap, *src) if cap else F(U), status=F(status, *src), years=F(years, *src))
    if use: d["current_use"] = F(use, *src)
    if hist: d["operator_history"] = F(hist, *src)
    d.update(kw); facs.append(d)
SO = W("Oakville_Refinery_(Shell_Canada)"); PO = W("Oakville_Refinery_(Petro-Canada)"); GM = "https://www.theglobeandmail.com/report-on-business/petro-canada-to-shut-oakville-refinery/article1166063/"
PC1 = "https://surpluspr.org/wp-content/uploads/2023/02/Imperial-Oil-Port-Credit-Divestment_Public-1.pdf"; PC2 = "https://www.mississauga.ca/projects-and-strategies/city-projects/inspiration-port-credit/"
CL = "https://heritagemississauga.com/business/clarkson-refinery/"
fac("shell_oakville", "Shell Oakville refinery (former)", "refinery_decom", "swo", 43.3816, -79.7220, "Wikipedia infobox coordinates", "Shell Canada", "1953-1983", "44,000 bbl/d", "Closed 1983", "Redeveloped: residential and parkland", "Shell Canada throughout", (SO,))
fac("pc_oakville", "Petro-Canada Oakville refinery (former; now terminal)", "refinery_decom", "swo", 43.4720, -79.6720, "approximate: Wikipedia infobox / OSM area of Petro-Canada Oakville terminal (verify)", "Petro-Canada (Suncor)", "1958-2005", "90,000 bbl/d", "Refining closed 2005", "Fuel products terminal", "Cities Service 1958 -> BP 1963 -> Petro-Canada", (PO, GM))
fac("port_credit", "Port Credit refinery (former Texaco/Imperial)", "refinery_decom", "swo", 43.5464, -79.5867, "site address 70 Mississauga Rd S (sale document)", "Imperial Oil (owner of site)", "1933-1978 refining; chemical plant to 1985", None, "Refining ceased 1978; demolished 1985-1990", "Sold 2017 to Port Credit West Village Partners for mixed-use redevelopment", "Lloyd 1933-44 -> Goodrich -> Texaco Canada 1960-1990 -> Imperial Oil", (PC1, PC2))
fac("clarkson", "Clarkson refinery (Mississauga)", "refinery", "swo", 43.503493, -79.612619, "OSM https://www.openstreetmap.org/" + next(i["osm"].split("org/")[1] for i in DEP["items"] if i["tags"].get("name") == "Petro-Canada Lubricants") + " (Petro-Canada Lubricants); address 2310 Lakeshore Rd W", "HF Sinclair (Petro-Canada Lubricants)", "1943-present", None, "Operating as lubricants plant since 1993; base-oil refining retirement planned by 2027", None, "British American 1943 -> Gulf 1969 -> Petro-Canada 1985 -> HF Sinclair", (CL, "https://www.insauga.com/hf-sinclair-to-end-base-oil-production-at-mississauga-refinery/"))
fac("nanticoke", "Imperial Oil Nanticoke refinery", "refinery", "swo", 42.835524, -80.047771, "approximate: unnamed OSM industrial=oil area near Nanticoke " + next(i["osm"] for i in DEP["items"] if abs(i["lat"] - 42.835524) < 1e-5) + " (not confirmed as the refinery)", "Imperial Oil", "1978-present", "112,000 bbl/d", "Operating; TNPI origin (Nanticoke-Oakville)", src=(W("Nanticoke_Refinery"), "https://www.imperialoil.ca/company/operations/nanticoke", CERT))
MR = W("Montreal_Refinery"); SME = W("Shell_Montreal_East_Refinery"); GME = W("Montreal_East_Refinery_(Gulf_Oil_Canada)")
fac("suncor_mtl", "Suncor Montreal refinery", "refinery", "mtl", 45.6438, -73.5224, "Wikipedia infobox coordinates", "Suncor Energy", "1955-present", "137,000 bbl/d", "Operating; receives Line 9 crude", None, "Petrofina 1955 -> Petro-Canada -> Suncor", (MR,))
fac("shell_mtl", "Shell Montreal East refinery (former; now terminal)", "refinery_decom", "mtl", 45.62528, -73.53028, "Wikipedia infobox coordinates", "Shell Canada", "1933-2010", "161,000 bbl/d", "Closed October 2010", "Shell fuel terminal", None, (SME,))
fac("gulf_mtl", "Gulf / BA Montreal East refinery (former)", "refinery_decom", "mtl", 45.63369, -73.52261, "Wikipedia infobox coordinates", "Gulf Oil Canada / Petro-Canada", U, None, "Refining closed 1983; site re-used by Petro-Canada (restart 2003 per source)", None, "British American -> Gulf Canada -> Petro-Canada", (GME,))
fac("texaco_mtl", "Texaco Montreal East refinery (former)", "refinery_decom", "mtl", 45.6300, -73.5050, "approximate: Montreal-Est municipality (site coordinates unknown)", "Texaco Canada", "1917?-1982/83 (sources differ)", None, "Closed Oct 1982 (UPI) / 1983 (Assemblée nationale notice)", U, None, ("https://www.upi.com/Archives/1982/08/24/Texaco-Canada-to-close-Montreal-refinery/", "https://www.assnat.qc.ca/"))
fac("imperial_mtl", "Imperial Oil Montreal East refinery (former)", "refinery_decom", "mtl", 45.6250, -73.5150, "approximate: Montreal-Est municipality (site coordinates unknown)", "Imperial Oil", U, None, "Closed 1983 or 1985 (sources inconsistent)", U, None, ("https://www.nytimes.com/1983/10/27/business/imperial-to-close-montreal-refinery.html",))
for id, n, lat, lon, cap, src in [("bayway", "Phillips 66 Bayway refinery (Linden NJ)", 40.637, -74.214, "238,000 bbl/d", W("Bayway_Refinery")), ("delcity", "PBF Delaware City refinery", 39.5809, -75.6309, "210,000 bbl/d", W("Delaware_City_Refinery")),
    ("trainer", "Monroe Energy Trainer refinery (PA)", 39.8222, -75.4044, "185,000 bbl/d", W("Trainer_Refinery")), ("paulsboro", "PBF Paulsboro refinery (NJ)", 39.8390, -75.2550, "155,000 bbl/d", "https://www.pbfenergy.com/refineries/"),
    ("irving", "Irving Oil refinery (Saint John NB)", 45.2789, -66.0125, "320,000 bbl/d", W("Irving_Oil_Refinery"))]:
    fac(id, n, "refinery", "east", lat, lon, "approximate: Paulsboro town/site location" if id == "paulsboro" else "Wikipedia infobox coordinates", n.split(" ")[0] if id != "irving" else "Irving Oil", U, cap, "Operating", src=(src,))
fac("pes", "Philadelphia Energy Solutions refinery (former; Point Breeze / Girard Point)", "refinery_decom", "east", 39.9032, -75.2089, "Wikipedia coordinates", "Philadelphia Energy Solutions", "closed 2019", "335,000 bbl/d", "Closed after June 2019 explosion and fire", "Being redeveloped as a logistics/life-science campus (Bellwether District) by HRP", None, (W("2019_Philadelphia_refinery_explosion"), "https://www.puc.pa.gov/pcdocs/1559771.pdf"))
fac("nyh_linden", "New York Harbor terminal hub (Linden NJ; Colonial/Buckeye)", "terminal", "east", 40.62, -74.22, "approximate: Linden NJ (Colonial terminus per source)", "multiple (Colonial, Buckeye, Kinder Morgan ...)", U, None, "Operating", src=(W("Colonial_Pipeline"), LAU))
fac("so_portland", "South Portland ME crude terminal (Portland-Montreal)", "terminal", "east", 43.6400, -70.2500, "approximate: South Portland ME", "Portland Pipe Line Corp.", "1941-", None, "Largely idle since 2016", src=(W("Portland–Montreal_pipeline"), PH))
# OSM oil depots / terminals
OILK = {"substation", "industrial", "port", "oil", "oil_storage", "oil_tank_farm", "oil_depot", "refinery", "natural_gas;refinery", "fuel"}
seen = {(round(f["lat"], 3), round(f["lon"], 3)) for f in facs}; stations_new = []
for i in DEP["items"]:
    t = i["tags"]; k = t.get("industrial") or t.get("landuse") or ("substation" if t.get("pipeline") == "substation" else None) or t.get("man_made"); n = t.get("name") or ""
    if k not in OILK or (i["osm"] == next(x["osm"] for x in DEP["items"] if abs(x["lat"] - 42.835524) < 1e-5)) or n == "Petro-Canada Lubricants" or n in ("contaminated soil",) or "Ethanol" in n or n in ("Suncor Sarnia Refinery", "Shell Corunna Refinery"): continue
    pos = "OSM " + i["osm"]; src = [i["osm"]]
    if k in ("substation",) and (t.get("operator") or n) or n in ("Enbridge Gas Keele/CNR Station",):
        stations_new.append(dict(name=(n or (t.get("operator") + " pipeline facility")) + " (OSM pipeline=substation)" if k == "substation" else n + " (OSM)", type="compressor" if "Compressor" in n else "meter" if "Meter" in n or "Enbridge Gas" in n or not t.get("substance") else "compressor" if t.get("substance") == "gas" else "pump", lat=i["lat"], lon=i["lon"], coord_note="OSM facility location", operator=t.get("operator") or "per OSM name", substance=t.get("substance") or "unknown", sources=src)); continue
    if k == "substation": continue
    if k in ("industrial", "port") and not re.search(r"Terminal|Depot", n) or re.search(r"Grain|Cement|Nicholson|Marine Terminal$", n) and "Michigan" not in n: continue
    if k in ("industrial", "port") and not re.search(r"Shell|Suncor|Valero|Petroleum|Fuel|Oil", n + " " + (t.get("operator") or "")): continue
    if re.search(r"Station|Junction|Pumping", n) or (t.get("operator") == "Enbridge" and not n):
        stations_new.append(dict(name=(n or "Enbridge oil facility (unnamed in OSM)") + " (OSM)", type="pump", lat=i["lat"], lon=i["lon"], coord_note="OSM facility location", operator=t.get("operator") or "per OSM name", sources=src)); continue
    if (round(i["lat"], 3), round(i["lon"], 3)) in seen: continue
    region = "mtl" if i["lon"] > -75 else "swo"
    kind = "refinery" if "refinery" in k or "Refin" in n else "terminal"
    facs.append(dict(id="osm_" + i["osm"].split("/")[-1], name=n or f"Oil facility (unnamed, OSM industrial={k})", kind=kind, region=region, lat=i["lat"], lon=i["lon"], pos_source=pos, operator=F(t.get("operator") or U, *src), status=F("mapped in OSM (status not verified)", *src), osm_tags={x: t[x] for x in t if x in ("industrial", "landuse", "operator", "name", "product")}))
# stations: keep v0.2 (approx), add OSM-sited ones
stations = OLD["stations"] + stations_new
for s in OLD["stations"]:
    if s["name"].startswith("Dawn"): s["coord_note"] = "approximate: Dawn Township place coordinates (no OSM facility found in fetched data)"
out = dict(OLD); out.update(version="0.3", generated=__import__("datetime").date.today().isoformat(), lines=lines, facilities=facs, stations=stations,
    coord_note="v0.3: line geometry from OSM/EIA operator matches where available (see route_accuracy per line); otherwise approximate land via-points. Facility positions: pos_source per item.",
    water_audit=json.load(open("data/water_audit.json")) if __import__("os").path.exists("data/water_audit.json") else None)
srcs = set(OLD["sources"])
def walk(o):
    if isinstance(o, dict):
        for k, v in o.items():
            if k == "sources" and isinstance(v, list): srcs.update(x for x in v if isinstance(x, str) and x.startswith("http"))
            else: walk(v)
    elif isinstance(o, list): [walk(x) for x in o]
walk(out); out["sources"] = sorted(srcs)
json.dump(out, open("data/swo.json", "w"), ensure_ascii=False)
print("lines", len(lines), "facs", len(facs), "stations", len(stations), "sources", len(srcs), "MB", round(len(json.dumps(out)) / 1e6, 2))
from collections import Counter; print(Counter((f["region"], f["kind"]) for f in facs))
