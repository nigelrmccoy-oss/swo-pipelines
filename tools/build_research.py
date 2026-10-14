import json
W5="https://en.wikipedia.org/wiki/Enbridge_Line_5"; WEPS="https://en.wikipedia.org/wiki/Enbridge_Pipeline_System"
WKZ="https://en.wikipedia.org/wiki/Kalamazoo_River_oil_spill"; ENBFS="https://www.enbridge.com/~/media/enb/documents/factsheets/fs_energyinfrastructureassets.pdf"
ICN="https://insideclimatenews.org/news/10042014/ruptured-michigan-pipeline-restart-now-new-and-double-capacity/"
MPSC="https://mi-psc.my.site.com/sfc/servlet.shepherd/version/download/068t0000000wdYQAAY"
ICC="https://iccqa.illinois.gov/docket/P2013-0134/documents/193818/files/341235.pdf"
CER9="https://apps.cer-rec.gc.ca/PPS/en/pipeline-profiles/enbridge-line-9"; ENB9="https://www.enbridge.com/media-center/news/details?id=1815802&lang=en&year=2014"
CER9B="https://cer-rec.gc.ca/en/applications-hearings/view-applications-projects/line-9b-reversal/index.html"
WENB="https://en.wikipedia.org/wiki/Enbridge_Gas_Inc."; WVEC="https://en.wikipedia.org/wiki/Vector_Pipeline"; WGL="https://en.wikipedia.org/wiki/Great_Lakes_Gas_Transmission"
FERCNX="https://www.ferc.gov/sites/default/files/2020-08/CP16-22.pdf"; EIANX="https://www.eia.gov/naturalgas/weekly/archivenew_ngwu/2018/10_18/"
RTNX="https://www.reuters.com/article/business/us-oks-startup-of-part-of-enbridge-ohio-michigan-nexus-natgas-pipe-idUSKCN1ML2J4/"
REPNX="https://www.indeonline.com/story/business/2018/10/24/nexus-pipeline-in-service/9427423007/"
DPR="https://www.enbridgegas.com/about-enbridge-gas/projects/dawn-parkway-renewal-project"
OEBDP="https://www.rds.oeb.ca/CMWebDrawer/Record/804343/File/document"; NGI="https://naturalgasintel.com/news/enbridge-gauging-support-to-boost-dawns-daily-capacity-by-91200-mmbtu-in-late-2027/"
STOR="https://www.enbridgegas.com/storage-transportation/operational-information/storage-reporting"
M12="https://enbridgegas.mediaroom.com/2020-11-24-Enbridge-Gas-Announces-M12-Transportation-Service-Open-Season"
PREP="https://www.enbridgegas.com/about-enbridge-gas/projects/panhandle-regional-expansion"; OEBPH="https://www.oeb.ca/sites/default/files/ENBRIDGE%20GAS-LTC-EB-2022-0157-PANHANDLE-BG-FINAL-14-05-24.pdf"
OEBPHD="https://www.rds.oeb.ca/CMWebDrawer/Record/852653/File/document"
SUNC="https://sun-canadian.com/crossings/pipeline-route-map-4-1_2012-2/"; SUNREF="https://www.suncor.com/en-ca/what-we-do/refining/sarnia-refinery"
OEBSUN="https://www.rds.oeb.ca/CMWebDrawer/Record/82078/File/document"
IMP="https://www.imperialoil.ca/company/operations/sarnia"; SHELL="https://caer.ca/pages/435/Shell_Canada/"; OSM="https://www.oilsandsmagazine.com/projects/canadian-refineries"
USACE="https://www.dvidshub.net/news/572235/corps-engineers-issues-enbridge-energy-permit-regulated-activities-proposed-line-5-tunnel-project-releases-record"
MISC="https://www.michbar.org/Portals/0/opinions/supreme/2026/073126/86270.pdf"
MLIVE="https://www.mlive.com/environment/2026/09/whitmer-administration-to-reconsider-line-5-tunnel-permits-after-court-ruling.html"
MBN="https://michiganbusinessnetwork.com/governor-whitmer-egle-director-roos-state-must-consider-impact-of-recent-supreme-court-decision-on-line-5-tunnel-permits/"
WSAR="https://en.wikipedia.org/wiki/Environmental_impact_of_the_chemical_industry_in_Sarnia"
U="unknown"
def F(v,*s): return {"value":v,"sources":list(s)}
# coordinates: approximate locations of named places (schematic waypoints, NOT surveyed alignments)
P={"Superior":[46.72,-92.10],"RapidRiver":[45.92,-86.96],"Mackinaw_N":[45.86,-84.77],"McGulpin":[45.79,-84.77],"Lewiston":[44.88,-84.31],"BayCity":[43.59,-83.89],"Marysville":[42.91,-82.49],"Sarnia":[42.97,-82.40],
"Griffith":[41.53,-87.42],"Flanagan":[40.88,-88.86],"Marshall":[42.27,-84.96],"Stockbridge":[42.45,-84.18],"Ortonville":[42.85,-83.44],"Westover":[43.30,-80.10],"Nanticoke":[42.80,-80.06],"Montreal":[45.50,-73.57],
"Joliet":[41.53,-88.08],"Dawn":[42.70,-82.17],"Kensington":[40.74,-80.95],"Ypsilanti":[42.24,-83.61],"Emerson":[49.00,-97.21],"StClairMI":[42.82,-82.49],
"Kirkwall":[43.33,-80.15],"Parkway":[43.53,-79.75],"Ojibway":[42.26,-83.09],"Dover":[42.42,-82.40],"Lakeshore":[42.30,-82.75],"Toronto":[43.70,-79.42],"London":[42.98,-81.25],"Hamilton":[43.25,-79.87],"Tecumseh":[42.85,-82.30],"Corunna":[42.89,-82.43]}
def R(*n): return [P[x]+[x] for x in n]
L=[]
L.append(dict(id="line5",name="Enbridge Line 5",kind="pipeline",operator=F("Enbridge (Lakehead System)",W5),product=F("Synthetic crude, NGLs, sweet crude, light sour crude",W5),commodity="crude/NGL",
 diameter_in=F(30,W5),capacity=F("540,000 bbl/d (as of 2013; up from 490,000)",W5),cap_num=540000,cap_unit="bbl/d",length=F("645 mi",W5),
 route=F("Superior WI -> Upper Peninsula -> Rapid River -> Straits of Mackinac -> Lewiston -> around Saginaw Bay/Bay City -> Marysville MI -> under St. Clair River -> Sarnia ON",W5),
 endpoints=F(["Superior, WI","Sarnia, ON"],W5),waypoints=R("Superior","RapidRiver","Mackinaw_N","McGulpin","Lewiston","BayCity","Marysville","Sarnia"),
 in_service=F(1953,W5),status=F("Operating; Michigan seeking shutdown in court; Canada invoked 1977 transit treaty (2021, 2022); Wisconsin Bad River reroute litigation",W5,MISC),
 incidents=[F("Spilled over 1.1 million gallons 1967-2017",W5),F("2018 tugboat anchor strike damaged Straits segment",W5),F("June 2020 east-leg screw anchor support shifted; east leg shut temporarily",W5),
 F("Bad River Band case: court ordered Enbridge to reroute or shut down in Wisconsin by June 2026; 7th Circuit (July 30 2026) remanded to fashion injunction",W5,MISC)],
 crossings=["Straits of Mackinac","St. Clair River (Marysville-Sarnia)"]))
