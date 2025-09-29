#!/usr/bin/env python3
import csv
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

WORKSPACE = Path(__file__).resolve().parents[1]
CSV_PATH = WORKSPACE / "data" / "name_to_gid_table.csv"
GADM_DIR = WORKSPACE / "data" / "gadm"


def initial_country_guess(name: str) -> Optional[str]:
    m = re.match(r"^([A-Z]{3})\b", name)
    if m:
        return m.group(1)
    mapping = {
        "India": "IND",
        "Pakistan": "PAK",
        "Nepal": "NPL",
        "Bhutan": "BTN",
        "Bangladesh": "BGD",
        "SriLanka": "LKA",
        "Sri Lanka": "LKA",
        "Mongolia": "MNG",
        "Vietnam": "VNM",
        "Laos": "LAO",
        "Cambodia": "KHM",
        "Brunei": "BRN",
        "Malaysia": "MYS",
        "Thailand": "THA",
        "Uzbekistan": "UZB",
        "Tajikistan": "TJK",
        "Turkmenistan": "TKM",
        "Iran": "IRN",
        "Iraq": "IRQ",
        "Syria": "SYR",
        "Israel": "ISR",
        "Jordan": "JOR",
        "Lebanon": "LBN",
        "Armenia": "ARM",
        "Azerbaijan": "AZE",
        "Georgia": "GEO",
        "Japan": "JPN",
        "Korea": "KOR",
        # Indian states/UTs
        "HimachalPradesh": "IND",
        "Uttarakhand": "IND",
        "Assam": "IND",
        "ArunachalPradesh": "IND",
        "Meghalaya": "IND",
        "Nagaland": "IND",
        "Manipur": "IND",
        "Mizoram": "IND",
        "Tripura": "IND",
        "Sikkim": "IND",
        "Punjab": "IND",
        "NCTofDelhi": "IND",
        "Rajasthan": "IND",
        "Odisha": "IND",
        "Bihar": "IND",
        "UttarPradesh": "IND",
        "Jharkhand": "IND",
        "TamilNadu": "IND",
        "Goa": "IND",
        "Kerala": "IND",
    }
    if name in mapping:
        return mapping[name]
    if name.startswith(("Jawa", "Jakarta", "Yogyakarta", "NusaTeng", "Sulawesi", "Sumatera")):
        return "IDN"
    if name.startswith("Z01"):
        return "IND"
    if name.startswith("Z06"):
        return "PAK"
    return None


def list_country_codes_for_level(level: int) -> List[str]:
    codes: List[str] = []
    for p in sorted(GADM_DIR.glob(f"gadm41_*_{level}.json")):
        codes.append(p.name.split("_")[1])
    return codes


def json_path_for(code: str, level: int) -> Path:
    return GADM_DIR / f"gadm41_{code}_{level}.json"


def feature_name_matches(props: Dict, level: int, query: str, startswith: bool) -> bool:
    key = f"NAME_{level}"
    val = props.get(key) or ""
    if not isinstance(val, str):
        return False
    if startswith:
        return val.replace(" ", "").startswith(query)
    return val.replace(" ", "") == query


def gid_prefix_matches(props: Dict, level: int, query: str) -> Optional[str]:
    key = f"GID_{level}"
    gid = props.get(key)
    if not isinstance(gid, str):
        return None
    base = gid.split("_")[0]
    if base == query or base.startswith(query):
        return gid
    return None


def search_gid(name: str, level: int, code_guess: Optional[str], startswith: bool) -> Tuple[Optional[str], Optional[str]]:
    candidates: List[str]
    if code_guess and json_path_for(code_guess, level).exists():
        candidates = [code_guess]
    else:
        candidates = list_country_codes_for_level(level)

    looks_like_code = bool(re.match(r"^[A-Z0-9]{2,3}\.\S+|^Z\d+", name))
    for cc in candidates:
        path = json_path_for(cc, level)
        try:
            with path.open("r", encoding="utf-8", errors="ignore") as f:
                data = json.load(f)
        except Exception:
            continue
        for feat in data.get("features", []):
            props = feat.get("properties", {})
            if looks_like_code:
                match = gid_prefix_matches(props, level, name)
                if match:
                    return cc, match
            if feature_name_matches(props, level, name, startswith):
                gid = props.get(f"GID_{level}")
                if isinstance(gid, str):
                    return cc, gid
    return None, None


def main() -> None:
    rows = []
    with CSV_PATH.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)

    changed = 0
    for row in rows:
        if row.get("gid"):
            continue
        name = row.get("name", "")
        try:
            level = int(row.get("level", ""))
        except Exception:
            continue
        nsw = (row.get("name_starts_with") == "True")
        guess = row.get("country_guess") or initial_country_guess(name)
        cc_used, gid_found = search_gid(name, level, guess, nsw)
        if gid_found:
            row["gid"] = gid_found
            if not row.get("matched_country"):
                row["matched_country"] = cc_used or ""
            if not row.get("country_guess"):
                row["country_guess"] = guess or ""
            changed += 1

    with CSV_PATH.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "name",
            "level",
            "country_guess",
            "name_starts_with",
            "matched_country",
            "gid",
        ])
        writer.writeheader()
        writer.writerows(rows)

    missing = [r for r in rows if not r.get("gid")]
    print(f"Updated rows: {changed} | Total: {len(rows)} | Remaining without gid: {len(missing)}")
    if missing:
        for r in missing[:20]:
            print(f"- name={r.get('name')} level={r.get('level')} guess={r.get('country_guess')}")


if __name__ == "__main__":
    main()

