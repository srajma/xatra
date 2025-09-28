import xatra

map = xatra.FlagMap()
map.BaseOption("OpenStreetMap", default=True)
map.BaseOption("Esri.WorldImagery")
map.BaseOption("OpenTopoMap")
map.BaseOption("Esri.WorldPhysical")
map.Admin(gadm="IND", level=3)
map.Admin(gadm="PAK", level=3) # level-3 GADM divisions in Pak are more like districts, but we don't have finer data
map.Admin(gadm="BGD", level=3)
map.Admin(gadm="AFG", level=2) # level-2 is the best we have for Afghanistan
map.Admin(gadm="NPL", level=3) # level-3 GADM divisions in Nepal are more like districts
map.Admin(gadm="BTN", level=2) # level-2 is the best we have for Bhutan, and they're like taluks anyway
map.Admin(gadm="LKA", level=2) # level-2 is the best we have for Lanka, and they're like taluks anyway
map.AdminRivers(sources=["naturalearth", "overpass"])
map.TitleBox("<b>Taluk-level map of the Indian subcontinent.")
map.show(out_json="map_admin.json", out_html="map_admin.html")