L.append(dict(id="line5_straits",name="Line 5 Straits of Mackinac dual crossing",kind="crossing",operator=F("Enbridge",W5),product=F("Same as Line 5",W5),commodity="crude/NGL",diameter_in=F("2 x 20",W5),
 capacity=F("part of Line 5 (540,000 bbl/d)",W5),cap_num=540000,cap_unit="bbl/d",length=F("4.5 mi across lakebed; max depth about 270 ft",W5),route=F("North shore of Straits -> McGulpin Point",W5),endpoints=F(["north shore Straits","McGulpin Point, MI"],W5),
 waypoints=R("Mackinaw_N","McGulpin"),in_service=F(1953,W5),status=F("Operating",W5),incidents=[F("2018 anchor strike; 2020 anchor-support shift (see Line 5)",W5)]))
L.append(dict(id="glt",name="Great Lakes Tunnel (Line 5 replacement segment)",kind="project",operator=F("Enbridge Energy LP",USACE),product=F("Line 5 replacement segment in a bedrock tunnel",USACE),commodity="crude/NGL",diameter_in=F(U),
 capacity=F(U),cap_num=None,cap_unit=None,length=F("about 4 miles of lakebed (USACE); 3.9-mile tunnel per search summary, unverified",USACE),route=F("Bedrock beneath the Straits of Mackinac",W5),endpoints=F(["north shore","south shore Straits"],W5),
 waypoints=R("Mackinaw_N","McGulpin"),in_service=F("not built; Enbridge earlier targeted 2024 completion",W5),
 status=F("Proposed. USACE permit issued Aug 12 2026; EGLE permits issued Jul 15 2026; MI Supreme Court vacated MPSC 2023 approval Jul 31 2026; EGLE reviewing again (Sep 9 2026); permit conditions block tunnel-entrance construction",USACE,MISC,MLIVE,MBN),
 incidents=[F("2018 MSCA agreement under Gov. Snyder; Bay Mills Indian Community challenge; USACE ROD acknowledges potentially severe damage to Indigenous cultural resources",W5,MLIVE)]))
