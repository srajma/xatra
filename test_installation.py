#!/usr/bin/env python3
"""
Test script to verify Xatra installation and data availability.

Run this after installing xatra and running xatra-install-data.
"""

import sys


def test_import():
    """Test that xatra can be imported."""
    print("Testing xatra import...")
    try:
        import xatra
        print(f"  ✓ Successfully imported xatra version {xatra.__version__}")
        return True
    except ImportError as e:
        print(f"  ✗ Failed to import xatra: {e}")
        return False


def test_data_location():
    """Test that data directory exists."""
    print("\nTesting data location...")
    try:
        from xatra.data_installer import get_data_dir, is_data_installed
        data_dir = get_data_dir()
        print(f"  Data directory: {data_dir}")
        
        if is_data_installed():
            print(f"  ✓ Data is installed")
            return True
        else:
            print(f"  ✗ Data is not installed")
            print(f"  Run: xatra-install-data")
            return False
    except Exception as e:
        print(f"  ✗ Error checking data: {e}")
        return False


def test_data_files():
    """Test that key data files exist."""
    print("\nTesting data files...")
    try:
        from xatra.data_installer import get_data_dir
        from pathlib import Path
        
        data_dir = get_data_dir()
        required_files = [
            "disputed_territories/disputed_mapping.json",
            "ne_10m_rivers.geojson",
        ]
        
        all_found = True
        for file_path in required_files:
            full_path = data_dir / file_path
            if full_path.exists():
                print(f"  ✓ Found: {file_path}")
            else:
                print(f"  ✗ Missing: {file_path}")
                all_found = False
        
        # Check directories
        required_dirs = [
            "gadm",
            "disputed_territories",
            "rivers_overpass_india",
        ]
        
        for dir_path in required_dirs:
            full_path = data_dir / dir_path
            if full_path.exists() and full_path.is_dir():
                file_count = sum(1 for _ in full_path.rglob("*") if _.is_file())
                print(f"  ✓ Found: {dir_path}/ ({file_count} files)")
            else:
                print(f"  ✗ Missing: {dir_path}/")
                all_found = False
        
        return all_found
    except Exception as e:
        print(f"  ✗ Error checking files: {e}")
        return False


def test_loaders():
    """Test that data loaders work."""
    print("\nTesting data loaders...")
    try:
        from xatra.loaders import gadm
        
        # Try to load a simple country
        print("  Attempting to load India (IND)...")
        territory = gadm("IND")
        print(f"  ✓ Successfully loaded India")
        return True
    except FileNotFoundError as e:
        print(f"  ✗ Data file not found: {e}")
        print(f"  Make sure you've run: xatra-install-data")
        return False
    except Exception as e:
        print(f"  ✗ Error loading data: {e}")
        return False


def test_map_creation():
    """Test that a simple map can be created."""
    print("\nTesting map creation...")
    try:
        import xatra
        from xatra.loaders import gadm
        
        # Create a simple map
        map = xatra.FlagMap()
        map.Flag(label="India", value=gadm("IND"))
        
        # Try to export to JSON (don't save HTML)
        data = map._export_json()
        
        if data and "flags" in data:
            print(f"  ✓ Successfully created map with {len(data['flags'])} flag(s)")
            return True
        else:
            print(f"  ✗ Map created but export failed")
            return False
    except Exception as e:
        print(f"  ✗ Error creating map: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("=" * 70)
    print("Xatra Installation Test")
    print("=" * 70)
    
    tests = [
        ("Import", test_import),
        ("Data Location", test_data_location),
        ("Data Files", test_data_files),
        ("Data Loaders", test_loaders),
        ("Map Creation", test_map_creation),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\nUnexpected error in {name} test: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 70)
    print("Test Results")
    print("=" * 70)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status}: {name}")
    
    all_passed = all(result for _, result in results)
    
    print("\n" + "=" * 70)
    if all_passed:
        print("SUCCESS: All tests passed! Xatra is ready to use.")
        return 0
    else:
        print("FAILURE: Some tests failed. See above for details.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

