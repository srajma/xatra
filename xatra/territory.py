from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from shapely.geometry import shape, mapping
from shapely.ops import unary_union

from .loaders import load_gadm_like, load_naturalearth_like


def _geojson_to_geometry(geojson_obj: Dict[str, Any]):
    if geojson_obj is None:
        return None
    geom_type = geojson_obj.get("type")
    if geom_type == "Feature":
        return shape(geojson_obj["geometry"]) if geojson_obj.get("geometry") else None
    if geom_type == "FeatureCollection":
        geoms = [shape(feat["geometry"]) for feat in geojson_obj.get("features", []) if feat.get("geometry")]
        return unary_union(geoms) if geoms else None
    # Geometry object
    return shape(geojson_obj)


@dataclass
class Territory:
    """Represents a composable territory via set algebra over base GeoJSON datasets."""

    _geometry_provider: Optional[callable] = None
    _geom_cache: Optional[Any] = None

    @staticmethod
    def from_geojson(geojson_obj: Dict[str, Any]) -> "Territory":
        def provider():
            return _geojson_to_geometry(geojson_obj)
        return Territory(_geometry_provider=provider)

    @staticmethod
    def from_gadm(key: str) -> "Territory":
        def provider():
            obj = load_gadm_like(key)
            return _geojson_to_geometry(obj)
        return Territory(_geometry_provider=provider)

    @staticmethod
    def from_naturalearth(ne_id: str) -> "Territory":
        def provider():
            obj = load_naturalearth_like(ne_id)
            return _geojson_to_geometry(obj)
        return Territory(_geometry_provider=provider)

    def to_geometry(self):
        if self._geom_cache is not None:
            return self._geom_cache
        if self._geometry_provider is None:
            return None
        self._geom_cache = self._geometry_provider()
        return self._geom_cache

    # Set algebra
    def __or__(self, other: "Territory") -> "Territory":
        def provider():
            a = self.to_geometry()
            b = other.to_geometry()
            if a is None:
                return b
            if b is None:
                return a
            return unary_union([a, b])
        return Territory(_geometry_provider=provider)

    def __sub__(self, other: "Territory") -> "Territory":
        def provider():
            a = self.to_geometry()
            b = other.to_geometry()
            if a is None:
                return None
            if b is None:
                return a
            return a.difference(b)
        return Territory(_geometry_provider=provider)
