#!/usr/bin/env python3
"""
Test multi-layer tooltip functionality with rivers.
"""

import xatra
from xatra.loaders import gadm

# Create a map with flags, admin regions, and rivers
map = xatra.FlagMap()
map.BaseOption("OpenStreetMap", default=True)

# Add a flag
map.Flag(label="Tamil Nadu", value=gadm("IND.31"), note="State in southern India")

# Add admin regions
map.Admin(gadm="IND.31", level=2, classes="districts")

# Add rivers - these should appear in tooltips when you hover over them
map.AdminRivers(sources=["naturalearth", "overpass"], classes="all-rivers")

# Add a path that might overlap with rivers
map.Path(label="Trade Route", value=[[12, 78], [13, 80], [14, 82]])

# Add points
map.Point(label="Chennai", position=[13.0827, 80.2707])

# Add title
map.TitleBox("<b>Multi-Layer Tooltip with Rivers</b><br>Hover over rivers to see their tooltips appear!")

# Add CSS
map.CSS("""
.flag { stroke: #333; stroke-width: 1; fill-opacity: 0.3; }
.admin { stroke: #666; stroke-width: 0.5; fill-opacity: 0.2; }
.admin-river { stroke: #0066cc; stroke-width: 2; opacity: 0.8; }
.all-rivers { stroke-width: 3; }
.path { stroke: #8B4513; stroke-width: 3; stroke-dasharray: 5 5; }

#multi-tooltip {
  font-family: Arial, sans-serif;
  max-width: 500px;
}

#multi-tooltip .tooltip-type {
  color: #cc6600;
  font-weight: bold;
  font-size: 12px;
}
""")

# Export the map
map.show(out_json="tests/map_multi_tooltip_rivers.json", out_html="tests/map_multi_tooltip_rivers.html")
print("Multi-layer tooltip test map with rivers exported!")
print("Open tests/map_multi_tooltip_rivers.html and hover over:")
print("  - Rivers (should show river name and source)")
print("  - Admin regions (should show district info)")
print("  - Flags (should show Tamil Nadu)")
print("  - Where they overlap (should show ALL tooltips)")

