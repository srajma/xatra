# Xatra: The Matplotlib of Maps

Xatra is the matplotlib of maps. You can create historical maps (static or dynamic, i.e. with a time slider), data maps, maps of administrative regions, whatever. Example maps produced with `xatra` can be seen [here](https://srajma.github.io/maps/).

## Installation

```bash
pip install xatra
xatra-install-data

```

This installs `xatra`, then downloads GADM administrative boundaries, Natural Earth rivers, and other geographical data from [Hugging Face](https://huggingface.co/datasets/srajma/xatra-data) to `~/.xatra/data/`. The data only needs to be downloaded once.

Check if data is installed:

```bash
xatra-install-data --check
```

If you need to re-download the data:

```bash
xatra-install-data --force
```
[Old alpha version of xatra](https://github.com/srajma/xatra1). Always make sure you're using version 2.2 or later.

## Example: Historical map

```python
import xatra
from xatra.loaders import gadm, naturalearth
from xatra.territory_library import NORTH_INDIA

map = xatra.Map()

# Flags automatically get colors from the default LinearColorSequence
# Flags with the same label will use the same color
map.Flag(label="Maurya", value=gadm("IND") | gadm("PAK"))
map.Flag(label="Chola", value=gadm("IND.31") | gadm("IND.17") - gadm("IND.17.5"))
map.Flag(label="Gupta", value=NORTH_INDIA)
map.River(label="Ganga", value=naturalearth("1159122643"))
map.Path(label="Uttarapatha", value=[[28,77],[30,90],[40, 120]])
map.Point(label="Indraprastha", position=[28,77])
map.Text(label="Jambudvipa", position=[22,79])
map.TitleBox("<b>Sample historical map of India</b><br>Classical period, source: Majumdar.")
map.show()
```

## Example: A map with everything (except dataframes)

And here's a more complex example, of a dynamic map (items can have periods so they only show up at certain time periods), with base tile layers, notes that show up in tooltips, and custom CSS for each object:

```python
import xatra
from xatra.loaders import gadm, naturalearth
from xatra.territory_library import NORTH_INDIA

map = xatra.Map()
map.BaseOption("OpenStreetMap", default=True)
map.BaseOption("Esri.WorldImagery")
map.BaseOption("OpenTopoMap")
map.BaseOption("Esri.WorldPhysical")
map.Flag(label="Maurya", value=gadm("IND") | gadm("PAK"), period=[-320, -240], note="south is lost after Ashoka's death")
map.Flag(label="Maurya", value=NORTH_INDIA, period=[-320, -180])
map.Flag(label="Gupta", value=NORTH_INDIA, period=[250, 500])
map.Flag(label="Chola", value=gadm("IND.31"), note="Chola persisted throughout this entire period")
map.Admin(gadm="IND.31", level=3)
map.AdminRivers(sources=["naturalearth", "overpass"], classes="all-rivers", note="All rivers from Natural Earth and Overpass data")
map.River(label="Ganga", value=naturalearth("1159122643"), note="can be specified as naturalearth(id) or overpass(id)", classes="ganga-river indian-river")
map.River(label="Ganga", value=naturalearth("1159122643"), period=[0, 600], note="Modern course of Ganga")
map.Path(label="Uttarapatha", value=[[28,77],[30,90],[40, 120]], classes="uttarapatha-path")
map.Path(label="Silk Road", value=[[35.0, 75.0], [40.0, 80.0], [45.0, 85.0]], period=[-200, 600])
map.Point(label="Indraprastha", position=[28,77])
map.Point(label="Delhi", position=[28.6, 77.2], period=[400, 800])
map.Text(label="Jambudvipa", position=[22,79], classes="jambudvipa-text")
map.Text(label="Aryavarta", position=[22,79], period=[0, 600])
map.TitleBox("<b>Map of major Indian empires</b><br>Classical period, source: Majumdar.")
map.TitleBox("<h2>Ancient Period (-500 to 0)</h2><p>This title appears only in ancient times</p>", period=[-500, 0])
map.TitleBox("<h2>Classical Period (-100 to 400)</h2><p>This title appears only in classical times</p>", period=[-100, 400])
map.slider(-480, 700) 
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
.chola-tehsils { stroke: #8B4513; stroke-width: 0.5; }
.all-rivers { stroke-width: 3; opacity: 0.7; }
""")

map.show()
```

## Example: Administrative map

Here's a taluk-level administrative map of the Indian subcontinent

```python
import xatra

map = xatra.Map()
map.BaseOption("OpenStreetMap", default=True)
map.BaseOption("Esri.WorldImagery")
map.BaseOption("OpenTopoMap")
map.BaseOption("Esri.WorldPhysical")
map.Admin(gadm="IND", level=3)
map.Admin(gadm="PAK", level=3) # level-3 GADM divisions in Pak are more like districts, but we don't have finer data
map.Admin(gadm="BGD", level=3)
map.Admin(gadm="AFG", level=2) # level-2 is the best we have for Afghanistan
map.Admin(gadm="NPL", level=3) # level-3 GADM divisions in Nepal are more like districts, but level-4 is WAY too fine
map.Admin(gadm="BTN", level=2) # level-2 is the best we have for Bhutan, and they're like taluks anyway
map.Admin(gadm="LKA", level=2) # level-2 is the best we have for Lanka, and they're like taluks anyway
map.AdminRivers(sources=["naturalearth", "overpass"])
map.TitleBox("<b>Taluk-level map of the Indian subcontinent.")
map.show()
```

## Example: Dataframe map

And here's a data map using DataFrames:

```python
import pandas as pd
import xatra
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm

map = xatra.Map()
map.BaseOption("OpenStreetMap", default=True)
map.BaseOption("Esri.WorldImagery")
map.BaseOption("OpenTopoMap")
map.BaseOption("Esri.WorldPhysical")

### STATIC MAP
df = pd.DataFrame({
    'GID': ['IND.31', 'IND.12', 'IND.20', 'Z01.14'],
    'population': [100, 200, 150, 100],
    # '2021': [100, 200, 150, 100],
    'note': ['ooga', 'booga', 'kooga', 'mooga'] # optional, shows up in tooltips
})

df.set_index('GID', inplace=True)
map.DataColormap(plt.cm.viridis, norm=LogNorm())
map.Dataframe(df)

map.show()
```

Or a dynamic map with a time slider: 

```python
import pandas as pd
import xatra
import matplotlib.pyplot as plt
map = xatra.Map()
map.BaseOption("OpenStreetMap", default=True)
map.BaseOption("Esri.WorldImagery")
map.BaseOption("OpenTopoMap")
map.BaseOption("Esri.WorldPhysical")

### DYNAMIC MAP
df = pd.DataFrame({
    'GID': ['IND.31', 'IND.12', 'Z01.14'],
    '2020': [100, 200, 100],
    '2020_note': ['2020_ooga', '2020_booga', '2020_mooga'],
    '2021': [110, 210, 110],
    '2021_note': ['2021_ooga', '2021_booga', '2021_mooga'],
    '2022': [120, 220, 340]
})

df.set_index('GID', inplace=True)
map.DataColormap(norm=LogNorm())
map.Dataframe(df)

map.show()
```

## Tip on coloring historical maps well

Successive Flags you define are assigned colors based on the map's `FlagColorSequence`, which is a class that determines how the next color is calculated. The default color sequence increments successive colors' hues by the conjugate golden ratio of the hue spectrum (taken from 0 to 1, so 0 is red, 1/3 is green, 2/3 is blue and 1 is red again) mod 1:

```python
map.FlagColorSequence(LinearColorSequence(colors=[<random>], step = Color.hsl(GOLDEN_RATIO, 0.0, 0.0)))
```

This is [best for making nearby colors as contrasting as possible](https://martin.ankerl.com/2009/12/09/how-to-create-random-colors-programmatically/) -- so as a general tip: place nearby flags near each other.

Sometimes you want to group some flags to be "similarly-colored" -- e.g. nations allied with each other, or belonging to the same religion. You can do this by assigning different color sequences to different groups, and using a smaller step size for each group's color sequence:

```python
#!/usr/bin/env python3

import xatra
from xatra.loaders import gadm, naturalearth
from xatra.colorseq import LinearColorSequence, Color
from matplotlib.colors import LinearSegmentedColormap

map = xatra.Map()
map.BaseOption("OpenStreetMap", default=True)
map.BaseOption("Esri.WorldImagery")
map.BaseOption("OpenTopoMap")
map.BaseOption("Esri.WorldPhysical")

map.FlagColorSequence(LinearColorSequence(colors=[Color.hex("#ff0000")], step=Color.hsl(0.03, 0.0, 0.0)), class_name="hindu")
map.FlagColorSequence(LinearColorSequence(colors=[Color.hex("#00ff00")], step=Color.hsl(0.03, 0.0, 0.0)), class_name="muslim")

map.Flag(label="Vijayanagara", value=gadm("IND.16") | gadm("IND.2") | gadm("IND.32") | gadm("IND.31") | gadm("IND.17"), classes="hindu")
map.Flag(label="Yadava", value=gadm("IND.20"), classes="hindu")
map.Flag(label="Rajput", value=gadm("IND.29"), classes="hindu")
map.Flag(label="Mughal", value=gadm("IND.25") | gadm("IND.12") | gadm("IND.34"), classes="muslim")
map.Flag(label="Ahmedabad", value=gadm("IND.11"), classes="muslim")
map.Flag(label="Bhopal", value=gadm("IND.19"), classes="muslim")
map.Flag(label="Gajapati", value=gadm("IND.26"), classes="hindu")

map.show(out_json="map_colorgroups.json", out_html="map_colorgroups.html")
```
## Disputed Territories

Some stuff to note about disputed territories:
- these are coded not under their country name (e.g. "IND.12") but under some `Z<some number>`. E.g. Jammu and Kashmir is Z01.14.
- they are typically contained under the json files of the countries that administer them. So e.g. Z01 (Jammu and Kashmir) is in the India data while Z06 (Pakistan-occupied Jammu and Gilgit-Baltistan) is in the Pakistan data.
- **This is the only important thing you need to know:** you cannot write `gadm("Z01")` -- there are no zeroth-level disputed territories, because those would just be the countries they belong to. You *can* do `gadm("Z01.14")`, `gadm("Z01.14.1")` etc. There are also custom territories `Z01`, `Z02` etc. that you can import from `xatra.territory_library`.

When mapping a country, e.g. `map.Admin(gadm="IND", level=1)`, it will map all the regions administered by it (i.e. contained in its file). When mapping a specific disputed region, e.g. `map.Flag(label="Kashmir", value=gadm("Z01.14"))` xatra finds out from data/disputed_territories/disputed_mapping.json which country it belongs to.

If for whatever reason that doesn't work, you can also specify which countries' files to find it in, e.g. `map.Admin(gadm="Z01.14", level=3, find_in_gadm=["IND"])`. But you probably won't need to use it.

The `find_in_gadm` parameter is available for:
- `map.Admin()` - Administrative regions
- `map.Flag()` - When using `gadm()` loader
- `map.Dataframe()` - DataFrame elements

## Directly doing `xatra.Flag() etc.`

All of the elements of `Map` e.g. `Flag()`, `River()` can also be directly called as methods of `xatra` i.e. `xatra.Flag()` etc. and it will apply to the "current plot". This is useful for modularity, i.e. creating some map as a module that can simply be imported into another map.

```python
#!/usr/bin/env python3
"""
Example demonstrating pyplot-style interface for Xatra.

This example shows how to use xatra.Flag(), xatra.River(), etc. 
directly without explicitly creating a Map object, similar to
how matplotlib.pyplot works.
"""

import xatra
from xatra.loaders import gadm, naturalearth
from xatra.territory_library import NORTH_INDIA

# No need to create a map object - just start adding elements!
# A Map is automatically created on first use.

xatra.BaseOption("OpenStreetMap", default=True)
xatra.BaseOption("Esri.WorldImagery")
xatra.Flag(label="Maurya", value=gadm("IND") | gadm("PAK"), period=[-320, -240])
xatra.Flag(label="Maurya", value=NORTH_INDIA, period=[-320, -180])
xatra.Flag(label="Gupta", value=NORTH_INDIA, period=[250, 500])
xatra.Flag(label="Chola", value=gadm("IND.31"), note="Chola persisted throughout")
xatra.River(label="Ganga", value=naturalearth("1159122643"), classes="major-river")
xatra.Path(label="Uttarapatha", value=[[28, 77], [30, 90], [40, 120]])
xatra.Point(label="Indraprastha", position=[28, 77])
xatra.Text(label="Jambudvipa", position=[22, 79])
xatra.TitleBox("<b>Pyplot-style Map Example</b><br>Classical period, using xatra.Flag() etc.")
xatra.CSS("""
.flag { stroke: #555; fill: rgba(200,0,0,0.4); }
.major-river { stroke: #0066cc; stroke-width: 3; }
""")

xatra.slider(-320, 500)

xatra.show(out_json="tests/map_pyplot.json", out_html="tests/map_pyplot.html")
print("Map exported to tests/map_pyplot.html")
```

## API Reference

### Map

The main class for creating maps.

```python
map = Map()
```

#### Methods

##### Adding Map Elements

The most important element of a Map is a "Flag". A Flag is a country or kingdom, and defined by a label, a territory (consisting of some algebra of GADM regions) and optionally a "period" (if period is left as None then the flag is considered to be active for the whole period of time).

- **`Flag(label, territory, period=None, note=None, color=None, classes=None)`**: Add a flag (country/kingdom)
- **`Dataframe(dataframe, data_column=None, year_columns=None, classes=None)`**: Add DataFrame-based choropleth data
- **`Admin(gadm, level, period=None, classes=None, color_by_level=1)`**: Add administrative regions from GADM data
- **`AdminRivers(period=None, classes=None, sources=None)`**: Add rivers from specified data sources
- **`River(label, geometry, note=None, classes=None, period=None, show_label=False, n_labels=1, hover_radius=10)`**: Add a river with optional label display and customizable hover detection radius
- **`Path(label, coords, classes=None, period=None, show_label=False, n_labels=1, hover_radius=10)`**: Add a path/route with optional label display and customizable hover detection radius
- **`Point(label, position, period=None, icon=None, show_label=False, hover_radius=20)`**: Add a point of interest with optional custom icon, label display, and customizable hover detection radius
- **`Text(label, position, classes=None, period=None)`**: Add a text label
- **`TitleBox(html, period=None)`**: Add a title box with HTML content

##### Styling and Configuration

- **`CSS(css)`**: Add custom CSS styles
- **`BaseOption(url_or_provider, name=None, default=False)`**: Add base map layer
- **`FlagColorSequence(color_sequence, class_name=None)`**: Set the color sequence for flags
- **`AdminColorSequence(color_sequence)`**: Set the color sequence for admin regions
- **`DataColormap(colormap, vmin=None, vmax=None, norm=None)`**: Set the color map for data elements
- **`slider(start=None, end=None, speed=5.0)`**: Set time limits and play speed for dynamic maps (speed in years per second)

##### Export

- **`show(out_json="map.json", out_html="map.html")`**: Export map to JSON and HTML files

### Pyplot-Style Functions

For convenience, Xatra provides pyplot-style functions that operate on a global "current map". These functions are available at the top level of the `xatra` module and mirror the `Map` methods.

#### Map Management

- **`get_current_map()`**: Get the current Map instance, creating one if none exists
- **`set_current_map(map)`**: Set the current Map instance (or None to clear)
- **`new_map()`**: Create a new Map and set it as current

#### Map methods are xatra methods

All Map methods are available as top-level functions that operate on the current map:

**Adding elements:**
- **`xatra.Flag(...)`**: Add a flag to the current map
- **`xatra.River(...)`**: Add a river to the current map
- **`xatra.Path(...)`**: Add a path to the current map
- **`xatra.Point(...)`**: Add a point to the current map
- **`xatra.Text(...)`**: Add a text label to the current map
- **`xatra.TitleBox(...)`**: Add a title box to the current map
- **`xatra.Admin(...)`**: Add administrative regions to the current map
- **`xatra.AdminRivers(...)`**: Add rivers to the current map
- **`xatra.Dataframe(...)`**: Add DataFrame data to the current map

**Styling and Configuration**

- **`xatra.CSS(...)`**: Add CSS styles to the current map
- **`xatra.BaseOption(...)`**: Add a base map layer to the current map
- **`xatra.FlagColorSequence(...)`**: Set flag color sequence for the current map
- **`xatra.AdminColorSequence(...)`**: Set admin color sequence for the current map
- **`xatra.DataColormap(...)`**: Set data colormap for the current map
- **`xatra.slider(...)`**: Set time controls for the current map

**Export**

- **`xatra.show(...)`**: Export the current map to JSON and HTML files

**Note:** All parameters are identical to the corresponding Map methods. The functions simply call the method on the current map instance.

### CSS Classes and Styling

Xatra provides powerful CSS-based styling for all map elements. Each element type receives default CSS classes, and you can add custom classes for fine-grained control.

#### Default CSS Classes

Every element type automatically receives a default CSS class that you can use for styling:

| Element Type | Default Class | Element |
|--------------|---------------|---------|
| `Flag()` | `.flag` | The flag geometry (polygon/path) |
| Flag labels | `.flag-label` | The text label that appears at the flag's centroid |
| `River()` | `.river` | River line geometry |
| `Path()` | `.path` | Path line geometry |
| `Point()` | `.point` | Point marker |
| `Text()` | `.text` | Text label |
| `Admin()` | `.admin` | Administrative region geometry |
| `Dataframe()` | `.dataframe` | DataFrame visualization geometry |
| `TitleBox()` | `#title` | The title box container (ID, not class) |
| `slider()` | `#controls` | The time slider controls (ID, not class) |

#### Custom CSS Classes

You can add custom classes to most elements for individual styling. Custom classes are added using the `classes` parameter:

```python
# Add custom classes to flags
map.Flag(label="Maurya", value=gadm("IND"), classes="empire hindu")
map.Flag(label="Chola", value=gadm("IND.31"), classes="kingdom hindu")
map.Flag(label="Mughal", value=gadm("IND.25"), classes="empire muslim")

# Add custom classes to other elements
map.River(label="Ganga", value=naturalearth("1159122643"), classes="sacred-river major-river")
map.Path(label="Silk Road", value=[[35, 75], [40, 80]], classes="trade-route ancient")
map.Text(label="Jambudvipa", position=[22, 79], classes="region-name large-text")
map.Admin(gadm="IND.31", level=3, classes="tamil-nadu-tehsils")
# DataFrame elements can be styled with CSS classes
# map.Dataframe(df, classes="state-data")
```

**Important:** Flag labels automatically inherit the custom classes from their parent flag. This means if you define:

```python
map.Flag(label="Maurya", value=gadm("IND"), classes="empire hindu")
```

Both the flag geometry and its label will receive the classes `empire` and `hindu`, in addition to their default classes (`.flag` and `.flag-label` respectively).

#### Styling with CSS

Use the `CSS()` method to add custom styles. You can target default classes, custom classes, or both:

```python
map.CSS("""
/* Style all flags */
.flag {
  stroke: #333;
  stroke-width: 1;
  fill-opacity: 0.4;
}

/* Style all flag labels */
.flag-label {
  font-size: 14px;
  font-weight: bold;
  color: #666;
}

/* Style specific custom classes */
.empire {
  stroke-width: 3;
  stroke: #ff0000;
}

.kingdom {
  stroke-width: 1;
  stroke-dasharray: 5 5;
}

.hindu {
  fill: rgba(255, 200, 100, 0.4);
}

.muslim {
  fill: rgba(100, 200, 255, 0.4);
}

/* Style flag labels with custom classes */
.flag-label.empire {
  font-size: 18px;
  font-weight: bold;
}

.flag-label.kingdom {
  font-size: 14px;
  font-style: italic;
}

/* Style rivers */
.river {
  stroke: #0066cc;
  stroke-width: 2;
}

.sacred-river {
  stroke: #ff6600;
  stroke-width: 4;
}

/* Style paths */
.path {
  stroke: #8B4513;
  stroke-width: 2;
  stroke-dasharray: 5 5;
}

.trade-route {
  stroke: #FFD700;
  stroke-width: 3;
}

/* Style text labels */
.text {
  font-size: 16px;
  color: #666;
}

.region-name {
  font-size: 24px;
  font-weight: bold;
}

/* Style the title box */
#title {
  background: rgba(255, 255, 255, 0.95);
  border: 1px solid #ccc;
  padding: 12px 16px;
  border-radius: 8px;
  max-width: 400px;
}

/* Style the time controls */
#controls {
  background: rgba(255, 255, 255, 0.9);
  padding: 10px;
  border-radius: 5px;
}
""")
```

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

### Color Sequences

Xatra supports automatic color assignment for both flags and admin regions using color sequences. By default, maps use `LinearColorSequence()` which generates contrasting colors. You can also use other color sequences:

- **`LinearColorSequence()`**: Generates contrasting colors (default)
- **`RotatingColorSequence()`**: Cycles through a predefined set of colors
- **`RandomColorSequence()`**: Generates random colors

#### Examples

```python
from xatra.colorseq import RotatingColorSequence, LinearColorSequence

# Set custom color sequences
map.FlagColorSequence(RotatingColorSequence())
map.AdminColorSequence(LinearColorSequence())

# Flags will automatically get colors from the sequence
map.Flag("Empire A", territory1)
map.Flag("Empire B", territory2)

# Admin regions will also get colors from their sequence
map.Admin(gadm="IND", level=3, color_by_level=1)

# You can also override with custom colors
map.Flag("Custom Empire", territory3, color="#ff0000")
```

#### Class-Based Color Sequences

Flags can be assigned to CSS classes for different color sequences. This allows you to group related flags (e.g., by religion, alliance, or historical period) with similar color schemes:

```python
from xatra.colorseq import RotatingColorSequence, LinearColorSequence

# Set up different color sequences for different classes
map.FlagColorSequence(LinearColorSequence(), None)  # Default sequence
map.FlagColorSequence(RotatingColorSequence(), "empire")  # For empires
map.FlagColorSequence(LinearColorSequence(), "kingdom")  # For kingdoms

# Add flags with different classes
map.Flag("Maurya", territory1, classes="empire")  # Uses empire colors
map.Flag("Gupta", territory2, classes="empire")   # Uses empire colors
map.Flag("Chola", territory3, classes="kingdom")  # Uses kingdom colors
map.Flag("Pandya", territory4, classes="kingdom") # Uses kingdom colors
map.Flag("Generic", territory5)  # Uses default colors (no classes)

# Flags with multiple classes use the first matching class
map.Flag("Mixed", territory6, classes="kingdom empire")  # Uses kingdom colors

# Flags with unknown classes fall back to default
map.Flag("Unknown", territory7, classes="unknown-class")  # Uses default colors
```

Flag labels automatically use a darker, more opaque version of the flag color for better readability.

### Data Visualization with DataFrames

Xatra provides powerful data visualization capabilities through the `Dataframe` method, which creates efficient choropleth maps from pandas DataFrames. This is the primary way to visualize data on maps.

The `Dataframe` method creates efficient choropleth maps from pandas DataFrames where each row represents an administrative division indexed by GID, and columns represent either a single data value or time-series data.

#### Static DataFrames (Single Data Column)

For static maps with a single data value per region:

```python
import pandas as pd
import xatra
import matplotlib.pyplot as plt

map = xatra.Map()
map.BaseOption("OpenStreetMap", default=True)

# Create a static DataFrame
df = pd.DataFrame({
    'GID': ['IND.31', 'IND.12', 'IND.20', 'Z01.14'],
    'population': [1000000, 2000000, 1500000, 500000],
    'note': ['Coastal state', 'Major state', 'Growing region', 'Disputed territory']
})

df.set_index('GID', inplace=True)

# Use custom colormap
map.DataColormap(plt.cm.viridis, vmin=0, vmax=2000000)
map.Dataframe(df)

map.show()
```

#### Dynamic DataFrames (Time-Series Data)

For dynamic maps with time-series data:

```python
import pandas as pd
import xatra
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm

map = xatra.Map()
map.BaseOption("OpenStreetMap", default=True)

# Create a dynamic DataFrame with year columns
df = pd.DataFrame({
    'GID': ['IND.31', 'IND.12', 'IND.20'],
    '2020': [1000000, 2000000, 1500000],
    '2021': [1100000, 2100000, 1600000],
    '2022': [1200000, 2200000, 1700000],
    '2020_note': ['Base year', 'Major growth', 'Steady increase'],
    '2021_note': ['Continued growth', 'Peak growth', 'Accelerating'],
    '2022_note': ['Sustained growth', 'Plateau', 'Strong growth']
})

df.set_index('GID', inplace=True)

# Use logarithmic colormap for wide-ranging data
map.DataColormap(plt.cm.plasma, norm=LogNorm(vmin=1000000, vmax=2200000))
map.Dataframe(df)
map.slider(2020, 2022)

map.show()
```

#### DataFrame Structure and Requirements

**Required Structure:**
- Must be a pandas DataFrame
- Must have GID as index or as a column named 'GID'
- GID values must correspond to GADM administrative codes (e.g., 'IND.31', 'PAK.1', 'Z01.14')

**Static Maps:**
- Single data column containing numeric values
- Optional `note` column for tooltip information
- Auto-detected when DataFrame has exactly one data column

**Dynamic Maps:**
- Multiple columns with year names (e.g., '2020', '2021', '2022')
- Optional `(year)_note` columns for year-specific tooltip information
- Auto-detected when DataFrame has multiple numeric columns

**Note Columns:**
- **Static maps**: Use a column named `note` for general tooltip information
- **Dynamic maps**: Use columns named `(year)_note` (e.g., `2020_note`, `2021_note`) for year-specific tooltip information
- Note columns are automatically excluded from data visualization and map type detection

#### Parameters

- `dataframe`: pandas DataFrame with GID-indexed rows and data columns
- `data_column`: Column name containing the data values (for static maps). If None, auto-detected.
- `year_columns`: List of year columns for time-series data (for dynamic maps). If None, auto-detected.
- `classes`: Optional CSS classes for styling
- `find_in_gadm`: Optional list of country codes to search in if GID is not found in its own file

#### Features

- **Automatic map type detection**: Static vs dynamic based on DataFrame structure
- **Missing value handling**: NaN values are rendered as fully transparent (blank)
- **Rich tooltips**: Shows data values, notes, and administrative information
- **Efficient rendering**: Data processed once during export, not on every render
- **Color mapping**: Uses the map's DataColormap for visualization
- **Time support**: Dynamic maps work with time slider and period filtering
- **Memory optimization**: Shared geometry for multiple data points per region

#### DataColormap Configuration

The `DataColormap` method controls how data values are mapped to colors. It supports both linear and non-linear color mapping:

```python
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm, PowerNorm

# Default colormap (yellow-orange-red)
map.DataColormap()

# Matplotlib colormaps
map.DataColormap(plt.cm.viridis)      # Viridis colormap
map.DataColormap(plt.cm.plasma)       # Plasma colormap
map.DataColormap(plt.cm.Reds)         # Red colormap
map.DataColormap(plt.cm.Blues)        # Blue colormap

# Custom value range
map.DataColormap(plt.cm.viridis, vmin=0, vmax=1000)

# Logarithmic normalization (great for wide-ranging data)
map.DataColormap(plt.cm.viridis, norm=LogNorm())
map.DataColormap(plt.cm.plasma, norm=LogNorm(vmin=100, vmax=1000000))

# Power normalization (custom gamma)
map.DataColormap(plt.cm.viridis, norm=PowerNorm(gamma=0.5))

# Custom colormap from color list
from matplotlib.colors import LinearSegmentedColormap
custom_cmap = LinearSegmentedColormap.from_list("custom", ["#000000", "#ffffff"])
map.DataColormap(custom_cmap)
```

**Parameters:**
- `colormap`: matplotlib colormap (e.g., `plt.cm.viridis`, `plt.cm.Reds`)
- `vmin`: Minimum value for color mapping (optional, auto-detected from data)
- `vmax`: Maximum value for color mapping (optional, auto-detected from data)
- `norm`: Normalization object (e.g., `LogNorm()`, `PowerNorm(gamma=0.5)`)

**Features:**
- **Automatic value range detection**: If vmin/vmax not specified, uses data min/max
- **Non-linear normalization**: Support for LogNorm, PowerNorm, and other matplotlib Normalize objects
- **Color bar legend**: Automatically displays the colormap with value range
- **SVG color bar**: High-quality vector color bar for the legend

### Administrative Regions

The `Admin` method displays administrative regions directly from GADM data with automatic coloring and rich tooltips:

```python
# Show all tehsils in Tamil Nadu, colored by state
map.Admin(gadm="IND.31", level=3)

# Show all tehsils in India, colored by district
map.Admin(gadm="IND", level=3, color_by_level=2)

# Show districts colored by state with custom styling
map.Admin(gadm="IND", level=2, color_by_level=1, classes="districts")
```

**Parameters:**
- `gadm`: GADM key (e.g., "IND.31" for Tamil Nadu)
- `level`: Administrative level to display (0=country, 1=state, 2=district, 3=tehsil)
- `color_by_level`: Level to group colors by (default: 1 for states)
- `period`: Optional time period as [start_year, end_year] list
- `classes`: Optional CSS classes for styling

**Features:**
- **Rich tooltips**: Shows all GADM properties (GID_0, COUNTRY, GID_1, NAME_1, etc.) on hover
- **Automatic coloring**: Regions are colored by the specified administrative level
- **Boundary-aware matching**: Uses exact prefix matching to avoid false matches
- **Time support**: Works with dynamic maps and period filtering

**Color grouping examples:**
- `level=3, color_by_level=1`: Tehsils colored by state (all tehsils in same state have same color)
- `level=3, color_by_level=2`: Tehsils colored by district (all tehsils in same district have same color)
- `level=2, color_by_level=1`: Districts colored by state (all districts in same state have same color)

### Admin Rivers

The `AdminRivers` method displays all rivers from Natural Earth and Overpass data files with automatic source identification and rich tooltips:

```python
# Show all rivers from data files
map.AdminRivers()

# Show only Natural Earth rivers
map.AdminRivers(sources=["naturalearth"])

# Show only Overpass rivers
map.AdminRivers(sources=["overpass"])

# Show all rivers with custom styling
map.AdminRivers(classes="all-rivers")

# Show rivers for a specific time period
map.AdminRivers(period=[1800, 1900], classes="historical-rivers")
```

**Parameters:**
- `period`: Optional time period as [start_year, end_year] list
- `classes`: Optional CSS classes for styling
- `sources`: List of data sources to include (default: ["naturalearth", "overpass"])

**Features:**
- **Source filtering**: Choose which data sources to include (Natural Earth, Overpass, or both)
- **Source identification**: Rivers are colored differently by source (blue for Natural Earth, orange for Overpass)
- **Rich tooltips**: Shows source information, IDs, and all available name fields
- **Automatic loading**: Loads rivers from specified data sources
- **Time support**: Works with dynamic maps and period filtering

**Tooltip information:**
- **Natural Earth rivers**: Shows "Natural Earth River", NE ID, and available name fields
- **Overpass rivers**: Shows "Overpass River", filename, and available name fields
- **Name fields**: Displays name, NAME, NAME_EN, NAME_LOC, NAME_ALT, NAME_OTHER as available
- **Additional properties**: Scale rank, feature class, min zoom level, etc.


### Point Icons

The `Icon` class allows you to customize the appearance of point markers on the map. You can use custom icons from URLs or load built-in icons from the package.

```python
#!/usr/bin/env python3
"""
Example demonstrating custom marker icons with the Point feature.
"""

import xatra
from xatra import Icon
from xatra.loaders import gadm

# Create a map
map = xatra.Map()
map.BaseOption("OpenStreetMap", default=True)
map.BaseOption("Esri.WorldImagery")
map.Flag(label="India", value=gadm("IND"))

# Example 1: Default marker (no custom icon)
map.Point(label="Default Marker", position=[28.6, 77.2])

# Example 2: Custom icon from URL
custom_icon = Icon(
    icon_url="https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png",
    shadow_url="https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
    shadow_size=(41, 41)
)
map.Point(label="Custom Red Marker", position=[19.0, 73.0], icon=custom_icon)

# Example 3: Built-in icon (if available)
builtin_icon = Icon.builtin(
    "example.svg",
    icon_size=(32, 32),
    icon_anchor=(16, 16),
    popup_anchor=(0, -16)
)
map.Point(label="Built-in Icon Marker", position=[13.0, 80.2], icon=builtin_icon)

# Example 3.5: Checking that Example 3 is really at the right place
map.Point(label="Built-in Icon Marker", position=[13.0, 80.2])

# Example 4: Another custom icon with different size
large_icon = Icon(
    icon_url="https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-green.png",
    icon_size=(30, 49),
    icon_anchor=(15, 49),
    popup_anchor=(1, -40),
    shadow_url="https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
    shadow_size=(41, 41)
)
map.Point(label="Large Green Marker", position=[23.0, 72.6], icon=large_icon)

# Example 5: Icon without shadow
no_shadow_icon = Icon(
    icon_url="https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-blue.png",
    icon_size=(25, 41),
    icon_anchor=(12, 41),
    popup_anchor=(1, -34)
)
map.Point(label="Blue Marker (No Shadow)", position=[11.0, 77.0], icon=no_shadow_icon)

# Add a title
map.TitleBox("<b>Custom Marker Icons Example</b><br>Demonstrating different icon styles for Point markers")

# Export the map
map.show(out_json="tests/map_icons.json", out_html="tests/map_icons.html")
print("Map with custom icons exported to map_icons.html")
```

### Point, Path, and River Labels

By default, Points, Paths, and Rivers display their labels in tooltips (on hover). You can optionally display the label directly on the map next to the element using the `show_label` parameter.

For Points, setting `show_label=True` displays the label to the right of the point marker:

```python
import xatra
from xatra.loaders import gadm

map = xatra.Map()
map.BaseOption("OpenStreetMap", default=True)
map.Flag(label="India", value=gadm("IND"))

# Default: label appears in tooltip on hover
map.Point(label="Mumbai", position=[19.0, 73.0])

# With show_label: label appears next to the point
map.Point(label="Delhi", position=[28.6, 77.2], show_label=True)

# Custom hover radius: easier to click on small points
map.Point(label="Small Village", position=[20.5, 75.0], hover_radius=40)

map.show()
```

For Paths, setting `show_label=True` calculates the midpoint along the path (by distance, not by index) and displays the label there. The label is automatically rotated to match the direction of the path at that point:

```python
import xatra
from xatra.loaders import gadm

map = xatra.Map()
map.BaseOption("OpenStreetMap", default=True)
map.Flag(label="India", value=gadm("IND"))

# Default: label appears in tooltip on hover
map.Path(label="Northern Route", value=[[28,77],[30,90],[35,100]])

# With show_label: label appears at the midpoint of the path, rotated to match the path direction
map.Path(label="Silk Road", value=[[28,77],[30,90],[40,120]], show_label=True)

# Multiple labels: display label at multiple evenly-spaced positions
map.Path(label="Long Trade Route", value=[[28,77],[30,90],[35,100],[40,120]], show_label=True, n_labels=3)

# Custom hover radius: easier to hover over
map.Path(label="Ancient Trade Route", value=[[25,75],[30,85]], hover_radius=20)

map.show()
```

**Label Rotation and Positioning:** Path labels are intelligently rotated to align with the path direction and offset perpendicular to the path for better readability. The algorithm:
1. Estimates the label length based on the number of characters
2. Finds path points within that distance on either side of each label position
3. Calculates the angle between those points
4. Rotates the label to match, while keeping text readable (never upside down)
5. Translates the label 8px perpendicular to the path to avoid overlapping with the path line

**Multiple Labels:** Use `n_labels` parameter to display multiple copies of the label along the path. Labels are placed at positions `k/(n+1)` where `k = 1, 2, ..., n`. For example:
- `n_labels=1` (default): One label at 1/2 (midpoint)
- `n_labels=2`: Two labels at 1/3 and 2/3
- `n_labels=3`: Three labels at 1/4, 2/4, and 3/4
- `n_labels=5`: Five labels at 1/6, 2/6, 3/6, 4/6, and 5/6

#### River Labels

For Rivers, setting `show_label=True` places the label at an intelligent location on the river. Rivers can be complex MultiLineString geometries with disconnected segments:

```python
import xatra
from xatra.loaders import gadm, naturalearth

map = xatra.Map()
map.BaseOption("OpenStreetMap", default=True)
map.Flag(label="India", value=gadm("IND"))

# Default: label appears in tooltip on hover
map.River(label="Ganga", value=naturalearth("1159122643"))

# With show_label: label appears on the river, rotated to match the river direction
map.River(label="Yamuna", value=naturalearth("1159122644"), show_label=True)

# Multiple labels: useful for long rivers
map.River(label="Nile", value=naturalearth("1159122999"), show_label=True, n_labels=5)

# Custom hover radius: easier to hover over thin rivers
map.River(label="Tributary", value=naturalearth("1159122650"), hover_radius=25)

map.show()
```

**River Label Algorithm:** For rivers with complex geometries (including MultiLineString with potentially disconnected segments):
1. Samples points from all river segments (up to 200 points for performance)
2. Finds the two most distant points along the river geometry (the pair that maximizes river distance)
3. For each label position `k/(n+1)`, interpolates along the line between these distant points
4. Finds the nearest point on the actual river geometry to each interpolated position
5. Places labels at these nearest points on the river
6. Calculates rotation angle based on the line between the two distant points
7. Translates each label 12px perpendicular to the river for better visibility

This approach ensures labels are distributed along the actual river course rather than just across a bounding box, providing much better geographic distribution for long, complex rivers.

**Multiple Labels:** The `n_labels` parameter distributes labels evenly along the river's longest axis:
- `n_labels=1` (default): One label at the midpoint along the river's longest dimension
- `n_labels=3`: Three labels distributed along the river's extent
- `n_labels=5`: Five labels for very long rivers like the Nile or Ganges, spread from end to end

**Styling Labels:**

You can style Point, Path, and River labels using CSS. Labels have the classes `point-label`, `path-label`, and `river-label` respectively, in addition to the `text-label` class.

**Customizing Offset Distance:** 

Labels use nested divs to separate rotation (calculated automatically) from translation (customizable via CSS):
- **Outer div**: Applies rotation based on path/river direction (set via inline style, not customizable)
- **Inner div**: Applies perpendicular offset using `transform: translateY()` (fully customizable via CSS)

This structure allows you to customize the offset distance without affecting the rotation. Default offsets are:
- **Points**: 10px to the right
- **Paths**: 8px perpendicular
- **Rivers**: 16px perpendicular

To customize the offset, simply override the `transform` property on the label class:

```python
map.CSS("""
.point-label {
  font-size: 14px;
  font-weight: bold;
  color: #cc0000;
  background: rgba(255,255,255,0.8);
  padding: 2px 6px;
  border-radius: 3px;
}

.path-label {
  font-size: 16px;
  color: #0066cc;
  font-style: italic;
  background: rgba(255,255,255,0.9);
  padding: 4px 8px;
  border-radius: 4px;
  border: 1px solid #0066cc;
  /* Customize offset distance (default is -8px) */
  transform: translateY(-12px);
}

.river-label {
  font-size: 15px;
  color: #0099cc;
  font-weight: bold;
  background: rgba(255,255,255,0.85);
  padding: 3px 7px;
  border-radius: 3px;
  border: 1px solid #0099cc;
  /* Customize offset distance (default is -16px) */
  transform: translateY(-20px);
}

/* You can also use custom classes */
.trade-route .path-label {
  color: #ff9900;
  border-color: #ff9900;
}

.sacred-river .river-label {
  color: #ff6600;
  border-color: #ff6600;
  /* Increase offset for this specific river */
  transform: translateY(-24px);
}
""")

map.Path(label="Trade Route", value=[[28,77],[30,90],[40,120]], show_label=True, classes="trade-route")
map.River(label="Ganga", value=naturalearth("1159122643"), show_label=True, classes="sacred-river")
```

### Multi-Layer Tooltips

Xatra features an intelligent **multi-layer tooltip system** that shows information for **all overlapping elements** at the cursor position, not just the topmost element.

When you hover over any location on the map, the tooltip displays information from all elements under the cursor:
- **Flags** (countries/kingdoms)
- **Admin regions** (states, districts, tehsils)
- **DataFrames** (data values)
- **Rivers** and **Paths**
- **Points** (cities, landmarks)

The tooltips are displayed in a clean, organized format with each element type clearly labeled.

**Example:**
```python
import xatra
from xatra.loaders import gadm

map = xatra.Map()
map.BaseOption("OpenStreetMap", default=True)

# These elements overlap - hovering over Tamil Nadu will show all tooltips
map.Flag(label="India", value=gadm("IND"), note="Republic of India")
map.Flag(label="Tamil Nadu", value=gadm("IND.31"), note="State in southern India")
map.Admin(gadm="IND.31", level=2)  # Districts

# Point in the overlapping area - hovering near Chennai shows Flag + Admin + Point tooltips
map.Point(label="Chennai", position=[13.0827, 80.2707])

map.show()
```

When you hover over Chennai, you'll see tooltips for:
- The "India" flag
- The "Tamil Nadu" flag
- The admin region (Chennai district)
- The "Chennai" point marker

#### Customizing Hover Detection Radius

For **Point**, **River**, and **Path** elements, you can customize the hover detection radius using the `hover_radius` parameter (in pixels). This controls how close your cursor needs to be to trigger the tooltip.

```python
# Rivers with larger hover radius for easier selection
map.River(label="Ganga", value=naturalearth("1159122643"), hover_radius=20)

# Paths with custom hover radius
map.Path(label="Silk Road", value=[[35, 75], [40, 80]], hover_radius=15)

# Points with larger hover radius for easier clicking
map.Point(label="Delhi", position=[28.6, 77.2], hover_radius=30)
```

**Default hover radii:**
- **Rivers**: 10 pixels
- **Paths**: 10 pixels  
- **Points**: 20 pixels

**Note:** The hover radius is specified in screen pixels and automatically scales with map zoom level. A larger hover radius makes elements easier to hover over, especially useful for thin rivers or small points.

#### Customizing Multi-Tooltip Styling

The multi-layer tooltip appearance can be customized using CSS:

```python
map.CSS("""
/* Customize the multi-tooltip container */
#multi-tooltip {
  background: rgba(255, 255, 255, 0.98);
  border: 3px solid #0066cc;
  border-radius: 8px;
  font-family: 'Georgia', serif;
  max-width: 500px;
}

/* Style the element type labels */
#multi-tooltip .tooltip-type {
  color: #cc6600;
  font-weight: bold;
  font-size: 13px;
  text-transform: uppercase;
}

/* Style the tooltip content */
#multi-tooltip .tooltip-content {
  color: #333;
  font-size: 14px;
  line-height: 1.6;
}

/* Style individual tooltip items */
#multi-tooltip .tooltip-item {
  margin-bottom: 10px;
  padding-bottom: 10px;
  border-bottom: 2px solid #ddd;
}
""")
```

## Performance

Xatra is optimized for large, complex maps with many elements:

- **Geometry Caching**: Territory geometries are cached globally by string representation, with both in-memory and on-disk persistence. Identical territory expressions (e.g., `gadm("IND") | gadm("PAK")`) are computed only once and reused across all instances.
- **File Caching**: Data files (GADM, Natural Earth) are cached in memory to avoid repeated disk reads
- **Centroid Pre-computation**: Flag centroids are calculated once during export, not on every render
- **Layer Visibility Toggling**: Dynamic maps use efficient visibility toggling instead of recreating layers
- **Memory Management**: Use `clear_file_cache()` to free memory when working with very large datasets

### Geometry Cache Management

The global geometry cache can be managed programmatically:

```python
import xatra

# Clear cache
xatra.clear_cache()                    # Clear both memory and disk
xatra.clear_cache(memory_only=True)    # Clear only memory
xatra.clear_cache(disk_only=True)      # Clear only disk

# Get cache statistics
stats = xatra.cache_stats()
print(f"Hit rate: {stats['hit_rate']:.1%}")
print(f"Memory cache: {stats['memory_cache_size']} items")
print(f"Disk cache: {stats['disk_cache_size']} files")
```

Cache files are stored in `~/.xatra/cache/` and persist across program runs for maximum performance.

### Time Debugging

Xatra includes a comprehensive time debugging feature that helps you understand where time is being spent when creating maps. When enabled, it prints detailed timing information for every major operation with HH:MM:SS timestamps and tracks **exclusive time** (time spent in each function excluding time spent in other tracked functions called from it).

#### Enabling Time Debugging

**Method 1: Environment Variable (Recommended)**
```bash
DEBUG_TIME=1 python your_script.py
```

**Method 2: Programmatically**
```python
import xatra

xatra.set_debug_time(True)

# Now create your map - all operations will be timed
map = xatra.Map()
map.Flag("India", xatra.gadm("IND"))
map.show()
```

**Environment Variable Values:**
- `DEBUG_TIME=1`, `true`, `yes`, `on` → Enable debugging
- `DEBUG_TIME=0`, `false`, `no`, `off` → Disable debugging (default)
- Unset or empty → Disable debugging (default)

When time debugging is enabled, you'll see timing information for:

**Data Loading Operations:**
- Loading GADM data files
- Loading Natural Earth features
- Loading Overpass data
- Reading JSON files from disk (with cache hits/misses)
- Converting GeoJSON to Shapely geometries

**Map Element Operations:**
- Adding Flags, Rivers, Paths, Points, Text, etc.
- Adding Admin regions
- Adding DataFrames

**Processing Operations:**
- Territory geometry conversions
- Pax-max aggregation for dynamic maps
- Centroid calculations
- Period filtering

**Export Operations:**
- Exporting to JSON format
- Exporting to HTML format

#### Exclusive Time Tracking

The time debugging system tracks two types of time for each function:

- **Total Time**: The complete time spent in the function, including time spent in other tracked functions called from it
- **Exclusive Time**: The time spent in the function itself, excluding time spent in other tracked functions called from it

This helps identify which functions are doing the most actual work versus just calling other functions.

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
[14:23:46]     ✓ FINISH: Paxmax aggregation
[14:23:47]   ✓ FINISH: Export to JSON
[14:23:47]   → START: Export to HTML
[14:23:47]   ✓ FINISH: Export to HTML
[14:23:47] ✓ FINISH: Show (export map)
```

#### Disabling Time Debugging

**Method 1: Environment Variable**
```bash
unset DEBUG_TIME
# or
export DEBUG_TIME=0
```

**Method 2: Programmatically**
```python
# Disable time debugging
xatra.set_debug_time(False)
```

**Note:** The programmatic methods override the environment variable setting.

#### Automatic Timing Display

When time debugging is enabled, timing statistics and charts are **automatically displayed** when your program exits. This means you don't need to manually call any functions - the performance analysis appears automatically!

#### Manual Timing Analysis

You can also manually analyze the timing data if needed:

**Print Timing Summary:**
```python
import xatra

# Print a formatted table of timing statistics
xatra.print_timing_summary()
```

**Get Raw Timing Data:**
```python
# Get timing statistics as a dictionary
stats = xatra.get_timing_stats()
print(f"Functions tracked: {len(stats['exclusive_times'])}")
print(f"Total function calls: {sum(stats['call_counts'].values())}")
```

**Create Timing Charts:**
```python
# Display an interactive timing chart (requires matplotlib)
xatra.show_timing_chart()

# Save timing chart to file
xatra.plot_timing_chart(save_path="timing_analysis.png")

# Get chart without displaying it
fig = xatra.plot_timing_chart(show_chart=False)
```

**Reset Timing Statistics:**
```python
# Clear all timing data
xatra.reset_timing_stats()
```

The timing chart shows:
- **Top chart**: Horizontal bar chart of exclusive times for the top 15 functions
- **Bottom chart**: Side-by-side comparison of exclusive vs total times
- **Summary statistics**: Total times, function counts, and call counts

**Automatic Display Features:**
- Timing statistics are automatically printed when the program exits
- Charts are automatically displayed (if matplotlib is available)
- No manual intervention required - just enable debug time and run your code
- Works with both environment variable (`DEBUG_TIME=1`) and programmatic (`xatra.set_debug_time(True)`) methods

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

## TODO

Kanging
- [ ] copy maps from old xatra (colonies and hsr remaining)
- [ ] maps of north-west: Panini, Puranas and Greek
- [ ] full history timeline
- [x] GDP per capita map
- [x] admin map

Features
- [x] Orient flag labels in direction of flag
- [x] option for different point markers besides pin
- [x] option for point labels, path, river labels
- [x] option to create multiple path, river labels.
- [x] And maybe calculate river label path using bounding box.
- [x] ideally make it so hovering hovers on *all* flags/elements at that point
- [x] "get current map" similar to matplotlib, to make maps more modular
- [x] Hover over color bar
- [x] periods for things other than flags
- [x] xatra.Admin
- [x] xatra.Flag color groups
- [x] xatra.Dataframe with notes and DataColormap
- [x] do we need to redraw everything each frame?
- [ ] MAYBE: class-based show labels, etc. Not that important. Main thing you'd use it for is hiding labels and CSS is enough for that.
- [ ] MAYBE: grouping of map elements and layer selection. PROBLEM: this is hard.
- [ ] MAYBE: calculate and keep simplified geometries (check what the main source of slowness is) PROBLEM: boundaries between different geometries no longer fit perfectly -- use mapshaper
- [ ] MAYBE: loading geojson from file instead of storing it in html; i.e. with a server

Dev
- [x] Get it in a publishable state
- [x] why not just upload my cache. Need to change the HF repository to have a data and a cache folder
- [x] Publish it
- [x] time debugging

Interactive platform
- [ ] DSL
- [ ] type in DSL panel, hit render => gets transmitted to server and parsed into Python, turned into geojson and re-rendered
- [ ] while typing in DSL panel: search, select from AdminMap, preview territories (matchers/gadms/...) on AdminMap
- [ ] ideally we want a crud type of thing for real-time updating

Stylistic changes
- [x] The slider seems to be hidden under the map: I can move it around by clicking where it should be, but can only actually see it visually when I'm zooming out or am fully zoomed out (because that's when the blank space behind the map appears before the tiles load to fill it up). The slider should be a fixed element on the screen *over* the map that stays at the exact same position regardless of where I pan or zoom to.
- [x] the TitleBox only appears when fully zoomed out. It too should appear as a fixed element on the screen *over* the map that stays at the exact same position regardless of where I pan or zoom to.
- [x] custom IDs and classes for styling
- [x] The tooltip that appears upon hovering over a flag should appear at the point of my cursor, and move with my cursor. I thought this is how default Leaflet tooltips appear? Why does it appear at a fixed point in our implementation?
- [x] also need flag names to appear at centroid
- [x] map.Text labels should by default just be plain text, without the border box and all that. Its default style could be different maybe "font-size: 16px; font-weight: bold; color: #666666"
- [x] color assignment
- [x] t logachoice of BaseMaps
- [x] slider shouldn't appear for static maps
- [x] map.slider()
- [x] slider play button plus positions of years, start and end year
- [x] watermark

Libraries
- [x] copy matchers from old xatra

Bugfixes
- [ ] Point labels should align to icon anchor
- [ ] Better documentation for icons
- [ ] classes for Points that affect their labels
- [ ] center map at center; and allow setting zoom
- [ ] how to do refs?
- [x] Efficiency: cache territory geometries by string rep rather than per-object
- [x] optimize paxmax aggregation
- [x] AdminRivers don't work again.
- [x] ~~show bounding boxes of flag paxmaxes when selected~~ instead just show outline on hover
- [x] AdminRivers doesn't work.
- [x] River name rendering position is weird
- [x] River names don't render for overpass
- [x] color bar hover on correct position
- [x] Dataframe should not work the stupid way it does. It should be a simple chloropleth, not creating new geometries for each year.
- [x] Static Dataframe maps don't work
- [x] logarithmic/normalized color bars with matplotlib Normalize support
- [x] Make sure color bars are shown correctly regardless of how it is
- [x] Support a "note" column for Dataframe.
- [x] Don't assume missing values
- [x] classes attribute not being passed on
- [x] disputed areas -- should show up for Admin, and more importantly should be able to specify source file
- [x] disputed areas admin map
- [x] fix issue with disputed areas
- [x] top-level disputed areas
- [x] debug slowness
- [x] xatra.Data issue with colors of data in dynamic maps and exact range
- [x] sub-regions -- use boundary-aware starts matching, same as elsewhere
- [x] Mark map as dynamic if any element as period
- [x] why country name appears on Data tooltip?
- [x] default color scheme
- [x] add color map in html
- [x] rename Colormap to Colormap
- [x] efficiency and documentation
- [x] [WONTFIX] make outline of rivers show on hover too -- need rivers to be grouped for that
