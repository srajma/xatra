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
# SOUTH ASIA
map.Admin(gadm="IND", level=2)
map.Admin(gadm="PAK", level=2)
map.Admin(gadm="BGD", level=1)
map.Admin(gadm="NPL", level=1)
map.Admin(gadm="AFG", level=1)
map.Admin(gadm="LKA", level=1)
map.Admin(gadm="MDV", level=0)
map.Admin(gadm="BTN", level=0)

# Generate the map
map.show(out_json="map_admin.json", out_html="map_admin.html")