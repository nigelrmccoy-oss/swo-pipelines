"""v0.4 wells layer: pull PUBLIC well records and pack them compactly (data/wells/*.bin + wells.json).
Sources (all open, no login):
  on  - Ontario Petroleum Well (Ontario Petroleum Data System / Oil, Gas and Salt Resources Library), LIO_Open08 MapServer/22, Open Government Licence - Ontario
  mi  - Michigan EGLE Oil, Gas and Mineral Well surface-hole locations, GrmdOpenData MapServer/10
  eia - EIA/NETL OilGasInfrastructure FeatureServer layers 17 (oil wells) + 18 (gas wells), clipped to OH, PA, NY (type + county only)
Record layout (16 bytes, little endian): i32 lon*1e5, i32 lat*1e5, u32 id, u8 type-index, u8 status-index, u16 operator-index.
Never-drilled records (Ontario 'Not Drilled'/'No Well Found'/'Potential'; Michigan 'Terminated Permit'/'Location') are skipped and counted in wells.json.
Raw pages are cached under data/ref/wells_raw/ (gitignored)."""
import json, os, struct, sys, time, urllib.parse, urllib.request, datetime
OUT = "data/wells"; RAW = "data/ref/wells_raw"
os.makedirs(OUT, exist_ok=True); os.makedirs(RAW, exist_ok=True)
TODAY = datetime.date.today().isoformat()
UA = {"User-Agent": "swo-pipelines/0.4 (personal research)"}
def get(url, params, tries=5):
    for k in range(tries):
        try:
            req = urllib.request.Request(url + "?" + urllib.parse.urlencode(params), headers=UA)
            return json.load(urllib.request.urlopen(req, timeout=120))
        except Exception as e:
            print("retry", url[-40:], e, file=sys.stderr); time.sleep(5 * (k + 1))
    raise SystemExit("FAILED " + url)
def pages(url, where, fields, page=2000, cache=None, geom=True):
    if cache and os.path.exists(cache): return json.load(open(cache))
    n = get(url + "/query", {"where": where, "returnCountOnly": "true", "f": "json"})["count"]
    rows = []; off = 0
    while off < n:
        d = get(url + "/query", {"where": where, "outFields": fields, "outSR": 4326, "returnGeometry": "true" if geom else "false", "orderByFields": "OBJECTID", "resultOffset": off, "resultRecordCount": page, "f": "json"})
        fs = d.get("features", [])
        if not fs: break
        rows += [{"a": f["attributes"], "g": f.get("geometry")} for f in fs]; off += len(fs)
    print(url[-30:], "expected", n, "got", len(rows)); 
    if cache: json.dump(rows, open(cache, "w"))
    return rows
# ---- classification (type -> class: 0 oil,1 gas,2 oil+gas/condensate,3 storage,4 injection/disposal/brine,5 dry/test/observation/other)
def tclass(t):
    s = (t or "").lower()
    if "storage" in s or "cavern" in s or "compressed air" in s: return 3
    if "inject" in s or "disposal" in s or "brine" in s or "solution" in s or "co2" in s: return 4
    if ("oil" in s and "gas" in s and "show" not in s) or "condensate" in s: return 2
    if "natural gas well" in s or s.startswith("gas well") or s in ("gas well", "private gas well", "gas production and brine disposal well", "gas show"): return 1
    if s in ("oil well", "historical oil well", "oil show") or "oil well" in s: return 0
    return 5
# status -> class: 0 active/producing,1 inactive,2 plugged/abandoned,3 permitted/drilling,4 orphan,5 unknown
def sclass(t):
    s = (t or "").lower()
    if s in ("active well", "active", "producing", "water supply", "well completed", "drilling completed") : return 0
    if any(k in s for k in ("suspend", "shut", "capped", "temporarily", "injection suspended")): return 1
    if any(k in s for k in ("plug", "abandon", "junked", "whipstock")): return 2
    if any(k in s for k in ("permit", "licensed", "drilling", "sump")): return 3
    if "orphan" in s: return 4
    return 5
class Reg:
    def __init__(s): s.t = {}; s.s = {}; s.o = {"": 0}; s.rec = []; s.names = []
    def idx(s, d, k):
        if k not in d: d[k] = len(d)
        return d[k]
    def add(s, lon, lat, id_, typ, st, op, name=None):
        ti = s.idx(s.t, typ or "Unknown"); si = s.idx(s.s, st or "Unknown")
        oi = 0
        if op:
            op = " ".join(op.split())
            if op not in s.o: s.o[op] = len(s.o)
            oi = s.o[op]
        s.rec.append(struct.pack("<iiIBBH", round(lon * 1e5), round(lat * 1e5), id_ if 0 <= id_ < 2**32 else 0, ti, si, min(oi, 65535)))
        if name is not None: s.names.append(name)
    def dump(s, key, meta):
        open(f"{OUT}/{key}.bin", "wb").write(b"".join(s.rec))
        m = dict(meta); m.update({"id": key, "file": f"{key}.bin", "n": len(s.rec), "types": [[k, tclass(k)] for k, _ in sorted(s.t.items(), key=lambda x: x[1])],
            "statuses": [[k, sclass(k)] for k, _ in sorted(s.s.items(), key=lambda x: x[1])], "operators": [k for k, _ in sorted(s.o.items(), key=lambda x: x[1])]})
        if s.names: json.dump(s.names, open(f"{OUT}/{key}.names.json", "w"), separators=(",", ":")); m["names_file"] = f"{key}.names.json"
        return m
