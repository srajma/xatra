"""
HELPER FUNCTIONS
"""

import pandas as pd
import geopandas as gpd
from shapely.geometry import shape

def css_str(css : dict):
    """Converts a CSS dictionary to a string.

    Args:
        css (dict): CSS dictionary.

    Returns:
        str: CSS string.
    """
    return "; ".join([f"{k}: {v}" for k, v in css.items()])

def px(l : str):
    if "px" in l:
        return float(l.replace("px", ""))
    elif "pt" in l:
        return float(l.replace("pt", "")) * 1.333
    else:
        return 0.0

def bullet_pos(css : dict, css_bullet : dict = None):
    """calculate center of bullet for anchor position
    (HACK, might break with a Folium update)"""
    if css_bullet is None:
        css_bullet = {}
    bullet_margin_x = css_bullet.get("margin-left", "0pt")
    parent_margin_x = css.get("margin-left", "0pt")
    bullet_width = css_bullet.get("width", "5pt")
    bullet_height = css_bullet.get("height", "5pt")
    anchor_shift_x = px(bullet_margin_x) + px(parent_margin_x) + px(bullet_width) / 2
    anchor_shift_y = px(bullet_height) /2
    return (anchor_shift_x, anchor_shift_y)


def get_lev(gid_code):
    """Calculates administrative level from GID code.
    E.g. `get_lev("IND.12.1") = 2`.

    Args:
        gid_code (str): GADM Unique ID

    Returns:
        int: usually 0, 1, 2 or 3
    """
    return gid_code.count(".")


def GID_max(feature):
    """
    When a GeoJSON feature as a dict, its unique ID is given by the key GID_n for the highest n
    for which it is defined and not None.
    ```
    Args:
        feature (dict|pd.Series): Either a dictionary with a key "properties", or a flat dict, or
            a GeoDataFrame row with the same structure.

    Returns:
        str: The highest GID_n value found in the feature
    """
    if isinstance(feature, pd.Series):
        d = flatdict_from_series(feature)
    elif isinstance(feature, dict):
        if "properties" in feature:
            d = feature["properties"]
        else:
            d = feature
    else:
        raise ValueError("feature for GID_max must be a dict or a dataframe row")

    d = {k: v for k, v in d.items() if v is not None and k.startswith("GID_")}
    ks = sorted(list(d.keys()))
    max_gid = d[ks[-1]] if ks else None
    return max_gid


def NAME_max(feature):
    """
    When a GeoJSON feature as a dict, its unique ID is given by the key GID_n for the highest n
    for which it is defined and not None.
    ```
    Args:
        feature (dict|pd.Series): Either a dictionary with a key "properties", or a flat dict, or
            a GeoDataFrame row with the same structure.

    Returns:
        str: The highest GID_n value found in the feature
    """
    if isinstance(feature, pd.Series):
        d = flatdict_from_series(feature)
    elif isinstance(feature, dict):
        if "properties" in feature:
            d = feature["properties"]
        else:
            d = feature
    else:
        raise ValueError("feature for GID_max must be a dict or a dataframe row")

    d = {k: v for k, v in d.items() if v is not None and k.startswith("NAME_")}
    ks = sorted(list(d.keys()))
    max_gid = d[ks[-1]] if ks else None
    return max_gid


def average_hex_color(hex_colors):
    # Initialize sums of each component
    r_total, g_total, b_total = 0, 0, 0
    
    for hex_color in hex_colors:
        # Convert hex to RGB
        r, g, b = int(hex_color[1:3], 16), int(hex_color[3:5], 16), int(hex_color[5:7], 16)
        # Add to totals
        r_total += r
        g_total += g
        b_total += b
    
    # Calculate averages
    num_colors = max(1, len(hex_colors))
    r_avg, g_avg, b_avg = r_total // num_colors, g_total // num_colors, b_total // num_colors
    
    # Convert averages back to hex (formatting to 2 digits with leading zeros)
    avg_hex_color = f"#{r_avg:02x}{g_avg:02x}{b_avg:02x}"
    
    return avg_hex_color


def is_river(feature):
    """Check if a given feature is a river. Kinda deprecated,
    I would rather just store feature lists and river lists
    separately.

    Args:
        feature (dict): GeoJSON dict.

    Returns:
        bool: True if it is a river, False otherwise.
    """
    return feature["properties"].get("river_name") is not None


def flatdict_from_feature(feature):
    """A function that takes a GeoJSON feature dict e.g.
    { "properties" : { "GID_0" ... }, "geometry" : [...] } and returns a flat dict
    e.g. { "GID_0": ... "GID_1" : ... "NAME_0" : ... "geometry" : [...] }

    Args:
        feature (dict): GeoJSON feature dict.

    Returns:
        dict: Flat dictionary.
    """
    # trick: simultaneously remove "properties" and add its contents to the dict
    feature = feature.copy()
    feature.update(feature.pop("properties"))
    return feature


