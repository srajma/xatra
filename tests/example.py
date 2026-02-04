#!/usr/bin/env python3

import xatra
from xatra.loaders import gadm, naturalearth
from xatra.territory_library import NORTH_INDIA
from xatra.colorseq import LinearColorSequence
from matplotlib.colors import LinearSegmentedColormap

# xatra.set_debug_time(True)

# Create a test map
map = xatra.Map()
map.BaseOption("Esri.WorldTopoMap", default=True)
map.BaseOption("Esri.WorldImagery")
# map.BaseOption("Stadia.OSMBright")
map.BaseOption("OpenTopoMap")
map.BaseOption("Esri.WorldPhysical")
map.FlagColorSequence(LinearColorSequence())
map.DataColormap(LinearSegmentedColormap.from_list("custom_cmap", ["yellow", "orange", "red"]), 100, 1000)
# map.Data(gadm = "IND.12", value=100)

map.Data(gadm = "IND.12", value=100)
map.Data(gadm = "IND.21", value=300, period=[0, 600])
map.Data(gadm = "IND.22", value=300, period=[0, 600])
map.Data(gadm = "IND.21", value=1000, period=[600, 700])
map.Data(gadm = "IND.22", value=1000, period=[600, 800])
map.Flag(label="Maurya", value=gadm("IND") | gadm("PAK"), period=[-320, -240], note="south is lost after Ashoka's death")
map.Flag(label="Maurya", value=NORTH_INDIA, period=[-320, -180])
map.Flag(label="Gupta", value=NORTH_INDIA, period=[250, 500], color="#ff0000")
map.Flag(label="Chola", value=gadm("IND.31"), note="Chola persisted throughout this entire period", classes="tamil")
map.Flag(label="Principality", value=gadm("IND.11.1"))
map.Flag(label="Gujarat", value=gadm("IND.11"), parent="Gupta", period=[400,600])
map.Flag(label="Mahārāṣṭra", value=gadm("IND.20"), parent="Gupta", period=[300,400])
map.Flag(label="Akāravanti", value=gadm("IND.19"), parent="Gupta", period=[150,500])
map.Flag(label="Muslim", placeholder=True, color="#00ff00")
map.Flag(label="Delhi", value=gadm("IND.25") | gadm("IND.34"), period=[1200,1500], parent="Muslim")
map.Flag(label="Mughal", value=NORTH_INDIA, period=[1500,1700], parent="Muslim")
map.Flag(label="Deccan", value=gadm("IND.2") | gadm("IND.16") | gadm("IND.32"), period=[1400,1600], parent="Muslim")
# map.Admin(gadm="IND", level=2)
map.Admin(gadm="IND.16", level=3, period=[-500,750])
map.Admin(gadm="BGD", level=1)
map.Admin(gadm="AFG", level=0)
map.AdminRivers(sources=["overpass"])
map.River(label="Ganga", value=naturalearth("1159122643"), note="can be specified as naturalearth(id) or overpass(id)", classes="ganga-river indian-river")
map.River(label="Ganga", value=naturalearth("1159122643"), period=[0, 600], note="Modern course of Ganga", classes="modern-river")
map.Path(label="Uttarapatha", value=[[28,77],[30,90],[40, 120]], classes="uttarapatha-path")
map.Path(label="Silk Road", value=[[35.0, 75.0], [40.0, 80.0], [45.0, 85.0]], period=[-200, 600], classes="silk-road")
map.Point(label="Indraprastha", position=[28,77])
map.Point(label="Delhi", position=[28.6, 77.2], period=[400, 800])
map.Text(label="Jambudvipa", position=[22,79], classes="jambudvipa-text")
map.Text(label="Aryavarta", position=[22,79], classes="aryavarta-text", period=[0, 600])

map.TitleBox("<b>Map of major Indian empires</b><br>Classical period, source: Majumdar.")
map.TitleBox("<h2>Ancient Period (-500 to 0)</h2><p>This title appears only in ancient times</p>", period=[-500, 0])
map.TitleBox("<h2>Classical Period (-100 to 400)</h2><p>This title appears only in classical times</p>", period=[-100, 400])
map.slider(speed=1000) # a slider is automatically added, but you can use this to set the time limits and play speed
map.zoom(4)
map.CSS("""
/* applies to all elements of given class */
.river { stroke: #0066cc; stroke-width: 2; }
.path { stroke: #8B4513; stroke-width: 2; stroke-dasharray: 5 5;}
#title { background: rgba(255,255,255,0.95); border: 1px solid #ccc; padding: 12px 16px; border-radius: 8px; max-width: 360px; z-index: 1000; }
.flag-label { color: #888;}
#controls, #controls input {width:90%;}

/* Specific styling for individual elements */
.tamil {fill: #880088}
.indian-river { stroke: #ff0000; }
.ganga-river { stroke-width: 4; }
.uttarapatha-path { stroke: #ff0000; stroke-width: 2; stroke-dasharray: 5 5; }
.jambudvipa-text { font-size: 24px; font-weight: normal; color: #666666; }
.ooga {display: none}
""")

# Generate the map
map.show(out_json="tests/map.json", out_html="tests/map.html")