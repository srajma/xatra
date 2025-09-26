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
from typing import Any, Dict, List, Optional, Tuple

from shapely.geometry import shape, mapping
from shapely.ops import unary_union


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
        return shape(geojson["geometry"]) if geojson.get("geometry") else None
    if t == "FeatureCollection":
        geoms = [shape(f["geometry"]) for f in geojson.get("features", []) if f.get("geometry")]
        return unary_union(geoms) if geoms else None
    return shape(geojson)


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
        flags_serialized: List of flag dictionaries with geometry and period info
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
            geoms = [_to_shape(it.get("geometry")) for it in items if it.get("geometry") is not None]
            geom = unary_union([g for g in geoms if g is not None]) if geoms else None
            out.append({
                "label": label,
                "geometry": mapping(geom) if geom is not None else None,
                "note": "; ".join([it.get("note") for it in items if it.get("note")]) or None,
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
            geoms = [_to_shape(a.get("geometry")) for a in active if a.get("geometry") is not None]
            geom = unary_union([g for g in geoms if g is not None]) if geoms else None
            snapshot_flags.append({
                "label": label,
                "geometry": mapping(geom) if geom is not None else None,
                "note": "; ".join(notes) or None,
            })
        snapshots.append({"year": year, "flags": snapshot_flags})

    return {"mode": "dynamic", "breakpoints": breakpoints, "snapshots": snapshots}


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
