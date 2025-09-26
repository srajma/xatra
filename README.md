# Xatra: The Matplotlib of Maps

Xatra is a Python library for creating interactive historical maps, similar to how matplotlib provides plotting capabilities. It supports various map elements including flags (countries/kingdoms), rivers, paths, points, text labels, and title boxes with optional time-based filtering for dynamic maps.

## Features

- **Interactive HTML Maps**: Generate self-contained HTML files using Leaflet.js
- **Territory Algebra**: Composable geographical regions using set operations
- **Dynamic Maps**: Time-based filtering with smooth transitions using pax-max aggregation
- **Multiple Base Layers**: Support for OpenStreetMap, Esri, CartoDB, and custom tile servers
- **Customizable Styling**: Full CSS support for all map elements
- **Data Loaders**: Built-in support for GADM, Natural Earth, and Overpass API
- **Precise Labeling**: Flag labels positioned at geometric centroids

## Installation

```bash
pip install shapely jinja2
```

## Quick Start

```python
import xatra

# Create a new map
map = xatra.FlagMap()

# Add a flag (country/kingdom)
india = xatra.gadm("IND")
map.Flag("India", india, period=[1947, 2024], note="Independent India")

# Add a river
ganges = xatra.naturalearth("ne_id_123")  # Replace with actual NE ID
map.River("Ganges", ganges, classes="major-river", note="Sacred river")

# Add a path/route
map.Path("Silk Road", [[40.0, 74.0], [35.0, 103.0]], classes="trade-route")

# Add a point of interest
map.Point("Delhi", [28.6139, 77.2090], period=[1200, 1800])

# Add text labels
map.Text("Ancient City", [28.6139, 77.2090], classes="city-label")

# Add a title box
map.TitleBox("<h1>Historical Map</h1><p>Map of ancient kingdoms</p>")

# Add custom CSS
map.CSS("""
.major-river { stroke: #0066cc; stroke-width: 3px; }
.trade-route { stroke: #ff6600; stroke-dasharray: 5 5; }
.city-label { font-size: 18px; color: #333; }
""")

# Configure base layers
map.BaseOption("OpenStreetMap", default=True)
map.BaseOption("Esri.WorldImagery")
map.BaseOption("OpenTopoMap")

# Set time limits for dynamic maps
map.lim(1000, 2000)

# Export to HTML
map.show("my_map.html")
```

## API Reference

### FlagMap Class

The main class for creating maps.

#### Constructor
```python
map = FlagMap()
```

#### Methods

##### Adding Map Elements

- **`Flag(label, territory, period=None, note=None)`**: Add a flag (country/kingdom)
- **`River(label, geometry, note=None, classes=None, period=None)`**: Add a river
- **`Path(label, coords, classes=None, period=None)`**: Add a path/route
- **`Point(label, position, period=None)`**: Add a point of interest
- **`Text(label, position, classes=None, period=None)`**: Add a text label
- **`TitleBox(html, period=None)`**: Add a title box with HTML content

##### Styling and Configuration

- **`CSS(css)`**: Add custom CSS styles
- **`BaseOption(url_or_provider, name=None, default=False)`**: Add base map layer
- **`lim(start, end)`**: Set time limits for dynamic maps

##### Export

- **`show(out_json="map.json", out_html="map.html")`**: Export map to JSON and HTML files

### Territory Class

Represents geographical regions with set algebra operations.

#### Static Methods

- **`from_geojson(geojson_obj)`**: Create from GeoJSON object
- **`from_gadm(key)`**: Create from GADM administrative boundary
- **`from_naturalearth(ne_id)`**: Create from Natural Earth dataset

#### Operations

- **`territory1 | territory2`**: Union of two territories
- **`territory1 - territory2`**: Difference of two territories

### Data Loaders

- **`gadm(key)`**: Load GADM administrative boundary (e.g., "IND", "PAK")
- **`naturalearth(ne_id)`**: Load Natural Earth feature by ID
- **`overpass(osm_id)`**: Load Overpass API data by OSM ID

## Examples

### Static Map

```python
import xatra

map = xatra.FlagMap()

# Add territories
india = xatra.gadm("IND")
pakistan = xatra.gadm("PAK")
northern_india = india - pakistan

map.Flag("Northern India", northern_india, note="Historical region")

# Add rivers
ganges = xatra.naturalearth("ne_id_123")
map.River("Ganges", ganges, classes="major-river")

# Export
map.show("static_map.html")
```

### Dynamic Map

```python
import xatra

map = xatra.FlagMap()

# Add flags with time periods
maurya = xatra.gadm("IND")
map.Flag("Maurya", maurya, period=[320, 180], note="Mauryan Empire")

gupta = xatra.gadm("IND")
map.Flag("Gupta", gupta, period=[320, 550], note="Gupta Empire")

# Add rivers that change over time
ganges_ancient = xatra.naturalearth("ne_id_123")
map.River("Ganges", ganges_ancient, period=[320, 600], classes="ancient-river")

ganges_modern = xatra.naturalearth("ne_id_124")
map.River("Ganges", ganges_modern, period=[600, 2024], classes="modern-river")

# Set time limits
map.lim(300, 2024)

# Export
map.show("dynamic_map.html")
```

