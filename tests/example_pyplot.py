#!/usr/bin/env python3
"""
Example demonstrating pyplot-style interface for Xatra.

This example shows how to use xatra.Flag(), xatra.River(), etc. 
directly without explicitly creating a Map object, similar to
how matplotlib.pyplot works.
"""

import xatra
from xatra.loaders import gadm, naturalearth
from xatra.territory_library import NORTH_INDIA

# No need to create a map object - just start adding elements!
# A Map is automatically created on first use.

xatra.BaseOption("OpenStreetMap", default=True)
xatra.BaseOption("Esri.WorldImagery")

# Add flags - colors are automatically assigned
xatra.Flag(label="Maurya", value=gadm("IND") | gadm("PAK"), period=[-320, -240])
xatra.Flag(label="Maurya", value=NORTH_INDIA, period=[-320, -180])
xatra.Flag(label="Gupta", value=NORTH_INDIA, period=[250, 500])
xatra.Flag(label="Chola", value=gadm("IND.31"), note="Chola persisted throughout")

# Add other elements
xatra.River(label="Ganga", value=naturalearth("1159122643"), classes="major-river")
xatra.Path(label="Uttarapatha", value=[[28, 77], [30, 90], [40, 120]])
xatra.Point(label="Indraprastha", position=[28, 77])
xatra.Text(label="Jambudvipa", position=[22, 79])

# Add title and styling
xatra.TitleBox("<b>Pyplot-style Map Example</b><br>Classical period, using xatra.Flag() etc.")
xatra.CSS("""
.flag { stroke: #555; fill: rgba(200,0,0,0.4); }
.major-river { stroke: #0066cc; stroke-width: 3; }
""")

# Set up time slider
xatra.slider(-320, 500)

# Export the map
xatra.show(out_json="tests/map_pyplot.json", out_html="tests/map_pyplot.html")
print("Map exported to tests/map_pyplot.html")

