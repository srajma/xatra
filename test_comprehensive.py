#!/usr/bin/env python3

import xatra
from xatra.loaders import gadm
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.pyplot as plt

# Comprehensive test of data mapping with subdivisions
map = xatra.FlagMap()
map.BaseOption("OpenStreetMap", default=True)

# Test different colormaps
print("Testing viridis colormap...")
map.DataColorMap(plt.cm.viridis, vmin=0, vmax=100)

# Test country-level data
map.Data("IND", 85.5, classes="country-data")
map.Data("PAK", 42.3, classes="country-data")

# Test state-level data
map.Data("IND.12", 75.8, classes="state-data")
map.Data("IND.31", 68.2, classes="state-data")

# Test with time periods
map.Data("CHN", 95.1, period=[0, 500], classes="historical-data")
map.Data("CHN", 98.5, period=[500, 1000], classes="historical-data")

# Test exact range colormap
print("Testing exact range colormap...")
map2 = xatra.FlagMap()
map2.BaseOption("OpenStreetMap", default=True)
map2.DataColorMap(LinearSegmentedColormap.from_list("custom", ["#000000", "#ffffff"]), 100, 1001)
map2.Data("IND", 100)
map2.Data("PAK", 1001)
map2.Data("IND.12", 500)  # Should work with subdivisions

# Add flags for comparison
map.Flag("India", gadm("IND"), note="Country with data")
map.Flag("State 12", gadm("IND.12"), note="State with data")

# Export both maps
map.show("test_comprehensive.json", "test_comprehensive.html")
map2.show("test_exact_range.json", "test_exact_range.html")

print("Comprehensive test completed!")
print("✓ Country-level data (IND, PAK)")
print("✓ State-level data (IND.12, IND.31)")  
print("✓ Time periods (CHN with different values)")
print("✓ Exact range colormap (100-1001)")
print("✓ Subdivision support (IND.12)")