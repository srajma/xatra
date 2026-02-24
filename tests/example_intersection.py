import xatra
from xatra.loaders import gadm, naturalearth, polygon
from xatra.territory_library import NORTH_INDIA, AUDICYA, JANGALA, BRAHMAVARTA
from xatra.colorseq import LinearColorSequence
from matplotlib.colors import LinearSegmentedColormap

xatra.Flag(
    label="Punjab",
    value=gadm("IND") & AUDICYA,
)
xatra.Flag(
    label="Haryanajangala",
    value=AUDICYA & JANGALA
)

xatra.show("tests/intersection.json", "tests/intersection.html")