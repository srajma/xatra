#!/usr/bin/env python3

import xatra
from xatra.loaders import gadm
import matplotlib.pyplot as plt

# Test default colormap
map = xatra.FlagMap()
map.BaseOption("OpenStreetMap", default=True)

# Test default colormap (should be yellow-orange-red)
print("Testing default colormap...")
map.Data("IND", 10, classes="test-data")
map.Data("PAK", 50, classes="test-data")
map.Data("CHN", 90, classes="test-data")

# Add some flags for comparison
map.Flag("India", gadm("IND"), note="Value: 10")
map.Flag("Pakistan", gadm("PAK"), note="Value: 50")
map.Flag("China", gadm("CHN"), note="Value: 90")

# Add a title
map.TitleBox("<b>Default Colormap Test</b><br>Should show yellow-orange-red color bar<br>India=yellow, Pakistan=orange, China=red")

# Export the map
map.show("test_default_colormap.json", "test_default_colormap.html")

print("Default colormap test completed! Check test_default_colormap.html")
print("✓ Should show yellow-orange-red color bar")
print("✓ India should be yellow (lowest value)")
print("✓ China should be red (highest value)")
print("✓ Pakistan should be orange (middle value)")

# Test custom colormap
print("\nTesting custom colormap...")
map2 = xatra.FlagMap()
map2.BaseOption("OpenStreetMap", default=True)
map2.DataColorMap(plt.cm.viridis)  # Custom colormap
map2.Data("IND", 10, classes="test-data")
map2.Data("PAK", 50, classes="test-data")
map2.Data("CHN", 90, classes="test-data")

map2.TitleBox("<b>Custom Colormap Test</b><br>Should show viridis color bar")
map2.show("test_custom_colormap.json", "test_custom_colormap.html")

print("Custom colormap test completed! Check test_custom_colormap.html")
print("✓ Should show viridis color bar")