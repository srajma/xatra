import os
from importlib.resources import path
import json
import requests
import overpy
import pandas as pd
import geopandas as gpd
import topojson as tp
from xatra.data import *
from xatra.utilities import *
from xatra.matchers import *

data_dir = "xatra.data"
"""Folder to load data from, treated as a module"""


class DataItem:
    """Class that holds a single downloadable data item.

    Attributes:
        type (str): "feature", "break", "river", "city"
        id (str): Depends on type:
            - for feature -- e.g. "IND"
            - for break -- e.g. "IND.20.20_1"
            - for river -- e.g. "1236345"
        level (int): for feature or break, administrative detail level
        river_type (str): for river, "way" or "relation"
        common_name (str): for river, e.g. "ganga"
        filename (str): for feature or break, {type}_{id}_{level}.json;
            for river, f"{type}_{river_type}_{id}_{common_name}.json"

    Methods:
        download(path_out=None, overwrite=True): Downloads the data item and saves it into path_out.
        load(format="gpd", verbose=False): Load the data item from path(data_dir, self.filename).

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

    def _download_gadm(self):
        """Downloads a GADM file. Should only be used for DataItems of type "feature".

        Returns:
            Dict: GeoJSON Feature Collection

        """
        url = f"https://geodata.ucdavis.edu/gadm/gadm4.1/json/gadm41_{self.id}_{self.level}.json"
        response = requests.get(url)
        if response.status_code == 200:
            feature_collection = response.json()
            return feature_collection
        return None

    def _osm_to_geojson(self, result, name="NA"):
        """Convert OSM data to regular feature collection

        Args:
            result (dict): Dict returned by Overpass API
            name (str, optional): common name for river.

        Returns:
            dict: GeoJSON Feature Collection

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
        feature_collection = {"type": "FeatureCollection", "features": features}

        return feature_collection

    def _download_overpass(self, item):
        """Download data from Overpass API and passes it through _osm_to_geojson.
        Only for DataItems of type "river".

        Args:
            item (DataItem): DataItem to download

        Returns:
            Dict: GeoJSON Feature Collection
        """
        api = overpy.Overpass()

        query = f"""
        [out:json];
        ({item.river_type}(id:{item.id}););
        out body;
        >;
        out skel qt;
        """

        osm_result = api.query(query)
        feature_collection = self._osm_to_geojson(osm_result, item.common_name)
        return feature_collection

    def _download_break(self):
        """Download the data item.

        Returns:
            Dict: GeoJSON dict

        """
        item_country = DataItem(
            type="feature", id=self.id.split(".")[0], level=self.level
        )
        item_filter = Matcher.gid(self.id)
        feature_collection = item_country._download_gadm()
        feature_collection = item_filter.filter(feature_collection)
        return feature_collection

    def download(self, path_out=None, overwrite=True):
        """Download the data item and save it into path_out.

        Args:
            overwrite (bool): overwrite?
            path_out (str|None): directory to download the data into

        """
        if self.type == "feature":
            feature_collection = self._download_gadm()
        if self.type == "river":
            feature_collection = self._download_overpass(self)
        if self.type == "break":
            feature_collection = self._download_break()

        filepath = os.path.join(path_out, self.filename)
        if overwrite == True or not os.path.exists(filepath):
            print(f"Downloading to {filepath}")
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(feature_collection, f, indent=4)

    def load(self, format="gpd", tolerance=None, verbose=False):
        """Load the data item from path(data_dir, self.filename).

        Args:
            format (str, optional): "gpd" for geopandas dataframe, "featurecollection" for raw GeoJSON,
                "features" for just the ["features"] part of the raw GeoJSON. Defaults to "gpd".
            tolerance (float, optional): Simplify geometry. Defaults to None.
            verbose (bool, optional): Print progress. Defaults to False.

        Returns:
            GeoDataFrame|Dict|List[Dict]: Data.

        """
        if verbose:
            print(f"DataItem: Loading {self.filename} as {format}")
        with path(data_dir, self.filename) as filepath:
            gdf = gpd.read_file(filepath)
            # add NAME_max and GID_max properties to each feature
            gdf["NAME_max"] = gdf.apply(NAME_max, axis=1)
            gdf["GID_max"] = gdf.apply(GID_max, axis=1)
            if tolerance is not None:
                if verbose:
                    print(
                        f"DataItem: Simplifying geometry with TopoJSON with tolerance {tolerance}"
                    )
                # gdf.geometry = gdf.geometry.simplify(tolerance, preserve_topology=True)
                # ^ we need a topology-aware thing to avoid gaps and overlaps
                topo = tp.Topology(gdf, prequantize=False)
                gdf = topo.toposimplify(tolerance).to_gdf()
                if self.type == "feature" or self.type == "break":
                    gdf['geometry'] = gdf['geometry'].buffer(0) # fix invalid geometries
                if format == "gpd":
                    return gdf
                else:
                    print(f"DataItem: Converting simplified GDF into {format}")
                    if format == "features":
                        return features_from(gdf, to_list=True)
                    elif format == "featurecollection":
                        return featurecollection_from(gdf)
                    else:
                        raise ValueError(
                            "format must be 'gpd', 'featurecollection' or 'features'"
                        )
            elif format == "gpd":
                return gdf
            elif format == "featurecollection":
                if verbose:
                    print(f"DataItem: Converting GDF into featurecollection")
                return featurecollection_from(gdf)
            elif format == "features":
                if verbose:
                    print(f"DataItem: Converting GDF into features")
                return features_from(gdf, to_list=True)
            else:
                raise ValueError(
                    "format must be 'gpd', 'featurecollection' or 'features"
                )

    def __repr__(self):
        return f"DataItem at {self.filename}"

    def __add__(self, other):
        return DataCollection(self, other)

    def __hash__(self):
        return hash(self.filename)
    
    def __eq__(self, other):
        return self.filename == other.filename


