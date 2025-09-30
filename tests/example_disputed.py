#!/usr/bin/env python3

import xatra
from xatra.loaders import gadm, naturalearth
from xatra.colorseq import LinearColorSequence
from xatra.territory_library import Z01
from matplotlib.colors import LinearSegmentedColormap

# Create a test map
map = xatra.FlagMap()
map.BaseOption("OpenStreetMap", default=True)
map.BaseOption("Esri.WorldImagery")
map.BaseOption("OpenTopoMap")
map.BaseOption("Esri.WorldPhysical")

# map.Admin(gadm="IND", level=0)
# map.Admin(gadm="IND", level=0)
# map.Admin(gadm="Z01.14", level=3) # , find_in_gadm=["IND"]
# map.Flag(label="India", value=gadm("IND"))
# map.Flag(label="Kashmir", value=gadm("Z01.14")) # , find_in_gadm=["IND"]
# map.Data(gadm="IND", value=100)
# map.Data(gadm="Z01.14", value=100) # , find_in_gadm=["IND"]

map.Flag(label="Z01", value=Z01)
# map.Data(gadm="Z01", value=100)

# Generate the map
map.show(out_json="tests/map_disputed.json", out_html="tests/map_disputed.html")