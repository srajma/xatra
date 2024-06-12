from copy import deepcopy
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


class Label:
    """Label class.

    Attributes:
        type (str): Type of label: "flag_label", "custom_label", "city".
        name (str): Text of label
        period (tuple[int|float, int|float] | None): tuple of start and end years, for dynamic Maps
        location (List[float]): Location of label
        css (Dict[str, str]): CSS for label
        css_bullet (Dict[str, str]): CSS for bullet, only for type "city"
        ref (str | None): source for claim
    """

    def __init__(
        self, type, name, location, period=None, css=None, css_bullet=None, ref=None
    ):
        """Constructs a Label.

        Args:
            type (str): Type of label: "flag_label", "custom_label", "city".
            name (str): Text of label
            period (tuple[int|float, int|float], optional): tuple of start and end years, for dynamic Maps
            location (List[float]): Location of label
            css (Dict[str, str], optional): CSS for label. NOTE: Do NOT give conflicting CSS for the same
                property, as dicts do not have order, and the behaviour would be unpredictable. Also always
                use individual property names (e.g. "margin-left") instead of shorthands (e.g. "margin"),
                this is important for a hack we use in _draw_label to align things correctly.
            css_bullet (Dict[str, str], optional): CSS for bullet, only for type "city". NOTE: Do NOT give conflicting CSS for the same
                property, as dicts do not have order, and the behaviour would be unpredictable. Also always
                use individual property names (e.g. "margin-left") instead of shorthands (e.g. "margin"),
                this is important for a hack we use in _draw_label to align things correctly.
            ref (str, optional): source for claim
        """
        self.type = type
        self.name = name
        self.period = period
        self.location = location
        self.css = {} if css is None else css
        self.css_bullet = {} if css_bullet is None else css_bullet
        self.ref = ref

    def __str__(self):
        if self.type == "city":
            return f"{self.name} at {self.location} ({self.type}) with CSS\n {self.css} and bullet CSS\n {self.css_bullet}"
        else:
            return f"{self.name} at {self.location} ({self.type}) with CSS\n {self.css}"

    css_default = {
        "flag_label": {
            "font-size": "10pt",
            "font-family": "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif",
            "font-weight": "bold",
            "text-align": "center",
            "filter": "brightness(0.5)",
            "color": "#000000",  # will be updated with the flag color
        },
        "custom_label": {
            "font-size": "10pt",
            "font-family": "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif",
            "font-weight": "bold",
            "text-align": "center",
            "color": "#666666",
        },
        "city": {
            "font-size": "10pt",
            "font-family": "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif",
            "font-weight": "bold",
            "text-align": "left",
            "color": "#000000",
        },
        "city_bullet": {
            "display": "inline-block",
            "margin-right": "5px",
            "height": "5pt",
            "width": "5pt",
            "background-color": "#000000",
            "border-radius": "50%",
        },
    }

