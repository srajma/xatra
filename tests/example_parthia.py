import xatra
from xatra.loaders import gadm, naturalearth, polygon, overpass
from xatra.icon import Icon
from xatra.colorseq import Color, ColorSequence, LinearColorSequence
from matplotlib.colors import LinearSegmentedColormap
from xatra.territory_library import PARTHIA

xatra.Flag(value=PARTHIA,label="PARTHIA")

xatra.show("tests/map_parthia.json", "tests/map_parthia.html")
