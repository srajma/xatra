import requests
import os
import json
import overpy
from chronologies.matchers import *

"""HELPER FUNCTIONS"""

def get_lev(gid_code):
    return gid_code.count('.')

def GID_max(feature):
    """
    This function takes a dictionary where keys are in the format "GID_n" and returns the highest "n" and its corresponding value.
    If the value for the highest "n" is None, it finds the next highest "n" with a non-None value.
    
    :param d: Dictionary with keys in the format "GID_n"
    :return: Dictionary with the highest "n" and its corresponding value if exists, else returns None for "GID_n"
    """
    d = feature["properties"]
    
    max_n = -1
    max_gid = None
    
    # Iterate through the dictionary to find the highest "n"
    for key, value in d.items():
        if key.startswith("GID_") and value is not None:
            try:
                # Extract the number after "GID_" and convert it to integer
                n = int(key[4:])
                if n > max_n:
                    max_n = n
                    max_gid = value
            except ValueError:
                # If conversion to integer fails, ignore this key
                continue
    
    # Check if a valid "GID_n" was found
    if max_n >= 0:
        return {"n": max_n, "GID_n": max_gid}
    else:
        return {"n": None, "GID_n": None}

def NAME_max(feature):
    """
    This function takes a dictionary where keys are in the format "GID_n" and returns the highest "n" and its corresponding value.
    If the value for the highest "n" is None, it finds the next highest "n" with a non-None value.
    
    :param d: Dictionary with keys in the format "GID_n"
    :return: Dictionary with the highest "n" and its corresponding value if exists, else returns None for "GID_n"
    """
    d = feature["properties"]
    
    max_n = -1
    max_name = None
    
    # Iterate through the dictionary to find the highest "n"
    for key, value in d.items():
        if key.startswith("NAME_") and value is not None:
            try:
                # Extract the number after "NAME_" and convert it to integer
                n = int(key[5:])
                if n > max_n:
                    max_n = n
                    max_name = value
            except ValueError:
                # If conversion to integer fails, ignore this key
                continue
    
    # Check if a valid "NAME_n" was found
    if max_n >= 0:
        return {"n": max_n, "NAME_n": max_name}
    else:
        return {"n": None, "NAME_n": None}

class Loka:
    def __init__(self, id, level, loc = "data/"):
        self.id = id
        self.level = level
        self.path = loc + f"loka_{id}_{level}.json"

class Break:
    def __init__(self, id, level, loc = "data/"):
        self.id = id
        self.level = level
        self.path = loc + f"break_{id}_{level}.json"

class Varuna:
    def __init__(self, item_id, item_type, name, loc = "data/"):
        self.item_id = item_id
        self.item_type = item_type # way or relation
        self.name = name
        self.path = loc + f"varuna_{item_type}_{item_id}_{name}.json"

"""ITEMS"""

loka_subcont = [
    Loka("IND", 2),
    Loka("PAK", 3),
    Loka("BGD", 2),
    Loka("LKA", 2),
    Loka("NPL", 3),
    Loka("BTN", 2)
]

loka_afghan = [
    Loka("AFG", 2)
]

loka_iranic = [
    Loka("IRN", 2),
    Loka("TJK", 2),
    Loka("UZB", 2),
    Loka("TKM", 2),
    Loka("KGZ", 2),
    Loka("KAZ", 2)
]

loka_sinic = [
    Loka("CHN", 2),
    Loka("MNG", 2),
]

loka_mainlandsea = [
    Loka("MMR", 2),
    Loka("THA", 2),
    Loka("LAO", 2),
    Loka("KHM", 2),
    Loka("VNM", 2)
]

loka_maritimesea = [
    Loka("MYS", 2),
    Loka("IDN", 2),
    Loka("BRN", 2),
    Loka("TLS", 2),
    Loka("SGP", 1)
]

loka_levant = [
    Loka("IRQ", 2),
    Loka("SYR", 2),
    Loka("LBN", 2),
    Loka("ISR", 1),
    Loka("PSE", 2),
    Loka("JOR", 2)
]

loka_gulf = [
    Loka("KWT", 1),
    Loka("BHR", 1),
    Loka("QAT", 1),
    Loka("ARE", 2),
    Loka("OMN", 2),
    Loka("SAU", 2),
    Loka("YEM", 2)
]

loka_mediterranean = [
    Loka("TUR", 2),
    Loka("GRC", 2),
    Loka("ITA", 2),
    Loka("EGY", 2),
    Loka("LBY", 1),
    Loka("TUN", 2)
]

loka_africa = [
    Loka("SOM", 2),
    Loka("TZA", 2),
    Loka("SDN", 2),
    Loka("DJI", 2),
    Loka("ERI", 2),
    Loka("MDG", 2)
]

loka = loka_africa+loka_gulf+loka_levant+loka_mainlandsea+loka_maritimesea+loka_mediterranean+loka_iranic+loka_sinic+loka_subcont+loka_afghan

breaks_subcont = [Break("IND.20.20_1", 3)]
breaks_sinic = [Break("CHN.28_1", 3)]

breaks = breaks_subcont+breaks_sinic

