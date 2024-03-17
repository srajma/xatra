from xatra.data import Loka, Varuna, DataItem
from xatra.matchers import *
import geopandas as gpd


def test_download():
    breaks = DataItem(type="break", id="IND.20.20_1", level=3) + DataItem(
        type="break", id="CHN.28_1", level=3
    )
    lok = DataItem(type="feature", id="IND", level=2) + DataItem(
        type="feature", id="PAK", level=2
    )
    varr = DataItem(
        type="river", id="1236345", river_type="relation", common_name="ganga"
    )
    breaks.download("tests/data/", overwrite=True)
    lok.download("tests/data/", overwrite=True)
    varr.download("tests/data/", overwrite=True)


def test_load_loka():
    gdf = Loka.INDIAN_SUBCONTINENT.load(format="gpd", tolerance=0.01, verbose=True)
    featurecollection = Loka.INDIAN_SUBCONTINENT.load(
        format="featurecollection", tolerance=0.01, verbose=True
    )
    features = Loka.INDIAN_SUBCONTINENT.load(format="features", verbose=True)
    assert (
        isinstance(gdf, gpd.GeoDataFrame)
        and len(gdf) > 10
        and "geometry" in gdf.columns
        and "GID_0" in gdf.columns
        and "GID_max" in gdf.columns
        and "NAME_max" in gdf.columns
        and isinstance(featurecollection, dict)
        and "features" in featurecollection
        and len(featurecollection["features"]) > 10
        and "geometry" in featurecollection["features"][0]
        and "properties" in featurecollection["features"][0]
        and "GID_max" in featurecollection["features"][0]["properties"]
        and "NAME_max" in featurecollection["features"][0]["properties"]
        and isinstance(features, list)
        and len(features) > 10
        and "geometry" in features[0]
        and "properties" in features[0]
        and "GID_max" in features[0]["properties"]
        and "NAME_max" in features[0]["properties"]
    )
    print(gdf.iloc[0])


def test_load_loka():
    gdf = Loka.INDIAN_SUBCONTINENT.load(format="gpd", tolerance=0.01, verbose=True)
    featurecollection = Loka.INDIAN_SUBCONTINENT.load(
        format="featurecollection", tolerance=0.01, verbose=True
    )
    features = Loka.INDIAN_SUBCONTINENT.load(format="features", verbose=True)
    assert (
        isinstance(gdf, gpd.GeoDataFrame)
        and len(gdf) > 10
        and "geometry" in gdf.columns
        and "GID_0" in gdf.columns
        and "GID_max" in gdf.columns
        and "NAME_max" in gdf.columns
        and isinstance(featurecollection, dict)
        and "features" in featurecollection
        and len(featurecollection["features"]) > 10
        and "geometry" in featurecollection["features"][0]
        and "properties" in featurecollection["features"][0]
        and "GID_max" in featurecollection["features"][0]["properties"]
        and "NAME_max" in featurecollection["features"][0]["properties"]
        and isinstance(features, list)
        and len(features) > 10
        and "geometry" in features[0]
        and "properties" in features[0]
        and "GID_max" in features[0]["properties"]
        and "NAME_max" in features[0]["properties"]
    )
    print(gdf.iloc[0])
    print(gdf.crs)


def test_load_varuna():
    gdf = Varuna.INDIAN_SUBCONTINENT.load(format="gpd", tolerance=0.01, verbose=True)
    featurecollection = Varuna.INDIAN_SUBCONTINENT.load(
        format="featurecollection", tolerance=0.01, verbose=True
    )
    features = Varuna.INDIAN_SUBCONTINENT.load(format="features", verbose=True)
    assert (
        isinstance(gdf, gpd.GeoDataFrame)
        and len(gdf) > 10
        and "geometry" in gdf.columns
        # and "GID_0" in gdf.columns
        # and "GID_max" in gdf.columns
        # and "NAME_max" in gdf.columns
        and isinstance(featurecollection, dict)
        and "features" in featurecollection
        and len(featurecollection["features"]) > 10
        and "geometry" in featurecollection["features"][0]
        and "properties" in featurecollection["features"][0]
        # and "GID_max" in featurecollection["features"][0]["properties"]
        # and "NAME_max" in featurecollection["features"][0]["properties"]
        and isinstance(features, list)
        and len(features) > 10
        and "geometry" in features[0]
        and "properties" in features[0]
        # and "GID_max" in features[0]["properties"]
        # and "NAME_max" in features[0]["properties"]
    )
    print(gdf.iloc[0])
    print(gdf.crs)


def test_loka_filter():
    #gdf = Loka.INDIC.load(format="gpd", tolerance=0.01, verbose=True)
    test_feature = {
        "type": "Feature",
        "properties": {
            "GID_3": "PAK.2.1.1_1",
            "GID_0": "PAK",
            "COUNTRY": "Pakistan",
            "GID_1": "PAK.2_1",
            "NAME_1": "Balochistan",
            "NL_NAME_1": "NA",
            "GID_2": "PAK.2.1_1",
            "NAME_2": "Kalat",
            "NL_NAME_2": "NA",
            "NAME_3": "Awaran",
            "VARNAME_3": "NA",
            "NL_NAME_3": "NA",
            "TYPE_3": "District",
            "ENGTYPE_3": "District",
            "CC_3": "NA",
            "HASC_3": "NA",
        },
        "geometry": {
            "type": "Polygon",
            "coordinates": [
                [
                    [65.08499908447266, 27.84916687011719],
                    [65.08499908447266, 27.84916687011719],
                ]
            ],
        },
    }
    boo = SUBCONTINENT_PROPER(test_feature)
    print(boo)
    assert not boo

def test_loka_repr():
    x=DataItem(type="feature", id="IND", level=2)
    y=DataItem(type="feature", id="IND", level=2)
    print(x == y)
    print(x)
    print(Loka.INDOSPHERE.items)

test_loka_repr()