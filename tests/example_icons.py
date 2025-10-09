#!/usr/bin/env python3
"""
Example demonstrating custom marker icons with the Point feature.
"""

import xatra
from xatra import Icon
from xatra.loaders import gadm

# Create a map
map = xatra.FlagMap()
map.BaseOption("OpenStreetMap", default=True)
map.BaseOption("Esri.WorldImagery")
map.Flag(label="India", value=gadm("IND"))

# Example 1: Default marker (no custom icon)
map.Point(label="Default Marker", position=[28.6, 77.2])

# Example 2: Custom icon from URL
custom_icon = Icon(
    icon_url="https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png",
    icon_size=(25, 41),
    icon_anchor=(12, 41),
    popup_anchor=(1, -34),
    shadow_url="https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
    shadow_size=(41, 41)
)
map.Point(label="Custom Red Marker", position=[19.0, 73.0], icon=custom_icon)

# Example 3: Built-in icon (if available)
builtin_icon = Icon.builtin(
    "example.svg",
    icon_size=(32, 32),
    icon_anchor=(16, 16),
    popup_anchor=(0, -16)
)
map.Point(label="Built-in Icon Marker", position=[13.0, 80.2], icon=builtin_icon)

# Example 3.5: Checking that Example 3 is really at the right place
map.Point(label="Built-in Icon Marker", position=[13.0, 80.2])

# Example 4: Another custom icon with different size
large_icon = Icon(
    icon_url="https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-green.png",
    icon_size=(30, 49),
    icon_anchor=(15, 49),
    popup_anchor=(1, -40),
    shadow_url="https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
    shadow_size=(41, 41)
)
map.Point(label="Large Green Marker", position=[23.0, 72.6], icon=large_icon)

# Example 5: Icon without shadow
no_shadow_icon = Icon(
    icon_url="https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-blue.png",
    icon_size=(25, 41),
    icon_anchor=(12, 41),
    popup_anchor=(1, -34)
)
map.Point(label="Blue Marker (No Shadow)", position=[11.0, 77.0], icon=no_shadow_icon)

# Add a title
map.TitleBox("<b>Custom Marker Icons Example</b><br>Demonstrating different icon styles for Point markers")

# Export the map
map.show(out_json="tests/map_icons.json", out_html="tests/map_icons.html")
print("Map with custom icons exported to map_icons.html")

