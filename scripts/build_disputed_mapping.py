#!/usr/bin/env python3

import os
import re
import json
import csv
from typing import Dict, List, Tuple, Set


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GADM_DIR = os.path.join(PROJECT_ROOT, "data", "gadm")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "data/disputed_territories")


FILENAME_RE = re.compile(r"^gadm41_([A-Z0-9]{3})_([0-4])\.json$")
GID_VALUE_RE = re.compile(r"^(?P<root>(?:[A-Z0-9]{3}|Z\d{2}))(?:\..+)?$")


def iter_gadm_files() -> List[Tuple[str, str, int]]:
    files: List[Tuple[str, str, int]] = []
    for name in os.listdir(GADM_DIR):
        match = FILENAME_RE.match(name)
        if not match:
            continue
        country = match.group(1)
        level = int(match.group(2))
        files.append((name, country, level))
    return sorted(files)


def extract_gid_values(feature_props: Dict[str, object]) -> Set[str]:
    roots: Set[str] = set()
    # Consider all keys that look like GID_0, GID_1, ... up to 4
    for key, value in feature_props.items():
        if not isinstance(value, str):
            continue
        if not key.startswith("GID_"):
            continue
        m = GID_VALUE_RE.match(value)
        if not m:
            continue
        roots.add(m.group("root"))
    return roots


def load_json(path: str) -> Dict[str, object]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_mapping() -> Tuple[List[Dict[str, object]], Dict[str, List[Dict[str, object]]]]:
    rows: List[Dict[str, object]] = []
    aggregated: Dict[str, List[Dict[str, object]]] = {}

    for filename, file_country, level in iter_gadm_files():
        path = os.path.join(GADM_DIR, filename)
        try:
            doc = load_json(path)
        except Exception as e:
            # Skip unreadable files
            continue

        features = doc.get("features", [])
        for feat in features:
            props = feat.get("properties", {}) if isinstance(feat, dict) else {}
            roots = extract_gid_values(props)
            for gid_root in roots:
                # Only include disputed blocks that look like Z followed by digits (e.g., Z01, Z06)
                is_disputed_root = bool(re.match(r"^Z\d+$", gid_root))
                if not is_disputed_root:
                    continue

                row = {
                    "gid_root": gid_root,
                    "file_country": file_country,
                    "file": filename,
                    "level": level,
                }
                rows.append(row)

                aggregated.setdefault(gid_root, [])
                # Avoid duplicate entries for same gid_root/file_country/level
                key_tuple = (file_country, level, filename)
                if not any(
                    (r.get("file_country"), r.get("level"), r.get("file")) == key_tuple
                    for r in aggregated[gid_root]
                ):
                    aggregated[gid_root].append({
                        "file_country": file_country,
                        "level": level,
                        "file": filename,
                    })

    # Sort outputs for reproducibility
    rows.sort(key=lambda r: (r["gid_root"], r["file_country"], r["level"], r["file"]))
    for gid_root in aggregated:
        aggregated[gid_root].sort(key=lambda r: (r["file_country"], r["level"], r["file"]))

    return rows, aggregated


def write_csv(rows: List[Dict[str, object]], path: str) -> None:
    fieldnames = ["gid_root", "file_country", "level", "file"]
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def write_json(obj: object, path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def write_markdown_table(aggregated: Dict[str, List[Dict[str, object]]], path: str) -> None:
    # Create a concise table of gid_root to countries/files
    lines: List[str] = []
    lines.append("| Disputed GID Root | Appears In (Country → Files) |")
    lines.append("|---|---|")
    for gid_root in sorted(aggregated.keys()):
        entries = aggregated[gid_root]
        # Group by country
        by_country: Dict[str, List[str]] = {}
        for e in entries:
            by_country.setdefault(e["file_country"], []).append(e["file"])
        # Build readable string
        parts: List[str] = []
        for country in sorted(by_country.keys()):
            files = sorted(set(by_country[country]))
            # show unique levels present
            parts.append(f"{country} → {', '.join(files)}")
        lines.append(f"| {gid_root} | {'; '.join(parts)} |")

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def main() -> None:
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    rows, aggregated = build_mapping()

    csv_path = os.path.join(OUTPUT_DIR, "disputed_mapping.csv")
    json_path = os.path.join(OUTPUT_DIR, "disputed_mapping.json")
    md_path = os.path.join(OUTPUT_DIR, "disputed_mapping.md")

    write_csv(rows, csv_path)
    write_json(aggregated, json_path)
    write_markdown_table(aggregated, md_path)

    print(f"Wrote: {csv_path}")
    print(f"Wrote: {json_path}")
    print(f"Wrote: {md_path}")


if __name__ == "__main__":
    main()

