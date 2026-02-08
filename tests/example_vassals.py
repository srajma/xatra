#!/usr/bin/env python3
"""Example demonstrating slash-labeled vassals in Xatra."""

import xatra
from xatra.loaders import gadm

map = xatra.Map()
map.BaseOption("Esri.WorldTopoMap", default=True)
map.BaseOption("Esri.WorldImagery")

# Parent territories
map.Flag(label="India", value=gadm("IND"), note="Parent territory")
map.Flag(label="Gupta", value=gadm("IND.25") | gadm("IND.20"), note="Parent dynasty")

# Vassals: slash-separated labels get hsla(h, 100%, 90%, 0.6) overlay colors.
# These are drawn on top of parent territories; parents are not cut out.
map.Flag(label="India/Karnataka", value=gadm("IND.16"), note="Overlay vassal")
map.Flag(label="India/Tamil Nadu", value=gadm("IND.31"), note="Overlay vassal")
map.Flag(label="India/Maharashtra", value=gadm("IND.20"), note="Overlay vassal")

# Multi-level slash labels also work.
map.Flag(label="India/Deccan/Bijapur", value=gadm("IND.16"), period=[1500, 1650])

map.Flag(label="Gupta/Gujarat", value=gadm("IND.11"), period=[320, 500])
map.Flag(label="Gupta/Malwa", value=gadm("IND.19"), period=[320, 500])

map.TitleBox("""
<b>Slash Vassals Demo</b><br>
<small>
Vassals use slash labels (for example, <code>India/Karnataka</code>) and receive light
HSLA overlay colors. Parent territories remain intact beneath vassals.
</small>
""")

map.show(out_json="tests/map_vassals.json", out_html="tests/map_vassals.html")
print("Vassals example exported to tests/map_vassals.html")
