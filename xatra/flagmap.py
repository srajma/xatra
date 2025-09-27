"""
Xatra FlagMap Module

This module provides the core FlagMap class for creating interactive historical maps.
It supports various map elements including flags (countries/kingdoms), rivers, paths, 
points, text labels, and title boxes with optional time-based filtering for dynamic maps.

The module uses the pax-max aggregation method to create stable periods for dynamic
maps, allowing smooth transitions between different historical states.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple, Union

from shapely.geometry import mapping

from .territory import Territory
from .render import export_html
from .paxmax import paxmax_aggregate
from .colorseq import ColorSequence, LinearColorSequence


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
    """
    label: str
    territory: Territory
    period: Optional[Tuple[int, int]] = None
    note: Optional[str] = None
    color: Optional[str] = None


@dataclass
class RiverEntry:
    """Represents a river with GeoJSON geometry and optional styling.
    
    Args:
        label: Display name for the river
        geometry: GeoJSON geometry object
        note: Optional tooltip text for the river
        classes: Optional CSS classes for styling
        period: Optional time period as (start_year, end_year) tuple
    """
    label: str
    geometry: Dict[str, Any]
    note: Optional[str] = None
    classes: Optional[str] = None
    period: Optional[Tuple[int, int]] = None


@dataclass
class PathEntry:
    """Represents a path/route with coordinate list and optional styling.
    
    Args:
        label: Display name for the path
        coords: List of (latitude, longitude) coordinate tuples
        classes: Optional CSS classes for styling
        period: Optional time period as (start_year, end_year) tuple
    """
    label: str
    coords: List[Tuple[float, float]]
    classes: Optional[str] = None
    period: Optional[Tuple[int, int]] = None


