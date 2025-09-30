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

# map.Admin(gadm="IND", level=0)
# map.Admin(gadm="IND", level=0)
# map.Admin(gadm="Z01.14", level=3) # , find_in_gadm=["IND"]
# map.Flag(label="India", value=gadm("IND"))
# map.Flag(label="Kashmir", value=gadm("Z01.14")) # , find_in_gadm=["IND"]
# map.Data(gadm="IND", value=100)
# map.Data(gadm="Z01.14", value=100) # , find_in_gadm=["IND"]

map.Admin(gadm="Z01", level=1)
map.Admin(gadm="Z02", level=1)
map.Admin(gadm="Z03", level=1)
map.Admin(gadm="Z04", level=1)
map.Admin(gadm="Z05", level=1)
map.Admin(gadm="Z06", level=1)
map.Admin(gadm="Z07", level=1)
map.Admin(gadm="Z08", level=1)
map.Admin(gadm="Z09", level=1)
# map.Flag(label="Z01", value=gadm("Z01"))
# map.Data(gadm="Z01", value=100)

# Generate the map
map.show(out_json="map_disputed.json", out_html="map_disputed.html")