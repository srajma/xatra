#!/usr/bin/env python3
"""
Test hover_radius parameter for Point, River, and Path elements.

This test demonstrates how to customize the hover detection radius
to make elements easier to interact with.
"""

import xatra
from xatra.loaders import gadm

# Create a map
map = xatra.FlagMap()
map.BaseOption("OpenStreetMap", default=True)

# Add a flag for context
map.Flag(label="India", value=gadm("IND"))

# Add paths with different hover radii
map.Path(label="Path (default 10px)", value=[[20, 75], [22, 77]], classes="path-default")
map.Path(label="Path (20px radius)", value=[[21, 75], [23, 77]], hover_radius=20, classes="path-large")
map.Path(label="Path (5px radius)", value=[[22, 75], [24, 77]], hover_radius=5, classes="path-small")

# Add points with different hover radii
map.Point(label="Point (default 20px)", position=[25, 80])
map.Point(label="Point (40px radius)", position=[26, 80], hover_radius=40)
map.Point(label="Point (10px radius)", position=[27, 80], hover_radius=10)

# Add rivers with different hover radii (using AdminRivers for demonstration)
map.AdminRivers(sources=["naturalearth"], classes="default-rivers")

# Add title
map.TitleBox("""
<b>Hover Radius Test</b><br>
<ul style="margin: 5px 0; padding-left: 20px;">
<li>Paths have different hover radii (5px, 10px, 20px)</li>
<li>Points have different hover radii (10px, 20px, 40px)</li>
<li>Rivers use default 10px (can be customized)</li>
</ul>
Try hovering over each element to see how hover radius affects selection ease.
""")

# Add CSS to distinguish different elements
map.CSS("""
.path-default { stroke: #0066cc; stroke-width: 2; }
.path-large { stroke: #cc6600; stroke-width: 2; }
.path-small { stroke: #00cc66; stroke-width: 2; }

#multi-tooltip {
  font-family: Arial, sans-serif;
  max-width: 500px;
}
""")

# Export the map
map.show(out_json="tests/map_hover_radius.json", out_html="tests/map_hover_radius.html")
print("Hover radius test map exported to tests/map_hover_radius.html")
print("\nTest the different hover radii:")
print("  - Try hovering over the paths with different colors")
print("  - Notice how the larger hover_radius makes selection easier")
print("  - The multi-layer tooltip shows all overlapping elements")

