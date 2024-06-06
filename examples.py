# %%
import xatra.maps.nations as nations
import xatra.maps.colonies as colonies
import xatra.maps.hsr as hsr

# %% nations of the Indian imperial core in antiquity
nations.INDIC.plot(
    mode="flags",  # play with "features", "raw", "flags_as_layers"; defaults to "flags"
    path_out="examples/nations/INDIC.html",
    verbose=True,
)
# %% nations of the silk road
nations.SILKRD.plot(
    path_out="examples/nations/SILKRD.html",
    drop_orphans=True,
    verbose=True,
)
# %% nations of southeast asia
nations.SEA_GREATER.plot(path_out="examples/nations/SEA_GREATER.html", verbose=True)
# %% akhand bharat
nations.INDOSPHERE.plot(
    path_out="examples/nations/INDOSPHERE.html",
    css={
        "flag_label": {
            "font-size": "7.5pt",
        }
    },
    drop_orphans=True,
    verbose=True,
)
# %% Early Indian colonies in Suvarnabhumi
colonies.EARLY_SUVARNABHUMI.plot(
    path_out="examples/colonies/EARLY_SUVARNABHUMI.html",
    verbose=True,
)
# %% Sea routes of India in antiquity
colonies.SEA_ROUTES.plot(
    path_out="examples/colonies/SEA_ROUTES.html",
    verbose=True,
)
# %% graphical aid for matchers: india
nations.INDIC.plot(
    mode="flags_as_layers", path_out="examples/matchers/INDIC.html", verbose=True
)
# %% graphical aid for matchers: silk road
nations.SILKRD.plot(
    mode="flags_as_layers", path_out="examples/matchers/SILKRD.html", verbose=True
)
# %% graphical aid for matchers: southeast asia
nations.SEA_GREATER.plot(
    mode="flags_as_layers", path_out="examples/matchers/SEA.html", verbose=True
)
# %% graphical aid for matchers: indosphere
nations.INDOSPHERE.plot(
    mode="flags_as_layers",
    path_out="examples/matchers/INDOSPHERE.html",
    verbose=True,
)
# %% raw data visualization: india
nations.INDIAN_SUBCONTINENT.plot(
    mode="raw",
    path_out="examples/rdviz/INDIAN_SUBCONTINENT.html",
    custom_html="Raw data visualization: Indian subcontinent",
    verbose=True,
)
# %% raw data visualization: silk road
nations.SILKRD.plot(
    mode="raw",
    path_out="examples/rdviz/SILKRD.html",
    custom_html="Raw data visualization: Silk Road",
    verbose=True,
)
# %% raw data visualization: southeast asia
nations.SEA_GREATER.plot(
    mode="raw",
    path_out="examples/rdviz/SEA.html",
    custom_html="Raw data visualization: Southeast Asia",
    verbose=True,
)
# %% raw data visualization: world as we know it
nations.WORLD.plot(
    mode="raw",
    path_out="examples/rdviz/WORLD.html",
    custom_html="Raw data visualization: World",
    verbose=True,
)
# %% hsr
hsr.HSR.plot(
    mode="raw",
    path_out="examples/hsr.html",
    verbose=True
)
# %%
