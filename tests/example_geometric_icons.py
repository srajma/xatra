#!/usr/bin/env python3
"""
Example demonstrating geometric shape icons created with HTML/CSS.

This example shows how to use the new Icon.geometric() method to create
pure HTML/CSS-based geometric shapes for map markers, including circles,
triangles, diamonds, squares, crosses, plus signs, stars, and polygons.
"""

import xatra
from xatra import Icon, ShapeType
from xatra.loaders import gadm

# Create a map
map = xatra.Map()
map.BaseOption("OpenStreetMap", default=True)
map.BaseOption("Esri.WorldImagery")

# Add a flag for context
map.Flag(label="India", value=gadm("IND"))

# Example 1: Basic geometric shapes - circles, squares, triangles
circle_icon = Icon.geometric("circle", color="red", size=24)
map.Point(label="Red Circle", position=[28.6, 77.2], icon=circle_icon)

square_icon = Icon.geometric("square", color="blue", size=24)
map.Point(label="Blue Square", position=[19.0, 73.0], icon=square_icon)

triangle_icon = Icon.geometric("triangle", color="green", size=24)
map.Point(label="Green Triangle", position=[12.3, 76.6], icon=triangle_icon)

# Example 2: Diamond and cross shapes
diamond_icon = Icon.geometric("diamond", color="purple", size=24)
map.Point(label="Purple Diamond", position=[10.8, 78.7], icon=diamond_icon)

cross_icon = Icon.geometric("cross", color="orange", size=24)
map.Point(label="Orange Cross", position=[25.0, 121.5], icon=cross_icon)

# Example 3: Plus sign and star
plus_icon = Icon.geometric("plus", color="cyan", size=24)
map.Point(label="Cyan Plus", position=[37.9, 23.7], icon=plus_icon)

star_icon = Icon.geometric("star", color="gold", size=24)
map.Point(label="Gold Star", position=[35.7, 139.7], icon=star_icon)

# Example 4: Polygons - hexagon, pentagon, octagon
hexagon_icon = Icon.geometric("hexagon", color="maroon", size=24)
map.Point(label="Maroon Hexagon", position=[40.7, -74.0], icon=hexagon_icon)

pentagon_icon = Icon.geometric("pentagon", color="teal", size=24)
map.Point(label="Teal Pentagon", position=[51.5, -0.1], icon=pentagon_icon)

octagon_icon = Icon.geometric("octagon", color="navy", size=24)
map.Point(label="Navy Octagon", position=[48.9, 2.3], icon=octagon_icon)

# Example 5: Using ShapeType enum instead of strings
enum_circle = Icon.geometric(ShapeType.CIRCLE, color="lime", size=24)
map.Point(label="Lime Circle (Enum)", position=[55.8, 37.6], icon=enum_circle)

# Example 6: Custom sizes and anchors
large_star = Icon.geometric(
    "star", 
    color="magenta", 
    size=32,
    icon_size=(32, 32),
    icon_anchor=(16, 16)
)
map.Point(label="Large Magenta Star", position=[59.9, 30.3], icon=large_star)

# Example 7: Shapes with borders
circle_with_border = Icon.geometric(
    "circle",
    color="yellow",
    size=28,
    border_color="black",
    border_width=2
)
map.Point(label="Yellow Circle with Border", position=[39.9, 116.4], icon=circle_with_border)

diamond_with_border = Icon.geometric(
    "diamond",
    color="white",
    size=24,
    border_color="red",
    border_width=3
)
map.Point(label="White Diamond with Red Border", position=[35.0, 136.0], icon=diamond_with_border)

# Example 8: Different color formats
hex_color = Icon.geometric("square", color="#ff6b6b", size=24)
map.Point(label="Hex Color Square", position=[22.3, 114.2], icon=hex_color)

rgb_color = Icon.geometric("triangle", color="rgb(255, 107, 107)", size=24)
map.Point(label="RGB Color Triangle", position=[1.3, 103.8], icon=rgb_color)

named_color = Icon.geometric("circle", color="darkblue", size=24)
map.Point(label="Named Color Circle", position=[-33.9, 18.4], icon=named_color)

# Add a title
map.TitleBox(
    "<b>Geometric Shape Icons Example</b><br>"
    "Demonstrating HTML/CSS-based geometric shapes for map markers<br>"
    "Shapes: circle, square, triangle, diamond, cross, plus, star, hexagon, pentagon, octagon"
)

# Export the map
map.show(out_json="tests/geometric_icons.json", out_html="tests/geometric_icons.html")
print("Map with geometric shape icons exported to geometric_icons.html")
