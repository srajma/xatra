#!/usr/bin/env python3
"""
Generate topology-safe simplified copies of GADM files.

This script builds simplified datasets under:
  ~/.xatra/data/gadm_simplified/tol_<tolerance-token>/gadm41_<ISO>_<level>.json

Important properties:
1. Subdivisions at the same level continue to fit together (coverage simplification).
2. Level n geometries are derived from unions of simplified level n+1 geometries,
   so parent/child boundaries are exactly consistent.
"""

from __future__ import annotations

import argparse
import copy
import json
import re
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

import shapely
from shapely.geometry import GeometryCollection, MultiPolygon, Polygon, mapping, shape
from shapely.ops import unary_union

from .loaders import GADM_DIR, GADM_SIMPLIFIED_DIR, _format_simplify_tolerance


GADM_FILE_RE = re.compile(r"^gadm41_([A-Z0-9]{3})_(\d+)\.json$")
DEFAULT_TOLERANCES = [0.01, 0.025, 0.05]


def _read_json(path: Path) -> Dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _write_json(path: Path, obj: Dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, separators=(",", ":"))


def _discover_gadm_files(gadm_dir: Path) -> Dict[str, Dict[int, Path]]:
    countries: Dict[str, Dict[int, Path]] = {}
    for path in sorted(gadm_dir.glob("gadm41_*_*.json")):
        m = GADM_FILE_RE.match(path.name)
        if not m:
            continue
        iso3, level_s = m.groups()
        level = int(level_s)
        countries.setdefault(iso3, {})[level] = path
    return countries


def _dissolve_by_gid(
    source_features: List[Dict],
    simplified_geometries: Iterable,
    levels: List[int],
) -> Dict[int, Dict[str, object]]:
    grouped: Dict[int, Dict[str, List[object]]] = {level: {} for level in levels}

    for feature, simp_geom in zip(source_features, simplified_geometries):
        props = feature.get("properties", {}) or {}
        for level in levels:
            gid = props.get(f"GID_{level}")
            if gid is None:
                continue
            gid_s = str(gid)
            grouped[level].setdefault(gid_s, []).append(simp_geom)

    dissolved: Dict[int, Dict[str, object]] = {level: {} for level in levels}
    for level in levels:
        for gid, geoms in grouped[level].items():
            if not geoms:
                continue
            dissolved[level][gid] = geoms[0] if len(geoms) == 1 else unary_union(geoms)
    return dissolved


def _polygonal_only(geom):
    """Return polygonal components only, or an empty Polygon if none remain."""
    if geom is None:
        return Polygon()
    if isinstance(geom, Polygon):
        return geom
    if isinstance(geom, MultiPolygon):
        return geom
    if isinstance(geom, GeometryCollection):
        polys = []
        for g in geom.geoms:
            pg = _polygonal_only(g)
            if pg is None or pg.is_empty:
                continue
            if isinstance(pg, Polygon):
                polys.append(pg)
            elif isinstance(pg, MultiPolygon):
                polys.extend(list(pg.geoms))
        if not polys:
            return Polygon()
        return polys[0] if len(polys) == 1 else MultiPolygon(polys)
    return Polygon()


def _sanitize_for_coverage(geom):
    """Coerce geometry to valid polygonal geometry for coverage operations."""
    if geom is None:
        return Polygon()
    g = geom
    if not g.is_valid:
        g = shapely.make_valid(g)
    g = _polygonal_only(g)
    if g is None:
        return Polygon()
    if not g.is_valid:
        try:
            g = g.buffer(0)
        except Exception:
            return Polygon()
        g = _polygonal_only(g)
    return g if g is not None else Polygon()


