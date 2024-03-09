import os
from importlib.resources import path
import json
import requests
import overpy
import folium
import matplotlib.colors as mcolors
import geopandas as gpd
from xatra.data import *
from xatra.utilities import *
from xatra.matchers import *

data_dir = "xatra.data"
"""Folder to load data from, treated as a module"""


class DataItem:
    """Class that holds a single downloadable data item.

    Attributes:
        type (str): "feature", "break" or "river"
        id (str): Depends on type:
            - for feature -- e.g. "IND"
            - for break -- e.g. "IND.20.20_1"
            - for river -- e.g. "1236345"
        level (int): for feature or break, administrative detail level
        river_type (str): for river, "way" or "relation"
        common_name (str): for river, e.g. "ganga"
        filename (str): for feature or break, {type}_{id}_{level}.json;
            for river, f"{type}_{river_type}_{id}_{common_name}.json"

    """

    def __init__(self, type, id, **kwargs):
        """Constructs a Data Item

        Args:
            type (str): "feature", "break" or "river"
            id (str): Depends on type.
                - for feature -- e.g. "IND"
                - for break -- e.g. "IND.20.20_1"
                - for river -- e.g. "1236345"
            **kwargs: Accepted kwargs depend on type.
                - level (int): for feature or break, administrative detail level
                - river_type (str): for river, "way" or "relation"
                - common_name (str): for river, e.g. "ganga"

        """
        self.type = type
        self.id = id
        if type == "feature" or type == "break":
            self.level = kwargs["level"]
            self.filename = f"{type}_{id}_{self.level}.json"
        if type == "river":
            self.river_type = kwargs["river_type"]
            self.common_name = kwargs["common_name"]
            self.filename = f"{type}_{self.river_type}_{id}_{self.common_name}.json"


