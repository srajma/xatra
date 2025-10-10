#!/usr/bin/env python3
"""
Simplest possible example of pyplot-style interface.
"""

import xatra
from xatra.loaders import gadm

# Just add elements directly
xatra.Flag(label="India", value=gadm("IND"))
xatra.TitleBox("<b>Simplest Pyplot Example</b>")

# Export
xatra.show(out_json="tests/map_pyplot_simple.json", out_html="tests/map_pyplot_simple.html")
print("Simple pyplot map exported to tests/map_pyplot_simple.html")

