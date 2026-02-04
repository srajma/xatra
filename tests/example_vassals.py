#!/usr/bin/env python3
"""
Example demonstrating the Vassals feature in Xatra.

This example shows how to use the parent parameter to create vassal/province
relationships between flags. Vassals of real parent flags get:
- Colors with reduced saturation derived from the parent's color
- Smaller label font sizes
- Tooltips showing the vassal relationship

Vassals of placeholder parents get:
- Colors from a shared color family (for grouping by religion, alliance, etc.)
- Normal font sizes (no reduction)
- Tooltips showing the vassal relationship

Placeholder flags can be created with placeholder=True to customize the color
sequence for their children without rendering the placeholder itself.
"""

import xatra
from xatra.loaders import gadm
from xatra.colorseq import LinearColorSequence, Color

# Create a new map
map = xatra.Map()
map.BaseOption("Esri.WorldTopoMap", default=True)
map.BaseOption("Esri.WorldImagery")

# Example 1: Real parent with vassals
# India is a real flag, Karnataka and Tamil Nadu are its vassals
map.Flag(label="India", value=gadm("IND"), note="Republic of India")
map.Flag(label="Karnataka", value=gadm("IND.16"), parent="India", note="A state of India")
map.Flag(label="Tamil Nadu", value=gadm("IND.31"), parent="India", note="Southernmost state")
map.Flag(label="Maharashtra", value=gadm("IND.20"), parent="India", note="Western state")

# Example 2: Placeholder parent with custom color
# "Hindu" is a placeholder flag (not rendered) but defines the color family for its children
map.Flag(label="Hindu", placeholder=True, color="#ff9933")  # Saffron color
map.Flag(label="Vijayanagara", value=gadm("IND.2"), parent="Hindu", note="Hindu empire")
map.Flag(label="Yadava", value=gadm("IND.21"), parent="Hindu", note="Hindu dynasty")

# Example 3: Another placeholder parent with custom color sequence
# "Muslim" is a placeholder with a custom children_color_seq
muslim_seq = LinearColorSequence(
    colors=[Color.hex("#00ff00")],  # Green base
    step=Color.hsl(0.03, 0.0, 0.0)
)
map.Flag(label="Muslim", placeholder=True, children_color_seq=muslim_seq)
map.Flag(label="Sultanate", value=gadm("IND.25"), parent="Muslim", note="Delhi Sultanate")
map.Flag(label="Ahmedabad", value=gadm("IND.11"), parent="Muslim", note="Gujarat Sultanate")

# Example 4: Implicit placeholder (parent name without a placeholder flag)
# "Buddhist" is referenced as parent but never defined - still works, uses auto-generated color
map.Flag(label="Maurya", value=gadm("IND.7"), parent="Buddhist", note="Buddhist empire")
map.Flag(label="Pala", value=gadm("IND.36"), parent="Buddhist", note="Buddhist dynasty")

# Example 5: Regular flags without parent (for comparison)
map.Flag(label="Pakistan", value=gadm("PAK"), note="Independent nation")

map.TitleBox("""
<b>Vassals Feature Demo</b><br>
<small>
- States of India: reduced saturation + smaller labels (vassal of real parent)<br>
- Hindu empires: saffron color family (explicit placeholder parent)<br>
- Muslim empires: green color family (placeholder with custom sequence)<br>
- Buddhist empires: auto-generated color family (implicit placeholder)<br>
- Pakistan: independent flag with its own color
</small>
""")

map.show(out_json="tests/map_vassals.json", out_html="tests/map_vassals.html")
print("Vassals example exported to tests/map_vassals.html")
