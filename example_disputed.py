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

# map.Admin(gadm="IND", level=0) # this should work, but doesn't
map.Admin(gadm="IND", level=1) # this should work, but doesn't
# map.Admin(gadm="Z01.14", level=0, find_in_gadm=["IND"]) # need to implement "find_in_gadm" feature 
# map.Flag(label="India", value=gadm("IND")) # this works
# map.Flag(label="Kashmir", value=gadm("Z01.14", find_in_gadm=["IND"])) # need to implement "find_in_gadm" feature 
# map.Data(gadm="IND", value=100) # this works
# map.Data(gadm="Z01.14", value=100, find_in_gadm=["IND"]) # need to implement "find_in_gadm" feature 

# map.slider(speed=1000) # a slider is automatically added, but you can use this to set the time limits and play speed

# Generate the map
map.show(out_json="map_disputed.json", out_html="map_disputed.html")