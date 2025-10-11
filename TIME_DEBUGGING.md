# Xatra Time Debugging Feature

## Overview

A comprehensive time debugging system has been added to xatra that provides detailed timing information for all major operations. When enabled, it prints start/finish messages with HH:MM:SS timestamps for every function call throughout the codebase.

## Implementation Details

### Core Module: `debug_utils.py`

Created a new module `/src/xatra/debug_utils.py` with:

1. **Global Flag**: `DEBUG_TIME` - Controls whether debugging is enabled
2. **Timestamp Function**: `get_timestamp()` - Returns current time in HH:MM:SS format
3. **Debug Log Function**: `debug_log(message, indent)` - Prints timestamped messages
4. **Decorator**: `@time_debug(activity_name, indent)` - Decorator to wrap functions with timing
5. **Context Manager**: `DebugSection` - For timing code sections

### Features

- **Automatic function timing**: Start and finish times are logged automatically
- **Argument logging**: Function arguments are shown (truncated for readability)
- **Error tracking**: Errors are caught and logged with timestamps
- **Nested indentation**: Not currently used but available for hierarchical debugging
- **Zero overhead when disabled**: When `DEBUG_TIME = False`, functions execute normally with minimal overhead

### Integration Points

Time debugging has been added to the following modules:

#### 1. **loaders.py** - Data Loading Functions
- `_read_json()` - JSON file reading with cache status
- `clear_file_cache()` - Cache clearing
- `_load_disputed_mapping()` - Disputed territory mapping
- `gadm()` - GADM data loading
- `naturalearth()` - Natural Earth feature loading
- `overpass()` - Overpass data loading
- `load_gadm_like()` - GADM-like data loading
- `load_naturalearth_like()` - Natural Earth-like data loading

#### 2. **territory.py** - Geometry Operations
- `_geojson_to_geometry()` - GeoJSON to Shapely conversion
- `Territory.to_geometry()` - Territory geometry conversion

#### 3. **flagmap.py** - Map Building Operations
- `Flag()` - Adding flags
- `River()` - Adding rivers
- `Path()` - Adding paths
- `Point()` - Adding points
- `Text()` - Adding text labels
- `TitleBox()` - Adding title boxes
- `Admin()` - Adding administrative regions
- `AdminRivers()` - Adding administrative rivers
- `Dataframe()` - Adding DataFrame visualizations
- `_export_json()` - JSON export
- `show()` - Final map export

#### 4. **render.py** - HTML Rendering
- `export_html()` - HTML file generation

#### 5. **paxmax.py** - Aggregation Operations
- `_compute_centroid_for_geometry()` - Centroid calculation
- `paxmax_aggregate()` - Pax-max aggregation
- `filter_by_period()` - Period filtering

### Public API

Added to `__init__.py`:

```python
# Global flag
DEBUG_TIME = False

# Setter function
def set_debug_time(enabled: bool):
    """Enable or disable time debugging throughout xatra."""
    global DEBUG_TIME
    DEBUG_TIME = enabled
    debug_utils.DEBUG_TIME = enabled
```

Both `DEBUG_TIME` and `set_debug_time` are exported in `__all__`.

## Usage

### Basic Usage

```python
import xatra

# Enable debugging
xatra.set_debug_time(True)

# Create and export a map
map = xatra.FlagMap()
map.Flag("India", xatra.gadm("IND"))
map.show()

# Disable debugging
xatra.set_debug_time(False)
```

### Alternative Usage

```python
import xatra

# Direct flag setting
xatra.DEBUG_TIME = True

# ... create map ...

xatra.DEBUG_TIME = False
```

## Example Output

```
[14:23:45] → START: Add Flag
[14:23:45]   args: 'India', <Territory object at 0x...>
[14:23:45]   → START: Load GADM data
[14:23:45]     → START: Load GADM-like data
[14:23:45]       → START: Read JSON file
[14:23:45]       ✓ FINISH: Read JSON file
[14:23:45]     ✓ FINISH: Load GADM-like data
[14:23:45]   ✓ FINISH: Load GADM data
[14:23:45] ✓ FINISH: Add Flag
[14:23:46] → START: Show (export map)
[14:23:46]   → START: Export to JSON
[14:23:46]     → START: Paxmax aggregation
[14:23:46]       → START: Compute centroid
[14:23:46]       ✓ FINISH: Compute centroid
[14:23:46]     ✓ FINISH: Paxmax aggregation
[14:23:47]   ✓ FINISH: Export to JSON
[14:23:47]   → START: Export to HTML
[14:23:47]   ✓ FINISH: Export to HTML
[14:23:47] ✓ FINISH: Show (export map)
```

## Testing

A test script has been provided at `/test_debug_time.py` that demonstrates the time debugging feature by creating a simple map with debugging enabled.

Run it with:
```bash
python test_debug_time.py
```

## Documentation

Full documentation has been added to the main README.md under the "Time Debugging" section, including:
- How to enable/disable the feature
- What operations get timed
- Example output
- Use cases

## Files Modified

1. **New file**: `src/xatra/debug_utils.py` - Core debugging utilities
2. **Modified**: `src/xatra/__init__.py` - Public API and flag management
3. **Modified**: `src/xatra/loaders.py` - Data loading timing
4. **Modified**: `src/xatra/territory.py` - Geometry operation timing
5. **Modified**: `src/xatra/flagmap.py` - Map building operation timing
6. **Modified**: `src/xatra/render.py` - Rendering timing
7. **Modified**: `src/xatra/paxmax.py` - Aggregation timing
8. **Modified**: `README.md` - Documentation
9. **New file**: `test_debug_time.py` - Test script
10. **New file**: `TIME_DEBUGGING.md` - This file

## Performance Impact

When `DEBUG_TIME = False` (default), the performance impact is minimal:
- The decorator checks the flag once per function call
- No string formatting or I/O occurs
- Function execution proceeds normally

When `DEBUG_TIME = True`, there is some overhead from:
- Timestamp generation
- String formatting
- Console output
- But this is acceptable since debugging is for development/profiling use

## Future Enhancements

Possible improvements for the future:
- Add indentation support for nested call visualization
- Add total elapsed time for each operation
- Add memory usage tracking
- Output to file instead of console
- Configurable verbosity levels
- Statistical summary at the end (total time, slowest operations, etc.)