L.append(dict(id="line6b",name="Enbridge Line 6B (original, replaced)",kind="pipeline",operator=F("Enbridge Energy",WKZ),product=F("Crude incl. diluted bitumen",WKZ),commodity="crude",diameter_in=F(30,WKZ),
 capacity=F("240,000 bbl/d (old line)",ICN),cap_num=240000,cap_unit="bbl/d",length=F("285 mi path",ICN),route=F("Griffith IN -> Marshall -> Stockbridge -> Ortonville -> St. Clair River at Marysville -> Sarnia",ICN,MPSC),
 endpoints=F(["Griffith, IN","Sarnia, ON"],ICN),waypoints=R("Griffith","Marshall","Stockbridge","Ortonville","Marysville","Sarnia"),in_service=F("about 1968 (described as 46-year-old pipe in 2014)",ICN),
 status=F("Replaced 2013-2014; now part of Line 78",ICN,ENBFS),incidents=[F("July 25 2010 Marshall MI rupture, >1 million US gal dilbit into Talmadge Creek/Kalamazoo River; cleanup about $1.21B (2014); $3.7M PHMSA fine; $177M 2016 DOJ/EPA settlement; NTSB: corrosion fatigue, disbonded tape coating",WKZ)]))
L.append(dict(id="line78",name="Enbridge Line 78 (78A + 78B)",kind="pipeline",operator=F("Enbridge Energy LP",ENBFS),product=F("Light, medium and heavy crude",ENBFS),commodity="crude",diameter_in=F("30-36",ENBFS),
 capacity=F("78A 570,000 bbl/d; 78B 500,000 bbl/d (average annual)",ENBFS),cap_num=500000,cap_unit="bbl/d",length=F("78A 264 mi; 78B 109 mi; total 373 mi (600 km)",ENBFS),
 route=F("Flanagan Terminal (Pontiac IL) -> Griffith IN -> Stockbridge MI (78A); Stockbridge -> Sarnia (78B). Replaced Line 6B with 36-in Griffith-Stockbridge and 30-in Ortonville-St. Clair River",ENBFS,MPSC,ICC),
 endpoints=F(["Flanagan Terminal, IL","Sarnia, ON"],ENBFS),waypoints=R("Flanagan","Griffith","Marshall","Stockbridge","Ortonville","Marysville","Sarnia"),
 in_service=F("6B replacement 2014; Flanagan-Griffith segment planned mid-2015",ICN,ICC),status=F("Operational",ENBFS),incidents=[F("Successor of Line 6B (Kalamazoo spill)",ICN)]))
L.append(dict(id="line6",name="Enbridge Line 6 (Superior-Griffith, feeder)",kind="pipeline",operator=F("Enbridge",ENBFS),product=F("Light, medium and heavy crude",ENBFS),commodity="crude",diameter_in=F(34,ENBFS),
 capacity=F("667,000 bbl/d",ENBFS),cap_num=667000,cap_unit="bbl/d",length=F("465 mi (748 km)",ENBFS),route=F("Superior WI -> Griffith/Hartsdale IN, south around Lake Michigan",ENBFS,W5),endpoints=F(["Superior, WI","Griffith, IN"],ENBFS),
 waypoints=R("Superior","Joliet","Griffith"),in_service=F(U),status=F("Operational",ENBFS),incidents=[]))
