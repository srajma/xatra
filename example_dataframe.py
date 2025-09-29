import pandas as pd
import xatra

map = xatra.FlagMap()
map.BaseOption("OpenStreetMap", default=True)
map.BaseOption("Esri.WorldImagery")
map.BaseOption("OpenTopoMap")
map.BaseOption("Esri.WorldPhysical")

# df = pd.DataFrame({
#     'GID': ['IND.31', 'IND.12', 'IND.20'],
#     'population': [100, 200, 150]
# })
# df.set_index('GID', inplace=True)
# map.Dataframe(df, data_column='population')

df = pd.DataFrame({
    'GID': ['IND.31', 'IND.12'],
    '2020': [100, 200],
    '2021': [110, 210],
    '2022': [120, 220]
})
df.set_index('GID', inplace=True)
map.Dataframe(df, year_columns=['2020', '2021', '2022'])

map.show(out_json="map_dataframe.json", out_html="map_dataframe.html")