def feature_from_flatdict(flatdict):
    """A function that takes a flat dict e.g.
    { "GID_0": ... "GID_1" : ... "NAME_0" : ... "geometry" : [...] } and returns a
    GeoJSON feature dict e.g. { "properties" : { "GID_0" ... }, "geometry" : [...] }.
    The reverse of `flatdict_from_feature`.

    Args:
        flatdict (dict): Flat dictionary.

    Returns:
        dict: GeoJSON feature dict.
    """
    # trick: popping the geometry removes it from the dict
    flatdict = flatdict.copy()
    return {"properties": flatdict, "geometry": flatdict.pop("geometry")}


def gdf_from_flatdicts(flatdicts):
    """A function that takes a list of flat dicts e.g.
    { "GID_0": ... "GID_1" : ... "NAME_0" : ... "geometry" : [...] } and returns a
    GeoPandas GeoDataFrame.

    Args:
        flatdicts (List[dict]): Flat dictionaries.

    Returns:
        GeoDataFrame: GeoPandas GeoDataFrame.
    """
    return gpd.GeoDataFrame.from_features(
        [feature_from_flatdict(flatdict) for flatdict in flatdicts]
    )


def gdf_from_features(features):
    """A function that takes a list of GeoJSON feature dicts e.g.
    { "properties" : { "GID_0" ... }, "geometry" : [...] } and returns a
    GeoPandas GeoDataFrame.

    Args:
        features (list[dict]): GeoJSON feature dicts.

    Returns:
        GeoDataFrame: GeoPandas GeoDataFrame.
    """

    return gpd.GeoDataFrame.from_features(features)


def series_from_flatdict(flatdict, convert_geometry=True):
    """A function that takes a flat dict e.g.
    { "GID_0": ... "GID_1" : ... "NAME_0" : ... "geometry" : [...] } and returns a
    Pandas Series.

    Args:
        flatdict (dict): Flat dictionary.

    Returns:
        Series: Pandas Series.
    """
    thing = pd.Series(flatdict)
    if convert_geometry and "geometry" in thing and isinstance(thing["geometry"], dict):
        thing["geometry"] = shape(thing["geometry"])
    return thing


def series_from_feature(feature):
    """A function that takes a GeoJSON feature dict e.g.
    { "properties" : { "GID_0" ... }, "geometry" : [...] } and returns a
    Pandas Series.

    Args:
        feature (dict): GeoJSON feature dict.

    Returns:
        Series: Pandas Series.
    """

    return series_from_flatdict(flatdict_from_feature(feature))


def flatdicts_from_gdf(gdf):
    """A function that takes a GeoPandas DataFrame and returns a list of flat dicts
    e.g. { "GID_0": ... "GID_1" : ... "NAME_0" : ... "geometry" : [...] }.

    Args:
        gdf (GeoPandas.DataFrame): GeoPandas DataFrame.

    Returns:
        List[dict]: Flat dictionaries.
    """
    # alternatively, to better preserve geometry:
    # json_str = series.to_json()
    # return json.loads(json_str)
    # shapely.geometry.mapping should also work but it doesn't idk

    return gdf.to_dict(orient="records")


def features_from_gdf(gdf, to_list=False):
    """A function that takes a GeoPandas DataFrame and returns a list of GeoJSON feature dicts
    e.g. { "properties" : { "GID_0" ... }, "geometry" : [...] }.

    Args:
        gdf (GeoPandas.DataFrame): GeoPandas DataFrame.

    Returns:
        List[dict]: GeoJSON feature dictionaries.
    """
    feats = gdf.iterfeatures()
    if to_list:
        return list(feats)
    return feats
    # return [feature_from_flatdict(flatdict) for flatdict in flatdicts_from_gdf(gdf)]


def flatdict_from_series(series):
    """A function that takes a Pandas Series and returns a flat dict
    e.g. { "GID_0": ... "GID_1" : ... "NAME_0" : ... "geometry" : [...] }.

    Args:
        series (Pandas.Series): Pandas Series.

    Returns:
        dict: Flat dictionary.
    """
    return series.to_dict()
    # return flatdicts_from_gdf(gpd.GeoDataFrame([series]))[0] # slow


def feature_from_series(series):
    """A function that takes a Pandas Series and returns a GeoJSON feature dict
    e.g. { "properties" : { "GID_0" ... }, "geometry" : [...] }.

    Args:
        series (Pandas.Series): Pandas Series.

    Returns:
        dict: GeoJSON feature dictionary.
    """
    return feature_from_flatdict(flatdict_from_series(series))