manifest = {"version": "0.4.0", "retrieved": TODAY, "record_bytes": 16, "scale": 1e5, "regions": [], "skipped": {}}
# ---- Ontario
ON = "https://ws.lioservices.lrc.gov.on.ca/arcgis2/rest/services/LIO_OPEN_DATA/LIO_Open08/MapServer/22"
rows = pages(ON, "1=1", "WELL_ID,WELL_NAME,OPERATOR,WELL_TYPE,WELL_MODE,OFFSHORE_BLOCK,COUNTY,SURFACE_LATITUDE_83,SURFACE_LONGITUDE_83", cache=f"{RAW}/on.json")
r = Reg(); skip = 0; off = 0
for w in rows:
    a = w["a"]; g = w["g"]
    if a["WELL_MODE"] in ("Not Drilled", "No Well Found", "Potential") or not g or g.get("x") is None: skip += 1; continue
    if a.get("OFFSHORE_BLOCK"): off += 1
    try: wid = int(a["WELL_ID"])
    except Exception: wid = 0
    r.add(g["x"], g["y"], wid, a["WELL_TYPE"], a["WELL_MODE"], a["OPERATOR"], (a.get("WELL_NAME") or "") + ("" if not a.get("OFFSHORE_BLOCK") else f" [offshore block {a['OFFSHORE_BLOCK']}]"))
manifest["regions"].append(r.dump("on", {"name": "Ontario", "source": "Ontario Petroleum Well - Ontario Petroleum Data System / Oil, Gas and Salt Resources Library (Ontario Ministry of Natural Resources), via Land Information Ontario",
    "url": "https://www.ontario.ca/page/oil-gas-and-salt-resources-library", "service": ON, "license": "Open Government Licence - Ontario", "has_operator": True, "offshore": off, "id_label": "Well ID"})); manifest["skipped"]["on"] = skip
# ---- Michigan
MI = "https://gisagoegle.state.mi.us/arcgis/rest/services/EGLE/GrmdOpenData/MapServer/10"
rows = pages(MI, "1=1", "WellID,api_num,CompanyName,WellType,WellStatus", cache=f"{RAW}/mi.json")
r = Reg(); skip = 0
for w in rows:
    a = w["a"]; g = w["g"]
    if a["WellStatus"] in ("Terminated Permit",) or a["WellType"] in ("Location",) or not g or g.get("x") is None: skip += 1; continue
    try: wid = int(a["WellID"])
    except Exception: wid = 0
    r.add(g["x"], g["y"], wid, a["WellType"], a["WellStatus"], a["CompanyName"])
manifest["regions"].append(r.dump("mi", {"name": "Michigan", "source": "Michigan EGLE Oil, Gas and Mineral Well surface-hole locations (EGLE Geological Resources Management Division open data)",
    "url": "https://www.michigan.gov/egle/about/organization/oil-gas-and-minerals", "service": MI, "license": "State of Michigan open data (public records; see EGLE terms)", "has_operator": True, "id_label": "EGLE Well ID"})); manifest["skipped"]["mi"] = skip
# ---- EIA (OH, PA, NY): type + county only
EIA = "https://services7.arcgis.com/p4qwkH3IF5hxHqd7/ArcGIS/rest/services/OilGasInfrastructure/FeatureServer"
r = Reg(); 
for lay, tn in ((17, "Oil well"), (18, "Gas well")):
    rows = pages(f"{EIA}/{lay}", "state IN ('OH','PA','NY')", "OBJECTID,state,countynm,welltype", cache=f"{RAW}/eia{lay}.json")
    for w in rows:
        g = w["g"]
        if not g or g.get("x") is None: continue
        r.add(g["x"], g["y"], w["a"]["OBJECTID"], tn, "Status not in source", w["a"]["state"] + " / " + (w["a"]["countynm"] or "").title())
manifest["regions"].append(r.dump("eia", {"name": "Ohio, Pennsylvania, New York (EIA/NETL)", "source": "U.S. EIA / NETL Oil & Gas Infrastructure - oil wells (layer 17) and gas wells (layer 18); location + well type + county only",
    "url": "https://atlas.eia.gov/", "service": EIA, "license": "US Government public domain (EIA/NETL)", "has_operator": False, "operator_is_county": True, "id_label": "EIA object ID"}))
json.dump(manifest, open(f"{OUT}/wells.json", "w"), indent=0)
print({m["id"]: m["n"] for m in manifest["regions"]}, manifest["skipped"])
