#!/usr/bin/env python3
"""
Test script for icon_size and icon_anchor parameter handling in geometric icons.
"""

from xatra import Icon, ShapeType

def test_single_integer_conversion():
    """Test that single integers are converted to tuples."""
    
    # Test single integer icon_size
    icon1 = Icon.geometric("circle", color="red", icon_size=12)
    assert icon1.icon_size == (12, 12), f"Expected (12, 12), got {icon1.icon_size}"
    
    # Test single integer icon_anchor
    icon2 = Icon.geometric("square", color="blue", icon_anchor=8)
    assert icon2.icon_anchor == (8, 8), f"Expected (8, 8), got {icon2.icon_anchor}"
    
    # Test both single integers
    icon3 = Icon.geometric("triangle", color="green", icon_size=16, icon_anchor=10)
    assert icon3.icon_size == (16, 16), f"Expected (16, 16), got {icon3.icon_size}"
    assert icon3.icon_anchor == (10, 10), f"Expected (10, 10), got {icon3.icon_anchor}"
    
    print("✓ Single integer conversion works correctly")

def test_tuple_preservation():
    """Test that tuples are preserved as-is."""
    
    # Test tuple icon_size
    icon1 = Icon.geometric("diamond", color="purple", icon_size=(20, 30))
    assert icon1.icon_size == (20, 30), f"Expected (20, 30), got {icon1.icon_size}"
    
    # Test tuple icon_anchor
    icon2 = Icon.geometric("cross", color="orange", icon_anchor=(15, 25))
    assert icon2.icon_anchor == (15, 25), f"Expected (15, 25), got {icon2.icon_anchor}"
    
    # Test both tuples
    icon3 = Icon.geometric("star", color="gold", icon_size=(24, 28), icon_anchor=(12, 14))
    assert icon3.icon_size == (24, 28), f"Expected (24, 28), got {icon3.icon_size}"
    assert icon3.icon_anchor == (12, 14), f"Expected (12, 14), got {icon3.icon_anchor}"
    
    print("✓ Tuple preservation works correctly")

def test_default_values():
    """Test that default values work correctly."""
    
    # Test default values with size=20
    icon1 = Icon.geometric("circle", color="red", size=20)
    assert icon1.icon_size == (20, 20), f"Expected (20, 20), got {icon1.icon_size}"
    assert icon1.icon_anchor == (10, 10), f"Expected (10, 10), got {icon1.icon_anchor}"
    
    # Test default values with size=32
    icon2 = Icon.geometric("square", color="blue", size=32)
    assert icon2.icon_size == (32, 32), f"Expected (32, 32), got {icon2.icon_size}"
    assert icon2.icon_anchor == (16, 16), f"Expected (16, 16), got {icon2.icon_anchor}"
    
    print("✓ Default values work correctly")

def test_to_dict_method():
    """Test that to_dict method works with converted values."""
    
    # Test with single integers
    icon1 = Icon.geometric("circle", color="red", icon_size=12, icon_anchor=6)
    icon_dict = icon1.to_dict()
    assert icon_dict['iconSize'] == [12, 12], f"Expected [12, 12], got {icon_dict['iconSize']}"
    assert icon_dict['iconAnchor'] == [6, 6], f"Expected [6, 6], got {icon_dict['iconAnchor']}"
    
    # Test with tuples
    icon2 = Icon.geometric("square", color="blue", icon_size=(20, 30), icon_anchor=(10, 15))
    icon_dict2 = icon2.to_dict()
    assert icon_dict2['iconSize'] == [20, 30], f"Expected [20, 30], got {icon_dict2['iconSize']}"
    assert icon_dict2['iconAnchor'] == [10, 15], f"Expected [10, 15], got {icon_dict2['iconAnchor']}"
    
    print("✓ to_dict method works correctly")

if __name__ == "__main__":
    test_single_integer_conversion()
    test_tuple_preservation()
    test_default_values()
    test_to_dict_method()
    print("\n🎉 All icon size/anchor tests passed!")
