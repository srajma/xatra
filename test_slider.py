#!/usr/bin/env python3
"""
Test script to verify slider behavior for static vs dynamic maps.
"""

import xatra
from xatra.loaders import gadm

def test_static_map():
    """Test static map (no periods) - should not show slider."""
    print("Creating static map...")
    map = xatra.FlagMap()
    map.BaseOption("OpenStreetMap", default=True)
    map.Flag("India", gadm("IND"), note="Static map - no periods")
    map.Point("Delhi", [28.6, 77.2])
    map.Text("India", [22.0, 79.0])
    map.TitleBox("<h2>Static Map</h2><p>No time periods - no slider should appear</p>")
    map.show(out_json="static_test.json", out_html="static_test.html")
    print("Static map generated: static_test.html")

def test_dynamic_map():
    """Test dynamic map (with periods) - should show slider."""
    print("Creating dynamic map...")
    map = xatra.FlagMap()
    map.BaseOption("OpenStreetMap", default=True)
    map.Flag("Maurya", gadm("IND"), period=[-320, -180], note="Dynamic map with periods")
    map.Point("Ancient City", [28.6, 77.2], period=[-300, 500])
    map.Text("Ancient Label", [22.0, 79.0], period=[-500, 0])
    map.TitleBox("<h2>Dynamic Map</h2><p>With time periods - slider should appear</p>", period=[-500, 0])
    map.show(out_json="dynamic_test.json", out_html="dynamic_test.html")
    print("Dynamic map generated: dynamic_test.html")

if __name__ == "__main__":
    test_static_map()
    test_dynamic_map()
    print("\nDone! Check the HTML files:")
    print("- static_test.html should NOT have a slider")
    print("- dynamic_test.html should have a slider")