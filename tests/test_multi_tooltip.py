#!/usr/bin/env python3
"""
Test multi-layer tooltip functionality.

This test creates overlapping map elements (flags, rivers, points) to demonstrate
the multi-layer tooltip system that shows information for all elements under the cursor.
"""

import xatra
from xatra.loaders import gadm, naturalearth

# Create a map with overlapping elements
map = xatra.FlagMap()
map.BaseOption("OpenStreetMap", default=True)

# Add overlapping flags (countries/regions)
map.Flag(label="India", value=gadm("IND"), note="Republic of India")
map.Flag(label="Tamil Nadu", value=gadm("IND.31"), note="State in southern India")

# Add points in the overlapping area - these will overlap with the flag regions
map.Point(label="Chennai", position=[13.0827, 80.2707], hover_radius=20)
map.Point(label="Bangalore", position=[12.9716, 77.5946], hover_radius=5)

# Add a path that crosses through
map.Path(label="Historical Trade Route", value=[[12, 75], [13, 80], [14, 82]])

# Add title explaining the feature
map.TitleBox("<b>Multi-Layer Tooltip Demo</b><br>Hover over overlapping regions to see tooltips for all elements at the cursor position.")

# Add some CSS to make tooltips more visible
map.CSS("""
.flag { stroke: #333; stroke-width: 1; fill-opacity: 0.5; }
.path { stroke: #8B4513; stroke-width: 2; stroke-dasharray: 5 5; }

/* Multi-tooltip styling can be customized */
#multi-tooltip {
  font-family: Arial, sans-serif;
  max-width: 450px;
}

#multi-tooltip .tooltip-type {
  color: #cc6600;
  font-weight: bold;
  font-size: 12px;
}

#multi-tooltip .tooltip-content {
  font-size: 13px;
  line-height: 1.4;
}
""")

# Export the map
map.show(out_json="tests/map_multi_tooltip.json", out_html="tests/map_multi_tooltip.html")
print("Multi-layer tooltip test map exported to tests/map_multi_tooltip.html")
print("Open the HTML file and hover over overlapping regions to see the multi-layer tooltips!")

