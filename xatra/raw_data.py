import requests
import os
import json
import overpy
from importlib.resources import path
from .data import *
from .utilities import *
from .maps.matchers import *

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

class DataCollection:
    """List of DataItems.
    
    Attributes:
        items (List[DataItem]): A list of DataItems
    """
    def __init__(self, *args):
        """Constructs a DataCollection from either a list of DataItems
        or as a union of other DataCollections.
        
        Args:
            *args: A list of DataItems or DataCollections
        
        """
        items = []
        for item in args:
            if isinstance(item, DataItem):
                items.append(item)
            elif isinstance(item, DataCollection):
                items.extend(item.items)
        self.items = items
    
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

    def _convert_to_geojson(self, result, name = "NA"):
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
                "properties": {
                    "river_name": name,
                    "id": way.id,
                    "tags": way.tags
                },
                "geometry": {
                    "type": "LineString",
                    "coordinates": coordinates
                }
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
    
    def download(self, path_out = None, overwrite = True):
        """Downloads all items in the DataCollection
        
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
        should_overwrite = lambda item: path_out is not None and (overwrite == True or not os.path.exists(path_out + item.filename))
        
        all_data = []
        for item in features:                
            data = self._download_gadm(item)
            data = [
                x for x in data if not 
                any([x["properties"].get("GID_" + str(get_lev(b.id)), "") == b.id for b in breaks])]
            all_data.extend(data)
            
            if should_overwrite(item):
                print(f"Downloading to {path_out + item.filename}")
                with open(path_out + item.filename, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent = 4)

        for item in breaks:
            item_country = DataItem(type = "feature", id = item.id.split('.')[0], level = item.level)
            data = self._download_gadm(item_country)
            data = [
                x for x in data if 
                x["properties"].get("GID_" + str(get_lev(item.id)), "") == item.id]
            all_data.extend(data)
            
            if should_overwrite(item):
                print(f"Downloading to {path_out + item.filename}")
                with open(path_out + item.filename, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent = 4)
        
        for item in rivers:
            if should_overwrite(item):
                print(f"Downloading to {path_out + item.filename}")
                geojson_data = self._download_overpass(item)
                with open(path_out + item.filename, 'w') as file:
                    file.write(geojson_data)
        
        return all_data

    def load(self, filter = lambda x: True):
        """Load DataItem iztem from item.filename in path_in.

        Args:
            path_in (str): path to data
            filter (Callable[[Dict], bool], optional): Generally can be anything 
                from maps.matchers; Defaults to lambda x: True.

        Returns:
            List[Dict]: List of GeoJSON Dicts
        
        """
        all_data = []
        for item in self.items:
            with path(data_dir, item.filename) as file_path:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    data_filtered = [x for x in data if filter(x)]
                    all_data.extend(data_filtered)
        # to save in standard GeoJSON format
        # all_data = {
        #     "type": "FeatureCollection",
        #     "crs": { "type": "name", "properties": { "name": "urn:ogc:def:crs:OGC:1.3:CRS84" } },
        #     "features" : all_data }
        else:
            return all_data


loka_subcont = DataCollection(
    DataItem(type = "feature", id = "IND", level = 2),
    DataItem(type = "feature", id = "PAK", level = 3),
    DataItem(type = "feature", id = "BGD", level = 2),
    DataItem(type = "feature", id = "LKA", level = 2),
    DataItem(type = "feature", id = "NPL", level = 3),
    DataItem(type = "feature", id = "BTN", level = 2),
    DataItem(type = "break", id = "IND.20.20_1", level = 3)
)

loka_afghan = DataCollection(
    DataItem(type = "feature", id = "AFG", level = 2)
)

loka_iranic = DataCollection(
    DataItem(type = "feature", id = "IRN", level = 2),
    DataItem(type = "feature", id = "TJK", level = 2),
    DataItem(type = "feature", id = "UZB", level = 2),
    DataItem(type = "feature", id = "TKM", level = 2),
    DataItem(type = "feature", id = "KGZ", level = 2),
    DataItem(type = "feature", id = "KAZ", level = 2)
)

loka_sinic = DataCollection(
    DataItem(type = "feature", id = "CHN", level = 2),
    DataItem(type = "feature", id = "MNG", level = 2),
    DataItem(type = "break", id = "CHN.28_1", level = 3)
)

loka_mainlandsea = DataCollection(
    DataItem(type = "feature", id = "MMR", level = 2),
    DataItem(type = "feature", id = "THA", level = 2),
    DataItem(type = "feature", id = "LAO", level = 2),
    DataItem(type = "feature", id = "KHM", level = 2),
    DataItem(type = "feature", id = "VNM", level = 2)
)

loka_maritimesea = DataCollection(
    DataItem(type = "feature", id = "MYS", level = 2),
    DataItem(type = "feature", id = "IDN", level = 2),
    DataItem(type = "feature", id = "BRN", level = 2),
    DataItem(type = "feature", id = "TLS", level = 2),
    DataItem(type = "feature", id = "SGP", level = 1)
)

loka_levant = DataCollection(
    DataItem(type = "feature", id = "IRQ", level = 2),
    DataItem(type = "feature", id = "SYR", level = 2),
    DataItem(type = "feature", id = "LBN", level = 2),
    DataItem(type = "feature", id = "ISR", level = 1),
    DataItem(type = "feature", id = "PSE", level = 2),
    DataItem(type = "feature", id = "JOR", level = 2)
)

loka_gulf = DataCollection(
    DataItem(type = "feature", id = "KWT", level = 1),
    DataItem(type = "feature", id = "BHR", level = 1),
    DataItem(type = "feature", id = "QAT", level = 1),
    DataItem(type = "feature", id = "ARE", level = 2),
    DataItem(type = "feature", id = "OMN", level = 2),
    DataItem(type = "feature", id = "SAU", level = 2),
    DataItem(type = "feature", id = "YEM", level = 2)
)

loka_mediterranean = DataCollection(
    DataItem(type = "feature", id = "TUR", level = 2),
    DataItem(type = "feature", id = "GRC", level = 2),
    DataItem(type = "feature", id = "ITA", level = 2),
    DataItem(type = "feature", id = "EGY", level = 2),
    DataItem(type = "feature", id = "LBY", level = 1),
    DataItem(type = "feature", id = "TUN", level = 2)
)

loka_africa = DataCollection(
    DataItem(type = "feature", id = "SOM", level = 2),
    DataItem(type = "feature", id = "TZA", level = 2),
    DataItem(type = "feature", id = "SDN", level = 2),
    DataItem(type = "feature", id = "DJI", level = 2),
    DataItem(type = "feature", id = "ERI", level = 2),
    DataItem(type = "feature", id = "MDG", level = 2)
)

loka_silkrd = DataCollection(
    loka_iranic, 
    loka_afghan, 
    loka_sinic, # for xinjiang
    loka_subcont # for Balochistan, maybe Inner Kamboja
)

loka = DataCollection(
    loka_africa,
    loka_gulf,
    loka_levant,
    loka_mainlandsea,
    loka_maritimesea,
    loka_mediterranean,
    loka_iranic,
    loka_sinic,
    loka_subcont,
    loka_afghan
)

varuna_subcont = DataCollection(
    DataItem(type = "river", id = "1236345", river_type = "relation", common_name = "ganga"),
    DataItem(type = "river", id = "326077", river_type = "relation", common_name = "yamuna"),
    DataItem(type = "river", id = "15793911", river_type = "relation", common_name = "sarayu"),
    DataItem(type = "river", id = "6722174", river_type = "relation", common_name = "ramaganga"),
    DataItem(type = "river", id = "12559166", river_type = "relation", common_name = "suvarnanadi"),
    DataItem(type = "river", id = "247787304", river_type = "way", common_name = "campa"),
    DataItem(type = "river", id = "13676883", river_type = "relation", common_name = "kaushika"),
    DataItem(type = "river", id = "5405552", river_type = "relation", common_name = "narmada"),
    DataItem(type = "river", id = "11117634", river_type = "relation", common_name = "kshipra"),
    DataItem(type = "river", id = "8385364", river_type = "relation", common_name = "chambal"),
    DataItem(type = "river", id = "2826093", river_type = "relation", common_name = "godavari"),
    DataItem(type = "river", id = "337204", river_type = "relation", common_name = "krsnaveni"),
    DataItem(type = "river", id = "2858525", river_type = "relation", common_name = "bhimarathi"),
    DataItem(type = "river", id = "2742213", river_type = "relation", common_name = "tungabhadra"),
    DataItem(type = "river", id = "2704746", river_type = "relation", common_name = "kaveri"),
    DataItem(type = "river", id = "1159233", river_type = "relation", common_name = "sindhu"),
    DataItem(type = "river", id = "8306691", river_type = "relation", common_name = "vitasta (jhelum)"),
    DataItem(type = "river", id = "6085682", river_type = "relation", common_name = "chandrabhaga (chenab)"),
    DataItem(type = "river", id = "8894611", river_type = "relation", common_name = "iravati (ravi)"),
    DataItem(type = "river", id = "325142", river_type = "relation", common_name = "satadru (sutlej)"),
    DataItem(type = "river", id = "10693630", river_type = "relation", common_name = "vipasa (beas)"),
    DataItem(type = "river", id = "5388381", river_type = "relation", common_name = "sarasvati (ghaggar)")
)

varuna_afghanistan = DataCollection(
    DataItem(type = "river", id = "1676476", river_type = "relation", common_name = "kubha (kabul)"),
    DataItem(type = "river", id = "6608825", river_type = "relation", common_name = "kama (kunar)"),
    DataItem(type = "river", id = "8623883", river_type = "relation", common_name = "haraxvati (arghandab)"),
    DataItem(type = "river", id = "5252846", river_type = "relation", common_name = "haetumant (helmand)"),
    DataItem(type = "river", id = "3173475", river_type = "relation", common_name = "hari (hari)"),
    DataItem(type = "river", id = "223008", river_type = "relation", common_name = "vaksu (amu darya)")
)

varuna_iranic = DataCollection(
    DataItem(type = "river", id = "223008", river_type = "relation", common_name = "vaksu (amu darya)"),
    DataItem(type = "river", id = "1206456", river_type = "relation", common_name = "jaxartes (syr darya)"),
    DataItem(type = "river", id = "2162521", river_type = "relation", common_name = "sita (tarim)")
)

varuna_iranic_greater = DataCollection(varuna_iranic, varuna_afghanistan)

varuna = DataCollection(varuna_subcont, varuna_afghanistan, varuna_iranic)

indiaish = loka_subcont.load(filter = SUBCONTINENT_PROPER)
silkrd = loka_silkrd.load(filter = union(CENTRAL_ASIA_GREATER, TARIM)) # CENTRAL_ASIA to exclude INNER_KAMBOJA
world = loka.load()
subcont = DataCollection(loka_subcont, loka_sinic).load(filter = SUBCONTINENT)

indiaish_rivers = varuna_subcont.load()
afghanish_rivers = varuna_afghanistan.load()
silkrd_rivers = varuna_iranic_greater.load()
world_rivers = varuna.load()