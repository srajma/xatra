#!/usr/bin/env python3
"""
Example demonstrating built-in marker icons with the Point feature.
"""

import xatra
from xatra import Icon
from xatra.loaders import gadm

# Create a map
map = xatra.FlagMap()
map.BaseOption("OpenStreetMap", default=True)
map.BaseOption("Esri.WorldImagery")

# Add a flag for context
map.Flag(label="India", value=gadm("IND"))

# Example 1: Ancient city with gavaksha architecture
city_icon = Icon.builtin(
    "city.png",
    icon_size=(32, 32),
    icon_anchor=(16, 16),
    popup_anchor=(0, -16)
)
map.Point(label="Ancient City", position=[28.6, 77.2], icon=city_icon)

# Example 2: Temple with traditional architecture
temple_icon = Icon.builtin(
    "temple.svg",
    icon_size=(32, 32),
    icon_anchor=(16, 16),
    popup_anchor=(0, -16)
)
map.Point(label="Sacred Temple", position=[19.0, 73.0], icon=temple_icon)

# Example 2b: Nagara-style temple with shikhara on one side
nagara_icon = Icon.builtin(
    "temple-nagara.svg",
    icon_size=(32, 32),
    icon_anchor=(16, 16),
    popup_anchor=(0, -16)
)
map.Point(label="Nagara Temple", position=[12.3, 76.6], icon=nagara_icon)

# Example 2c: pyramidal temple, kinda like gopuram
gopuram_icon = Icon.builtin(
    "temple-gopuram.svg",
    icon_size=(32, 32),
    icon_anchor=(16, 16),
    popup_anchor=(0, -16)
)
map.Point(label="Gopuram Temple", position=[10.8, 78.7], icon=gopuram_icon)

# Example 2d: East Asian pagoda-style temple
pagoda_icon = Icon.builtin(
    "temple-pagoda.svg",
    icon_size=(32, 32),
    icon_anchor=(16, 16),
    popup_anchor=(0, -16)
)
map.Point(label="Pagoda Temple", position=[25.0, 121.5], icon=pagoda_icon)

# Example 2e: Classical Greek temple
parthenon_icon = Icon.builtin(
    "temple-parthenon.svg",
    icon_size=(32, 32),
    icon_anchor=(16, 16),
    popup_anchor=(0, -16)
)
map.Point(label="Classical Temple", position=[37.9, 23.7], icon=parthenon_icon)

# Example 3: Fortress or citadel
fort_icon = Icon.builtin(
    "fort.svg",
    icon_size=(32, 32),
    icon_anchor=(16, 16),
    popup_anchor=(0, -16)
)
map.Point(label="Ancient Fort", position=[26.9, 75.8], icon=fort_icon)

# Example 4: Seaport
port_icon = Icon.builtin(
    "port.svg",
    icon_size=(32, 32),
    icon_anchor=(16, 16),
    popup_anchor=(0, -16)
)
map.Point(label="Seaport", position=[19.0, 73.0], icon=port_icon)

# Example 4: Important location (star)
star_icon = Icon.builtin(
    "star.svg",
    icon_size=(32, 32),
    icon_anchor=(16, 16),
    popup_anchor=(0, -16)
)
map.Point(label="Important Site", position=[13.0, 80.2], icon=star_icon)

# Example 5: Religious symbols
om_icon = Icon.builtin(
    "symbol-om.svg",
    icon_size=(32, 32),
    icon_anchor=(16, 16),
    popup_anchor=(0, -16)
)
map.Point(label="Hindu Temple", position=[27.2, 77.4], icon=om_icon)

crescent_icon = Icon.builtin(
    "symbol-crescent-star.svg",
    icon_size=(32, 32),
    icon_anchor=(16, 16),
    popup_anchor=(0, -16)
)
map.Point(label="Mosque", position=[31.2, 29.9], icon=crescent_icon)

cross_icon = Icon.builtin(
    "symbol-cross.svg",
    icon_size=(32, 32),
    icon_anchor=(16, 16),
    popup_anchor=(0, -16)
)
map.Point(label="Church", position=[41.9, 12.5], icon=cross_icon)

star_david_icon = Icon.builtin(
    "symbol-star-david.svg",
    icon_size=(32, 32),
    icon_anchor=(16, 16),
    popup_anchor=(0, -16)
)
map.Point(label="Synagogue", position=[31.8, 35.2], icon=star_david_icon)

# Example 6: Notable location (exclamation)
important_icon = Icon.builtin(
    "important.svg",
    icon_size=(32, 32),
    icon_anchor=(16, 16),
    popup_anchor=(0, -16)
)
map.Point(label="Notable Place", position=[17.4, 78.5], icon=important_icon)

# Example 6: Simple example icon
example_icon = Icon.builtin(
    "example.svg",
    icon_size=(32, 32),
    icon_anchor=(16, 16),
    popup_anchor=(0, -16)
)
map.Point(label="Example Marker", position=[15.3, 74.1], icon=example_icon)

# Add a title
map.TitleBox("<b>Built-in Icon Examples</b><br>Demonstrating various built-in marker icons for historical mapping")

# Export the map
map.show(out_json="tests/map_builtin_icons.json", out_html="tests/map_builtin_icons.html")
print("Map with built-in icons exported to map_builtin_icons.html")
