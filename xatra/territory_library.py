"""
Xatra Territory Library Module

This module provides predefined composite territories that can be used
as building blocks for historical maps. These territories are created
by combining base GADM administrative boundaries using set algebra.

The library includes commonly used geographical regions that are useful
for historical mapping applications.
"""

from __future__ import annotations

from .loaders import gadm

# Example composite territory for Northern India (very rough placeholder)
NORTHERN_INDIA = gadm("IND") - gadm("IND.31")
