"""
Example: fetch and cache Overpass rivers by OSM id.

This script demonstrates the new behavior:
- if an id is missing locally, xatra.loaders.overpass(id) queries Overpass API
- the normalized GeoJSON is saved into ~/.xatra/data/rivers_overpass_india/
- the returned geometry is used immediately in a map
"""

import xatra
from xatra.loaders import overpass

xatra.BaseOption("Esri.WorldTopoMap", default=True)
xatra.BaseOption("Esri.WorldImagery")
xatra.CSS(
    """
    .river, .admin-river {
        stroke: #0077cc;
        stroke-width: 3;
        opacity: 0.9;
    }
    """
)


# IDs chosen from existing examples/comments; one or both may already exist locally.
# If not, they will be downloaded and cached.
ids = [
    ("Ganga (Overpass)", "1236345"),
    ("Kubha/Kabul (Overpass)", "1676476"),
    ("Svat", "9612817"),
    ("Danube Segment (Overpass way)", "8078884"),
]

for label, osm_id in ids:
    try:
        xatra.River(label=label,value=overpass(osm_id),)
        print(f"Loaded overpass river id={osm_id}")
    except Exception as exc:
        print(f"Failed overpass river id={osm_id}: {exc}")

xatra.TitleBox("Overpass Fetch + Cache Demo")
xatra.focus(34.9, 72.4)  # Swat valley region
xatra.zoom(8)
xatra.show(out_json="tests/map_overpass_fetch.json", out_html="tests/map_overpass_fetch.html")
