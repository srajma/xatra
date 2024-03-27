# %%
import xatra.maps.nations as nations

# %% nations of the Indian imperial core in antiquity
nations.INDIC.plot(path_out="examples/nations/INDIC.html", verbose=True)
# %% nations of the silk road
nations.SILKRD.plot(
    path_out="examples/nations/SILKRD.html", drop_orphans=True, verbose=True
)
# %% nations of southeast asia
nations.SEA.plot(path_out="examples/nations/SEA.html", verbose=True)
# %% akhand bharat
nations.INDOSPHERE.plot(
    path_out="examples/nations/INDOSPHERE.html",
    css={
        "font_size": "7.5pt",
    },
    drop_orphans=True,
    verbose=True,
)
# %% alternative plot method: india
nations.INDIC.plot_flags(path_out="examples/nations/INDIC_flags.html", verbose=True)
# %% alternative plot method: silk road
nations.SILKRD.plot_flags(path_out="examples/nations/SILKRD_flags.html", verbose=True)
# %% alternative plot method: southeast asia
nations.SEA.plot_flags(path_out="examples/nations/SEA_flags.html", verbose=True)
# %% alternative plot method: indosphere
nations.INDOSPHERE.plot_flags(
    path_out="examples/nations/INDOSPHERE_flags.html", verbose=True
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
# %% raw data visualization: india
nations.INDIAN_SUBCONTINENT.plot_raw(
    path_out="examples/rdviz/INDIAN_SUBCONTINENT.html",
    custom_html="Raw data visualization: Indian subcontinent",
    verbose=True,
)
# %% raw data visualization: silk road
nations.SILKRD.plot_raw(
    path_out="examples/rdviz/SILKRD.html",
    custom_html="Raw data visualization: Silk Road",
    verbose=True,
)
# %% raw data visualization: southeast asia
nations.SEA.plot_raw(
    path_out="examples/rdviz/SEA.html",
    custom_html="Raw data visualization: Southeast Asia",
    verbose=True,
)
# %% raw data visualization: world as we know it
nations.WORLD.plot_raw(
    path_out="examples/rdviz/WORLD.html",
    custom_html="Raw data visualization: World",
    verbose=True,
)
# %%
