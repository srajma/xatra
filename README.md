# Xatra
Xatra (pronounced _kṣatra_), a tool for making historical maps -- the data I have is currently focused on India, but I welcome expansions to the library. Installation:

```console
pip install xatra
```

For a quick start, see [examples.py](examples.py) e.g.

```python
import xatra.maps.nations as nations

# any custom options may be set either while initializing or in plot()

nations.INDIC.plot(path_out="examples/nations/INDIC.html") 
nations.SILKRD.plot(path_out="examples/nations/SILKRD.html")
nations.SEA.plot(path_out="examples/nations/SEA.html") 
nations.INDOSPHERE.plot(path_out="examples/nations/INDOSPHERE.html")
```

The outputs are in 
* [examples/nations/INDIC.html](examples/nations/INDIC.html)
* [examples/nations/SILKRD.html](examples/nations/SILKRD.html)
* [examples/nations/SEA.html](examples/nations/SEA.html)
* [examples/nations/INDOSPHERE.html](examples/nations/INDOSPHERE.html).

Note: view this documentation,
 - through the project website: [srajma.github.io/xatra](https://srajma.github.io/xatra/) to see the visualizations properly
 - through Github: [github.com/srajma/xatra](https://github.com/srajma/xatra) to see the code

## Documentation

Key ideas:
- **`xatra.FlagMap`**: Any historical visualization you'll make is an instance of `xatra.FlagMap`, which is fundamentally specified by a list of `xatra.Flag`s (plus some GeoJSON data) 
  - It may be _static_, e.g. "map of ancient Indian Mahājanapadas", "map of India according to Pāṇini"
  - or _dynamic_, e.g. "map of India from 1300 BC to 500 BC, every year" or "traditional Puranic chronology"
- **`xatra.Flag`**: A `xatra.Flag` is a declaration that a particular polity (`Flag.name`) ruled over some particular set of features (`Flag.matcher`), optionally for some particular specific period of history (`Flag.period`). 
  - `name : str` -- the name of the historical polity.
  - `period : (num, num)` (only for dynamic maps) -- period for which the flag is valid, e.g. `(-322, 500)` = "322 BC to 500 AD" -- inclusive of starting year but exclusive of ending year. 
  - `matcher : xatra.Matcher` -- a `xatra.Matcher` object is basically a function that returns True or False for a given GeoJSON feature (dict or GeoPandas Row), i.e. the characteristic function for the set of features claimed by the flag.

```python
from xatra.data import Loka, Varuna
from xatra.maps import Flag, FlagMap
from xatra.matchers import *

flags_sample = [
    Flag(name="Arjunayana", period=[-60, 80], matcher=KURU, ref="Majumdar p 29"),
    Flag(name="Kuru", period=[-1100, -900], matcher=KURU),
    Flag(
        name="Maurya",
        period=[-260, -180],
        matcher=(SUBCONTINENT_PROPER | country("Afghanistan") | BALOCH)
        - (BACTRIA | MARGIANA | MERU | KALINGA | TAMIL_PROPER),
    ),
    Flag(name="Maurya", period=[-260, -180], matcher=KALINGA),
]

SampleMap = FlagMap(
    flags=flags_sample,
    loka=Loka.INDIC,
    varuna=Varuna.INDIAN_SUBCONTINENT,
    custom_html="Sample map for demonstration",
)
sample.plot(path_out="examples/sample.html")
```

- **`xatra.Matcher`**: A basically comprehensive list of `matcher`s is given in [`xatra.matchers`](xatra/matchers/matcherlib.py). Useful functions:
  - `country("India")`, `province("Maharashtra")`, `district("Nanded")`, `taluk("Hadgaon")` etc. However you should usually use GADM Unique IDs to avoid name clashes -- use [examples/rdviz/INDIAN_SUBCONTINENT.html](examples/rdviz/INDIAN_SUBCONTINENT.html), [examples/rdviz/SILKRD.html](examples/rdviz/SILKRD.html), [examples/rdviz/SEA.html](examples/rdviz/SEA.html) to easily find GIDs. Also note that for some countries like Pakistan and Nepal, "districts" are actually level-3 divisions and thus accessed by `taluk()`. 
  - set operations: `|`, `&`, `-`. Important to note that `-` takes precedence over the other operators in Python, so use brackets when needed.
  - Matchers for custom region names like `COLA`, `KOSALA`, `RS_DOAB`, `GY_DOAB`, `BACTRIA`. These are quite comprehensive, you probably won't have to define your own. See [examples/nations/INDIC_matchers.html](examples/nations/INDIC_matchers.html), [examples/nations/SILKRD_matchers.html](examples/nations/SILKRD_matchers.html), [examples/nations/SEA_matchers.html](examples/nations/SEA_matchers.html), [examples/nations/INDOSPHERE_matchers.html](examples/nations/INDOSPHERE_matchers.html) for a visual overview of what I have.
- **`xatra.DataCollection`**: The raw GeoJSON data we plot our flag lists on is stored in the `xatra/data/` directory and accessed through the `xatra.DataCollection` class and its `load()` method in [`xatra.data`](xatra/data/data.py). Useful DataCollections are in [`xatra.data.Loka`](xatra/data/varuna.py) and [`xatra.data.Varuna`](xatra/data/Varuna.py). See [examples/rdviz/INDIAN_SUBCONTINENT.html](examples/rdviz/INDIAN_SUBCONTINENT.html), [examples/rdviz/SILKRD.html](examples/rdviz/SILKRD.html), [examples/rdviz/SEA.html](examples/rdviz/SEA.html), [examples/rdviz/WORLD.html](examples/rdviz/WORLD.html) to visualize the GeoJSON data. The only thing worth noting about `DataCollection`s is that they can contain "breaks" `DataItem(type="break", id="IND.20.20_1", level=3)`, which specify which features in the rawdata should be broken into even finer administrative detail -- e.g. in the data right now, Nanded district in Maharashtra is broken into its taluks (because the ancient tracts of Asmaka and Mulaka contained different taluks of the district), and the districts of Xinjiang province are broken into their taluks (because the districts are too big and coarse, and contained multiple ancient Tarim city-states).

- In summary, the code is quite small:
  - [`xatra.data`](xatra/data/data.py) contains the Raw GeoJSONs for areas of interest to us and the class and method for loading them (`DataCollection.load()`). It also contains `DataCollection.download()`, which is used when preparing the package.
  - [`xatra.maps.FlagMap`](xatra/maps/FlagMap.py) contains the `xatra.Flag` and `xatra.FlagMap` classes
  - [`xatra.maps`](xatra/maps/) is otherwise a directory of useful and interesting example Maps. This is where I would like PRs, more than anywhere else.
  - [`xatra.matchers.Matcher`](xatra/matchers/Matcher.py) is the `xatra.Matcher` class, and [`xatra.matchers.matcherlib`](xatra/matchers/matcherlib.py) is a collection of `matcher` functions you can use in building your own Maps.

## Appendix: optional arguments

Optional arguments can be specified either while initiazing a `xatra.FlagMap` object or to `plot()` (which overrides the optional arguments set during initialization).

```python
"""
custom_colors (Dict[str, str]): custom colours for flags to override any calculated ones.
color_segments (int): Flags within this distance of each other in self.flags will be assigned
    contrasting colours (unless forced otherwise in self.custom_colors). Defaults to 8.
location (List[float]): Initial position of Folium map. Defaults to calculated from loka.
    E.g. India: [20.5937, 78.9629]. Brahmavarta: [29.9691899, 76.7260054]. Meru: [39, 71.9610313].
zoom_start (int): Initial zoom of Folium map. Defaults to 5.
color_legend (bool): to include a legend of colours? Defaults to False.
custom_html (str): Custom HTML to be added to the top of the legend, e.g. a title. Defaults to "".
names_on_map (bool): show flag labels on the map? (tooltips will show on hover regardless). Defaults
    to True.
opacity (float): Opacity of the flags. Defaults to 0.7.
text_outline_width (str): Width of the text outline. Defaults to None. Set either this
    or text_outline_color to None to disable text outline. Generally should be like 0.1px.
text_outline_color (str): Color of the text outline. Defaults to '#FFFFFF'. Set either
    text_outline_width or this to None to disable text outline.
font_size (str): Font size of the flag labels. Defaults to "10pt".
font_family (str): Font family of the flag labels. Defaults to system theme font, i.e.
    "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif".
tolerance (float): Tolerance for simplifying geometries. Defaults to 0.01.
"base_maps" (Dict[str, bool]): Base maps to show. Those with value True will be shown by default,
    others will be options in the Layer Control. Defaults to
    {
        "OpenStreetMap" : True,
        "Esri.WorldImagery" : False,
        "OpenTopoMap" : False,
        "Esri.WorldPhysical" : False,
    }
    Stuff that
    you can include in the keys (can also be {} to have no base map):
        "OpenStreetMap" (general all-rounder)
        "CartoDB.Positron" (like OSM but light and minimalistic)
        "CartoDB.PositronNoLabels" (like OSM but light and minimalistic)
        "USGS.USImageryTopo" (physical map: satellite view)
        "Esri.WorldImagery" (physical map: satellite view)
        "OpenTopoMap" (physical map: topographic)
        "Esri.WorldPhysical" (physical map: general)
        "Esri.OceanBasemap" (physical map: rivers network)
        See http://leaflet-extras.github.io/leaflet-providers/preview/ for a full list.
verbose (bool): Print progress? Defaults to True.
"""
```

## TODO

If you're interested in contributing to this open-source project, please do so! I'm an amateur at coding, and this is just a side-project of mine, and I'm quite busy with real work to do everything I wish I could. 

Ideally if you'd like to contribute, create an issue and assign it to yourself, then start a pull request. I _will_ review and approve pull requests daily. Here's a to-do list of priorities you could work on:

- [ ] Slider-based control for dynamic maps -- right now each year is just a layer which you can toggle by pressing the "down" key in the toggle. See the [technial debt](#technical-debt) section below for details.
- [ ] Make example maps and visualizations:
  - [x] "nations" -- classical nations of antiquity
  - [ ] north-west circa 322 BC (panini, alexandrian records, puranic etc.)
  - [ ] standard mainstream chronology, at least for some period (probably depends on better implementation for dynamic maps)
  - [ ] early south-east asian colonies (probably depends on handling for cities)
  - [ ] continents of the world, names of india
- [x] add Suvarnabhumi and Tibet-adjacent lands to matchers.py
- [x] make everything verbose
- [x] Loading all the stuff is really inefficient, fix that
- [x] make legend options do something
- [x] make flag name appear at center of geometry
- [ ] handling for making cities appear on map (`data.Pura`)
- [x] add more stuff to Terai
- [x] fix the double display
- [x] rename trigarta
- [x] add tibet to SEA
- [x] fix tooltips on plot_flags_as_layers

### technical debt
There's already some inefficiency in the code as it stands, which should be fixed.
- [ ] **(high priority)** Handling for dynamic (year-wise) maps is _terribly_ inefficient: you create a new layer with GeoJSON data for each "breakpoint year" (year at which a territorial change occurs) -- whereas the GeoJSON really remains the same in all the years, and only the styling and other properties should change. Even a tiny sample map I made [examples/dynamic.html](examples/dynamic.html) as an example is 14MB. I don't think this can be fixed with Folium at all -- maybe we need an alternate `matplotlib` implementation for dynamic maps, or work with Leaflet.js directly, idk.
- [x] **(mid priority)** All the data handling should probably be done with GeoPandas instead of manipulating `dict`s directly. In particular this would allow us to use `gpd.simplify()` to reduce file sizes.
- [x] **(low priority)** Maybe the matcher functions should be a class, with a method that works on dicts and a method that works on geopandas rows. IDK tbh. 
 - [x] **(low priority)** interface for plotting should probably look like `INDOSPHERE = Map(); INDOSPHERE.add_flags(...), INDOSPHERE.add_geojson(...)` etc. instead of the end user having to define a class.

### polls

Live versions of the designs being polled:

* [Control](examples/polls/0_control.html)
* [Poll 1: different basemap](examples/polls/1_basemap.html)
* [Poll 2: opaque](examples/polls/2_opacity.html)
* [Poll 3: smaller font size](examples/polls/3_fontsize.html)
* [Poll 4: font family: system theme (i.e. Segoe for MS, Roboto for Android etc.)](examples/polls/4_font_system.html)
* [Poll 5: font family: Gabriola](examples/polls/5_font_gabriola.html)
* [Poll 6: font family: Papyrus](examples/polls/6_font_papyrus.html)