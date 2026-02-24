#!/usr/bin/env python3
"""
Example demonstrating standard icon-library usage for Point markers.
"""

import xatra
from xatra import Icon
from xatra.loaders import gadm

# Create a map
map = xatra.Map()
map.BaseOption("Esri.WorldTopoMap", default=True)
map.BaseOption("Esri.WorldImagery")
map.Flag(label="India", value=gadm("IND"))

# Bootstrap Icons (default center anchor)
capital_icon = Icon.bootstrap("building", icon_size=26)
map.Point(label="Capital", position=[28.6, 77.2], icon=capital_icon)

temple_icon = Icon.bootstrap("bank2", icon_size=26)
map.Point(label="Temple Complex", position=[19.0, 73.0], icon=temple_icon)

port_icon = Icon.bootstrap("anchor-fill", icon_size=24)
map.Point(label="Port", position=[13.0, 80.2], icon=port_icon)

trade_icon = Icon.bootstrap("signpost-split-fill", icon_size=24)
map.Point(label="Trade Junction", position=[23.0, 72.6], icon=trade_icon)

# Explicit anchor override: bottom-center for a pin-like feel
town_icon = Icon.bootstrap(
    "geo-alt-fill",
    icon_size=24,
    icon_anchor=(12, 24),
    popup_anchor=(0, -20),
)
map.Point(label="Town", position=[12.3, 76.6], icon=town_icon)

# Leaflet built-in markers are still available
leaflet_marker = Icon.builtin("marker-icon-red.png")
map.Point(label="Leaflet Marker", position=[17.4, 78.5], icon=leaflet_marker)

icon = Icon.geometric("circle", color="red", size=24)
map.Point("Geometric Marker", [30, 77.2], icon=icon)

map.TitleBox("<b>Icon Examples</b><br>Bootstrap Icons plus Leaflet marker built-ins")
map.show(out_json="tests/map_builtin_icons.json", out_html="tests/map_builtin_icons.html")
print("Map with icon examples exported to map_builtin_icons.html")
