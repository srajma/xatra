#!/usr/bin/env python3
"""
Test script to verify flag label rotation works with various geometries.
"""

import xatra
from xatra.loaders import gadm

# Create a map
map = xatra.FlagMap()
map.BaseOption("OpenStreetMap", default=True)
map.Flag(label="India", value=gadm("IND"))

# Add some flags with different geometries to test rotation
map.Flag(label="Tamil Nadu", value=gadm("IND.31"), note="Southern state - should be oriented roughly N-S")
map.Flag(label="Rajasthan", value=gadm("IND.24"), note="Western state - should be oriented roughly E-W")
map.Flag(label="West Bengal", value=gadm("IND.28"), note="Eastern state - should be oriented roughly N-S")
map.Flag(label="Gujarat", value=gadm("IND.09"), note="Western state - should be oriented roughly E-W")

# Add a title
map.TitleBox("<b>Flag Label Rotation Test</b><br>Flag labels should be oriented along the dominant direction of their geometries")

# Export the map
map.show(out_json="tests/map_flag_rotation.json", out_html="tests/map_flag_rotation.html")
print("Map with flag rotation test exported to tests/map_flag_rotation.html")
