# SWO-PIPELINES v0.1 — Southwestern Ontario oil & gas pipelines (public-source map/sim)

Interactive three.js schematic of oil, NGL, gas and products pipelines in and feeding southwestern Ontario, driven by `data/pipelines.json`.
Same stack as `wr-water`: no build step, vanilla ES modules, vendored three.js r170. **Unofficial**, public sources only.

## Run
```bash
cd ~/swo-pipelines
python3 -m http.server 8770
# open http://localhost:8770/
```

## What's modelled
- 15 lines (Line 5, Straits dual crossing, Great Lakes Tunnel project, Line 6B (historic), Line 78, Line 6, Line 9, Line 7, Vector, NEXUS, Great Lakes Gas Transmission, Dawn-Parkway, Enbridge Gas Panhandle, Sun-Canadian, Rover) + 6 facilities (Dawn and Tecumseh storage, Imperial / Suncor / Shell refineries, Chemical Valley).
- Tube thickness follows the sourced diameter; animated flow density follows sourced nameplate capacity. Replaced or proposed lines don't flow.
- Click any line or facility for a faceplate listing every field with its source links. Unknowns are shown as unknown.
- Scenario: "Line 5 shut at Straits" stops Line 5 and recomputes crude capacity into Sarnia from sourced nameplate numbers (arithmetic only, no hydraulics).
- Waypoints are approximate named-place coordinates, **not surveyed routes**.

Research: `docs/research.md`, generator `docs/build_research.py`.
