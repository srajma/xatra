from typing import Optional
from matplotlib import color_sequences
import colorsys
import math
import random
import matplotlib.pyplot as plt
GOLDEN_RATIO = (1 + 5**0.5) / 2 # in HSL space

# Default "atlas" palette: colours are generated in the perceptually uniform
# OKLCH space so that every flag has the same visual weight (no glaring yellows
# next to murky blues), with a gentle three-step lightness rhythm so that
# neighbouring hues stay distinguishable even after the hue wheel wraps around.
ATLAS_LIGHTNESS = 0.78
ATLAS_CHROMA = 0.105
ATLAS_START_HUE = 30.0  # degrees; a warm terracotta
ATLAS_LIGHTNESS_RHYTHM = (0.0, -0.06, 0.035)


def _srgb_encode(x: float) -> float:
    return 12.92 * x if x <= 0.0031308 else 1.055 * x ** (1 / 2.4) - 0.055


def _srgb_decode(x: float) -> float:
    return x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4


def _oklab_to_linear_rgb(L: float, a: float, b: float) -> tuple[float, float, float]:
    l_ = L + 0.3963377774 * a + 0.2158037573 * b
    m_ = L - 0.1055613458 * a - 0.0638541728 * b
    s_ = L - 0.0894841775 * a - 1.2914855480 * b
    l, m, s = l_ ** 3, m_ ** 3, s_ ** 3
    return (
        4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s,
        -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s,
        -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s,
    )


def oklch_to_rgb(L: float, C: float, h: float) -> tuple[float, float, float]:
    """Convert OKLCH (L in 0..1, chroma, hue in degrees) to sRGB in 0..1.

    Out-of-gamut colours are brought into gamut by reducing chroma, which keeps
    lightness and hue (the perceptually important parts) intact.
    """
    L = min(max(L, 0.0), 1.0)
    hr = math.radians(h % 360)
    chroma = max(C, 0.0)
    for _ in range(40):
        rgb = _oklab_to_linear_rgb(L, chroma * math.cos(hr), chroma * math.sin(hr))
        if all(-1e-6 <= c <= 1 + 1e-6 for c in rgb):
            break
        chroma *= 0.92
    return tuple(min(max(_srgb_encode(min(max(c, 0.0), 1.0)), 0.0), 1.0) for c in rgb)


def rgb_to_oklch(r: float, g: float, b: float) -> tuple[float, float, float]:
    """Convert sRGB (0..1) to OKLCH (L, C, hue in degrees)."""
    r, g, b = (_srgb_decode(c) for c in (r, g, b))
    l = 0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b
    m = 0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b
    s = 0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b
    l_, m_, s_ = (math.copysign(abs(v) ** (1 / 3), v) for v in (l, m, s))
    L = 0.2104542553 * l_ + 0.7936177850 * m_ - 0.0040720468 * s_
    a = 1.9779984951 * l_ - 2.4285922050 * m_ + 0.4505937099 * s_
    bb = 0.0259040371 * l_ + 0.7827717662 * m_ - 0.8086757660 * s_
    return (L, math.hypot(a, bb), math.degrees(math.atan2(bb, a)) % 360)


class Color:
    """A colour, stored as HSL (each component in 0..1)."""

    COLOR_NAMES = {
        "red": (0, 1, 0.5),
        "green": (120 / 360, 1, 0.5),
        "blue": (240 / 360, 1, 0.5),
        "yellow": (60 / 360, 1, 0.5),
        "purple": (300 / 360, 1, 0.5),
        "orange": (30 / 360, 1, 0.5),
        "brown": (30 / 360, 0.5, 0.5),
        "gray": (0 / 360, 0, 0.5),
        "black": (0 / 360, 0, 0),
        "white": (0 / 360, 0, 1),
        "pink": (320 / 360, 1, 0.5),
        "cyan": (180 / 360, 1, 0.5),
        "magenta": (300 / 360, 1, 0.5),
        "lime": (120 / 360, 1, 0.5),
        "teal": (180 / 360, 1, 0.5),
        "indigo": (240 / 360, 1, 0.5),
        "violet": (300 / 360, 1, 0.5),
    }

    def __init__(self, h: float, s: float, l: float):
        self.hsl = (h, s, l)
        # colorsys uses HLS ordering (hue, lightness, saturation)
        self.rgb = colorsys.hls_to_rgb(h % 1.0, l, s)
        self.hex = Color.rgb_to_hex(self.rgb)

    @classmethod
    def hsl(cls, h: float, s: float, l: float):
        return cls(h, s, l)

    @classmethod
    def rgb(cls, r: float, g: float, b: float):
        h, l, s = colorsys.rgb_to_hls(r, g, b)
        color = cls(h, s, l)
        color.rgb = (r, g, b)  # keep the exact input; avoids round-trip drift
        color.hex = Color.rgb_to_hex(color.rgb)
        return color

    @classmethod
    def hex(cls, hex: str):
        return cls.rgb(*Color.hex_to_rgb(hex))

    @classmethod
    def oklch(cls, L: float, C: float, h: float):
        """Create a colour from OKLCH (perceptual lightness 0..1, chroma ~0..0.37, hue in degrees)."""
        return cls.rgb(*oklch_to_rgb(L, C, h))

    @classmethod
    def named(cls, name: str):
        return cls(*Color.COLOR_NAMES[name])

    def __str__(self):
        return self.hex

    def __repr__(self):
        return f"Color.hex({self.hex!r})"

    def __eq__(self, other):
        return isinstance(other, Color) and self.hex == other.hex

    def __hash__(self):
        return hash(self.hex)

    @staticmethod
    def hex_to_rgb(hex):
        if hex.startswith("#"):
            hex = hex[1:]
        if len(hex) == 3:
            hex = "".join(ch * 2 for ch in hex)
        return tuple(int(hex[i:i+2], 16) / 255 for i in (0, 2, 4))

    @staticmethod
    def rgb_to_hex(rgb):
        return "#{:02x}{:02x}{:02x}".format(*(int(round(min(max(c, 0.0), 1.0) * 255)) for c in rgb))


