# %%
import xatra.maps.nations as nations

# %% nations of the Indian imperial core in antiquity
nations.INDIC.plot(
    path_out="examples/nations/INDIC.html", base_map="CartoDB Positron", verbose=True
)
# %% nations of the silk road
nations.SILKRD.plot(
    path_out="examples/nations/SILKRD.html", base_map="CartoDB Positron", verbose=True
)
# %% nations of southeast asia
nations.SEA.plot(
    path_out="examples/nations/SEA.html", base_map="CartoDB Positron", verbose=True
)
# %% akhand bharat
nations.INDOSPHERE.plot(
    path_out="examples/nations/INDOSPHERE.html",
    base_map="CartoDB Positron",
    verbose=True,
)
# %% graphical aid for matchers: india
nations.INDIC.plot_flags_as_layers(
    path_out="examples/matchers/INDIC.html", base_map="CartoDB Positron", verbose=True
)
# %% graphical aid for matchers: silk road
nations.SILKRD.plot_flags_as_layers(
    path_out="examples/matchers/SILKRD.html", base_map="CartoDB Positron", verbose=True
)
# %% graphical aid for matchers: southeast asia
nations.SEA.plot_flags_as_layers(
    path_out="examples/matchers/SEA.html", base_map="CartoDB Positron", verbose=True
)
# %% graphical aid for matchers: indosphere
nations.INDOSPHERE.plot_flags_as_layers(
    path_out="examples/matchers/INDOSPHERE.html",
    base_map="CartoDB Positron",
    verbose=True,
)
# %% raw data visualization
# nations.INDIAN_SUBCONTINENT.plot_raw(path_out="examples/rdviz/INDIAN_SUBCONTINENT.html", base_map="CartoDB Positron", verbose=True)
# nations.SILKRD.plot_raw(path_out="examples/rdviz/SILKRD.html", base_map="CartoDB Positron", verbose=True)
nations.SEA.plot_raw(
    path_out="examples/rdviz/SEA.html", base_map="CartoDB Positron", verbose=True
)
# nations.WORLD.plot_raw(path_out="examples/rdviz/WORLD.html", base_map="CartoDB Positron", verbose=True)
# %% example dynamic map
from xatra.maps.example_dynamic_map import ExampleDynamic

ExampleDynamic.plot(path_out="examples/dynamic.html")
# %%
