"""
Matplotlib-style pyplot interface for Xatra.

This module provides convenience functions that operate on a global "current map",
similar to matplotlib.pyplot. Users can call xatra.Flag(), xatra.River(), etc. 
without explicitly creating a Map object.

Example:
    >>> import xatra
    >>> from xatra.loaders import gadm
    >>> 
    >>> xatra.Flag("Maurya", gadm("IND"))
    >>> xatra.River("Ganges", river_geometry)
    >>> xatra.show()
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional, Union

from .flagmap import Map
from .territory import Territory
from .colorseq import ColorSequence

# Global state for current map
_current_map: Optional[Map] = None


def get_current_map() -> Map:
    """
    Get the current Map instance, creating one if none exists.
    
    This function is similar to matplotlib's get current figure.
    If no map exists, a new Map is created and set as current.
    
    Returns:
        The current Map instance
    """
    global _current_map
    if _current_map is None:
        _current_map = Map()
    return _current_map


def set_current_map(map: Optional[Map]) -> None:
    """
    Set the current Map instance.
    
    Args:
        map: Map instance to set as current, or None to clear
    """
    global _current_map
    _current_map = map


def new_map() -> Map:
    """
    Create a new Map and set it as the current map.
    
    Returns:
        The newly created Map instance
    """
    global _current_map
    _current_map = Map()
    return _current_map


# Wrapper functions for all Map methods

def FlagColorSequence(color_sequence: ColorSequence, class_name: Optional[str] = None) -> None:
    """Set the color sequence for flags on the current map."""
    get_current_map().FlagColorSequence(color_sequence, class_name)


def AdminColorSequence(color_sequence: ColorSequence) -> None:
    """Set the color sequence for admin regions on the current map."""
    get_current_map().AdminColorSequence(color_sequence)


def DataColormap(colormap=None, vmin: Optional[float] = None, vmax: Optional[float] = None, norm=None) -> None:
    """Set the color map for data elements on the current map."""
    get_current_map().DataColormap(colormap, vmin, vmax, norm)


def Data(gadm: str, value: float, period: Optional[List[int]] = None, classes: Optional[str] = None, find_in_gadm: Optional[List[str]] = None) -> None:
    """Add a data point to the current map."""
    get_current_map().Data(gadm, value, period, classes, find_in_gadm)


def Dataframe(dataframe, data_column: Optional[str] = None, year_columns: Optional[List[str]] = None, classes: Optional[str] = None, find_in_gadm: Optional[List[str]] = None) -> None:
    """Add DataFrame-based choropleth data to the current map."""
    get_current_map().Dataframe(dataframe, data_column, year_columns, classes, find_in_gadm)


def Flag(label: str, value: Territory = None, period: Optional[List[int]] = None, note: Optional[str] = None, color: Optional[str] = None, classes: Optional[str] = None, type: Optional[str] = None, inherit: Optional[str] = None) -> None:
    """Add a flag (country/kingdom) to the current map.
    
    Args:
        label: Display name for the flag
        value: Territory object defining the geographical extent
        period: Optional time period as [start_year, end_year] list
        note: Optional tooltip text for the flag
        color: Optional color for the flag (overrides color sequence) in hex code
        classes: Optional CSS classes for styling and color sequence assignment
        type: Optional relationship type: "vassal", "province", or None
        inherit: Optional label of an earlier-defined flag to force color inheritance
    """
    get_current_map().Flag(label, value, period, note, color, classes, type, inherit)


def River(label: str, value: Dict[str, Any], note: Optional[str] = None, classes: Optional[str] = None, period: Optional[List[int]] = None, show_label: bool = False, n_labels: int = 1, hover_radius: int = 10) -> None:
    """Add a river to the current map."""
    get_current_map().River(label, value, note, classes, period, show_label, n_labels, hover_radius)


def Path(label: str, value: List[List[float]], note: Optional[str] = None, classes: Optional[str] = None, period: Optional[List[int]] = None, show_label: bool = False, n_labels: int = 1, hover_radius: int = 10) -> None:
    """Add a path/route to the current map."""
    get_current_map().Path(label, value, note, classes, period, show_label, n_labels, hover_radius)


def Point(label: str, position: List[float], note: Optional[str] = None, period: Optional[List[int]] = None, icon: Optional[Any] = None, show_label: bool = False, hover_radius: int = 20, classes: Optional[str] = None, rotation: Optional[float] = None) -> None:
    """Add a point of interest to the current map."""
    get_current_map().Point(label, position, note, period, icon, show_label, hover_radius, classes, rotation)


def Text(label: str, position: List[float], note: Optional[str] = None, classes: Optional[str] = None, period: Optional[List[int]] = None, rotation: Optional[float] = None) -> None:
    """Add a text label to the current map."""
    get_current_map().Text(label, position, note, classes, period, rotation)


def TitleBox(html: str, period: Optional[List[int]] = None) -> None:
    """Add a title box with HTML content to the current map."""
    get_current_map().TitleBox(html, period)


def Geocoder(provider: str = "nominatim", api_key: Optional[str] = None) -> None:
    """Configure the map geocoder (search for places worldwide) on the current map."""
    get_current_map().Geocoder(provider, api_key)


def CSS(css: str) -> None:
    """Add custom CSS styles to the current map."""
    get_current_map().CSS(css)


def BaseOption(url_or_provider: str, name: Optional[str] = None, default: bool = False) -> None:
    """Add a base map layer to the current map."""
    get_current_map().BaseOption(url_or_provider, name, default)


def Admin(gadm: str, level: int, period: Optional[List[int]] = None, classes: Optional[str] = None, color_by_level: int = 1, find_in_gadm: Optional[List[str]] = None) -> None:
    """Add administrative regions to the current map."""
    get_current_map().Admin(gadm, level, period, classes, color_by_level, find_in_gadm)


def AdminRivers(period: Optional[List[int]] = None, classes: Optional[str] = None, sources: Optional[List[str]] = None, show_label: bool = False, n_labels: int = 1) -> None:
    """Add rivers from specified data sources to the current map."""
    get_current_map().AdminRivers(period, classes, sources, show_label, n_labels)


def zoom(level: int) -> None:
    """Set the initial zoom level for the current map."""
    get_current_map().zoom(level)


def focus(latitude: float, longitude: float) -> None:
    """Set the initial map focus (center) for the current map."""
    get_current_map().focus(latitude, longitude)


def to_html_string() -> str:
    """Export the current map to an HTML string."""
    return get_current_map().to_html_string()


def slider(start: Optional[int] = None, end: Optional[int] = None, speed: float = 5.0) -> None:
    """Set time limits and play speed for the current map."""
    get_current_map().slider(start, end, speed)


def show(out_json: str = "map.json", out_html: str = "map.html") -> None:
    """Export the current map to JSON and HTML files."""
    get_current_map().show(out_json, out_html)
