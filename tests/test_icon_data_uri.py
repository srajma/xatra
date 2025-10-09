#!/usr/bin/env python3
"""
Test to verify that icons are properly embedded as data URIs.
"""

import json
import xatra
from xatra import MarkerIcon

# Create a simple map with a point
map = xatra.FlagMap()
map.Point("Test Point", [28.6, 77.2])
map.show(out_json="test_icon_uri.json", out_html="test_icon_uri.html")

# Read the JSON and verify data URIs
with open("test_icon_uri.json", "r") as f:
    data = json.load(f)

points = data["points"]
assert len(points) == 1, "Should have exactly 1 point"

point = points[0]
assert "icon" in point, "Point should have icon data"
assert "iconUrl" in point["icon"], "Icon should have iconUrl"
assert "shadowUrl" in point["icon"], "Icon should have shadowUrl"

# Verify they are data URIs, not file paths
assert point["icon"]["iconUrl"].startswith("data:image/png;base64,"), \
    f"Icon URL should be a data URI, got: {point['icon']['iconUrl'][:50]}"
assert point["icon"]["shadowUrl"].startswith("data:image/png;base64,"), \
    f"Shadow URL should be a data URI, got: {point['icon']['shadowUrl'][:50]}"

# Verify the data URIs are not empty
assert len(point["icon"]["iconUrl"]) > 100, "Icon data URI should contain actual image data"
assert len(point["icon"]["shadowUrl"]) > 100, "Shadow data URI should contain actual image data"

print("✅ All data URI tests passed!")
print(f"   Icon data URI length: {len(point['icon']['iconUrl'])}")
print(f"   Shadow data URI length: {len(point['icon']['shadowUrl'])}")

# Clean up
import os
os.remove("test_icon_uri.json")
os.remove("test_icon_uri.html")
print("✅ Cleanup complete")