class DataCollection():
    """List of DataItems.

    Attributes:
        items (List[DataItem]): A list of DataItems
        filter (Callable[[Dict], bool]): Generally anything from xatra.matchers,
            decides which districts are loaded by self.load(). Defaults to
            lambda x: True
        name (str): Name of the DataCollection. Defaults to None.

    """

    def __init__(self, *args, filter=lambda x: True):
        """Constructs a DataCollection from either a list of DataItems
        or as a union of other DataCollections. In particular we can define a new
        DataCollection y from a given one x changing the filter, as
        y = DataCollection(x, filter = ...).

        Args:
            *items: A list of DataItems or DataCollections
            filter (Callable[[Dict], bool], optional): Generally anything from
                xatra.matchers. Defaults to lambda x: True

        """
        self.items = []
        for arg in args:
            if isinstance(arg, DataCollection):
                self.items.extend(arg.items)
            elif isinstance(arg, DataItem):
                self.items.append(arg)
        self.filter = filter

    def _download_gadm(self, item):
        """Downloads a GADM file.

        Args:
            item (DataItem): a DataItem file that is of type "feature"

        Returns:
            Dict: GeoJSON dict

        """
        url = f"https://geodata.ucdavis.edu/gadm/gadm4.1/json/gadm41_{item.id}_{item.level}.json"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()["features"]
        return None

    def _convert_to_geojson(self, result, name="NA"):
        """Convert OSM data to regular feature collection

        Args:
            result (dict): Dict returned by Overpass API
            name (str, optional): common name for river.

        Returns:
            dict: GeoJSON dict

        """
        features = []

        for way in result.ways:
            # Convert Decimal to float for JSON serialization
            coordinates = [[float(node.lon), float(node.lat)] for node in way.nodes]
            feature = {
                "type": "Feature",
                "properties": {"river_name": name, "id": way.id, "tags": way.tags},
                "geometry": {"type": "LineString", "coordinates": coordinates},
            }
            features.append(feature)

        # to save in standard GeoJSON format
        # geojson = {
        #     "type": "FeatureCollection",
        #     "features": features
        # }

        return json.dumps(features, indent=4)

    def _download_overpass(self, item):
        """Download data from Overpass API.

        Args:
            item (DataItem): DataItem to download
        """
        api = overpy.Overpass()

        query = f"""
        [out:json];
        ({item.river_type}(id:{item.id}););
        out body;
        >;
        out skel qt;
        """

        result = api.query(query)
        return self._convert_to_geojson(result, item.common_name)

    def download(self, path_out=None, overwrite=True):
        """Downloads all items in the DataCollection. NOTE: this downloads
        everything regardless of self.filter, because we want to be able to
        define a new DataCollection from a given one changing the filter, as
        y = DataCollection(x, filter = ...).

        Args:
            path_out (str|None): path to download the data into, ending with "/"
            overwrite (bool): overwrite?

        Returns:
            List[Dict]: list of GeoJSON dicts, equivalent to the file that
                would have been saved

        """
        features = [item for item in self.items if item.type == "feature"]
        breaks = [item for item in self.items if item.type == "break"]
        rivers = [item for item in self.items if item.type == "river"]
        should_overwrite = lambda item: path_out is not None and (
            overwrite == True or not os.path.exists(path_out + item.filename)
        )

        all_data = []
        for item in features:
            data = self._download_gadm(item)
            data = [
                x
                for x in data
                if not any(
                    [
                        x["properties"].get("GID_" + str(get_lev(b.id)), "") == b.id
                        for b in breaks
                    ]
                )
            ]
            all_data.extend(data)

            if should_overwrite(item):
                print(f"Downloading to {path_out + item.filename}")
                with open(path_out + item.filename, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=4)

        for item in breaks:
            item_country = DataItem(
                type="feature", id=item.id.split(".")[0], level=item.level
            )
            data = self._download_gadm(item_country)
            data = [
                x
                for x in data
                if x["properties"].get("GID_" + str(get_lev(item.id)), "") == item.id
            ]
            all_data.extend(data)

            if should_overwrite(item):
                print(f"Downloading to {path_out + item.filename}")
                with open(path_out + item.filename, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=4)

        for item in rivers:
            if should_overwrite(item):
                print(f"Downloading to {path_out + item.filename}")
                geojson_data = self._download_overpass(item)
                with open(path_out + item.filename, "w") as file:
                    file.write(geojson_data)

        return all_data

    def load(self, verbose=False):
        """Load DataItem items from item.filename.

        Returns:
            List[Dict]: List of GeoJSON Dicts

        """
        all_data = []
        for item in self.items:
            if verbose:
                print(f"DataCollection: Loading {item.filename}")
            with path(data_dir, item.filename) as file_path:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if verbose:
                        print(f"DataCollection: Filtering {item.filename}")
                    data_filtered = [x for x in data if self.filter(x)]
                    all_data.extend(data_filtered)
        # to save in standard GeoJSON format
        # all_data = {
        #     "type": "FeatureCollection",
        #     "crs": { "type": "name", "properties": { "name": "urn:ogc:def:crs:OGC:1.3:CRS84" } },
        #     "features" : all_data }
        else:
            return all_data

    # Function to filter tooltip fields based on specific criteria
    def _filter_tooltip_fields(self, properties):
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

    # Function to generate a color based on GID_1
    def _color_producer(self, gid1):
        colors = list(mcolors.CSS4_COLORS.values())
        return colors[hash(gid1) % len(colors)]

    def plot(self, path_out=None, verbose=False):
        """Plot Raw Data

        Args:
            filter (Callable[[Dict], bool], optional): Generally can be anything
                from xatra.matchers; Defaults to lambda x: True.

        """
        feature_list = self.load(verbose=verbose)

        if verbose:
            print(f"DataCollection: Calculating center")
        gdf = gpd.GeoDataFrame.from_features(feature_list)
        center = [gdf.geometry.centroid.y.mean(), gdf.geometry.centroid.x.mean()]
        m = folium.Map(location=center, zoom_start=5)

        rivers = folium.FeatureGroup(name="Rivers", show=True)
        districts = folium.FeatureGroup(name="Districts")

        for feature in feature_list:
            if is_river(feature):
                if verbose:
                    print(f"DataCollection: Adding river {feature['properties']['river_name']} ({feature['properties']['id']})")
                folium.GeoJson(
                    feature,
                    style_function=lambda x: {
                        "color": "blue",
                        "weight": 3,
                        "fillOpacity": 0.7,
                    },
                    tooltip=folium.GeoJsonTooltip(fields=["river_name", "id"]),
                ).add_to(rivers)
            else:
                if verbose:
                    print(f"DataCollection: Adding feature {NAME_max(feature)['NAME_n']}")
                folium.GeoJson(
                    feature,
                    style_function=lambda x: {
                        "fillColor": self._color_producer(x["properties"]["GID_1"]),
                        "color": "black",
                        "weight": 0.5,
                        "fillOpacity": 0.7,
                    },
                    tooltip=folium.GeoJsonTooltip(
                        fields=self._filter_tooltip_fields(feature["properties"])
                    ),
                ).add_to(districts)

        # Add the feature groups to the map
        districts.add_to(m)
        rivers.add_to(m)

        # Add a layer control to toggle rivers
        folium.LayerControl().add_to(m)
        
        if verbose:
            print(f"DataCollection: Saving to {path_out}")
        
        # Save to HTML
        m.save(path_out)
        
        if verbose:
            print(f"DataCollection: Done")
        
        return m


