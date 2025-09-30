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


def extract_highest_gid_root(feature_props: Dict[str, object]) -> str:
    """Extract the root from the highest-level GID in the feature properties."""
    # Find all GID_n keys and their values
    gid_entries = []
    for key, value in feature_props.items():
        if not isinstance(value, str):
            continue
        if not key.startswith("GID_"):
            continue
        try:
            level = int(key.split("_")[1])
            gid_entries.append((level, value))
        except (ValueError, IndexError):
            continue
    
    if not gid_entries:
        return ""
    
    # Get the highest level GID
    highest_level, highest_gid = max(gid_entries, key=lambda x: x[0])
    
    # Extract root from the highest GID
    m = GID_VALUE_RE.match(highest_gid)
    if not m:
        return ""
    
    return m.group("root")


def extract_highest_gid_value(feature_props: Dict[str, object]) -> str:
    """Extract the full highest-level GID value (e.g., 'Z01.14.5_1')."""
    gid_entries = []
    for key, value in feature_props.items():
        if not isinstance(value, str):
            continue
        if not key.startswith("GID_"):
            continue
        try:
            level = int(key.split("_")[1])
            gid_entries.append((level, value))
        except (ValueError, IndexError):
            continue
    if not gid_entries:
        return ""
    highest_level, highest_gid = max(gid_entries, key=lambda x: x[0])
    return highest_gid


def load_json(path: str) -> Dict[str, object]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_mapping() -> Tuple[List[Dict[str, object]], Dict[str, List[Dict[str, object]]], List[Dict[str, object]]]:
    rows: List[Dict[str, object]] = []
    aggregated: Dict[str, List[Dict[str, object]]] = {}
    disputed_gid_rows: List[Dict[str, object]] = []

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
            highest_gid_root = extract_highest_gid_root(props)
            highest_gid_value = extract_highest_gid_value(props)
            gid0 = str(props.get("GID_0", ""))
            
            if not highest_gid_root:
                continue
                
            # Only include entries where the highest GID doesn't match the file's country code
            if highest_gid_root == file_country:
                continue

            row = {
                "gid_root": highest_gid_root,
                "file_country": file_country,
                "file": filename,
                "level": level,
            }
            rows.append(row)

            aggregated.setdefault(highest_gid_root, [])
            # Avoid duplicate entries for same gid_root/file_country/level
            key_tuple = (file_country, level, filename)
            if not any(
                (r.get("file_country"), r.get("level"), r.get("file")) == key_tuple
                for r in aggregated[highest_gid_root]
            ):
                aggregated[highest_gid_root].append({
                    "file_country": file_country,
                    "level": level,
                    "file": filename,
                })

            # Also record the full highest-level GID for any feature whose GID_0 doesn't match file country
            if gid0 and gid0 != file_country:
                disputed_gid_rows.append({
                    "gid": highest_gid_value,
                    "gid_root": highest_gid_root,
                    "gid0": gid0,
                    "file_country": file_country,
                    "level": level,
                    "file": filename,
                })

    # Sort outputs for reproducibility
    rows.sort(key=lambda r: (r["gid_root"], r["file_country"], r["level"], r["file"]))
    for gid_root in aggregated:
        aggregated[gid_root].sort(key=lambda r: (r["file_country"], r["level"], r["file"]))

    return rows, aggregated, disputed_gid_rows


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


def write_disputed_gid_outputs(rows: List[Dict[str, object]], base_path_no_ext: str) -> None:
    """Write disputed GID rows to CSV, JSON, and Markdown table."""
    # CSV
    csv_path = base_path_no_ext + ".csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        fieldnames = ["gid", "gid_root", "gid0", "file_country", "level", "file"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)
    # JSON
    json_path = base_path_no_ext + ".json"
    write_json(rows, json_path)
    # Markdown
    md_path = base_path_no_ext + ".md"
    lines: List[str] = []
    lines.append("| GID | Root | GID_0 | File Country | Level | File |")
    lines.append("|---|---|---|---|---|---|")
    for r in rows:
        lines.append(f"| {r['gid']} | {r['gid_root']} | {r['gid0']} | {r['file_country']} | {r['level']} | {r['file']} |")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def main() -> None:
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    rows, aggregated, disputed_gid_rows = build_mapping()

    csv_path = os.path.join(OUTPUT_DIR, "disputed_mapping.csv")
    json_path = os.path.join(OUTPUT_DIR, "disputed_mapping.json")
    md_path = os.path.join(OUTPUT_DIR, "disputed_mapping.md")
    # Additional comprehensive GID list
    disputed_gids_base = os.path.join(OUTPUT_DIR, "disputed_gid_list")

    write_csv(rows, csv_path)
    write_json(aggregated, json_path)
    write_markdown_table(aggregated, md_path)
    write_disputed_gid_outputs(disputed_gid_rows, disputed_gids_base)

    print(f"Wrote: {csv_path}")
    print(f"Wrote: {json_path}")
    print(f"Wrote: {md_path}")
    print(f"Wrote: {disputed_gids_base}.csv")
    print(f"Wrote: {disputed_gids_base}.json")
    print(f"Wrote: {disputed_gids_base}.md")


if __name__ == "__main__":
    main()

