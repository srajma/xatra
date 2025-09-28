#!/usr/bin/env python3

import xatra
from xatra.loaders import gadm
from matplotlib.colors import LinearSegmentedColormap

# Test the specific case mentioned by the user
map = xatra.FlagMap()
map.BaseOption("OpenStreetMap", default=True)

# Test with exact range and subdivision
map.DataColorMap(LinearSegmentedColormap.from_list("custom_cmap", ["#000000", "#ffffff"]), 100, 1001)
map.Data(gadm="IND", value=100)
map.Data(gadm="IND.12", value=300, period=[0, 600])  # This should work now
map.Data(gadm="CHN", value=300, period=[0, 600])
map.Data(gadm="PAK", value=300, period=[0, 600])
map.Data(gadm="CHN", value=1000, period=[600, 700])
map.Data(gadm="PAK", value=1000, period=[600, 700])

# Add some flags for comparison
map.Flag("India", gadm("IND"), note="Always 100")
map.Flag("India State 12", gadm("IND.12"), note="300 (0-600)")
map.Flag("China", gadm("CHN"), note="300 (0-600), 1000 (600-700)")
map.Flag("Pakistan", gadm("PAK"), note="300 (0-600), 1000 (600-700)")

# Add a title
map.TitleBox("<b>IND.12 Subdivision Test</b><br>Testing subdivision data mapping with IND.12")

# Set up time slider
map.slider(0, 700, speed=10.0)

# Export the map
map.show("test_ind12.json", "test_ind12.html")

print("IND.12 subdivision test completed! Check test_ind12.html")
print("IND.12 should show value 300 from years 0-600")