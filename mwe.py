#!/usr/bin/env python3

import xatra
from xatra.loaders import gadm, naturalearth
from xatra.territory_library import NORTHERN_INDIA

# Create a test map
map = xatra.FlagMap()
map.Flag(label="Maurya", value=gadm("IND") | gadm("PAK"), period=[-320, -240], note="south is lost after Ashoka's death")
map.Text(label="Jambudvipa", position=[22,79], classes="jambudvipa-text", period=[-500, 300])
map.show()