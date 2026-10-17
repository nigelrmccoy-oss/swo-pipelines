# SWO-PIPELINES v0.3.1: North American oil & gas pipelines, SW Ontario, Montreal & Eastern Seaboard detail

Interactive 3D globe (CesiumJS, vendored, **no API keys**) with high-detail terrain (AWS Terrain Tiles) under Esri World Imagery.
Same style as `wr-water`: no build step, vanilla ES modules, vendored libs, dark control-panel UI. **Unofficial**; uses public data only.

## Run
```bash
python3 tools/serve.py 8770        # http://127.0.0.1:8770/  (localhost only; Ctrl-C to stop)
npm install && npm test            # headless tests (or set PW=/path/to/node_modules/playwright)
```

## What's modelled
- **Continental layers** (GeoJSON in `data/gis`, each with `source_url`): EIA US crude, HGL, products and natural-gas pipelines (via the DOE/NETL-hosted EIA FeatureServer); OSM Canada pipelines; detailed OSM SW Ontario/Michigan pipelines; NACEI border crossings. Mexico is not covered (the OSM fetch failed with Overpass 504s; see `docs/datasets.md`).
- **Researched lines** (`data/swo.json`): 32 lines, 60 facilities, 37 stations and 27 crossings, with 150 distinct source URLs. Every attribute carries its sources; unknowns are marked unknown. Click a line for operator, product, diameter, capacity, in-service year, status, incidents, route accuracy and sources.
- **Sim**: animated flow dots (only on lines with sourced geometry; never on approximate, endpoints-only or replaced lines) in the nominal, source-described direction, with density and speed proportional to sourced capacity. A **Line 5 shut** scenario updates the Sarnia crude-capacity KPI (nameplate arithmetic only).
- **Toggles** by product and point type, a **search** box, and fly-to quick views.
- **Optional private "My home" layer**: if `data/private/home.json` exists (gitignored, never published), the app shows a schematic gas supply path to a house and a usage panel. Without that file, or with `?nohome`, the layer, its button and its KPI are hidden. No home data is in this repository.

