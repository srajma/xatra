#!/usr/bin/env python3
import csv
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

WORKSPACE = Path(__file__).resolve().parents[1]
CSV_PATH = WORKSPACE / "data" / "name_to_gid_table.csv"
GADM_DIR = WORKSPACE / "data" / "gadm"
TARGET = WORKSPACE / "xatra" / "territory_library.py"


def load_mapping() -> Dict[Tuple[str, int, bool], str]:
    mapping: Dict[Tuple[str, int, bool], str] = {}
    with CSV_PATH.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row.get("name", "")
            try:
                level = int(row.get("level", ""))
            except Exception:
                continue
            nsw = row.get("name_starts_with") == "True"
            gid = (row.get("gid") or "").strip()
            if not gid:
                continue
            base = gid.split("_")[0]
            mapping[(name, level, nsw)] = base
    return mapping


def list_country_codes_for_level(level: int) -> List[str]:
    codes: List[str] = []
    for p in sorted(GADM_DIR.glob(f"gadm41_*_{level}.json")):
        codes.append(p.name.split("_")[1])
    return codes


def json_path_for(code: str, level: int) -> Path:
    return GADM_DIR / f"gadm41_{code}_{level}.json"


def all_gids_for_prefix(level: int, prefix: str) -> List[str]:
    out: List[str] = []
    pnorm = prefix.replace(" ", "")
    for cc in list_country_codes_for_level(level):
        path = json_path_for(cc, level)
        try:
            with path.open("r", encoding="utf-8", errors="ignore") as f:
                data = json.load(f)
        except Exception:
            continue
        for feat in data.get("features", []):
            props = feat.get("properties", {})
            name_key = f"NAME_{level}"
            nm = props.get(name_key)
            if not isinstance(nm, str):
                continue
            if nm.replace(" ", "").startswith(pnorm):
                gid = props.get(f"GID_{level}")
                if isinstance(gid, str):
                    base = gid.split("_")[0]
                    if base not in out:
                        out.append(base)
    return out


def replace_calls(src: str, mapping: Dict[Tuple[str, int, bool], str]) -> str:
    # name_starts_with(level, "prefix") -> union of gadm(GIDs)
    def repl_nsw(m: re.Match) -> str:
        level = int(m.group(1))
        prefix = m.group(2)
        gids = all_gids_for_prefix(level, prefix)
        if not gids:
            # leave as-is if nothing found
            return m.group(0)
        parts = [f'gadm("{g}")' for g in gids]
        if len(parts) == 1:
            return parts[0]
        return "(" + " | ".join(parts) + ")"

    src = re.sub(r"name_starts_with\(\s*(\d+)\s*,\s*\"([^\"]+)\"\s*\)", repl_nsw, src)

    # country/province/district/taluk("name") -> gadm("GID") using mapping
    func_level = {"country": 0, "province": 1, "district": 2, "taluk": 3}

    def repl_simple(m: re.Match) -> str:
        func = m.group(1)
        name = m.group(2)
        level = func_level[func]
        key_exact = (name, level, False)
        key_code_like = (name, level, True) if False else None  # not used
        gid = mapping.get(key_exact)
        if gid:
            return f'gadm("{gid}")'
        # Fallback: if name looks like a code with possible missing underscore version, try scan all by GID prefix equality
        # Otherwise, leave unchanged for manual review
        return m.group(0)

    src = re.sub(r"\b(country|province|district|taluk)\(\s*\"([^\"]+)\"\s*\)", repl_simple, src)
    return src


def main() -> None:
    mapping = load_mapping()
    src = TARGET.read_text(encoding="utf-8", errors="ignore")
    out = replace_calls(src, mapping)
    TARGET.write_text(out, encoding="utf-8")
    print("Upgraded territory_library.py to gadm(<GID>) calls.")


if __name__ == "__main__":
    main()

