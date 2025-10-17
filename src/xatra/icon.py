"""
Xatra Icon Module

This module provides the Icon class for customizing marker icons in maps.
It supports three types of icons:
1. Custom image URLs
2. Built-in icons loaded as base64 URIs
3. Pure SVG geometric shapes (circles, triangles, diamonds, etc.)

The geometric shapes are generated using SVG and converted to data URIs,
providing lightweight, scalable alternatives to image-based icons.
"""

from __future__ import annotations

import base64
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple, Union
from enum import Enum

try:
    from importlib.resources import files
except ImportError:
    # Fallback for Python < 3.9
    from importlib_resources import files


class ShapeType(Enum):
    """Available geometric shapes for HTML-based icons."""
    CIRCLE = "circle"
    SQUARE = "square"
    TRIANGLE = "triangle"
    DIAMOND = "diamond"
    CROSS = "cross"
    PLUS = "plus"
    STAR = "star"
    HEXAGON = "hexagon"
    PENTAGON = "pentagon"
    OCTAGON = "octagon"


def _generate_shape_svg(shape: ShapeType, size: int, color: str, border_color: str = None, border_width: int = 0) -> str:
    """Generate SVG for a geometric shape.
    
    Args:
        shape: The type of shape to generate
        size: Size of the shape in pixels
        color: Fill color (CSS color string)
        border_color: Border color (CSS color string)
        border_width: Border width in pixels
    
    Returns:
        SVG string for the shape
    """
    # SVG viewBox and dimensions
    viewbox = f"0 0 {size} {size}"
    
    # Border attributes
    border_attrs = ""
    if border_width > 0 and border_color:
        border_attrs = f'stroke="{border_color}" stroke-width="{border_width}"'
    
    if shape == ShapeType.CIRCLE:
        center = size // 2
        radius = center - border_width
        return f"""
        <svg viewBox="{viewbox}" xmlns="http://www.w3.org/2000/svg">
            <circle cx="{center}" cy="{center}" r="{radius}" fill="{color}" {border_attrs}/>
        </svg>
        """
    
    elif shape == ShapeType.SQUARE:
        return f"""
        <svg viewBox="{viewbox}" xmlns="http://www.w3.org/2000/svg">
            <rect x="0" y="0" width="{size}" height="{size}" fill="{color}" {border_attrs}/>
        </svg>
        """
    
    elif shape == ShapeType.TRIANGLE:
        # Triangle pointing up
        half_width = size // 2
        points = f"{half_width},{border_width} {size - border_width},{size - border_width} {border_width},{size - border_width}"
        return f"""
        <svg viewBox="{viewbox}" xmlns="http://www.w3.org/2000/svg">
            <polygon points="{points}" fill="{color}" {border_attrs}/>
        </svg>
        """
    
    elif shape == ShapeType.DIAMOND:
        # Diamond (rotated square)
        half_size = size // 2
        points = f"{half_size},0 {size},0 {half_size},{size} 0,{half_size}"
        return f"""
        <svg viewBox="{viewbox}" xmlns="http://www.w3.org/2000/svg">
            <polygon points="{points}" fill="{color}" {border_attrs}/>
        </svg>
        """
    
    elif shape == ShapeType.CROSS:
        # Cross shape
        thickness = max(2, size // 8)
        center = size // 2
        half_thickness = thickness // 2
        return f"""
        <svg viewBox="{viewbox}" xmlns="http://www.w3.org/2000/svg">
            <rect x="0" y="{center - half_thickness}" width="{size}" height="{thickness}" fill="{color}" {border_attrs}/>
            <rect x="{center - half_thickness}" y="0" width="{thickness}" height="{size}" fill="{color}" {border_attrs}/>
        </svg>
        """
    
    elif shape == ShapeType.PLUS:
        # Plus shape (thicker than cross)
        thickness = max(3, size // 6)
        center = size // 2
        half_thickness = thickness // 2
        return f"""
        <svg viewBox="{viewbox}" xmlns="http://www.w3.org/2000/svg">
            <rect x="0" y="{center - half_thickness}" width="{size}" height="{thickness}" fill="{color}" {border_attrs}/>
            <rect x="{center - half_thickness}" y="0" width="{thickness}" height="{size}" fill="{color}" {border_attrs}/>
        </svg>
        """
    
    elif shape == ShapeType.STAR:
        # 5-pointed star
        center = size // 2
        outer_radius = center - border_width
        inner_radius = outer_radius * 0.4
        
        # Calculate star points
        import math
        points = []
        for i in range(10):
            angle = math.pi / 2 + i * math.pi / 5  # Start from top
            radius = outer_radius if i % 2 == 0 else inner_radius
            x = center + radius * math.cos(angle)
            y = center + radius * math.sin(angle)
            points.append(f"{x:.1f},{y:.1f}")
        
        points_str = " ".join(points)
        return f"""
        <svg viewBox="{viewbox}" xmlns="http://www.w3.org/2000/svg">
            <polygon points="{points_str}" fill="{color}" {border_attrs}/>
        </svg>
        """
    
    elif shape == ShapeType.HEXAGON:
        # Regular hexagon
        center = size // 2
        radius = center - border_width
        import math
        points = []
        for i in range(6):
            angle = i * math.pi / 3
            x = center + radius * math.cos(angle)
            y = center + radius * math.sin(angle)
            points.append(f"{x:.1f},{y:.1f}")
        
        points_str = " ".join(points)
        return f"""
        <svg viewBox="{viewbox}" xmlns="http://www.w3.org/2000/svg">
            <polygon points="{points_str}" fill="{color}" {border_attrs}/>
        </svg>
        """
    
    elif shape == ShapeType.PENTAGON:
        # Regular pentagon
        center = size // 2
        radius = center - border_width
        import math
        points = []
        for i in range(5):
            angle = math.pi / 2 + i * 2 * math.pi / 5  # Start from top
            x = center + radius * math.cos(angle)
            y = center + radius * math.sin(angle)
            points.append(f"{x:.1f},{y:.1f}")
        
        points_str = " ".join(points)
        return f"""
        <svg viewBox="{viewbox}" xmlns="http://www.w3.org/2000/svg">
            <polygon points="{points_str}" fill="{color}" {border_attrs}/>
        </svg>
        """
    
    elif shape == ShapeType.OCTAGON:
        # Regular octagon
        center = size // 2
        radius = center - border_width
        import math
        points = []
        for i in range(8):
            angle = math.pi / 8 + i * math.pi / 4  # Offset to make it point up
            x = center + radius * math.cos(angle)
            y = center + radius * math.sin(angle)
            points.append(f"{x:.1f},{y:.1f}")
        
        points_str = " ".join(points)
        return f"""
        <svg viewBox="{viewbox}" xmlns="http://www.w3.org/2000/svg">
            <polygon points="{points_str}" fill="{color}" {border_attrs}/>
        </svg>
        """
    
    else:
        raise ValueError(f"Unsupported shape type: {shape}")


def _create_svg_data_uri(svg_content: str) -> str:
    """Convert SVG content to a data URI.
    
    Args:
        svg_content: SVG content as string
    
    Returns:
        Data URI string
    """
    # Encode as base64 data URI
    b64_data = base64.b64encode(svg_content.encode('utf-8')).decode('utf-8')
    return f"data:image/svg+xml;base64,{b64_data}"


@dataclass
class Icon:
    """Represents a custom marker icon for Points on the map.
    
    This class allows you to customize the appearance of point markers by specifying
    custom icons, sizes, and anchor points. Icons can be loaded from URLs, from
    built-in icons shipped with the package, or created as pure HTML/CSS geometric shapes.
    
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
        
        >>> # Create a geometric shape icon
        >>> icon = Icon.geometric("circle", color="red", size=24)
        >>> map.Point("Geometric Marker", [28.6, 77.2], icon=icon)
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
            filename: Name of the icon file (e.g., "star.svg", "temple.svg")
            **kwargs: Additional Icon parameters (icon_size, icon_anchor, etc.)
        
        Returns:
            Icon instance with the built-in icon loaded as a data URI
        
        Raises:
            FileNotFoundError: If the specified icon file doesn't exist
        
        Available Built-in Icons:
        
        Cities and Buildings:
            - city.png - Ancient Indian style city
            - temple.svg - Hindu temple with shikhara
            - temple-nagara.svg - Nagara-style temple
            - temple-gopuram.svg - Dravidian gopuram style
            - temple-nepali.svg - Nepali temple style
            - temple-pagoda.svg - Pagoda-style temple
            - temple-parthenon.svg - Classical Greek Parthenon
            - fort.svg - Fortress or citadel
            - port.svg - Seaport with ships and cranes
            - oilrig.svg - Oil rig platform
        
        General Purpose:
            - star.svg - Five-pointed star for important locations
            - important.svg - Exclamation mark in circle
            - example.svg - Simple circular marker with exclamation
        
        Geometric Shapes:
            - circle.svg - Empty circle outline
            - disk.svg - Filled circle/disk
            - square.svg - Filled square
            - rectangle.svg - Filled rectangle
            - triangle.svg - Filled triangle (pointing up)
            - diamond.svg - Filled diamond shape
            - cross.svg - X-shaped cross
            - plus.svg - Plus sign (+)
        
        Religious Symbols:
            - symbol-om.svg - Hindu Om symbol
            - symbol-cross.svg - Christian cross
            - symbol-star.svg - Jewish Star of David
            - symbol-muslim.svg - Islamic crescent and star
            - symbol-zoro.svg - Zoroastrian faravahar
        
        Leaflet Markers:
            - marker-icon.png - Default blue marker
            - marker-icon-red.png - Red marker
            - marker-icon-green.png - Green marker
            - marker-icon-2x.png - High-res blue marker
            - marker-icon-2x-red.png - High-res red marker
            - marker-icon-2x-green.png - High-res green marker
            - marker-shadow.png - Default marker shadow
        
        Example:
            >>> # Load a built-in temple icon with custom size
            >>> icon = Icon.builtin("temple.svg", icon_size=(32, 32), icon_anchor=(16, 16))
            >>> map.Point("Sacred Temple", [28.6, 77.2], icon=icon)
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
    
    @classmethod
    def geometric(
        cls, 
        shape: Union[ShapeType, str], 
        color: str = "#3388ff", 
        size: int = 24,
        border_color: str = None,
        border_width: int = 0,
        **kwargs
    ) -> Icon:
        """Create an icon using a pure SVG geometric shape.
        
        This method generates icons using SVG instead of image files, providing
        lightweight, scalable geometric shapes for map markers.
        
        Args:
            shape: The geometric shape to create. Can be a ShapeType enum or string.
                  Available shapes: circle, square, triangle, diamond, cross, plus, 
                  star, hexagon, pentagon, octagon
            color: Fill color for the shape (CSS color string, e.g., "#ff0000", "red")
            size: Size of the shape in pixels (default: 24)
            border_color: Optional border color (CSS color string)
            border_width: Optional border width in pixels (default: 0)
            **kwargs: Additional Icon parameters (icon_size, icon_anchor, etc.)
                     Single integers for icon_size and icon_anchor will be converted to tuples
        
        Returns:
            Icon instance with the geometric shape as a data URI
        
        Raises:
            ValueError: If the shape type is not supported
        
        Example:
            >>> # Create a red circle icon
            >>> circle_icon = Icon.geometric("circle", color="red", size=32)
            >>> map.Point("Important", [28.6, 77.2], icon=circle_icon)
            
            >>> # Create a blue diamond with border
            >>> diamond_icon = Icon.geometric(
            ...     ShapeType.DIAMOND, 
            ...     color="blue", 
            ...     border_color="white", 
            ...     border_width=2,
            ...     icon_size=(32, 32),
            ...     icon_anchor=(16, 16)
            ... )
            >>> map.Point("Diamond Point", [19.0, 73.0], icon=diamond_icon)
            
            >>> # Create a green triangle
            >>> triangle_icon = Icon.geometric("triangle", color="#00ff00", size=28)
            >>> map.Point("Triangle Marker", [13.0, 80.2], icon=triangle_icon)
            
            >>> # Single integers for icon_size and icon_anchor are converted to tuples
            >>> city_icon = Icon.geometric("circle", color="blue", icon_size=12, icon_anchor=6)
            >>> map.Point("City", [28.6, 77.2], icon=city_icon)
        """
        # Convert string to ShapeType if needed
        if isinstance(shape, str):
            try:
                shape = ShapeType(shape.lower())
            except ValueError:
                available_shapes = [s.value for s in ShapeType]
                raise ValueError(
                    f"Unsupported shape '{shape}'. Available shapes: {available_shapes}"
                )
        
        # Generate SVG for the shape
        shape_svg = _generate_shape_svg(
            shape=shape,
            size=size,
            color=color,
            border_color=border_color,
            border_width=border_width
        )
        
        # Convert to data URI
        data_uri = _create_svg_data_uri(shape_svg)
        
        # Handle icon_size - convert single int to tuple if needed
        if 'icon_size' in kwargs:
            icon_size = kwargs['icon_size']
            if isinstance(icon_size, int):
                kwargs['icon_size'] = (icon_size, icon_size)
        else:
            kwargs['icon_size'] = (size, size)
        
        # Handle icon_anchor - convert single int to tuple if needed
        if 'icon_anchor' in kwargs:
            icon_anchor = kwargs['icon_anchor']
            if isinstance(icon_anchor, int):
                kwargs['icon_anchor'] = (icon_anchor, icon_anchor)
        else:
            kwargs['icon_anchor'] = (size // 2, size // 2)
        
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

    def to_html(
        self,
        *,
        alt: str = "",
        classes: Optional[str] = None,
        style: Optional[str] = None,
        attrs: Optional[dict] = None,
    ) -> str:
        """Return the HTML string for this icon as rendered in the final HTML.
        
        This returns an <img> element that mirrors how the icon image is embedded
        on the map, using the current `icon_url` and `icon_size`. This is useful
        for building legends or custom UI outside the map canvas.
        
        Args:
            alt: Alt text for the image tag
            classes: Optional space-separated class names to add to the <img>
            style: Optional inline CSS to add to the <img>
            attrs: Optional dict of additional HTML attributes to include
        
        Returns:
            HTML string (an <img> tag) that can be embedded in legends/labels
        """
        width, height = self.icon_size
        attributes: list[str] = [
            f'src="{self.icon_url}"',
            f'width="{width}"',
            f'height="{height}"',
            f'alt="{alt}"',
        ]
        if classes:
            attributes.append(f'class="{classes}"')
        if style:
            attributes.append(f'style="{style}"')
        if attrs:
            for key, value in attrs.items():
                # Basic attribute serialization; assumes keys/values are safe strings
                attributes.append(f'{key}="{value}"')
        return f"<img {' '.join(attributes)} />"

