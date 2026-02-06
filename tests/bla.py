import xatra
from xatra.loaders import gadm, naturalearth, polygon, overpass

# Define reusable territories here
# e.g. maurya = gadm("IND") | gadm("PAK")

map = xatra.Map()

map.BaseOption("Esri.WorldTopoMap", name="", default=True)
map.TitleBox("""<b>My Interactive Map</b>""")

map.Flag(value=gadm("IND") | polygon([[25.1652,57.5684],[17.6859,57.832],[14.5198,61.5674],[18.5629,73.1689],[26.116,71.3232]]), note='Republic of India', period=[-320,0], label='maurya')
map.Point(position=[28.6, 77.2], label='New point')
map.Path(value=[[9.2756,58.4912],[10.7038,63.5889],[11.9963,55.9863],[19.8494,53.0859]], label='New path', period=[-320,100])
map.River(value=naturalearth("1159122643"), label='New river')
map.show()
