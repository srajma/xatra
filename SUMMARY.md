# Xatra Map-Making Software - Implementation Summary

## Overview
A "matplotlib of maps" called `xatra` that creates interactive historical maps with territory algebra, time-based visualization, and customizable styling.

## Core Architecture

### Main API (`xatra/flagmap.py`)
- **FlagMap class**: Main interface for creating maps
- **Territory algebra**: Union (`|`) and difference (`-`) operations using Shapely
- **Time periods**: All objects can have `period=[start, end]` for dynamic maps
- **Pax-max aggregation**: Combines flags by label over time periods

### Key Methods
```python
map.Flag(label, territory, period=None, note=None)
map.Admin(gadm, level, period=None, classes=None, color_by_level=1)
map.AdminRivers(period=None, classes=None, sources=None)
map.River(label, value, note=None, classes=None, period=None)  
map.Path(label, coords, classes=None, period=None)
map.Point(label, position, period=None)
map.Text(label, position, classes=None, period=None)
map.TitleBox(html, period=None)
map.BaseOption(url_or_provider, name=None, default=False)
map.FlagColorSequence(color_sequence)
map.AdminColorSequence(color_sequence)
map.CSS(css_string)
map.lim(start, end)  # Set time limits for the map
map.show(out_json="map.json", out_html="map.html")
```

### Data Loaders (`xatra/loaders.py`)
- **GADM**: `gadm("IND")`, `gadm("IND.31")` - reads from `data/gadm/gadm41_*.json`
- **Natural Earth**: `naturalearth("1159122643")` - filters from `data/ne_10m_rivers.geojson`
- **Overpass**: `overpass("id")` - converts from `data/rivers_overpass_india/`

### Territory System (`xatra/territory.py`)
- **Territory class**: Lazy evaluation with Shapely geometry
- **Algebra**: `territory1 | territory2` (union), `territory1 - territory2` (difference)
- **Caching**: Geometries computed once and cached

### Pax-Max Aggregation (`xatra/paxmax.py`)
- **Static maps**: Union all flags with same label
- **Dynamic maps**: Create snapshots at breakpoint years, union active flags per snapshot
- **Breakpoints**: All start/end years from flag periods only, plus the earliest start year of any object (without this it will show the earliest period-having flag even before its period begins, because it will display whatever's from the first snapshot)
- **Map limits**: Optional time range restriction with `map.lim(start, end)`

### Rendering (`xatra/render.py`)
- **Leaflet-based HTML**: Interactive map with zoom/pan
- **Base layer selector**: Dropdown with custom URLs and provider names
- **Time slider**: For dynamic maps with year controls
- **Flag labels**: Centered at territory centroids using proper geometric calculation
- **Tooltips**: Follow cursor, show on hover
- **CSS styling**: Classes for rivers, paths, texts, flags

## Key Features Implemented

### Base Layers
- Default: OpenStreetMap, Esri.WorldImagery, OpenTopoMap, Esri.WorldPhysical
- Custom URLs: `map.BaseOption("https://...")`
- Provider names: `map.BaseOption("Esri.WorldImagery")`
- Layer selector UI with "None" option

### Administrative Regions
- **Admin method**: `map.Admin(gadm, level, color_by_level=1)` displays GADM administrative regions
- **Rich tooltips**: Shows all GADM properties (GID_0, COUNTRY, GID_1, NAME_1, etc.) on hover
- **Automatic coloring**: Regions colored by specified administrative level
- **Boundary-aware matching**: Exact prefix matching to avoid false matches
- **Color sequences**: `map.AdminColorSequence()` for custom color schemes

### Admin Rivers
- **AdminRivers method**: `map.AdminRivers(sources=["naturalearth", "overpass"])` displays rivers from specified data sources
- **Source filtering**: Choose which data sources to include (Natural Earth, Overpass, or both)
- **Source identification**: Rivers colored differently by source (blue for Natural Earth, orange for Overpass)
- **Rich tooltips**: Shows source information, IDs, and all available name fields
- **Automatic loading**: Loads rivers from specified data sources
- **Time support**: Works with dynamic maps and period filtering

### Styling System
- **Classes**: `classes="custom-class"` parameter for rivers, paths, texts, admins, admin_rivers
- **CSS**: `map.CSS()` for global styling
- **Flag labels**: Auto-positioned at centroids, no background boxes

### Dynamic Maps
- **Time periods**: `period=[-320, -180]` on all object types (flags, admins, admin_rivers, rivers, paths, points, texts, title_boxes)
- **Year slider**: Bottom controls for time navigation (only appears for maps with periods)
- **Pax-max**: Stable periods with union of active flags
- **Map limits**: `map.lim(start, end)` restricts all object periods to specified range
- **Period filtering**: Objects with no period are always visible; objects with periods are filtered by time

### Centroid Calculation
- **Geometric centroids**: Proper shoelace formula for polygons
- **MultiPolygon support**: Area-weighted centroids
- **Debug markers**: `DEBUG_CENTROIDS = true/false` for positioning

## File Structure
```
xatra/
├── __init__.py          # FlagMap export
├── flagmap.py           # Main API and data structures
├── territory.py         # Territory algebra with Shapely
├── loaders.py           # GADM, NaturalEarth, Overpass loaders
├── paxmax.py           # Time-based flag aggregation
├── render.py            # Leaflet HTML generation
└── territory_library.py # Predefined territories (NORTHERN_INDIA)

data/
├── gadm/               # GADM GeoJSON files
├── ne_10m_rivers.geojson # Natural Earth rivers
└── rivers_overpass_india/ # Overpass river data
```

## Current Status
- ✅ Full API implementation
- ✅ Territory algebra working
- ✅ Dynamic maps with time slider
- ✅ Base layer system
- ✅ Flag labels at centroids
- ✅ Tooltips following cursor
- ✅ CSS class-based styling
- ✅ Debug mode for positioning
- ✅ Period support for all object types (flags, rivers, paths, points, texts, title_boxes)
- ✅ Map limits functionality (`map.lim()`)
- ✅ Proper period filtering (objects without periods always visible)

## Example Usage
```python
import xatra
from xatra.loaders import gadm, naturalearth
from xatra.territory_library import NORTHERN_INDIA

map = xatra.FlagMap()
map.Flag("Maurya", gadm("IND") | gadm("PAK"), period=[-320, -240])
map.River("Ganga", naturalearth("1159122643"), classes="ganga-river", period=[-500, 0])
map.Point("Delhi", [28.6, 77.2], period=[1000, 1500])
map.Text("Ancient India", [22.0, 79.0], period=[-500, 300])
map.TitleBox("<h2>Map of Major Indian Empires</h2>", period=[-1000, 2000])
map.lim(-500, 500)  # Restrict map to 500 BCE - 500 CE
map.BaseOption("Esri.WorldImagery", default=True)
map.show()
```