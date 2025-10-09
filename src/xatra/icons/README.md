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

## Example Icons

This directory can include various icon styles for different map needs:
- `star.png` - Star marker for important locations
- `flag-red.png` - Red flag marker
- `circle-blue.png` - Blue circle marker
- etc.

Icons are automatically converted to base64 data URIs when exported, so the generated HTML files are self-contained.

