"""
Xatra Map Module

This module provides the core Map class for creating interactive historical maps.
It supports various map elements including flags (countries/kingdoms), rivers, paths, 
points, text labels, and title boxes with optional time-based filtering for dynamic maps.

The module uses the pax-max aggregation method to create stable periods for dynamic
maps, allowing smooth transitions between different historical states.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple, Union


from .territory import Territory
from .render import export_html
from .paxmax import paxmax_aggregate
from .colorseq import ColorSequence, LinearColorSequence
from .debug_utils import time_debug


GeometryLike = Union[Territory, Dict[str, Any]]


@dataclass
class FlagEntry:
    """Represents a flag (country/kingdom) with territory and optional time period.
    
    Args:
        label: Display name for the flag
        territory: Territory object defining the geographical extent
        period: Optional time period as (start_year, end_year) tuple
        note: Optional tooltip text for the flag
        color: Optional color for the flag (overrides color sequence)
        classes: Optional CSS classes for styling and color sequence assignment
    """
    label: str
    territory: Territory
    period: Optional[Tuple[int, int]] = None
    note: Optional[str] = None
    color: Optional[str] = None
    classes: Optional[str] = None


@dataclass
class RiverEntry:
    """Represents a river with GeoJSON geometry and optional styling.
    
    Args:
        label: Display name for the river
        geometry: GeoJSON geometry object
        note: Optional tooltip text for the river
        classes: Optional CSS classes for styling
        period: Optional time period as (start_year, end_year) tuple
        show_label: If True, display label next to the river instead of in tooltip
        n_labels: Number of labels to display along the river (default: 1)
        hover_radius: Hover detection radius in pixels (default: 10)
    """
    label: str
    geometry: Dict[str, Any]
    note: Optional[str] = None
    classes: Optional[str] = None
    period: Optional[Tuple[int, int]] = None
    show_label: bool = False
    n_labels: int = 1
    hover_radius: int = 10


@dataclass
class PathEntry:
    """Represents a path/route with coordinate list and optional styling.
    
    Args:
        label: Display name for the path
        coords: List of (latitude, longitude) coordinate tuples
        classes: Optional CSS classes for styling
        period: Optional time period as (start_year, end_year) tuple
        show_label: If True, display label next to the path instead of in tooltip
        n_labels: Number of labels to display along the path (default: 1)
        hover_radius: Hover detection radius in pixels (default: 10)
    """
    label: str
    coords: List[Tuple[float, float]]
    classes: Optional[str] = None
    period: Optional[Tuple[int, int]] = None
    show_label: bool = False
    n_labels: int = 1
    hover_radius: int = 10


@dataclass
class PointEntry:
    """Represents a point of interest with position and optional time period.
    
    Args:
        label: Display name for the point
        position: (latitude, longitude) coordinate tuple
        period: Optional time period as (start_year, end_year) tuple
        icon: Optional custom icon for the marker
        show_label: If True, display label next to the point instead of in tooltip
        hover_radius: Hover detection radius in pixels (default: 20)
    """
    label: str
    position: Tuple[float, float]
    period: Optional[Tuple[int, int]] = None
    icon: Optional[Any] = None  # Icon type imported later to avoid circular imports
    show_label: bool = False
    hover_radius: int = 20


@dataclass
class TextEntry:
    """Represents a text label with position and optional styling.
    
    Args:
        label: Text content to display
        position: (latitude, longitude) coordinate tuple
        classes: Optional CSS classes for styling
        period: Optional time period as (start_year, end_year) tuple
    """
    label: str
    position: Tuple[float, float]
    classes: Optional[str] = None
    period: Optional[Tuple[int, int]] = None


@dataclass
class TitleBoxEntry:
    """Represents a title box with HTML content and optional time period.
    
    Args:
        html: HTML content for the title box
        period: Optional time period as (start_year, end_year) tuple
    """
    html: str
    period: Optional[Tuple[int, int]] = None


@dataclass
class AdminEntry:
    """Represents administrative regions from GADM data.
    
    Args:
        gadm_key: GADM key (e.g., "IND.31" for Tamil Nadu)
        level: Administrative level to display (e.g., 3 for tehsils)
        period: Optional time period as (start_year, end_year) tuple
        classes: Optional CSS classes for styling
        color_by_level: Level to group colors by (e.g., 1 for states)
        find_in_gadm: Optional list of country codes to search in if gadm is not found in its own file
    """
    gadm_key: str
    level: int
    period: Optional[Tuple[int, int]] = None
    classes: Optional[str] = None
    color_by_level: int = 1
    find_in_gadm: Optional[List[str]] = None


@dataclass
class AdminRiversEntry:
    """Represents all rivers from data files.
    
    Args:
        period: Optional time period as (start_year, end_year) tuple
        classes: Optional CSS classes for styling
        sources: List of data sources to include (default: ["naturalearth", "overpass"])
        show_label: Whether to display labels on the rivers (default: False)
        n_labels: Number of labels to display along each river (default: 1)
    """
    period: Optional[Tuple[int, int]] = None
    classes: Optional[str] = None
    sources: List[str] = None
    show_label: bool = False
    n_labels: int = 1
    
    def __post_init__(self):
        if self.sources is None:
            self.sources = ["naturalearth", "overpass"]
        else:
            # Create a copy to avoid shared references
            self.sources = list(self.sources)


@dataclass
class BaseOptionEntry:
    """Represents a base map layer option.
    
    Args:
        url: Tile server URL or provider name
        name: Display name for the layer
        default: Whether this layer should be selected by default
    """
    url: str
    name: str
    default: bool = False


@dataclass
class DataEntry:
    """Represents a data element with GADM region and value for color mapping.
    
    Args:
        gadm: GADM key (e.g., "IND.31" for Tamil Nadu)
        value: Numeric value for color mapping
        period: Optional time period as (start_year, end_year) tuple
        classes: Optional CSS classes for styling
        find_in_gadm: Optional list of country codes to search in if gadm is not found in its own file
    """
    gadm: str
    value: float
    period: Optional[Tuple[int, int]] = None
    classes: Optional[str] = None
    find_in_gadm: Optional[List[str]] = None


@dataclass
class DataframeEntry:
    """Represents a DataFrame-based data visualization for choropleth mapping.
    
    Args:
        dataframe: pandas DataFrame with GID-indexed rows and year/data columns
        data_column: Column name containing the data values (if single column)
        year_columns: List of year columns for time-series data (if multiple columns)
        classes: Optional CSS classes for styling
        find_in_gadm: Optional list of country codes to search in if GID is not found in its own file
    """
    dataframe: Any  # pandas DataFrame
    data_column: Optional[str] = None
    year_columns: Optional[List[str]] = None
    classes: Optional[str] = None
    find_in_gadm: Optional[List[str]] = None


class DataColormap:
    """Handles color mapping for data elements using matplotlib Colormap objects.
    
    This class wraps matplotlib Colormap objects to provide color mapping functionality
    for data elements based on their numeric values. Supports both basic normalization
    and matplotlib Normalize objects for advanced scaling.
    
    Args:
        colormap: matplotlib Colormap object (e.g., plt.cm.viridis, plt.cm.Reds)
        vmin: Minimum value for normalization (default: None, auto-detect)
        vmax: Maximum value for normalization (default: None, auto-detect)
        norm: matplotlib Normalize object (e.g., LogNorm, PowerNorm). If provided,
              vmin and vmax are ignored and the norm object handles normalization.
    """
    
    def __init__(self, colormap, vmin: Optional[float] = None, vmax: Optional[float] = None, norm=None):
        self.colormap = colormap
        self.vmin = vmin
        self.vmax = vmax
        self.norm = norm
        self._values = []  # Store values for auto-detection of vmin/vmax
    
    def add_value(self, value: float) -> None:
        """Add a value to the dataset for auto-detection of vmin/vmax.
        
        Args:
            value: Numeric value to add to the dataset
        """
        self._values.append(value)
    
    def get_color(self, value: float) -> str:
        """Get color for a given value using the colormap.
        
        Args:
            value: Numeric value to map to color
            
        Returns:
            Hex color string (e.g., "#ff0000")
        """
        if self.norm is not None:
            # Use matplotlib Normalize object for normalization
            try:
                normalized = self.norm(value)
                # Clamp to [0, 1] range
                normalized = max(0.0, min(1.0, normalized))
            except (ValueError, TypeError):
                # Handle cases where normalization fails (e.g., log of negative values)
                normalized = 0.5
        else:
            # Use basic linear normalization
            vmin = self.vmin
            vmax = self.vmax
            
            if vmin is None or vmax is None:
                if self._values:
                    all_values = self._values
                else:
                    all_values = [value]
                
                if vmin is None:
                    vmin = min(all_values)
                if vmax is None:
                    vmax = max(all_values)
            
            # Normalize value to [0, 1] range
            if vmax == vmin:
                # If all values are the same, use the middle of the colormap
                normalized = 0.5
            else:
                normalized = (value - vmin) / (vmax - vmin)
                # Clamp to [0, 1] range
                normalized = max(0.0, min(1.0, normalized))
        
        # Get color from colormap
        color_rgba = self.colormap(normalized)
        
        # Convert to hex
        r, g, b = int(color_rgba[0] * 255), int(color_rgba[1] * 255), int(color_rgba[2] * 255)
        return f"#{r:02x}{g:02x}{b:02x}"


def generate_colormap_svg(colormap, vmin: float, vmax: float, width: int = 200, height: int = 20, norm=None) -> str:
    """Generate an SVG color bar for a colormap.
    
    Args:
        colormap: matplotlib Colormap object
        vmin: Minimum value for the color bar
        vmax: Maximum value for the color bar
        width: Width of the color bar in pixels
        height: Height of the color bar in pixels
        norm: matplotlib Normalize object (optional)
        
    Returns:
        SVG string for the color bar
    """
    import matplotlib.pyplot as plt
    import numpy as np
    import io
    
    # Create a figure with just the color bar
    fig, ax = plt.subplots(figsize=(width/100, height/100))
    fig.patch.set_facecolor('white')
    
    # Create a gradient
    gradient = np.linspace(0, 1, width)
    gradient = np.vstack((gradient, gradient))
    
    # Display the gradient with optional normalization
    if norm is not None:
        ax.imshow(gradient, aspect='auto', cmap=colormap, norm=norm, extent=[vmin, vmax, 0, 1])
    else:
        ax.imshow(gradient, aspect='auto', cmap=colormap, extent=[vmin, vmax, 0, 1])
    
    ax.set_xlim(vmin, vmax)
    ax.set_ylim(0, 1)
    ax.set_xlabel('')
    ax.set_ylabel('')
    ax.set_yticks([])
    ax.set_xticks([vmin, vmax])
    ax.set_xticklabels([str(vmin), str(vmax)])
    
    # Remove borders
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_visible(True)
    
    # Save to SVG string
    svg_buffer = io.StringIO()
    plt.savefig(svg_buffer, format='svg', bbox_inches='tight', pad_inches=0.1)
    plt.close(fig)
    
    svg_content = svg_buffer.getvalue()
    svg_buffer.close()
    
    return svg_content


class Map:
    """Main class for creating interactive historical maps.
    
    Map is the core class for creating maps similar to "matplotlib of maps".
    It supports various map elements including flags (countries/kingdoms), rivers,
    paths, points, text labels, and title boxes. Maps can be static or dynamic
    with time-based filtering using the pax-max aggregation method.
    
    Example:
        >>> map = Map()
        >>> map.Flag("Maurya", territory, period=[320, 180])
        >>> map.River("Ganges", river_geometry, classes="major-river")
        >>> map.export("map.html")
    """
    
    def __init__(self) -> None:
        """Initialize a new Map instance.
        
        Creates an empty map with default base layer options (OpenStreetMap,
        Esri.WorldImagery, OpenTopoMap, Esri.WorldPhysical).
        """
        self._flags: List[FlagEntry] = []
        self._rivers: List[RiverEntry] = []
        self._paths: List[PathEntry] = []
        self._points: List[PointEntry] = []
        self._texts: List[TextEntry] = []
        self._title_boxes: List[TitleBoxEntry] = []
        self._admins: List[AdminEntry] = []
        self._admin_rivers: List[AdminRiversEntry] = []
        self._data: List[DataEntry] = []
        self._dataframes: List[DataframeEntry] = []
        self._base_options: List[BaseOptionEntry] = []
        self._css: List[str] = []
        self._map_limits: Optional[Tuple[int, int]] = None
        self._play_speed: int = 200  # Default play speed in milliseconds (5 years/second)
        self._color_sequences: Dict[Optional[str], ColorSequence] = {None: LinearColorSequence()}
        self._flag_indexes: Dict[Optional[str], int] = {None: 0}
        self._label_colors: Dict[str, str] = {}  # Track colors by label
        self._admin_color_sequence: ColorSequence = LinearColorSequence()
        self._admin_index: int = 0
        self._admin_colors: Dict[str, str] = {}  # Track colors by admin grouping key
        self._data_colormap: Optional[DataColormap] = None
        
        # Add default base options
        self._add_default_base_options()

    # API methods
    def FlagColorSequence(self, color_sequence: ColorSequence, class_name: Optional[str] = None) -> None:
        """Set the color sequence for flags.
        
        Args:
            color_sequence: ColorSequence instance to use for flag colors
            class_name: Optional CSS class name to assign this color sequence to.
                       If None, assigns to the default color sequence for flags without classes.
            
        Example:
            >>> from xatra.colorseq import RotatingColorSequence
            >>> map.FlagColorSequence(RotatingColorSequence())  # Default sequence
            >>> map.FlagColorSequence(RotatingColorSequence(), "empire")  # For flags with class "empire"
        """
        self._color_sequences[class_name] = color_sequence
        self._flag_indexes[class_name] = 0  # reset index every time we set a new color sequence

    def AdminColorSequence(self, color_sequence: ColorSequence) -> None:
        """Set the color sequence for admin regions.
        
        Args:
            color_sequence: ColorSequence instance to use for admin region colors
            
        Example:
            >>> from xatra.colorseq import RotatingColorSequence
            >>> map.AdminColorSequence(RotatingColorSequence())
        """
        self._admin_color_sequence = color_sequence

    def DataColormap(self, colormap=None, vmin: Optional[float] = None, vmax: Optional[float] = None, norm=None) -> None:
        """Set the color map for data elements.
        
        Args:
            colormap: matplotlib Colormap object (e.g., plt.cm.viridis, plt.cm.Reds).
                     If None, uses default yellow-orange-red colormap.
            vmin: Minimum value for normalization (default: None, auto-detect)
            vmax: Maximum value for normalization (default: None, auto-detect)
            norm: matplotlib Normalize object (e.g., LogNorm, PowerNorm). If provided,
                  vmin and vmax are ignored and the norm object handles normalization.
            
        Example:
            >>> import matplotlib.pyplot as plt
            >>> from matplotlib.colors import LogNorm, PowerNorm
            >>> map.DataColormap()  # Uses default yellow-orange-red colormap
            >>> map.DataColormap(plt.cm.viridis)
            >>> map.DataColormap(plt.cm.Reds, vmin=0, vmax=100)
            >>> map.DataColormap(plt.cm.viridis, norm=LogNorm(vmin=1, vmax=1000))
            >>> map.DataColormap(plt.cm.plasma, norm=PowerNorm(gamma=0.5))
        """
        if colormap is None:
            from matplotlib.colors import LinearSegmentedColormap
            colormap = LinearSegmentedColormap.from_list("custom_cmap", ["yellow", "orange", "red"])
        elif isinstance(colormap, str):
            import matplotlib.pyplot as plt
            colormap = plt.get_cmap(colormap)
        self._data_colormap = DataColormap(colormap, vmin, vmax, norm)

    def Data(self, gadm: str, value: float, period: Optional[List[int]] = None, classes: Optional[str] = None, find_in_gadm: Optional[List[str]] = None) -> None:
        """Add a data element to the map.
        
        Data elements are colored based on their numeric values using the map's data colormap.
        If no colormap is set, a default yellow-orange-red colormap will be used.
        
        Args:
            gadm: GADM key (e.g., "IND.31" for Tamil Nadu)
            value: Numeric value for color mapping
            period: Optional time period as [start_year, end_year] list
            classes: Optional CSS classes for styling
            find_in_gadm: Optional list of country codes to search in if gadm is not found in its own file
            
        Example:
            >>> map.Data("IND.31", 85.5, period=[2020, 2025], classes="population-data")
            >>> map.Data("IND.11", 42.3, classes="gdp-data")
            >>> map.Data("Z01.14", 100, find_in_gadm=["IND"])  # Disputed territory from IND file
        """
        period_tuple: Optional[Tuple[int, int]] = None
        if period is not None:
            if len(period) != 2:
                raise ValueError("period must be [start, end]")
            period_tuple = (int(period[0]), int(period[1]))
        
        # Create default colormap if none exists
        if self._data_colormap is None:
            from matplotlib.colors import LinearSegmentedColormap
            self._data_colormap = DataColormap(LinearSegmentedColormap.from_list("custom_cmap", ["yellow", "orange", "red"]))
        
        # Add value to colormap for auto-detection of vmin/vmax
        self._data_colormap.add_value(value)
        
        self._data.append(DataEntry(gadm=gadm, value=value, period=period_tuple, classes=classes, find_in_gadm=find_in_gadm))

    @time_debug("Add Dataframe")
    def Dataframe(self, dataframe, data_column: Optional[str] = None, year_columns: Optional[List[str]] = None, classes: Optional[str] = None, find_in_gadm: Optional[List[str]] = None) -> None:
        """Add a DataFrame-based data visualization to the map.
        
        Creates a choropleth map from a pandas DataFrame where each row represents an administrative
        division indexed by GID, and columns represent either a single data value or time-series data.
        
        Args:
            dataframe: pandas DataFrame with GID-indexed rows and data columns
            data_column: Column name containing the data values (for static maps). If None, auto-detected.
            year_columns: List of year columns for time-series data (for dynamic maps). If None, auto-detected.
            classes: Optional CSS classes for styling
            find_in_gadm: Optional list of country codes to search in if GID is not found in its own file
            
        Auto-detection behavior:
            - If neither data_column nor year_columns is specified:
              - Single data column (besides GID): treated as data_column for static map
              - Multiple data columns (besides GID): treated as year_columns for dynamic map
            
        Example:
            >>> # Static map with single data column (auto-detected)
            >>> df = pd.DataFrame({'GID': ['IND.31', 'IND.12'], 'population': [100, 200]})
            >>> df.set_index('GID', inplace=True)
            >>> map.Dataframe(df)  # 'population' auto-detected as data_column
            
            >>> # Dynamic map with year columns (auto-detected)
            >>> df = pd.DataFrame({'GID': ['IND.31', 'IND.12'], '2020': [100, 200], '2021': [110, 210]})
            >>> df.set_index('GID', inplace=True)
            >>> map.Dataframe(df)  # ['2020', '2021'] auto-detected as year_columns
            
            >>> # Explicit specification (overrides auto-detection)
            >>> map.Dataframe(df, data_column='population')
            >>> map.Dataframe(df, year_columns=['2020', '2021'])
        """
        try:
            import pandas as pd
        except ImportError:
            raise ImportError("pandas is required for DataFrame functionality. Install it with: pip install pandas")
        
        # Validate input
        if not isinstance(dataframe, pd.DataFrame):
            raise ValueError("dataframe must be a pandas DataFrame")
        
        # Auto-detect data_column or year_columns if not specified
        if data_column is None and year_columns is None:
            # Ensure GID is the index for analysis
            temp_df = dataframe.copy()
            if temp_df.index.name != 'GID' and 'GID' in temp_df.columns:
                temp_df = temp_df.set_index('GID')
            
            # Get non-GID columns
            # Exclude note columns from detection
            import re
            def is_note_column(c: str) -> bool:
                return c == 'note' or bool(re.match(r"^\d{1,4}_note$", str(c)))
            data_columns = [col for col in temp_df.columns if col != 'GID' and not is_note_column(str(col))]
            
            if len(data_columns) == 1:
                # Single column - assume it's data_column
                data_column = data_columns[0]
            elif len(data_columns) > 1:
                # Multiple columns - assume they're year_columns
                year_columns = data_columns
            else:
                raise ValueError("DataFrame must have at least one data column besides GID")
        
        if data_column is not None and year_columns is not None:
            raise ValueError("Cannot specify both data_column and year_columns")
        
        # Validate DataFrame structure
        if dataframe.index.name is None and 'GID' not in dataframe.columns:
            raise ValueError("DataFrame must have GID as index or as a column")
        
        # Ensure GID is the index
        if dataframe.index.name != 'GID' and 'GID' in dataframe.columns:
            dataframe = dataframe.set_index('GID')
        
        if data_column is not None:
            if data_column not in dataframe.columns:
                raise ValueError(f"Column '{data_column}' not found in DataFrame")
        else:
            # Validate year columns
            missing_cols = [col for col in year_columns if col not in dataframe.columns]
            if missing_cols:
                raise ValueError(f"Year columns not found in DataFrame: {missing_cols}")
        
        # Create default colormap if none exists
        if self._data_colormap is None:
            from matplotlib.colors import LinearSegmentedColormap
            self._data_colormap = DataColormap(LinearSegmentedColormap.from_list("custom_cmap", ["yellow", "orange", "red"]))
        
        # Add all values to colormap for auto-detection of vmin/vmax
        if data_column is not None:
            values = dataframe[data_column].dropna()
        else:
            # Only include specified year_columns, which exclude note columns
            values = dataframe[year_columns].values.flatten()
            values = pd.Series(values).dropna()
        
        for value in values:
            self._data_colormap.add_value(value)
        
        self._dataframes.append(DataframeEntry(
            dataframe=dataframe,
            data_column=data_column,
            year_columns=year_columns,
            classes=classes,
            find_in_gadm=find_in_gadm
        ))

    @time_debug("Add Flag")
    def Flag(self, label: str, value: Territory, period: Optional[List[int]] = None, note: Optional[str] = None, color: Optional[str] = None, classes: Optional[str] = None) -> None:
        """Add a flag (country/kingdom) to the map.
        
        Flags automatically get colors from the map's color sequence. Flags with the same label
        will always use the same color. You can override this behavior by providing a custom color.
        Flags can be assigned to CSS classes for different color sequences.
        
        Args:
            label: Display name for the flag
            value: Territory object defining the geographical extent
            period: Optional time period as [start_year, end_year] list
            note: Optional tooltip text for the flag
            color: Optional color for the flag (overrides color sequence) in hex code
            classes: Optional CSS classes for styling and color sequence assignment
            
        Example:
            >>> map.Flag("Maurya", maurya_territory, period=[320, 180], note="Ancient Indian empire")
            >>> map.Flag("Maurya", other_territory)  # Reuses the same color as above
            >>> map.Flag("Custom", territory, color="#ff0000")  # Custom red color
            >>> map.Flag("Empire", territory, classes="empire")  # Uses empire color sequence
        """
        period_tuple: Optional[Tuple[int, int]] = None
        if period is not None:
            if len(period) != 2:
                raise ValueError("period must be [start, end]")
            period_tuple = (int(period[0]), int(period[1]))
        
        # Handle color assignment
        if color is not None:
            # Custom color provided - store it for this label
            self._label_colors[label] = color
        else:
            # Check if we already have a color for this label
            if label in self._label_colors:
                # Reuse existing color for this label
                color = self._label_colors[label]
            else:
                # Determine which color sequence to use based on classes
                color_sequence_class = None
                if classes:
                    # Extract first class that has a color sequence assigned
                    class_list = classes.split()
                    for cls in class_list:
                        if cls in self._color_sequences:
                            color_sequence_class = cls
                            break
                
                # Use the determined class (or None for default)
                assigned_color = self._color_sequences[color_sequence_class][self._flag_indexes[color_sequence_class]]
                color = assigned_color.hex
                self._label_colors[label] = color
                self._flag_indexes[color_sequence_class] += 1
        
        self._flags.append(FlagEntry(label=label, territory=value, period=period_tuple, note=note, color=color, classes=classes))

    @time_debug("Add River")
    def River(self, label: str, value: Dict[str, Any], note: Optional[str] = None, classes: Optional[str] = None, period: Optional[List[int]] = None, show_label: bool = False, n_labels: int = 1, hover_radius: int = 10) -> None:
        """Add a river to the map.
        
        Args:
            label: Display name for the river
            value: GeoJSON geometry object
            note: Optional tooltip text for the river
            classes: Optional CSS classes for styling
            period: Optional time period as [start_year, end_year] list
            show_label: If True, display label next to the river instead of in tooltip
            n_labels: Number of labels to display along the river (default: 1)
            hover_radius: Hover detection radius in pixels (default: 10)
            
        Example:
            >>> map.River("Ganges", ganges_geometry, classes="major-river", note="Sacred river")
            >>> map.River("Yamuna", yamuna_geometry, show_label=True)
            >>> map.River("Nile", nile_geometry, show_label=True, n_labels=3, hover_radius=20)
        """
        period_tuple: Optional[Tuple[int, int]] = None
        if period is not None:
            if len(period) != 2:
                raise ValueError("period must be [start, end]")
            period_tuple = (int(period[0]), int(period[1]))
        self._rivers.append(RiverEntry(label=label, geometry=value, note=note, classes=classes, period=period_tuple, show_label=show_label, n_labels=n_labels, hover_radius=hover_radius))

    @time_debug("Add Path")
    def Path(self, label: str, value: List[List[float]], classes: Optional[str] = None, period: Optional[List[int]] = None, show_label: bool = False, n_labels: int = 1, hover_radius: int = 10) -> None:
        """Add a path/route to the map.
        
        Args:
            label: Display name for the path
            value: List of [latitude, longitude] coordinate pairs
            classes: Optional CSS classes for styling
            period: Optional time period as [start_year, end_year] list
            show_label: If True, display label next to the path instead of in tooltip
            n_labels: Number of labels to display along the path (default: 1)
            hover_radius: Hover detection radius in pixels (default: 10)
            
        Example:
            >>> map.Path("Silk Road", [[40.0, 74.0], [35.0, 103.0]], classes="trade-route")
            >>> map.Path("Trade Route", [[40.0, 74.0], [35.0, 103.0]], show_label=True)
            >>> map.Path("Long Route", [[40.0, 74.0], [35.0, 103.0]], show_label=True, n_labels=3, hover_radius=15)
        """
        coords = [(float(lat), float(lon)) for lat, lon in value]
        period_tuple: Optional[Tuple[int, int]] = None
        if period is not None:
            if len(period) != 2:
                raise ValueError("period must be [start, end]")
            period_tuple = (int(period[0]), int(period[1]))
        self._paths.append(PathEntry(label=label, coords=coords, classes=classes, period=period_tuple, show_label=show_label, n_labels=n_labels, hover_radius=hover_radius))

    @time_debug("Add Point")
    def Point(self, label: str, position: List[float], period: Optional[List[int]] = None, icon: Optional[Any] = None, show_label: bool = False, hover_radius: int = 20) -> None:
        """Add a point of interest to the map.
        
        Args:
            label: Display name for the point
            position: [latitude, longitude] coordinate pair
            period: Optional time period as [start_year, end_year] list
            icon: Optional Icon instance for custom marker appearance
            show_label: If True, display label next to the point instead of in tooltip
            hover_radius: Hover detection radius in pixels (default: 20)
            
        Example:
            >>> map.Point("Delhi", [28.6139, 77.2090], period=[1200, 1800])
            >>> 
            >>> # With custom icon
            >>> from xatra.icon import Icon
            >>> icon = Icon.builtin("star.png", icon_size=(32, 32))
            >>> map.Point("Capital", [28.6, 77.2], icon=icon)
            >>> 
            >>> # With label displayed next to the point
            >>> map.Point("Delhi", [28.6139, 77.2090], show_label=True, hover_radius=30)
        """
        period_tuple: Optional[Tuple[int, int]] = None
        if period is not None:
            if len(period) != 2:
                raise ValueError("period must be [start, end]")
            period_tuple = (int(period[0]), int(period[1]))
        self._points.append(PointEntry(label=label, position=(float(position[0]), float(position[1])), period=period_tuple, icon=icon, show_label=show_label, hover_radius=hover_radius))

    @time_debug("Add Text")
    def Text(self, label: str, position: List[float], classes: Optional[str] = None, period: Optional[List[int]] = None) -> None:
        """Add a text label to the map.
        
        Args:
            label: Text content to display
            position: [latitude, longitude] coordinate pair
            classes: Optional CSS classes for styling
            period: Optional time period as [start_year, end_year] list
            
        Example:
            >>> map.Text("Ancient City", [28.6139, 77.2090], classes="city-label")
        """
        period_tuple: Optional[Tuple[int, int]] = None
        if period is not None:
            if len(period) != 2:
                raise ValueError("period must be [start, end]")
            period_tuple = (int(period[0]), int(period[1]))
        self._texts.append(TextEntry(label=label, position=(float(position[0]), float(position[1])), classes=classes, period=period_tuple))

    @time_debug("Add TitleBox")
    def TitleBox(self, html: str, period: Optional[List[int]] = None) -> None:
        """Add a title box with HTML content to the map.
        
        Args:
            html: HTML content for the title box
            period: Optional time period as [start_year, end_year] list
            
        Example:
            >>> map.TitleBox("<h1>Ancient India</h1><p>Map of historical kingdoms</p>")
        """
        period_tuple: Optional[Tuple[int, int]] = None
        if period is not None:
            if len(period) != 2:
                raise ValueError("period must be [start, end]")
            period_tuple = (int(period[0]), int(period[1]))
        self._title_boxes.append(TitleBoxEntry(html=html, period=period_tuple))

    def CSS(self, css: str) -> None:
        """Add custom CSS styles to the map.
        
        Args:
            css: CSS string to add to the map's stylesheet
            
        Example:
            >>> map.CSS(".major-river { stroke: #0066cc; stroke-width: 3px; }")
        """
        self._css.append(css)

    def slider(self, start: Optional[int] = None, end: Optional[int] = None, speed: float = 5.0) -> None:
        """Set the time limits and play speed for the map.
        
        This restricts all object periods to be within the specified range.
        Object periods are considered clopen intervals [x, y), so we add a small
        epsilon to ensure proper behavior at the boundaries.
        
        Args:
            start: Start year (inclusive). If None, uses earliest period start.
            end: End year (exclusive). If None, uses latest period end.
            speed: Play speed in years per second (default: 5.0 years/second)
        """
        if start is not None and end is not None:
            self._map_limits = (int(start), int(end))
        # Convert years per second to milliseconds per year
        self._play_speed = int(1000 / float(speed))

    def BaseOption(self, url_or_provider: str, name: Optional[str] = None, default: bool = False) -> None:
        """Add a base layer option.
        
        Args:
            url_or_provider: Either a full tile URL template or a provider name from leaflet-providers
            name: Display name for the layer (defaults to provider name or derived from URL)
            default: Whether this should be the default layer
        """
        
        if url_or_provider in self.PROVIDER_URLS:
            url = self.PROVIDER_URLS[url_or_provider]
            display_name = name or url_or_provider
        else:
            url = url_or_provider
            display_name = name or self._derive_name_from_url(url)
        
        # Check if this layer already exists and update it
        for i, existing in enumerate(self._base_options):
            if existing.url == url:
                self._base_options[i] = BaseOptionEntry(url=url, name=display_name, default=default)
                return
        
        # Add new layer
        self._base_options.append(BaseOptionEntry(url=url, name=display_name, default=default))

    def _derive_name_from_url(self, url: str) -> str:
        """Derive a display name from URL.
        
        Args:
            url: Tile server URL
            
        Returns:
            Human-readable name for the layer
        """
        if "openstreetmap" in url:
            return "OpenStreetMap"
        elif "opentopomap" in url:
            return "OpenTopoMap"
        elif "arcgisonline" in url:
            if "World_Imagery" in url:
                return "Esri World Imagery"
            elif "World_Physical" in url:
                return "Esri World Physical"
            elif "Ocean" in url:
                return "Esri Ocean"
        elif "cartocdn" in url:
            return "CartoDB"
        elif "nationalmap" in url:
            return "USGS"
        return "Custom Layer"

    def _add_default_base_options(self) -> None:
        """Add default base layer options.
        
        Currently disabled to allow users to override defaults.
        """
        # self.BaseOption("OpenStreetMap", default=True)
        # self.BaseOption("Esri.WorldImagery")
        # self.BaseOption("OpenTopoMap")
        # self.BaseOption("Esri.WorldPhysical")
        # let's not do this, because it makes it impossible to override the default
        pass

    @time_debug("Add Admin regions")
    def Admin(self, gadm: str, level: int, period: Optional[List[int]] = None, classes: Optional[str] = None, color_by_level: int = 1, find_in_gadm: Optional[List[str]] = None) -> None:
        """Add administrative regions from GADM data.
        
        Args:
            gadm: GADM key (e.g., "IND.31" for Tamil Nadu)
            level: Administrative level to display (e.g., 3 for tehsils)
            period: Optional time period as [start_year, end_year] list
            classes: Optional CSS classes for styling
            color_by_level: Level to group colors by (e.g., 1 for states, 2 for districts)
            find_in_gadm: Optional list of country codes to search in if gadm is not found in its own file
            
        Example:
            >>> map.Admin(gadm="IND.31", level=3)  # Show all tehsils in Tamil Nadu, colored by state
            >>> map.Admin(gadm="IND", level=3, color_by_level=2)  # Show all tehsils in India, colored by district
            >>> map.Admin(gadm="Z01.14", level=0, find_in_gadm=["IND"])  # Show disputed territory from IND file
        """
        period_tuple: Optional[Tuple[int, int]] = None
        if period is not None:
            if len(period) != 2:
                raise ValueError("period must be [start, end]")
            period_tuple = (int(period[0]), int(period[1]))
        
        self._admins.append(AdminEntry(gadm_key=gadm, level=level, period=period_tuple, classes=classes, color_by_level=color_by_level, find_in_gadm=find_in_gadm))

    @time_debug("Add AdminRivers")
    def AdminRivers(self, period: Optional[List[int]] = None, classes: Optional[str] = None, sources: Optional[List[str]] = None, show_label: bool = False, n_labels: int = 1) -> None:
        """Add rivers from specified data sources.
        
        Args:
            period: Optional time period as [start_year, end_year] list
            classes: Optional CSS classes for styling
            sources: List of data sources to include (default: ["naturalearth", "overpass"])
            show_label: Whether to display labels on the rivers (default: False)
            n_labels: Number of labels to display along each river (default: 1)
            
        Example:
            >>> map.AdminRivers()  # Show all rivers from Natural Earth and Overpass data
            >>> map.AdminRivers(sources=["naturalearth"])  # Only Natural Earth rivers
            >>> map.AdminRivers(sources=["overpass"])  # Only Overpass rivers
            >>> map.AdminRivers(classes="all-rivers")  # With custom styling
            >>> map.AdminRivers(show_label=True, n_labels=3)  # With labels on rivers
        """
        period_tuple: Optional[Tuple[int, int]] = None
        if period is not None:
            if len(period) != 2:
                raise ValueError("period must be [start, end]")
            period_tuple = (int(period[0]), int(period[1]))
        
        # Validate sources
        if sources is not None:
            valid_sources = ["naturalearth", "overpass"]
            for source in sources:
                if source not in valid_sources:
                    raise ValueError(f"Invalid source '{source}'. Must be one of: {valid_sources}")
        
        self._admin_rivers.append(AdminRiversEntry(period=period_tuple, classes=classes, sources=sources, show_label=show_label, n_labels=n_labels))

    def _apply_limits_to_period(self, period: Optional[Tuple[int, int]]) -> Optional[Tuple[int, int]]:
        """Apply map limits to a period with epsilon adjustment.
        
        Object periods are clopen intervals [x, y), so we add epsilon to ensure
        proper behavior at boundaries. If the resulting period becomes null
        (start >= end), return None.
        
        Args:
            period: Original period tuple (start, end) or None
            
        Returns:
            Restricted period tuple or None if period becomes null
        """
        if period is None:
            return None  # Objects with no period are always visible (handled separately)
        if self._map_limits is None:
            return period
            
        start, end = period
        map_start, map_end = self._map_limits
        epsilon = 1  # Small epsilon for clopen interval handling
        
        # Apply limits with epsilon
        restricted_start = max(start, map_start - epsilon)
        restricted_end = min(end, map_end + epsilon)
        
        # Return None if period becomes null set
        if restricted_start >= restricted_end:
            return None
            
        return (restricted_start, restricted_end)

    def _serialize_colormap_info(self, all_dataframe_values: List[float]) -> Dict[str, Any]:
        """Serialize colormap information for frontend rendering.
        
        Args:
            all_dataframe_values: List of all DataFrame values for auto-detection
            
        Returns:
            Dictionary with colormap information for frontend
        """
        if self._data_colormap is None:
            return None
        
        # Determine vmin and vmax
        vmin = self._data_colormap.vmin
        vmax = self._data_colormap.vmax
        
        if vmin is None or vmax is None:
            if all_dataframe_values:
                vmin = vmin if vmin is not None else min(all_dataframe_values)
                vmax = vmax if vmax is not None else max(all_dataframe_values)
            else:
                vmin = 0.0
                vmax = 1.0
        
        # Generate color samples for the frontend
        # For Normalize objects, we need to sample the actual normalized values
        if self._data_colormap.norm is not None:
            # Sample values across the range and normalize them
            sample_values = [vmin + (vmax - vmin) * i / 255.0 for i in range(256)]
            try:
                # Create a new norm object with the correct bounds
                norm_type = type(self._data_colormap.norm)
                if norm_type.__name__ == 'LogNorm':
                    from matplotlib.colors import LogNorm
                    working_norm = LogNorm(vmin=vmin, vmax=vmax)
                elif norm_type.__name__ == 'PowerNorm':
                    from matplotlib.colors import PowerNorm
                    # Copy gamma parameter if available
                    gamma = getattr(self._data_colormap.norm, 'gamma', 1.0)
                    working_norm = PowerNorm(gamma=gamma, vmin=vmin, vmax=vmax)
                else:
                    # For other norm types, try to create with vmin/vmax
                    working_norm = norm_type(vmin=vmin, vmax=vmax)
                
                normalized_values = [working_norm(v) for v in sample_values]
                # Clamp to [0, 1] range
                normalized_values = [max(0.0, min(1.0, n)) for n in normalized_values]
            except (ValueError, TypeError) as e:
                print(f"Warning: Normalization failed: {e}, falling back to linear")
                # Fallback to linear normalization if norm fails
                normalized_values = [i / 255.0 for i in range(256)]
        else:
            # Linear normalization
            normalized_values = [i / 255.0 for i in range(256)]
        
        # Generate colors using the colormap
        colors = []
        sample_values_for_frontend = []
        for i, norm_val in enumerate(normalized_values):
            color_rgba = self._data_colormap.colormap(norm_val)
            colors.append([float(x) for x in color_rgba[:3]])  # RGB only
            sample_values_for_frontend.append(vmin + (vmax - vmin) * i / 255.0)
        
        return {
            "vmin": float(vmin),
            "vmax": float(vmax),
            "colors": colors,
            "has_norm": self._data_colormap.norm is not None,
            "norm_type": type(self._data_colormap.norm).__name__ if self._data_colormap.norm is not None else None,
            "sample_values": sample_values_for_frontend if self._data_colormap.norm is not None else None
        }

    def _feature_matches_gid(self, feature: Dict[str, Any], gid: str) -> bool:
        """Check if a GADM feature matches a given GID.
        
        Args:
            feature: GeoJSON feature with GADM properties
            gid: GID string to match (e.g., "IND.31", "Z01.14")
            
        Returns:
            True if feature matches the GID
        """
        props = feature.get("properties", {}) or {}
        
        # Handle disputed territories (Z prefix)
        if gid.startswith("Z"):
            # For disputed territories, use the same prefix matching logic as load_gadm_like
            parts = gid.split('.')
            level = 0 if len(parts) == 1 else len(parts) - 1
            
            if level == 0:
                # Country level - check GID_0
                feature_gid = props.get("GID_0", "")
                return str(feature_gid) == gid
            else:
                # Subdivision level - check appropriate GID field
                gid_key = f"GID_{level}"
                feature_gid = props.get(gid_key, "")
                
                # Use exact prefix matching with boundary check (same as load_gadm_like)
                return (str(feature_gid).startswith(gid) and 
                       (len(str(feature_gid)) == len(gid) or str(feature_gid)[len(gid)] in ['.', '_']))
        
        # Handle regular GADM codes
        parts = gid.split('.')
        level = len(parts) - 1
        
        if level == 0:
            # Country level - check GID_0
            return props.get("GID_0") == gid
        else:
            # Subdivision level - check appropriate GID field
            gid_key = f"GID_{level}"
            feature_gid = props.get(gid_key, "")
            
            # Use exact prefix matching with boundary check
            return (str(feature_gid).startswith(gid) and 
                   (len(str(feature_gid)) == len(gid) or str(feature_gid)[len(gid)] in ['.', '_']))


    @time_debug("Export to JSON")
    def _export_json(self) -> Dict[str, Any]:
        """Export map data to JSON format for rendering.
        
        Applies time limits, performs pax-max aggregation on flags, and serializes
        all map elements to a dictionary suitable for HTML rendering.
        
        Returns:
            Dictionary containing all map data including flags, rivers, paths, etc.
        """
        # Prepare flags for paxmax aggregation (keep territories for efficient union)
        flags_serialized: List[Dict[str, Any]] = []
        for fl in self._flags:
            restricted_period = self._apply_limits_to_period(fl.period)
            # Include objects with no period (always visible) or valid restricted periods
            if fl.period is None or restricted_period is not None:
                flags_serialized.append({
                    "label": fl.label,
                    "territory": fl.territory,  # Pass territory object for efficient union
                    "period": list(restricted_period) if restricted_period is not None else None,
                    "note": fl.note,
                    "color": fl.color,
                    "classes": fl.classes,
                })

        # Find the earliest start year from all object types
        earliest_start = None
        for f in flags_serialized:
            if f.get("period") is not None:
                if earliest_start is None or f["period"][0] < earliest_start:
                    earliest_start = f["period"][0]
        
        for r in self._rivers:
            if r.period is not None:
                if earliest_start is None or r.period[0] < earliest_start:
                    earliest_start = r.period[0]
                    
        for p in self._paths:
            if p.period is not None:
                if earliest_start is None or p.period[0] < earliest_start:
                    earliest_start = p.period[0]
                    
        for p in self._points:
            if p.period is not None:
                if earliest_start is None or p.period[0] < earliest_start:
                    earliest_start = p.period[0]
                    
        for t in self._texts:
            if t.period is not None:
                if earliest_start is None or t.period[0] < earliest_start:
                    earliest_start = t.period[0]
                    
        for tb in self._title_boxes:
            if tb.period is not None:
                if earliest_start is None or tb.period[0] < earliest_start:
                    earliest_start = tb.period[0]
                    
        for a in self._admins:
            if a.period is not None:
                if earliest_start is None or a.period[0] < earliest_start:
                    earliest_start = a.period[0]
                    
        for ar in self._admin_rivers:
            if ar.period is not None:
                if earliest_start is None or ar.period[0] < earliest_start:
                    earliest_start = ar.period[0]
                    
        for d in self._data:
            if d.period is not None:
                if earliest_start is None or d.period[0] < earliest_start:
                    earliest_start = d.period[0]

        # Check if any object type has periods to determine if map is dynamic
        has_periods = (
            any(f.get("period") is not None for f in flags_serialized) or
            any(r.period is not None for r in self._rivers) or
            any(p.period is not None for p in self._paths) or
            any(p.period is not None for p in self._points) or
            any(t.period is not None for t in self._texts) or
            any(tb.period is not None for tb in self._title_boxes) or
            any(a.period is not None for a in self._admins) or
            any(ar.period is not None for ar in self._admin_rivers) or
            any(d.period is not None for d in self._data) or
            any(df.year_columns is not None for df in self._dataframes)
        )

        # Pax-max aggregation
        pax = paxmax_aggregate(flags_serialized, earliest_start)
        
        # Override mode if any non-flag objects have periods
        if has_periods and pax.get("mode") == "static":
            # Convert static flags to dynamic format
            pax = {
                "mode": "dynamic",
                "breakpoints": [earliest_start] if earliest_start is not None else [],
                "snapshots": [{"year": earliest_start, "flags": pax.get("flags", [])}] if earliest_start is not None else []
            }

        rivers_serialized = []
        for r in self._rivers:
            restricted_period = self._apply_limits_to_period(r.period)
            # Include objects with no period (always visible) or valid restricted periods
            if r.period is None or restricted_period is not None:
                rivers_serialized.append({
                    "label": r.label,
                    "geometry": r.geometry,
                    "note": r.note,
                    "classes": r.classes,
                    "period": list(restricted_period) if restricted_period is not None else None,
                    "show_label": r.show_label,
                    "n_labels": r.n_labels,
                    "hover_radius": r.hover_radius,
                })

        paths_serialized = []
        for p in self._paths:
            restricted_period = self._apply_limits_to_period(p.period)
            # Include objects with no period (always visible) or valid restricted periods
            if p.period is None or restricted_period is not None:
                paths_serialized.append({
                    "label": p.label,
                    "coords": p.coords,
                    "classes": p.classes,
                    "period": list(restricted_period) if restricted_period is not None else None,
                    "show_label": p.show_label,
                    "n_labels": p.n_labels,
                    "hover_radius": p.hover_radius,
                })

        points_serialized = []
        for p in self._points:
            restricted_period = self._apply_limits_to_period(p.period)
            # Include objects with no period (always visible) or valid restricted periods
            if p.period is None or restricted_period is not None:
                point_data = {
                    "label": p.label,
                    "position": p.position,
                    "period": list(restricted_period) if restricted_period is not None else None,
                    "show_label": p.show_label,
                    "hover_radius": p.hover_radius,
                }
                # Add icon data if present
                if p.icon is not None:
                    point_data["icon"] = p.icon.to_dict()
                points_serialized.append(point_data)

        texts_serialized = []
        for t in self._texts:
            restricted_period = self._apply_limits_to_period(t.period)
            # Include objects with no period (always visible) or valid restricted periods
            if t.period is None or restricted_period is not None:
                texts_serialized.append({
                    "label": t.label,
                    "position": t.position,
                    "classes": t.classes,
                    "period": list(restricted_period) if restricted_period is not None else None,
                })

        base_options_serialized = [{
            "url": b.url,
            "name": b.name,
            "default": b.default,
        } for b in self._base_options]

        title_boxes_serialized = []
        for ft in self._title_boxes:
            restricted_period = self._apply_limits_to_period(ft.period)
            # Include objects with no period (always visible) or valid restricted periods
            if ft.period is None or restricted_period is not None:
                title_boxes_serialized.append({
                    "html": ft.html,
                    "period": list(restricted_period) if restricted_period is not None else None,
                })

        # Serialize admin regions
        admins_serialized = []
        for a in self._admins:
            restricted_period = self._apply_limits_to_period(a.period)
            # Include objects with no period (always visible) or valid restricted periods
            if a.period is None or restricted_period is not None:
                try:
                    from .loaders import _read_json, _compute_find_in_gadm_default, GADM_DIR
                    import os
                    
                    # Load the appropriate level file directly
                    parts = a.gadm_key.split('.')
                    iso3 = parts[0]
                    gadm_dir = GADM_DIR
                    level_file_path = os.path.join(gadm_dir, f"gadm41_{iso3}_{a.level}.json")
                    
                    # Try to load the level file, with fallback to find_in_gadm (explicit or computed) if needed
                    level_file = None
                    if os.path.exists(level_file_path):
                        level_file = _read_json(level_file_path)
                    else:
                        # Determine candidate countries: explicit list or computed from disputed mapping
                        candidate_countries = a.find_in_gadm or _compute_find_in_gadm_default(a.gadm_key)
                        if candidate_countries:
                            for country_code in candidate_countries:
                                search_path = os.path.join(gadm_dir, f"gadm41_{country_code}_{a.level}.json")
                                if os.path.exists(search_path):
                                    level_file = _read_json(search_path)
                                    break
                    
                    if not level_file:
                        print(f"Warning: GADM file not found for level {a.level}: {level_file_path}")
                        if a.find_in_gadm:
                            print(f"Also tried find_in_gadm countries: {a.find_in_gadm}")
                        continue
                    
                    # Filter features that match the gadm_key prefix
                    filtered_features = []
                    for feature in level_file.get("features", []):
                        props = feature.get("properties", {}) or {}
                        gid_key = f"GID_{a.level}"
                        gid = str(props.get(gid_key, ""))
                        
                        # For level 0, include all features from the country file (including disputed territories)
                        # For higher levels, include all features from the country file if gadm_key is just the country code
                        # Otherwise use exact prefix matching with boundary check
                        if a.level == 0 or (a.level > 0 and len(a.gadm_key.split('.')) == 1):
                            # Include all features from the country file (including disputed territories)
                            filtered_features.append(feature)
                        else:
                            # Use exact prefix matching with boundary check for specific regions
                            if gid.startswith(a.gadm_key) and (len(gid) == len(a.gadm_key) or gid[len(a.gadm_key)] in ['.', '_']):
                                filtered_features.append(feature)
                    
                    # Assign colors based on color_by_level (clamped to level)
                    effective_color_by_level = min(a.color_by_level, a.level)
                    color_groups = {}  # Maps grouping key to color
                    for feature in filtered_features:
                        props = feature.get("properties", {}) or {}
                        grouping_key = str(props.get(f"GID_{effective_color_by_level}", ""))
                        
                        if grouping_key and grouping_key not in color_groups:
                            # Assign new color to this group
                            if grouping_key in self._admin_colors:
                                color_groups[grouping_key] = self._admin_colors[grouping_key]
                            else:
                                assigned_color = self._admin_color_sequence[self._admin_index]
                                color = assigned_color.hex
                                self._admin_colors[grouping_key] = color
                                color_groups[grouping_key] = color
                                self._admin_index += 1
                        
                        # Add color to feature properties
                        if grouping_key in color_groups:
                            feature["properties"]["_color"] = color_groups[grouping_key]
                    
                    # Create a FeatureCollection with filtered features
                    admin_geojson = {
                        "type": "FeatureCollection",
                        "features": filtered_features
                    }
                    
                    admins_serialized.append({
                        "gadm_key": a.gadm_key,
                        "level": a.level,
                        "geometry": admin_geojson,
                        "classes": a.classes,
                        "period": list(restricted_period) if restricted_period is not None else None,
                        "color_by_level": effective_color_by_level,
                    })
                except Exception as e:
                    # Skip admin regions that can't be loaded
                    print(f"Warning: Could not load admin regions for {a.gadm_key} level {a.level}: {e}")
                    continue

        # Serialize admin rivers
        admin_rivers_serialized = []
        for ar in self._admin_rivers:
            restricted_period = self._apply_limits_to_period(ar.period)
            # Include objects with no period (always visible) or valid restricted periods
            if ar.period is None or restricted_period is not None:
                try:
                    # Load all rivers from Natural Earth and Overpass data
                    all_rivers = []
                    
                    # Load rivers based on specified sources
                    from .loaders import _read_json, NE_RIVERS_FILE, OVERPASS_DIR
                    import os
                    
                    # Load Natural Earth rivers if requested
                    if "naturalearth" in ar.sources:
                        if os.path.exists(NE_RIVERS_FILE):
                            ne_data = _read_json(NE_RIVERS_FILE)
                            for feature in ne_data.get("features", []):
                                props = feature.get("properties", {}) or {}
                                # Add source information to properties
                                feature.setdefault("properties", {})
                                feature["properties"]["_source"] = "naturalearth"
                                feature["properties"]["_ne_id"] = props.get("ne_id", "unknown")
                                all_rivers.append(feature)
                    
                    # Load Overpass rivers if requested
                    if "overpass" in ar.sources:
                        if os.path.isdir(OVERPASS_DIR):
                            for filename in os.listdir(OVERPASS_DIR):
                                if filename.endswith('.json'):
                                    filepath = os.path.join(OVERPASS_DIR, filename)
                                    try:
                                        overpass_data = _read_json(filepath)
                                        # Handle both Feature and FeatureCollection
                                        if overpass_data.get("type") == "Feature":
                                            overpass_data.setdefault("properties", {})
                                            overpass_data["properties"]["_source"] = "overpass"
                                            overpass_data["properties"]["_filename"] = filename
                                            all_rivers.append(overpass_data)
                                        elif overpass_data.get("type") == "FeatureCollection":
                                            for feature in overpass_data.get("features", []):
                                                feature.setdefault("properties", {})
                                                feature["properties"]["_source"] = "overpass"
                                                feature["properties"]["_filename"] = filename
                                                all_rivers.append(feature)
                                    except Exception as e:
                                        print(f"Warning: Could not load overpass file {filename}: {e}")
                                        continue
                    
                    # Only create AdminRivers entry if we actually found rivers
                    if all_rivers:
                        # Create a FeatureCollection with all rivers
                        admin_rivers_geojson = {
                            "type": "FeatureCollection",
                            "features": all_rivers
                        }
                        
                        admin_rivers_serialized.append({
                            "geometry": admin_rivers_geojson,
                            "classes": ar.classes,
                            "period": list(restricted_period) if restricted_period is not None else None,
                            "sources": ar.sources,
                            "show_label": ar.show_label,
                            "n_labels": ar.n_labels,
                        })
                    else:
                        print(f"Warning: No rivers found for AdminRivers with sources: {ar.sources}")
                except Exception as e:
                    # Skip admin rivers that can't be loaded
                    print(f"Warning: Could not load admin rivers: {e}")
                    continue

        # Serialize data elements - optimized approach
        data_serialized = []
        data_by_gadm = {}  # Group data elements by GADM code and find_in_gadm
        
        # First, group all data elements by GADM code and find_in_gadm
        for d in self._data:
            restricted_period = self._apply_limits_to_period(d.period)
            # Include objects with no period (always visible) or valid restricted periods
            if d.period is None or restricted_period is not None:
                # Create a unique key that includes both gadm and find_in_gadm
                key = (d.gadm, tuple(d.find_in_gadm) if d.find_in_gadm else None)
                if key not in data_by_gadm:
                    data_by_gadm[key] = []
                data_by_gadm[key].append({
                    "value": d.value,
                    "period": list(restricted_period) if restricted_period is not None else None,
                    "classes": d.classes,
                })
        
        # Process DataFrame elements - create efficient dataframe entries with actual geometry
        dataframes_serialized = []
        all_dataframe_values = []  # Collect all values for colormap generation
        
        for df_entry in self._dataframes:
            try:
                import pandas as pd
                from .loaders import load_gadm_like
                
                # Process static DataFrame (single data column)
                if df_entry.data_column is not None:
                    # Group GIDs by their GADM file for efficient loading
                    gid_groups = {}
                    dataframe_data = {}
                    dataframe_notes = {}
                    for gid, row in df_entry.dataframe.iterrows():
                        value = row[df_entry.data_column]
                        note_val = None
                        if 'note' in df_entry.dataframe.columns:
                            note_val = row.get('note')
                        if not pd.isna(value):
                            gid_str = str(gid)
                            dataframe_data[gid_str] = float(value)
                            if note_val is not None and not (isinstance(note_val, float) and pd.isna(note_val)):
                                dataframe_notes[gid_str] = str(note_val)
                            all_dataframe_values.append(float(value))
                            # Determine the GADM file key for this GID
                            if gid_str.startswith('Z'):
                                # Disputed territory - use the GID itself
                                gadm_key = gid_str
                            else:
                                # Regular GADM - use the GID itself to determine level
                                gadm_key = gid_str
                            if gadm_key not in gid_groups:
                                gid_groups[gadm_key] = []
                            gid_groups[gadm_key].append(gid_str)
                    
                    # Load geometry and create layers for each GADM group
                    for gadm_key, gids in gid_groups.items():
                        try:
                            # Load GADM data for this key
                            gadm_geojson = load_gadm_like(gadm_key, df_entry.find_in_gadm)
                            if not gadm_geojson.get("features"):
                                continue
                            
                            # Filter features that match our GIDs
                            matching_features = []
                            for feature in gadm_geojson.get("features", []):
                                props = feature.get("properties", {}) or {}
                                # Check if this feature matches any of our GIDs
                                for gid in gids:
                                    if self._feature_matches_gid(feature, gid):
                                        # Add data value to feature properties
                                        feature_copy = feature.copy()
                                        feature_copy["properties"] = props.copy()
                                        feature_copy["properties"]["_dataframe_value"] = dataframe_data[gid]
                                        feature_copy["properties"]["_dataframe_gid"] = gid
                                        if gid in dataframe_notes:
                                            feature_copy["properties"]["_dataframe_note"] = dataframe_notes[gid]
                                        matching_features.append(feature_copy)
                            
                            if matching_features:
                                dataframes_serialized.append({
                                    "type": "static",
                                    "geometry": {"type": "FeatureCollection", "features": matching_features},
                                    "classes": df_entry.classes,
                                })
                                
                        except Exception as e:
                            print(f"Warning: Could not load GADM data for {gadm_key}: {e}")
                            continue
                
                # Process dynamic DataFrame (year columns)
                elif df_entry.year_columns is not None:
                    # Group GIDs by their GADM file for efficient loading
                    gid_groups = {}
                    dataframe_data = {}
                    dataframe_notes = {}
                    years = []
                    
                    # Parse years from column names
                    for year_col in df_entry.year_columns:
                        try:
                            year = int(year_col)
                            years.append(year)
                        except ValueError:
                            continue
                    
                    # Build data structure: {gid: {year: value}}
                    for gid, row in df_entry.dataframe.iterrows():
                        gid_data = {}
                        gid_notes = {}
                        for year_col in df_entry.year_columns:
                            try:
                                year = int(year_col)
                                value = row[year_col]
                                if not pd.isna(value):
                                    gid_data[year] = float(value)
                                    all_dataframe_values.append(float(value))
                                # Optional per-year note column like 2021_note
                                note_col = f"{year_col}_note"
                                if note_col in df_entry.dataframe.columns:
                                    note_val = row.get(note_col)
                                    if note_val is not None and not (isinstance(note_val, float) and pd.isna(note_val)):
                                        gid_notes[year] = str(note_val)
                            except ValueError:
                                continue
                        
                        if gid_data:  # Only include GIDs with valid data
                            gid_str = str(gid)
                            dataframe_data[gid_str] = gid_data
                            if gid_notes:
                                dataframe_notes[gid_str] = gid_notes
                            # Determine the GADM file key for this GID
                            if gid_str.startswith('Z'):
                                # Disputed territory - use the GID itself
                                gadm_key = gid_str
                            else:
                                # Regular GADM - use the GID itself to determine level
                                gadm_key = gid_str
                            if gadm_key not in gid_groups:
                                gid_groups[gadm_key] = []
                            gid_groups[gadm_key].append(gid_str)
                    
                    # Load geometry and create layers for each GADM group
                    for gadm_key, gids in gid_groups.items():
                        try:
                            # Load GADM data for this key
                            gadm_geojson = load_gadm_like(gadm_key, df_entry.find_in_gadm)
                            if not gadm_geojson.get("features"):
                                continue
                            
                            # Filter features that match our GIDs
                            matching_features = []
                            for feature in gadm_geojson.get("features", []):
                                props = feature.get("properties", {}) or {}
                                # Check if this feature matches any of our GIDs
                                for gid in gids:
                                    if self._feature_matches_gid(feature, gid):
                                        # Add time-series data to feature properties
                                        feature_copy = feature.copy()
                                        feature_copy["properties"] = props.copy()
                                        feature_copy["properties"]["_dataframe_data"] = dataframe_data[gid]
                                        feature_copy["properties"]["_dataframe_gid"] = gid
                                        if gid in dataframe_notes:
                                            feature_copy["properties"]["_dataframe_notes"] = dataframe_notes[gid]
                                        matching_features.append(feature_copy)
                            
                            if matching_features:
                                dataframes_serialized.append({
                                    "type": "dynamic",
                                    "geometry": {"type": "FeatureCollection", "features": matching_features},
                                    "years": sorted(years),
                                    "classes": df_entry.classes,
                                })
                                
                        except Exception as e:
                            print(f"Warning: Could not load GADM data for {gadm_key}: {e}")
                            continue
            
            except Exception as e:
                print(f"Warning: Could not process DataFrame: {e}")
                continue
        
        # Process each GADM group efficiently
        from .loaders import load_gadm_like
        
        for (gadm, find_in_gadm), data_elements in data_by_gadm.items():
            try:
                # Load GADM data once per GADM (already cached via _file_cache)
                gadm_geojson = load_gadm_like(gadm, list(find_in_gadm) if find_in_gadm else None)
                
                if not gadm_geojson.get("features"):
                    print(f"Warning: No GADM features found for: {gadm}")
                    continue
                
                # Create a single FeatureCollection for this GADM with all data elements
                # This avoids deep copying the same geometry multiple times
                features_with_data = []
                for feature in gadm_geojson.get("features", []):
                    # Shallow copy the feature (much faster than deep copy)
                    feature_copy = feature.copy()
                    feature_copy["properties"] = feature["properties"].copy()
                    
                    # Add all data values as properties for this feature
                    feature_copy["properties"]["_data_values"] = [de["value"] for de in data_elements]
                    feature_copy["properties"]["_data_periods"] = [de["period"] for de in data_elements]
                    feature_copy["properties"]["_data_classes"] = [de["classes"] for de in data_elements]
                    
                    # Calculate colors for all values at once
                    colors = []
                    for de in data_elements:
                        if self._data_colormap is not None:
                            colors.append(self._data_colormap.get_color(de["value"]))
                        else:
                            # Use default yellow-orange-red colormap if none set
                            from matplotlib.colors import LinearSegmentedColormap
                            default_colormap = DataColormap(LinearSegmentedColormap.from_list("custom_cmap", ["yellow", "orange", "red"]))
                            default_colormap.add_value(de["value"])
                            colors.append(default_colormap.get_color(de["value"]))
                    
                    feature_copy["properties"]["_data_colors"] = colors
                    features_with_data.append(feature_copy)
                
                # Create a single FeatureCollection for this GADM
                data_geojson = {
                    "type": "FeatureCollection",
                    "features": features_with_data
                }
                
                # Create one data entry per data element, but all share the same geometry
                for i, data_element in enumerate(data_elements):
                    data_serialized.append({
                        "gadm": gadm,
                        "value": data_element["value"],
                        "geometry": data_geojson,  # Shared geometry
                        "classes": data_element["classes"],
                        "period": data_element["period"],
                        "color": colors[i],  # Pre-calculated color
                        "data_index": i,  # Index to identify which data element this represents
                    })
                    
            except Exception as e:
                # Skip data elements that can't be loaded
                print(f"Warning: Could not load data element for {gadm}: {e}")
                continue

        # Generate color bar if data elements or DataFrames exist
        colormap_svg = None
        if (data_serialized and self._data_colormap is not None) or all_dataframe_values:
            # Use DataFrame colormap if available, otherwise use data colormap
            if all_dataframe_values and self._data_colormap is not None:
                # Generate colormap for DataFrame data using user's colormap
                colormap = self._data_colormap.colormap
                
                # Use DataFrame values for vmin/vmax if not explicitly set
                if self._data_colormap.vmin is not None:
                    vmin = self._data_colormap.vmin
                else:
                    vmin = min(all_dataframe_values)
                if self._data_colormap.vmax is not None:
                    vmax = self._data_colormap.vmax
                else:
                    vmax = max(all_dataframe_values)
                
                try:
                    colormap_svg = generate_colormap_svg(colormap, vmin, vmax, norm=self._data_colormap.norm)
                except Exception as e:
                    print(f"Warning: Could not generate DataFrame color bar: {e}")
            
            elif data_serialized and self._data_colormap is not None:
                # Use existing data colormap logic
                vmin = self._data_colormap.vmin
                vmax = self._data_colormap.vmax
                
                # If vmin/vmax are None, calculate from values
                if vmin is None or vmax is None:
                    all_values = [d["value"] for d in data_serialized]
                    vmin = vmin if vmin is not None else min(all_values)
                    vmax = vmax if vmax is not None else max(all_values)
                
                try:
                    colormap_svg = generate_colormap_svg(self._data_colormap.colormap, vmin, vmax, norm=self._data_colormap.norm)
                except Exception as e:
                    print(f"Warning: Could not generate color bar: {e}")

        return {
            "css": "\n".join(self._css) if self._css else "",
            "flags": pax,
            "rivers": rivers_serialized,
            "paths": paths_serialized,
            "points": points_serialized,
            "texts": texts_serialized,
            "title_boxes": title_boxes_serialized,
            "admins": admins_serialized,
            "admin_rivers": admin_rivers_serialized,
            "data": data_serialized,
            "dataframes": dataframes_serialized,
            "base_options": base_options_serialized,
            "map_limits": list(self._map_limits) if self._map_limits is not None else None,
            "play_speed": self._play_speed,
            "colormap_svg": colormap_svg,
                "colormap_info": self._serialize_colormap_info(all_dataframe_values) if self._data_colormap is not None else None,
        }

    @time_debug("Show (export map)")
    def show(self, out_json: str = "map.json", out_html: str = "map.html") -> None:
        """Export the map to JSON and HTML files.
        
        Args:
            out_json: Output path for JSON data file
            out_html: Output path for HTML visualization file
            
        Example:
            >>> map.show("my_map.json", "my_map.html")
        """
        # watermark with a TitleBox
        self.TitleBox("<i>made with <a href='https://github.com/srajma/xatra'>xatra</a></i>")
        payload = self._export_json()
        import json
        with open(out_json, "w", encoding="utf-8") as f:
            json.dump(payload, f)
        export_html(payload, out_html)

    # Handle provider names from leaflet-providers
    PROVIDER_URLS = {
        "OpenStreetMap": "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
        "Esri.WorldImagery": "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        "OpenTopoMap": "https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png",
        "Esri.WorldPhysical": "https://server.arcgisonline.com/ArcGIS/rest/services/World_Physical_Map/MapServer/tile/{z}/{y}/{x}",
        "CartoDB.Positron": "https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png",
        "CartoDB.PositronNoLabels": "https://{s}.basemaps.cartocdn.com/light_nolabels/{z}/{x}/{y}.png",
        "USGS.USImageryTopo": "https://basemap.nationalmap.gov/arcgis/rest/services/USGSImageryTopo/MapServer/tile/{z}/{y}/{x}",
        "Esri.OceanBasemap": "https://server.arcgisonline.com/ArcGIS/rest/services/Ocean_Basemap/MapServer/tile/{z}/{y}/{x}",
    }
