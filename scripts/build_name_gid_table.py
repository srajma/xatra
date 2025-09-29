#!/usr/bin/env python3
import csv
import json
import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

WORKSPACE = Path(__file__).resolve().parents[1]
TERRITORY_FILE = WORKSPACE / "xatra" / "territory_library.py"
GADM_DIR = WORKSPACE / "data" / "gadm"
OUT_CSV = WORKSPACE / "data" / "name_to_gid_table.csv"


LEGACY_CALL_RE = re.compile(r"\b(?P<func>country|province|district|taluk|name_starts_with)\((?P<args>[^)]*)\)")


def parse_calls() -> List[Tuple[str, int, bool]]:
    entries: List[Tuple[str, int, bool]] = []
    src = TERRITORY_FILE.read_text(encoding="utf-8", errors="ignore")
    for m in LEGACY_CALL_RE.finditer(src):
        func = m.group("func")
        args = m.group("args").strip()
        if func == "name_starts_with":
            # format: name_starts_with(level, "prefix")
            parts = [p.strip() for p in args.split(",", 1)]
            if len(parts) != 2:
                continue
            try:
                level = int(eval(parts[0], {}, {}))  # safe for small int/consts
            except Exception:
                continue
            name = parts[1].strip()
            if name.startswith("\"") and name.endswith("\""):
                name = name[1:-1]
            elif name.startswith("'") and name.endswith("'"):
                name = name[1:-1]
            entries.append((name, level, True))
            continue

        # other calls have a single string arg
        # country(), province(), district(), taluk()
        try:
            # find first quoted string in args
            sm = re.search(r"\s*([\"'])(.*?)\1", args)
            if not sm:
                continue
            name = sm.group(2)
        except Exception:
            continue

        level_map = {"country": 0, "province": 1, "district": 2, "taluk": 3}
        level = level_map[func]
        entries.append((name, level, False))

    # de-duplicate while preserving order
    seen = set()
    uniq: List[Tuple[str, int, bool]] = []
    for name, level, nsw in entries:
        key = (name, level, nsw)
        if key in seen:
            continue
        seen.add(key)
        uniq.append((name, level, nsw))
    return uniq


def initial_country_guess(name: str) -> Optional[str]:
    # If it starts with a 3-letter ISO code followed by dot, prefer that
    m = re.match(r"^([A-Z]{3})\b", name)
    if m:
        code = m.group(1)
        return code

    # Heuristic name→ISO guesses for common cases in this repo
    mapping = {
        # Countries
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
        "Punjab": "PAK",  # contextually more often PAK in this file
        "NCTofDelhi": "IND",
        "Rajasthan": "IND",
        "Odisha": "IND",
        "Bihar": "IND",
        "UttarPradesh": "IND",
        "Jharkhand": "IND",
        "TamilNadu": "IND",
        "Goa": "IND",
        "Kerala": "IND",
        # Pakistan provinces
        "Khyber-Pakhtunkhwa": "PAK",
        "Balochistan": "PAK",
        # Afghanistan provinces (fallback)
        "Kabul": "AFG",
        # China
        "Xinjiang": "CHN",
    }
    if name in mapping:
        return mapping[name]

    # For Indonesian startswith cases (handled earlier) default to IDN
    if name.startswith(("Jawa", "Jakarta", "Yogyakarta", "NusaTeng", "Sulawesi", "Sumatera")):
        return "IDN"

    # Disputed Z-codes: make a conservative guess if identifiable
    if name.startswith("Z01"):
        return "IND"
    if name.startswith("Z06"):
        return "PAK"

    return None


def list_country_codes_for_level(level: int) -> List[str]:
    codes: List[str] = []
    for p in sorted(GADM_DIR.glob(f"gadm41_*_{level}.json")):
        code = p.name.split("_")[1]
        codes.append(code)
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
    # In GADM, IDs look like IND.31.1_1; match prefix before underscore
    key = f"GID_{level}"
    gid = props.get(key)
    if not isinstance(gid, str):
        return None
    base = gid.split("_")[0]
    if base == query or base.startswith(query):
        return gid
    return None


def search_gid(name: str, level: int, code_guess: Optional[str], startswith: bool) -> Tuple[Optional[str], Optional[str]]:
    # Returns (country_code_used, gid_found)
    candidates: List[str]
    if code_guess and json_path_for(code_guess, level).exists():
        candidates = [code_guess]
    else:
        candidates = list_country_codes_for_level(level)

    # If name looks like a code (IND.31, IND.31.1, Z01.14.13, etc.), prefer GID prefix match
    looks_like_code = bool(re.match(r"^[A-Z0-9]{2,3}\.\S+|^Z\d+", name))

    for cc in candidates:
        path = json_path_for(cc, level)
        try:
            with path.open("r", encoding="utf-8", errors="ignore") as f:
                data = json.load(f)
        except Exception:
            continue

        feats = data.get("features", [])
        for feat in feats:
            props = feat.get("properties", {})
            # GID match
            if looks_like_code:
                match = gid_prefix_matches(props, level, name)
                if match:
                    return cc, match
            # Name match
            if feature_name_matches(props, level, name, startswith):
                gid = props.get(f"GID_{level}")
                if isinstance(gid, str):
                    return cc, gid

    return None, None


def main() -> None:
    entries = parse_calls()

    rows: List[Dict[str, Optional[str]]] = []
    for name, level, nsw in entries:
        guess = initial_country_guess(name)
        cc_used, gid_found = search_gid(name=name, level=level, code_guess=guess, startswith=nsw)
        row = {
            "name": name,
            "level": str(level),
            "country_guess": guess or "",
            "name_starts_with": "True" if nsw else "False",
            "matched_country": cc_used or "",
            "gid": gid_found or "",
        }
        rows.append(row)

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=["name", "level", "country_guess", "name_starts_with", "matched_country", "gid"]
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} rows to {OUT_CSV}")


if __name__ == "__main__":
    main()

