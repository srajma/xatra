"""
Xatra: The Matplotlib of Maps

Xatra is a Python library for creating interactive historical maps, similar to
how matplotlib provides plotting capabilities. It supports various map elements
including flags (countries/kingdoms), rivers, paths, points, text labels, and
title boxes with optional time-based filtering for dynamic maps.

Key Features:
- Interactive HTML maps using Leaflet.js
- Territory algebra for composable geographical regions
- Dynamic maps with time sliders using pax-max aggregation
- Support for multiple base map layers
- Customizable styling with CSS
- Data loaders for GADM, Natural Earth, and Overpass API

Example (explicit FlagMap):
    >>> import xatra
    >>> map = xatra.FlagMap()
    >>> map.Flag("Maurya", territory, period=[320, 180])
    >>> map.River("Ganges", river_geometry, classes="major-river")
    >>> map.show("map.html")

Example (pyplot-style):
    >>> import xatra
    >>> from xatra.loaders import gadm
    >>> xatra.Flag("Maurya", gadm("IND"))
    >>> xatra.River("Ganges", river_geometry)
    >>> xatra.show()
"""

from .flagmap import FlagMap
from .territory import Territory
from .loaders import gadm, naturalearth, overpass
from .icon import Icon

# Import pyplot-style functions
from .pyplot import (
    get_current_map,
    set_current_map,
    new_map,
    FlagColorSequence,
    AdminColorSequence,
    DataColormap,
    Data,
    Dataframe,
    Flag,
    River,
    Path,
    Point,
    Text,
    TitleBox,
    CSS,
    BaseOption,
    Admin,
    AdminRivers,
    slider,
    show,
)

__version__ = "0.1.0"
__all__ = [
    # Core classes
    "FlagMap",
    "Territory",
    "Icon",
    # Loaders
    "gadm",
    "naturalearth",
    "overpass",
    # Pyplot-style functions
    "get_current_map",
    "set_current_map",
    "new_map",
    "FlagColorSequence",
    "AdminColorSequence",
    "DataColormap",
    "Data",
    "Dataframe",
    "Flag",
    "River",
    "Path",
    "Point",
    "Text",
    "TitleBox",
    "CSS",
    "BaseOption",
    "Admin",
    "AdminRivers",
    "slider",
    "show",
]