def flatdict_from(data):
    """flatdict_from takes a GeoJSON feature or dataframe row and returns a flat dict.

    Args:
        data (dict|pd.Series): Either a dictionary with a key "properties", or a flat dict, or
            a GeoDataFrame row with the same structure.
    """
    if isinstance(data, pd.Series):
        return flatdict_from_series(data)
    elif isinstance(data, dict):
        if "properties" in data:
            return flatdict_from_feature(data)
        else:
            return data
    else:
        raise ValueError("data for flatdict_from must be a dict or a dataframe row")


def feature_from(data):
    """feature_from takes a flat dict or dataframe row and returns a GeoJSON feature.

    Args:
        data (dict|pd.Series): Either a dictionary with a key "properties", or a flat dict, or
            a GeoDataFrame row with the same structure.
    """
    if isinstance(data, pd.Series):
        return feature_from_series(data)
    elif isinstance(data, dict):
        if "properties" in data:
            return data
        else:
            return feature_from_flatdict(data)
    else:
        raise ValueError("data for feature_from must be a dict or a dataframe row")


def series_from(data):
    """series_from takes a flat dict or GeoJSON feature and returns a series.

    Args:
        data (dict|pd.Series): Either a dictionary with a key "properties", or a flat dict, or
            a GeoDataFrame row with the same structure.
    """
    if isinstance(data, pd.Series):
        return data
    elif isinstance(data, dict):
        if "properties" in data:
            return series_from_feature(data)
        else:
            return series_from_flatdict(data)
    else:
        raise ValueError("data for series_from must be a dict or a dataframe row")


def flatdicts_from(data):
    """flatdicts_from takes a GeoDataFrame or a list of GeoJSON features or a FeatureCollection
    and returns a list of flat dicts.

    Args:
        data (GeoDataFrame|List[dict]|dict): Either a GeoDataFrame, or a list of features or flatdicts,
        or a FeatureCollection.
    """
    if isinstance(data, gpd.GeoDataFrame):
        return flatdicts_from_gdf(data)
    elif isinstance(data, dict) and "features" in data:
        return [flatdict_from(f) for f in data["features"]]
    elif isinstance(data, list):
        if "properties" in data[0]:
            return [flatdict_from(f) for f in data]
        else:
            return data
    else:
        raise ValueError(
            "data for flatdicts_from must be a GeoDataFrame "
            "or a list of flat dicts or GeoJSON features"
        )


def features_from(data, to_list=False):
    """features_from takes a GeoDataFrame or a list of flatdicts or a FeatureCollection
    and returns a list of GeoJSON features.

    Args:
        data (GeoDataFrame|List[dict]|dict): Either a GeoDataFrame, or a list of features or flatdicts,
        or a FeatureCollection.
    """
    if isinstance(data, gpd.GeoDataFrame):
        return features_from_gdf(data, to_list=to_list)
    elif isinstance(data, dict) and "features" in data:
        return data["features"]
    elif isinstance(data, list):
        if "properties" in data[0]:
            return data
        else:
            return [feature_from(f) for f in data]
    else:
        raise ValueError(
            "data for features_from must be a GeoDataFrame "
            "or a list of flat dicts or GeoJSON features"
        )


def featurecollection_from(data):
    """featurecollection_from takes a GeoDataFrame or a list of flatdicts or a list of GeoJSON features
    and returns a FeatureCollection.

    Args:
        data (GeoDataFrame|List[dict]|List[dict]): Either a GeoDataFrame, or a list of features or flatdicts.
    """
    features = features_from(data)
    return {
        "type": "FeatureCollection",
        "crs": {
            "type": "name",
            "properties": {
            "name": "urn:ogc:def:crs:OGC:1.3:CRS84"
            }
        },
        "features": features}


def gdf_from(data):
    """gdf_from takes a list of flatdicts or a list of GeoJSON features or a FeatureCollection
    and returns a GeoDataFrame.

    Args:
        data (List[dict]|List[dict]|dict): Either a list of flatdicts or a list of features or
            a FeatureCollection.
    """
    if isinstance(data, gpd.GeoDataFrame):
        return data
    elif isinstance(data, dict) and "features" in data:
        return gdf_from_features(data["features"])
    elif isinstance(data, list):
        if "properties" in data[0]:
            return gdf_from_features(data)
        else:
            return gdf_from_features([feature_from(f) for f in data])
    else:
        raise ValueError(
            "data for gdf_from must be a GeoDataFrame "
            "or a list of flat dicts or GeoJSON features"
        )


# test feature
# flatdict1 = {
#     "GID_0": "IND",
#     "GID_1": "IND.12",
#     "NAME_0": "India",
#     "geometry": {"type": "LineString", "coordinates": [[1, 2], [3, 4]]},
# }
# dit = lambda x: x["GID_0"] == "IND"
# gdf1=gdf_from_flatdicts([flatdict1.copy(), flatdict1])
# print(gdf1.apply(dit, axis=1))
