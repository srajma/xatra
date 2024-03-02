"""Visualize raw data"""

import folium
import geopandas as gpd
import matplotlib.colors as mcolors

import raw_data
from chronologies.matchers import is_river

def rdviz(feature_list, path_out):

    # Convert GeoJSON to GeoDataFrame for easy handling
    gdf = gpd.GeoDataFrame.from_features(feature_list)

    # Find the center of the map
    center = [gdf.geometry.centroid.y.mean(), gdf.geometry.centroid.x.mean()]

    # Create a Folium map
    m = folium.Map(location=center, zoom_start=5)
    
    # Function to filter tooltip fields based on specific criteria
    def filter_tooltip_fields(properties):
        return [key for key in properties.keys() if properties[key] and (key == "COUNTRY" or key.startswith("NAME_") or key.startswith("VARNAME_") or key.startswith("GID_"))]
    
    # Function to generate a color based on GID_1
    def color_producer(gid1):
        colors = list(mcolors.CSS4_COLORS.values())
        return colors[hash(gid1) % len(colors)]

    # Create a Feature Group for rivers and for other features
    rivers = folium.FeatureGroup(name='Rivers', show=False)
    districts = folium.FeatureGroup(name='Districts')

    # Add GeoJSON features to their respective feature groups
    for feature in feature_list:
        if is_river(feature):
            # Add rivers to the river feature group
            folium.GeoJson(
                feature,
                style_function=lambda x: {
                    'color': 'blue',
                    'weight': 3,
                    'fillOpacity': 0.7,
                },
                tooltip=folium.GeoJsonTooltip(fields=['river_name', 'id'])
            ).add_to(rivers)
        else:
            # Add other features (like districts) to the districts feature group
            folium.GeoJson(
                feature,
                style_function=lambda x: {
                    'fillColor': color_producer(x['properties']['GID_1']),
                    'color': 'black',
                    'weight': 0.5,
                    'fillOpacity': 0.7,
                },
                tooltip=folium.GeoJsonTooltip(fields=filter_tooltip_fields(feature['properties']))
            ).add_to(districts)

    # Add the feature groups to the map
    rivers.add_to(m)
    districts.add_to(m)

    # Add a layer control to toggle rivers
    folium.LayerControl().add_to(m)

    # Save to HTML
    m.save(path_out)
