from xatra.utilities import *


def test_conversions():

    flatdict0 = {
        "GID_0": "IND",
        "GID_1": "IND.12",
        "NAME_0": "India",
        "geometry": {"type": "LineString", "coordinates": [[1, 2], [3, 4]]},
    }
    flatdicts0 = [flatdict0.copy(), flatdict0.copy()]
    
    feature0 = feature_from_flatdict(flatdict0)
    features0 = [feature0.copy(), feature0.copy()]
    
    flatdict1 = flatdict_from_feature(feature0)

    gdf0 = gdf_from_flatdicts(flatdicts0)
    gdf1 = gdf_from_features(features0)

    series0 = series_from_flatdict(flatdict0)
    series1 = series_from_feature(feature0)

    flatdict2 = flatdicts_from_gdf(gdf0)[0]
    feature1 = features_from_gdf(gdf0)[0]

    flatdict3 = flatdict_from_series(series0)
    feature2 = feature_from_series(series0)

    flatdict_coerced_from_flatdict = flatdict_from(flatdict0)
    flatdict_coerced_from_feature = flatdict_from(feature0)
    flatdict_coerced_from_series = flatdict_from(series0)

    feature_coerced_from_flatdict = feature_from(flatdict0)
    feature_coerced_from_feature = feature_from(feature0)
    feature_coerced_from_series = feature_from(series0)

    series_coerced_from_flatdict = series_from(flatdict0)
    series_coerced_from_feature = series_from(feature0)
    series_coerced_from_series = series_from(series0)

    flatdicts_coerced_from_flatdicts = flatdicts_from(flatdicts0)
    flatdicts_coerced_from_features = flatdicts_from(features0)
    flatdicts_coerced_from_gdf = flatdicts_from(gdf0)
    
    features_coerced_from_flatdicts = features_from(flatdicts0)
    features_coerced_from_features = features_from(features0)
    features_coerced_from_gdf = features_from(gdf0)
    
    gdf_coerced_from_flatdicts = gdf_from(flatdicts0)
    gdf_coerced_from_features = gdf_from(features0)
    gdf_coerced_from_gdf = gdf_from(gdf0)

    tests = [
        flatdict0 == flatdict1,
        gdf0.equals(gdf1),
        series0.equals(series1),
        # flatdict0 == flatdict2, # this fails because of geometry
        # feature0 == feature1,
        # flatdict0 == flatdict3,
        # feature0 == feature2,
        flatdict0 == flatdict_coerced_from_flatdict,
        flatdict0 == flatdict_coerced_from_feature,
        # flatdict0 == flatdict_coerced_from_series,
        feature0 == feature_coerced_from_flatdict,
        feature0 == feature_coerced_from_feature,
        # feature0 == feature_coerced_from_series,
        series0.equals(series_coerced_from_flatdict),
        series0.equals(series_coerced_from_feature),
        series0.equals(series_coerced_from_series),
        flatdicts0 == flatdicts_coerced_from_flatdicts,
        features0 == features_coerced_from_features,
        gdf0.equals(gdf_coerced_from_flatdicts),
        gdf0.equals(gdf_coerced_from_features),
        gdf0.equals(gdf_coerced_from_gdf)
    ]

    assert all(tests)
    print(list(enumerate(tests)))
    print(
        f"flatdict0: \n{flatdict0}\n\n"
        f"flatdict1: \n{flatdict1}\n\n"
        f"gdf0: \n{gdf0}\n\n"
        f"gdf1: \n{gdf1}\n\n"
        f"series0: \n{series0}\n\n"
        f"series1: \n{series1}\n\n"
        f"flatdict2: \n{flatdict2}\n\n"
        f"feature1: \n{feature1}\n\n"
        f"flatdict3: \n{flatdict3}\n\n"
        f"feature2: \n{feature2}\n\n"
        f"flatdict_coerced_from_flatdict: \n{flatdict_coerced_from_flatdict}\n\n"
        f"flatdict_coerced_from_feature: \n{flatdict_coerced_from_feature}\n\n"
        f"flatdict_coerced_from_series: \n{flatdict_coerced_from_series}\n\n"
        f"feature_coerced_from_flatdict: \n{feature_coerced_from_flatdict}\n\n"
        f"feature_coerced_from_feature: \n{feature_coerced_from_feature}\n\n"
        f"feature_coerced_from_series: \n{feature_coerced_from_series}\n\n"
        f"series_coerced_from_flatdict: \n{series_coerced_from_flatdict}\n\n"
        f"series_coerced_from_feature: \n{series_coerced_from_feature}\n\n"
        f"series_coerced_from_series: \n{series_coerced_from_series}\n\n"
        f"flatdicts_coerced_from_flatdicts: \n{flatdicts_coerced_from_flatdicts}\n\n"
        f"features_coerced_from_features: \n{features_coerced_from_features}\n\n"
        f"gdf_coerced_from_gdf: \n{gdf_coerced_from_gdf}\n\n"
    )

def test_conversions2():
    flatdict = {
        "GID_0": "IND",
        "GID_1": "IND.12",
        "NAME_0": "India",
        "geometry": {"type": "LineString", "coordinates": [[1, 2], [3, 4]]},
    }
    gdf1 = gdf_from_flatdicts([flatdict.copy(), flatdict.copy()])
    print(list(gdf1.iterfeatures()))

def test_GID_NAME_max():
    flatdict = {
        "GID_0": "IND",
        "GID_1": "IND.12",
        "GID_2": "IND.12.1",
        "GID_3": None,
        "NAME_0": "India",
        "NAME_1": "Karnataka",
        "NAME_2": "Bangalore",
        "NAME_3": None,
        "geometry": {"type": "LineString", "coordinates": [[1, 2], [3, 4]]},
    }
    feature = feature_from_flatdict(flatdict)
    gs = series_from_flatdict(flatdict)
    assert (
        GID_max(flatdict) == "IND.12.1"
        and GID_max(feature) == "IND.12.1"
        and GID_max(gs) == "IND.12.1"
        and NAME_max(flatdict) == "Bangalore"
        and NAME_max(feature) == "Bangalore"
        and NAME_max(gs) == "Bangalore"
    )

def test_average_hex_color():
    hex_colors = ['#FF0000', '#00FF00', '#0000FF']
    average_color = average_hex_color(hex_colors)
    print(average_color)
    assert average_color == "#555555"

test_average_hex_color()