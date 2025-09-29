#!/usr/bin/env python3

import xatra
from xatra.loaders import gadm, naturalearth
from xatra.colorseq import LinearColorSequence
from matplotlib.colors import LinearSegmentedColormap

# Create a test map
map = xatra.FlagMap()
map.BaseOption("OpenStreetMap", default=True)
map.BaseOption("Esri.WorldImagery")
map.BaseOption("OpenTopoMap")
map.BaseOption("Esri.WorldPhysical")

map.Admin(gadm="IND", level=0)
map.Admin(gadm="IND", level=2)
map.Admin(gadm="Z01.14", level=3, find_in_gadm=["IND"])
map.Flag(label="India", value=gadm("IND"))
map.Flag(label="Kashmir", value=gadm("Z01.14", find_in_gadm=["IND"]))
map.Data(gadm="IND", value=100)
map.Data(gadm="Z01.14", value=100, find_in_gadm=["IND"])

# map.slider(speed=1000) # a slider is automatically added, but you can use this to set the time limits and play speed

# Generate the map
map.show(out_json="map_disputed.json", out_html="map_disputed.html")