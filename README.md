# SWO-PIPELINES v0.3: North American oil & gas pipelines, SW Ontario, Montreal & Eastern Seaboard detail

Interactive 3D globe (CesiumJS, vendored, **no API keys**) with high-detail terrain (AWS Terrain Tiles) under Esri World Imagery.
Same style as `wr-water`: no build step, vanilla ES modules, vendored libs, dark control-panel UI. **Unofficial**; uses public data only.

## Run
```bash
cd ~/swo-pipelines && python3 -m http.server 8770 --bind 127.0.0.1   # http://localhost:8770/
node tests/smoke.mjs                                                  # headless smoke test (playwright from ~/qa-2026-10-08/pw)
```

## What's modelled
- **Continental layers** (GeoJSON in `data/gis`, each with `source_url`): EIA US crude, HGL, products and natural-gas pipelines (via the DOE/NETL-hosted EIA FeatureServer); OSM Canada pipelines; detailed OSM SW Ontario/Michigan pipelines; NACEI border crossings. The Mexico OSM fetch failed (Overpass 504s); see `docs/datasets.md`.
- **Researched lines** (`data/swo.json`): 31 lines, 60 facilities, 37 stations and 27 crossings, with 147 distinct source URLs. Every attribute carries its sources; unknowns are marked unknown. Click a line for operator, product, diameter, capacity, in-service year, status, incidents, route accuracy and sources.
- **Sim**: animated flow dots in the nominal, source-described direction, with density and speed proportional to sourced capacity. A **Line 5 shut** scenario updates the Sarnia crude-capacity KPI (nameplate arithmetic only).
- **Toggles** by product and point type, a **search** box, and fly-to quick views.
- **Optional private "My home" layer**: if `data/private/home.json` exists (gitignored, never published), the app shows a schematic gas supply path to a house and a usage panel. Without that file, or with `?nohome`, the layer, its button and its KPI are hidden. No home data is in this repository.

## v0.3
- **Real geometry**: researched lines use OSM/EIA operator/name-matched geometry chained between via-points (`tools/route_match.py`, `tools/build_routes.py`); each line has `route_accuracy` (OSM / EIA / partial / approximate / unknown, matched share, datasets, sources). Approximate lines are dashed.
- **Lake audit** (`tools/water_audit.py`, Natural Earth 10m lakes): no pipeline crosses Lake Ontario; wrong v0.2 crossings of Ontario, Erie and Michigan removed. Only the real Straits of Mackinac crossings remain. See `docs/v03.md`.
- **Depots/terminals** (OSM, `tools/fetch_tiles_osm.py`) and **decommissioned refineries** (Shell Oakville, Petro-Canada Oakville, Port Credit/Texaco, Shell/Gulf/Texaco/Imperial Montreal East, PES Philadelphia) with operator history, years, closure and current use. These have their own grey/red ⊘ style and a toggle.
- **Montreal** (Line 9B, TNPI, TQM, TC Mainline, Portland-Montreal, Suncor) and **Eastern Seaboard** (M&NE, PNGTS, Iroquois, Tennessee, Algonquin, Transco, Texas Eastern, Millennium, Eastern Gas, Colonial, Buckeye, Laurel; Bayway, Delaware City, Trainer, Paulsboro, Irving), with quick views for Lake Ontario, Montreal and E. Seaboard.
- QA: `node tests/smoke.mjs`; `node tests/nohome_check.mjs` (loads with no private home file); on-display tour `python3 tools/shoot_tour.py` (opens `#tour` in Firefox and saves screenshots to `shots/`, which is gitignored). A URL hash such as `#view=mtl` or `#open=Enbridge Line 9` flies to a view or opens a popup.
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
