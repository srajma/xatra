# Built-in Icons Directory

This directory contains built-in marker icons that can be loaded using `Icon.builtin()`.

## Usage

```python
from xatra import Icon

# Load a built-in icon
icon = Icon.builtin("star.png", icon_size=(32, 32), icon_anchor=(16, 16))
map.Point("Important Place", [28.6, 77.2], icon=icon)
```

## Adding Custom Icons

To add a new built-in icon:

1. Add your image file (PNG, JPG, SVG, etc.) to this directory
2. Use `Icon.builtin("your_icon_name.png")` to load it
3. Optionally specify custom sizes and anchor points

## Icon Parameters

- `icon_size`: Size of the icon as `(width, height)` in pixels
- `icon_anchor`: Point of the icon which corresponds to the marker's location `(x, y)`
- `shadow_url`: Optional shadow image URL
- `shadow_size`: Optional shadow size `(width, height)`
- `shadow_anchor`: Optional shadow anchor point `(x, y)`
- `popup_anchor`: Point from which popups open relative to the icon anchor `(x, y)`

## Built-in Icons

This directory includes several SVG icons for different map needs:

### Cities and buildings
- `city.png` - City in ancient Indian style
- `temple.svg` - Hindu temple with shikhara (spire) and traditional architectural elements
- `temple-nagara.svg` - Nagara-style temple with shikhara over garbhagriha and separate mandapa with tiered roof
- `temple-gopuram.svg` - somewhat like Dravidian gopuram
- `temple-nepali.svg` - somewhat Nepali temple
- `temple-pagoda.svg` - somewhat pagoda-like temple
- `temple-parthenon.svg` - Classical Greek Parthenon-style temple with columns and pediment
- `fort.svg` - Fortress or citadel with crenellations and central tower
- `port.svg` - Seaport with ship, dock, cranes, and cargo containers



### General Purpose Icons
- `star.svg` - Five-pointed star for important or significant locations
- `important.svg` - Exclamation mark in a circle for urgent/notable places
- `example.svg` - Simple circular marker with exclamation point
- `symbol-om.svg` - Hindu Om symbol (sacred syllable)

### Geometric Shape Icons
Simple geometric markers in dark blue for basic map annotations:
- `disk.svg` - Filled circle/disk
- `circle.svg` - Empty circle (outline only)
- `cross.svg` - X shape (cross)
- `plus.svg` - + shape (plus sign)
- `rectangle.svg` - Filled square
- `diamond.svg` - Filled diamond shape
- `triangle.svg` - Filled triangle (pointing upward)

### Religious Symbols
- `symbol-cross.svg` - Christian cross
- `symbol-star.svg` - Jewish Star of David (Magen David)
- `symbol-muslim.svg` - Islamic crescent moon and star

### Adding More Icons

You can add your own icons following these guidelines:
- Use SVG format for scalability
- Keep designs simple and recognizable at small sizes (32x32px)
- Use a circular border or background for consistency
- Choose colors that work well on both light and dark map backgrounds
- Test icons at different zoom levels to ensure readability

Icons are automatically converted to base64 data URIs when exported, so the generated HTML files are self-contained.

