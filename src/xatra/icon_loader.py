"""
Icon loader utility for converting package icons to data URIs.
"""

import base64
import os
from pathlib import Path


def get_icon_data_uri(filename: str) -> str:
    """Load an icon file from the package and convert it to a data URI.
    
    Args:
        filename: Name of the icon file (e.g., 'marker-icon.png')
    
    Returns:
        Data URI string that can be used directly in HTML/CSS
    """
    # Get the directory where this module is located
    module_dir = Path(__file__).parent
    icon_path = module_dir / 'icons' / filename
    
    if not icon_path.exists():
        raise FileNotFoundError(f"Icon file not found: {icon_path}")
    
    # Read the file and convert to base64
    with open(icon_path, 'rb') as f:
        icon_data = f.read()
    
    b64_data = base64.b64encode(icon_data).decode('utf-8')
    
    # Determine MIME type from extension
    ext = icon_path.suffix.lower()
    mime_types = {
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.gif': 'image/gif',
        '.svg': 'image/svg+xml',
    }
    mime_type = mime_types.get(ext, 'image/png')
    
    return f"data:{mime_type};base64,{b64_data}"


# Pre-load default icons as data URIs
DEFAULT_MARKER_ICON_DATA_URI = get_icon_data_uri('marker-icon.png')
DEFAULT_MARKER_SHADOW_DATA_URI = get_icon_data_uri('marker-shadow.png')

