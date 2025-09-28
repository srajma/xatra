#!/usr/bin/env python3

import xatra
from xatra.loaders import gadm
from matplotlib.colors import LinearSegmentedColormap

# Test with the user's original example but using default colormap
map = xatra.FlagMap()
map.BaseOption("OpenStreetMap", default=True)

# User's example - no explicit DataColorMap call, should use default
map.Data(gadm="IND", value=100)
map.Data(gadm="CHN", value=300, period=[0, 600])
map.Data(gadm="PAK", value=300, period=[0, 600])
map.Data(gadm="CHN", value=1000, period=[600, 700])
map.Data(gadm="PAK", value=1000, period=[600, 700])

# Add flags without periods
map.Flag("India", gadm("IND"), note="Always 100")
map.Flag("China", gadm("CHN"), note="300 (0-600), 1000 (600-700)")
map.Flag("Pakistan", gadm("PAK"), note="300 (0-600), 1000 (600-700)")

# Add a title
map.TitleBox("<b>User Example with Default Colormap</b><br>Should show yellow-orange-red color bar<br>Map should be dynamic with slider")

# Set up time slider
map.slider(0, 700, speed=10.0)

# Export the map
map.show("test_user_default.json", "test_user_default.html")

print("User example with default colormap completed! Check test_user_default.html")
print("✓ Should use default yellow-orange-red colormap")
print("✓ Should show color bar")
print("✓ Map should be dynamic with slider")
print("✓ China and Pakistan should show 300 from 0-600, then 1000 from 600-700")