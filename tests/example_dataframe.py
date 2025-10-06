import pandas as pd
import xatra
import matplotlib.pyplot as plt
map = xatra.FlagMap()
map.BaseOption("OpenStreetMap", default=True)
map.BaseOption("Esri.WorldImagery")
map.BaseOption("OpenTopoMap")
map.BaseOption("Esri.WorldPhysical")

### STATIC MAP
df = pd.DataFrame({
    'GID': ['IND.31', 'IND.12', 'IND.20', 'Z01.14'],
    # 'population': [100, 200, 150, 100],
    '2021': [100, 200, 150, 100],
    'note': ['ooga', 'booga', 'kooga', 'mooga']
})
### DYNAMIC MAP
df = pd.DataFrame({
    'GID': ['IND.31', 'IND.12', 'Z01.14'],
    '2020': [100, 200, 100],
    '2020_note': ['2020_ooga', '2020_booga', '2020_mooga'],
    '2021': [110, 210, 110],
    '2021_note': ['2021_ooga', '2021_booga', '2021_mooga'],
    '2022': [120, 220, 1200]
})

df.set_index('GID', inplace=True)
# map.DataColormap(plt.cm.viridis)
map.Dataframe(df)


map.show(out_json="tests/map_dataframe.json", out_html="tests/map_dataframe.html")
