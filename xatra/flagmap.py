from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Union

from shapely.geometry import shape, mapping, Point, LineString
from shapely.ops import unary_union

from .territory import Territory
from .render import export_html
from .paxmax import paxmax_aggregate


GeometryLike = Union[Territory, Dict[str, Any]]


@dataclass
class FlagEntry:
    label: str
    territory: Territory
    period: Optional[Tuple[int, int]] = None
    note: Optional[str] = None


@dataclass
class RiverEntry:
    label: str
    geometry: Dict[str, Any]
    note: Optional[str] = None
    classes: Optional[str] = None
    period: Optional[Tuple[int, int]] = None


@dataclass
class PathEntry:
    label: str
    coords: List[Tuple[float, float]]
    classes: Optional[str] = None
    period: Optional[Tuple[int, int]] = None


@dataclass
class PointEntry:
    label: str
    position: Tuple[float, float]
    period: Optional[Tuple[int, int]] = None


@dataclass
class TextEntry:
    label: str
    position: Tuple[float, float]
    classes: Optional[str] = None
    period: Optional[Tuple[int, int]] = None


@dataclass
class TitleBoxEntry:
    html: str
    period: Optional[Tuple[int, int]] = None


@dataclass
class BaseOptionEntry:
    url: str
    name: str
    default: bool = False


