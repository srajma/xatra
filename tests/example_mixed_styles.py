#!/usr/bin/env python3
"""
Example demonstrating mixing explicit FlagMap and pyplot-style interfaces.
"""

import xatra
from xatra.loaders import gadm

# Start with explicit FlagMap
map = xatra.FlagMap()
map.Flag(label="India", value=gadm("IND"))
map.Flag(label="Pakistan", value=gadm("PAK"))

# Now switch to pyplot-style with the same map
xatra.set_current_map(map)
xatra.Flag(label="Bangladesh", value=gadm("BGD"))
xatra.TitleBox("<b>Mixed Styles Example</b><br>India and Pakistan added with map.Flag(), Bangladesh with xatra.Flag()")

# Export using pyplot-style
xatra.show(out_json="tests/map_mixed.json", out_html="tests/map_mixed.html")
print("Mixed styles map exported to tests/map_mixed.html")

# Verify all three flags are present
print(f"Total flags: {len(map._flags)}")
print(f"Flag labels: {[f.label for f in map._flags]}")

