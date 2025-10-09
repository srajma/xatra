#!/usr/bin/env python3

"""
Example demonstrating custom point icons in Xatra.
"""

import xatra
from xatra import Icon
from xatra.loaders import gadm

map = xatra.FlagMap()
map.BaseOption("OpenStreetMap", default=True)
map.BaseOption("Esri.WorldImagery")
map.BaseOption("OpenTopoMap")
map.BaseOption("Esri.WorldPhysical")

# Add a simple flag for context
map.Flag(label="India", value=gadm("IND"))

# Point with default icon (no icon parameter specified)
map.Point(label="Delhi (Default)", position=[28.6139, 77.2090])

# Point with default built-in icon (explicitly specified)
default_icon = Icon(
    icon_url="marker-icon.png",
    shadow_url="marker-shadow.png"
)
map.Point(label="Mumbai (Also Default)", position=[19.0760, 72.8777], icon=default_icon)

# Point with built-in icon but custom size and positioning
large_icon = Icon(
    icon_url="marker-icon.png",
    shadow_url="marker-shadow.png",
    icon_size=[25, 41],      # Standard size
    shadow_size=[41, 41],     # Standard shadow size
    icon_anchor=[12, 41],     # Point that corresponds to marker location
    shadow_anchor=[4, 62],    # Point for shadow position
    popup_anchor=[1, -34]     # Popup offset from icon anchor
)
map.Point(label="Kolkata (Custom Size)", position=[22.5726, 88.3639], icon=large_icon)

# Point with custom URL (user could provide their own icon path here)
# This demonstrates the API - in real use, provide actual file paths
custom_url_icon = Icon(
    icon_url="https://example.com/custom-icon.png",  # Replace with real path/URL
    shadow_url="https://example.com/custom-shadow.png",
    icon_size=[30, 50],
    icon_anchor=[15, 50],
    popup_anchor=[-3, -50]
)
map.Point(label="Bangalore (Custom URL)", position=[12.9716, 77.5946], icon=custom_url_icon)

map.TitleBox("<b>Example: Custom Point Markers</b><br>Demonstrating different marker icon configurations")

map.show(out_json="tests/map_point_icon.json", out_html="tests/map_point_icon.html")

