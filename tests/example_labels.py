#!/usr/bin/env python3
"""
Example demonstrating the show_label parameter for Points and Paths.
"""

import xatra
from xatra.loaders import gadm

# Create a map
map = xatra.FlagMap()
map.BaseOption("OpenStreetMap", default=True)
map.BaseOption("Esri.WorldImagery")
map.Flag(label="India", value=gadm("IND"))

# Points with and without show_label
map.Point(label="Mumbai (tooltip only)", position=[19.0, 73.0])
map.Point(label="Delhi", position=[28.6, 77.2], show_label=True)
map.Point(label="Kolkata", position=[22.5, 88.3], show_label=True)
map.Point(label="Chennai", position=[13.0, 80.2], show_label=True)

# Paths with and without show_label
map.Path(label="Northern Route (tooltip)", value=[[28.6, 77.2], [30.3, 78.0], [34.0, 74.8]])
map.Path(label="Silk Road", value=[[28.6, 77.2], [32.0, 75.0], [35.5, 78.0], [39.0, 76.0]], show_label=True)
map.Path(label="Coastal Route", value=[[19.0, 73.0], [15.3, 74.1], [13.0, 80.2], [11.0, 76.0]], show_label=True, classes="coastal")

# Add custom CSS for styling
map.CSS("""
/*.point-label {
  font-size: 13px;
  font-weight: bold;
  color: #cc0000;
  background: rgba(255,255,255,0.85);
  padding: 3px 7px;
  border-radius: 4px;
  border: 1px solid #cc0000;
}

.path-label {
  font-size: 14px;
  color: #0066cc;
  font-style: italic;
  background: rgba(255,255,255,0.9);
  padding: 4px 8px;
  border-radius: 4px;
  border: 1px solid #0066cc;
}*/

.coastal.path-label {
  color: #009933 !important;
  border-color: #009933;
}

.coastal {
  stroke: #009933;
  stroke-width: 3;
}
""")

# Add a title
map.TitleBox("<b>Point and Path Labels Example</b><br>Demonstrating show_label parameter for Points and Paths")

# Export the map
map.show(out_json="tests/map_labels.json", out_html="tests/map_labels.html")
print("Map with point and path labels exported to tests/map_labels.html")

