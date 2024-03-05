"""
HELPER FUNCTIONS
"""

def get_lev(gid_code):
    """Calculates administrative level from GID code.
    E.g. `get_lev("IND.12.1") = 2`.

    Args:
        gid_code (str): GADM Unique ID

    Returns:
        int: usually 0, 1, 2 or 3
    """
    return gid_code.count('.')

def GID_max(feature):
    """ 
    When a GeoJSON feature as a dict, its unique ID is given by the key GID_n for the highest n
    for which it is defined and not None. E.g. 
    
    ```python
    eg_feature = {
        "properties" : {
            "GID_0" : "IND",
            "GID_1" : "IND.2",
            "GID_2" : "IND.2.1",
            "GID_3" : None
        }
    }
    GID_max(eg_feature) # {"n" : 2, "GID_n" : "IND.2.1"}
    ```    
    Args:
        feature (dict): Dictionary with a key "properties" whose val is another dict

    Returns:
        dict: Dictionary with keys "n" : int, "GID_n" : str 
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
    When a GeoJSON feature as a dict, its name is given by the key NAME_n for the highest n
    for which it is defined and not None. E.g. 
    
    ```python
    eg_feature = {
        "properties" : {
            "NAME_0" : "India",
            "NAME_1" : "Maharashtra",
            "NAME_2" : "Pune",
            "NAME_3" : None
        }
    }
    NAME_max(eg_feature) # {"n" : 2, "GID_n" : "Pune"}
    ```    
    Args:
        feature (dict): Dictionary with a key "properties" whose val is another dict

    Returns:
        dict: Dictionary with keys "n" : int, "NAME_n" : str 
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

def is_river(feature):
    """Check if a given feature is a river. Kinda deprecated,
    I would rather just store feature lists and river lists
    separately.

    Args:
        feature (dict): GeoJSON dict.

    Returns:
        bool: True if it is a river, False otherwise.
    """
    return feature['properties'].get('river_name') is not None
