from xatra.data import Loka, Varuna, Combined
import xatra.maps.nations as nations

# raw data download
# Loka.WORLD.download("examples/rd/", overwrite = True)
# Varuna.WORLD.download("examples/rd/")
# ^ no real point to running this unless you're a developer working on the package itself
# ^ in which case you would run it to "xatra/data/"

# raw data visualization
# Combined.INDIAN_SUBCONTINENT.plot(path_out = 'examples/rdviz/INDIAN_SUBCONTINENT.html')
# Combined.SILKRD.plot(path_out="examples/rdviz/SILKRD.html")
# Loka.SEA.plot(
#     path_out="examples/rdviz/SEA.html"
# )  # TODO: maybe add Brahmaputra & Iravati (Burma)
# Combined.WORLD.plot(
#     path_out="examples/rdviz/WORLD.html"
# )  # too big to share on Github, so excluded with .gitignore, you can generate it yourself

indic = nations.INDIC(verbose=True)
silkrd = nations.SILKRD(verbose=True)
sea = nations.SEA(verbose=True)
indosphere = nations.INDOSPHERE(verbose=True)

# main historical visualizations : standard nations
indic.plot(path_out="examples/nations/INDIC.html")
silkrd.plot(path_out="examples/nations/SILKRD.html")
sea.plot(path_out="examples/nations/SEA.html")
indosphere.plot(path_out="examples/nations/INDOSPHERE.html")

# graphical aids for select matchers (use the layer toggle to view each matcher)
indic.plot_flags_as_layers(path_out="examples/nations/INDIC_matchers.html")
silkrd.plot_flags_as_layers(path_out="examples/nations/SILKRD_matchers.html")
sea.plot_flags_as_layers(path_out="examples/nations/SEA_matchers.html")
indosphere.plot_flags_as_layers(path_out="examples/nations/INDOSPHERE_matchers.html")