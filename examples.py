# from xatra.data import Loka, Varuna, Combined
import xatra.maps.nations as nations

# raw data download
# Loka.WORLD.download("examples/rd/", overwrite = True)
# Varuna.WORLD.download("examples/rd/")
# ^ no real point to running this unless you're a developer working on the package itself
# ^ in which case you would run it to "xatra/data/"

# raw data visualization
# Combined.INDIAN_SUBCONTINENT.plot(path_out = 'examples/rdviz/INDIAN_SUBCONTINENT.html')
# Combined.SILKRD.plot(path_out = 'examples/rdviz/SILKRD.html')
# Combined.WORLD.plot(
#     path_out="examples/rdviz/WORLD.html"
# )  # too big to share on Github, so excluded with .gitignore, you can generate it yourself

indic = nations.INDIC(verbose=True)
silkrd = nations.SILKRD(verbose=True)
sea = nations.SEA(verbose=True)
indosphere = nations.INDOSPHERE(verbose=True)

# main historical visualizations : standard nations
indic.plot(path_out="examples/nations/INDIC.html")
# silkrd.plot(path_out="examples/nations/SILKRD.html")
# sea.plot(path_out="examples/nations/SEA.html")
# indosphere.plot(path_out="examples/nations/INDOSPHERE.html")

# graphical aids for select matchers (use the layer toggle to view each matcher)
# indic.plot_flags_as_layers(path_out="examples/nations/INDIC_matchers.html")
# silkrd.plot_flags_as_layers(path_out="examples/nations/SILKRD_matchers.html")
# sea.plot_flags_as_layers(path_out="examples/nations/SEA_matchers.html")
# indosphere.plot_flags_as_layers(path_out="examples/nations/INDOSPHERE_matchers.html")

# nations.INDIC.plot(path_out = 'examples/nations/INDIC.html')
# nations.SILKRD.plot(path_out = 'examples/nations/SILKRD.html')
# nations.SEA.plot(path_out = 'examples/nations/SEA.html')
# nations.WORLD.plot(path_out = 'examples/nations/WORLD.html')
# nations.INDIC.plot_flags_as_layers(path_out = 'examples/nations/INDIC_flags.html')
# nations.SILKRD.plot_flags_as_layers(path_out = 'examples/nations/SILKRD_flags.html')
# nations.SEA.plot_flags_as_layers(path_out = 'examples/nations/SEA_flags.html')
# nations.WORLD.plot_flags_as_layers(path_out = 'examples/nations/WORLD_flags.html')

# xatra.rdviz(feature_list = raw_data.subcont + raw_data.indiaish_rivers, path_out = 'examples/rdviz/subcont.html')
# xatra.rdviz(feature_list = raw_data.indiaish + raw_data.indiaish_rivers, path_out = 'examples/rdviz/indiaish.html')
# xatra.rdviz(feature_list = raw_data.silkrd + raw_data.silkrd_rivers, path_out = 'examples/rdviz/silkrd.html')
# xatra.rdviz(feature_list = raw_data.world + raw_data.world_rivers, path_out = 'examples/rdviz/world.html')
# ^ i recommend you don't run this last one as the file it generates is close to Github's 75 MB limit

# main historical visualizations : standard nations
# nations.indiaish.plot(path_out = "examples/nations/indiaish.html")
# nations.silkrd.plot(path_out = "examples/nations/silkrd.html")
# nations.world.plot(path_out = "examples/nations/world.html")

# flags_test = [dict(flag, period = [-1000,1000]) for flag in maps.tracts.flags]
