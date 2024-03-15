# %%
import xatra.maps.nations as nations

# %% nations of the Indian imperial core in antiquity
nations.INDIC.plot(
    path_out="examples/nations/INDIC.html", base_map="CartoDB Positron", verbose=True
)  # any custom options may be set either while initializing or in plot()
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
    font_size="7.5pt",
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
nations.INDIAN_SUBCONTINENT.plot_raw(
    path_out="examples/rdviz/INDIAN_SUBCONTINENT.html",
    base_map="CartoDB Positron",
    verbose=True,
)
nations.SILKRD.plot_raw(
    path_out="examples/rdviz/SILKRD.html", base_map="CartoDB Positron", verbose=True
)
nations.SEA.plot_raw(
    path_out="examples/rdviz/SEA.html", base_map="CartoDB Positron", verbose=True
)
nations.WORLD.plot_raw(
    path_out="examples/rdviz/WORLD.html", base_map="CartoDB Positron", verbose=True
)
# %% example dynamic map
from xatra.maps.example_dynamic_map import ExampleDynamic

ExampleDynamic.plot(path_out="examples/dynamic.html")
# %%

#%% for polling

# 1: control
nations.INDIC.plot(
    path_out="examples/polls/1.html",
    base_map="OpenStreetMap",
    opacity=0.5,
    font_size="10pt",
    font_family="'Helvetica Neue', Arial, Helvetica, sans-serif",
    verbose=True,
)

# 2: CartoDB positron (with increased opacity because of the thick labels in the background)
nations.INDIC.plot(
    path_out="examples/polls/2.html",
    base_map="CartoDB Positron",
    opacity=0.75,
    font_size="10pt",
    font_family="'Helvetica Neue', Arial, Helvetica, sans-serif",
    verbose=True,
)

# 3: full opacity 

nations.INDIC.plot(
    path_out="examples/polls/3.html",
    base_map="OpenStreetMap",
    opacity=1.0,
    font_size="10pt",
    font_family="'Helvetica Neue', Arial, Helvetica, sans-serif",
    verbose=True,
)

# 4: smaller font size

nations.INDIC.plot(
    path_out="examples/polls/4.html",
    base_map="OpenStreetMap",
    opacity=0.5,
    font_size="7.5pt",
    font_family="'Helvetica Neue', Arial, Helvetica, sans-serif",
    verbose=True,
)


# 6: font family: system theme
nations.INDIC.plot(
    path_out="examples/polls/6.html",
    base_map="OpenStreetMap",
    opacity=0.5,
    font_size="10pt",
    font_family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif",
    verbose=True,
)

# 7: font family: "Gabriola", with larger font size because Gabriola is tiny
nations.INDIC.plot(
    path_out="examples/polls/7.html",
    base_map="OpenStreetMap",
    opacity=0.5,
    font_size="12pt",
    font_family="Gabriola",
    verbose=True,
)

# 8: font family: "Papyrus", and smaller font size because Papyrus is huge
nations.INDIC.plot(
    path_out="examples/polls/8.html",
    base_map="OpenStreetMap",
    opacity=0.5,
    font_size="6.5pt",
    font_family="Papyrus",
    verbose=True,
)