def atlas_color(index: int, hue_step: float = GOLDEN_RATIO, lightness_step: float = 0.0, chroma_step: float = 0.0) -> Color:
    """The ``index``-th colour of xatra's default palette.

    Hues advance by ``hue_step`` turns (the golden ratio by default, which keeps
    consecutive colours maximally distinct), in OKLCH so all colours carry the
    same visual weight.
    """
    hue = ATLAS_START_HUE + index * (hue_step % 1.0) * 360.0
    lightness = ATLAS_LIGHTNESS + ATLAS_LIGHTNESS_RHYTHM[index % len(ATLAS_LIGHTNESS_RHYTHM)] + index * lightness_step
    # Yellows and olives turn muddy when dark; lift them a little.
    lightness += 0.06 * max(0.0, math.cos(math.radians(hue - 100))) ** 2
    chroma = ATLAS_CHROMA + index * chroma_step * 0.2
    return Color.oklch(min(max(lightness, 0.3), 0.97), max(chroma, 0.0), hue)


class ColorSequence:

    def __init__(self, colors: Optional[list[Color]] = None):
        if not colors:
            colors = [atlas_color(0)]
        self.colors = list(colors)

    def next_color(self, colors: list[Color]) -> Color:
        """Define how to compute next color in sequence
        self.colors -> return next color
        """
        pass
    
    def append(self, val: Optional[Color] = None) -> Color:
        """Can force a value to be added to the sequence"""
        if val is None:
            val = self.next_color(self.colors)
        self.colors.append(val)
        return val
    
    def append_many(self, n: int):
        """Append n colors to the sequence"""
        for _ in range(n):
            self.append()

    def __getitem__(self, index: int) -> Color:
        if index >= len(self.colors):
            self.append_many(index - len(self.colors) + 1)
        
        return self.colors[index]
    
    def __setitem__(self, index: int, value: Color):
        if index >= len(self.colors):
            self.append_many(index - len(self.colors) + 1)
        self.colors[index] = value

    def plot(self, ax: plt.Axes):
        """Plot the color sequence as a sequence of colored bars"""
        ax.bar(range(len(self.colors)), range(len(self.colors)), color=[color.rgb for color in self.colors])
    
class LinearColorSequence(ColorSequence):
    """Best for creating contrast.

    With no starting ``colors`` this produces xatra's default "atlas" palette:
    soft, evenly weighted colours whose hues advance by ``step``'s hue (golden
    ratio by default) in the perceptual OKLCH space; ``step``'s saturation and
    lightness components nudge chroma and lightness per colour. The output is
    deterministic, so a map keeps its colours across renders.

    With explicit starting ``colors``, each next colour is the previous one plus
    ``step`` in HSL (hue wraps around; saturation/lightness are clamped).

    https://martin.ankerl.com/2009/12/09/how-to-create-random-colors-programmatically/
    """

    def __init__(self, colors: Optional[list[Color]] = None, step: Color = Color.hsl(GOLDEN_RATIO, 0.0, 0.0)):
        self.perceptual = not colors
        self.step = step
        if self.perceptual:
            colors = [self._atlas(0)]
        super().__init__(colors)

    def _atlas(self, index: int) -> Color:
        h, s, l = self.step.hsl
        return atlas_color(index, hue_step=h, lightness_step=l, chroma_step=s)

    def next_color(self, colors: list[Color]) -> Color:
        if self.perceptual:
            return self._atlas(len(colors))
        h, s, l = colors[-1].hsl
        dh, ds, dl = self.step.hsl
        return Color.hsl((h + dh) % 1.0, min(max(s + ds, 0.0), 1.0), min(max(l + dl, 0.0), 1.0))
    