class FlagMap:
    def __init__(self) -> None:
        self._flags: List[FlagEntry] = []
        self._rivers: List[RiverEntry] = []
        self._paths: List[PathEntry] = []
        self._points: List[PointEntry] = []
        self._texts: List[TextEntry] = []
        self._title_boxes: List[TitleBoxEntry] = []
        self._base_options: List[BaseOptionEntry] = []
        self._css: List[str] = []
        self._map_limits: Optional[Tuple[int, int]] = None
        
        # Add default base options
        self._add_default_base_options()

    # API methods
    def Flag(self, label: str, value: Territory, period: Optional[List[int]] = None, note: Optional[str] = None) -> None:
        period_tuple: Optional[Tuple[int, int]] = None
        if period is not None:
            if len(period) != 2:
                raise ValueError("period must be [start, end]")
            period_tuple = (int(period[0]), int(period[1]))
        self._flags.append(FlagEntry(label=label, territory=value, period=period_tuple, note=note))

    def River(self, label: str, value: Dict[str, Any], note: Optional[str] = None, classes: Optional[str] = None, period: Optional[List[int]] = None) -> None:
        period_tuple: Optional[Tuple[int, int]] = None
        if period is not None:
            if len(period) != 2:
                raise ValueError("period must be [start, end]")
            period_tuple = (int(period[0]), int(period[1]))
        self._rivers.append(RiverEntry(label=label, geometry=value, note=note, classes=classes, period=period_tuple))

    def Path(self, label: str, value: List[List[float]], classes: Optional[str] = None, period: Optional[List[int]] = None) -> None:
        coords = [(float(lat), float(lon)) for lat, lon in value]
        period_tuple: Optional[Tuple[int, int]] = None
        if period is not None:
            if len(period) != 2:
                raise ValueError("period must be [start, end]")
            period_tuple = (int(period[0]), int(period[1]))
        self._paths.append(PathEntry(label=label, coords=coords, classes=classes, period=period_tuple))

    def Point(self, label: str, position: List[float], period: Optional[List[int]] = None) -> None:
        period_tuple: Optional[Tuple[int, int]] = None
        if period is not None:
            if len(period) != 2:
                raise ValueError("period must be [start, end]")
            period_tuple = (int(period[0]), int(period[1]))
        self._points.append(PointEntry(label=label, position=(float(position[0]), float(position[1])), period=period_tuple))

    def Text(self, label: str, position: List[float], classes: Optional[str] = None, period: Optional[List[int]] = None) -> None:
        period_tuple: Optional[Tuple[int, int]] = None
        if period is not None:
            if len(period) != 2:
                raise ValueError("period must be [start, end]")
            period_tuple = (int(period[0]), int(period[1]))
        self._texts.append(TextEntry(label=label, position=(float(position[0]), float(position[1])), classes=classes, period=period_tuple))

    def TitleBox(self, html: str, period: Optional[List[int]] = None) -> None:
        period_tuple: Optional[Tuple[int, int]] = None
        if period is not None:
            if len(period) != 2:
                raise ValueError("period must be [start, end]")
            period_tuple = (int(period[0]), int(period[1]))
        self._title_boxes.append(TitleBoxEntry(html=html, period=period_tuple))

    def CSS(self, css: str) -> None:
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
        """Derive a display name from URL."""
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
        """Add default base layer options."""
        # self.BaseOption("OpenStreetMap", default=True)
        # self.BaseOption("Esri.WorldImagery")
        # self.BaseOption("OpenTopoMap")
        # self.BaseOption("Esri.WorldPhysical")
        # let's not do this, because it makes it impossible to override the default
        pass

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
        if period is None or self._map_limits is None:
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
        # Resolve territories to GeoJSON shapes and apply limits
        flags_serialized: List[Dict[str, Any]] = []
        for fl in self._flags:
            restricted_period = self._apply_limits_to_period(fl.period)
            if restricted_period is not None:  # Skip if period becomes null set
                geom = fl.territory.to_geometry()
                flags_serialized.append({
                    "label": fl.label,
                    "geometry": mapping(geom) if geom is not None else None,
                    "period": list(restricted_period),
                    "note": fl.note,
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

        # Pax-max aggregation
        pax = paxmax_aggregate(flags_serialized, earliest_start)

        rivers_serialized = []
        for r in self._rivers:
            restricted_period = self._apply_limits_to_period(r.period)
            if restricted_period is not None:  # Skip if period becomes null set
                rivers_serialized.append({
                    "label": r.label,
                    "geometry": r.geometry,
                    "note": r.note,
                    "classes": r.classes,
                    "period": list(restricted_period),
                })

        paths_serialized = []
        for p in self._paths:
            restricted_period = self._apply_limits_to_period(p.period)
            if restricted_period is not None:  # Skip if period becomes null set
                paths_serialized.append({
                    "label": p.label,
                    "coords": p.coords,
                    "classes": p.classes,
                    "period": list(restricted_period),
                })

        points_serialized = []
        for p in self._points:
            restricted_period = self._apply_limits_to_period(p.period)
            if restricted_period is not None:  # Skip if period becomes null set
                points_serialized.append({
                    "label": p.label,
                    "position": p.position,
                    "period": list(restricted_period),
                })

        texts_serialized = []
        for t in self._texts:
            restricted_period = self._apply_limits_to_period(t.period)
            if restricted_period is not None:  # Skip if period becomes null set
                texts_serialized.append({
                    "label": t.label,
                    "position": t.position,
                    "classes": t.classes,
                    "period": list(restricted_period),
                })

        base_options_serialized = [{
            "url": b.url,
            "name": b.name,
            "default": b.default,
        } for b in self._base_options]

        title_boxes_serialized = []
        for ft in self._title_boxes:
            restricted_period = self._apply_limits_to_period(ft.period)
            if restricted_period is not None:  # Skip if period becomes null set
                title_boxes_serialized.append({
                    "html": ft.html,
                    "period": list(restricted_period),
                })

        return {
            "css": "\n".join(self._css) if self._css else "",
            "flags": pax,
            "rivers": rivers_serialized,
            "paths": paths_serialized,
            "points": points_serialized,
            "texts": texts_serialized,
            "title_boxes": title_boxes_serialized,
            "base_options": base_options_serialized,
            "map_limits": list(self._map_limits) if self._map_limits is not None else None,
        }

    def show(self, out_json: str = "map.json", out_html: str = "map.html") -> None:
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
