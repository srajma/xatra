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
    id: Optional[str] = None
    class_name: Optional[str] = None


@dataclass
class PathEntry:
    label: str
    coords: List[Tuple[float, float]]
    id: Optional[str] = None
    class_name: Optional[str] = None


@dataclass
class PointEntry:
    label: str
    position: Tuple[float, float]


@dataclass
class TextEntry:
    label: str
    position: Tuple[float, float]
    id: Optional[str] = None
    class_name: Optional[str] = None


@dataclass
class FixedTextBoxEntry:
    html: str


class FlagMap:
    def __init__(self) -> None:
        self._flags: List[FlagEntry] = []
        self._rivers: List[RiverEntry] = []
        self._paths: List[PathEntry] = []
        self._points: List[PointEntry] = []
        self._texts: List[TextEntry] = []
        self._fixed_text_boxes: List[FixedTextBoxEntry] = []
        self._css: List[str] = []

    # API methods
    def Flag(self, label: str, value: Territory, period: Optional[List[int]] = None, note: Optional[str] = None) -> None:
        period_tuple: Optional[Tuple[int, int]] = None
        if period is not None:
            if len(period) != 2:
                raise ValueError("period must be [start, end]")
            period_tuple = (int(period[0]), int(period[1]))
        self._flags.append(FlagEntry(label=label, territory=value, period=period_tuple, note=note))

    def River(self, label: str, value: Dict[str, Any], note: Optional[str] = None, id: Optional[str] = None, class_name: Optional[str] = None) -> None:
        self._rivers.append(RiverEntry(label=label, geometry=value, note=note, id=id, class_name=class_name))

    def Path(self, label: str, value: List[List[float]], id: Optional[str] = None, class_name: Optional[str] = None) -> None:
        coords = [(float(lat), float(lon)) for lat, lon in value]
        self._paths.append(PathEntry(label=label, coords=coords, id=id, class_name=class_name))

    def Point(self, label: str, position: List[float]) -> None:
        self._points.append(PointEntry(label=label, position=(float(position[0]), float(position[1]))))

    def Text(self, label: str, position: List[float], id: Optional[str] = None, class_name: Optional[str] = None) -> None:
        self._texts.append(TextEntry(label=label, position=(float(position[0]), float(position[1])), id=id, class_name=class_name))

    def FixedTextBox(self, html: str) -> None:
        self._fixed_text_boxes.append(FixedTextBoxEntry(html=html))

    def CSS(self, css: str) -> None:
        self._css.append(css)

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
            "id": r.id,
            "class_name": r.class_name,
        } for r in self._rivers]

        paths_serialized = [{
            "label": p.label,
            "coords": p.coords,
            "id": p.id,
            "class_name": p.class_name,
        } for p in self._paths]

        points_serialized = [{
            "label": p.label,
            "position": p.position,
        } for p in self._points]

        texts_serialized = [{
            "label": t.label,
            "position": t.position,
            "id": t.id,
            "class_name": t.class_name,
        } for t in self._texts]

        return {
            "css": "\n".join(self._css) if self._css else "",
            "flags": pax,
            "rivers": rivers_serialized,
            "paths": paths_serialized,
            "points": points_serialized,
            "texts": texts_serialized,
            "fixed_text_boxes": [ft.html for ft in self._fixed_text_boxes],
        }

    def show(self, out_json: str = "map.json", out_html: str = "map.html") -> None:
        payload = self._export_json()
        import json
        with open(out_json, "w", encoding="utf-8") as f:
            json.dump(payload, f)
        export_html(payload, out_html)