class LogColorSequence(ColorSequence):

    def __init__(self, colors: Optional[list[Color]] = None, step: Color = Color.hsl(GOLDEN_RATIO, 1.0, 1.0)):
        super().__init__(colors)
        self.step = step

    def next_color(self, colors: list[Color]) -> Color:
        return Color.hsl(*(a * b % 1 for a, b in zip(colors[-1].hsl, self.step.hsl)))

class RotatingColorSequence(ColorSequence):

    def __init__(self, colors: Optional[list[Color]] = None):
        super().__init__(colors)
        self.modulus = len(self.colors)

    def next_color(self, colors: list[Color]) -> Color:
        return colors[len(colors) % self.modulus]

    def from_matplotlib_color_sequence(self, name: str):
        return RotatingColorSequence([Color.rgb(*color) for color in color_sequences[name]])
    

class RandomColorSequence(ColorSequence):

    def __init__(self, colors: Optional[list[Color]] = None):
        super().__init__(colors)

    def next_color(self, colors: list[Color]) -> Color:
        return Color.hsl(random.random(), random.random(), random.random())

CONTRASTING_COLORS = [
        Color.hex("#000000"),
        Color.hex("#00FF00"),
        Color.hex("#0000FF"),
        Color.hex("#FF0000"),
        Color.hex("#01FFFE"),
        Color.hex("#FFA6FE"),
        Color.hex("#FFDB66"),
        Color.hex("#006401"),
        Color.hex("#010067"),
        Color.hex("#95003A"),
        Color.hex("#007DB5"),
        Color.hex("#FF00F6"),
        Color.hex("#FFEEE8"),
        Color.hex("#774D00"),
        Color.hex("#90FB92"),
        Color.hex("#0076FF"),
        Color.hex("#D5FF00"),
        Color.hex("#FF937E"),
        Color.hex("#6A826C"),
        Color.hex("#FF029D"),
        Color.hex("#FE8900"),
        Color.hex("#7A4782"),
        Color.hex("#7E2DD2"),
        Color.hex("#85A900"),
        Color.hex("#FF0056"),
        Color.hex("#A42400"),
        Color.hex("#00AE7E"),
        Color.hex("#683D3B"),
        Color.hex("#BDC6FF"),
        Color.hex("#263400"),
        Color.hex("#BDD393"),
        Color.hex("#00B917"),
        Color.hex("#9E008E"),
        Color.hex("#001544"),
        Color.hex("#C28C9F"),
        Color.hex("#FF74A3"),
        Color.hex("#01D0FF"),
        Color.hex("#004754"),
        Color.hex("#E56FFE"),
        Color.hex("#788231"),
        Color.hex("#0E4CA1"),
        Color.hex("#91D0CB"),
        Color.hex("#BE9970"),
        Color.hex("#968AE8"),
        Color.hex("#BB8800"),
        Color.hex("#43002C"),
        Color.hex("#DEFF74"),
        Color.hex("#00FFC6"),
        Color.hex("#FFE502"),
        Color.hex("#620E00"),
        Color.hex("#008F9C"),
        Color.hex("#98FF52"),
        Color.hex("#7544B1"),
        Color.hex("#B500FF"),
        Color.hex("#00FF78"),
        Color.hex("#FF6E41"),
        Color.hex("#005F39"),
        Color.hex("#6B6882"),
        Color.hex("#5FAD4E"),
        Color.hex("#A75740"),
        Color.hex("#A5FFD2"),
        Color.hex("#FFB167"),
        Color.hex("#009BFF"),
        Color.hex("#E85EBE"),
    ]
"""from https://stackoverflow.com/questions/1168260/algorithm-for-generating-unique-colors"""


# import matplotlib.pyplot as plt
# from xatra.colorseq import *

# linear_seq = LinearColorSequence()
# log_seq = LogColorSequence()
# trivial_seq = RotatingColorSequence()
# rotating_seq = RotatingColorSequence(color_sequences["tab10"])
# matplotlib_seq = RotatingColorSequence().from_matplotlib_color_sequence("tab10")
# random_seq = RandomColorSequence()
# stack_overflow_seq = LinearColorSequence(CONTRASTING_COLORS)

# linear_seq.append_many(30)
# log_seq.append_many(30)
# trivial_seq.append_many(30)
# rotating_seq.append_many(30)
# matplotlib_seq.append_many(30)
# random_seq.append_many(30)
# # stack_overflow_seq.append_many(30)

# fig, ax = plt.subplots()
# linear_seq.plot(ax)
# # log_seq.plot(ax)
# # trivial_seq.plot(ax)
# # rotating_seq.plot(ax)
# # matplotlib_seq.plot(ax)
# # random_seq.plot(ax)
# stack_overflow_seq.plot(ax)
# plt.show()