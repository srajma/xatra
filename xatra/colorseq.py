from typing import Optional
from matplotlib import color_sequences
import colorsys
import random
import matplotlib.pyplot as plt
GOLDEN_RATIO = (1 + 5**0.5) / 2 # in HSL space

Color = tuple[float, float, float]

def hex_to_rgb(hex):
    if hex.startswith("#"):
        hex = hex[1:]
    return tuple(int(hex[i:i+2], 16) / 255 for i in (0, 2, 4))

class ColorSequence:

    def __init__(self, colors: Optional[list[Color]] = None):
        if not colors:
            colors = [(random.random(), 0.5, 0.5)]
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

    @property
    def colors_rgb(self) -> list[Color]:
        """Return the colors in RGB space"""
        return [colorsys.hls_to_rgb(*color) for color in self.colors]

    def plot(self, ax: plt.Axes):
        """Plot the color sequence as a sequence of colored bars"""
        ax.bar(range(len(self.colors)), range(len(self.colors)), color=self.colors_rgb)
    
class LinearColorSequence(ColorSequence):
    """Best for creating contrast.
    
    https://martin.ankerl.com/2009/12/09/how-to-create-random-colors-programmatically/
    """

    def __init__(self, colors: Optional[list[Color]] = None, step: Color = (GOLDEN_RATIO, 0.0, 0.0)):
        super().__init__(colors)
        self.step = step

    def next_color(self, colors: list[Color]) -> Color:
        return tuple(a + b for a, b in zip(colors[-1], self.step))
    

class LogColorSequence(ColorSequence):

    def __init__(self, colors: Optional[list[Color]] = None, step: Color = (GOLDEN_RATIO, 1.0, 1.0)):
        super().__init__(colors)
        self.step = step

    def next_color(self, colors: list[Color]) -> Color:
        return tuple(a * b for a, b in zip(colors[-1], self.step))

class RotatingColorSequence(ColorSequence):

    def __init__(self, colors: Optional[list[Color]] = None):
        super().__init__(colors)
        self.modulus = len(self.colors)

    def next_color(self, colors: list[Color]) -> Color:
        return colors[len(colors) % self.modulus]

    def from_matplotlib_color_sequence(self, name: str):
        rgb = color_sequences[name]
        hsl = [colorsys.rgb_to_hls(*rgb[i]) for i in range(len(rgb))]
        return RotatingColorSequence(hsl)
    

class RandomColorSequence(ColorSequence):

    def __init__(self, colors: Optional[list[Color]] = None):
        super().__init__(colors)

    def next_color(self, colors: list[Color]) -> Color:
        return tuple(random.random() for _ in range(3))

CONTRASTING_COLORS_HEX = [
        "#000000",
        "#00FF00",
        "#0000FF",
        "#FF0000",
        "#01FFFE",
        "#FFA6FE",
        "#FFDB66",
        "#006401",
        "#010067",
        "#95003A",
        "#007DB5",
        "#FF00F6",
        "#FFEEE8",
        "#774D00",
        "#90FB92",
        "#0076FF",
        "#D5FF00",
        "#FF937E",
        "#6A826C",
        "#FF029D",
        "#FE8900",
        "#7A4782",
        "#7E2DD2",
        "#85A900",
        "#FF0056",
        "#A42400",
        "#00AE7E",
        "#683D3B",
        "#BDC6FF",
        "#263400",
        "#BDD393",
        "#00B917",
        "#9E008E",
        "#001544",
        "#C28C9F",
        "#FF74A3",
        "#01D0FF",
        "#004754",
        "#E56FFE",
        "#788231",
        "#0E4CA1",
        "#91D0CB",
        "#BE9970",
        "#968AE8",
        "#BB8800",
        "#43002C",
        "#DEFF74",
        "#00FFC6",
        "#FFE502",
        "#620E00",
        "#008F9C",
        "#98FF52",
        "#7544B1",
        "#B500FF",
        "#00FF78",
        "#FF6E41",
        "#005F39",
        "#6B6882",
        "#5FAD4E",
        "#A75740",
        "#A5FFD2",
        "#FFB167",
        "#009BFF",
        "#E85EBE",
    ]
"""from https://stackoverflow.com/questions/1168260/algorithm-for-generating-unique-colors"""

CONTRASTING_COLORS_RGB = [hex_to_rgb(color) for color in CONTRASTING_COLORS_HEX]
CONTRASTING_COLORS_HSL = [colorsys.rgb_to_hls(*color) for color in CONTRASTING_COLORS_RGB]

# import matplotlib.pyplot as plt
# from xatra.colorseq import *

# linear_seq = LinearColorSequence()
# log_seq = LogColorSequence()
# trivial_seq = RotatingColorSequence()
# rotating_seq = RotatingColorSequence(color_sequences["tab10"])
# matplotlib_seq = RotatingColorSequence().from_matplotlib_color_sequence("tab10")
# random_seq = RandomColorSequence()
# stack_overflow_seq = LinearColorSequence(CONTRASTING_COLORS_HSL)

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
# $ stack_overflow_seq.plot(ax)
# plt.show()