class Loka:
    """Holder class for your favourite feature DataCollections.
    - Loka for feature DataCollections
    - Varuna for river DataCollections
    - Pura for city DataCollections
    - Mixed for mixed/combined DataCollections
    """

    INDIAN_SUBCONTINENT_LOC = DataCollection(
        DataItem(type="feature", id="IND", level=2),
        DataItem(type="feature", id="PAK", level=3),
        DataItem(type="feature", id="BGD", level=2),
        DataItem(type="feature", id="LKA", level=2),
        DataItem(type="feature", id="NPL", level=3),
        DataItem(type="feature", id="BTN", level=2),
        DataItem(type="break", id="IND.20.20_1", level=3),
    )
    """Indian subcontinent, modern political boundaries, excludes Afghanistan.
    INDIAN_SUBCONTINENT_LOC excludes Chinese claims, INDIAN_SUBCONTINENT includes it."""

    INDIAN_SUBCONTINENT = DataCollection(
        INDIAN_SUBCONTINENT_LOC,
        DataItem(type="feature", id="CHN", level=2),
        filter=SUBCONTINENT,
    )
    """Indian subcontinent, modern political boundaries, excludes Afghanistan.
    INDIAN_SUBCONTINENT_LOC excludes Chinese claims, INDIAN_SUBCONTINENT includes it."""

    IRANIAN_SUBCONTINENT = DataCollection(
        DataItem(type="feature", id="IRN", level=2),
        DataItem(type="feature", id="TJK", level=2),
        DataItem(type="feature", id="UZB", level=2),
        DataItem(type="feature", id="TKM", level=2),
        DataItem(type="feature", id="KGZ", level=2),
        DataItem(type="feature", id="KAZ", level=2),
    )
    """Iranian subcontinent, modern political boundaries, excludes Afghanistan."""

    AFGHANISTAN = DataCollection(DataItem(type="feature", id="AFG", level=2))
    """Afghanistan, modern political boundaries."""

    CHINESE_SUBCONTINENT = DataCollection(
        DataItem(type="feature", id="CHN", level=2),
        DataItem(type="feature", id="MNG", level=2),
        DataItem(type="break", id="CHN.28_1", level=3),
    )
    """East Asia, modern political boundaries. TODO: include Japan and Korea"""

    SEA_MAINLAND = DataCollection(
        DataItem(type="feature", id="IND", level=2), # Andaman and Nicobar, North-East India
        DataItem(type="feature", id="MMR", level=2),
        DataItem(type="feature", id="THA", level=2),
        DataItem(type="feature", id="LAO", level=2),
        DataItem(type="feature", id="KHM", level=2),
        DataItem(type="feature", id="VNM", level=2),
        filter = SEA_MAINLAND
    )
    """Mainland Southeast Asia. Excludes North Vietnam and Kachin (in Burma)"""

    SEA_MARITIME = DataCollection(
        DataItem(type="feature", id="MYS", level=2),
        DataItem(type="feature", id="IDN", level=2),
        DataItem(type="feature", id="BRN", level=2),
        DataItem(type="feature", id="TLS", level=2),
        DataItem(type="feature", id="SGP", level=1),
        filter = SEA_MARITIME
    )
    """Maritime Southeast Asia."""

    SEA = DataCollection(SEA_MAINLAND, SEA_MARITIME, filter = SEA)
    """Southeast Asia. Excludes North Vietnam and Kachin (in Burma)."""
    
    LEVANT = DataCollection(
        DataItem(type="feature", id="IRQ", level=2),
        DataItem(type="feature", id="SYR", level=2),
        DataItem(type="feature", id="LBN", level=2),
        DataItem(type="feature", id="ISR", level=1),
        DataItem(type="feature", id="PSE", level=2),
        DataItem(type="feature", id="JOR", level=2),
    )
    """Levant, modern political boundaries. Excludes Kuwait."""

    GULF = DataCollection(
        DataItem(type="feature", id="KWT", level=1),
        DataItem(type="feature", id="BHR", level=1),
        DataItem(type="feature", id="QAT", level=1),
        DataItem(type="feature", id="ARE", level=2),
        DataItem(type="feature", id="OMN", level=2),
        DataItem(type="feature", id="SAU", level=2),
        DataItem(type="feature", id="YEM", level=2),
    )
    """Gulf, modern political boundaries. Includes Kuwait and Yemen."""

    MEDITERRANEAN = DataCollection(
        DataItem(type="feature", id="TUR", level=2),
        DataItem(type="feature", id="GRC", level=2),
        DataItem(type="feature", id="ITA", level=2),
        DataItem(type="feature", id="EGY", level=2),
        DataItem(type="feature", id="LBY", level=1),
        DataItem(type="feature", id="TUN", level=2),
    )
    """Mediterranean, modern political boundaries. TODO: Include a lot of things."""

    AFRICA_EAST = DataCollection(
        DataItem(type="feature", id="SOM", level=2),
        DataItem(type="feature", id="TZA", level=2),
        DataItem(type="feature", id="SDN", level=2),
        DataItem(type="feature", id="DJI", level=2),
        DataItem(type="feature", id="ERI", level=2),
        DataItem(type="feature", id="MDG", level=2),
    )
    """East Africa, modern political boundaries."""

    INDOSPHERE = DataCollection(
        INDIAN_SUBCONTINENT,
        IRANIAN_SUBCONTINENT,
        AFGHANISTAN,
        CHINESE_SUBCONTINENT,
        SEA,
        filter = INDOSPHERE
    )
    """Akhand Bharat"""
    
    WORLD = DataCollection(
        AFRICA_EAST,
        GULF,
        LEVANT,
        SEA_MAINLAND,
        SEA_MARITIME,
        MEDITERRANEAN,
        AFGHANISTAN,
        IRANIAN_SUBCONTINENT,
        CHINESE_SUBCONTINENT,
        INDIAN_SUBCONTINENT,
    )
    """Everything we've got."""

    INDIC = DataCollection(INDIAN_SUBCONTINENT, filter=SUBCONTINENT_PROPER)
    """Core areas of India in antiquity. TODO: figure out valley regions in UK etc."""

    SILKRD = DataCollection(
        IRANIAN_SUBCONTINENT,
        AFGHANISTAN,
        CHINESE_SUBCONTINENT,  # for xinjiang
        INDIAN_SUBCONTINENT,  # for Balochistan, maybe Inner Kamboja
        filter=union(CENTRAL_ASIA_GREATER, TARIM),
    )
    """Iranic regions, Afghanistan, Tarim baisin and NW Frontier territories of Pakistan."""

    NEXUS = DataCollection(SILKRD, filter=union(CENTRAL_ASIA_GREATER, TARIM, AUDICYA))
    """Iranic regions, Afghanistan, Tarim basin and Audichya region of the Indian subcontinent"""


