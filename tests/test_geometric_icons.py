#!/usr/bin/env python3
"""
Test script for geometric shape icons functionality.
"""

import xatra
from xatra import Icon, ShapeType

def test_geometric_shapes():
    """Test basic geometric shape creation."""
    
    # Test string-based shape creation
    circle = Icon.geometric("circle", color="red", size=24)
    assert circle.icon_url.startswith("data:image/svg+xml;base64,")
    assert circle.icon_size == (24, 24)
    assert circle.icon_anchor == (12, 12)
    
    # Test enum-based shape creation
    square = Icon.geometric(ShapeType.SQUARE, color="blue", size=32)
    assert square.icon_url.startswith("data:image/svg+xml;base64,")
    assert square.icon_size == (32, 32)
    assert square.icon_anchor == (16, 16)
    
    # Test custom icon_size and icon_anchor
    triangle = Icon.geometric(
        "triangle", 
        color="green", 
        size=24,
        icon_size=(48, 48),
        icon_anchor=(24, 24)
    )
    assert triangle.icon_size == (48, 48)
    assert triangle.icon_anchor == (24, 24)
    
    # Test shapes with borders
    diamond = Icon.geometric(
        "diamond",
        color="yellow",
        size=28,
        border_color="black",
        border_width=2
    )
    assert diamond.icon_url.startswith("data:image/svg+xml;base64,")
    
    print("✓ All geometric shape tests passed!")

def test_shape_types():
    """Test all available shape types."""
    shapes = [
        "circle", "square", "triangle", "diamond", "cross", "plus", 
        "star", "hexagon", "pentagon", "octagon"
    ]
    
    for shape in shapes:
        icon = Icon.geometric(shape, color="purple", size=20)
        assert icon.icon_url.startswith("data:image/svg+xml;base64,")
        print(f"✓ {shape} shape created successfully")
    
    print("✓ All shape types tested successfully!")

def test_error_handling():
    """Test error handling for invalid shapes."""
    try:
        Icon.geometric("invalid_shape", color="red", size=24)
        assert False, "Should have raised ValueError for invalid shape"
    except ValueError as e:
        assert "Unsupported shape 'invalid_shape'" in str(e)
        print("✓ Invalid shape error handling works correctly")

if __name__ == "__main__":
    test_geometric_shapes()
    test_shape_types()
    test_error_handling()
    print("\n🎉 All tests passed! Geometric icons are working correctly.")
