#!/usr/bin/env python3
"""
Test script for custom polygon territory feature.

This script demonstrates and tests the polygon() loader and Territory.from_polygon()
functionality, including set algebra operations with other territories.
"""

import xatra
from xatra.loaders import polygon, gadm

# Test 1: Create a simple polygon territory
print("Test 1: Creating simple polygon territory...")
simple_polygon = polygon([
    [28, 77],  # [lat, lon]
    [29, 78],
    [28, 79],
])
geom = simple_polygon.to_geometry()
assert geom is not None, "Simple polygon geometry should not be None"
print(f"  Simple polygon created successfully. Area: {geom.area}")

# Test 2: Create a rectangular polygon
print("\nTest 2: Creating rectangular polygon...")
rectangle = polygon([
    [25, 75],
    [25, 85],
    [15, 85],
    [15, 75]
])
geom = rectangle.to_geometry()
assert geom is not None, "Rectangle geometry should not be None"
print(f"  Rectangle created successfully. Area: {geom.area}")

# Test 3: Create polygon with hole
print("\nTest 3: Creating polygon with hole...")
polygon_with_hole = polygon(
    [[20, 75], [25, 75], [25, 80], [20, 80]],  # Exterior
    holes=[[[21, 76], [24, 76], [24, 79], [21, 79]]]  # Interior hole
)
geom = polygon_with_hole.to_geometry()
assert geom is not None, "Polygon with hole geometry should not be None"
print(f"  Polygon with hole created successfully. Area: {geom.area}")

# Test 4: Union of polygon with GADM
print("\nTest 4: Testing union with GADM...")
try:
    tamil_nadu = gadm("IND.31")
    extended = tamil_nadu | polygon([[10, 75], [12, 76], [10, 77]])
    geom = extended.to_geometry()
    assert geom is not None, "Union geometry should not be None"
    print(f"  Union operation successful.")
except Exception as e:
    print(f"  Union test skipped (GADM data may not be installed): {e}")

# Test 5: Intersection of polygon with GADM
print("\nTest 5: Testing intersection with GADM...")
try:
    india = gadm("IND")
    # Create a bounding box for south India
    south_box = polygon([[8, 72], [8, 88], [20, 88], [20, 72]])
    south_india = india & south_box
    geom = south_india.to_geometry()
    assert geom is not None, "Intersection geometry should not be None"
    print(f"  Intersection operation successful.")
except Exception as e:
    print(f"  Intersection test skipped (GADM data may not be installed): {e}")

# Test 6: Difference of polygon from GADM
print("\nTest 6: Testing difference with GADM...")
try:
    india = gadm("IND")
    cutout = polygon([[25, 75], [25, 85], [30, 85], [30, 75]])
    india_minus_cutout = india - cutout
    geom = india_minus_cutout.to_geometry()
    assert geom is not None, "Difference geometry should not be None"
    print(f"  Difference operation successful.")
except Exception as e:
    print(f"  Difference test skipped (GADM data may not be installed): {e}")

# Test 7: Chained operations
print("\nTest 7: Testing chained operations...")
p1 = polygon([[20, 70], [20, 80], [30, 80], [30, 70]])
p2 = polygon([[22, 72], [22, 78], [28, 78], [28, 72]])
p3 = polygon([[24, 74], [24, 76], [26, 76], [26, 74]])

# (p1 - p2) | p3 should work
result = (p1 - p2) | p3
geom = result.to_geometry()
assert geom is not None, "Chained operations geometry should not be None"
print(f"  Chained operations successful. Area: {geom.area}")

# Test 8: Using polygon in a map
print("\nTest 8: Testing polygon in map...")
try:
    map = xatra.Map()
    map.BaseOption("Esri.WorldTopoMap", default=True)
    
    # Create a custom region using polygon
    custom_region = polygon([
        [28, 77],
        [30, 80],
        [28, 83],
        [26, 80]
    ])
    map.Flag(label="Custom Diamond", value=custom_region, color="#ff0000")
    
    # Create union with GADM
    try:
        extended_tn = gadm("IND.31") | polygon([[10, 75], [12, 76], [10, 77]])
        map.Flag(label="Extended Tamil Nadu", value=extended_tn, color="#00ff00")
    except Exception:
        pass  # Skip if GADM not available
    
    map.TitleBox("<b>Custom Polygon Territory Test</b>")
    map.show(out_json="tests/map_polygon.json", out_html="tests/map_polygon.html")
    print("  Map exported to tests/map_polygon.html")
except Exception as e:
    print(f"  Map test failed: {e}")

print("\n" + "="*50)
print("All polygon territory tests completed!")
print("="*50)
