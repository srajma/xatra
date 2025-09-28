from typing import Optional
from matplotlib import color_sequences
import colorsys
import random
import matplotlib.pyplot as plt
GOLDEN_RATIO = (1 + 5**0.5) / 2 # in HSL space

class Color:
    
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
        self.rgb = colorsys.hls_to_rgb(h, s, l)
        self.hex = Color.rgb_to_hex(self.rgb)
    
    @classmethod
    def hsl(cls, h: float, s: float, l: float):
        return cls(h, s, l)
    
    @classmethod
    def rgb(cls, r: float, g: float, b: float):
        return cls(*colorsys.rgb_to_hls(r, g, b))
    
    @classmethod
    def hex(cls, hex: str):
        return cls.rgb(*Color.hex_to_rgb(hex))

    @classmethod
    def named(cls, name: str):
        return cls(*Color.COLOR_NAMES[name])
    
    def __str__(self):
        return self.hex
    
    @staticmethod
    def hex_to_rgb(hex):
        if hex.startswith("#"):
            hex = hex[1:]
        return tuple(int(hex[i:i+2], 16) / 255 for i in (0, 2, 4))

    @staticmethod
    def rgb_to_hex(rgb):
        return "#{:02x}{:02x}{:02x}".format(int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255))

class ColorSequence:

    def __init__(self, colors: Optional[list[Color]] = None):
        if not colors:
            colors = [Color.hsl(random.random(), 0.5, 0.5)]
        self.colors = colors

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
    
    https://martin.ankerl.com/2009/12/09/how-to-create-random-colors-programmatically/
    """

    def __init__(self, colors: Optional[list[Color]] = None, step: Color = Color.hsl(GOLDEN_RATIO, 0.0, 0.0)):
        super().__init__(colors)
        self.step = step

    def next_color(self, colors: list[Color]) -> Color:
        return Color.hsl(*(a + b % 1 for a, b in zip(colors[-1].hsl, self.step.hsl)))
    

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