#!/usr/bin/env python3
"""
Example demonstrating the show_label and n_labels parameters for Points, Paths, and Rivers.
"""

import xatra
from xatra.loaders import gadm, naturalearth

# Create a map
map = xatra.FlagMap()
map.BaseOption("OpenStreetMap", default=True)
map.BaseOption("Esri.WorldImagery")
map.Flag(label="India", value=gadm("IND"))

# Rivers with and without show_label
map.River(label="Ganga", value=naturalearth("1159122643"), show_label=True, n_labels=5, classes="sacred")

# Points with and without show_label
map.Point(label="Mumbai (tooltip only)", position=[19.0, 73.0])
map.Point(label="Delhi", position=[28.6, 77.2], show_label=True)
map.Point(label="Kolkata", position=[22.5, 88.3], show_label=True)
map.Point(label="Chennai", position=[13.0, 80.2], show_label=True)

# Paths with and without show_label
map.Path(label="Northern Route (tooltip)", value=[[28.6, 77.2], [30.3, 78.0], [34.0, 74.8]])
map.Path(label="Silk Road", value=[[28.6, 77.2], [32.0, 75.0], [35.5, 78.0], [39.0, 76.0]], show_label=True, n_labels=2)
map.Path(label="Coastal Route", value=[[19.0, 73.0], [15.3, 74.1], [13.0, 80.2], [11.0, 76.0]], show_label=True, classes="coastal", n_labels=3)

# Add custom CSS for styling
map.CSS("""
.coastal.path-label {
  color: rgb(0, 153, 51);
/*  background: rgba(255, 255, 255, 0.7); */
}

.coastal {
  stroke: rgb(0, 153, 51);
  stroke-width: 3;
}

.sacred.river {
  stroke: #ff6600;
  stroke-width: 2.5;
}

.sacred .river-label {
  color: #ff6600;
  border-color: #ff6600;
  font-size: 16px;
  font-weight: bold;
}
""")

# Add a title
map.TitleBox("<b>Point, Path, and River Labels Example</b><br>Demonstrating show_label and n_labels parameters")

# Export the map
map.show(out_json="tests/map_labels.json", out_html="tests/map_labels.html")
print("Map with point, path, and river labels exported to tests/map_labels.html")

