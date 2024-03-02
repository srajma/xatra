import folium
import matplotlib

import raw_data
import chronologies.tracts
from chronologies.matchers import is_river

def create_contrasting_color_mapping(flags, cmap, segments=8):
    color_mapping = {}

    # Calculate the number of colors per segment
    n_colors = cmap.N  # Get the total number of colors available in the color map
    colors_per_segment = n_colors // segments

    # Assign colors from different segments to ensure contrast
    for i, flag in enumerate(flags):
        segment_index = i % segments
        color_index = (i // segments) % colors_per_segment
        color_position = segment_index * colors_per_segment + color_index
        color = cmap(color_position)[:3]  # Get the RGB part of the color
        color_mapping[flag['name']] = matplotlib.colors.rgb2hex(color)

    return color_mapping

def visualize_map(feature_list, flags_list, path_out = 'outputs/magic.html'):

    # Identify all unique flags for color mapping
    #unique_flags = set(flag['name'] for flag in flags) | {'No Flag'}
    unique_flags = [flag for flag in flags_list] + [{'name': 'No Flag'}]
    cmap = matplotlib.cm.get_cmap('tab20', len(unique_flags))
    #color_mapping = {flag: matplotlib.colors.rgb2hex(cmap(i)[:3]) for i, flag in enumerate(unique_flags)}
    color_mapping = create_contrasting_color_mapping(unique_flags, cmap)
    color_mapping['No Flag'] = '#ffffff' # force these guys to be white
    for flag in color_mapping: # and these guys to be grey
        if flag.startswith('YYY_') or flag.startswith('ZZZ_'):
            color_mapping[flag] = '#444444'

    # Create a Folium map
    m = folium.Map(location=[20.5937, 78.9629], zoom_start=5)  # Centered on India
    rivers = folium.FeatureGroup(name='Rivers', show=True)
    districts = folium.FeatureGroup(name='Districts')
    
    # Modify GeoJSON features based on flags and separate rivers

    for feature in feature_list:
        if is_river(feature):
            rivers.add_child(folium.GeoJson(
                data=feature,
                style_function=lambda x: {'color': 'blue', 'weight': 2, 'fillOpacity': 0},
                tooltip=folium.GeoJsonTooltip(fields=['river_name', 'id'])
            ))
        else:
            feature_flags = [flag for flag in flags_list if flag['matcher'](feature)]
            # In case of conflict, duplicate the feature for each flag it matches
            for flag in feature_flags:
                temp_feature = feature.copy()
                temp_feature['properties']['flag'] = flag['name']
                temp_feature['properties']['flags'] = [f['name'] for f in feature_flags]
                temp_feature['properties']['NAME_max'] = raw_data.NAME_max(temp_feature)["NAME_n"]
                districts.add_child(folium.GeoJson(
                    data=temp_feature,
                    name="Flags",
                    style_function=lambda feature: {
                        'fillColor': color_mapping.get(feature['properties']['flag'], '#808080'),
                        'color': 'black',
                        'weight': 0,
                        'fillOpacity': 0.5,  # Adjusted fill opacity for visual overlap transparency
                    },
                    tooltip=folium.GeoJsonTooltip(fields=['NAME_max', 'flags'], aliases=['NAME', 'Flag'])
                ))

    m.add_child(districts)
    m.add_child(rivers)

    # Add a layer control to toggle historical regions and rivers
    folium.LayerControl().add_to(m)

    # Adjust legend for color display
    legend_html = '<div style="position: fixed; bottom: 50px; left: 50px; width: 150px; height: {}px; background-color: white; border:2px solid grey; z-index:9999; font-size:14px;">'\
                  '&nbsp; <b>Legend</b> <br>'.format(25 + len(unique_flags) * 20)
    for flag, color in color_mapping.items():
        legend_html += '&nbsp; <i style="background:{}; width: 15px; height: 15px; float: left; margin-right: 5px;"></i>{}<br>'.format(color, flag)
    legend_html += '</div>'
    m.get_root().html.add_child(folium.Element(legend_html))

    m.save(path_out)
    # Display the map
    return m

# example usage
map = visualize_map(raw_data.indiaish+raw_data.indiaish_rivers, chronologies.tracts.flags, 'examples/magic_test_old.html')