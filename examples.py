# %%

import xatra.maps.nations as nations

# %% nations of the Indian imperial core in antiquity

indic = nations.INDIC(verbose=True)  # this takes a while to load
indic.plot(path_out="examples/nations/INDIC.html")
indic.plot_flags_as_layers(
    path_out="examples/nations/INDIC_matchers.html"
)  # plots graphical aids for select matchers (use the layer toggle to view each matcher)

# %% nations of the silk road

silkrd = nations.SILKRD(verbose=True)
silkrd.plot(path_out="examples/nations/SILKRD.html")
silkrd.plot_flags_as_layers(path_out="examples/nations/SILKRD_matchers.html")

# %% nations of southeast asia

sea = nations.SEA(verbose=True)
sea.plot(path_out="examples/nations/SEA.html")
sea.plot_flags_as_layers(path_out="examples/nations/SEA_matchers.html")

# %% akhand bharat

indosphere = nations.INDOSPHERE(verbose=True)
indosphere.plot(path_out="examples/nations/INDOSPHERE.html")
indosphere.plot_flags_as_layers(path_out="examples/nations/INDOSPHERE_matchers.html")

# %% example dynamic map
from xatra.maps.example_dynamic_map import MyDynamic

dynamic = MyDynamic(verbose=True)
dynamic.plot(path_out="examples/dynamic.html")

# %% raw data visualization

from xatra.data import Loka, Varuna, Combined

Combined.INDIAN_SUBCONTINENT.plot(path_out="examples/rdviz/INDIAN_SUBCONTINENT.html")
Combined.SILKRD.plot(path_out="examples/rdviz/SILKRD.html")
Loka.SEA.plot(
    path_out="examples/rdviz/SEA.html"
)  # TODO: maybe add Brahmaputra & Iravati (Burma)
Combined.WORLD.plot(
    path_out="examples/rdviz/WORLD.html"
)  # too big to share on Github, so excluded with .gitignore, you can generate it yourself

# %% raw data download

# from xatra.data import Loka, Varuna, Combined
# Loka.WORLD.download("examples/rd/", overwrite = False)
# Varuna.WORLD.download("examples/rd/")
# ^ basically only run this if you're a developer contributing to
# ^ the the package, or if you want to use the project for some
# ^ other region of the world not included in the package by default
# ^ the data included in the package is in "xatra/data"