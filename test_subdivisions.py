#!/usr/bin/env python3

import xatra
from xatra.loaders import gadm
import matplotlib.pyplot as plt

# Create a test map with subdivision data mapping
map = xatra.FlagMap()

# Set up base layers
map.BaseOption("OpenStreetMap", default=True)

# Set up a data colormap
map.DataColorMap(plt.cm.viridis, vmin=0, vmax=100)

# Test country-level data
map.Data("IND", 85.5, classes="country-data")
map.Data("PAK", 42.3, classes="country-data")

# Test state-level data (IND.12 should be a state in India)
map.Data("IND.12", 75.8, classes="state-data")
map.Data("IND.31", 68.2, classes="state-data")  # Tamil Nadu

# Test district-level data (if available)
map.Data("IND.31.1", 55.5, classes="district-data")

# Add some flags for comparison
map.Flag("India", gadm("IND"), note="Country level")
map.Flag("State 12", gadm("IND.12"), note="State level")
map.Flag("Tamil Nadu", gadm("IND.31"), note="Tamil Nadu state")

# Add a title
map.TitleBox("<b>Subdivision Data Mapping Test</b><br>Testing country, state, and district level data")

# Export the map
map.show("test_subdivisions.json", "test_subdivisions.html")

print("Subdivision data mapping test completed! Check test_subdivisions.html")
print("Should show data for country (IND), state (IND.12, IND.31), and district (IND.31.1) levels")