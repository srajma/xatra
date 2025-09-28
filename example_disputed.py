#!/usr/bin/env python3

import xatra
from xatra.loaders import gadm, naturalearth
from xatra.territory_library import NORTHERN_INDIA
from xatra.colorseq import LinearColorSequence
from matplotlib.colors import LinearSegmentedColormap

# Create a test map
map = xatra.FlagMap()
map.BaseOption("OpenStreetMap", default=True)
map.BaseOption("Esri.WorldImagery")
map.BaseOption("OpenTopoMap")
map.BaseOption("Esri.WorldPhysical")

# map.Admin(gadm="IND", level=0)
map.Flag(label="India", value=gadm("IND"))

map.slider(speed=1000) # a slider is automatically added, but you can use this to set the time limits and play speed

# Generate the map
map.show(out_json="map_disputed.json", out_html="map_disputed.html")