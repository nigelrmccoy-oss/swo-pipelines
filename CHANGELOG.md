# Changelog

## v0.4.0 (2026-11-03)
### Added
- **Large terminals layer** (134): 31 crude, 93 refined-product, 9 LNG, 1 NGL. 19 have a sourced capacity (Cushing, Hardisty, Edmonton, Superior, Patoka, Nederland, St. James, Mont Belvieu, NY Harbor, Canaport and the EIA LNG sites), each with its source link; every other tank farm shows a tank-farm size that is an **ESTIMATE** from mapped OSM tank footprints. Metric with bbl. See `docs/v04.md`.
- **Wells & field infrastructure layer** (toggle, off by default): 276,442 wells (Ontario OPDS/OGSR Library via LIO 26,717 incl. 2,118 Lake Erie offshore; Michigan EGLE 84,333; OH/PA/NY via EIA/NETL 165,392), with type and status filters, level-of-detail clustering (clusters when zoomed out, individual wells when <= 30,000 are in view) and popups with status, type and operator where public. Plus 478 EIA gas processing plants, 18 compressor sites and 480 OSM oil/gas field sites.
- `tools/fetch_wells.py`, `fetch_terminals.py`, `build_terminals.py`, `fetch_field.py`, `build_docs_v04.py`; `tests/v04.mjs`, `tests/shots_v04.mjs`.
### Fixed (Code Critic v0.3.1 P2/P3)
- Search "Line 6B" / "6B" opens the line (not the Marshall pump station); "Enbridge" opens the operator panel; a failed search closes the old faceplate.
- The URL hash is written on fly, open and the Line 5 toggle; `#view=X&open=Y` keeps the view; `#open=bad-id` shows "Not found".
- Line 6 popup no longer shows "98% legs matched" beside "98% drawn straight" (now "98% of the route length follows a source dataset (that source line is itself schematic)").
- No page overflow (document no longer taller than the viewport); compact header/KPIs at small heights (88 px of 720 px, 12%); the legend defaults to collapsed below 800 px height.
### Known limits
- Terminal coverage is from OSM tiles around the listed hubs/regions; tile boxes for smaller areas and the EIA-anchor sweeps were not run, so some terminals are missing. Capacities for non-hub terminals are estimates. EIA LNG data is dated Apr 2020.
- No gathering lines: none are mapped in OSM for Lake Erie/Ontario (the line renderer is in place).
- OH/PA/NY wells have no status or operator in the public source.

## v0.3.1
See README (Line 78/6B fixes, Line 7/11, route accuracy from geometry, metric units, deep links).
