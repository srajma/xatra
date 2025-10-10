# Pyplot-Style Interface Feature

## Overview

Implemented a matplotlib.pyplot-style interface for Xatra that allows users to create maps without explicitly managing a `FlagMap` object. Users can now call `xatra.Flag()`, `xatra.River()`, etc. directly, and a current map is automatically created and managed.

## Implementation

### Core Module: `src/xatra/pyplot.py`

This module provides:

1. **Global state management** via `_current_map` variable
2. **Map management functions:**
   - `get_current_map()`: Returns current FlagMap (creates one if needed)
   - `set_current_map(map)`: Sets the current FlagMap
   - `new_map()`: Creates a new FlagMap and makes it current

3. **Wrapper functions** for all FlagMap methods:
   - Adding elements: `Flag()`, `River()`, `Path()`, `Point()`, `Text()`, `TitleBox()`, `Admin()`, `AdminRivers()`, `Dataframe()`, `Data()`
   - Styling: `CSS()`, `BaseOption()`, `FlagColorSequence()`, `AdminColorSequence()`, `DataColormap()`
   - Time control: `slider()`
   - Export: `show()`

### Updated Files

1. **`src/xatra/__init__.py`**
   - Imports all pyplot functions
   - Exports them in `__all__`
   - Updated docstring with both usage styles

2. **`README.md`**
   - Added "Two Ways to Use Xatra" section with examples
   - Added "Pyplot-Style Functions" section in API Reference
   - Marked TODO item as complete

## Usage Examples

### Simple Usage

```python
import xatra
from xatra.loaders import gadm

xatra.Flag(label="India", value=gadm("IND"))
xatra.show()
```

### Multiple Maps

```python
# Create first map
map1 = xatra.new_map()
xatra.Flag(label="India", value=gadm("IND"))
xatra.show(out_html="map1.html")

# Create second map
map2 = xatra.new_map()
xatra.Flag(label="Pakistan", value=gadm("PAK"))
xatra.show(out_html="map2.html")

# Switch back to first map
xatra.set_current_map(map1)
xatra.Flag(label="More data", value=gadm("IND.31"))
```

### Mixed Styles

```python
# Start with explicit FlagMap
map = xatra.FlagMap()
map.Flag(label="India", value=gadm("IND"))

# Continue with pyplot-style
xatra.set_current_map(map)
xatra.Flag(label="Pakistan", value=gadm("PAK"))
xatra.show()
```

## Test Files

Created comprehensive examples demonstrating the new feature:

1. **`tests/example_pyplot.py`**: Full-featured pyplot-style map with time slider
2. **`tests/example_pyplot_simple.py`**: Minimal example
3. **`tests/example_multiple_maps.py`**: Working with multiple maps
4. **`tests/example_mixed_styles.py`**: Mixing explicit and pyplot styles

All tests pass successfully!

## Backward Compatibility

The feature is fully backward compatible:
- Existing code using `map = xatra.FlagMap()` continues to work unchanged
- Both styles can be used in the same codebase
- No breaking changes to any existing APIs

## Design Philosophy

Following matplotlib's successful pattern:
- **Convenience over complexity**: Simple maps are trivial to create
- **Progressive disclosure**: Advanced features (multiple maps) available when needed
- **Flexibility**: Both styles supported for different use cases

