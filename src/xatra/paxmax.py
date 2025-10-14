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

from collections import defaultdict
from typing import Any, Dict, List, Optional

from shapely.geometry import shape, mapping
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
    return unary_union(geometries)


@time_debug("Compute centroid")
def _compute_centroid_for_geometry(geometry: Dict[str, Any]) -> Optional[List[float]]:
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


@time_debug("Paxmax aggregation")
def paxmax_aggregate(flags_serialized: List[Dict[str, Any]], earliest_start: int = None) -> Dict[str, Any]:
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
        # Simple union per label
        out = []
        for label, items in by_label.items():
            # Check if we have territories or geometries
            territories = [it.get("territory") for it in items if it.get("territory") is not None]
            geometries = [it.get("geometry") for it in items if it.get("geometry") is not None]
            
            if territories:
                # Use territory union (more efficient with caching)
                union_territory = Territory.union_territories(territories)
                geom = union_territory.to_geometry()
                geom_dict = mapping(geom) if geom is not None else None
                centroid = _compute_centroid_for_geometry(geom_dict) if geom_dict else None
            elif geometries:
                # Fallback to geometry union (legacy support)
                geoms = [_to_shape(geom) for geom in geometries]
                geom = _unary_union_wrapper([g for g in geoms if g is not None]) if geoms else None
                geom_dict = _mapping_wrapper(geom) if geom is not None else None
                centroid = _compute_centroid_for_geometry(geom_dict) if geom_dict else None
            else:
                geom_dict = None
                centroid = None
            
            # Preserve color from the first item (they should all have the same color for the same label)
            color = items[0].get("color") if items else None
            # Collect all unique classes from items with the same label
            all_classes = []
            for it in items:
                if it.get("classes"):
                    all_classes.extend(it.get("classes").split())
            unique_classes = " ".join(sorted(set(all_classes))) if all_classes else None
            
            out.append({
                "label": label,
                "geometry": geom_dict,
                "centroid": centroid,
                "note": "; ".join([it.get("note") for it in items if it.get("note")]) or None,
                "color": color,
                "classes": unique_classes,
            })
        return {"mode": "static", "flags": out}

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
    for year in breakpoints:
        snapshot_flags = []
        for label, items in by_label.items():
            active = []
            notes = []
            for it in items:
                per = it.get("period")
                if per is None:
                    active.append(it)
                    if it.get("note"):
                        notes.append(it.get("note"))
                else:
                    start, end = int(per[0]), int(per[1])
                    if year >= start and year < end:
                        active.append(it)
                        if it.get("note"):
                            notes.append(it.get("note"))
            if not active:
                continue
            
            # Check if we have territories or geometries
            territories = [a.get("territory") for a in active if a.get("territory") is not None]
            geometries = [a.get("geometry") for a in active if a.get("geometry") is not None]
            
            if territories:
                # Use territory union (more efficient with caching)
                union_territory = Territory.union_territories(territories)
                geom = union_territory.to_geometry()
                geom_dict = mapping(geom) if geom is not None else None
                centroid = _compute_centroid_for_geometry(geom_dict) if geom_dict else None
            elif geometries:
                # Fallback to geometry union (legacy support)
                geoms = [_to_shape(geom) for geom in geometries]
                geom = _unary_union_wrapper([g for g in geoms if g is not None]) if geoms else None
                geom_dict = _mapping_wrapper(geom) if geom is not None else None
                centroid = _compute_centroid_for_geometry(geom_dict) if geom_dict else None
            else:
                geom_dict = None
                centroid = None
            
            # Preserve color from the first active item
            color = active[0].get("color") if active else None
            # Collect all unique classes from active items
            all_classes = []
            for it in active:
                if it.get("classes"):
                    all_classes.extend(it.get("classes").split())
            unique_classes = " ".join(sorted(set(all_classes))) if all_classes else None
            
            snapshot_flags.append({
                "label": label,
                "geometry": geom_dict,
                "centroid": centroid,
                "note": "; ".join(notes) or None,
                "color": color,
                "classes": unique_classes,
            })
        snapshots.append({"year": year, "flags": snapshot_flags})

    return {"mode": "dynamic", "breakpoints": breakpoints, "snapshots": snapshots}


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
