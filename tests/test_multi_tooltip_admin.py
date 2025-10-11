#!/usr/bin/env python3
"""
Test multi-layer tooltip functionality with Admin regions and DataFrames.

This test creates overlapping admin regions and dataframes to verify
the multi-layer tooltip system works for all element types.
"""

import pandas as pd
import xatra
from xatra.loaders import gadm

# Create a map with admin regions
map = xatra.FlagMap()
map.BaseOption("OpenStreetMap", default=True)

# Add a flag for context
map.Flag(label="Tamil Nadu", value=gadm("IND.31"), note="State in southern India")

# Add admin regions at district level - these will overlap with the flag
map.Admin(gadm="IND.31", level=2, classes="districts")

# Add a DataFrame with data - this will also overlap
df = pd.DataFrame({
    'GID': ['IND.31.1', 'IND.31.2', 'IND.31.3'],
    'population': [4646732, 2818997, 3847334],
    'note': ['Chennai district', 'Coimbatore district', 'Madurai district']
})
df.set_index('GID', inplace=True)
map.Dataframe(df)

# Add points that will overlap with everything
map.Point(label="Chennai City", position=[13.0827, 80.2707])
map.Point(label="Coimbatore City", position=[11.0168, 76.9558])

# Add a path crossing through
map.Path(label="NH-44 Highway", value=[[13.0, 80.0], [11.5, 78.0], [10.5, 77.0]])

# Add title explaining the feature
map.TitleBox("<b>Multi-Layer Tooltip Demo with Admin & DataFrames</b><br>Hover over regions to see tooltips for Flags, Admin regions, and DataFrames all at once!")

# Add some CSS
map.CSS("""
.flag { stroke: #333; stroke-width: 2; fill-opacity: 0.3; }
.admin { stroke: #666; stroke-width: 1; fill-opacity: 0.2; }
.data { stroke: #000; stroke-width: 1; }
.path { stroke: #8B4513; stroke-width: 3; stroke-dasharray: 5 5; }

/* Multi-tooltip styling */
#multi-tooltip {
  font-family: Arial, sans-serif;
  max-width: 500px;
}

#multi-tooltip .tooltip-type {
  color: #cc6600;
  font-weight: bold;
  font-size: 12px;
}

#multi-tooltip .tooltip-content {
  font-size: 13px;
  line-height: 1.5;
}
""")

# Export the map
map.show(out_json="tests/map_multi_tooltip_admin.json", out_html="tests/map_multi_tooltip_admin.html")
print("Multi-layer tooltip test map with Admin & DataFrames exported!")
print("Open tests/map_multi_tooltip_admin.html and hover over Chennai district to see:")
print("  - Flag tooltip (Tamil Nadu)")
print("  - Admin Region tooltip (district name and GID)")
print("  - DataFrame tooltip (population data)")
print("  - Point tooltip (if you hover near Chennai City)")

