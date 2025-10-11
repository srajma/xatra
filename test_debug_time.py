#!/usr/bin/env python3
"""
Test script to demonstrate the time debugging feature in xatra.

This script creates a simple map and enables time debugging to show
all the timing information for each operation.
"""

import xatra
from xatra.loaders import gadm, naturalearth

# Enable time debugging
xatra.set_debug_time(True)
# xatra.DEBUG_TIME = True

print("=" * 60)
print("Testing xatra time debugging feature")
print("=" * 60)
print()

# Create a simple map
map = xatra.FlagMap()

# Add some elements (each will be timed)
map.Flag(label="India", value=gadm("IND"))
map.Flag(label="Pakistan", value=gadm("PAK"))

# Add a river (this will show timing for loading Natural Earth data)
try:
    map.River(label="Test River", value=naturalearth("1159122643"))
except Exception as e:
    print(f"Note: River loading failed (expected if data not available): {e}")

# Add other elements
map.Point(label="Delhi", position=[28.6, 77.2])
map.Text(label="South Asia", position=[20, 75])
map.TitleBox("<b>Test Map for Time Debugging</b>")

# Export (this will show timing for the entire export process)
map.show(out_json="test_debug_map.json", out_html="test_debug_map.html")

print()
print("=" * 60)
print("Time debugging test complete!")
print("Map exported to test_debug_map.html")
print("=" * 60)

