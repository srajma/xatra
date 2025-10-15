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

Example (explicit Map):
    >>> import xatra
    >>> map = xatra.Map()
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

import warnings
import sys
import os

# Check for data installation
from .data_installer import is_data_installed, get_xatra_dir

if not is_data_installed():
    xatra_dir = get_xatra_dir()
    warnings.warn(
        f"\n{'='*70}\n"
        f"XATRA DATA NOT FOUND\n"
        f"{'='*70}\n"
        f"Xatra requires data files to be installed at: {xatra_dir}\n\n"
        f"To install the data, run:\n"
        f"    xatra-install-data\n\n"
        f"This will download ~500MB-1GB of geographical data from Hugging Face.\n"
        f"The download may take several minutes depending on your connection.\n"
        f"{'='*70}\n",
        UserWarning,
        stacklevel=2
    )

from .flagmap import Map
from .territory import Territory
from .loaders import gadm, naturalearth, overpass
from .icon import Icon
from . import debug_utils
from .geometry_cache import clear_geometry_cache, get_geometry_cache_stats

# Import timing debugging functions
from .debug_utils import (
    reset_timing_stats,
    get_timing_stats, 
    print_timing_summary,
    plot_timing_chart,
    show_timing_chart,
    _auto_display_timing_stats
)

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


# Debugging flags - initialize from environment variable
def _parse_debug_time_env():
    """Parse DEBUG_TIME environment variable."""
    env_value = os.environ.get("DEBUG_TIME", "").lower()
    if env_value in ("1", "true", "yes", "on"):
        return True
    elif env_value in ("0", "false", "no", "off", ""):
        return False
    else:
        # Invalid value - warn and default to False
        warnings.warn(
            f"Invalid DEBUG_TIME environment variable value: '{os.environ.get('DEBUG_TIME')}'. "
            f"Expected one of: 1, 0, true, false, yes, no, on, off. Defaulting to False.",
            UserWarning,
            stacklevel=3
        )
        return False

DEBUG_TIME = _parse_debug_time_env()
debug_utils.DEBUG_TIME = DEBUG_TIME

# Register automatic display of timing stats if debug time is enabled via environment
if DEBUG_TIME:
    import atexit
    atexit.register(_auto_display_timing_stats)


def set_debug_time(enabled: bool):
    """Enable or disable time debugging throughout xatra.
    
    When enabled, all major operations will print timing information
    showing when activities start and finish with HH:MM:SS timestamps.
    Additionally, timing statistics and charts are automatically displayed
    when the program exits.
    
    This function overrides the DEBUG_TIME environment variable setting.
    
    Args:
        enabled: True to enable time debugging, False to disable
        
    Example:
        >>> import xatra
        >>> xatra.set_debug_time(True)  # Overrides environment variable
        >>> xatra.DEBUG_TIME = True     # Alternative way (also overrides env)
    """
    global DEBUG_TIME
    DEBUG_TIME = enabled
    debug_utils.DEBUG_TIME = enabled
    
    # Register automatic display of timing stats on program exit
    if enabled:
        import atexit
        atexit.register(_auto_display_timing_stats)


def clear_cache(memory_only: bool = False, disk_only: bool = False):
    """Clear the global geometry cache.
    
    This can improve memory usage or force fresh geometry calculations.
    
    Args:
        memory_only: If True, only clear in-memory cache
        disk_only: If True, only clear on-disk cache
        
    Example:
        >>> import xatra
        >>> xatra.clear_cache()  # Clear both memory and disk cache
        >>> xatra.clear_cache(memory_only=True)  # Clear only memory cache
        >>> xatra.clear_cache(disk_only=True)  # Clear only disk cache
    """
    clear_geometry_cache(memory_only=memory_only, disk_only=disk_only)


def cache_stats():
    """Get statistics for the global geometry cache.
    
    Returns:
        Dictionary with cache statistics including hit rates and sizes
        
    Example:
        >>> import xatra
        >>> stats = xatra.cache_stats()
        >>> print(f"Hit rate: {stats['hit_rate']:.2%}")
        >>> print(f"Memory cache size: {stats['memory_cache_size']} items")
        >>> print(f"Disk cache size: {stats['disk_cache_size']} files")
    """
    return get_geometry_cache_stats()

__version__ = "0.1.0"
__all__ = [
    # Core classes
    "Map",
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
    # Debug utilities
    "DEBUG_TIME",
    "set_debug_time",
    # Cache management
    "clear_cache",
    "cache_stats",
]
