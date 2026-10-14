# SWO-PIPELINES v0.3: North American oil & gas pipelines, SW Ontario, Montreal & Eastern Seaboard detail

Interactive 3D globe (CesiumJS, vendored, **no API keys**) with high-detail terrain (AWS Terrain Tiles) under Esri World Imagery.
Same style as `wr-water`: no build step, vanilla ES modules, vendored libs, dark control-panel UI. **Unofficial**; uses public data only.

## Run
```bash
cd ~/swo-pipelines && python3 -m http.server 8770 --bind 127.0.0.1   # http://localhost:8770/
node tests/smoke.mjs                                                  # headless smoke test (playwright from ~/qa-2026-10-08/pw)
```

## What's modelled
- **Continental layers** (GeoJSON in `data/gis`, each with `source_url`): EIA US crude, HGL, products and natural gas pipelines (DOE/NETL-hosted EIA FeatureServer); OSM Canada pipelines; OSM detailed SW Ontario/Michigan pipelines; NACEI border crossings. Mexico OSM failed (Overpass 504s), see docs/datasets.md.
- **Researched SW Ontario detail** (`data/swo.json`): 15 lines with a source on every fact. Click any one for operator, product, diameter, capacity, in-service year, status, incidents and sources.
- **Points**: 16 pump/compressor/terminal stations, Dawn and Tecumseh storage, the Sarnia refineries and Chemical Valley, and 27 crossings (St. Clair River and Detroit River from NACEI, plus the Straits of Mackinac).
- **Sim**: animated flow dots in the nominal source-described direction, with density and speed proportional to sourced capacity. A **Line 5 shut** scenario updates the Sarnia crude-capacity KPI (nameplate arithmetic only).
- **Toggles** by product, a **search** box (lines, stations, crossings, operators), and fly-to views.
- **My home**: [private address] (OSM geocode), with the schematic supply path Dawn → Enbridge transmission → Kitchener gate (APPROXIMATE) → Kitchener Utilities distribution (schematic) → house. The usage panel reads from `data/home.json` (built by `tools/build_home.py` from meter readings and the partial smart-plug log).

## v0.3
- **Real geometry**: researched lines use OSM/EIA operator/name-matched geometry chained between via-points (`tools/route_match.py`, `tools/build_routes.py`); each line has `route_accuracy` (OSM / EIA / partial / approximate / unknown, matched share, datasets, sources). Approximate lines are dashed.
- **Lake audit** (`tools/water_audit.py`, Natural Earth 10m lakes): no pipeline crosses Lake Ontario; wrong v0.2 crossings of Ontario, Erie and Michigan removed. Only the real Straits of Mackinac crossings remain. See `docs/v03.md`.
- **Depots/terminals** (OSM, `tools/fetch_tiles_osm.py`) and **decommissioned refineries** (Shell Oakville, Petro-Canada Oakville, Port Credit/Texaco, Shell/Gulf/Texaco/Imperial Montreal East, PES Philadelphia) with operator history, years, closure and current use. These have their own grey/red ⊘ style and a toggle.
- **Montreal** (Line 9B, TNPI, TQM, TC Mainline, Portland-Montreal, Suncor) and **Eastern Seaboard** (M&NE, PNGTS, Iroquois, Tennessee, Algonquin, Transco, Texas Eastern, Millennium, Eastern Gas, Colonial, Buckeye, Laurel; Bayway, Delaware City, Trainer, Paulsboro, Irving), with quick views for Lake Ontario, Montreal and E. Seaboard.
- QA: `node tests/smoke.mjs`; on-display tour `python3 tools/shoot_tour.py` (opens `#tour` in Firefox and saves `shots/v03-*.png`). A URL hash such as `#view=mtl` or `#open=Enbridge Line 9` flies to a view or opens a popup.
- Build: `tools/.venv/bin/python tools/build_v03.py && python3 tools/build_docs_v03.py`.
Tools: `tools/fetch_eia.py`, `tools/fetch_other.py`, `tools/fetch_swo_osm.py`, `tools/augment.py`, `tools/build_home.py`, `tools/build_research.py`. Docs: `docs/research.md`, `docs/datasets.md`.
