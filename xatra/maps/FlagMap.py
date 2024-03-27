import folium
import folium.plugins
import matplotlib as mpl
import geopandas as gpd
from xatra.utilities import *
from xatra.data import DataCollection


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

    def __init__(self, name, matcher=None, period=None, ref=None):
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

        def __hash__(self):
            return hash(self.name, self.period)

        def __eq__(self, other):
            return self.name == other.name


class FlagMap:
    """A Map is defined by a list of Flags, some DataCollections, and optionally some custom colors.

    Attributes:
        flags (List[Flag]): List of flags
        loka (DataCollection): Stuff from Loka.
        varuna (DataCollection): Stuff from Varuna.
        loka_flagged (gpd.GeoDataFrame): loka with matching flag OBJECTS added as a column.
        breakpoints (List[int|float]): List of years at which territorial changes occur,
            according to self.flags. If empty, just ["static"].
        loka_flagged_yearwise (gpd.GeoDataFrame): loka_flagged, but here there is a column
            for each breakpoint year showing the matching flags within that period.
        unique_flag_names (List[str]): List of unique flag names for generating colour map.
        color_map (Dict[str, str]): Dict specifying the colour for each flag name.
        labels (List[Dict]): List of labels to add to the map, both calculated flag labels and
            specified custom labels.
        options (Dict[str, any]): See kwargs of __init__ for details. May be set either via
            __init__() or plot().

    Methods:
        plot: Plot with Folium.
        plot_flags: Alternative version of plot that merges the features by flag name and plots those
            instead of plotting each district. BROKEN.
        plot_flags_as_layers: Plot each flag as a separate layer, ignoring year/period, with Folium.
        plot_raw: Plot raw data with Folium.
        plot_mpl: Plot with Matplotlib.
        _load: Load loka and varuna, if not loaded already.
        _calc: Calculate breakpoints, color_map, loka_flagged, loka_flagged_yearwise.
            Only really called by plot.
        _flag_features: Get features for flag_name for year.
        _color: For a list of matching flags, return the average of the colours specified by
            self.color_map for each.

    """

    def __init__(self, flags, loka, varuna=None, **kwargs):
        """Initialize map with options. Lazy initialization of breakpoints, color_map, loka_flagged,
        loka_flagged_yearwise. They're only calculated when needed, i.e. when plot is called.

        Args:
            flags (List[Flag]): List of flags
            loka (DataCollection): Stuff from Loka.
            varuna (DataCollection, optional): Stuff from Varuna. Defaults to None.
            **kwargs: Recognized kwargs for options follow (any of these may also be set with plot()).

        Keyword Arguments:
            custom_colors (Dict[str, str]): custom colours for flags to override any calculated ones.
            color_segments (int): Flags within this distance of each other in self.flags will be assigned
                contrasting colours (unless forced otherwise in self.custom_colors). Defaults to 8.
            labels_on_map (bool): show flag labels on the map at calculated locations? (tooltips will show
                on hover regardless). Defaults to True.
            custom_labels (List[Dict]): custom labels to add to map. E.g.
                [
                    {
                        "label": "Persian Gulf", # set to key.name if not specified
                        "period": (-1000, -900),
                        "location": [29.9691899, 76.7260054],
                        "css" : { # inherits from self.css for attributes not specified
                            "font-size": "10pt",
                            "transform" : "rotate(20deg)",
                            "color" : "#000044",
                        }
                    }
                ]
            color_legend (bool): to include a legend of colours? Defaults to False.
            location (List[float]): Initial position of Folium map. Defaults to calculated from loka.
                E.g. India: [20.5937, 78.9629]. Brahmavarta: [29.9691899, 76.7260054]. Meru: [39, 71.9610313].
            zoom_start (int): Initial zoom of Folium map. Defaults to 5.
            custom_html (str): Custom HTML to be added to the top of the legend, e.g. a title. Defaults to "".
            opacity (float): Opacity of the map. Defaults to 0.7.
            css (Dict[str, str]): CSS for labels. Defaults to
                {
                    "font-size": "10pt",
                    "font-family": "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif",
                    "font-weight": "bold",
                    filter: "brightness(0.5)" # to make the text contrast with the map
                    color: None, # will be set to the flag color
                }
            tolerance (float): Tolerance for simplifying geometries. Defaults to 0.01.
            drop_orphans (bool): Drop features with no flags? Defaults to False.
            "base_maps" (Dict[str, bool]): Base maps to show. Those with value True will be shown by default,
                others will be options in the Layer Control. Defaults to
                {
                    "OpenStreetMap" : True,
                    "Esri.WorldImagery" : False,
                    "OpenTopoMap" : False,
                    "Esri.WorldPhysical" : False,
                }
                Stuff that
                you can include in the keys (can also be {} to have no base map):
                    "OpenStreetMap" (general all-rounder)
                    "CartoDB.Positron" (like OSM but light and minimalistic)
                    "CartoDB.PositronNoLabels" (like OSM but light and minimalistic)
                    "USGS.USImageryTopo" (physical map: satellite view)
                    "Esri.WorldImagery" (physical map: satellite view)
                    "OpenTopoMap" (physical map: topographic)
                    "Esri.WorldPhysical" (physical map: general)
                    "Esri.OceanBasemap" (physical map: rivers network)
                    See http://leaflet-extras.github.io/leaflet-providers/preview/ for a full list.
            verbose (bool): Print progress? Defaults to True.

        """
        self.flags = flags
        self.loka = loka
        self.varuna = varuna

        # default options
        self.options = {
            "custom_colors": {},
            "color_segments": 8,
            "labels_on_map": True,
            "custom_labels": [],
            "location": None,  # update this later after loading loka
            "zoom_start": 5,
            "custom_html": "",
            "color_legend": False,
            "opacity": 0.7,
            "css": {
                "font-size": "10pt",
                "font-family": "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif",
                "font-weight": "bold",
                "text-align": "center",
                "filter": "brightness(0.5)",
                "color": None,  # will be set to the flag color
            },
            "base_maps": {
                "OpenStreetMap": True,
                "Esri.WorldImagery": False,
                "OpenTopoMap": False,
                "Esri.WorldPhysical": False,
            },
            "drop_orphans": False,
            "tolerance": 0.01,
            "verbose": True,
        }
        self.options.update(kwargs)  # update with supplied arguments
        for k, v in self.options.items():  # set options as attributes
            setattr(self, k, v)

        # lazy initialization
        self.breakpoints = None
        self.unique_flag_names = None
        self.color_map = None
        self.loka_flagged = None
        self.loka_flagged_yearwise = None
        self._calculated = False

    def _load(self):
        """Load loka and varuna, if not loaded already."""
        if isinstance(self.loka, DataCollection):
            if self.verbose:
                print(f"Map: Loading loka")
            self.loka = self.loka.load(
                format="gpd", tolerance=self.tolerance, verbose=self.verbose
            )
        if self.varuna is not None and isinstance(self.varuna, DataCollection):
            if self.verbose:
                print(f"Map: Loading varuna")
            self.varuna = self.varuna.load(
                format="gpd", tolerance=self.tolerance, verbose=self.verbose
            )
        if self.location is None:
            if self.verbose:
                print(
                    f"Map: Calculating location, since not supplied in initialization"
                )
            self.options["location"] = [
                self.loka.geometry.centroid.y.mean(),  # self.loka.to_crs('+proj=cea').centroid.to_crs(self.loka.crs).x.mean(),
                self.loka.geometry.centroid.x.mean(),  # self.loka.to_crs('+proj=cea').centroid.to_crs(self.loka.crs).y.mean(),
            ]
            self.location = self.options["location"]

    def _calc_breakpoints(self):
        """Breakpoints at which the map needs to be computed, basically all
        the endpoints of each flag's period in self.flags. NOTE: self.breakpoints == []
        can be used to test if a map is static.

        """
        if self.verbose:
            print(f"Map: Calculating breakpoints")
        points = []
        for flag in self.flags:
            if flag.period is not None:
                points.extend(flag.period)
        if points == []:
            self.breakpoints = ["static"]
        else:
            self.breakpoints = sorted(set(points))

    def _calc_loka_flagged(self):
        """loka with matching flag OBJECTS added as a column."""
        if self.verbose:
            print(f"Map: copying loka for adding flags")
        loka_flagged = self.loka.copy()
        if self.verbose:
            print(f"Map: Adding flags to loka")

        def add_flags(row):
            if self.verbose:
                print(f"Map: Adding flags to {row['NAME_max']}")
            return [flag for flag in self.flags if flag.matcher(row)]

        loka_flagged["flags"] = loka_flagged.apply(add_flags, axis=1)
        if self.drop_orphans:
            if self.verbose:
                print(f"Map: Dropping orphans")
            loka_flagged = loka_flagged[
                loka_flagged["flags"].apply(lambda x: len(x) > 0)
            ]

        self.loka_flagged = loka_flagged

    def _calc_loka_flagged_yearwise(self):
        """loka with columns flag_y for each breakpoint year y, showing the matching
        flag NAMES for that year."""
        if self.verbose:
            print(f"Map: Copying loka for adding flags yearwise")
        loka_flagged_yearwise = self.loka_flagged.copy()
        for year in self.breakpoints:
            if self.verbose:
                print(f"Map: Adding column flags_{year}")
            loka_flagged_yearwise["flags_" + str(year)] = loka_flagged_yearwise.apply(
                lambda x: [
                    flag.name
                    for flag in x["flags"]
                    if flag.period is None
                    or year == "static"
                    or (flag.period[0] <= year < flag.period[1])
                ],
                axis=1,
            )
        # this is important for JSON serialization later in plot()
        loka_flagged_yearwise.drop(columns=["flags"], inplace=True)
        self.loka_flagged_yearwise = loka_flagged_yearwise

    def _calc_unique_flag_names(self):
        """List of unique flag names for generating colour map."""
        if self.verbose:
            print(f"Map: Calculating relevant flags")
        # get a list of all relevant flags
        flag_names = []
        for year in self.breakpoints:
            for flag_name in self.loka_flagged_yearwise["flags_" + str(year)]:
                flag_names.extend(flag_name)
        # ^ this would work, but we want them to be in the original order in self.flags,
        # so we can assign a contrasting colour map to it
        if self.verbose:
            print(f"Map: Doing a weird thing to maintain original order of flags")
        flag_names = [flag.name for flag in self.flags if flag.name in flag_names]
        if self.verbose:
            print(f"Map: Making unique")
        flag_names = list(dict.fromkeys(flag_names))
        self.unique_flag_names = flag_names

    def _calc_color_map(self):
        """Color map, calculated to ensure contrast between Flags that are within
        self.options["color_segments"] of each other in self.flags. Any colors specified
        in self.custom_colors overrides the ones automatically calculated."""
        if self.verbose:
            print(f"Map: Calculating color map")
        cmap = mpl.cm.get_cmap("tab20", len(self.unique_flag_names))
        color_mapping = {}
        colors_per_segment = max(
            1, cmap.N // self.color_segments
        )  # Calculate the number of colors per segment for contrast

        # Assign colors from different segments to ensure contrast
        for i, flag_name in enumerate(self.unique_flag_names):
            segment_index = i % self.color_segments
            color_index = (i // self.color_segments) % colors_per_segment
            color_position = segment_index * colors_per_segment + color_index
            color = cmap(color_position)[:3]  # Get the RGB part of the color
            color_mapping[flag_name] = mpl.colors.rgb2hex(color)

        # custom colors override calculated colors
        # not using .update() because we don't want to add new keys
        # since this also goes in the legend
        for flag_name in color_mapping:
            if flag_name in self.custom_colors:
                color_mapping[flag_name] = self.custom_colors[flag_name]

        self.color_map = color_mapping

    def _calc(self):
        """Calculate breakpoints, color_map, loka_flagged, loka_flagged_yearwise.
        Only really called by plot."""
        if not self._calculated:
            if self.verbose:
                print(f"Map: Got up from being lazy, calculating properies now.")
            self._load()
            self._calc_breakpoints()
            self._calc_loka_flagged()
            self._calc_loka_flagged_yearwise()
            self._calc_unique_flag_names()
            self._calc_color_map()
            self._calculated = True

    def _color(self, flag_names):
        """For a list of matching flags, return the average of the colours specified by
        self.color_map for each."""
        colors = [self.color_map[flag_name] for flag_name in flag_names]
        color = average_hex_color(colors)
        return {
            "fillColor": color,
            "color": color,
            "weight": 0,
            "fillOpacity": self.opacity,
        }

    def _flag_features(self, flag_name, year="static"):
        """Get features for flag_name for year."""
        if self.verbose:
            print(f"Map: Getting features for flag {flag_name} for year {year}")
        return self.loka_flagged_yearwise[
            self.loka_flagged_yearwise["flags_" + str(year)].apply(
                lambda x: flag_name in x
            )
        ]

    def _label(self, flag_name, year="static", flag_features=None):
        """Calculate flag label. You can either supply flag_features (e.g. if it has already been calculated),
        or it will be calculated."""
        if self.verbose:
            print(f"Map: Calculating label for flag {flag_name} for year {year}")
        if flag_features is None:
            flag_features = self._flag_features(flag_name, year)
        if flag_features.empty:
            return None
        location = [
            flag_features.geometry.centroid.y.mean(),
            flag_features.geometry.centroid.x.mean(),
        ]
        label = {
            "label": flag_name,
            "location": location,
            "css": {"color": self.color_map[flag_name]},
        }
        return label

    def _draw_base_map(self):
        """Return base map and base map layers list."""
        m = folium.Map(
            location=self.location,
            tiles=None,
            zoom_start=self.zoom_start,
            control_scale=True,
        )
        tile_layers = []
        for base_map, show in self.base_maps.items():
            layer = folium.TileLayer(base_map, overlay=True, show=show)
            tile_layers.append(layer)
            m.add_child(layer)
        return m, tile_layers

    def _draw_legend(self):
        if self.verbose:
            print(f"Map: Calculating legend HTML")
        object_height = "400px" if self.color_legend else "150px"

        legend_html = (
            '<div style="position: fixed; bottom: 50px; top: 50px; left: 50px; '
            f"width: 300px; height: {object_height}; padding: 10px; background-color: white; "
            'border:2px solid grey; z-index:9999; font-size:14px; overflow-y: scroll;">'
            + self.custom_html
        )
        if self.color_legend:
            legend_html += "<br><br>"
            for flag, color in self.color_map.items():
                legend_html += (
                    f'&nbsp; <i style="background:{color}; width: 15px; height: 15px; '
                    f'float: left; margin-right: 5px;"></i>{flag}<br>'
                )
        legend_html += "</div>"
        return folium.Element(legend_html)

    def _draw_label(self, label):
        """A label is a dictionary with the following keys:
        - label: the text to display
        - location: the location to display the label
        - css: a dictionary of CSS attributes to apply to the label
        """
        if self.verbose:
            print(f"Map: Adding custom label {label['label']} to map")
        css = self.css.copy()
        css.update(label.get("css", {}))
        css_string = "; ".join([f"{k}: {v}" for k, v in css.items()])
        return folium.Marker(
            location=label["location"],
            icon=folium.DivIcon(
                icon_size=(150, 36),
                icon_anchor=(75, 18),
                html=(f'<div style="{css_string}">{label["label"]}</div>'),
            ),
        )

    def _draw_flag_label(self, flag_name, year="static", flag_features=None):
        """Draw flag label. You can either supply flag_features (e.g. if it has already been calculated),
        or it will be calculated.
        """
        label = self._label(flag_name, year, flag_features)
        if label:
            return self._draw_label(label)
        else:
            return None
    
    def _draw_custom_labels(self):
        """Draw custom labels."""
        custom_layer = folium.FeatureGroup(name="Custom Labels", show=True)
        for label in self.custom_labels:
            custom_layer.add_child(self._draw_label(label))
        return custom_layer

    def _draw_loka(self, year="static"):
        """Draw loka.

        Returns:
            folium.FeatureGroup: Layer with loka.

        """
        loka = folium.FeatureGroup(name="Loka_" + str(year), show=True)
        loka.add_child(
            folium.GeoJson(
                data=self.loka_flagged_yearwise,
                style_function=lambda feature: self._color(
                    feature["properties"]["flags_" + str(year)]
                ),
                tooltip=folium.GeoJsonTooltip(
                    fields=["NAME_max", "flags_" + str(year)], aliases=["NAME", "Flag"]
                ),
            )
        )
        return loka

    def _draw_varuna(self, show=True):
        """Draw varuna.

        Returns:
            folium.FeatureGroup: Layer with rivers.

        """
        varuna = folium.FeatureGroup(name="Varuna", show=show)
        varuna.add_child(
            folium.GeoJson(
                data=self.varuna,
                style_function=lambda x: {
                    "color": "blue",
                    "weight": 2,
                    "fillOpacity": 0,
                },
                tooltip=folium.GeoJsonTooltip(fields=["river_name", "id"]),
            )
        )
        return varuna

    def plot(self, path_out=None, return_map=False, **kwargs):
        """Plot with Folium.

        Args:
            path_out (str, optional): To save the produced HTML somewhere. Defaults to None.
            return_map (bool, optional): Return the map object? Defaults to False.
            **kwargs: Allow user to update options while plotting.

        Returns:
            Folium.Map | None: Folium Map Object if return_map is True, else None
        """
        if self.verbose:
            print(f"Map: Plotting")
        self.options.update(kwargs)
        for k, v in self.options.items():  # set options as attributes
            setattr(self, k, v)

        self._calc()
        m, tile_layers = self._draw_base_map()
        year_layers = []
        for year in self.breakpoints:
            if self.verbose:
                print(f"Map: Adding layer for year {year}")
            layer = self._draw_loka(year)
            if self.labels_on_map:
                for flag in self.unique_flag_names:
                    flag_marker = self._draw_flag_label(flag, year)
                    if flag_marker:
                        layer.add_child(flag_marker)
            year_layers.append(layer)
            m.add_child(layer)
        if self.varuna is not None:
            m.add_child(self._draw_varuna())
        if self.custom_labels:
            m.add_child(self._draw_custom_labels())
        m.get_root().html.add_child(self._draw_legend())
        m.add_child(folium.LayerControl())
        if len(self.base_maps) > 1:
            m.add_child(
                folium.plugins.GroupedLayerControl(
                    groups={"Base maps": tile_layers},
                    autoZIndex=False,
                    exclusive_groups=False,
                )
            )
            
        if len(self.breakpoints) > 1:
            m.add_child(
                folium.plugins.GroupedLayerControl(
                    groups={"years": year_layers},
                    autoZIndex=False,
                    exclusive_groups=True,
                )
            )
        if self.verbose:
            print(f"Map: Saving to {path_out}")
        if path_out:
            m.save(path_out)
        if self.verbose:
            print(f"Map: Done")
        if return_map:
            return m

    # def plot_flags(self, path_out=None, return_map=False, **kwargs):
    #    """BROKEN"""
    #     """Alternative version of plot that merges the features by flag name and plots those
    #     instead of plotting each district. As before, each year is a separate layer.

    #     Args:
    #         path_out (str, optional): To save the produced HTML somewhere. Defaults to None.
    #         return_map (bool, optional): Return the map object? Defaults to False.
    #         **kwargs: Allow user to update options while plotting.

    #     Returns:
    #         Folium.Map | None: Folium Map Object if return_map is True, else None
    #     """
    #     if self.verbose:
    #         print(f"Map: Plotting flags")
    #     self.options.update(kwargs)
    #     for k, v in self.options.items():  # set options as attributes
    #         setattr(self, k, v)
    #     self._calc()
    #     m = folium.Map(
    #         location=self.location,
    #         tiles=None,
    #         zoom_start=self.zoom_start,
    #         control_scale=True,
    #     )
    #     tile_layers = []
    #     for base_map, show in self.base_maps.items():
    #         layer = folium.TileLayer(base_map, overlay=True, show=show)
    #         tile_layers.append(layer)
    #         m.add_child(layer)
    #     for year in self.breakpoints:
    #         if self.verbose:
    #             print(f"Map: Adding layer for year {year}")
    #         layer = folium.FeatureGroup(name=str(year), show=True)
    #         for flag in self.unique_flag_names:
    #             if self.verbose:
    #                 print(f"Map: Adding features for flag {flag} for year {year}")
    #             flag_features = self._flag_features(flag, year)
    #             if flag_features.crs is None:
    #                 flag_features.set_crs(self.loka.crs, inplace=True)
    #             if not flag_features.empty:
    #                 # use unary_union to merge the geometies and construct a new GeoDataFrame
    #                 # with columns "geometry" and "flag_name" and a single row
    #                 layer.add_child(
    #                     folium.GeoJson(
    #                         data=gpd.GeoDataFrame(
    #                             {
    #                                 "geometry": [flag_features.geometry.unary_union],
    #                                 "flag_name": [flag],
    #                             },
    #                             crs=self.loka.crs,
    #                         ),
    #                         style_function=lambda feature: self._color(
    #                             [feature["properties"]["flag_name"]]
    #                         ),
    #                         tooltip=folium.GeoJsonTooltip(
    #                             fields=["flag_name"], aliases=["Flag"]
    #                         ),
    #                     )
    #                 )
    #                 # actually, that doesn't work, because we need to set a CRS to transform geometries:
    #                 # layer.add_child(folium.GeoJson(data=gpd.GeoDataFrame({"geometry": [flag_features.geometry.unary_union], "flag_name": [flag]}).to_crs(self.loka.crs), style_function=lambda feature: self._color([feature["properties"]["flag_name"]]), tooltip=folium.GeoJsonTooltip(fields=["flag_name"], aliases=["Flag"])))
    #                 layer.add_child(self._draw_flag_label(flag, year, flag_features))
    #         m.add_child(layer)

    #     if self.varuna is not None:
    #         m.add_child(self._draw_varuna())
    #     if len(self.base_maps) > 1:
    #         m.add_child(
    #             folium.plugins.GroupedLayerControl(
    #                 groups={"Base maps": tile_layers},
    #                 autoZIndex=False,
    #                 exclusive_groups=False,
    #             )
    #         )
    #     m.add_child(folium.LayerControl())
    #     m.get_root().html.add_child(self._draw_legend())
    #     if path_out:
    #         if self.verbose:
    #             print(f"Map: Saving to {path_out}")
    #         m.save(path_out)
    #         if self.verbose:
    #             print(f"Map: Done")
    #     if return_map:
    #         return m

    def plot_flags_as_layers(self, path_out=None, return_map=False, **kwargs):
        """Plot each flag as a separate layer, ignoring year/period.

        Args:
            path_out (str, optional): To save the produced HTML somewhere. Defaults to None.
            return_map (bool, optional): Return the map object? Defaults to False.
            **kwargs: Allow user to update options while plotting.

        Returns:
            Folium.Map | None: Folium Map Object if return_map is True, else None
        """
        if self.verbose:
            print(f"Map: Plotting flags as layers")
        self.options.update(kwargs)
        for k, v in self.options.items():  # set options as attributes
            setattr(self, k, v)
        self._calc()
        m, tile_layers = self._draw_base_map()
        for flag in self.unique_flag_names:
            if self.verbose:
                print(f"Map: Adding layer for flag {flag}")
            layer = folium.FeatureGroup(name=flag, show=True)
            for year in self.breakpoints:
                if self.verbose:
                    print(f"Map: Adding features for flag {flag} for year {year}")
                features = self._flag_features(flag, year)
                layer.add_child(
                    folium.GeoJson(
                        data=features,
                        style_function=lambda feature: self._color(
                            feature["properties"]["flags_" + str(year)]
                        ),
                        tooltip=folium.GeoJsonTooltip(
                            fields=["NAME_max", "flags_" + str(year)],
                            aliases=["NAME", "Flag"],
                        ),
                    )
                )
                flag_marker = self._draw_flag_label(flag, year, features)
                if flag_marker:
                    layer.add_child(flag_marker)
            m.add_child(layer)
        if self.varuna is not None:
            m.add_child(self._draw_varuna())
        if self.custom_labels:
            m.add_child(self._draw_custom_labels())
        if len(self.base_maps) > 1:
            m.add_child(
                folium.plugins.GroupedLayerControl(
                    groups={"Base maps": tile_layers},
                    autoZIndex=False,
                    exclusive_groups=False,
                )
            )
        m.add_child(folium.LayerControl())
        m.get_root().html.add_child(self._draw_legend())
        if path_out:
            if self.verbose:
                print(f"Map: Saving to {path_out}")
            m.save(path_out)
            if self.verbose:
                print(f"Map: Done")
        if return_map:
            return m

    def _color_simple(self, gid1):
        colors = list(mpl.colors.CSS4_COLORS.values())
        return colors[hash(gid1) % len(colors)]

    def _tooltips(self, properties):
        return [
            key
            for key in properties.keys()
            if properties[key]
            and (
                key == "COUNTRY"
                or key.startswith("NAME_")
                or key.startswith("VARNAME_")
                or key.startswith("GID_")
            )
        ]

    def plot_raw(self, path_out=None, return_map=False, **kwargs):
        """Plot Raw data: i.e. plot loka and varuna, colouring loka by GID_1.

        Args:
            path_out (str, optional): To save the produced HTML somewhere. Defaults to None.
            return_map (bool, optional): Return the map object? Defaults to False.
            **kwargs: Allow user to update options while plotting.

        Returns:
            Folium.Map | None: Folium Map Object if return_map is True, else None
        """
        if self.verbose:
            print(f"Map: Plotting raw data")
        self.options.update(kwargs)
        self._load()
        for k, v in self.options.items():
            setattr(self, k, v)
        m = folium.Map(
            location=self.location,
            tiles=None,
            zoom_start=self.zoom_start,
            control_scale=True,
        )
        for base_map in self.base_maps:
            m.add_child(folium.TileLayer(base_map, overlay=True))
        loka = folium.FeatureGroup(name="Loka")
        for feature in features_from(self.loka):
            if self.verbose:
                print(f"Map: Adding feature {feature['properties']['NAME_max']}")
            loka.add_child(
                folium.GeoJson(
                    feature,
                    style_function=lambda x: {
                        "fillColor": self._color_simple(x["properties"]["GID_1"]),
                        "color": "black",
                        "weight": 0.5,
                        "fillOpacity": 0.7,
                    },
                    tooltip=folium.GeoJsonTooltip(
                        fields=self._tooltips(feature["properties"])
                    ),
                )
            )
        m.add_child(loka)
        if self.varuna is not None:
            m.add_child(self._draw_varuna())
        m.add_child(folium.LayerControl())
        m.get_root().html.add_child(self._draw_legend())
        if path_out:
            if self.verbose:
                print(f"Map: Saving to {path_out}")
            m.save(path_out)
            if self.verbose:
                print(f"Map: Done")
        if return_map:
            return m
