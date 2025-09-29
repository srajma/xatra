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
            level = row.get("level", "")
            gid = row.get("gid", "")
            guess = row.get("country_guess", "")
            matched_country = row.get("matched_country", "")
            if level == "0" and (not gid) and guess:
                row["gid"] = guess
                if not matched_country:
                    row["matched_country"] = guess
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
        # Print a few examples
        preview = missing[:20]
        print("Examples of missing:")
        for r in preview:
            print(f"- name={r.get('name')} level={r.get('level')} guess={r.get('country_guess')}")


if __name__ == "__main__":
    main()