### Custom Styling

```python
import xatra

map = xatra.FlagMap()

# Add custom CSS
map.CSS("""
.empire { 
    fill: rgba(200, 0, 0, 0.3); 
    stroke: #cc0000; 
    stroke-width: 2px; 
}
.major-river { 
    stroke: #0066cc; 
    stroke-width: 3px; 
    stroke-opacity: 0.8; 
}
.trade-route { 
    stroke: #ff6600; 
    stroke-dasharray: 8 4; 
    stroke-width: 2px; 
}
.city-label { 
    font-size: 16px; 
    font-weight: bold; 
    color: #333; 
    text-shadow: 1px 1px 2px rgba(255,255,255,0.8); 
}
""")

# Add elements with custom classes
map.Flag("Maurya", territory, classes="empire")
map.River("Ganges", river_geom, classes="major-river")
map.Path("Silk Road", coords, classes="trade-route")
map.Text("Delhi", position, classes="city-label")

map.show("styled_map.html")
```

### Base Layer Configuration

```python
import xatra

map = xatra.FlagMap()

# Add multiple base layers
map.BaseOption("OpenStreetMap", default=True)
map.BaseOption("Esri.WorldImagery")
map.BaseOption("OpenTopoMap")
map.BaseOption("CartoDB.Positron")
map.BaseOption("USGS.USImageryTopo")

# Custom tile server
map.BaseOption(
    "https://tiles.example.com/{z}/{x}/{y}.png",
    name="Custom Tiles",
    default=False
)

map.show("multi_layer_map.html")
```

## Data Sources

### GADM (Global Administrative Areas)
- Country codes: "IND", "PAK", "CHN", etc.
- Subdivisions: "IND.31", "IND.31.1", etc.
- Files: `data/gadm/gadm41_*.json`

### Natural Earth
- Rivers: `data/ne_10m_rivers.geojson`
- Features identified by `ne_id` property

### Overpass API
- Rivers: `data/rivers_overpass_india/`
- Features identified by OSM ID in filename

## File Structure

```
xatra2/
├── xatra/
│   ├── __init__.py          # Main package interface
│   ├── flagmap.py           # FlagMap class and data structures
│   ├── territory.py         # Territory class and set algebra
│   ├── loaders.py           # Data loading functions
│   ├── paxmax.py            # Pax-max aggregation for dynamic maps
│   ├── render.py            # HTML template and JavaScript
│   └── territory_library.py # Predefined composite territories
├── data/                    # Geographical data files
│   ├── gadm/               # GADM administrative boundaries
│   ├── ne_10m_rivers.geojson # Natural Earth rivers
│   └── rivers_overpass_india/ # Overpass API rivers
├── example.py              # Usage examples
└── README.md               # This file
```

## Requirements

- Python 3.7+
- Shapely (geometrical operations)
- Jinja2 (HTML templating)

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

## Changelog

### v0.1.0
- Initial release
- Basic FlagMap functionality
- Territory algebra with GADM, Natural Earth, and Overpass support
- Dynamic maps with pax-max aggregation
- Multiple base layer support
- Custom CSS styling
- Precise flag label positioning


# TODO
Stylistic changes
- [x] The slider seems to be hidden under the map: I can move it around by clicking where it should be, but can only actually see it visually when I'm zooming out or am fully zoomed out (because that's when the blank space behind the map appears before the tiles load to fill it up). The slider should be a fixed element on the screen *over* the map that stays at the exact same position regardless of where I pan or zoom to.
- [x] the TitleBox only appears when fully zoomed out. It too should appear as a fixed element on the screen *over* the map that stays at the exact same position regardless of where I pan or zoom to.
- [x] custom IDs and classes for styling
- [x] The tooltip that appears upon hovering over a flag should appear at the point of my cursor, and move with my cursor. I thought this is how default Leaflet tooltips appear? Why does it appear at a fixed point in our implementation?
- [x] also need flag names to appear at centroid
- [x] map.Text labels should by default just be plain text, without the border box and all that. Its default style could be different maybe "font-size: 16px; font-weight: bold; color: #666666"
- [ ] color assignment
- [x] choice of BaseMaps
- [x] slider shouldn't appear for static maps
- [x] slider.lim()

Libraries
- [ ] copy matchers from old xatra
- [ ] copy maps from old xatra

Development
- [x] periods for things other than flags
- [ ] xatra.AdminMap
- [ ] xatra.DataMap
- [ ] possibly calculate and keep simplified geometries
- [ ] loading geojson from file instead of storing it in html; i.e. with a server

Interactive platform
- [ ] DSL
- [ ] type in DSL panel, hit render => gets transmitted to server and parsed into Python, turned into geojson and re-rendered
- [ ] while typing in DSL panel: search, select from AdminMap, preview territories (matchers/gadms/...) on AdminMap