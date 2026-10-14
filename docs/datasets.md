# v0.2 datasets, stations and crossings

## GIS datasets (data/gis)

- `data/gis/nacei_border_gas.geojson`: 99 features; source https://geoappext.nrcan.gc.ca/arcgis/rest/services/NACEI/energy_infrastructure_of_north_america_en/MapServer/2 (); North American Cooperation on Energy Information (NACEI), Aug 2017
- `data/gis/nacei_border_liquids.geojson`: 52 features; source https://geoappext.nrcan.gc.ca/arcgis/rest/services/NACEI/energy_infrastructure_of_north_america_en/MapServer/3 (); North American Cooperation on Energy Information (NACEI), Aug 2017
- `data/gis/osm_canada_pipelines.geojson`: 3204 features; source https://overpass-api.de/api/interpreter (ODbL 1.0 (c) OpenStreetMap contributors); OpenStreetMap contributors via Overpass API; query: [out:json][timeout:600];area["ISO3166-1"="CA"][admin_level=2]->.a;way["man_made"="pipeline"]["substance"~"^(gas|oil|fuel|natural_gas|crude_oil|ngl|l
- `data/gis/osm_swo_facilities.geojson`: 14 features; source https://overpass-api.de/api/interpreter (ODbL 1.0 (c) OpenStreetMap contributors); OpenStreetMap contributors via Overpass; query: [out:json][timeout:300];(way["man_made"="pipeline"]["substance"~"gas|oil|fuel|ngl|lpg|crude|petroleum|ethylene|propane|butane"](41.5,-87.5,46.5,-79.0);n
- `data/gis/osm_swo_pipelines.geojson`: 1317 features; source https://overpass-api.de/api/interpreter (ODbL 1.0 (c) OpenStreetMap contributors); OpenStreetMap contributors via Overpass; query: [out:json][timeout:300];(way["man_made"="pipeline"]["substance"~"gas|oil|fuel|ngl|lpg|crude|petroleum|ethylene|propane|butane"](41.5,-87.5,46.5,-79.0);n
- `data/gis/us_crude.geojson`: 236 features; source https://arcgis.netl.doe.gov/server/rest/services/Hosted/EIA_pipeline_data/FeatureServer/2 (U.S. Government public domain); U.S. EIA pipeline layers, hosted by DOE/NETL (EIA_pipeline_data FeatureServer); see https://www.eia.gov/maps/layer_info-m.php
- `data/gis/us_hgl.geojson`: 133 features; source https://arcgis.netl.doe.gov/server/rest/services/Hosted/EIA_pipeline_data/FeatureServer/0 (U.S. Government public domain); U.S. EIA pipeline layers, hosted by DOE/NETL (EIA_pipeline_data FeatureServer); see https://www.eia.gov/maps/layer_info-m.php
- `data/gis/us_natgas.geojson`: 32920 features; source https://arcgis.netl.doe.gov/server/rest/services/Hosted/EIA_pipeline_data/FeatureServer/3 (U.S. Government public domain); U.S. EIA pipeline layers, hosted by DOE/NETL (EIA_pipeline_data FeatureServer); see https://www.eia.gov/maps/layer_info-m.php
- `data/gis/us_products.geojson`: 329 features; source https://arcgis.netl.doe.gov/server/rest/services/Hosted/EIA_pipeline_data/FeatureServer/1 (U.S. Government public domain); U.S. EIA pipeline layers, hosted by DOE/NETL (EIA_pipeline_data FeatureServer); see https://www.eia.gov/maps/layer_info-m.php
- Mexico OSM layer: NOT included. Three Overpass attempts on 2026-10-13 (overpass-api.de, kumi.systems, private.coffee) returned 504. Mexico appears only through NACEI border-crossing points.

