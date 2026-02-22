#!/usr/bin/env python3
"""
Example demonstrating map.Music() – both static and dynamic usage.

For a quick smoke-test without a real audio file, the map is exported
and you can inspect the HTML to verify that `musics` appears in the
payload JSON and that the `setupMusic()` JS function is present.
"""

import xatra
from xatra.loaders import gadm

# ── Static map example ───────────────────────────────────────────────────────
# (no periods → no slider → simple play/pause controls for the music)
static_map = xatra.Map()
static_map.BaseOption("Esri.WorldTopoMap", default=True)
static_map.Flag(label="India", value=gadm("IND"))
static_map.TitleBox("<b>Static map with music</b>")

# Uncomment and point to a real audio file to test:
static_map.Music("tests/audio.mp3")
static_map.Music("tests/audio.mp3", timestamps=(10, 70))   # play seconds 10–70 on loop

static_map.show(out_json="tests/map_music_static.json",
                out_html="tests/map_music_static.html")
print("Static music map → tests/map_music_static.html")

# ── Dynamic map example ──────────────────────────────────────────────────────
# (flags have periods → slider appears → music syncs with slider)
dyn_map = xatra.Map()
dyn_map.BaseOption("Esri.WorldTopoMap", default=True)
dyn_map.Flag(label="Maurya", value=gadm("IND"), period=[-320, -180])
dyn_map.Flag(label="Gupta",  value=gadm("IND"), period=[320, 550])
dyn_map.TitleBox("<b>Dynamic map with music</b>")
dyn_map.slider(-400, 600)

# period=None → defaults to the full slider period (-400, 600)
# timestamps=None → plays the whole audio file
# Uncomment and point to a real audio file to test:
dyn_map.Music("tests/audio.mp3")
dyn_map.Music("tests/audio.mp3", timestamps=None, period=(-320, 550))

dyn_map.show(out_json="tests/map_music_dynamic.json",
             out_html="tests/map_music_dynamic.html")
print("Dynamic music map → tests/map_music_dynamic.html")
