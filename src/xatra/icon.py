"""
Xatra Icon Module

This module provides the Icon class for customizing marker icons in maps.
It supports both custom image URLs and built-in icons loaded as base64 URIs.
"""

from __future__ import annotations

import base64
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple

try:
    from importlib.resources import files
except ImportError:
    # Fallback for Python < 3.9
    from importlib_resources import files


@dataclass
class Icon:
    """Represents a custom marker icon for Points on the map.
    
    This class allows you to customize the appearance of point markers by specifying
    custom icons, sizes, and anchor points. Icons can be loaded from URLs or from
    built-in icons shipped with the package.
    
    Args:
        icon_url: URL or data URI for the icon image
        shadow_url: Optional URL or data URI for the icon shadow
        icon_size: Size of the icon as [width, height] in pixels
        shadow_size: Optional size of the shadow as [width, height] in pixels
        icon_anchor: Point of the icon which corresponds to marker's location [x, y]
        shadow_anchor: Point of the shadow which corresponds to marker's location [x, y]
        popup_anchor: Point from which the popup should open relative to iconAnchor [x, y]
    
    Example:
        >>> # Use a custom icon from a URL
        >>> icon = Icon(
        ...     icon_url="https://example.com/my-icon.png",
        ...     icon_size=[32, 32],
        ...     icon_anchor=[16, 32]
        ... )
        >>> map.Point("Delhi", [28.6, 77.2], icon=icon)
        
        >>> # Use a built-in icon
        >>> icon = Icon.builtin("star.png")
        >>> map.Point("Important Place", [28.6, 77.2], icon=icon)
    """
    
    icon_url: str
    shadow_url: Optional[str] = None
    icon_size: Tuple[int, int] = (25, 41)  # Default Leaflet icon size
    shadow_size: Optional[Tuple[int, int]] = None
    icon_anchor: Tuple[int, int] = (12, 41)  # Default Leaflet icon anchor
    shadow_anchor: Optional[Tuple[int, int]] = None
    popup_anchor: Tuple[int, int] = (1, -34)  # Default Leaflet popup anchor
    
    @classmethod
    def builtin(cls, filename: str, **kwargs) -> Icon:
        """Load a built-in icon from the package's icons directory.
        
        This method loads icons from the `src/xatra/icons/` directory and converts
        them to base64 data URIs that can be embedded directly in the HTML output.
        
        Args:
            filename: Name of the icon file (e.g., "star.png", "marker-red.png")
            **kwargs: Additional Icon parameters (icon_size, icon_anchor, etc.)
        
        Returns:
            Icon instance with the built-in icon loaded as a data URI
        
        Raises:
            FileNotFoundError: If the specified icon file doesn't exist
        
        Example:
            >>> # Load a built-in star icon with custom size
            >>> icon = Icon.builtin("star.png", icon_size=(32, 32), icon_anchor=(16, 16))
            >>> map.Point("Capital", [28.6, 77.2], icon=icon)
        """
        try:
            # Try to use importlib.resources (Python 3.9+)
            icon_path = files('xatra').joinpath('icons', filename)
            icon_data = icon_path.read_bytes()
        except (AttributeError, FileNotFoundError):
            # Fallback: try to find it relative to this module
            module_dir = Path(__file__).parent
            icon_file = module_dir / 'icons' / filename
            
            if not icon_file.exists():
                raise FileNotFoundError(
                    f"Built-in icon '{filename}' not found. "
                    f"Please ensure the file exists in src/xatra/icons/"
                )
            
            icon_data = icon_file.read_bytes()
        
        # Determine MIME type from extension
        ext = filename.lower().split('.')[-1]
        mime_types = {
            'png': 'image/png',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'gif': 'image/gif',
            'svg': 'image/svg+xml',
            'webp': 'image/webp'
        }
        mime_type = mime_types.get(ext, 'image/png')
        
        # Convert to base64 data URI
        b64_data = base64.b64encode(icon_data).decode('utf-8')
        data_uri = f"data:{mime_type};base64,{b64_data}"
        
        return cls(icon_url=data_uri, **kwargs)
    
    def to_dict(self) -> dict:
        """Convert Icon to a dictionary for JSON serialization.
        
        Returns:
            Dictionary with icon configuration for Leaflet
        """
        result = {
            'iconUrl': self.icon_url,
            'iconSize': list(self.icon_size),
            'iconAnchor': list(self.icon_anchor),
            'popupAnchor': list(self.popup_anchor)
        }
        
        if self.shadow_url is not None:
            result['shadowUrl'] = self.shadow_url
        
        if self.shadow_size is not None:
            result['shadowSize'] = list(self.shadow_size)
        
        if self.shadow_anchor is not None:
            result['shadowAnchor'] = list(self.shadow_anchor)
        
        return result

