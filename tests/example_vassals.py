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

# Vassals: slash-separated labels + type="vassal" get hsla(h, 100%, 90%, 0.6) fills.
# These are drawn on top of parent territories; parents are not cut out.
map.Flag(label="India/Karnataka", value=gadm("IND.16"), note="Overlay vassal", type="vassal")
map.Flag(label="India/Tamil Nadu", value=gadm("IND.31"), note="Overlay vassal", type="vassal")
map.Flag(label="India/Maharashtra", value=gadm("IND.20"), note="Overlay vassal", type="vassal")

# Provinces: slash labels + type="province" get no fill, only thin border in root parent color.
map.Flag(label="India/Deccan", value=gadm("IND.2"), period=[1400, 1700], type="province")
# Multi-level hierarchy labels also work.
map.Flag(label="India/Deccan/Bijapur", value=gadm("IND.16"), period=[1500, 1650], type="province")

map.Flag(label="Gupta/Gujarat", value=gadm("IND.11"), period=[320, 500], type="vassal")
map.Flag(label="Gupta/Malwa", value=gadm("IND.19"), period=[320, 500], type="province")

map.TitleBox("""
<b>Slash Vassals Demo</b><br>
<small>
Vassals use slash labels + <code>type=&quot;vassal&quot;</code> and receive light HSLA overlays.<br>
Provinces use <code>type=&quot;province&quot;</code> and draw only thin borders in their root parent's color.<br>
Parent territories remain intact beneath children.
</small>
""")

map.show(out_json="tests/map_vassals.json", out_html="tests/map_vassals.html")
print("Vassals example exported to tests/map_vassals.html")
