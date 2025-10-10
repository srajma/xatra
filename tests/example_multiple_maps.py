#!/usr/bin/env python3
"""
Example demonstrating multiple maps with pyplot-style interface.

This example shows how to create and switch between multiple maps
using new_map(), set_current_map(), and get_current_map().
"""

import xatra
from xatra.loaders import gadm

# Create first map
map1 = xatra.new_map()
xatra.Flag(label="India", value=gadm("IND"))
xatra.Flag(label="Pakistan", value=gadm("PAK"))
xatra.TitleBox("<b>Map 1: India and Pakistan</b>")
xatra.show(out_json="tests/map_multi1.json", out_html="tests/map_multi1.html")
print("Map 1 exported to tests/map_multi1.html")

# Create second map
map2 = xatra.new_map()
xatra.Flag(label="Bangladesh", value=gadm("BGD"))
xatra.Flag(label="Nepal", value=gadm("NPL"))
xatra.TitleBox("<b>Map 2: Bangladesh and Nepal</b>")
xatra.show(out_json="tests/map_multi2.json", out_html="tests/map_multi2.html")
print("Map 2 exported to tests/map_multi2.html")

# Switch back to first map and add more elements
xatra.set_current_map(map1)
xatra.Flag(label="Afghanistan", value=gadm("AFG"))
xatra.TitleBox("<b>Map 1 (updated): India, Pakistan, and Afghanistan</b>")
xatra.show(out_json="tests/map_multi1_updated.json", out_html="tests/map_multi1_updated.html")
print("Updated Map 1 exported to tests/map_multi1_updated.html")

# Verify we're on the right map
current = xatra.get_current_map()
print(f"Current map has {len(current._flags)} flags")