## v0.3.1
- **Line 78 / 6B fixed**: they no longer run on past Sarnia along Line 9A or a 206 km straight chord. Matching is now restricted by name and to the west side of the St. Clair River, with a per-leg corridor and detour check (`tools/route_match.py`). Both end at Sarnia (drawn 630 km and 488 km). Line 6B is drawn faded and thin as "replaced", with no flow, and clicks prefer the in-service line.
- **Line 7 corrected**: the v0.3 solid Sarnia-London line with flow was invented. It is now Sarnia Terminal → Westover (Enbridge factsheet, CER): 20 in (508 mm), 193 km, 180,000 bbl/d. **Line 11** has been added: Westover → Nanticoke, 16-20 in (406-508 mm), 76 km, 117,000 bbl/d. Their routes are not in open data, so each is drawn as a dashed **endpoints-only** link with no flow. That link is not the route.
- **Route accuracy computed from geometry**: each line now records drawn km, stated km, longest straight run, and km in straight runs over 25 km. "partial" is used when coverage or straight runs are poor. Straight runs over 25 km (EIA's schematic liquids layer, approximate legs) are drawn dashed.
- **Units**: metric throughout (km, m, mm, kW, million m³/d), with the original units in brackets; "converted" marks derived gas volumes. Oil capacity stays in bbl/d. Estimates are labelled as estimates.
- **Safety**: no valve or block-valve sites are named or located; intermediate points on approximate routes are towns or areas only.
- **App**:
  - Deep links (`#view=`, `#open=`, `#l5off=1`) now work on a fresh load.
  - The tour ends with every filter on.
  - Search is ranked (exact > word-prefix > all words > substring), shows a message when nothing matches, and does nothing on an empty query. Picking an operator no longer moves the view.
  - The legend is collapsible and only lists "My home" when that layer exists.
  - Popup content is escaped, and missing fields are guarded.
  - The private home file is only requested from localhost.
  - Mobile layout.
- **Tooling**: `tools/serve.py` (localhost only; refuses `/data/private/` to non-local Host headers and refuses dot-paths); `package.json`; portable tests including `tests/deeplink.mjs`; `python3 tools/shoot_tour.py [prefix]` (uses `?nohome`).

## v0.3
- **Real geometry**: researched lines use OSM/EIA operator/name-matched geometry chained between via-points (`tools/route_match.py`, `tools/build_routes.py`); each line has `route_accuracy` (OSM / EIA / partial / approximate / unknown, matched share, datasets, sources). Approximate lines are dashed.
- **Lake audit** (`tools/water_audit.py`, Natural Earth 10m lakes): no pipeline crosses Lake Ontario; wrong v0.2 crossings of Ontario, Erie and Michigan removed. Only the real Straits of Mackinac crossings remain. See `docs/v03.md`.
- **Depots/terminals** (OSM, `tools/fetch_tiles_osm.py`) and **decommissioned refineries** (Shell Oakville, Petro-Canada Oakville, Port Credit/Texaco, Shell/Gulf/Texaco/Imperial Montreal East, PES Philadelphia) with operator history, years, closure and current use. These have their own grey/red ⊘ style and a toggle.
- **Montreal** (Line 9B, TNPI, TQM, TC Mainline, Portland-Montreal, Suncor) and **Eastern Seaboard** (M&NE, PNGTS, Iroquois, Tennessee, Algonquin, Transco, Texas Eastern, Millennium, Eastern Gas, Colonial, Buckeye, Laurel; Bayway, Delaware City, Trainer, Paulsboro, Irving), with quick views for Lake Ontario, Montreal and E. Seaboard.
- QA: `node tests/smoke.mjs`; `node tests/nohome_check.mjs` (loads with no private home file); on-display tour `python3 tools/shoot_tour.py [prefix]` (opens `?nohome#tour` in Firefox and saves screenshots to `shots/`, which is gitignored). A URL hash such as `#view=mtl` or `#open=Enbridge Line 9` flies to a view or opens a popup.
- Build: `tools/.venv/bin/python tools/build_v03.py && python3 tools/build_docs_v03.py`.
Tools: `tools/fetch_eia.py`, `tools/fetch_other.py`, `tools/fetch_swo_osm.py`, `tools/augment.py`, `tools/build_research.py`. Docs: `docs/research.md`, `docs/datasets.md`.

## Data sources, licenses and attribution
Unofficial and for information only; not for navigation, excavation or safety decisions. Routes are approximations of public data, not surveyed alignments. Call before you dig (Ontario One Call, 811 in the US).

| Source | Used for | Terms |
|---|---|---|
| U.S. EIA energy infrastructure layers via [DOE/NETL ArcGIS](https://arcgis.netl.doe.gov/server/rest/services/Hosted/EIA_pipeline_data/FeatureServer) | US crude, HGL, products and gas pipelines | U.S. Government work, public domain ([EIA copyright](https://www.eia.gov/about/copyrights_reuse.php)) |
| © [OpenStreetMap](https://www.openstreetmap.org/copyright) contributors, via the Overpass API and Nominatim | Canadian and SW Ontario pipelines, terminals, depots, stations | [ODbL 1.0](https://opendatacommons.org/licenses/odbl/). Derived data in `data/gis/osm_*`, `data/ref/osm_*` and the OSM-derived geometry in `data/swo.json` / `data/routes_raw.json` is released under ODbL |
| [NACEI](https://geoappext.nrcan.gc.ca/arcgis/rest/services/NACEI/energy_infrastructure_of_north_america_en/MapServer) (Natural Resources Canada) | Border-crossing pipelines | [Open Government Licence – Canada](https://open.canada.ca/en/open-government-licence-canada) |
| [Natural Earth](https://www.naturalearthdata.com/) 10m lakes | Lake-crossing audit (`data/ref/ne_10m_lakes.*`) | Public domain |
| Canada Energy Regulator, FERC, OEB, company and Wikipedia pages | Researched attributes (URLs per fact in `data/swo.json`) | Facts are cited, not copied. Wikipedia text is CC BY-SA; `research/wiki/*.json` caches page extracts with their URLs |
| [Esri World Imagery](https://www.arcgis.com/home/item.html?id=10df2279f9684e4a9f6a7f08febac2a4) | Satellite basemap tiles, streamed at runtime (none are stored here) | Esri terms of use; attribution shown in the app (Esri, Maxar, Earthstar Geographics, GIS User Community) |
| [AWS Terrain Tiles](https://registry.opendata.aws/terrain-tiles/) (Terrarium) | 3D terrain, streamed at runtime | See the registry page for source attributions (SRTM, USGS, GMTED and others) |
| [CesiumJS](https://cesium.com/platform/cesiumjs/) 1.138.0, vendored in `vendor/cesium` | 3D globe | Apache-2.0 (`vendor/cesium-LICENSE.md`). No Cesium ion token is used |

The code (`js/`, `css/`, `tools/`, `tests/`, `index.html`) is MIT licensed; see `LICENSE`. Third-party data keeps its own license as listed above. Vendored CesiumJS is Apache-2.0, and OpenStreetMap-derived data is ODbL 1.0.
