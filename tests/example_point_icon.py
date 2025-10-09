#!/usr/bin/env python3
"""
Example demonstrating custom marker icons for Points.
"""

import xatra
from xatra import MarkerIcon

map = xatra.FlagMap()
map.BaseOption("OpenStreetMap", default=True)
map.BaseOption("Esri.WorldImagery")

# Default marker icon (uses data URI from package)
map.Point(label="Delhi (Default)", position=[28.6139, 77.2090])

# Default marker icon but with explicit MarkerIcon() - still uses data URIs
custom_icon1 = MarkerIcon()
map.Point(label="Mumbai (Also Default)", position=[19.0760, 72.8777], icon=custom_icon1)

# Custom icon with all size properties but still using default icon images
custom_icon2 = MarkerIcon(
    icon_size=[25, 41],
    shadow_size=[41, 41],
    icon_anchor=[12, 41],
    shadow_anchor=[4, 62],
    popup_anchor=[1, -34]
)
map.Point(label="Kolkata (Custom Size)", position=[22.5726, 88.3639], icon=custom_icon2)

# Custom icon with external URL (for your own custom icons)
custom_icon3 = MarkerIcon(
    icon_url='https://example.com/custom-icon.png',
    shadow_url='https://example.com/custom-shadow.png',
    icon_size=[30, 50],
    icon_anchor=[15, 50]
)
map.Point(label="Bangalore (Custom URL)", position=[12.9716, 77.5946], icon=custom_icon3)

map.TitleBox("<b>Example: Custom Point Markers</b><br>Demonstrating different marker icon configurations")

map.show(out_json="map_point_icon.json", out_html="map_point_icon.html")

