"""Add sourced stations and NACEI river crossings (focus box) to data/pipelines.json -> data/swo.json."""
import json
D=json.load(open("research/pipelines.json"))
W5="https://en.wikipedia.org/wiki/Enbridge_Line_5"; ENBFS="https://www.enbridge.com/~/media/enb/documents/factsheets/fs_energyinfrastructureassets.pdf"
FERC="https://www.ferc.gov/sites/default/files/2020-08/CP16-22.pdf"; PREP="https://www.enbridgegas.com/about-enbridge-gas/projects/panhandle-regional-expansion"
OEBPH="https://www.oeb.ca/sites/default/files/ENBRIDGE%20GAS-LTC-EB-2022-0157-PANHANDLE-BG-FINAL-14-05-24.pdf"; WKZ="https://en.wikipedia.org/wiki/Kalamazoo_River_oil_spill"
OEBDP="https://www.rds.oeb.ca/CMWebDrawer/Record/804343/File/document"
AP="approximate: coordinates are the named town/place, not the station site"
st=[("Rapid River pump/NGL station (Line 5)","pump",45.92,-86.96,W5),("Lewiston pumping station (Line 5)","pump",44.88,-84.31,W5),("Marysville pumping station (Line 5)","pump",42.91,-82.49,W5),
("Marshall pump station (Line 6B/78)","pump",42.27,-84.96,WKZ),("Superior Terminal","terminal",46.72,-92.10,ENBFS),("Griffith/Hartsdale Terminal","terminal",41.53,-87.42,ENBFS),
("Stockbridge Terminal","terminal",42.45,-84.18,ENBFS),("Flanagan Terminal (near Pontiac IL)","terminal",40.88,-88.86,ENBFS),
("Dawn Compressor Station","compressor",42.70,-82.17,OEBPH),("Dover Transmission Station","compressor",42.42,-82.40,PREP),
("Kirkwall interconnect (TC Energy)","compressor",43.33,-80.15,OEBDP),("Parkway interconnect (TC Energy)","compressor",43.53,-79.75,OEBDP),
("Hanoverton Compressor Station (NEXUS, 52,000 hp)","compressor",40.75,-80.94,FERC),("Wadsworth Compressor Station (NEXUS, 26,000 hp)","compressor",41.03,-81.73,FERC),
("Clyde Compressor Station (NEXUS, 26,000 hp)","compressor",41.30,-82.98,FERC),("Waterville Compressor Station (NEXUS, 26,000 hp)","compressor",41.50,-83.72,FERC)]
D["stations"]=[dict(name=n,type=t,lat=a,lon=o,coord_note=AP,sources=[s]) for n,t,a,o,s in st]
N="https://geoappext.nrcan.gc.ca/arcgis/rest/services/NACEI/energy_infrastructure_of_north_america_en/MapServer"
cr=[dict(name="Straits of Mackinac (Line 5 dual 20-in)",river="Straits of Mackinac",lat=45.82,lon=-84.77,commodity="crude/NGL",coord_note="approximate midpoint",sources=[W5])]
for lid,kind in ((2,"gas"),(3,"liquids")):
    for f in json.load(open(f"data/gis/nacei_border_{'gas' if lid==2 else 'liquids'}.geojson"))["features"]:
        x,y=f["geometry"]["coordinates"]; p=f["properties"]
        if -84<x<-81.5 and 41.5<y<43.5:
            cr.append(dict(name=p.get("Pipeline"),owner=p.get("Owner"),river="St. Clair River" if y>42.5 else "Detroit River",lat=y,lon=x,commodity="gas" if lid==2 else ("products" if p.get("TypeProd")=="Product" else "crude" if p.get("TypeProd")=="Crude" else "crude/NGL"),
              diameter_in=p.get("Diam_Inch") or "unknown",volume=(p.get("Vol_MMcfd") and p["Vol_MMcfd"]+" MMcf/d") or (p.get("Vol_Mbpd") and p["Vol_Mbpd"]+" Mb/d") or "unknown",
              num_pipes=p.get("NumPipes"),period=p.get("Period"),direction=f"{p.get('FrmState')} -> {p.get('ToState')}",coord_note="NACEI border-crossing point",sources=[f"{N}/{lid}"]))
D["crossings"]=cr
# nominal flow direction = waypoint order
for l in D["lines"]: l["flow_note"]="Animated in waypoint order = nominal direction described by sources (gas lines can be bidirectional)."
D["sources"]=sorted(set(D["sources"])|{s for x in D["stations"]+cr for s in x["sources"]})
D["version"]="0.2"; json.dump(D,open("data/swo.json","w"),indent=1); print(len(D["lines"]),len(D["stations"]),len(cr),len(D["sources"]))
