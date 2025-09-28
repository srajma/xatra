#!/usr/bin/env python3

import xatra
from xatra.loaders import gadm, naturalearth
from xatra.territory_library import NORTHERN_INDIA
from xatra.colorseq import LinearColorSequence, Color
from matplotlib.colors import LinearSegmentedColormap

# Create a test map
map = xatra.FlagMap()
map.BaseOption("OpenStreetMap", default=True)
map.BaseOption("Esri.WorldImagery")
map.BaseOption("OpenTopoMap")
map.BaseOption("Esri.WorldPhysical")

map.FlagColorSequence(LinearColorSequence(colors=[Color.hex("#ff0000")], step=Color.hsl(0.05, 0.0, 0.0)))
map.Flag(label="Vijayanagara", value=gadm("IND.16") | gadm("IND.2") | gadm("IND.32") | gadm("IND.31") | gadm("IND.17"))
map.Flag(label="Yadava", value=gadm("IND.20"))
map.Flag(label="Rajput", value=gadm("IND.29"))

map.FlagColorSequence(LinearColorSequence(colors=[Color.hex("#00ff00")], step=Color.hsl(0.05, 0.0, 0.0)))
map.Flag(label="Mughal", value=gadm("IND.25") | gadm("IND.12") | gadm("IND.34"))
map.Flag(label="Ahmedabad", value=gadm("IND.11"))
map.Flag(label="Bhopal", value=gadm("IND.19"))

# Generate the map
map.show(out_json="map_colorgroups.json", out_html="map_colorgroups.html")