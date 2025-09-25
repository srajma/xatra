from __future__ import annotations

from .loaders import gadm

# Example composite territory for Northern India (very rough placeholder)
NORTHERN_INDIA = gadm("IND") - gadm("IND.31")
