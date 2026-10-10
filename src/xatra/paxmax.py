"""
Xatra Pax-Max Aggregation Module

This module implements the pax-max aggregation method for creating stable periods
in dynamic maps. The pax-max method groups flags with the same label over time
and creates stable periods where the territory remains unchanged, reducing the
number of map updates needed for smooth visualization.

The algorithm finds the maximum extent of each flag's territory over time and
creates stable periods where the territory remains constant.
"""

from __future__ import annotations

import math
from collections import defaultdict
from typing import Any, Dict, List, Optional

from shapely.geometry import shape, mapping, Point, Polygon, MultiPolygon, GeometryCollection
from shapely.ops import unary_union

from .debug_utils import time_debug
from .territory import Territory


@time_debug("Shapely shape conversion")
def _shape_wrapper(geojson_geometry):
    """Wrapper for shapely.geometry.shape with time debugging."""
    return shape(geojson_geometry)


@time_debug("Shapely mapping conversion")
def _mapping_wrapper(geometry):
    """Wrapper for shapely.geometry.mapping with time debugging."""
    from shapely.geometry import mapping
    return mapping(geometry)


@time_debug("Shapely unary union")
def _unary_union_wrapper(geometries):
    """Wrapper for shapely.ops.unary_union with time debugging."""
    if not geometries:
        return None
    # print(f"DEBUG: Unioning {len(geometries)} geometries...")
    return unary_union(geometries)


@time_debug("Compute centroid")
def _compute_centroid_for_geometry(geometry: Dict[str, Any]) -> Optional[List[float]]:
    """Compute a label anchor for a GeoJSON (Multi)Polygon.

    Works on the largest part of the territory (so an empire with island
    possessions is labelled on its mainland), in a locally equal-scaled
    plane (longitude shrunk by cos(latitude)) so distances match what the
    reader sees. Among interior points with comfortable room around them
    (at least half the room at the pole of inaccessibility), it picks the
    one closest to the area centroid: labels sit in the visual middle of the
    territory, yet never on a sliver or outside a crescent/L-shaped region.

    Returns:
        [latitude, longitude] or None if invalid
    """
    if geometry is None or geometry.get("type") not in ["Polygon", "MultiPolygon"]:
        return None
    try:
        import numpy as np
        import shapely
        from shapely import affinity
        from shapely.ops import polylabel

        geom = shape(geometry)
        if geom.is_empty:
            return None
        parts = list(geom.geoms) if isinstance(geom, MultiPolygon) else [geom]
        main = max(parts, key=lambda g: g.area)
        if main.area <= 0:
            return _area_weighted_centroid(geometry)
        kx = max(math.cos(math.radians(main.centroid.y)), 0.05)
        plane = affinity.scale(main, xfact=kx, yfact=1.0, origin=(0, 0))
        minx, miny, maxx, maxy = plane.bounds
        size = max(maxx - minx, maxy - miny)
        simple = plane.simplify(size / 400, preserve_topology=True)
        if simple.is_empty or not simple.is_valid:
            simple = plane
        pole = polylabel(simple, tolerance=max(size / 300, 1e-6))
        boundary = simple.boundary
        pole_depth = boundary.distance(pole)
        centroid = simple.centroid
        best = pole
        if pole_depth > 0:
            n = 48
            xs, ys = np.meshgrid(np.linspace(minx, maxx, n), np.linspace(miny, maxy, n))
            xs, ys = xs.ravel(), ys.ravel()
            inside = shapely.contains_xy(simple, xs, ys)
            xs, ys = xs[inside], ys[inside]
            centroid_inside = simple.contains(centroid)
            candidates = list(zip(xs, ys)) + ([(centroid.x, centroid.y)] if centroid_inside else [])
            points = shapely.points(np.array(candidates)) if candidates else []
            depth = shapely.distance(boundary, points) if candidates else np.array([])
            ok = depth >= 0.5 * pole_depth
            if centroid_inside and ok[-1]:
                best = centroid
            elif ok.any():
                cand = np.array(candidates)[ok]
                d2 = (cand[:, 0] - centroid.x) ** 2 + (cand[:, 1] - centroid.y) ** 2
                x, y = cand[int(np.argmin(d2))]
                best = Point(x, y)
        return [best.y, best.x / kx]
    except Exception:
        return _area_weighted_centroid(geometry)