L.append(dict(id="line9",name="Enbridge Line 9 (9A Sarnia-Westover, 9B Westover-Montreal)",kind="pipeline",operator=F("Enbridge Pipelines Inc.",CER9),product=F("Light, medium and heavy crude",CER9),commodity="crude",diameter_in=F(30,ENB9),
 capacity=F("about 300,000 bbl/d (was 240,000)",CER9,CER9B),cap_num=300000,cap_unit="bbl/d",length=F("853 km CER-regulated; 9A 246 km, 9B 639 km",CER9,ENB9),route=F("Sarnia -> North Westover -> Montreal; supplies Nanticoke",ENB9,CER9B),
 endpoints=F(["Sarnia, ON","Montreal, QC"],CER9),waypoints=R("Sarnia","London","Westover","Toronto","Montreal"),in_service=F("June 1976",ENB9),
 status=F("Operating west-to-east; reversed 1999 and 2015 (9A Aug 2013, 9B Dec 2015)",CER9,ENB9),incidents=[F("2013 Hamilton protests: Highway 6 blocked; at least 10 arrests June 26 2013 after six-day compound occupation",WENB)]))
L.append(dict(id="line7",name="Enbridge Line 7 (from Sarnia)",kind="pipeline",operator=F("Enbridge",WEPS),product=F("Crude (Line 5 volumes not used in Sarnia go to tanks for Line 7)",W5),commodity="crude",diameter_in=F(U),capacity=F(U),cap_num=None,cap_unit=None,length=F(U),
 route=F("Starts at Sarnia; rest of route unknown in sources used",W5),endpoints=F(["Sarnia, ON",U],W5),waypoints=R("Sarnia","London"),in_service=F(U),status=F("Part of Mainline system",WEPS),incidents=[]))
L.append(dict(id="vector",name="Vector Pipeline",kind="pipeline",operator=F("Vector Pipeline L.P. (Enbridge 60% / DTE); Enbridge operates",WVEC),product=F("Natural gas",WVEC),commodity="gas",diameter_in=F(U),
 capacity=F("about 1 Bcf/d",WVEC),cap_num=1.0,cap_unit="Bcf/d",length=F("348 mi",WVEC),route=F("Joliet IL -> Indiana -> Michigan -> Ontario (Dawn)",WVEC,WENB),endpoints=F(["Joliet, IL","Dawn Hub, ON"],WVEC,WENB),
 waypoints=R("Joliet","Marshall","Ypsilanti","StClairMI","Dawn"),in_service=F("Dec 1, 2000",WVEC),status=F("Operating; connects Alliance and NEXUS to Dawn",WENB),incidents=[]))
L.append(dict(id="nexus",name="NEXUS Gas Transmission",kind="pipeline",operator=F("NEXUS Gas Transmission LLC (Enbridge/DTE)",RTNX),product=F("Natural gas (Marcellus/Utica)",RTNX),commodity="gas",diameter_in=F(36,REPNX),
 capacity=F("1.5 Bcf/d design",FERCNX,EIANX),cap_num=1.5,cap_unit="Bcf/d",length=F("about 255-257.5 mi new pipe",FERCNX,EIANX),route=F("Kensington OH -> northern Ohio -> DTE Gas at Ypsilanti Twp MI; leased DTE + Vector capacity to Dawn",FERCNX),
 endpoints=F(["Kensington, OH","Ypsilanti Twp, MI (to Dawn via leases)"],FERCNX),waypoints=R("Kensington","Ypsilanti"),in_service=F("Oct 2018 (partial, ~1.0 Bcf/d)",EIANX,REPNX),status=F("Operating",REPNX),incidents=[]))