def _build_simplified_country(
    iso3: str,
    level_paths: Dict[int, Path],
    tolerance: float,
    out_root: Path,
) -> None:
    levels = sorted(level_paths)
    source_level = max(levels)

    level_data = {level: _read_json(path) for level, path in level_paths.items()}
    source_fc = level_data[source_level]
    source_features = source_fc.get("features", [])
    source_geoms = [shape(feat["geometry"]) for feat in source_features if feat.get("geometry")]

    if len(source_geoms) != len(source_features):
        raise ValueError(f"{iso3} level {source_level}: found features with null geometry")

    sanitized_source_geoms = [_sanitize_for_coverage(g) for g in source_geoms]
    try:
        simplified_source_geoms = shapely.coverage_simplify(sanitized_source_geoms, tolerance)
    except Exception as exc:
        print(f"    ! coverage_simplify failed for {iso3}: {exc}; falling back to per-feature simplify")
        simplified_source_geoms = [
            _sanitize_for_coverage(g).simplify(tolerance, preserve_topology=True)
            for g in sanitized_source_geoms
        ]
    dissolved = _dissolve_by_gid(source_features, simplified_source_geoms, levels)

    tol_token = _format_simplify_tolerance(tolerance)
    out_dir = out_root / f"tol_{tol_token}"

    for level in levels:
        in_fc = level_data[level]
        gid_key = f"GID_{level}"
        out_fc = copy.deepcopy(in_fc)
        out_features = []

        for feat in in_fc.get("features", []):
            props = feat.get("properties", {}) or {}
            gid = str(props.get(gid_key, ""))
            geom = dissolved[level].get(gid)
            if geom is None:
                # Rare fallback for unmatched feature ids.
                geom = _sanitize_for_coverage(shape(feat["geometry"])).simplify(
                    tolerance, preserve_topology=True
                )
            geom = _sanitize_for_coverage(geom)

            out_feat = copy.deepcopy(feat)
            out_feat["geometry"] = mapping(geom)
            out_features.append(out_feat)

        out_fc["features"] = out_features
        out_fc.setdefault("xatra_simplification", {})
        out_fc["xatra_simplification"] = {
            "tolerance": tolerance,
            "country": iso3,
            "level": level,
            "source_level": source_level,
            "method": "coverage_simplify + hierarchical dissolve",
        }

        out_path = out_dir / f"gadm41_{iso3}_{level}.json"
        _write_json(out_path, out_fc)


def build_simplified_gadm(
    tolerances: List[float],
    countries: List[str] | None = None,
    gadm_dir: Path | None = None,
    out_root: Path | None = None,
) -> None:
    gadm_path = Path(gadm_dir or GADM_DIR)
    out_path = Path(out_root or GADM_SIMPLIFIED_DIR)
    discovered = _discover_gadm_files(gadm_path)

    target_countries = sorted(discovered)
    if countries:
        wanted = {c.upper() for c in countries}
        target_countries = [c for c in target_countries if c in wanted]

    if not target_countries:
        raise ValueError("No matching GADM country files found")

    for tol in tolerances:
        tol_f = float(tol)
        if tol_f <= 0:
            raise ValueError(f"Invalid tolerance {tol_f}; expected > 0")
        print(f"[xatra-simplify-data] tolerance={tol_f}")
        for iso3 in target_countries:
            print(f"  - {iso3}")
            try:
                _build_simplified_country(iso3, discovered[iso3], tol_f, out_path)
            except Exception as exc:
                print(f"    ! failed {iso3}: {exc}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build topology-safe simplified copies of GADM data for xatra.",
    )
    parser.add_argument(
        "--tolerance",
        action="append",
        type=float,
        dest="tolerances",
        help="Simplification tolerance in degrees (repeatable). Default: 0.01, 0.025, 0.05",
    )
    parser.add_argument(
        "--country",
        action="append",
        dest="countries",
        help="ISO3 country code filter (repeatable), e.g. --country IND --country PAK",
    )
    parser.add_argument(
        "--gadm-dir",
        type=Path,
        default=Path(GADM_DIR),
        help=f"Input GADM directory (default: {GADM_DIR})",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path(GADM_SIMPLIFIED_DIR),
        help=f"Output simplified GADM root (default: {GADM_SIMPLIFIED_DIR})",
    )
    args = parser.parse_args()

    tolerances = args.tolerances if args.tolerances else DEFAULT_TOLERANCES
    build_simplified_gadm(
        tolerances=tolerances,
        countries=args.countries,
        gadm_dir=args.gadm_dir,
        out_root=args.out_dir,
    )


if __name__ == "__main__":
    main()
