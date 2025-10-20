#!/usr/bin/env python3

import xatra
from xatra.loaders import gadm, naturalearth
from xatra.colorseq import LinearColorSequence, Color

# Create a test map
map = xatra.Map()
map.BaseOption("Esri.WorldTopoMap", default=True)
map.BaseOption("Esri.WorldImagery")
map.BaseOption("OpenTopoMap")
map.BaseOption("Esri.WorldPhysical")

map.FlagColorSequence(LinearColorSequence(colors=[Color.hex("#ff0000")], step=Color.hsl(0.03, 0.0, 0.0)), class_name="hindu")
map.FlagColorSequence(LinearColorSequence(colors=[Color.hex("#00ff00")], step=Color.hsl(0.03, 0.0, 0.0)), class_name="muslim")
map.FlagColorSequence(LinearColorSequence(colors=[Color.hex("#0000ff")]))

# map.FlagColorSequence(LinearColorSequence(colors=[Color.hex("#ff0000")], step=Color.hsl(0.03, 0.0, 0.0)))
map.Flag(label="Vijayanagara", value=gadm("IND.16") | gadm("IND.2") | gadm("IND.32") | gadm("IND.31") | gadm("IND.17"), classes="hindu")
map.Flag(label="Yadava", value=gadm("IND.20"), classes="hindu")
map.Flag(label="Rajput", value=gadm("IND.29"), classes="hindu")

# current_color = map._color_sequence[-1]
# map.FlagColorSequence(LinearColorSequence(colors=[Color.hex("#00ff00")], step=Color.hsl(0.03, 0.0, 0.0)))

map.Flag(label="Mughal", value=gadm("IND.25") | gadm("IND.12") | gadm("IND.34"), classes="muslim")
map.Flag(label="Ahmedabad", value=gadm("IND.11"), classes="muslim")
map.Flag(label="Bhopal", value=gadm("IND.19"), classes="muslim")

# map._flag_index += 1
map.Flag(label="Gajapati", value=gadm("IND.26"), classes="hindu")

map.Flag(label="Myanmar", value=gadm("MMR"))
map.Flag(label="Somali", value=gadm("SOM"), classes="china")

# Generate the map
map.show(out_json="tests/map_colorgroups.json", out_html="tests/map_colorgroups.html")