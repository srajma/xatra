# Xatra
Xatra (pronounced _kṣatra_), a tool for making historical maps -- the data I have is currently focused on India, but I welcome expansions to the library. Installation:

```console
pip install xatra
```

For a quick start, see [examples.py](examples.py) e.g.

```python
import xatra.maps.nations as nations

nations.INDIC.plot(
    path_out="examples/nations/INDIC.html", base_map="CartoDB Positron", verbose=True
)
nations.SILKRD.plot(
    path_out="examples/nations/SILKRD.html", base_map="CartoDB Positron", verbose=True
)
nations.SEA.plot(
    path_out="examples/nations/SEA.html", base_map="CartoDB Positron", verbose=True
)
nations.INDOSPHERE.plot(
    path_out="examples/nations/INDOSPHERE.html",
    base_map="CartoDB Positron",
    verbose=True,
)
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
- Any historical visualization you'll make is a subclass of `xatra.maps.FlagMap`, which is fundamentally specified by a list of `xatra.maps.Flag`s (plus some GeoJSON data) 
  - It may be _static_, e.g. "map of ancient Indian Mahājanapadas", "map of India according to Pāṇini"
  - or _dynamic_, e.g. "map of India from 1300 BC to 500 BC, every year" or "traditional Puranic chronology"
- A `xatra.maps.Flag` is a declaration that a particular polity (Flag.name) ruled over some particular set of features (Flag.matcher), optionally for some particular specific period of history (Flag.period). 
  - `name : str` -- the name of the historical polity.
  - `period : (num, num)` (only for dynamic maps) -- period for which the flag is valid, e.g. `(-322, 500)` = "322 BC to 500 AD" -- inclusive of starting year but exclusive of ending year. 
  - `matcher : Dict -> Bool` -- returns True or False for a given GeoJSON dict, indicating which "features" (basically districts) are included in the flag.

  ```python
  from xatra.data import Loka, Varuna
  from xatra.maps import Flag, FlagMap
  from xatra.matchers import *

  flags_sample = [
    Flag(name = "Arjunayana", period = [-60, 80], matcher = KURU, ref = "Majumdar p 29"),
    Flag(name = "Kuru", period = [-1100, -900], matcher = KURU),
    Flag(
      name = "Maurya", 
      period = [-260, -180], 
      matcher = (SUBCONTINENT_PROPER | country("Afghanistan") | BALOCH) - (BACTRIA | MARGIANA | MERU | KALINGA | TAMIL_PROPER)),
    Flag(name = "Maurya", period = [-260, -180], matcher = KALINGA)
  ]

SampleMap = FlagMap(
  flags = flags_sample,
  loka = Loka.INDIC,
  varuna = Varuna.INDIAN_SUBCONTINENT,
  custom_html = 'Sample map for demonstration'
)
sample.plot(path_out = "examples/sample.html", text_outline_width ='2px') # any custom options may be set either while initializing or in plot()
  ```

- A basically comprehensive list of `matcher`s is given in `xatra.matchers`. Useful functions:
  - `country("India")`, `province("Maharashtra")`, `district("Nanded")`, `taluk("Hadgaon")` etc. However you should usually use GADM Unique IDs to avoid name clashes -- use [examples/rdviz/INDIAN_SUBCONTINENT.html](examples/rdviz/INDIAN_SUBCONTINENT.html), [examples/rdviz/SILKRD.html](examples/rdviz/SILKRD.html), [examples/rdviz/SEA.html](examples/rdviz/SEA.html) to easily find GIDs. Also note that for some countries like Pakistan and Nepal, "districts" are actually level-3 divisions and thus accessed by `taluk()`. 
  - set operations: `|`, `&`, `-`. Important to note that `-` takes precedence over the other operators in Python, so use brackets when needed.
  - Matchers for custom region names like `COLA`, `KOSALA`, `RS_DOAB`, `GY_DOAB`, `BACTRIA`. These are quite comprehensive, you probably won't have to define your own. See [examples/nations/INDIC_matchers.html](examples/nations/INDIC_matchers.html), [examples/nations/SILKRD_matchers.html](examples/nations/SILKRD_matchers.html), [examples/nations/SEA_matchers.html](examples/nations/SEA_matchers.html), [examples/nations/INDOSPHERE_matchers.html](examples/nations/INDOSPHERE_matchers.html) for a visual overview of what I have.
- The raw GeoJSON data we plot our flag lists on is stored in the `xatra/data/` directory and accessed through `xatra.data`, which holds `DataCollection`s that can be loaded as a list of GeoJSON dicts through the `DataCollection.load()` method. See [examples/rdviz/INDIAN_SUBCONTINENT.html](examples/rdviz/INDIAN_SUBCONTINENT.html), [examples/rdviz/SILKRD.html](examples/rdviz/SILKRD.html), [examples/rdviz/SEA.html](examples/rdviz/SEA.html), [examples/rdviz/WORLD.html](examples/rdviz/WORLD.html) to visualize the GeoJSON data. The only thing worth noting about `DataCollection`s is that they can contain "breaks" `DataItem(type="break", id="IND.20.20_1", level=3)`, which specify which features in the rawdata should be broken into even finer administrative detail -- e.g. in the data right now, Nanded district in Maharashtra is broken into its taluks (because the ancient tracts of Asmaka and Mulaka contained different taluks of the district), and the districts of Xinjiang province are broken into their taluks (because the districts are too big and coarse, and contained multiple ancient Tarim city-states).

- In summary, the code is quite small:
  - [`xatra.data`](xatra/data/data.py) contains the Raw GeoJSONs for areas of interest to us and the class and method for loading them (`DataCollection.load()`). It also contains `DataCollection.download()`, which is used when preparing the package.
  - [`xatra.maps.FlagMap`](xatra/maps/FlagMap.py) contains the `xatra.maps.Flag` and `xatra.maps.FlagMap` classes
  - [`xatra.maps`](xatra/maps/) is otherwise a directory of useful and interesting example Maps. This is where I would like PRs, more than anywhere else.
  - [`xatra.matchers`](xatra/matchers/Matcher.py) is a collection of `matcher` functions you can use in building your own Maps.

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
- [x] rename trigarta (needs recompile)

### technical debt
There's already some inefficiency in the code as it stands, which should be fixed.
- [ ] **(high priority)** Handling for dynamic (year-wise) maps is _terribly_ inefficient: you create a new layer with GeoJSON data for each "breakpoint year" (year at which a territorial change occurs) -- whereas the GeoJSON really remains the same in all the years, and only the styling and other properties should change. Even a tiny sample map I made [examples/dynamic.html](examples/dynamic.html) as an example is 14MB. I don't think this can be fixed with Folium at all -- maybe we need an alternate `matplotlib` implementation for dynamic maps, or work with Leaflet.js directly, idk.
- [x] **(mid priority)** All the data handling should probably be done with GeoPandas instead of manipulating `dict`s directly. In particular this would allow us to use `gpd.simplify()` to reduce file sizes.
- [x] **(low priority)** Maybe the matcher functions should be a class, with a method that works on dicts and a method that works on geopandas rows. IDK tbh. 
 - [x] **(low priority)** interface for plotting should probably look like `INDOSPHERE = Map(); INDOSPHERE.add_flags(...), INDOSPHERE.add_geojson(...)` etc. instead of the end user having to define a class.