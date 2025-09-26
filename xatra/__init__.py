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

Example:
    >>> import xatra
    >>> map = xatra.FlagMap()
    >>> map.Flag("Maurya", territory, period=[320, 180])
    >>> map.River("Ganges", river_geometry, classes="major-river")
    >>> map.show("map.html")
"""

from .flagmap import FlagMap
from .territory import Territory
from .loaders import gadm, naturalearth, overpass
from .territory_library import NORTHERN_INDIA

__version__ = "0.1.0"
__all__ = ["FlagMap", "Territory", "gadm", "naturalearth", "overpass", "NORTHERN_INDIA"]
