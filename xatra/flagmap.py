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

    def _export_json(self) -> Dict[str, Any]:
        # Resolve territories to GeoJSON shapes
        flags_serialized: List[Dict[str, Any]] = []
        for fl in self._flags:
            geom = fl.territory.to_geometry()
            flags_serialized.append({
                "label": fl.label,
                "geometry": mapping(geom) if geom is not None else None,
                "period": list(fl.period) if fl.period is not None else None,
                "note": fl.note,
            })

        # Pax-max aggregation
        pax = paxmax_aggregate(flags_serialized)

        rivers_serialized = [{
            "label": r.label,
            "geometry": r.geometry,
            "note": r.note,
            "classes": r.classes,
            "period": list(r.period) if r.period is not None else None,
        } for r in self._rivers]

        paths_serialized = [{
            "label": p.label,
            "coords": p.coords,
            "classes": p.classes,
            "period": list(p.period) if p.period is not None else None,
        } for p in self._paths]

        points_serialized = [{
            "label": p.label,
            "position": p.position,
            "period": list(p.period) if p.period is not None else None,
        } for p in self._points]

        texts_serialized = [{
            "label": t.label,
            "position": t.position,
            "classes": t.classes,
            "period": list(t.period) if t.period is not None else None,
        } for t in self._texts]

        base_options_serialized = [{
            "url": b.url,
            "name": b.name,
            "default": b.default,
        } for b in self._base_options]

        title_boxes_serialized = [{
            "html": ft.html,
            "period": list(ft.period) if ft.period is not None else None,
        } for ft in self._title_boxes]

        return {
            "css": "\n".join(self._css) if self._css else "",
            "flags": pax,
            "original_flags": flags_serialized,  # Include original flags for no-period rendering
            "rivers": rivers_serialized,
            "paths": paths_serialized,
            "points": points_serialized,
            "texts": texts_serialized,
            "title_boxes": title_boxes_serialized,
            "base_options": base_options_serialized,
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