@dataclass
class PointEntry:
    """Represents a point of interest with position and optional time period.
    
    Args:
        label: Display name for the point
        position: (latitude, longitude) coordinate tuple
        period: Optional time period as (start_year, end_year) tuple
    """
    label: str
    position: Tuple[float, float]
    period: Optional[Tuple[int, int]] = None


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
    """
    gadm_key: str
    level: int
    period: Optional[Tuple[int, int]] = None
    classes: Optional[str] = None


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


class FlagMap:
    """Main class for creating interactive historical maps.
    
    FlagMap is the core class for creating maps similar to "matplotlib of maps".
    It supports various map elements including flags (countries/kingdoms), rivers,
    paths, points, text labels, and title boxes. Maps can be static or dynamic
    with time-based filtering using the pax-max aggregation method.
    
    Example:
        >>> map = FlagMap()
        >>> map.Flag("Maurya", territory, period=[320, 180])
        >>> map.River("Ganges", river_geometry, classes="major-river")
        >>> map.export("map.html")
    """
    
    def __init__(self) -> None:
        """Initialize a new FlagMap instance.
        
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
        self._base_options: List[BaseOptionEntry] = []
        self._css: List[str] = []
        self._map_limits: Optional[Tuple[int, int]] = None
        self._color_sequence: ColorSequence = LinearColorSequence()
        self._flag_index: int = 0
        self._label_colors: Dict[str, str] = {}  # Track colors by label
        
        # Add default base options
        self._add_default_base_options()

    # API methods
    def FlagColorSequence(self, color_sequence: ColorSequence) -> None:
        """Set the color sequence for flags.
        
        Args:
            color_sequence: ColorSequence instance to use for flag colors
            
        Example:
            >>> from xatra.colorseq import RotatingColorSequence
            >>> map.FlagColorSequence(RotatingColorSequence())
        """
        self._color_sequence = color_sequence

    def Flag(self, label: str, value: Territory, period: Optional[List[int]] = None, note: Optional[str] = None, color: Optional[str] = None) -> None:
        """Add a flag (country/kingdom) to the map.
        
        Flags automatically get colors from the map's color sequence. Flags with the same label
        will always use the same color. You can override this behavior by providing a custom color.
        
        Args:
            label: Display name for the flag
            value: Territory object defining the geographical extent
            period: Optional time period as [start_year, end_year] list
            note: Optional tooltip text for the flag
            color: Optional color for the flag (overrides color sequence) in hex code
            
        Example:
            >>> map.Flag("Maurya", maurya_territory, period=[320, 180], note="Ancient Indian empire")
            >>> map.Flag("Maurya", other_territory)  # Reuses the same color as above
            >>> map.Flag("Custom", territory, color="#ff0000")  # Custom red color
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
                # Assign new color from sequence and store it for this label
                assigned_color = self._color_sequence[self._flag_index]
                color = assigned_color.hex
                self._label_colors[label] = color
                self._flag_index += 1
        
        self._flags.append(FlagEntry(label=label, territory=value, period=period_tuple, note=note, color=color))

    def River(self, label: str, value: Dict[str, Any], note: Optional[str] = None, classes: Optional[str] = None, period: Optional[List[int]] = None) -> None:
        """Add a river to the map.
        
        Args:
            label: Display name for the river
            value: GeoJSON geometry object
            note: Optional tooltip text for the river
            classes: Optional CSS classes for styling
            period: Optional time period as [start_year, end_year] list
            
        Example:
            >>> map.River("Ganges", ganges_geometry, classes="major-river", note="Sacred river")
        """
        period_tuple: Optional[Tuple[int, int]] = None
        if period is not None:
            if len(period) != 2:
                raise ValueError("period must be [start, end]")
            period_tuple = (int(period[0]), int(period[1]))
        self._rivers.append(RiverEntry(label=label, geometry=value, note=note, classes=classes, period=period_tuple))

    def Path(self, label: str, value: List[List[float]], classes: Optional[str] = None, period: Optional[List[int]] = None) -> None:
        """Add a path/route to the map.
        
        Args:
            label: Display name for the path
            value: List of [latitude, longitude] coordinate pairs
            classes: Optional CSS classes for styling
            period: Optional time period as [start_year, end_year] list
            
        Example:
            >>> map.Path("Silk Road", [[40.0, 74.0], [35.0, 103.0]], classes="trade-route")
        """
        coords = [(float(lat), float(lon)) for lat, lon in value]
        period_tuple: Optional[Tuple[int, int]] = None
        if period is not None:
            if len(period) != 2:
                raise ValueError("period must be [start, end]")
            period_tuple = (int(period[0]), int(period[1]))
        self._paths.append(PathEntry(label=label, coords=coords, classes=classes, period=period_tuple))

    def Point(self, label: str, position: List[float], period: Optional[List[int]] = None) -> None:
        """Add a point of interest to the map.
        
        Args:
            label: Display name for the point
            position: [latitude, longitude] coordinate pair
            period: Optional time period as [start_year, end_year] list
            
        Example:
            >>> map.Point("Delhi", [28.6139, 77.2090], period=[1200, 1800])
        """
        period_tuple: Optional[Tuple[int, int]] = None
        if period is not None:
            if len(period) != 2:
                raise ValueError("period must be [start, end]")
            period_tuple = (int(period[0]), int(period[1]))
        self._points.append(PointEntry(label=label, position=(float(position[0]), float(position[1])), period=period_tuple))

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

    def lim(self, start: int, end: int) -> None:
        """Set the time limits for the map.
        
        This restricts all object periods to be within the specified range.
        Object periods are considered clopen intervals [x, y), so we add a small
        epsilon to ensure proper behavior at the boundaries.
        
        Args:
            start: Start year (inclusive)
            end: End year (exclusive)
        """
        self._map_limits = (int(start), int(end))

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

    def Admin(self, gadm: str, level: int, period: Optional[List[int]] = None, classes: Optional[str] = None) -> None:
        """Add administrative regions from GADM data.
        
        Args:
            gadm: GADM key (e.g., "IND.31" for Tamil Nadu)
            level: Administrative level to display (e.g., 3 for tehsils)
            period: Optional time period as [start_year, end_year] list
            classes: Optional CSS classes for styling
            
        Example:
            >>> map.Admin(gadm="IND.31", level=3)  # Show all tehsils in Tamil Nadu
            >>> map.Admin(gadm="IND", level=1, period=[1950, 2000])  # Show states in India for specific period
        """
        period_tuple: Optional[Tuple[int, int]] = None
        if period is not None:
            if len(period) != 2:
                raise ValueError("period must be [start, end]")
            period_tuple = (int(period[0]), int(period[1]))
        
        self._admins.append(AdminEntry(gadm_key=gadm, level=level, period=period_tuple, classes=classes))

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

    def _export_json(self) -> Dict[str, Any]:
        """Export map data to JSON format for rendering.
        
        Applies time limits, performs pax-max aggregation on flags, and serializes
        all map elements to a dictionary suitable for HTML rendering.
        
        Returns:
            Dictionary containing all map data including flags, rivers, paths, etc.
        """
        # Resolve territories to GeoJSON shapes and apply limits
        flags_serialized: List[Dict[str, Any]] = []
        for fl in self._flags:
            restricted_period = self._apply_limits_to_period(fl.period)
            # Include objects with no period (always visible) or valid restricted periods
            if fl.period is None or restricted_period is not None:
                geom = fl.territory.to_geometry()
                flags_serialized.append({
                    "label": fl.label,
                    "geometry": mapping(geom) if geom is not None else None,
                    "period": list(restricted_period) if restricted_period is not None else None,
                    "note": fl.note,
                    "color": fl.color,
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

        # Pax-max aggregation
        pax = paxmax_aggregate(flags_serialized, earliest_start)

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
                })

        points_serialized = []
        for p in self._points:
            restricted_period = self._apply_limits_to_period(p.period)
            # Include objects with no period (always visible) or valid restricted periods
            if p.period is None or restricted_period is not None:
                points_serialized.append({
                    "label": p.label,
                    "position": p.position,
                    "period": list(restricted_period) if restricted_period is not None else None,
                })

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
                # Load GADM data for the specified level and filter by the gadm_key
                from .loaders import _read_json
                import os
                try:
                    # Load the appropriate level file directly
                    parts = a.gadm_key.split('.')
                    iso3 = parts[0]
                    gadm_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "gadm")
                    level_file_path = os.path.join(gadm_dir, f"gadm41_{iso3}_{a.level}.json")
                    
                    if not os.path.exists(level_file_path):
                        print(f"Warning: GADM file not found: {level_file_path}")
                        continue
                    
                    level_file = _read_json(level_file_path)
                    
                    # Filter features that match the gadm_key prefix
                    filtered_features = []
                    for feature in level_file.get("features", []):
                        props = feature.get("properties", {}) or {}
                        gid_key = f"GID_{a.level}"
                        gid = str(props.get(gid_key, ""))
                        # Use exact prefix matching with boundary check
                        if gid.startswith(a.gadm_key) and (len(gid) == len(a.gadm_key) or gid[len(a.gadm_key)] in ['.', '_']):
                            filtered_features.append(feature)
                    
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
                    })
                except Exception as e:
                    # Skip admin regions that can't be loaded
                    print(f"Warning: Could not load admin regions for {a.gadm_key} level {a.level}: {e}")
                    continue

        return {
            "css": "\n".join(self._css) if self._css else "",
            "flags": pax,
            "rivers": rivers_serialized,
            "paths": paths_serialized,
            "points": points_serialized,
            "texts": texts_serialized,
            "title_boxes": title_boxes_serialized,
            "admins": admins_serialized,
            "base_options": base_options_serialized,
            "map_limits": list(self._map_limits) if self._map_limits is not None else None,
        }

    def show(self, out_json: str = "map.json", out_html: str = "map.html") -> None:
        """Export the map to JSON and HTML files.
        
        Args:
            out_json: Output path for JSON data file
            out_html: Output path for HTML visualization file
            
        Example:
            >>> map.show("my_map.json", "my_map.html")
        """
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
