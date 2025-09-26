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
- [ ] xatra.Admin
- [ ] xatra.Data
- [ ] possibly calculate and keep simplified geometries
- [ ] loading geojson from file instead of storing it in html; i.e. with a server

Interactive platform
- [ ] DSL
- [ ] type in DSL panel, hit render => gets transmitted to server and parsed into Python, turned into geojson and re-rendered
- [ ] while typing in DSL panel: search, select from AdminMap, preview territories (matchers/gadms/...) on AdminMap

# Xatra: The Matplotlib of Maps

Xatra is the matplotlib of maps. You can create historical maps (static or dynamic, i.e. with a time slider), data maps, maps of administrative regions, whatever. Here's a minimal example:

```python
import xatra
from xatra.loaders import gadm, naturalearth
from xatra.territory_library import NORTHERN_INDIA

map = xatra.FlagMap()

map.Flag(label="Maurya", value=gadm("IND") | gadm("PAK"))
map.Flag(label="Chola", value=gadm("IND.31") | gadm("IND.17") - gadm("IND.17.5"))
map.River(label="Ganga", value=naturalearth("1159122643"))
map.Path(label="Uttarapatha", value=[[28,77],[30,90],[40, 120]])
map.Point(label="Indraprastha", position=[28,77])
map.Text(label="Jambudvipa", position=[22,79])
map.TitleBox("<b>Sample historical map of India</b><br>Classical period, source: Majumdar.")
map.show()
```
and here's a more complex example, of a dynamic map (items can have periods so they only show up at certain time periods), with base tile layers, notes that show up in tooltips, and custom CSS for each object:

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

map.show()
```

## API Reference

### FlagMap

The main class for creating maps.

```python
map = FlagMap()
```

#### Methods

##### Adding Map Elements

The most important element of a Map is a "Flag". A Flag is a country or kingdom, and defined by a label, a territory (consisting of some algebra of GADM regions) and optionally a "period" (if period is left as None then the flag is considered to be active for the whole period of time).

- **`Flag(label, territory, period=None, note=None)`**: Add a flag (country/kingdom)
- **`River(label, geometry, note=None, classes=None, period=None)`**: Add a river
- **`Path(label, coords, classes=None, period=None)`**: Add a path/route
- **`Point(label, position, period=None)`**: Add a point of interest
- **`Text(label, position, classes=None, period=None)`**: Add a text label
- **`TitleBox(html, period=None)`**: Add a title box with HTML content

##### Styling and Configuration

- **`CSS(css)`**: Add custom CSS styles
- **`BaseOption(url_or_provider, name=None, default=False)`**: Add base map layer
- **`lim(start, end)`**: Optionally manually set time limit for dynamic maps

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