class Varuna:
    """Holder class for your favourite river DataCollections.
    - Loka for feature DataCollections
    - Varuna for river DataCollections
    - Pura for city DataCollections
    - Mixed for mixed/combined DataCollections
    """

    NORTHINDIAN = DataCollection(
        DataItem(
            type="river", id="1236345", river_type="relation", common_name="ganga"
        ),
        DataItem(
            type="river", id="326077", river_type="relation", common_name="yamuna"
        ),
        DataItem(
            type="river", id="15793911", river_type="relation", common_name="sarayu"
        ),
        DataItem(
            type="river", id="6722174", river_type="relation", common_name="ramaganga"
        ),
        DataItem(
            type="river",
            id="12559166",
            river_type="relation",
            common_name="suvarnanadi",
        ),
        DataItem(type="river", id="247787304", river_type="way", common_name="campa"),
        DataItem(
            type="river", id="13676883", river_type="relation", common_name="kaushika"
        ),
        DataItem(
            type="river",
            id="5388381",
            river_type="relation",
            common_name="sarasvati (ghaggar)",
        ),
        DataItem(
            type="river", id="11117634", river_type="relation", common_name="kshipra"
        ),
        DataItem(
            type="river", id="8385364", river_type="relation", common_name="chambal"
        ),
    )
    """Rivers of Northern India, excluding the Audichya region."""

    PENINSULAR = DataCollection(
        DataItem(
            type="river", id="5405552", river_type="relation", common_name="narmada"
        ),
        DataItem(
            type="river", id="2826093", river_type="relation", common_name="godavari"
        ),
        DataItem(
            type="river", id="337204", river_type="relation", common_name="krsnaveni"
        ),
        DataItem(
            type="river", id="2858525", river_type="relation", common_name="bhimarathi"
        ),
        DataItem(
            type="river", id="2742213", river_type="relation", common_name="tungabhadra"
        ),
        DataItem(
            type="river", id="2704746", river_type="relation", common_name="kaveri"
        ),
    )
    """Rivers of Peninsular India"""

    SAPTASINDHU = DataCollection(
        DataItem(
            type="river", id="1159233", river_type="relation", common_name="sindhu"
        ),
        DataItem(
            type="river",
            id="8306691",
            river_type="relation",
            common_name="vitasta (jhelum)",
        ),
        DataItem(
            type="river",
            id="6085682",
            river_type="relation",
            common_name="chandrabhaga (chenab)",
        ),
        DataItem(
            type="river",
            id="8894611",
            river_type="relation",
            common_name="iravati (ravi)",
        ),
        DataItem(
            type="river",
            id="325142",
            river_type="relation",
            common_name="satadru (sutlej)",
        ),
        DataItem(
            type="river",
            id="10693630",
            river_type="relation",
            common_name="vipasa (beas)",
        ),
    )
    """Rivers of the Audichya region"""

    INDIAN_SUBCONTINENT = DataCollection(NORTHINDIAN, PENINSULAR, SAPTASINDHU)
    """Rivers of the Indian Subcontinent"""

    AFGHANISTAN = DataCollection(
        DataItem(
            type="river",
            id="1676476",
            river_type="relation",
            common_name="kubha (kabul)",
        ),
        DataItem(
            type="river",
            id="6608825",
            river_type="relation",
            common_name="kama (kunar)",
        ),
        DataItem(
            type="river",
            id="8623883",
            river_type="relation",
            common_name="haraxvati (arghandab)",
        ),
        DataItem(
            type="river",
            id="5252846",
            river_type="relation",
            common_name="haetumant (helmand)",
        ),
        DataItem(
            type="river", id="3173475", river_type="relation", common_name="hari (hari)"
        ),
        DataItem(
            type="river",
            id="223008",
            river_type="relation",
            common_name="vaksu (amu darya)",
        ),
    )
    """Rivers of Afghanistan"""

    IRANIAN_SUBCONTINENT = DataCollection(
        DataItem(
            type="river",
            id="223008",
            river_type="relation",
            common_name="vaksu (amu darya)",
        ),
        DataItem(
            type="river",
            id="1206456",
            river_type="relation",
            common_name="jaxartes (syr darya)",
        ),
    )
    """Oxus and Jaxartes"""

    SILKRD = DataCollection(
        IRANIAN_SUBCONTINENT,
        AFGHANISTAN,
        DataItem(
            type="river",
            id="2162521",
            river_type="relation",
            common_name="sita (tarim)",
        ),
    )
    """Oxus, Jaxartes, Tarim and Afghan rivers"""

    WORLD = DataCollection(INDIAN_SUBCONTINENT, SILKRD)
    """All rivers we have"""

    NEXUS = DataCollection(SILKRD, SAPTASINDHU)
    """Oxus, Jaxartes, Tarim, Afghan rivers and Audichya (Sapta-Sindhu) rivers"""


