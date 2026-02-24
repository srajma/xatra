# Leaflet Marker Built-ins

This directory contains only Leaflet-compatible marker assets used by `Icon.builtin()`.

## Supported files

- `marker-icon.png`
- `marker-icon-red.png`
- `marker-icon-green.png`
- `marker-icon-2x.png`
- `marker-icon-2x-red.png`
- `marker-icon-2x-green.png`
- `marker-shadow.png`

## Usage

```python
from xatra import Icon

marker = Icon.builtin("marker-icon-red.png")
map.Point("City", [28.6, 77.2], icon=marker)
```

`Icon.builtin(...)` automatically applies Leaflet marker defaults (size/anchor/popup/shadow).

For standard iconography beyond marker pins, use `Icon.bootstrap(...)` or `Icon.geometric(...)`.