def _area_weighted_centroid(geometry: Dict[str, Any]) -> Optional[List[float]]:
    """Compute centroid for a GeoJSON geometry.
    
    Args:
        geometry: GeoJSON geometry object
        
    Returns:
        [latitude, longitude] centroid coordinates or None if invalid
    """
    if geometry is None or geometry.get("type") not in ["Polygon", "MultiPolygon"]:
        return None
        
    if geometry["type"] == "Polygon":
        coords = geometry["coordinates"][0]  # Exterior ring
        if len(coords) < 3:
            return None
            
        area = 0
        cx = cy = 0
        
        for i in range(len(coords) - 1):
            x1, y1 = coords[i]
            x2, y2 = coords[i + 1]
            
            cross = x1 * y2 - x2 * y1
            area += cross
            cx += (x1 + x2) * cross
            cy += (y1 + y2) * cross
            
        area *= 0.5
        if abs(area) < 1e-10:
            return None
            
        cx /= (6 * area)
        cy /= (6 * area)
        
        return [cy, cx]  # [lat, lng]
        
    elif geometry["type"] == "MultiPolygon":
        total_area = 0
        weighted_x = weighted_y = 0
        
        for polygon in geometry["coordinates"]:
            coords = polygon[0]  # Exterior ring
            if len(coords) < 3:
                continue
                
            area = 0
            cx = cy = 0
            
            for i in range(len(coords) - 1):
                x1, y1 = coords[i]
                x2, y2 = coords[i + 1]
                
                cross = x1 * y2 - x2 * y1
                area += cross
                cx += (x1 + x2) * cross
                cy += (y1 + y2) * cross
                
            area *= 0.5
            if abs(area) > 1e-10:
                cx /= (6 * area)
                cy /= (6 * area)
                
                weighted_x += cx * abs(area)
                weighted_y += cy * abs(area)
                total_area += abs(area)
                
        if total_area < 1e-10:
            return None
            
        return [weighted_y / total_area, weighted_x / total_area]  # [lat, lng]
        
    return None


@time_debug("Convert GeoJSON to Shapely geometry")
def _to_shape(geojson):
    """Convert GeoJSON to Shapely geometry.
    
    Args:
        geojson: GeoJSON object
        
    Returns:
        Shapely geometry or None if invalid
    """
    if geojson is None:
        return None
    t = geojson.get("type")
    if t == "Feature":
        return _shape_wrapper(geojson["geometry"]) if geojson.get("geometry") else None
    if t == "FeatureCollection":
        geoms = [_shape_wrapper(f["geometry"]) for f in geojson.get("features", []) if f.get("geometry")]
        return _unary_union_wrapper(geoms) if geoms else None
    return _shape_wrapper(geojson)


def _extract_polygon_parts(geom):
    """Recursively collect Polygon parts from any Shapely geometry."""
    if geom is None or geom.is_empty:
        return []

    if isinstance(geom, Polygon):
        return [geom]

    if isinstance(geom, MultiPolygon):
        return [g for g in geom.geoms if g is not None and not g.is_empty]

    if isinstance(geom, GeometryCollection):
        parts = []
        for subgeom in geom.geoms:
            parts.extend(_extract_polygon_parts(subgeom))
        return parts

    return []


# Interior rings smaller than this (in square degrees, ~20 km² at Indian
# latitudes), or thin slivers, are seams between imperfectly matching source
# polygons rather than real enclaves; they show up as specks once flags have borders.
_MIN_HOLE_AREA = 0.002
_MIN_HOLE_COMPACTNESS = 0.05


def _is_artifact_hole(ring) -> bool:
    hole = Polygon(ring)
    area = hole.area
    if area < _MIN_HOLE_AREA:
        return True
    perimeter = hole.length
    compactness = 4 * math.pi * area / (perimeter * perimeter) if perimeter > 0 else 0
    return compactness < _MIN_HOLE_COMPACTNESS


def _drop_artifact_holes(poly: Polygon) -> Polygon:
    if not poly.interiors:
        return poly
    kept = [ring for ring in poly.interiors if not _is_artifact_hole(ring)]
    if len(kept) == len(poly.interiors):
        return poly
    return Polygon(poly.exterior, kept)


def _polygonal_only(geom):
    """Keep only polygonal components of a geometry for area-based flag rendering."""
    if geom is None or geom.is_empty:
        return None

    parts = _extract_polygon_parts(geom)
    if not parts:
        return None
    parts = [_drop_artifact_holes(p) for p in parts]
    if len(parts) == 1:
        return parts[0]
    return MultiPolygon(parts)


