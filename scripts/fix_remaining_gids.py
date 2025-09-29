#!/usr/bin/env python3
import csv
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[1]
CSV_PATH = WORKSPACE / "data" / "name_to_gid_table.csv"


def main() -> None:
    rows = []
    with CSV_PATH.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames or []
        for row in reader:
            name = row.get("name", "")
            level = row.get("level", "")
            gid = row.get("gid", "")
            matched_country = row.get("matched_country", "")

            # Fixes:
            # 1) Sambhai -> Sambhal (UP district)
            if name == "Sambhai" and level == "2":
                row["name"] = "Sambhal"
                # keep matched_country if present; rely on gid search to have already filled
            # 2) Ambedkarnagar -> AmbedkarNagar
            if name == "Ambedkarnagar" and level == "2":
                row["name"] = "AmbedkarNagar"
            # 3) 8.3.2 at level 3 missing country code -> PAK.8.3.2
            if name == "8.3.2" and level == "3":
                row["name"] = "PAK.8.3.2"
                if not matched_country:
                    row["matched_country"] = "PAK"
            # 4) Afghanistan level 0 -> AFG
            if name == "Afghanistan" and level == "0":
                row["gid"] = "AFG"
                if not matched_country:
                    row["matched_country"] = "AFG"

            rows.append(row)

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

    # Report remaining without gid
    missing = [r for r in rows if not r.get("gid")]
    print(f"Total rows: {len(rows)} | Remaining without gid: {len(missing)}")
    if missing:
        preview = missing[:20]
        print("Examples of missing:")
        for r in preview:
            print(f"- name={r.get('name')} level={r.get('level')} guess={r.get('country_guess')}")


if __name__ == "__main__":
    main()

