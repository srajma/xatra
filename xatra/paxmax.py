from __future__ import annotations

from collections import defaultdict
from typing import Any, Dict, List, Optional, Tuple

from shapely.geometry import shape, mapping
from shapely.ops import unary_union


def _to_shape(geojson):
    if geojson is None:
        return None
    t = geojson.get("type")
    if t == "Feature":
        return shape(geojson["geometry"]) if geojson.get("geometry") else None
    if t == "FeatureCollection":
        geoms = [shape(f["geometry"]) for f in geojson.get("features", []) if f.get("geometry")]
        return unary_union(geoms) if geoms else None
    return shape(geojson)


def paxmax_aggregate(flags_serialized: List[Dict[str, Any]]) -> Dict[str, Any]:
    print("DEBUG: paxmax_aggregate called with flags:", len(flags_serialized))
    for i, f in enumerate(flags_serialized):
        print(f"  Flag {i}: {f['label']} period={f.get('period')}")
    
    # Group by label
    by_label: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for f in flags_serialized:
        by_label[f["label"]].append(f)

    print("DEBUG: Grouped by label:", {k: len(v) for k, v in by_label.items()})

    # Determine if dynamic
    dynamic = any(f.get("period") is not None for f in flags_serialized)
    print(f"DEBUG: Dynamic mode: {dynamic}")

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
    print(f"DEBUG: Flag breakpoints: {breakpoints}")

    # For each label and each breakpoint year, compute union of active geometries
    snapshots: List[Dict[str, Any]] = []
    for year in breakpoints:
        print(f"DEBUG: Processing year {year}")
        snapshot_flags = []
        for label, items in by_label.items():
            active = []
            notes = []
            for it in items:
                per = it.get("period")
                if per is None:
                    print(f"  {label}: No period, always active")
                    active.append(it)
                    if it.get("note"):
                        notes.append(it.get("note"))
                else:
                    start, end = int(per[0]), int(per[1])
                    is_active = year >= start and year < end
                    print(f"  {label}: period=[{start}, {end}), year={year}, active={is_active}")
                    if is_active:
                        active.append(it)
                        if it.get("note"):
                            notes.append(it.get("note"))
            if not active:
                print(f"  {label}: No active items for year {year}")
                continue
            print(f"  {label}: {len(active)} active items for year {year}")
            geoms = [_to_shape(a.get("geometry")) for a in active if a.get("geometry") is not None]
            geom = unary_union([g for g in geoms if g is not None]) if geoms else None
            snapshot_flags.append({
                "label": label,
                "geometry": mapping(geom) if geom is not None else None,
                "note": "; ".join(notes) or None,
            })
        snapshots.append({"year": year, "flags": snapshot_flags})
        print(f"DEBUG: Year {year} has {len(snapshot_flags)} flags")

    print(f"DEBUG: Final snapshots: {len(snapshots)} snapshots")
    for s in snapshots:
        print(f"  Year {s['year']}: {[f['label'] for f in s['flags']]}")
    
    return {"mode": "dynamic", "breakpoints": breakpoints, "snapshots": snapshots}


def filter_by_period(items: List[Dict[str, Any]], year: int) -> List[Dict[str, Any]]:
    """Filter items by period for a given year."""
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
