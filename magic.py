import folium
import matplotlib
from folium.plugins import TimestampedGeoJson
import raw_data # raw_data.world
import chronologies.tracts # chronologies.tracts.flags, chronologies.tracts.custom_colors
from chronologies.matchers import is_river

def features_with_flags(features_list, flags_list, year=None):
    result = []
    for feature in features_list:
        feature_copies = []
        matching_flags = [
            flag["name"] for flag in flags_list if 
            flag["matcher"](feature) and 
            (year == None 
             or "period" not in flag 
             or (flag["period"][0] <= year < flag["period"][1]))]
        for flag_name in matching_flags:
            feature_copy = feature.copy()
            feature_copy["properties"]["flag"] = flag_name
            feature_copy["properties"]["flags"] = matching_flags
            feature_copy['properties']['NAME_max'] = raw_data.NAME_max(feature_copy)["NAME_n"] # for tooltip
            feature_copies.append(feature_copy)
        result.extend(feature_copies)
    return result

def breakpoints(flags_list):
    points = []
    for flag in flags_list:
        if "period" in flag:
            points.extend(flag["period"])
    return sorted(set(points))

def features_by_year(
    features_list,
    flags_list,
    breakpoint_years = None # optionally set your own years to choose to compute on
    ):
    if not breakpoint_years:
        breakpoint_years = breakpoints(flags_list)
    if breakpoint_years:
        return {
            year: features_with_flags(features_list, flags_list, year)
            for year in breakpoint_years
        }
    else:
        return {"static": features_with_flags(features_list, flags_list)}

def unique_flag_names(features_list, flags_list):
    fby = features_by_year(features_list, flags_list)
    flag_names_from_fby = [ # get a list of all relevant flags
        feature["properties"]["flag"] 
        for year, feature_list in fby.items() 
        for feature in feature_list]
    # ^ this would work, but we want them to be in the original order in flags_list, 
    # so we can assign a contrasting colour map to it 
    flag_names = [flag["name"] for flag in flags_list if flag["name"] in flag_names_from_fby]
    flag_names = list(dict.fromkeys(flag_names)) # make unique
    return flag_names

def cmap_contrasting(flag_names, custom_colors = None, segments = 8):
    cmap = matplotlib.cm.get_cmap('tab20', len(flag_names))
    color_mapping = {}
    colors_per_segment = max(1, cmap.N // segments) # Calculate the number of colors per segment

    # Assign colors from different segments to ensure contrast
    for i, flag_name in enumerate(flag_names):
        segment_index = i % segments
        color_index = (i // segments) % colors_per_segment
        color_position = segment_index * colors_per_segment + color_index
        color = cmap(color_position)[:3]  # Get the RGB part of the color
        color_mapping[flag_name] = matplotlib.colors.rgb2hex(color)
        
    # specific customizations
    for flag_name in color_mapping:
        if flag_name in custom_colors:
            color_mapping[flag_name] = custom_colors[flag_name]
    
    return color_mapping

def visualize_map(
    features_list, 
    flags_list, 
    rivers_list = None, 
    custom_colors = None,
    show_legend = True, 
    path_out = 'examples/magic.html'
    ):
    data = features_by_year(features_list, flags_list)
    flag_names = unique_flag_names(features_list, flags_list)
    cmap = cmap_contrasting(flag_names, custom_colors, segments = 8)

    m = folium.Map(location=[20.5937, 78.9629], zoom_start=5)  # Center on India
    
    # add layer for each breakpoint year
    for year, features in data.items():
        layer = folium.FeatureGroup(name=str(year))
        for feature in features:
            layer.add_child(folium.GeoJson(
                data = feature,
                name = "Flags DEBUG",
                style_function = lambda feature: {
                    'fillColor': cmap.get(feature['properties']['flag'], '#808080'),
                    'color': 'black',
                    'weight': 0,
                    'fillOpacity': 0.5,  # for visual overlap transparency
                    },
                tooltip=folium.GeoJsonTooltip(fields=['NAME_max', 'flags'], aliases=['NAME', 'Flag'])
            ))
        m.add_child(layer)

    # add rivers
    if rivers_list:
        rivers = folium.FeatureGroup(name='Rivers', show=True)
        for river in rivers_list:
            rivers.add_child(folium.GeoJson(
                data = river,
                style_function=lambda x: {'color': 'blue', 'weight': 2, 'fillOpacity': 0},
                tooltip=folium.GeoJsonTooltip(fields=['river_name', 'id'])
            ))
        m.add_child(rivers)
    
    # layer control
    folium.LayerControl().add_to(m)
    
    if show_legend:
        legend_html = '<div style="position: fixed; bottom: 50px; left: 50px; width: 150px; height: {}px; background-color: white; border:2px solid grey; z-index:9999; font-size:14px;">'\
                    '&nbsp; <b>Legend</b> <br>'.format(25 + len(flag_names) * 20)
        for flag, color in cmap.items():
            legend_html += '&nbsp; <i style="background:{}; width: 15px; height: 15px; float: left; margin-right: 5px;"></i>{}<br>'.format(color, flag)
        legend_html += '</div>'
        m.get_root().html.add_child(folium.Element(legend_html))
    
    m.save(path_out)
    
    return m

flags_test = [dict(flag, period = [-1000,1000]) for flag in chronologies.tracts.flags]

if __name__ == '__main__':
    visualize_map(
        features_list = raw_data.indiaish, 
        flags_list = chronologies.tracts.flags, 
        rivers_list = raw_data.indiaish_rivers, 
        custom_colors = chronologies.tracts.custom_colors,
        show_legend = False,
        path_out = 'examples/magic_test2.html')