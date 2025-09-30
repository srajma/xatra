import xatra
from xatra.loaders import gadm, naturalearth
from xatra.territory_library import PUNJAB
from xatra.colorseq import LinearColorSequence
from matplotlib.colors import LinearSegmentedColormap

map = xatra.FlagMap()
map.BaseOption("OpenStreetMap", default=True)
map.Flag(label="punjab", value=PUNJAB)
map.show(out_json="map_punjab.json", out_html="map_punjab.html")