L.append(dict(id="glgt",name="Great Lakes Gas Transmission",kind="pipeline",operator=F("Great Lakes Gas Transmission L.P. (TC Energy)",WGL),product=F("Natural gas",WGL),commodity="gas",diameter_in=F(U),
 capacity=F("up to 2,400 MMcf/d",WGL),cap_num=2.4,cap_unit="Bcf/d",length=F("2,115 mi",WGL),route=F("Emerson MB -> Minnesota -> Wisconsin -> Michigan -> St. Clair MI (re-enters Canada)",WGL),endpoints=F(["Emerson, MB","St. Clair, MI"],WGL),
 waypoints=R("Emerson","Superior","RapidRiver","Mackinaw_N","Lewiston","StClairMI"),in_service=F(1967,WGL),status=F("Operating",WGL),incidents=[]))
L.append(dict(id="dawnparkway",name="Dawn-Parkway System",kind="pipeline",operator=F("Enbridge Gas Inc.",DPR),product=F("Natural gas",DPR),commodity="gas",diameter_in=F("includes NPS 26 line (multiple parallel lines)",DPR),
 capacity=F("design day demand 7,891,876 GJ/d (2023-24)",OEBDP),cap_num=7.89,cap_unit="PJ/d",length=F("225-229 km",DPR,OEBDP),route=F("Dawn Hub -> Kirkwall and Parkway (TC Energy interconnects, GTA)",OEBDP,M12),
 endpoints=F(["Dawn Hub","Parkway (Milton/Oakville)"],OEBDP),waypoints=R("Dawn","London","Kirkwall","Parkway"),in_service=F("1950s (oldest pipe)",DPR),
 status=F("Operating; interim pressure restrictions on NPS 26 reduced capacity; renewal project under way",DPR),incidents=[F("Integrity concerns on NPS 26-inch segments (14 segments, 225 km)",DPR)]))
L.append(dict(id="panhandle",name="Enbridge Gas Panhandle System (+ PREP NPS 36 loop)",kind="pipeline",operator=F("Enbridge Gas Inc.",OEBPH),product=F("Natural gas",OEBPH),commodity="gas",diameter_in=F("NPS 36 loop (rest unknown)",PREP),
 capacity=F(U),cap_num=None,cap_unit=None,length=F("PREP loop about 19 km Dover TS - Lakeshore; full system unknown",PREP),route=F("Dawn Compressor Station -> Ojibway Valve Site, Windsor",OEBPHD,OEBPH),
 endpoints=F(["Dawn","Ojibway, Windsor"],OEBPH),waypoints=R("Dawn","Dover","Lakeshore","Ojibway"),in_service=F("PREP loop Dec 15, 2024; original system unknown",PREP),status=F("Operating; OEB approved PREP May 14 2024",OEBPH),incidents=[]))
L.append(dict(id="suncanadian",name="Sun-Canadian Pipe Line",kind="pipeline",operator=F("Sun-Canadian Pipe Line Company",SUNC),product=F("Refined products",SUNC,SUNREF),commodity="products",diameter_in=F(U),capacity=F(U),cap_num=None,cap_unit=None,
 length=F("about 300 km (search summary of OEB doc, unverified)",OEBSUN),route=F("Sarnia -> London -> Hamilton -> Toronto area",OEBSUN),endpoints=F(["Sarnia","Toronto"],OEBSUN),waypoints=R("Sarnia","London","Hamilton","Toronto"),
 in_service=F(U),status=F("Operating",SUNREF),incidents=[]))
L.append(dict(id="rover",name="Rover Pipeline (feeder via Vector)",kind="pipeline",operator=F(U),product=F("Natural gas from Appalachia",EIANX),commodity="gas",diameter_in=F(U),capacity=F("about 1 Bcf/d flowing onto Vector (Oct 2018)",EIANX),cap_num=1.0,cap_unit="Bcf/d",
 length=F(U),route=F("Appalachia -> Vector -> Dawn, similar route to NEXUS",EIANX),endpoints=F(["Appalachia",U],EIANX),waypoints=R("Kensington","Ypsilanti"),in_service=F(U),status=F("Operating (Oct 2018 force majeure outage)",EIANX),incidents=[F("Oct 2018 equipment failure force majeure, flow to zero",EIANX)]))