class Combined:
    """Holder class for your favourite mixed DataCollections.
    - Loka for feature DataCollections
    - Varuna for river DataCollections
    - Pura for city DataCollections
    - Mixed for mixed/combined DataCollections
    """

    INDIAN_SUBCONTINENT_LOC = DataCollection(
        Loka.INDIAN_SUBCONTINENT_LOC,
        Varuna.INDIAN_SUBCONTINENT,
        filter=union(Loka.INDIAN_SUBCONTINENT_LOC.filter, is_river),
    )
    INDIAN_SUBCONTINENT = DataCollection(
        Loka.INDIAN_SUBCONTINENT,
        Varuna.INDIAN_SUBCONTINENT,
        filter=union(Loka.INDIAN_SUBCONTINENT.filter, is_river),
    )
    IRANIAN_SUBCONTINENT = DataCollection(
        Loka.IRANIAN_SUBCONTINENT,
        Varuna.IRANIAN_SUBCONTINENT,
        filter=union(Loka.IRANIAN_SUBCONTINENT.filter, is_river),
    )
    AFGHANISTAN = DataCollection(
        Loka.AFGHANISTAN,
        Varuna.AFGHANISTAN,
        filter=union(Loka.AFGHANISTAN.filter, is_river),
    )
    # no rivers defined yet for these regions:
    # CHINESE_SUBCONTINENT
    # SEA_MAINLAND
    # SEA_MARITIME
    # LEVANT
    # GULF
    # MEDITERRANEAN
    # AFRICA_EAST
    WORLD = DataCollection(
        Loka.WORLD, Varuna.WORLD, filter=union(Loka.WORLD.filter, is_river)
    )
    INDIC = DataCollection(
        Loka.INDIC,
        Varuna.INDIAN_SUBCONTINENT,
        filter=union(Loka.INDIC.filter, is_river),
    )
    SILKRD = DataCollection(
        Loka.SILKRD, Varuna.SILKRD, filter=union(Loka.SILKRD.filter, is_river)
    )
    NEXUS = DataCollection(
        Loka.NEXUS, Varuna.NEXUS, filter=union(Loka.NEXUS.filter, is_river)
    )
