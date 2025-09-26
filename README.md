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

# Xatra: The Matplotlib of Maps

Xatra is the matplotlib of maps. You can create historical maps (static or dynamic, i.e. with a time slider), data maps, maps of administrative regions, whatever.


## Quick Start

```python
import xatra
from xatra.loaders import gadm, naturalearth
from xatra.territory_library import NORTHERN_INDIA

# Create a test map
map = xatra.FlagMap()
map.BaseOption("OpenStreetMap", default=True)
map.BaseOption("Esri.WorldImagery")
map.BaseOption("OpenTopoMap")
map.BaseOption("Esri.WorldPhysical")
map.Flag(label="Maurya", value=gadm("IND") | gadm("PAK"), period=[-320, -240], note="south is lost after Ashoka's death")
map.Flag(label="Maurya", value=NORTHERN_INDIA, period=[-320, -180])
map.Flag(label="Gupta", value=NORTHERN_INDIA, period=[250, 500])
map.Flag(label="Chola", value=gadm("IND.31"), note="Chola persisted throughout this entire period")
map.River(label="Ganga", value=naturalearth("1159122643"), note="can be specified as naturalearth(id) or overpass(id)", classes="ganga-river indian-river")
map.River(label="Ganga", value=naturalearth("1159122643"), period=[0, 600], note="Modern course of Ganga", classes="modern-river")
map.Path(label="Uttarapatha", value=[[28,77],[30,90],[40, 120]], classes="uttarapatha-path")
map.Path(label="Silk Road", value=[[35.0, 75.0], [40.0, 80.0], [45.0, 85.0]], period=[-200, 600], classes="silk-road")
map.Point(label="Indraprastha", position=[28,77])
map.Point(label="Delhi", position=[28.6, 77.2], period=[400, 800])
map.Text(label="Jambudvipa", position=[22,79], classes="jambudvipa-text")
map.Text(label="Aryavarta", position=[22,79], classes="aryavarta-text", period=[0, 600])
map.TitleBox("<b>Map of major Indian empires</b><br>Classical period, source: Majumdar.")
map.TitleBox("<h2>Ancient Period (-500 to 0)</h2><p>This title appears only in ancient times</p>", period=[-500, 0])
map.TitleBox("<h2>Classical Period (-100 to 400)</h2><p>This title appears only in classical times</p>", period=[-100, 400])
map.lim(-480, 700) 
map.CSS("""
/* applies to all elements of given class */
.flag { stroke: #555; fill: rgba(200,0,0,0.4); }
.river { stroke: #0066cc; stroke-width: 2; }
.path { stroke: #8B4513; stroke-width: 2; stroke-dasharray: 5 5;}
#title { background: rgba(255,255,255,0.95); border: 1px solid #ccc; padding: 12px 16px; border-radius: 8px; max-width: 360px; z-index: 1000; }
.flag-label { color: #888;}
#controls, #controls input {width:90%;}

/* Specific styling for individual elements */
.indian-river { stroke: #ff0000; }
.ganga-river { stroke-width: 4; }
.uttarapatha-path { stroke: #ff0000; stroke-width: 2; stroke-dasharray: 5 5; }
.jambudvipa-text { font-size: 24px; font-weight: normal; color: #666666; }
""")

# Generate the map
map.show()
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
