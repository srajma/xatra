#!/usr/bin/env python3
"""
Test script to verify AdminRivers show_label and n_labels functionality.
"""

import xatra
from xatra.loaders import gadm

# Create a map
map = xatra.Map()
map.BaseOption("OpenStreetMap", default=True)
map.Flag(label="India", value=gadm("IND"))

# Test AdminRivers with labels
map.AdminRivers(show_label=True, n_labels=2, classes="test-rivers")

# Add a title
map.TitleBox("<b>AdminRivers Label Test</b><br>Admin rivers should have labels distributed along their length")

# Export the map
map.show(out_json="tests/map_adminrivers_labels.json", out_html="tests/map_adminrivers_labels.html")
print("Map with AdminRivers labels exported to tests/map_adminrivers_labels.html")
