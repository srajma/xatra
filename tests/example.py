#!/usr/bin/env python3

import xatra
from xatra.loaders import gadm, naturalearth, polygon
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

# ============================================================================
# Custom Polygon Territory Examples
# ============================================================================
# Key coordinates:
#   Delhi: 28, 76      | Nagpur: 20, 78      | Bengal: 23, 87
#   Bangalore: 12, 77.5 | Gujarat: 22, 74    | Center of UP: 26, 82

# Example 1: A custom "Gangetic Heartland" polygon covering the Indo-Gangetic plain
# This creates a diamond-shaped region from Delhi to Bengal to Nagpur and back
gangetic_heartland = polygon([
    [28, 76],    # Delhi (north)
    [23, 87],    # Bengal (east)
    [20, 78],    # Nagpur (south)
    [22, 74],    # Gujarat border (west)
])
map.Flag(
    label="Gangetic Heartland", 
    value=gangetic_heartland, 
    period=[100, 300],
    note="Custom polygon: the fertile Indo-Gangetic plain",
    classes="heartland"
)

# Example 2: Intersection - Clip a state to a custom region
# This shows only the parts of UP+Bihar within a diagonal band
diagonal_band = polygon([
    [28, 80],    # Northwest 
    [28, 88],    # Northeast
    [24, 88],    # Southeast
    [24, 80],    # Southwest
])
gangetic_plain_section = (gadm("IND.34") | gadm("IND.5")) & diagonal_band
map.Flag(
    label="Gangetic Section",
    value=gangetic_plain_section,
    period=[700, 900],
    note="Intersection: UP + Bihar clipped to an eastern section",
    classes="clipped-region"
)

# Example 3: Union - Extend Tamil Nadu with a custom coastal region
coastal_extension = polygon([
    [8, 77],     # Southern tip
    [10, 80],    # East coast
    [8, 82],     # Southeast
    [6, 79],     # Further south (extending beyond TN)
])
extended_tamil_nadu = gadm("IND.31") | coastal_extension
map.Flag(
    label="Extended Chola",
    value=extended_tamil_nadu,
    period=[900, 1100],
    note="Union: Tamil Nadu + custom southern coastal region",
    classes="extended-tn"
)

# Example 4: Difference - Create a "donut" by removing central region from a state
# Remove a region around Nagpur from Maharashtra
nagpur_exclusion = polygon([
    [21, 77],
    [21, 80],
    [19, 80],
    [19, 77],
])
maharashtra_without_vidarbha = gadm("IND.20") - nagpur_exclusion
map.Flag(
    label="Western Maharashtra",
    value=maharashtra_without_vidarbha,
    period=[1100, 1300],
    note="Difference: Maharashtra minus Vidarbha region",
    classes="western-mh"
)

# Example 5: Complex operation - A "trade corridor" from Pakistan through India to Bangladesh
# The corridor extends beyond India's borders, but intersection clips it to Indian territory
trade_corridor_box = polygon([
    [26, 66],    # Pakistan (west, outside India)
    [28, 66],    # Pakistan north
    [28, 92],    # Bangladesh (east, outside India)
    [24, 92],    # Bangladesh south
    [24, 66],    # Back to Pakistan
])
# Intersection clips the corridor to only show parts within India
trade_corridor = gadm("IND") & trade_corridor_box
map.Flag(
    label="Trade Corridor",
    value=trade_corridor,
    period=[1300, 1500],
    note="Intersection: corridor from Pakistan to Bangladesh, clipped to India",
    classes="trade-corridor"
)

# Example 6: Triangle region for a hypothetical "Deccan Sultanate"
deccan_triangle = polygon([
    [20, 78],    # Nagpur (north)
    [12, 77.5],  # Bangalore (south)
    [17, 83],    # East coast
])
map.Flag(
    label="Deccan Triangle",
    value=deccan_triangle,
    period=[1500, 1700],
    note="Custom polygon: triangular Deccan region",
    classes="deccan"
)

# ============================================================================
# End of Custom Polygon Examples
# ============================================================================
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

/* Custom polygon territory styling */
.heartland { fill: rgba(255, 215, 0, 0.5); stroke: #daa520; stroke-width: 2; }
.clipped-region { fill: rgba(100, 149, 237, 0.4); stroke: #4169e1; stroke-width: 2; }
.extended-tn { fill: rgba(255, 140, 0, 0.5); stroke: #ff8c00; stroke-width: 2; }
.western-mh { fill: rgba(147, 112, 219, 0.5); stroke: #9370db; stroke-width: 2; }
.trade-corridor { fill: rgba(60, 179, 113, 0.4); stroke: #3cb371; stroke-width: 2; stroke-dasharray: 8 4; }
.deccan { fill: rgba(220, 20, 60, 0.4); stroke: #dc143c; stroke-width: 2; }
""")

# Generate the map
map.show(out_json="tests/map.json", out_html="tests/map.html")