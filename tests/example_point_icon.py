#!/usr/bin/env python3
"""
Example demonstrating custom marker icons for Points.
"""

import xatra
from xatra import MarkerIcon

map = xatra.FlagMap()
map.BaseOption("OpenStreetMap", default=True)
map.BaseOption("Esri.WorldImagery")

# Default marker icon (uses local icons/marker-icon.png)
map.Point(label="Delhi (Default)", position=[28.6139, 77.2090])

# Custom icon with just URL
custom_icon1 = MarkerIcon(
    icon_url='icons/marker-icon.png',
    shadow_url='icons/marker-shadow.png'
)
map.Point(label="Mumbai (Custom)", position=[19.0760, 72.8777], icon=custom_icon1)

# Custom icon with all properties
custom_icon2 = MarkerIcon(
    icon_url='icons/marker-icon.png',
    shadow_url='icons/marker-shadow.png',
    icon_size=[25, 41],
    shadow_size=[41, 41],
    icon_anchor=[12, 41],
    shadow_anchor=[4, 62],
    popup_anchor=[1, -34]
)
map.Point(label="Kolkata (Fully Custom)", position=[22.5726, 88.3639], icon=custom_icon2)

map.TitleBox("<b>Example: Custom Point Markers</b><br>Demonstrating different marker icon configurations")

map.show(out_json="map_point_icon.json", out_html="map_point_icon.html")