varuna_subcont = [
    Varuna("1236345", "relation", "ganga"),
    Varuna("326077", "relation", "yamuna"),
    Varuna("15793911", "relation", "sarayu"),
    Varuna("6722174", "relation", "ramaganga"),
    Varuna("12559166", "relation", "suvarnanadi"),
    Varuna("247787304", "way", "campa"),
    Varuna("13676883", "relation", "kaushika"),
    Varuna("5405552", "relation", "narmada"),
    Varuna("11117634", "relation", "kshipra"),
    Varuna("8385364", "relation", "chambal"),
    Varuna("2826093", "relation", "godavari"),
    Varuna("337204", "relation", "krsnaveni"),
    Varuna("2858525", "relation", "bhimarathi"),
    Varuna("2742213", "relation", "tungabhadra"),
    Varuna("2704746", "relation", "kaveri"),
    Varuna("1159233", "relation", "sindhu"),
    Varuna("8306691", "relation", "vitasta (jhelum)"),
    Varuna("6085682", "relation", "chandrabhaga (chenab)"),
    Varuna("8894611", "relation", "iravati (ravi)"),
    Varuna("325142", "relation", "satadru (sutlej)"),
    Varuna("10693630", "relation", "vipasa (beas)"),
    Varuna("5388381", "relation", "sarasvati (ghaggar)")
]

varuna_afghanistan = [
    Varuna("1676476", "relation", "kubha (kabul)"),
    Varuna("6608825", "relation", "kama (kunar)"),
    Varuna("8623883", "relation", "haraxvati (arghandab)"),
    Varuna("5252846", "relation", "haetumant (helmand)"),
    Varuna("3173475", "relation", "hari (hari)"),
    Varuna("223008", "relation", "vaksu (amu darya)")
]

varuna_iranic = [
    Varuna("223008", "relation", "vaksu (amu darya)"),
    Varuna("1206456", "relation", "jaxartes (syr darya)"),
    Varuna("2162521", "relation", "sita (tarim)")
]

varuna = list(set(varuna_subcont+varuna_afghanistan+varuna_iranic))

"""LOKA AND VARUNA FUNCTIONS"""

def download_gadm_from_url(item):
    url = f"https://geodata.ucdavis.edu/gadm/gadm4.1/json/gadm41_{item.id}_{item.level}.json"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()["features"]
    return None

def download_loka(lokas, breaks = [], dump = True, overwrite = False):
    break_ids = [b.id for b in breaks]
    all_features = []
    for item in lokas:
        if overwrite == True or not os.path.exists(item.path):
            features = download_gadm_from_url(item)
            print(f"Downloading to {item.path}")
            features = [
                feature for feature in features if not 
                any([feature["properties"].get("GID_" + str(get_lev(b.id)), "") == b.id for b in breaks])]
            all_features = all_features + features
            if dump:
                with open(item.path, 'w', encoding='utf-8') as f:
                    json.dump(features, f, indent = 4)
    for item in breaks:
        if overwrite == True or not os.path.exists(item.path):
            item_country = item.id.split('.')[0]
            features = download_gadm_from_url(Loka(item_country, item.level))
            print(f"Downloading to {item.path}")
            features = [feature for feature in features if feature["properties"].get("GID_" + str(get_lev(item.id)), "") == item.id]
            all_features = all_features + features
            if dump:
                with open(item.path, 'w', encoding='utf-8') as f:
                    json.dump(features, f, indent = 4)
    return all_features

# convert OSM style data to simple feature collection
def convert_to_geojson(result, name = "NA"):
    """convert OSM data to regular feature collection"""
    
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

# query overpass api
def download_river_OVERPASS(item_id, item_type, name = "NA"):
    api = overpy.Overpass()

    # Construct the query based on the item_id and item_type
    query = f"""
    [out:json];
    ({item_type}(id:{item_id}););
    out body;
    >;
    out skel qt;
    """

    result = api.query(query)
    return convert_to_geojson(result, name)

# main river download function
def download_varuna(varunas, overwrite = False):
    for item in varunas:
        if overwrite == True or not os.path.exists(item.path):
            print(f"Downloading to {item.path}")
            geojson_data = download_river_OVERPASS(item.item_id, item.item_type, item.name)
            with open(item.path, 'w') as file:
                file.write(geojson_data)

# load data as a dict
def load_data(
    objects, # e.g. loka + breaks + varuna
    filter = lambda x: True, # generally can be anything from chronologies.matchers
    padwithdumbshit = False
    ):
    all_data = []
    for item in objects:
        with open(item.path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            data_filtered = [x for x in data if filter(x)]
            all_data.extend(data_filtered)
    if padwithdumbshit:  
        all_data_geojson = {
            "type": "FeatureCollection",
            "crs": { "type": "name", "properties": { "name": "urn:ogc:def:crs:OGC:1.3:CRS84" } },
            "features" : all_data }
        return all_data_geojson
    else:
        return all_data

if __name__ == "__main__":    
    download_loka(loka, breaks)
    download_varuna(varuna)

indiaish = load_data(
    loka_subcont +  # add loka_sinic to include Aksai Chin; not needed since we're excluding Himalayan
    breaks_subcont, # regions with the filter anyway
    filter = SUBCONTINENT_PROPER
    )
afghanish = load_data(loka_afghan)
silkrd = load_data(
    loka_iranic + loka_afghan + 
    loka_sinic + breaks_sinic + # for xinjiang
    loka_subcont, # for balochistan and maybe INNER_KAMBOJA
    filter = union(CENTRAL_ASIA_GREATER, TARIM) # CENTRAL_ASIA to exclude INNER_KAMBOJA
    )
world = load_data(loka+breaks)

indiaish_rivers = load_data(varuna_subcont)
afghanish_rivers = load_data(varuna_afghanistan)
silkrd_rivers = load_data(varuna_iranic + varuna_afghanistan)
world_rivers = load_data(varuna)
