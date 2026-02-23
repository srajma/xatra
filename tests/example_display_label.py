#!/usr/bin/env python3

import xatra
from xatra.loaders import gadm, naturalearth, polygon
from xatra.territory_library import *
from xatra.colorseq import LinearColorSequence
from matplotlib.colors import LinearSegmentedColormap

# xatra.set_debug_time(True)

# Create a test map
map = xatra.Map()
map.BaseOption("Esri.WorldTopoMap", default=True)

map.Flag(label="Maurya", display_label="Candragupta Maurya<br><span style='font-size:6px'>(early conquests)</span>", value=gadm("PAK") | gadm("AFG"), period=[-325,-320])
map.Flag(label="Maurya", display_label="Candragupta Maurya", value=NORTH_INDIA - KALINGA, period=[-320,-290])
map.Flag(label="Maurya", display_label="Candragupta Maurya", value=gadm("AFG"), period=[-320,-290])
map.Flag(label="Maurya", display_label="Bindusara", value=NORTH_INDIA | gadm("AFG") - KALINGA, period=[-290,-260])
map.Flag(label="Maurya", display_label="Bindusara<span style='font-size:6px'>(southern conquests)</span>", value=gadm("IND") - KALINGA, period=[-280,-260]) # new display_label should override old one for the period [-280, -260]
map.Flag(label="Maurya", display_label="Asoka", value=NORTH_INDIA | gadm("IND") | gadm("AFG"), period=[-260,-230])

map.Flag(label="Shunga", value=NORTH_INDIA, period=[-180, -100])
map.Flag(label="Shunga", display_label="Agnmitra", value=gadm("IND"), period=[-140, -100])

# expected behaviour:
# From -325 to -320: show "Candragupta Maurya<br><span style='font-size:6px'>(early conquests)</span>" over PAK + AFG
# From -320 to -290: show "Candragupta Maurya" over NORTH_INDIA - KALINGA + AFG
# From -290 to -280: show "Bindusara" over NORTH_INDIA - KALINGA + AFG
# From -280 to -260: show "Bindusara<span style='font-size:6px'>(southern conquests)</span>" over NORTH_INDIA + IND + AFG - KALINGA
# From -260 to -230: show "Asoka" over NORTH_INDIA + IND + AFG
# From -180 to -140: show "Shunga" over NORTH_INDIA
# From -140 to -100: show "Agnimitra" over NORTH_INDIA + IND


# Generate the map
map.show(out_json="tests/map.json", out_html="tests/map.html")
