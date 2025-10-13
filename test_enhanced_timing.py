#!/usr/bin/env python3
"""
Test script to demonstrate the enhanced time debugging feature with exclusive timing
and bar chart generation.
"""

import xatra
from xatra.loaders import gadm, naturalearth

print("=" * 70)
print("Testing Enhanced Time Debugging with Exclusive Timing")
print("=" * 70)

# Clear any existing timing data
xatra.clear_timing_stats()

# Enable time debugging
xatra.set_debug_time(True)

print("\nCreating a map with various operations...")

# Create a map with multiple operations
map = xatra.FlagMap()

# Add flags (these will call nested tracked functions)
map.Flag(label="India", value=gadm("IND"))
map.Flag(label="Pakistan", value=gadm("PAK"))

# Try to add a river (may fail if data not available)
try:
    map.River(label="Test River", value=naturalearth("1159122643"))
except Exception as e:
    print(f"River loading failed (expected): {e}")

# Add other elements
map.Point(label="Delhi", position=[28.6, 77.2])
map.Text(label="South Asia", position=[20, 75])
map.TitleBox("<b>Enhanced Timing Test Map</b>")

# Export the map
map.show(out_json="test_enhanced_timing.json", out_html="test_enhanced_timing.html")

print("\n" + "=" * 70)
print("TIMING ANALYSIS")
print("=" * 70)

# Print timing summary
xatra.print_timing_summary()

# Generate timing chart
print("\nGenerating timing analysis chart...")
chart_path = xatra.generate_timing_chart(show_chart=False)
print(f"Chart saved to: {chart_path}")

print("\n" + "=" * 70)
print("Enhanced timing test complete!")
print("=" * 70)