@time_debug("Paxmax aggregation")
def paxmax_aggregate(flags_serialized: List[Dict[str, Any]], earliest_start: Optional[int] = None) -> Dict[str, Any]:
    """Aggregate flags using the pax-max method for dynamic maps.
    
    The pax-max method groups flags with the same label over time and creates
    stable periods where the territory remains unchanged. This reduces the
    number of map updates needed for smooth visualization.

    For static maps (those where all flag periods are None), this amounts to just 
    taking the union of all flags with the same label so we have a single item for 
    each flag label. For dynamic maps -- we create an entry for each "stable period" 
    of a Flag label. i.e. collect the breakpoint years for each label (the start 
    and end years of every flag with a particular label), and create unions for the 
    flags active at each breakpoint year (a flag is considered active at its start year 
    but not its end year)
    
    Args:
        flags_serialized: List of flag dictionaries with territory or geometry and period info
        earliest_start: Optional earliest start year to ensure initial snapshot
        
    Returns:
        Dictionary with mode ("static" or "dynamic"), flags, and snapshots
    """
    # Group by label
    by_label: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for f in flags_serialized:
        by_label[f["label"]].append(f)

    # Determine if dynamic
    dynamic = any(f.get("period") is not None for f in flags_serialized)

    if not dynamic:
        # Simple union per label.
        # Keep static mode geometry externalized too, so render payloads stay compact.
        out = []
        geometry_library: Dict[str, Any] = {}
        for label, items in by_label.items():
            # Check if we have territories or geometries
            territories = [it.get("territory") for it in items if isinstance(it.get("territory"), Territory)]
            geometries = [it.get("geometry") for it in items if it.get("geometry") is not None]

            if territories:
                # Use territory union (more efficient with caching)
                union_territory = Territory.union_territories(territories)
                geom = union_territory.to_geometry()
                geom = _polygonal_only(geom)
                geom_dict = mapping(geom) if geom is not None else None
                centroid = _compute_centroid_for_geometry(geom_dict) if geom_dict else None
            elif geometries:
                # Fallback to geometry union (legacy support)
                geoms = [_to_shape(geom) for geom in geometries]
                geom = _unary_union_wrapper([g for g in geoms if g is not None]) if geoms else None
                geom = _polygonal_only(geom)
                geom_dict = _mapping_wrapper(geom) if geom is not None else None
                centroid = _compute_centroid_for_geometry(geom_dict) if geom_dict else None
            else:
                geom_dict = None
                centroid = None

            if geom_dict:
                geom_id = f"g{len(geometry_library)}"
                geometry_library[geom_id] = geom_dict
            else:
                geom_id = None

            # Preserve color from the first item (they should all have the same color for the same label)
            color = items[0].get("color") if items else None
            # Collect all unique classes from items with the same label
            all_classes = []
            for it in items:
                classes = it.get("classes")
                if isinstance(classes, str) and classes:
                    all_classes.extend(classes.split())
            unique_classes = " ".join(sorted(set(all_classes))) if all_classes else None

            # Preserve hierarchy metadata from the first item.
            # Display label intentionally uses last declared item for this label.
            parent = items[0].get("parent") if items else None
            type_ = items[0].get("type") if items else None
            root_parent = items[0].get("root_parent") if items else None
            root_parent_color = items[0].get("root_parent_color") if items else None
            display_label = (items[-1].get("display_label") or label) if items else label
            vassal_depth = items[0].get("vassal_depth", 0) if items else 0

            out.append({
                "label": label,
                "display_label": display_label,
                "geom_id": geom_id,
                "centroid": centroid,
                "note": "; ".join([str(it.get("note")) for it in items if it.get("note")]) or None,
                "color": color,
                "classes": unique_classes,
                "parent": parent,
                "type": type_,
                "root_parent": root_parent,
                "root_parent_color": root_parent_color,
                "vassal_depth": vassal_depth,
            })
        return {"mode": "static", "flags": out, "geometry_library": geometry_library}

    # Dynamic: compute breakpoints and stable periods
    breakpoints: List[int] = []
    for items in by_label.values():
        for it in items:
            per = it.get("period")
            if per is not None:
                breakpoints.extend([int(per[0]), int(per[1])])
    breakpoints = sorted(set(breakpoints))
    
    # Add the earliest start year to ensure we have a snapshot at the beginning
    if earliest_start is not None and earliest_start not in breakpoints:
        breakpoints.insert(0, earliest_start)

    # For each label and each breakpoint year, compute union of active geometries
    snapshots: List[Dict[str, Any]] = []
    
    # Global geometry registry for this aggregation
    geometry_library: Dict[str, Any] = {}
    
    # Local cache to avoid redundant processing of the same label/active-set
    # within the same aggregation run.
    processed_cache: Dict[tuple, Dict[str, Any]] = {}
    
    # Cache for geometry to dict mapping (for non-Territory items)
    mapping_cache: Dict[int, Dict[str, Any]] = {}

    for year in breakpoints:
        snapshot_flags = []
        for label, items in by_label.items():
            active = []
            active_indices: List[int] = []
            notes = []
            for idx, it in enumerate(items):
                per = it.get("period")
                if per is None:
                    active.append(it)
                    active_indices.append(idx)
                    if it.get("note"):
                        notes.append(it.get("note"))
                else:
                    start, end = int(per[0]), int(per[1])
                    if year >= start and year < end:
                        active.append(it)
                        active_indices.append(idx)
                        if it.get("note"):
                            notes.append(it.get("note"))
            if not active:
                continue

            # Cache by (label, active item indices). This avoids repeated string
            # sorting/hashing for static labels across many breakpoint years.
            cache_key = (label, tuple(active_indices))
            cached_flag = processed_cache.get(cache_key)
            if cached_flag is not None:
                snapshot_flags.append(dict(cached_flag))
                continue
            else:
                # Check if we have territories or geometries
                territories = [a.get("territory") for a in active if isinstance(a.get("territory"), Territory)]
                geometries = [a.get("geometry") for a in active if a.get("geometry") is not None]
                
                if territories:
                    # Use territory union (more efficient with caching)
                    union_territory = Territory.union_territories(territories)
                    geom = _polygonal_only(union_territory.to_geometry())
                    geom_dict = mapping(geom) if geom is not None else None
                    centroid = _compute_centroid_for_geometry(geom_dict) if geom_dict else None
                elif geometries:
                    # Fallback to geometry union (legacy support)
                    geoms = [_to_shape(geom) for geom in geometries]
                    geom = _unary_union_wrapper([g for g in geoms if g is not None]) if geoms else None
                    geom = _polygonal_only(geom)
                    
                    # Cache the mapping conversion
                    if geom is not None:
                        gid = id(geom)
                        if gid not in mapping_cache:
                            mapping_cache[gid] = mapping(geom)
                        geom_dict = mapping_cache[gid]
                    else:
                        geom_dict = None
                        
                    centroid = _compute_centroid_for_geometry(geom_dict) if geom_dict else None
                else:
                    geom_dict = None
                    centroid = None

                if geom_dict:
                    # Geometry ids only need to be unique within this export payload.
                    geom_id = f"g{len(geometry_library)}"
                    geometry_library[geom_id] = geom_dict
                else:
                    geom_id = None

            # Preserve color from the first active item
            color = active[0].get("color") if active else None
            # Collect all unique classes from active items
            all_classes = []
            for it in active:
                classes = it.get("classes")
                if isinstance(classes, str) and classes:
                    all_classes.extend(classes.split())
            unique_classes = " ".join(sorted(set(all_classes))) if all_classes else None
            
            # Preserve hierarchy metadata from the first active item.
            # Display label intentionally uses last declared active item for this label.
            parent = active[0].get("parent") if active else None
            type_ = active[0].get("type") if active else None
            root_parent = active[0].get("root_parent") if active else None
            root_parent_color = active[0].get("root_parent_color") if active else None
            display_label = (active[-1].get("display_label") or label) if active else label
            vassal_depth = active[0].get("vassal_depth", 0) if active else 0
            
            flag_payload = {
                "label": label,
                "display_label": display_label,
                "geom_id": geom_id,
                "centroid": centroid,
                "note": "; ".join(notes) or None,
                "color": color,
                "classes": unique_classes,
                "parent": parent,
                "type": type_,
                "root_parent": root_parent,
                "root_parent_color": root_parent_color,
                "vassal_depth": vassal_depth,
            }
            processed_cache[cache_key] = flag_payload
            snapshot_flags.append(dict(flag_payload))
        snapshots.append({"year": year, "flags": snapshot_flags})

    return {
        "mode": "dynamic",
        "breakpoints": breakpoints,
        "snapshots": snapshots,
        "geometry_library": geometry_library
    }


@time_debug("Filter by period")
def filter_by_period(items: List[Dict[str, Any]], year: int) -> List[Dict[str, Any]]:
    """Filter items by period for a given year.
    
    Args:
        items: List of items with optional period information
        year: Year to filter by
        
    Returns:
        List of items that are active during the given year
    """
    filtered = []
    for item in items:
        period = item.get("period")
        if period is None:
            # No period means always visible
            filtered.append(item)
        else:
            start, end = int(period[0]), int(period[1])
            if year >= start and year < end:
                filtered.append(item)
    return filtered