## Stations (coords approximate = town/place)
- Rapid River pump/NGL station (Line 5) (pump) 45.92,-86.96 [src](https://en.wikipedia.org/wiki/Enbridge_Line_5)
- Lewiston pumping station (Line 5) (pump) 44.88,-84.31 [src](https://en.wikipedia.org/wiki/Enbridge_Line_5)
- Marysville pumping station (Line 5) (pump) 42.91,-82.49 [src](https://en.wikipedia.org/wiki/Enbridge_Line_5)
- Marshall pump station (Line 6B/78) (pump) 42.27,-84.96 [src](https://en.wikipedia.org/wiki/Kalamazoo_River_oil_spill)
- Superior Terminal (terminal) 46.72,-92.1 [src](https://www.enbridge.com/~/media/enb/documents/factsheets/fs_energyinfrastructureassets.pdf)
- Griffith/Hartsdale Terminal (terminal) 41.53,-87.42 [src](https://www.enbridge.com/~/media/enb/documents/factsheets/fs_energyinfrastructureassets.pdf)
- Stockbridge Terminal (terminal) 42.45,-84.18 [src](https://www.enbridge.com/~/media/enb/documents/factsheets/fs_energyinfrastructureassets.pdf)
- Flanagan Terminal (near Pontiac IL) (terminal) 40.88,-88.86 [src](https://www.enbridge.com/~/media/enb/documents/factsheets/fs_energyinfrastructureassets.pdf)
- Dawn Compressor Station (compressor) 42.7,-82.17 [src](https://www.oeb.ca/sites/default/files/ENBRIDGE%20GAS-LTC-EB-2022-0157-PANHANDLE-BG-FINAL-14-05-24.pdf)
- Dover Transmission Station (compressor) 42.42,-82.4 [src](https://www.enbridgegas.com/about-enbridge-gas/projects/panhandle-regional-expansion)
- Kirkwall interconnect (TC Energy) (compressor) 43.33,-80.15 [src](https://www.rds.oeb.ca/CMWebDrawer/Record/804343/File/document)
- Parkway interconnect (TC Energy) (compressor) 43.53,-79.75 [src](https://www.rds.oeb.ca/CMWebDrawer/Record/804343/File/document)
- Hanoverton Compressor Station (NEXUS, 52,000 hp) (compressor) 40.75,-80.94 [src](https://www.ferc.gov/sites/default/files/2020-08/CP16-22.pdf)
- Wadsworth Compressor Station (NEXUS, 26,000 hp) (compressor) 41.03,-81.73 [src](https://www.ferc.gov/sites/default/files/2020-08/CP16-22.pdf)
- Clyde Compressor Station (NEXUS, 26,000 hp) (compressor) 41.3,-82.98 [src](https://www.ferc.gov/sites/default/files/2020-08/CP16-22.pdf)
- Waterville Compressor Station (NEXUS, 26,000 hp) (compressor) 41.5,-83.72 [src](https://www.ferc.gov/sites/default/files/2020-08/CP16-22.pdf)

## River / strait crossings
- Straits of Mackinac: Straits of Mackinac (Line 5 dual 20-in) owner  dia  vol  () [src](https://en.wikipedia.org/wiki/Enbridge_Line_5)
- St. Clair River: The Link Pipeline owner Niagara Gas Transmission Limited dia 24 vol unknown (Michigan -> Ontario) [src](https://geoappext.nrcan.gc.ca/arcgis/rest/services/NACEI/energy_infrastructure_of_north_america_en/MapServer/2)
- St. Clair River: St. Clair River Crossing Pipeline owner St. Clair Pipelines Management Inc. dia 12/24 vol unknown (Ontario -> Michigan) [src](https://geoappext.nrcan.gc.ca/arcgis/rest/services/NACEI/energy_infrastructure_of_north_america_en/MapServer/2)
- St. Clair River: Bluewater River Crossing Replacement owner St. Clair Pipelines Management Inc. dia 20 vol unknown (Ontario -> Michigan) [src](https://geoappext.nrcan.gc.ca/arcgis/rest/services/NACEI/energy_infrastructure_of_north_america_en/MapServer/2)
- St. Clair River: Line 500-1, Line 500-2 owner TransCanada Pipelines Limited dia 36(2) vol unknown (Michigan -> Ontario) [src](https://geoappext.nrcan.gc.ca/arcgis/rest/services/NACEI/energy_infrastructure_of_north_america_en/MapServer/2)
- Detroit River: Detroit River/Windsor 1 And 2 owner Union Gas Limited dia 12(2) vol unknown (Michigan -> Ontario) [src](https://geoappext.nrcan.gc.ca/arcgis/rest/services/NACEI/energy_infrastructure_of_north_america_en/MapServer/2)
- St. Clair River: Vector owner Vector Pipeline Limited Partnership dia 42 vol unknown (Michigan -> Ontario) [src](https://geoappext.nrcan.gc.ca/arcgis/rest/services/NACEI/energy_infrastructure_of_north_america_en/MapServer/2)
- Detroit River: Panhandle Eastern PL owner Southern Union dia unknown vol 100 MMcf/d (Michigan -> Ontario) [src](https://geoappext.nrcan.gc.ca/arcgis/rest/services/NACEI/energy_infrastructure_of_north_america_en/MapServer/2)
- St. Clair River: Bluewater Pipeline Co owner  dia unknown vol 250 MMcf/d (Michigan -> Ontario) [src](https://geoappext.nrcan.gc.ca/arcgis/rest/services/NACEI/energy_infrastructure_of_north_america_en/MapServer/2)
- St. Clair River: ANR Pipeline Co owner TransCanada dia unknown vol 150 MMcf/d (Michigan -> Ontario) [src](https://geoappext.nrcan.gc.ca/arcgis/rest/services/NACEI/energy_infrastructure_of_north_america_en/MapServer/2)
- St. Clair River: Great Lakes Transmission owner TransCanada dia unknown vol 1350 MMcf/d (Michigan -> Ontario) [src](https://geoappext.nrcan.gc.ca/arcgis/rest/services/NACEI/energy_infrastructure_of_north_america_en/MapServer/2)
- St. Clair River: Vector Pipeline Co owner Enbridge\DTE Energy dia unknown vol 1350 MMcf/d (Michigan -> Ontario) [src](https://geoappext.nrcan.gc.ca/arcgis/rest/services/NACEI/energy_infrastructure_of_north_america_en/MapServer/2)
- St. Clair River: Michigan Consolidated Gas owner DTE Energy dia unknown vol unknown (Michigan -> Ontario) [src](https://geoappext.nrcan.gc.ca/arcgis/rest/services/NACEI/energy_infrastructure_of_north_america_en/MapServer/2)
- Detroit River: Canadian Eastern Section owner Kinder Morgan Cochin ULC dia 10 vol unknown (Michigan -> Ontario) [src](https://geoappext.nrcan.gc.ca/arcgis/rest/services/NACEI/energy_infrastructure_of_north_america_en/MapServer/3)
- Detroit River: Eastern Delivery System owner Plains Midstream dia 10 vol unknown (Michigan -> Ontario) [src](https://geoappext.nrcan.gc.ca/arcgis/rest/services/NACEI/energy_infrastructure_of_north_america_en/MapServer/3)
- St. Clair River: Line 5 owner Enbridge Pipelines Inc. dia 30 vol unknown (Michigan -> Ontario) [src](https://geoappext.nrcan.gc.ca/arcgis/rest/services/NACEI/energy_infrastructure_of_north_america_en/MapServer/3)
- St. Clair River: Line 6 owner Enbridge Pipelines Inc. dia 30 vol unknown (Michigan -> Ontario) [src](https://geoappext.nrcan.gc.ca/arcgis/rest/services/NACEI/energy_infrastructure_of_north_america_en/MapServer/3)
- St. Clair River: Salmon A owner SCL Pipeline Inc. dia 6 vol unknown (Michigan -> Ontario) [src](https://geoappext.nrcan.gc.ca/arcgis/rest/services/NACEI/energy_infrastructure_of_north_america_en/MapServer/3)
- St. Clair River: St. Clair River owner Genesis Pipeline (Canada) Ltd. dia 8/6(2) vol unknown (Michigan -> Ontario) [src](https://geoappext.nrcan.gc.ca/arcgis/rest/services/NACEI/energy_infrastructure_of_north_america_en/MapServer/3)
- St. Clair River: Sun-Canadian owner Sunoco dia 8 vol unknown (Ontario -> Michigan) [src](https://geoappext.nrcan.gc.ca/arcgis/rest/services/NACEI/energy_infrastructure_of_north_america_en/MapServer/3)
- St. Clair River: Line 5 owner Enbridge Energy Partners dia 30 vol unknown (Michigan -> Ontario) [src](https://geoappext.nrcan.gc.ca/arcgis/rest/services/NACEI/energy_infrastructure_of_north_america_en/MapServer/3)
- St. Clair River: Line 6 owner Enbridge Energy Partners dia 30 vol unknown (Michigan -> Ontario) [src](https://geoappext.nrcan.gc.ca/arcgis/rest/services/NACEI/energy_infrastructure_of_north_america_en/MapServer/3)
- St. Clair River: Salmon A owner Salmon Resources dia 6 vol unknown (Michigan -> Ontario) [src](https://geoappext.nrcan.gc.ca/arcgis/rest/services/NACEI/energy_infrastructure_of_north_america_en/MapServer/3)
- St. Clair River: Genesis Pipeline owner NOVA dia 12/8/6(2) vol unknown (Michigan -> Ontario) [src](https://geoappext.nrcan.gc.ca/arcgis/rest/services/NACEI/energy_infrastructure_of_north_america_en/MapServer/3)
- St. Clair River: Mariner West owner Sunoco Logistic dia 8 vol unknown (Michigan -> Ontario) [src](https://geoappext.nrcan.gc.ca/arcgis/rest/services/NACEI/energy_infrastructure_of_north_america_en/MapServer/3)
- Detroit River: Detroit Pipeline (EDS) owner Plains LPG dia 10 vol unknown (Michigan -> Ontario) [src](https://geoappext.nrcan.gc.ca/arcgis/rest/services/NACEI/energy_infrastructure_of_north_america_en/MapServer/3)
- Detroit River: Cochin owner Kinder Morgan dia 10 vol unknown (Michigan -> Ontario) [src](https://geoappext.nrcan.gc.ca/arcgis/rest/services/NACEI/energy_infrastructure_of_north_america_en/MapServer/3)

## Terrain / imagery
- AWS Terrain Tiles (Terrarium) https://registry.opendata.aws/terrain-tiles/ , decoded client-side to z15
- Esri World Imagery https://services.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer (keyless, the same approach as GEV's keyless fallback)
- CesiumJS 1.138.0 copied (vendored) from ~/gods-eye-view/node_modules (Apache-2.0); GEV itself not modified or run
