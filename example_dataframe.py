import pandas as pd
import xatra

map = xatra.FlagMap()
map.BaseOption("OpenStreetMap", default=True)
map.BaseOption("Esri.WorldImagery")
map.BaseOption("OpenTopoMap")
map.BaseOption("Esri.WorldPhysical")

### STATIC MAP
# df = pd.DataFrame({
#     'GID': ['IND.31', 'IND.12', 'IND.20', 'Z01.14'],
#     'population': [100, 200, 150, 100]
# })
### DYNAMIC MAP
df = pd.DataFrame({
    'GID': ['IND.31', 'IND.12', 'Z01.14'],
    '2020': [100, 200, 100],
    '2021': [110, 210, 110],
    '2022': [120, 220, 120]
})

df.set_index('GID', inplace=True)
map.Dataframe(df)


map.show(out_json="map_dataframe.json", out_html="map_dataframe.html")
