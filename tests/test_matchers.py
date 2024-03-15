from xatra.matchers import *
import numpy as np

def test_matchers():
    feature = {
        "type": "Feature",
        "properties": {
            "GID_3": "PAK.7.7.1_1",
            "GID_0": "PAK",
            "COUNTRY": "Pakistan",
            "GID_1": "PAK.7_1",
            "NAME_1": "Punjab",
            "NL_NAME_1": "NA",
            "GID_2": "PAK.7.7_1",
            "NAME_2": "Rawalpindi",  # TODO: annex this region
            "NL_NAME_2": "NA",
            "NAME_3": "Attok",
            "VARNAME_3": "Attock",
            "NL_NAME_3": "NA",
            "TYPE_3": "District",
            "ENGTYPE_3": "District",
            "CC_3": "NA",
            "HASC_3": "NA",
        },
        "geometry": "",
    }
    features = [feature.copy(), feature]
    flatdict = flatdict_from_feature(feature)
    featurecollection = featurecollection_from(features)
    gdf = gdf_from_features([feature.copy(), feature])
    series = series_from_flatdict(flatdict)
    
    mat = Matcher.taluks("PAK.7.7.1", "PAK.7.5.3_1")
    print(mat(series))
    
test_matchers()