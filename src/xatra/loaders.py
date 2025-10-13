"""
Xatra Data Loaders Module

This module provides functions to load geographical data from various sources
including GADM administrative boundaries, Natural Earth datasets, and Overpass API.

The loaders handle different GeoJSON formats and provide a unified interface
for accessing geographical data in the xatra system.
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional, Tuple

from .debug_utils import time_debug

# Get data directory from data_installer
try:
    from .data_installer import get_data_dir
    DATA_DIR = str(get_data_dir())
except ImportError:
    # Fallback to package directory if data_installer not available
    DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

GADM_DIR = os.path.join(DATA_DIR, "gadm")
DISPUTED_DIR = os.path.join(DATA_DIR, "disputed_territories")
DISPUTED_MAPPING_JSON = os.path.join(DISPUTED_DIR, "disputed_mapping.json")
NE_RIVERS_FILE = os.path.join(DATA_DIR, "ne_10m_rivers.geojson")
OVERPASS_DIR = os.path.join(DATA_DIR, "rivers_overpass_india")

# Global file cache to avoid repeated disk reads
_file_cache: Dict[str, Any] = {}
_disputed_mapping_cache: Optional[Dict[str, Any]] = None

DEBUG_FILE_CACHE = False

@time_debug("Read JSON file")
def _read_json(path: str):
    """Read JSON file from disk with caching.
    
    Args:
        path: Path to JSON file
        
    Returns:
        Parsed JSON data
        
    Raises:
        FileNotFoundError: If file doesn't exist
    """
    if path not in _file_cache:
        if not os.path.exists(path):
            raise FileNotFoundError(f"Missing data file: {path}")
        if DEBUG_FILE_CACHE:
            print(f"DEBUG: Loading file from disk: {path}")
        with open(path, "r", encoding="utf-8") as f:
            _file_cache[path] = json.load(f)
    else:
        if DEBUG_FILE_CACHE:
            print(f"DEBUG: Using cached file: {path}")
    return _file_cache[path]


@time_debug("Clear file cache")
def clear_file_cache():
    """Clear the file cache to free memory.
    
    This can be useful when working with very large datasets or when
    you want to ensure fresh data is loaded from disk.
    """
    global _file_cache
    _file_cache.clear()
    global _disputed_mapping_cache
    _disputed_mapping_cache = None


@time_debug("Load disputed mapping")
def _load_disputed_mapping() -> Optional[Dict[str, Any]]:
    global _disputed_mapping_cache
    if _disputed_mapping_cache is not None:
        return _disputed_mapping_cache
    try:
        if os.path.exists(DISPUTED_MAPPING_JSON):
            _disputed_mapping_cache = _read_json(DISPUTED_MAPPING_JSON)
        else:
            _disputed_mapping_cache = None
    except Exception:
        _disputed_mapping_cache = None
    return _disputed_mapping_cache


def _compute_find_in_gadm_default(key: str) -> Optional[List[str]]:
    """Compute default find_in_gadm list from disputed mapping for a given GADM key.

    Selects countries that contain the gid_root at the exact level implied by the key.
    """
    parts = key.split('.')
    gid_root = parts[0]
    # Expected level equals number of dots in key
    desired_level = 0 if len(parts) == 1 else len(parts) - 1

    mapping = _load_disputed_mapping()
    if not mapping:
        return None
    entries = mapping.get(gid_root)
    if not entries:
        return None
    # Filter by level match
    countries: List[str] = []
    for e in entries:
        try:
            if int(e.get("level", -1)) == desired_level:
                c = str(e.get("file_country"))
                if c and c not in countries:
                    countries.append(c)
        except Exception:
            continue
    return countries or None


@time_debug("Load GADM data")
def gadm(key: str, find_in_gadm: Optional[List[str]] = None):
    """Load GADM administrative boundary as Territory.
    
    Args:
        key: GADM country code (e.g., "IND", "PAK")
        find_in_gadm: Optional list of country codes to search in if key is not found in its own file
        
    Returns:
        Territory object
    """
    from .territory import Territory
    return Territory.from_gadm(key, find_in_gadm)


@time_debug("Load Natural Earth feature")
def naturalearth(ne_id: str) -> Dict[str, Any]:
    """Return GeoJSON Feature for a Natural Earth feature id from a monolithic file.

    For this prototype, we support rivers from data/ne_10m_rivers.geojson by ne_id.
    
    Args:
        ne_id: Natural Earth feature ID
        
    Returns:
        GeoJSON Feature object
        
    Raises:
        FileNotFoundError: If Natural Earth file doesn't exist
        KeyError: If ne_id not found in the file
    """
    if not os.path.exists(NE_RIVERS_FILE):
        raise FileNotFoundError(f"Missing Natural Earth rivers file: {NE_RIVERS_FILE}")
    obj = _read_json(NE_RIVERS_FILE)
    if obj.get("type") != "FeatureCollection":
        raise ValueError("Expected FeatureCollection in Natural Earth rivers file")
    for feat in obj.get("features", []):
        props = feat.get("properties", {}) or {}
        if str(props.get("ne_id")) == str(ne_id):
            return feat
    raise KeyError(f"ne_id {ne_id} not found in {NE_RIVERS_FILE}")


@time_debug("Load Overpass data")
def overpass(osm_id: str) -> Dict[str, Any]:
    """Return a GeoJSON Feature or FeatureCollection for an Overpass river by id.

    We search files under data/rivers_overpass_india whose filename contains the id.
    If the file is already GeoJSON (has type Feature/FeatureCollection), return it.
    If it's Overpass JSON (has 'elements'), convert to a LineString/MultiLineString Feature.
    
    Args:
        osm_id: OpenStreetMap ID to search for
        
    Returns:
        GeoJSON Feature or FeatureCollection
        
    Raises:
        FileNotFoundError: If no matching file found
        ValueError: If data format is unsupported
    """
    if not os.path.isdir(OVERPASS_DIR):
        raise FileNotFoundError(f"Missing overpass dir: {OVERPASS_DIR}")
    candidates: List[str] = []
    for name in os.listdir(OVERPASS_DIR):
        if str(osm_id) in name:
            candidates.append(os.path.join(OVERPASS_DIR, name))
    if not candidates:
        raise FileNotFoundError(f"No overpass file containing id '{osm_id}' in {OVERPASS_DIR}")
    # Choose the first match deterministically by name
    path = sorted(candidates)[0]
    data = _read_json(path)
    t = data.get("type")
    if t in ("Feature", "FeatureCollection"):
        return data
    # Likely Overpass JSON; convert to GeoJSON by stitching ways
    elements = data.get("elements")
    if not isinstance(elements, list):
        raise ValueError("Unsupported overpass data format")
    # Build node id -> (lon, lat)
    nodes: Dict[int, Tuple[float, float]] = {}
    ways: List[Dict[str, Any]] = []
    for el in elements:
        if el.get("type") == "node":
            nodes[int(el["id"])] = (float(el["lon"]), float(el["lat"]))
        elif el.get("type") == "way":
            ways.append(el)
    # Convert each way to coordinates
    line_geoms: List[List[List[float]]] = []
    for way in ways:
        coords: List[List[float]] = []
        for nd in way.get("nodes", []):
            if int(nd) in nodes:
                lon, lat = nodes[int(nd)]
                coords.append([lon, lat])
        if len(coords) >= 2:
            line_geoms.append(coords)
    if not line_geoms:
        raise ValueError("Could not extract line geometries from overpass data")
    geometry: Dict[str, Any]
    if len(line_geoms) == 1:
        geometry = {"type": "LineString", "coordinates": line_geoms[0]}
    else:
        geometry = {"type": "MultiLineString", "coordinates": line_geoms}
    return {"type": "Feature", "properties": {"source": os.path.basename(path)}, "geometry": geometry}


@time_debug("Load GADM-like data")
def load_gadm_like(key: str, find_in_gadm: Optional[List[str]] = None) -> Dict[str, Any]:
    """Load GADM geometry by key like 'IND' or 'IND.31' or deeper.

    - If key has no dot: open gadm41_<ISO>_0.json and return its FeatureCollection
      as a single unified geometry FeatureCollection (caller will union).
    - If key has dots: level = number of dots, open gadm41_<ISO>_<level>.json and
      filter features whose GID_<level> startswith the prefix (without any trailing underscore).
    Returns a FeatureCollection containing matching features.
    
    Args:
        key: GADM key (e.g., "IND", "IND.31", "IND.31.1")
        find_in_gadm: Optional list of country codes to search in if key is not found in its own file
        
    Returns:
        GeoJSON FeatureCollection
        
    Raises:
        ValueError: If key format is invalid
        FileNotFoundError: If GADM file doesn't exist
    """
    if not key or len(key) < 3:
        raise ValueError("Invalid GADM key")
    parts = key.split('.')
    iso3 = parts[0]
    level = 0 if len(parts) == 1 else len(parts) - 1
    
    # Try to load from the key's own file first
    path = os.path.join(GADM_DIR, f"gadm41_{iso3}_{level}.json")
    if os.path.exists(path):
        fc = _read_json(path)
        if fc.get("type") != "FeatureCollection":
            raise ValueError(f"Expected FeatureCollection in {path}")
        if level == 0:
            return fc
        prefix = '.'.join(parts[:level+1])
        gid_key = f"GID_{level}"
        features = []
        for feat in fc.get("features", []):
            props = feat.get("properties", {}) or {}
            gid = str(props.get(gid_key, ""))
            # Use exact prefix matching with boundary check
            if gid.startswith(prefix) and (len(gid) == len(prefix) or gid[len(prefix)] in ['.', '_']):
                features.append(feat)
        return {"type": "FeatureCollection", "features": features}
    
    # If not found, search in provided or computed find_in_gadm
    if find_in_gadm is None:
        find_in_gadm = _compute_find_in_gadm_default(key)
    if find_in_gadm:
        for country_code in find_in_gadm:
            search_path = os.path.join(GADM_DIR, f"gadm41_{country_code}_{level}.json")
            if os.path.exists(search_path):
                fc = _read_json(search_path)
                if fc.get("type") != "FeatureCollection":
                    continue
                if level == 0:
                    # For level 0, return all features from the country file
                    return fc
                prefix = '.'.join(parts[:level+1])
                gid_key = f"GID_{level}"
                features = []
                for feat in fc.get("features", []):
                    props = feat.get("properties", {}) or {}
                    gid = str(props.get(gid_key, ""))
                    # Use exact prefix matching with boundary check
                    if gid.startswith(prefix) and (len(gid) == len(prefix) or gid[len(prefix)] in ['.', '_']):
                        features.append(feat)
                if features:  # If we found features, return them
                    return {"type": "FeatureCollection", "features": features}
    
    # If still not found, raise the original error
    raise FileNotFoundError(f"GADM file not found: {path}")


@time_debug("Load Natural Earth-like data")
def load_naturalearth_like(ne_id: str) -> Dict[str, Any]:
    """Load Natural Earth feature as GeoJSON Feature.
    
    For compatibility with Territory.from_naturalearth, return Feature.
    
    Args:
        ne_id: Natural Earth feature ID
        
    Returns:
        GeoJSON Feature object
    """
    return naturalearth(ne_id)
