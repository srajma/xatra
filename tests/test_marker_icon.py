#!/usr/bin/env python3
"""
Simple test to verify MarkerIcon functionality.
"""

import xatra
from xatra import MarkerIcon

# Test 1: Default icon
map1 = xatra.FlagMap()
map1.Point(label="Default Marker", position=[28.6, 77.2])
print("✓ Test 1 passed: Default icon works")

# Test 2: Custom icon with only URLs
map2 = xatra.FlagMap()
custom_icon = MarkerIcon(
    icon_url='custom-icon.png',
    shadow_url='custom-shadow.png'
)
map2.Point(label="Custom URL Marker", position=[28.6, 77.2], icon=custom_icon)
print("✓ Test 2 passed: Custom icon URLs work")

# Test 3: Custom icon with all properties
map3 = xatra.FlagMap()
full_custom_icon = MarkerIcon(
    icon_url='icons/marker-icon.png',
    shadow_url='icons/marker-shadow.png',
    icon_size=[25, 41],
    shadow_size=[41, 41],
    icon_anchor=[12, 41],
    shadow_anchor=[4, 62],
    popup_anchor=[1, -34]
)
map3.Point(label="Fully Custom Marker", position=[28.6, 77.2], icon=full_custom_icon)
print("✓ Test 3 passed: Fully custom icon works")

# Test 4: Create a MarkerIcon object independently
standalone_icon = MarkerIcon()
assert standalone_icon.icon_url == 'icons/marker-icon.png'
assert standalone_icon.shadow_url == 'icons/marker-shadow.png'
assert standalone_icon.icon_size is None
print("✓ Test 4 passed: MarkerIcon class defaults are correct")

# Test 5: Multiple points with different icons
map4 = xatra.FlagMap()
map4.Point(label="Point 1", position=[28.6, 77.2])
map4.Point(label="Point 2", position=[19.0, 72.8], icon=MarkerIcon(icon_url='icon2.png'))
map4.Point(label="Point 3", position=[22.5, 88.3], icon=MarkerIcon(icon_size=[30, 50]))
print("✓ Test 5 passed: Multiple points with different icons work")

print("\n✅ All tests passed!")

