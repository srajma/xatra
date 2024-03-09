# Xatra
Xatra (pronounced _kṣatra_), a tool for making historical maps -- the data I have is currently focused on India, but I welcome expansions to the library. Installation:

```console
pip install xatra
```

For a quick start, see [examples.py](examples.py) e.g.

```python
import xatra.maps.nations as nations

nations.INDIC(verbose=True).plot(path_out="examples/nations/INDIC.html")
nations.SILKRD(verbose=True).plot(path_out="examples/nations/SILKRD.html")
nations.SEA(verbose=True).plot(path_out="examples/nations/SEA.html")
nations.INDOSPHERE(verbose=True).plot(path_out="examples/nations/INDOSPHERE.html")
```

The outputs are in 
* [examples/nations/INDIC.html](examples/nations/INDIC.html)
* [examples/nations/SILKRD.html](examples/nations/SILKRD.html)
* [examples/nations/INDOSPHERE.html](examples/nations/WORLD.html).

Note: view this documentation,
 - through the project website: [srajma.github.io/xatra](https://srajma.github.io/xatra/) to see the visualizations properly
 - through Github: [github.com/srajma/xatra](https://github.com/srajma/xatra) to see the code

## Documentation

Key ideas:
- Any historical visualization you'll make is a subclass of `xatra.maps.Map`, which is fundamentally specified by a list of `xatra.maps.Flag`s (plus some GeoJSON base map, etc.) 
  - It may be _static_, e.g. "map of ancient Indian Mahājanapadas", "map of India according to Pāṇini"
  - or _dynamic_, e.g. "map of India from 1300 BC to 500 BC, every year" or "traditional Puranic chronology"
- A `xatra.maps.Flag` is a declaration that a particular polity (Flag.name) ruled over some particular set of features (Flag.matcher), optionally for some particular specific period of history (Flag.period). 
  - `name : str` -- the name of the historical polity.
  - `period : (num, num)` (only for dynamic maps) -- period for which the flag is valid, e.g. `(-322, 500)` = "322 BC to 500 AD" -- inclusive of starting year but exclusive of ending year. 
  - `matcher : Dict -> Bool` -- returns True or False for a given GeoJSON dict, indicating which "features" (basically districts) are included in the flag.

  ```python
  from xatra.data import Loka, Varuna
  from xatra.maps import Flag, Map
  from xatra.matchers import *

  flags_sample = [
    Flag(name = "Arjunayana", period = [-60, 80], matcher = KURU, ref = "Majumdar p 29"),
    Flag(name = "Kuru", period = [-1100, -900], matcher = KURU),
    Flag(
      name = "Maurya", 
      period = [-260, -180], 
      matcher = minus(
        union(SUBCONTINENT_PROPER, country("Afghanistan"), BALOCH), 
        union(BACTRIA, MARGIANA, MERU, KALINGA, TAMIL_PROPER))),
    Flag(name = "Maurya", period = [-260, -180], matcher = KALINGA)
  ]

  class Sample(Map):
      def __init__(self, **kwargs):
          super().__init__(**kwargs)

      @property
      def geojson(self):
          return Loka.INDIC.load(verbose=self.verbose)

      @property
      def geojson_rivers(self):
          return Varuna.INDIAN_SUBCONTINENT.load(verbose=self.verbose)


  sample = Sample()
  sample.plot(path_out = "examples/sample.html")
  ```

- A basically comprehensive list of `matcher`s is given in `xatra.matchers`. Useful functions:
  - `country("India")`, `province("Maharashtra")`, `district("Nanded")`, `taluk("Hadgaon")` etc. However you should usually use GADM Unique IDs to avoid name clashes -- use [examples/rdviz/INDIAN_SUBCONTINENT.html](examples/rdviz/INDIAN_SUBCONTINENT.html), [examples/rdviz/SILKRD.html](examples/rdviz/SILKRD.html), [examples/rdviz/SEA.html](examples/rdviz/SEA.html) to easily find GIDs. Also note that for some countries like Pakistan and Nepal, "districts" are actually level-3 divisions and thus accessed by `taluk()`. 
  - set operations: `union(*args)`, `inter(*args)`, `minus(arg1, arg2)`.
  - Matchers for custom region names like `COLA`, `KOSALA`, `RS_DOAB`, `GY_DOAB`, `BACTRIA`. These are quite comprehensive, you probably won't have to define your own. See [examples/nations/WORLD.html](examples/nations/WORLD.html) for a visual overview of what I have.
- The raw GeoJSON data we plot our flag lists on is stored in the `xatra/data/` directory and accessed through `xatra.data`, which holds `DataCollection`s that can be loaded as a list of GeoJSON dicts through the `DataCollection.load()` method. See [examples/rdviz/INDIAN_SUBCONTINENT.html](examples/rdviz/INDIAN_SUBCONTINENT.html), [examples/rdviz/SILKRD.html](examples/rdviz/SILKRD.html), [examples/rdviz/SEA.html](examples/rdviz/SEA.html) to visualize the GeoJSON data. The only thing worth noting about `DataCollection`s is that they can contain "breaks" `DataItem(type="break", id="IND.20.20_1", level=3)`, which specify which features in the rawdata should be broken into even finer administrative detail -- e.g. in the data right now, Nanded district in Maharashtra is broken into its taluks (because the ancient tracts of Asmaka and Mulaka contained different taluks of the district), and the districts of Xinjiang province are broken into their taluks (because the districts are too big and coarse, and contained multiple ancient Tarim city-states).

- In summary, the code is quite small:
  - [`xatra.data`](xatra/data/data.py) contains the Raw GeoJSONs for areas of interest to us and the class and method for loading them (`DataCollection.load()`). It also contains `DataCollection.download()`, which is used when preparing the package.
  - [`xatra.maps.FlagMap`](xatra/maps/FlagMap.py) contains the `xatra.maps.Flag` and `xatra.maps.Map` classes
  - [`xatra.maps`](xatra/maps/) is otherwise a directory of useful and interesting example Maps. This is where I would like PRs, more than anywhere else.
  - [`xatra.matchers`](xatra/matchers/matchers.py) is a collection of `matcher` functions you can use in building your own Maps.

## TODO
- [ ] slider-based layer control for magic.py, or automatic video maker idk
- [ ] Make example maps and visualizations:
  - [x] "nations" -- classical nations of antiquity
  - [ ] north-west circa 322 BC (panini, alexandrian records, puranic etc.)
  - [ ] standard mainstream chronology, at least for some period
  - [ ] early south-east asian colonies
  - [ ] continents of the world, names of india
- [x] add Suvarnabhumi and Tibet-adjacent lands to matchers.py
- [x] make everything verbose
- [x] Loading all the stuff is really inefficient, fix that
- [ ] make legend options do something
- [ ] make flag name appear at center of geometry, bold upon highlighting any feature
- [ ] handling for cities