class Path:
    
    def __init__(self, name, points, **kwargs):
        """Path object.
        
        Args:        
            name (str): Name of the path, label.
            points (list[Label]): List of points.
        
        Keyword Args:
            weight (int): Weight of the path. Defaults to 2.
            color (str): Color of the path. Defaults to "black".
            opacity (float): Opacity of the path. Defaults to 1.0.
            dash_array (str): Dash array of the path. Defaults to "".
        """
        
        self.name = name
        self.points = points
        self.options = {
            "weight": 2,
            "color": "black",
            "opacity": 1.0,
            "dash_array": "",
        }
        self.options.update(kwargs)
    
    def add(self, other, name=None):
        """Add another path to this path.
        
        Args:
            other (Path): Other path to add.
            name (str, optional): Name of the new path. Defaults to None.
        
        Returns:
            Path: New path.
        """
        if name is None:
            name = self.name
        return Path(
            name=name,
            points=self.points + other.points[1:],
            **self.options
        )

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
        options (Dict[str, any]): See kwargs of __init__ for details. May be set either via
            __init__() or plot().

    Methods:
        plot: Plot with Folium. Set optional argument mode to "features", "flags", "flags_as_layers",
            or "raw" to control between the following modes (default is "flags"):
        plot_features: Plot with Folium by adding flags to each feature and plotting it. You will
            also get the name of the feature you're hovering over in the tooltip, instead of just
            the flag.
        plot_flags: Plot with Folium by merging the features by flag name and plots those instead of
            plotting each district.
        plot_flags_as_layers: Plot each flag as a separate layer, ignoring year/period, with Folium.
        plot_raw: Plot raw data with Folium.
        plot_mpl: Plot with Matplotlib.
        _load: Load loka and varuna, if not loaded already.
        _calc: Calculate breakpoints, color_map, loka_flagged, loka_flagged_yearwise.
            Only really called by plot.
        _flag_features: Get features for flag_name for year.
        _flag_gdf: Get features for flag_name for year, dissolved.
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
            paths (List[Path]): List of paths.
            color_segments (int): Flags within this distance of each other in self.flags will be assigned
                contrasting colours (unless forced otherwise in self.custom_colors). Defaults to 8.
            labels_on_map (bool): show flag labels on the map at calculated locations? (tooltips will show
                on hover regardless). Defaults to True.
            custom_labels (List[Label]): custom labels to add to map. E.g.
                [
                    Label(
                        type="custom_label", # or "flag_label", "city"
                        name="Persian Gulf",
                        period=(-1000, -900), # optional
                        location=[29.9691899, 76.7260054],
                        css={
                            "font-size": "10pt",
                            "transform": "rotate(20deg)",
                            "color": "#000044",
                        },
                    )
                ]
                Can include custom labels with type "custom_label", "city" or even "flag_label".
                Defaults to [].
            color_legend (bool): to include a legend of colours? Defaults to False.
            location (List[float]): Initial position of Folium map. Defaults to calculated from loka.
                E.g. India: [20.5937, 78.9629]. Brahmavarta: [29.9691899, 76.7260054]. Meru: [39, 71.9610313].
            zoom_start (int): Initial zoom of Folium map. Defaults to 5.
            custom_html (str): Custom HTML to be added to the top of the legend, e.g. a title. Defaults to "".
            opacity (float): Opacity of the map. Defaults to 0.7.
            css (Dict[str, Dict[str, str]]): CSS for labels. NOTE: Do NOT give conflicting CSS for the same
                property, as dicts do not have order, and the behaviour would be unpredictable. Also always
                use individual property names (e.g. "margin-left") instead of shorthands (e.g. "margin"),
                this is important for a hack we use in _draw_label to align things correctly.
                Defaults to xatra.Label.css_default.
            css_legend (Dict[str, str]): CSS for legend. Defaults to {
                "font-family": "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif",
                "position": "fixed",
                "bottom": "50px",
                "top": "50px",
                "left": "50px",
                "width": "300px",
                "height": "min-content",
                "max-height": "400px",
                "padding": "10px",
                "background-color": "white",
                "border": "2px solid grey",
                "z-index": "9999",
                "font-size": "10pt",
                "overflow-y": "scroll",
            }
            tolerance (float): Tolerance for simplifying geometries. Defaults to 0.01.
            drop_orphans (bool): Drop features with no flags? Defaults to False.
            "base_maps" (tuple(List[str], List[str])): Base maps to show. The first element is the maps shown by default;
                the second are the remaining options in the Layer Control. Defaults to
                "base_maps": (
                    ["OpenStreetMap"],
                    ["Esri.WorldImagery", "OpenTopoMap", "Esri.WorldPhysical"]
                )
                Stuff that you can include in the keys (can also be [] to have no base map):
                    "OpenStreetMap" (general all-rounder)
                    "CartoDB.Positron" (like OSM but light and minimalistic)
                    "CartoDB.PositronNoLabels" (like OSM but light and minimalistic)
                    "USGS.USImageryTopo" (physical map: satellite view)
                    "Esri.WorldImagery" (physical map: satellite view)
                    "OpenTopoMap" (physical map: topographic)
                    "Esri.WorldPhysical" (physical map: general)
                    "Esri.OceanBasemap" (physical map: rivers network)
                    See http://leaflet-extras.github.io/leaflet-providers/preview/ for a full list.
            show_loka (bool): Show loka? Defaults to True.
            show_varuna (bool): Show varuna? Defaults to False.
            verbose (bool): Print progress? Defaults to True.

        """
        self.flags = flags
        self.loka = loka
        self.varuna = varuna

        # default options
        self.options = {
            "paths": [],
            "custom_colors": {},
            "color_segments": 8,
            "labels_on_map": True,
            "custom_labels": [],
            "location": None,  # update this later after loading loka
            "zoom_start": 5,
            "custom_html": "",
            "color_legend": False,
            "opacity": 0.7,
            "css": deepcopy(Label.css_default),
            "css_legend": {
                "font-family": "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif",
                "position": "fixed",
                "bottom": "50px",
                "top": "50px",
                "left": "50px",
                "width": "300px",
                "height": "min-content",
                "max-height": "400px",
                "padding": "10px",
                "background-color": "white",
                "border": "2px solid grey",
                "z-index": "9999",
                "font-size": "10pt",
                "overflow-y": "scroll",
            },
            "base_maps": (
                ["OpenStreetMap"],
                ["Esri.WorldImagery", "OpenTopoMap", "Esri.WorldPhysical"],
            ),
            "show_loka": True,
            "show_varuna": True,
            "drop_orphans": False,
            "tolerance": 0.01,
            "verbose": True,
        }
        self._deep_update(kwargs)
        for k, v in self.options.items():  # set options as attributes
            setattr(self, k, v)

        # lazy initialization
        self.breakpoints = None
        self.unique_flag_names = None
        self.color_map = None
        self.loka_flagged = None
        self.loka_flagged_yearwise = None
        self._calculated = False

    def _deep_update(self, overrides, source=None):
        """Recursively update a dictionary.

        Args:
            overrides (dict): Dictionary with updates.
            source (dict, optional): Original dictionary to be updated. Defaults to
                self.options.

        Returns:
            dict: The updated dictionary.
        """
        if source is None:
            source = self.options
        for key, value in overrides.items():
            if (
                isinstance(value, dict)
                and key in source
                and isinstance(source[key], dict)
            ):
                source[key] = self._deep_update(value, source[key])
            else:
                source[key] = value
        return source

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
                lambda x: tuple(
                    [  # tuple because we will use it as a key later
                        flag.name
                        for flag in x["flags"]
                        if flag.period is None
                        or year == "static"
                        or (flag.period[0] <= year < flag.period[1])
                    ]
                ),
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
                print(
                    f"Map: Got up from being lazy, finally got around to calculating properies."
                )
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

    def _flag_gdf(self, flag_name, year="static", flag_features=None):
        """Get features for flag_name for year, dissolved."""
        if self.verbose:
            print(
                f"Map: Getting dissolved features for flag {flag_name} for year {year}"
            )
        if flag_features is None:
            flag_features = self._flag_features(flag_name, year)
        return flag_features.dissolve()

    def _label(self, flag_name, year="static", flag_gdf=None):
        """Calculate flag label. You can either supply flag_features (e.g. if it has already been calculated),
        or it will be calculated."""
        if self.verbose:
            print(f"Map: Calculating label for flag {flag_name} for year {year}")
        if flag_gdf is None:
            flag_gdf = self._flag_gdf(flag_name, year)
        if flag_gdf.empty:
            return None
        location = [
            flag_gdf.geometry.centroid.y.values[0],
            flag_gdf.geometry.centroid.x.values[0],
        ]
        label = Label(
            type="flag_label",
            name=flag_name,
            location=location,
            css={"color": self.color_map[flag_name]},
        )
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
        for base_map in self.base_maps[0]:
            layer = folium.TileLayer(base_map, overlay=True, show=True)
            tile_layers.append(layer)
            m.add_child(layer)
        for base_map in self.base_maps[1]:
            layer = folium.TileLayer(base_map, overlay=True, show=False)
            tile_layers.append(layer)
            m.add_child(layer)

        if len(tile_layers) > 0:
            layer_control = folium.plugins.GroupedLayerControl(
                groups={"Base maps": tile_layers},
                autoZIndex=False,
                exclusive_groups=False,
            )
        else:
            layer_control = None

        return m, layer_control

    def _draw_legend(self):
        if self.verbose:
            print(f"Map: Calculating legend HTML")
        css_string = css_str(self.css_legend)
        legend_html = f'<div style="{css_string}">' + self.custom_html
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
        if self.verbose:
            print(f"Map: Adding custom label {label.name} to map")
        css = self.css[label.type].copy()
        css.update(label.css)
        css_string = css_str(css)
        if label.type == "city":
            css_bullet = self.css["city_bullet"].copy()
            css_bullet.update(label.css_bullet)
            css_bullet_str = css_str(css_bullet)
            shift_x, shift_y = bullet_pos(css, css_bullet)
            return folium.Marker(
                location=label.location,
                icon=folium.DivIcon(
                    icon_size=(180, 36),
                    icon_anchor=(shift_x, 18-shift_y),
                    html=(
                        f'<div style="{css_string}">'
                        f'<span style="{css_bullet_str}"></span>'
                        f"{label.name}"
                        "</div>"
                    ),
                ),
            )
        else:
            return folium.Marker(
                location=label.location,
                icon=folium.DivIcon(
                    icon_size=(150, 36),
                    icon_anchor=(75, 18),
                    html=(f'<div style="{css_string}">{label.name}</div>'),
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

    def _draw_custom_labels(self, year="static"):
        """Draw custom labels."""
        relevant_labels = [
            label
            for label in self.custom_labels
            if label.period is None
            or year == "static"
            or (label.period[0] <= year < label.period[1])
        ]
        if relevant_labels:
            custom_layer = folium.FeatureGroup(name="Custom Labels", show=True)
            for label in relevant_labels:
                custom_layer.add_child(self._draw_label(label))
            return custom_layer
        else:
            return None
    
    def _draw_paths(self):
        """Draw paths."""
        if self.verbose:
            print(f"Map: Adding paths")
        
        if self.paths:
            paths = folium.FeatureGroup(name="Paths", show=True)
            for path in self.paths:
                points = [point.location for point in path.points]
                folium.PolyLine(
                    points,
                    **path.options
                ).add_to(paths)
                # add path name as a label
                # label = Label(
                #     type="custom_label",
                #     name=path.name,
                #     location=points[0],
                #     css={
                #         "color": path.options["color"],
                #         "font-size": "10pt",
                #         "font-weight": "bold",
                #     },
                # )
                # paths.add_child(self._draw_label(label))
            return paths
        else:
            return None

    def _draw_loka(self, year="static"):
        """Draw loka.

        Returns:
            folium.FeatureGroup: Layer with loka.

        """
        loka = folium.FeatureGroup(name="Loka_" + str(year), show=self.show_loka)
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

    def _draw_varuna(self):
        """Draw varuna.

        Returns:
            folium.FeatureGroup: Layer with rivers.

        """
        if self.verbose:
            print(f"Map: Adding Rivers")
        varuna = folium.FeatureGroup(name="Varuna", show=self.show_varuna)
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

    def plot_features(self, path_out=None, return_map=False, **kwargs):
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
        self._deep_update(kwargs)
        for k, v in self.options.items():  # set options as attributes
            setattr(self, k, v)
        self._calc()

        m, tiles_control = self._draw_base_map()

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
            custom_labels = self._draw_custom_labels(year)
            paths = self._draw_paths()
            if custom_labels:
                layer.add_child(custom_labels)
            if paths:
                layer.add_child(paths)
            year_layers.append(layer)
            m.add_child(layer)

        if self.varuna is not None:
            m.add_child(self._draw_varuna())

        m.get_root().html.add_child(self._draw_legend())

        m.add_child(folium.LayerControl())
        if tiles_control is not None:
            m.add_child(tiles_control)
        if len(self.breakpoints) > 1:
            m.add_child(
                folium.plugins.GroupedLayerControl(
                    groups={"years": year_layers},
                    autoZIndex=False,
                    exclusive_groups=True,
                )
            )
        if path_out:
            if self.verbose:
                print(f"Map: Saving to {path_out}")
            m.save(path_out)
        if self.verbose:
            print(f"Map: Done")
        if return_map:
            return m

    def plot_flags(self, path_out=None, return_map=False, **kwargs):
        """Alternative version of plot that merges the features by flag name and plots those
        instead of plotting each district. As before, each year is a separate layer.

        Args:
            path_out (str, optional): To save the produced HTML somewhere. Defaults to None.
            return_map (bool, optional): Return the map object? Defaults to False.
            **kwargs: Allow user to update options while plotting.

        Returns:
            Folium.Map | None: Folium Map Object if return_map is True, else None
        """
        if self.verbose:
            print(f"Map: Plotting flags")
        self._deep_update(kwargs)
        for k, v in self.options.items():
            setattr(self, k, v)
        self._calc()

        m, tiles_control = self._draw_base_map()

        year_layers = []
        for year in self.breakpoints:
            if self.verbose:
                print(f"Map: Adding layer for year {year}")
            layer = folium.FeatureGroup(name=str(year), show=True)
            flag_names_plotted = []  # to avoid plotting the same flag twice
            for flag_tuple in self.loka_flagged_yearwise["flags_" + str(year)].unique():
                if self.verbose:
                    print(
                        f"Map: Adding features for flag tuple {flag_tuple} for year {year}"
                    )
                features = self.loka_flagged_yearwise[
                    self.loka_flagged_yearwise["flags_" + str(year)] == flag_tuple
                ]
                layer.add_child(
                    folium.GeoJson(
                        data=features.dissolve(),
                        style_function=lambda feature, flag_tuple=flag_tuple: self._color(
                            flag_tuple
                        ),
                        tooltip=folium.GeoJsonTooltip(
                            fields=["flags_" + str(year)], aliases=["Flag"]
                        ),
                    )
                )
                if self.labels_on_map:
                    for flag_name in flag_tuple:
                        if flag_name not in flag_names_plotted:
                            flag_marker = self._draw_flag_label(flag_name, year)
                            if flag_marker:
                                layer.add_child(flag_marker)
            custom_labels = self._draw_custom_labels(year)
            paths = self._draw_paths()
            if custom_labels:
                layer.add_child(custom_labels)
            if paths:
                layer.add_child(paths)
            year_layers.append(layer)
            m.add_child(layer)

        if self.varuna is not None:
            m.add_child(self._draw_varuna())

        m.get_root().html.add_child(self._draw_legend())

        m.add_child(folium.LayerControl())
        if tiles_control is not None:
            m.add_child(tiles_control)
        if len(self.breakpoints) > 1:
            m.add_child(
                folium.plugins.GroupedLayerControl(
                    groups={"years": year_layers},
                    autoZIndex=False,
                    exclusive_groups=True,
                )
            )
        if path_out:
            if self.verbose:
                print(f"Map: Saving to {path_out}")
            m.save(path_out)
            if self.verbose:
                print(f"Map: Done")
        if return_map:
            return m

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
        self._deep_update(kwargs)
        for k, v in self.options.items():  # set options as attributes
            setattr(self, k, v)
        self._calc()
        m, tiles_control = self._draw_base_map()
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
                if self.labels_on_map:
                    flag_marker = self._draw_flag_label(flag, year)
                    if flag_marker:
                        layer.add_child(flag_marker)
                custom_labels = self._draw_custom_labels(year)
                paths = self._draw_paths()
                if custom_labels:
                    layer.add_child(custom_labels)
                if paths:
                    layer.add_child(paths)
            m.add_child(layer)
        if self.varuna is not None:
            m.add_child(self._draw_varuna())
        if tiles_control is not None:
            m.add_child(tiles_control)
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
        self._deep_update(kwargs)
        self._load()
        for k, v in self.options.items():
            setattr(self, k, v)
        m = folium.Map(
            location=self.location,
            tiles=None,
            zoom_start=self.zoom_start,
            control_scale=True,
        )
        m, tiles_control = self._draw_base_map()
        loka = folium.FeatureGroup(name="Loka", show=self.show_loka)
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
                        "fillOpacity": self.opacity,
                    },
                    tooltip=folium.GeoJsonTooltip(
                        fields=self._tooltips(feature["properties"])
                    ),
                )
            )
        m.add_child(loka)
        if self.varuna is not None:
            m.add_child(self._draw_varuna())
        custom_labels = self._draw_custom_labels()
        paths = self._draw_paths()
        if custom_labels:
            m.add_child(custom_labels)
        if paths:
            m.add_child(paths)
        if tiles_control is not None:
            m.add_child(tiles_control)
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

    def plot(self, mode="flags", path_out=None, return_map=False, **kwargs):
        """
        Plot.

        Args:
            mode (str, optional): One of "flags", "flags_as_layers", "raw". Defaults to "flags".
            path_out (str, optional): To save the produced HTML somewhere. Defaults to None.
            return_map (bool, optional): Return the map object? Defaults to False.
            **kwargs: Allow user to update options while plotting.
        """
        if mode == "flags":
            return self.plot_flags(path_out=path_out, return_map=return_map, **kwargs)
        elif mode == "flags_as_layers":
            return self.plot_flags_as_layers(
                path_out=path_out, return_map=return_map, **kwargs
            )
        elif mode == "raw":
            return self.plot_raw(path_out=path_out, return_map=return_map, **kwargs)
        else:
            return self.plot_features(
                path_out=path_out, return_map=return_map, **kwargs
            )