FAC=[dict(id="dawn",name="Dawn Hub storage",kind="storage",operator=F("Enbridge Gas Inc.",STOR),product=F("Natural gas storage",STOR),capacity=F("250.8 PJ total, 189.5 PJ working; peak withdrawal 3,999,425 GJ/d",STOR),waypoints=R("Dawn"),status=F("Operating; marketed as 280-288 Bcf working, 7.6 Bcf/d takeaway",M12,NGI)),
 dict(id="tecumseh",name="Tecumseh storage",kind="storage",operator=F("Enbridge Gas Inc.",STOR),product=F("Natural gas storage",STOR),capacity=F("165.5 PJ total, 133.1 PJ working",STOR),waypoints=R("Tecumseh"),status=F("Operating; location approximate/unknown",STOR)),
 dict(id="imperial",name="Imperial Oil Sarnia refinery",kind="refinery",operator=F("Imperial Oil",IMP),product=F("Refined products",IMP),capacity=F("about 113,000 bbl/d (other listings 119,000-124,000)",IMP,OSM),waypoints=R("Sarnia"),status=F("Operating",IMP)),
 dict(id="suncor",name="Suncor Sarnia refinery",kind="refinery",operator=F("Suncor",SUNREF),product=F("Refined products (ships via Sun-Canadian)",SUNREF),capacity=F("about 92,000 bbl/d",SUNREF),waypoints=R("Sarnia"),status=F("Operating",SUNREF)),
 dict(id="shell",name="Shell Sarnia Manufacturing Centre (Corunna)",kind="refinery",operator=F("Shell Canada",SHELL),product=F("Refined products",SHELL),capacity=F("about 72,000 bbl/d (other listing 85,000)",SHELL,OSM),waypoints=R("Corunna"),status=F("Operating",SHELL)),
 dict(id="chemvalley",name="Sarnia Chemical Valley",kind="cluster",operator=F("62 chemical facilities and refineries",WSAR),product=F("Petrochemicals",WSAR),capacity=F(U),waypoints=R("Sarnia"),status=F("Aamjiwnaang state of emergency over benzene Apr 2024; federal interim order May 2024; INEOS Styrolution closed Dec 2025",WSAR))]
NOT=["TC Energy Canadian Mainline in SW Ontario (diameter/capacity not verified)","Panhandle Eastern Pipe Line (US) - details not verified","Individual St. Clair River crossing pipes beyond Line 5/78/Vector/GLGT","Enbridge Line 17 (Stockbridge-Toledo) mentioned only","Sunoco Marysville-Toledo line (mentioned in Line 5 article)","Other Lambton/Kent storage pools (only Dawn and Tecumseh totals verified)"]
srcs=set()
def walk(o):
    if isinstance(o,dict):
        for k,v in o.items():
            if k=="sources": srcs.update(v)
            else: walk(v)
    elif isinstance(o,list): [walk(x) for x in o]
walk(L);walk(FAC)
out=dict(version="0.1",generated="2026-10-13",coord_note="Waypoint coordinates are approximate locations of named places used as schematic waypoints; they are not surveyed alignments.",lines=L,facilities=FAC,not_verified=NOT,sources=sorted(srcs))
json.dump(out,open("pipelines.json","w"),indent=1)
md=["# Southwestern Ontario oil & gas pipelines: research (v0.1, 2026-10-13)\n",out["coord_note"]+" Unknown values are marked `unknown`.\n"]
for x in L+FAC:
    md.append(f"\n## {x['name']}\n")
    for k in ["operator","product","diameter_in","capacity","length","route","endpoints","in_service","status"]:
        if k in x: md.append(f"- **{k}**: {x[k]['value']}  " + " ".join(f"[src]({s})" for s in x[k]['sources']))
    md.append("- **waypoints (approx)**: "+"; ".join(f"{w[2]} {w[0]},{w[1]}" for w in x["waypoints"]))
    for i in x.get("incidents",[]): md.append(f"- **incident/controversy**: {i['value']} "+" ".join(f"[src]({s})" for s in i['sources']))
md.append("\n## Not verified / gaps\n"+"\n".join("- "+n for n in NOT))
md.append("\n## Sources\n"+"\n".join("- "+s for s in sorted(srcs)))
open("research.md","w").write("\n".join(md)+"\n")
print(len(L),len(FAC),len(srcs))
