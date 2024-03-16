# %%
import xatra.maps.nations as nations

# %% nations of the Indian imperial core in antiquity
nations.INDIC.plot(path_out="examples/nations/INDIC.html", verbose=True)
# %% nations of the silk road
nations.SILKRD.plot(path_out="examples/nations/SILKRD.html", verbose=True)
# %% nations of southeast asia
nations.SEA.plot(path_out="examples/nations/SEA.html", verbose=True)
# %% akhand bharat
nations.INDOSPHERE.plot(
    path_out="examples/nations/INDOSPHERE.html",
    font_size="7.5pt",
    verbose=True,
)
# %% graphical aid for matchers: india
nations.INDIC.plot_flags_as_layers(
    path_out="examples/matchers/INDIC.html", verbose=True
)
# %% graphical aid for matchers: silk road
nations.SILKRD.plot_flags_as_layers(
    path_out="examples/matchers/SILKRD.html", verbose=True
)
# %% graphical aid for matchers: southeast asia
nations.SEA.plot_flags_as_layers(path_out="examples/matchers/SEA.html", verbose=True)
# %% graphical aid for matchers: indosphere
nations.INDOSPHERE.plot_flags_as_layers(
    path_out="examples/matchers/INDOSPHERE.html",
    verbose=True,
)
# %% raw data visualization
nations.INDIAN_SUBCONTINENT.plot_raw(
    path_out="examples/rdviz/INDIAN_SUBCONTINENT.html",
    base_maps={"CartoDB Positron": True},
    verbose=True,
)
nations.SILKRD.plot_raw(
    path_out="examples/rdviz/SILKRD.html",
    base_maps={"CartoDB Positron": True},
    verbose=True,
)
nations.SEA.plot_raw(
    path_out="examples/rdviz/SEA.html",
    base_maps={"CartoDB Positron": True},
    verbose=True,
)
nations.WORLD.plot_raw(
    path_out="examples/rdviz/WORLD.html",
    base_maps={"CartoDB Positron": True},
    verbose=True,
)
# %% for polling

# 0: control
nations.INDIC.plot(
    path_out="examples/polls/0_control.html",
    base_map="OpenStreetMap",
    opacity=0.5,
    font_size="10pt",
    font_family="'Helvetica Neue', Arial, Helvetica, sans-serif",
    verbose=True,
)

# 1: CartoDB positron (with increased opacity because of the thick labels in the background)
nations.INDIC.plot(
    path_out="examples/polls/1_basemap.html",
    base_map="CartoDB Positron",
    opacity=0.75,
    font_size="10pt",
    font_family="'Helvetica Neue', Arial, Helvetica, sans-serif",
    verbose=True,
)

# 2: full opacity

nations.INDIC.plot(
    path_out="examples/polls/2_opacity.html",
    base_map="OpenStreetMap",
    opacity=1.0,
    font_size="10pt",
    font_family="'Helvetica Neue', Arial, Helvetica, sans-serif",
    verbose=True,
)

# 3: smaller font size

nations.INDIC.plot(
    path_out="examples/polls/3_fontsize.html",
    base_map="OpenStreetMap",
    opacity=0.5,
    font_size="7.5pt",
    font_family="'Helvetica Neue', Arial, Helvetica, sans-serif",
    verbose=True,
)


# 4: font family: system theme
nations.INDIC.plot(
    path_out="examples/polls/4_font_system.html",
    base_map="OpenStreetMap",
    opacity=0.5,
    font_size="10pt",
    font_family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif",
    verbose=True,
)

# 5: font family: "Gabriola", with larger font size because Gabriola is tiny
nations.INDIC.plot(
    path_out="examples/polls/5_font_gabriola.html",
    base_map="OpenStreetMap",
    opacity=0.5,
    font_size="12pt",
    font_family="Gabriola",
    verbose=True,
)

# 6: font family: "Papyrus", and smaller font size because Papyrus is huge
nations.INDIC.plot(
    path_out="examples/polls/6_font_papyrus.html",
    base_map="OpenStreetMap",
    opacity=0.5,
    font_size="7.5pt",
    font_family="Papyrus",
    verbose=True,
)

# %%