class DataCollection:
    """Set of DataItems.

    Attributes:
        items (Set[DataItem]): Set of DataItems.
        filter (Matcher): Generally anything from xatra.matchers,
            decides which districts are loaded by self.load(). Defaults to Matcher.__true__()

    Methods:
        download(path_out=None, overwrite=True): Downloads all items in the DataCollection.
        load(verbose=False): Load DataItem items from item.filename.

    """

    def __init__(self, *args, filter=None):
        """Constructs a DataCollection from either a set of DataItems
        or as a union of other DataCollections. In particular we can define a new
        DataCollection y from a given one x changing the filter, as
        y = DataCollection(x, filter = ...).

        Args:
            *items: DataItems or DataCollections
            filter (Matcher), optional): Generally anything from
                xatra.matchers. Defaults to Matcher.__true__()

        """
        self.items = set()
        for arg in args:
            if isinstance(arg, DataCollection):
                self.items.update(arg.items)
            elif isinstance(arg, DataItem):
                self.items.add(arg)
        if filter is None:
            self.filter = Matcher.__true__()
        else:
            self.filter = filter

    def download(self, path_out=None, overwrite=True):
        """Downloads all items in the DataCollection. NOTE: this downloads
        everything regardless of breaks and self.filter, because we want to
        be able to define a new DataCollection from a given one changing the
        filter, as y = DataCollection(x, filter = ...).

        Args:
            path_out (str|None): path to download the data into, ending with "/"
            overwrite (bool): overwrite?

        """
        for item in self.items:
            item.download(path_out, overwrite)

    def load(self, format="gpd", tolerance=None, verbose=False):
        """Load DataItem items from item.filename.

        Args:
            format (str, optional): "gpd" for geopandas dataframe, "featurecollection" for raw GeoJSON,
                "features" for just the ["features"] part of the raw GeoJSON. Defaults to "gpd".
            tolerance (float, optional): Simplify geometry. Defaults to None.
            verbose (bool, optional): Print progress. Defaults to False.

        Returns:
            GeoDataFrame|Dict|List[Dict]: Data.

        """
        if verbose:
            print(f"DataCollection: Loading {len(self.items)} items")
        # filter defined by break: drop all features matching gid(item.id)
        break_filter = ~Matcher.__any__(
            [Matcher.gid(item.id) for item in self.items if item.type == "break"]
        )
        if format == "gpd":
            data = gpd.GeoDataFrame()
        elif format == "featurecollection":
            data = {"type": "FeatureCollection", "features": []}
        elif format == "features":
            data = []
        else:
            raise ValueError("format must be 'gpd', 'featurecollection' or 'features'")
        for item in self.items:
            if verbose:
                print(f"DataCollection: Loading {item.filename}")
            item_data = item.load(format=format, tolerance=tolerance, verbose=verbose)
            item_data = self.filter.filter(item_data)
            if item.type == "feature":
                item_data = break_filter.filter(item_data)
            if format == "gpd":
                data = pd.concat([data, item_data], ignore_index=True)
            elif format == "featurecollection":
                data["features"].extend(item_data["features"])
            else:
                data.extend(item_data)
        return data

    def __add__(self, other):
        return DataCollection(self, other)

    def __repr__(self):
        return "DataCollection with items:\n  {}".format(
            "\n  ".join([x.__repr__() for x in self.items])
        )
