import folium
import matplotlib
from folium.plugins import TimestampedGeoJson
from xatra.utilities import NAME_max

class Flag:
    """A "Flag" is a declaration that a particular polity (Flag.name) ruled 
    over some particular set of features (Flag.matcher), optionally for some
    particular specific period of history (Flag.period).
    
    Attributes:
        name (str): Name of polity
        matcher (Callable[[Dict], bool]): Function that returns True onn the
            set of features included by the Flag.
        period (tuple[int|float, int|float] | None): tuple of start and end years, for
            dynamic Maps
        ref (str | None): source for claim
    
    """
    def __init__(self, name, matcher, period = None, ref = None):
        """Constructs a Flag.

        Args:
            name (str): Name of polity
            matcher (Callable[[Dict], bool]): Function that returns True onn the
                set of features included by the Flag.
            period (tuple[int|float, int|float], optional): tuple of start and end years,
                for dynamic Maps
            ref (str, optional): source for claim
        """
        self.name = name
        self.matcher = matcher
        self.period = period
        self.ref = ref

class Map:
    """A Map is a list of Flags. It can be plotted with the .plot() method.
    
    Attributes:
        flags (List[Flag]): List of flags
        geojson (List[Dict]): List of features (GeoJSON dicts), loaded from xatra.raw_data
        geojson_rivers (List[Dict]): List of rivers (GeoJSON dicts), loaded from xatra.raw_data
        breakpoints (List[int|float]): List of years at which territorial changes occur,
            according to self.flags.
        geojson_by_year (Dict[int|float, List[Dict]]): Dict showing for each year, the GeoJSON
            with matching flags appended to each feature.
        custom_colors (Dict[str, str]): Dictionary mapping Flag names to custom (not calculated) 
            Hex colors. Can be empty.
        legend_options (Dict[str, any]): Dictionary with legend options `color_legend : bool`, 
            `custom_html : str`, `size : float`, `names_on_map : bool`
        folium_init (Dict[str, any]): Dict specifying where to center Folium map.
        color_map (Dict[str, str]): Dict specifying the colour for each flag name.
        
    """
    
    def __init__(
        self, 
        flags, 
        geojson,
        geojson_rivers = [], 
        custom_colors = {}, 
        legend_options = None,
        folium_init = "India",
        _color_segments = 8):
        """Construct a Map.

        Args:
            flags (List[Flag]): List of Flags.
            geojson (List[Dict], optional): List of features (GeoJSON dicts) to use as the Map base.
                Defaults to [].
            geojson_rivers (List[Dict]): List of rivers (GeoJSON dicts) to be shown.
            custom_colors (dict, optional): Custom colours to force. Remaining colours 
                will be computed. Defaults to {}.
            legend_options (None | Dict[str, any], optional): Dictionary with legend options. Defaults 
                to None.
            folium_init (str | Dict[str, any], optional): Dictionary specifying where to center Folium map.
                Alternatively, a recognized string ("india", "meru", "kurukshetra" or "brahmavarta"). 
                Defaults to "india".
            _color_segments (int, optional): Flags within this distance of each other in
                self.flags will be assigned contrasting colours (unless forced otherwise
                in self.custom_colors). Defaults to 8.
                
        """
        self.flags = flags
        self.geojson = geojson
        self.geojson_rivers = geojson_rivers
        self.custom_colors = custom_colors
        
        # switch for legend_options
        if legend_options is None:
            self.legend_options = {
                "color_legend" : True,
                "custom_html" : "",
                "size" : 1.0,
                "names_on_map" : True
            }
        else:
            self.legend_options = legend_options
        
        # switch for folium_init
        if type(folium_init) is str:
            if folium_init.lower() == "meru":
                self.folium_init = {
                    "location" : [39, 71.9610313],
                    "zoom_start" : 5
                }
            elif folium_init.lower() in ["kuruksetra", "kurukshetra", "kuruxetra", "brahmavarta"]:
                self.folium_init = {
                    "location" : [29.9691899, 76.7260054],
                    "zoom_start" : 5
                }
            else: # by default, "india"
                self.folium_init = {
                    "location" : [20.5937, 78.9629],
                    "zoom_start" : 5
                }
        else:
            self.folium_init = folium_init
        
        self._color_segments = _color_segments
        
        # cache properties
        self.breakpoints = self._calc_breakpoints()
        self.geojson_by_year = self._calc_geojson_by_year()
        self._unique_flag_names = self._calc_unique_flag_names()
        self.color_map = self._calc_color_map()

    def _calc_breakpoints(self):
        """Breakpoints at which the map needs to be computed, basically all
        the endpoints of each flag's period in self.flags. NOTE: self.breakpoints == []
        can be used to test if a map is static.
        
        """
        points = []
        for flag in self.flags:
            if flag.period is not None:
                points.extend(flag.period)
        return sorted(set(points))
    
    def _geojson_with_flags(self, year=None):
        """self.geojson with list of claiming flags in a particular year 
        added to each feature. To be used in self.geojson_by_year

        Args:
            year (int|float, optional): _description_. Defaults to None.

        Returns:
            List[Dict]: List of Dicts where each such dict["properties"] has additional
            keys "flag", "flags", and "NAME_max".
            
        """
        result = []
        for feature in self.geojson:
            feature_copies = []
            matching_flags = [
                flag.name for flag in self.flags if 
                flag.matcher(feature) and 
                (year == None 
                or flag.period is not None 
                or (flag.period[0] <= year < flag.period[1]))]
            for flag_name in matching_flags:
                feature_copy = feature.copy()
                feature_copy["properties"]["flag"] = flag_name
                feature_copy["properties"]["flags"] = matching_flags
                feature_copy['properties']['NAME_max'] = NAME_max(feature_copy)["NAME_n"] # for tooltip
                feature_copies.append(feature_copy)
            result.extend(feature_copies)
        return result    
    
    def _calc_geojson_by_year(self):
        """Dict showing for each year, the GeoJSON with matching flags appended to each feature, i.e.
        a dictionary of year : self._geojson_with_flags(year). For a static map it will simply return
        { "static": self._geojson_with_flags() }.

        Returns:
            Dict[int|float|str, List[Dict]]: as described
            
        """
        if self.breakpoints:
            return { year: self._geojson_with_flags(year) for year in self.breakpoints }
        else:
            return { "static": self._geojson_with_flags() }
    
    def _calc_unique_flag_names(self):
        """List of unique flag names for generating colour map.

        Returns:
            List[str]: List of unique flag names in self.flags.
        
        """
        # get a list of all relevant flags
        flag_names_from_fby = [
            feature["properties"]["flag"] 
            for year, feature_list in self.geojson_by_year.items() 
            for feature in feature_list]
        # ^ this would work, but we want them to be in the original order in self.flags, 
        # so we can assign a contrasting colour map to it 
        flag_names = [flag.name for flag in self.flags if flag.name in flag_names_from_fby]
        flag_names = list(dict.fromkeys(flag_names)) # make unique
        return flag_names
    
    def _calc_color_map(self):
        """Color map, calculated to ensure contrast between Flags that are within
        self._color_segments of each other in self._unique_flag_names (which is also
        roughly the same as being within that distance in self.flags). Any colors specified
        in self.custom_colors overrides the ones automatically calculated.

        Returns:
            Dict[str, str]: Dict specifying the colour for each flag name.
            
        """
        flag_names = self._unique_flag_names
        cmap = matplotlib.cm.get_cmap('tab20', len(flag_names))
        color_mapping = {}
        colors_per_segment = max(1, cmap.N // self._color_segments) # Calculate the number of colors per segment

        # Assign colors from different segments to ensure contrast
        for i, flag_name in enumerate(flag_names):
            segment_index = i % self._color_segments
            color_index = (i // self._color_segments) % colors_per_segment
            color_position = segment_index * colors_per_segment + color_index
            color = cmap(color_position)[:3]  # Get the RGB part of the color
            color_mapping[flag_name] = matplotlib.colors.rgb2hex(color)
            
        # custom colors override calculated colors
        for flag_name in color_mapping:
            if flag_name in self.custom_colors:
                color_mapping[flag_name] = self.custom_colors[flag_name]
        
        return color_mapping

    def plot(self, path_out = None):
        """Plot with Folium.

        Args:
            path_out (str, optional): To save the produced HTML somewhere. Defaults to None.

        Returns:
            Folium.Map: Folium Map Object
        """

        m = folium.Map(**self.folium_init)
        
        # add layer for each breakpoint year
        for year, features in self.geojson_by_year.items():
            layer = folium.FeatureGroup(name=str(year))
            for feature in features:
                layer.add_child(folium.GeoJson(
                    data = feature,
                    name = "Flags",
                    style_function = lambda feature: {
                        'fillColor': self.color_map.get(feature['properties']['flag'], '#808080'),
                        'color': 'black',
                        'weight': 0,
                        'fillOpacity': 0.5,  # for visual overlap transparency
                        },
                    tooltip=folium.GeoJsonTooltip(fields=['NAME_max', 'flags'], aliases=['NAME', 'Flag'])
                ))
            m.add_child(layer)

        # add rivers
        if self.geojson_rivers:
            rivers = folium.FeatureGroup(name='Rivers', show=True)
            for river in self.geojson_rivers:
                rivers.add_child(folium.GeoJson(
                    data = river,
                    style_function=lambda x: {'color': 'blue', 'weight': 2, 'fillOpacity': 0},
                    tooltip=folium.GeoJsonTooltip(fields=['river_name', 'id'])
                ))
            m.add_child(rivers)
        
        # layer control
        folium.LayerControl().add_to(m)
        
        if self.legend_options["color_legend"]:
            legend_html = '<div style="position: fixed; bottom: 50px; left: 50px; width: 150px; height: {}px; background-color: white; border:2px solid grey; z-index:9999; font-size:14px;">'\
                        '&nbsp; <b>Legend</b> <br>'.format(25 + len(self._unique_flag_names) * 20)
            for flag, color in self.color_map.items():
                legend_html += '&nbsp; <i style="background:{}; width: 15px; height: 15px; float: left; margin-right: 5px;"></i>{}<br>'.format(color, flag)
            legend_html += '</div>'
            m.get_root().html.add_child(folium.Element(legend_html))
        
        if path_out:
            m.save(path_out)
        
        return m

