"""
Xatra Territory Module

This module provides the Territory class for representing geographical regions
with support for set algebra operations (union, difference) and lazy loading
from various GeoJSON data sources.

The Territory class enables composable geographical regions by combining
base datasets using Shapely geometry operations.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from shapely.geometry import shape, mapping
from shapely.ops import unary_union

from .loaders import load_gadm_like, load_naturalearth_like
from .debug_utils import time_debug


@time_debug("Convert GeoJSON to geometry")
def _geojson_to_geometry(geojson_obj: Dict[str, Any]):
    """Convert GeoJSON object to Shapely geometry.
    
    Args:
        geojson_obj: GeoJSON Feature, FeatureCollection, or Geometry object
        
    Returns:
        Shapely geometry object or None if invalid
    """
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
    """Represents a composable territory via set algebra over base GeoJSON datasets.
    
    Territory objects support lazy loading from various data sources and can be
    combined using set algebra operations (union, difference). Geometries are
    cached after first access for performance.
    
    Example:
        >>> india = Territory.from_gadm("IND")
        >>> pakistan = Territory.from_gadm("PAK")
        >>> northern_india = india - pakistan
    """

    _geometry_provider: Optional[callable] = None
    _geom_cache: Optional[Any] = None

    @staticmethod
    def from_geojson(geojson_obj: Dict[str, Any]) -> "Territory":
        """Create Territory from GeoJSON object.
        
        Args:
            geojson_obj: GeoJSON Feature, FeatureCollection, or Geometry object
            
        Returns:
            Territory instance
        """
        def provider():
            return _geojson_to_geometry(geojson_obj)
        return Territory(_geometry_provider=provider)

    @staticmethod
    def from_gadm(key: str, find_in_gadm: Optional[List[str]] = None) -> "Territory":
        """Create Territory from GADM administrative boundary.
        
        Args:
            key: GADM country code (e.g., "IND", "PAK")
            find_in_gadm: Optional list of country codes to search in if key is not found in its own file
            
        Returns:
            Territory instance
        """
        def provider():
            obj = load_gadm_like(key, find_in_gadm)
            return _geojson_to_geometry(obj)
        return Territory(_geometry_provider=provider)

    @staticmethod
    def from_naturalearth(ne_id: str) -> "Territory":
        """Create Territory from Natural Earth dataset.
        
        Args:
            ne_id: Natural Earth feature ID
            
        Returns:
            Territory instance
        """
        def provider():
            obj = load_naturalearth_like(ne_id)
            return _geojson_to_geometry(obj)
        return Territory(_geometry_provider=provider)

    @time_debug("Convert territory to geometry")
    def to_geometry(self):
        """Get the Shapely geometry for this territory.
        
        Returns:
            Shapely geometry object or None if invalid
        """
        if self._geom_cache is not None:
            return self._geom_cache
        if self._geometry_provider is None:
            return None
        self._geom_cache = self._geometry_provider()
        return self._geom_cache

    # Set algebra
    def __or__(self, other: "Territory") -> "Territory":
        """Union of two territories.
        
        Args:
            other: Another Territory object
            
        Returns:
            New Territory representing the union
        """
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
        """Difference of two territories (self - other).
        
        Args:
            other: Territory to subtract from self
            
        Returns:
            New Territory representing the difference
        """
        def provider():
            a = self.to_geometry()
            b = other.to_geometry()
            if a is None:
                return None
            if b is None:
                return a
            return a.difference(b)
        return Territory(_geometry_provider=provider)
