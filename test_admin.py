#!/usr/bin/env python3

import xatra
from xatra.loaders import gadm, naturalearth
from xatra.territory_library import NORTHERN_INDIA

# Create a test map
map = xatra.FlagMap()
map.BaseOption("OpenStreetMap", default=True)
map.BaseOption("Esri.WorldImagery")
map.BaseOption("OpenTopoMap")
map.BaseOption("Esri.WorldPhysical")
map.Admin(gadm="IND.31", level=3)
map.Admin(gadm="IND.15", level=2)

# Generate the map
map.show()