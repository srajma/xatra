"""
Library of Matchers for flags
"""

import geopandas as gpd
import pandas as pd
from xatra.utilities import *


class Matcher:
    """A Matcher defines a filter on GeoJSON features, either as a dict or as a
    GeoPandas DataFrame. A Matcher object may be constructed by specifying either
    method (or both).

    Methods:
        match_feature (Callable[[Dict], bool]): A function that takes a GeoJSON feature
            dict (i.e. {"properties" : { "GID_0" ... }, "geometry" : [...] }) and returns
            a boolean.
        match_flat_dict (Callable[[Dict], bool]): A function that takes a FLAT dict
            (i.e. { "GID_0": ... "GID_1" : ... "NAME_0" : ... "geometry" : [...] })
            and returns a boolean.
        match_gdf (Callable[[gpd.GeoDataFrame], pd.Series]): A function that takes
            a GeoDataFrame and returns a GeoSeries of bools indicating whether each row
            matches.

    """

    def __init__(
        self,
        match_feature=None,
        match_flat_dict=None,
        match_series=None,
        match_gdf=None,
    ):
        """Initialize a Matcher."""
        self.match_feature = match_feature
        self.match_flat_dict = match_flat_dict
        self.match_series = match_series
        self.match_gdf = match_gdf
    
    def filter(self, data):
        """Filter data to include only those features which match this matcher.
        
        Args:
            data (Dict | List[Dict] | gpd.GeoDataFrame): The data to filter.
        """
        if isinstance(data, gpd.GeoDataFrame):
            return data[self(data)]
        elif isinstance(data, list):
            return [feature for feature in data if self.match_feature(feature)]
        elif isinstance(data, dict):
            features = data["features"]
            features = [feature for feature in features if self.match_feature(feature)]
            return {"type": "FeatureCollection", "features": features}
            
    
    @classmethod
    def from_match_feature(cls, match_feature):
        """Calculate others from feature and construct."""
        obj = cls(match_feature=match_feature)
        obj.match_flat_dict = lambda d: match_feature(feature_from_flatdict(d))
        obj.match_series = lambda s: match_feature(feature_from_series(s))
        obj.match_gdf = lambda gdf: gdf.apply(obj.match_flat_dict, axis=1)
        return obj

    @classmethod
    def from_match_flat_dict(cls, match_flat_dict):
        """Calculate others from match_flat_dict and construct."""
        obj = cls(match_flat_dict=match_flat_dict)
        obj.match_feature = lambda d: match_flat_dict(flatdict_from_feature(d))
        obj.match_series = lambda s: match_flat_dict(flatdict_from_series(s))
        obj.match_gdf = lambda gdf: gdf.apply(match_flat_dict, axis=1)
        return obj

    @classmethod
    def from_match_gdf(cls, match_gdf):
        """Calculate others from match_gdf and construct."""
        obj = cls(match_gdf=match_gdf)
        obj.match_flat_dict = lambda d: match_gdf(gdf_from_flatdicts([d]))
        obj.match_feature = lambda d: match_gdf(gdf_from_features([d]))
        obj.match_series = lambda s: match_gdf(gpd.GeoDataFrame([s])).iloc[0]
        return obj

    @classmethod
    def match_properties(cls, op=any, **kwargs):
        """Construct a matcher that checks if any or all fields satisfies the
        corresponding function in kwargs.

        Args:
            **kwargs: A dictionary of functions Callable[[str], bool]
                or str for each field. If string, will be replaced by
                function that checks equality to the string.
        """
        for field, match in kwargs.items():
            if isinstance(match, str):
                # "match=match" -- because of late binding
                kwargs[field] = lambda x, match=match: x == match
            elif not callable(match):
                raise ValueError("All values must be callable")

        match_flat_dict = lambda d: op(
            [field in d and pd.notna(d[field]) and match(d[field]) for field, match in kwargs.items()]
        )
        obj = cls.from_match_flat_dict(match_flat_dict)
        return obj

    @classmethod
    def match_level(cls, level, value):
        """Construct a matcher that checks, for level i, if:
        * the NAME_i field is equal to value
        * the VARNAME_i field contains value
        * the GID_i field is equal to value or starts with value + "_"
        * i == 0 and the COUNTRY field is equal to value

        Args:
            level (int): The level of the NAME field to check.
            value (str): The string to check for.
        """
        return cls.match_properties(
            op=any,
            **{
                f"NAME_{level}": value,
                f"VARNAME_{level}": lambda x: value in x.split("|"),
                f"GID_{level}": lambda x: x == value or x.startswith(value + "_"),
                "COUNTRY": value if level == 0 else lambda x: False,
            },
        )

    @classmethod
    def name_starts_with(cls, level, name):
        """Construct a matcher that checks if the NAME_i field starts with name.

        Args:
            level (int): The level of the NAME field to check.
            name (str): The string to check for.
        """
        return cls.match_properties(**{f"NAME_{level}": lambda x: x.startswith(name)})

    @classmethod
    def gid(cls, value):
        """Construct a matcher that checks if the GID_i field of the level of
        value is equal to value.

        Args:
            value (str): The GID to check for.
        """
        lev = get_lev(value)
        return cls.match_properties(**{f"GID_{lev}": value})
    
    @classmethod
    def country(cls, value):
        """Construct a matcher that checks if:
        * the COUNTRY field is equal to value.
        * the NAME_0 field is equal to value.
        * the GID_0 field is equal to value or starts with value + "_".

        Args:
            value (str): The country to check for.
        """
        return cls.match_level(0, value)

    @classmethod
    def province(cls, value):
        """Construct a matcher that checks if:
        * the NAME_1 field is equal to value.
        * the VARNAME_1 field contains value.
        * the GID_1 field is equal to value or starts with value + "_".

        Args:
            value (str): The province to check for.
        """
        return cls.match_level(1, value)

    @classmethod
    def district(cls, value):
        """Construct a matcher that checks if:
        * the NAME_2 field is equal to value.
        * the VARNAME_2 field contains value.
        * the GID_2 field is equal to value or starts with value + "_".

        Args:
            value (str): The district to check for.
        """
        return cls.match_level(2, value)

    @classmethod
    def taluk(cls, value):
        """Construct a matcher that checks if:
        * the NAME_3 field is equal to value.
        * the VARNAME_3 field contains value.
        * the GID_3 field is equal to value or starts with value + "_".

        Args:
            value (str): The taluk to check for.
        """
        return cls.match_level(3, value)

    @classmethod
    def match_level_multiple(cls, level, *values):
        """__or__ over match_level for multiple values.

        Args:
            level (int): The level of the NAME field to check.
            *values (str): The strings to check for.
        """
        obj = cls.__false__()
        for value in values:
            obj |= cls.match_level(level, value)
        return obj

    @classmethod
    def countries(cls, *values):
        """__or__ over country for multiple values.

        Args:
            *values (str): The countries to check for.
        """
        return cls.match_level_multiple(0, *values)

    @classmethod
    def provinces(cls, *values):
        """__or__ over province for multiple values.

        Args:
            *values (str): The provinces to check for.
        """
        return cls.match_level_multiple(1, *values)

    @classmethod
    def districts(cls, *values):
        """__or__ over district for multiple values.

        Args:
            *values (str): The districts to check for.
        """
        return cls.match_level_multiple(2, *values)

    @classmethod
    def taluks(cls, *values):
        """__or__ over taluk for multiple values.

        Args:
            *values (str): The taluks to check for.
        """
        return cls.match_level_multiple(3, *values)

    def __call__(self, feature):
        if isinstance(feature, dict):
            if "properties" in feature:
                return self.match_feature(feature)
            else:
                return self.match_flat_dict(feature)
        elif isinstance(feature, pd.Series):
            return self.match_series(feature)
        elif isinstance(feature, gpd.GeoDataFrame):
            return self.match_gdf(feature)
        else:
            raise ValueError("Feature must be a flat dict, feature or a GeoDataFrame")

    @classmethod
    def __true__(cls):
        return cls(
            match_feature=lambda feature: True,
            match_flat_dict=lambda flatdict: True,
            match_series=lambda series: True,
            match_gdf=lambda gdf: pd.Series(True, index=gdf.index),
        )

    @classmethod
    def __false__(cls):
        return cls(
            match_feature=lambda feature: False,
            match_flat_dict=lambda flatdict: False,
            match_series=lambda series: False,
            match_gdf=lambda gdf: pd.Series(False, index=gdf.index),
        )

    def __or__(self, other):
        if not isinstance(other, Matcher):
            return NotImplemented
        return Matcher(
            match_feature=lambda feature: self(feature) or other(feature),
            match_flat_dict=lambda flatdict: self(flatdict) or other(flatdict),
            match_series=lambda series: self(series) or other(series),
            match_gdf=lambda gdf: self(gdf) | other(gdf),
        )

    def __and__(self, other):
        if not isinstance(other, Matcher):
            return NotImplemented
        return Matcher(
            match_feature=lambda feature: self(feature) and other(feature),
            match_flat_dict=lambda flatdict: self(flatdict) and other(flatdict),
            match_series=lambda series: self(series) and other(series),
            match_gdf=lambda gdf: self(gdf) & other(gdf),
        )

    def __invert__(self):
        return Matcher(
            match_feature=lambda feature: not self(feature),
            match_flat_dict=lambda flatdict: not self(flatdict),
            match_series=lambda series: not self(series),
            match_gdf=lambda gdf: ~self(gdf),
        )

    def __sub__(self, other):
        """NOTE: Takes precedence over __and__ and __or__, so remember to use
        brackets when combining with other operators."""
        if not isinstance(other, Matcher):
            return NotImplemented
        return Matcher(
            match_feature=lambda feature: self(feature) and not other(feature),
            match_flat_dict=lambda flatdict: self(flatdict) and not other(flatdict),
            match_series=lambda series: self(series) & ~other(series),
            match_gdf=lambda gdf: self(gdf) & ~other(gdf),
        )
    
    def __any__(selves):
        obj = Matcher.__false__()
        for self in selves:
            obj |= self
        return obj
    
    def __all__(selves):
        obj = Matcher.__true__()
        for self in selves:
            obj &= self
        return obj


# get these out for easy access
country = Matcher.country
province = Matcher.province
district = Matcher.district
taluk = Matcher.taluk
name_starts_with = Matcher.name_starts_with
countries = Matcher.countries
provinces = Matcher.provinces
districts = Matcher.districts
taluks = Matcher.taluks


"""custom, recurring, world regions"""

# sorting the himalayas
CHINESE_CLAIMS_UK = country("Z05") | province("Z09.35")
CHINESE_CLAIMS_HP = province("Z09.13") | country("Z04")
CHINESE_CLAIMS_LADAKH = country("Z03") | country("Z08")  # Aksai Chin
CHINESE_CLAIMS_GILGIT = country("Z02")
CHINESE_CLAIMS_AP = country("Z07")
CHINESE_CLAIMS = (
    CHINESE_CLAIMS_UK
    | CHINESE_CLAIMS_HP
    | CHINESE_CLAIMS_AP
    | CHINESE_CLAIMS_LADAKH
    | CHINESE_CLAIMS_GILGIT
)
TERAI_HP = (
    district("IND.13.4")
    | district("IND.13.3")
    | district("IND.13.12")
    | district("IND.13.1")
    | district("IND.13.11")
    | district("IND.13.10")
)
TERAI_UK = (
    district("IND.35.5")
    | district("IND.35.12")
    | district("IND.35.7")
    | district("IND.35.8")
)
TERAI_NPL_FW = taluk("NPL.3.1.4") | taluk("NPL.3.2.5")
TERAI_NPL_MW = taluk("NPL.4.1.1") | taluk("NPL.4.1.2")
TERAI_NPL_W = taluk("NPL.5.3.3") | taluk("NPL.5.3.6") | taluk("NPL.5.3.4")  # sakya
TERAI_NPL_C = (
    taluk("NPL.1.3.4")
    | taluk("NPL.1.3.1")
    | taluk("NPL.1.3.5")
    | taluk("NPL.1.2.5")
    | taluk("NPL.1.2.3")
    | taluk("NPL.1.2.1")
)
TERAI_NPL_E = (
    taluk("NPL.2.3.4")
    | taluk("NPL.2.3.3")
    | taluk("NPL.2.1.3")
    | taluk("NPL.2.1.5")
    | taluk("NPL.2.2.2")
)
TERAI_NPL = TERAI_NPL_FW | TERAI_NPL_MW | TERAI_NPL_W | TERAI_NPL_C | TERAI_NPL_E
TERAI = TERAI_HP | TERAI_UK | TERAI_NPL
HP_HIM = (province("HimachalPradesh") | CHINESE_CLAIMS_HP) - TERAI_HP
UK_HIM = (province("Uttarakhand") | CHINESE_CLAIMS_UK) - TERAI_UK
NPL_HIM = country("Nepal") - TERAI_NPL
LADAKH = (
    district("Leh(Ladakh)") | district("Kargil") | country("Z03") | country("Z08")
)  # Aksai Chin main part | Aksai Chin Southern bit
KASHMIR_MISC = (
    district("Z01.14.10")
    | district("Z01.14.5")
    | district("Z01.14.17")
    | district("Z01.14.18")
    | district("Z01.14.22")
    | district("Jammu")
    | district("Z01.14.19")
    | district("Z01.14.9")
)
KASHMIR_PROPER = province("JammuandKashmir") - (KASHMIR_MISC | LADAKH)
KASHMIR_TBC = province("Z06.1")  # POK
KASHMIR = KASHMIR_PROPER | KASHMIR_MISC | KASHMIR_TBC
DARADA = province("Gilgit-Baltistan")
KHYBER_HIM = district("Malakand") | district("Hazara")
BENGAL_HIM = (
    district("Darjiling")
    | district("Jalpaiguri")
    | district("Alipurduar")
    | district("KochBihar")
)
ASSAM_HIM = (
    district("IND.4.4")
    | district("IND.4.10")
    | district("IND.4.13")
    | district("IND.4.18")
    | district("IND.4.17")
    | district("IND.4.22")
)
LAUHITYA = province("Assam") - ASSAM_HIM
NEI_HIM = (
    province("ArunachalPradesh")
    | province("Meghalaya")
    | province("Nagaland")
    | province("Manipur")
    | province("Mizoram")
    | province("Tripura")
    | ASSAM_HIM
)
INNER_KAMBOJA = province("PAK.3")  # Federally Administered Tribal Areas
HIMALAYAN = (
    HP_HIM
    | UK_HIM
    | NPL_HIM
    | country("Bhutan")
    | BENGAL_HIM
    | NEI_HIM
    | province("Sikkim")
    | LADAKH
    | DARADA
    | KHYBER_HIM
    | CHINESE_CLAIMS
)

# tibeto-burman region

TIBET_CN_TIB = province("CHN.29")  # chinese occupied tibet
TIBET_CN_QIN = province("CHN.21")  # chinese occupied tibet
TIBET_CN_SIC = district("CHN.26.5") | district("CHN.26.16")  # chinese occupied tibet
TIBET_CN = TIBET_CN_TIB | TIBET_CN_QIN | TIBET_CN_SIC
TIBET_BHU = country("Bhutan")  # bhutanese occupied tibet
TIBET_NEP = (
    taluk("NPL.4.2.1")
    | taluk("NPL.4.2.2")
    | taluk("NPL.4.2.5")
    | district("NPL.5.1")
    | district("NPL.5.2")
    | district("NPL.1.1")
    | taluk("NPL.1.2.2")
    | taluk("NPL.1.2.4")
    | taluk("NPL.1.2.6")
    | taluk("NPL.2.3.5")
    | taluk("NPL.2.3.1")
    | taluk("NPL.2.3.2")
    | taluk("NPL.2.1.1")
    | taluk("NPL.2.1.4")
    | taluk("NPL.2.1.2")
    | taluk("NPL.2.1.6")
    | taluk("NPL.2.2.4")
    | taluk("NPL.2.2.3")
    | taluk("NPL.2.2.1")
)  # nepali-occupied tibet
TIBET_AP = CHINESE_CLAIMS_AP  # chinese-occupied indian tibet :(
TIBET_LAD = LADAKH  # tibet in its rightful home
TIBET_SIK = province("Sikkim")  # tibet in its rightful home
TIBET = TIBET_CN | TIBET_BHU | TIBET_NEP | TIBET_LAD | TIBET_AP | TIBET_SIK

TIBET_BURMA_INTERM = (
    NEI_HIM | province("MMR.3")
) - TIBET  # intermediary region from Tibet to Burma
YUNNAN_BURMA_INTERM = province("MMR.4")  # kachin state
KAREN = province("MMR.5") | province("MMR.6")  # karenic parts of myanmar
SIAM_BURMA_INTERM = province("MMR.13")  # shan state

BURMA_UPPER = (
    province("MMR.12") | province("MMR.7") | province("MMR.8") | province("MMR.10")
)
BURMA_LOWER_RIVER = province("MMR.2") | province("MMR.1") | province("MMR.15")
BURMA_LOWER_RAKHINE = province("MMR.11")
BURMA_LOWER_THAICOAST = province("MMR.9") | province("MMR.14")
BURMA_LOWER = BURMA_LOWER_RIVER | BURMA_LOWER_RAKHINE | BURMA_LOWER_THAICOAST
BURMA = BURMA_UPPER | BURMA_LOWER

# southeast asia
SIAM_THA = country("Thailand")
SIAM = SIAM_THA
LAOS = country("Laos")
KHMER = country("Cambodia")
CHAM = (
    province("VNM.41")
    | province("VNM.29")
    | province("VNM.46")
    | province("VNM.50")
    | province("VNM.54")
    | province("VNM.19")
    | province("VNM.47")
    | province("VNM.48")
    | province("VNM.34")
    | province("VNM.8")
    | province("VNM.21")
    | province("VNM.45")
    | province("VNM.32")
    | province("VNM.15")
    | province("VNM.43")
    | province("VNM.37")
    | province("VNM.16")
    | province("VNM.11")
    | province("VNM.7")
    | province("VNM.17")
    | province("VNM.10")
    | province("VNM.25")
    | province("VNM.9")
    | province("VNM.53")
    | province("VNM.39")
    | province("VNM.58")
    | province("VNM.6")
    | province("VNM.59")
    | province("VNM.61")
    | province("VNM.18")
    | province("VNM.51")
    | province("VNM.24")
    | province("VNM.2")
    | province("VNM.33")
    | province("VNM.12")
    | province("VNM.1")
    | province("VNM.13")
    | province("VNM.33")
)
NORTH_VIETNAM = country("Vietnam") - CHAM
BORNEO_MYS = (
    province("MYS.13") | province("MYS.14") | province("MYS.5")
)  # sabah serawak
BORNEO_BRU = country("Brunei")
BORNEO_MYS_GREATER = BORNEO_MYS | BORNEO_BRU
BORNEO_IDN = (
    province("IDN.35")
    | province("IDN.34")
    | province("IDN.12")
    | province("IDN.13")
    | province("IDN.14")
)  # kalimantan
BORNEO = BORNEO_MYS_GREATER | BORNEO_IDN

MALAY_PENINSULA_MYS = country("Malaysia") - BORNEO_MYS
MALAY_PENINSULA_SG = country("SGP")
MALAY_PENINSULA = MALAY_PENINSULA_MYS | MALAY_PENINSULA_SG
JAVA = (
    name_starts_with(1, "Jawa")
    | province("IDN.4")
    | name_starts_with(1, "Jakarta")
    | name_starts_with(1, "Yogyakarta")
)
LESSER_SUNDA_IDN = province("IDN.2") | name_starts_with(1, "NusaTeng")
LESSER_SUNDA_TLS = country("TLS")
LESSER_SUNDA = LESSER_SUNDA_IDN | LESSER_SUNDA_TLS

MALUKU_SOUTH = province("IDN.19")
MALUKU_NORTH = province("IDN.18")
MALUKU = MALUKU_SOUTH | MALUKU_NORTH

SULAWESI = name_starts_with(1, "Sulawesi") | province("IDN.6") | province("IDN.29")
KEPULAUAN = province("IDN.16")  # bits of indonesia between indonesia and malaysia
BANGKA = province("IDN.3")  # bits of indonesia between borneo and sumatra
SUMATRA = (
    name_starts_with(1, "Sumatera")
    | province("IDN.1")
    | province("IDN.24")
    | province("IDN.8")
    | province("IDN.17")
    | province("IDN.5")
)
ANDAMAN_NICOBAR = province("IND.1")

PAPUA_IDN = province("IDN.22") | province("IDN.23")

# gangetic
UP_CEDI = (
    district("Jalaun")
    | district("IND.34.34")
    | district("Banda")
    | district("Chitrakoot")
    | district("Jhansi")
    | district("Mahoba")
    | district("Lalitpur")
)
UP_KALAKAVANA = district("Mirzapur") | district("Sonbhadra")
SURASENA = district("Mathura") | district("Agra")
KURU_PROPER = (
    district("Saharanpur")
    | district("Muzaffarnagar")
    | district("Shamli")
    | district("Baghpat")
    | district("Meerut")
    | district("Ghaziabad")
    | district("Hapur")
    | district("Bulandshahr")
    | district("GautamBuddhaNagar")
    | district("IND.35.7")
)
KURU_KSETRA = (
    district("Yamunanagar")
    | district("Kurukshetra")
    | district("Kaithal")
    | district("Jind")
    | district("Karnal")
    | district("Panipat")
)
KURU_JANGALA = (
    province("NCTofDelhi")
    | district("Sonipat")
    | district("Rohtak")
    | district("Jhajjar")
    | district("Gurgaon")
    | district("Faridabad")
    | district("Palwal")
    | district("Mewat")
)
KURU = KURU_PROPER | KURU_JANGALA | KURU_KSETRA
PANCALA_S = (
    district("Aligarh")
    | district("Hathras")
    | district("Etah")
    | district("Kasganj")
    | district("IND.34.28")
    | district("Mainpuri")
    | district("Etawah")
    | district("Farrukhabad")
    | district("Kannauj")
)
PANCALA_N = (
    district("Bijnor")
    | district("Amroha")
    | district("Sambhai")
    | district("Moradabad")
    | district("Rampur")
    | district("Bareilly")
    | district("Budaun")
    | district("IND.34.64")
)
PANCALA = PANCALA_N | PANCALA_S
VATSA = district("Fatehpur") | district("Kaushambi") | district("Allahabad")
KASI = (
    district("Jaunpur")
    | district("SantRaviDasNagar")
    | district("Varanasi")
    | district("Chandauli")
    | district("Kaimur")
    | district("Rohtas")
    | district("Buxar")
    | district("IND.5.7")
)
KOSALA = (
    district("Bahraich")
    | district("Shravasti")
    | district("Gonda")
    | district("IND.34.12")
    | district("SiddharthNagar")
    | district("Basti")
    | district("SantKabirNagar")
    | district("Gorakhpur")
    | district("Faizabad")
    | district("Ambedkarnagar")
    | district("AmbedkarNagar")
    | district("Azamgarh")
    | district("IND.34.54")
    | district("IND.34.11")
    | district("Sultanpur")
    | district("Ghazipur")
)
SAKYA = TERAI_NPL_W
JANAKPUR = TERAI_NPL_C
MALLA = (
    district("Maharajganj")
    | district("Kushinagar")
    | district("Deoria")
    | district("IND.5.11")
    | district("Siwan")
    | district("Saran")
)
VIDEHA_IN = (
    district("PashchimChamparan")
    | district("PurbaChamparan")
    | district("Sheohar")
    | district("Sitamarhi")
    | district("Madhubani")
)
VIDEHA = VIDEHA_IN | JANAKPUR
LICCHAVI = (
    district("Muzaffarpur")
    | district("Vaishali")
    | district("Darbhanga")
    | district("Samastipur")
    | district("Begusarai")
    | district("Khagaria")
)
MAGADHA = (
    district("Patna")
    | district("Jehanabad")
    | district("IND.5.3")
    | district("IND.5.2")
    | district("Gaya")
    | district("Nalanda")
    | district("Sheikhpura")
    | district("Nawada")
    | district("Lakhisarai")
    | district("IND.5.12")
    | district("IND.5.21")
)
KOSALA_GREATER = KOSALA | VIDEHA | LICCHAVI | SAKYA | MALLA | KASI | VATSA
BIHAR_ANGA = district("IND.5.4") | district("IND.5.6")
BIHAR_NORTHEAST = province("Bihar") - (
    VIDEHA | LICCHAVI | MAGADHA | BIHAR_ANGA | KASI | MALLA
)
UP_NAIMISA = province("UttarPradesh") - (
    KURU_PROPER
    | PANCALA_S
    | PANCALA_N
    | SURASENA
    | KOSALA
    | KASI
    | VATSA
    | MALLA
    | UP_CEDI
    | UP_KALAKAVANA
)
BIHAR_N = LICCHAVI | VIDEHA
BIHAR = MAGADHA | LICCHAVI | VIDEHA
UP_EAST = KOSALA_GREATER
UP_WEST = KURU_PROPER | PANCALA | SURASENA
UP = UP_WEST | UP_EAST | UP_NAIMISA
GANGETIC = UP | BIHAR

AVANTI = (
    district("Dewas")
    | district("Ujjain")
    | district("Ratlam")
    | district("Mandsaur")
    | district("Neemuch")
    | district("Jhabua")
    | district("Alirajpur")
    | district("IND.19.16")
    | district("Indore")
)
AKARA = (
    district("AgarMalwa")
    | district("Shajapur")
    | district("Sehore")
    | district("IND.19.34")
    | district("Bhopal")
    | district("Raisen")
    | district("Vidisha")
    | district("IND.19.19")
    | district("IND.19.4")
)
DASARNA = (
    district("IND.19.44")
    | district("IND.19.43")
    | district("Gwalior")
    | district("IND.19.14")
    | district("IND.19.8")
    | district("IND.19.29")
)
PULINDA_W = (
    district("IND.19.21")
    | district("IND.19.18")
    | district("IND.19.51")
    | district("IND.19.10")
    | district("IND.19.6")
)
PULINDA_E = (
    district("Hoshangabad")
    | district("IND.19.7")
    | district("IND.19.12")
    | district("IND.19.30")
    | district("IND.19.40")
    | district("IND.19.27")
    | district("IND.19.5")
    | district("IND.19.17")
)
PULINDA = PULINDA_W | PULINDA_E
MP_CEDI = province("IND.19") - (AVANTI | AKARA | DASARNA | PULINDA_W | PULINDA_E)
CEDI = MP_CEDI | UP_CEDI

BRAHMAVARTA = province("Haryana") | province("NCTofDelhi")

MATSYA = (
    district("IND.29.6")
    | district("IND.29.2")
    | district("Jaipur")
    | district("IND.29.12")
    | district("IND.29.23")
    | district("IND.29.13")
    | district("IND.29.29")
)
KUKURA = (
    district("IND.29.32")
    | district("IND.29.9")
    | district("Ajmer")
    | district("IND.29.7")
    | district("IND.29.28")
    | district("Udaipur")
    | district("Chittaurgarh")
    | district("IND.29.14")
    | district("IND.29.27")
    | district("IND.29.3")
)
KUKURA_GREATER = MATSYA | KUKURA
HADOTI = district("IND.29.24") | district("IND.29.4") | district("IND.29.20")
RJ_MARU = province("Rajasthan") - (MATSYA | KUKURA | HADOTI)
MP = AVANTI | AKARA | DASARNA | PULINDA | CEDI | HADOTI
RJ = province("Rajasthan")

PUNJAB = (
    province("Punjab")
    | district("Chandigarh")
    | district("Islamabad")
    | province("Khyber-Pakhtunkhwa")
) - HIMALAYAN
GANDHARA_W = province("Khyber-Pakhtunkhwa") - HIMALAYAN
PSEUDOSATTAGYDIA_S = taluk("PAK.7.2.1") | taluk("PAK.7.2.4")
PSEUDOSATTAGYDIA_N = district("DeraIsmailKhan") | district("Bannu") | taluk("PAK.5.3.2")
PSEUDOSATTAGYDIA = PSEUDOSATTAGYDIA_N | PSEUDOSATTAGYDIA_S
DOAB_IJ_N = (
    district("Islamabad") | district("Rawalpindi") | district("Sargodha")
) - taluk("PAK.7.8.4")
DOAB_IJ_S = taluk("PAK.7.2.2") | taluk("PAK.7.2.3")
GANDHARA = GANDHARA_W | DOAB_IJ_N
DOAB_IJ = DOAB_IJ_N | DOAB_IJ_S
DOAB_JC = taluk("PAK.7.4.4") | taluk("PAK.7.4.1") | taluk("PAK.7.8.4")
DOAB_CR = (
    taluk("PAK.7.4.2")
    | taluk("PAK.7.4.3")
    | taluk("PAK.7.4.5")
    | taluk("PAK.7.4.6")
    | taluk("PAK.7.4.7")
    | taluk("PAK.7.4.8")
    | taluk("PAK.7.5.3")
    | taluk("PAK.7.5.6")
    | taluk("PAK.7.3.1")
    | taluk("PAK.7.3.2")
    | taluk("PAK.7.3.3")
)
DOAB_RS_N = (
    district("IND.28.16")
    | district("IND.28.8")
    | district("IND.28.1")
    | district("IND.28.22")
)
DOAB_RS_C = (
    taluk("PAK.7.5.1") | taluk("PAK.7.5.2") | taluk("PAK.7.5.4") | taluk("PAK.7.5.5")
)
DOAB_RS_S = district("Multan")
DOAB_RS = DOAB_RS_N | DOAB_RS_C | DOAB_RS_S
BAHAWALPUR = district("Bahawalpur")
TRIGARTA_PROPER = (province("IND.28") | district("Chandigarh")) - DOAB_RS_N
TRIGARTA = province("IND.28") | district("Chandigarh") | DOAB_RS_C
SINDH_N = taluk("PAK.8.3.1") | taluk("8.3.2") | taluk("PAK.8.3.4")
SINDH_SW = (
    taluk("PAK.8.2.5")
    | taluk("PAK.8.5.1")
    | taluk("PAK.8.2.4")
    | taluk("PAK.8.2.1")
    | taluk("PAK.8.2.2")
    | taluk("PAK.8.2.3")
)
SINDH_SE = (
    taluk("PAK.8.1.8") | taluk("PAK.8.1.1") | taluk("PAK.8.1.6") | taluk("PAK.8.4.2")
)
SINDH_W_PROPER = district("PAK.8.3") | taluk("PAK.8.1.2") | taluk("PAK.8.1.4")
SINDH_W = SINDH_W_PROPER | SINDH_SW
SINDH_E_PROPER = (
    taluk("PAK.8.1.3")
    | taluk("PAK.8.1.7")
    | taluk("PAK.8.4.1")
    | taluk("PAK.8.4.4")
    | taluk("PAK.8.4.3")
    | taluk("PAK.8.1.5")
    | taluk("PAK.8.6.1")
    | taluk("PAK.8.6.2")
    | taluk("PAK.8.6.3")
    | taluk("PAK.8.6.4")
    | taluk("PAK.8.6.5")
)
SINDH_E = SINDH_E_PROPER | SINDH_SE
SINDH_S = SINDH_SE | SINDH_SW
SINDH = SINDH_N | SINDH_W_PROPER | SINDH_E_PROPER | SINDH_S
AUDICYA = PUNJAB | SINDH

KUTCH = district("IND.11.16")
ANARTA = (
    district("IND.11.5")
    | district("IND.11.18")
    | district("IND.11.24")
    | district("IND.11.27")
    | district("IND.11.4")
    | district("IND.11.12")
)
SURASTRA = (
    district("IND.11.1")
    | district("IND.11.29")
    | district("IND.11.20")
    | district("IND.11.14")
    | district("IND.11.11")
    | district("IND.11.25")
    | district("IND.11.26")
    | district("IND.11.15")
    | district("IND.11.13")
    | district("IND.11.2")
    | district("IND.11.8")
    | district("IND.11.7")
)
LATA = (
    province("IND.11") | province("DadraandNagarHaveli") | province("DamanandDiu")
) - (KUTCH | ANARTA | SURASTRA)
GUJARAT = KUTCH | ANARTA | SURASTRA | LATA

JHARKHAND_ANGA = (
    district("IND.15.22")
    | district("IND.15.8")
    | district("IND.15.16")
    | district("IND.15.5")
    | district("IND.15.3")
    | district("IND.15.11")
)
JHARKHAND_CHHOTA_NAGPUR = province("Jharkhand") - JHARKHAND_ANGA
WB_CHHOTA_NAGPUR = district("Puruliya")
CHHOTA_NAGPUR = JHARKHAND_CHHOTA_NAGPUR | WB_CHHOTA_NAGPUR
ANGA = BIHAR_ANGA | JHARKHAND_ANGA
PUNDRA_WB = district("IND.36.5") | district("IND.36.20")
GAUDA_EB = district("BGD.5.5")
GAUDA_WB = district("IND.36.13") | district("IND.36.12")
GAUDA = GAUDA_EB | GAUDA_WB
RADHA = district("IND.36.2") | district("IND.36.3") | district("IND.36.4")
SUHMA = (
    district("IND.36.16")
    | district("IND.36.17")
    | district("IND.36.7")
    | district("IND.36.8")
)
VANGA_WB = (
    district("IND.36.11")
    | district("IND.36.14")
    | district("IND.36.15")
    | district("IND.36.19")
)
PUNDRA_EB = province("BGD.5") - GAUDA_EB
VANGA_EB = (
    province("BGD.4")
    | province("BGD.1")
    | district("BGD.3.2")
    | district("BGD.3.4")
    | district("BGD.3.7")
    | district("BGD.3.14")
    | district("BGD.3.15")
)
SAMATATA = country("Bangladesh") - (VANGA_EB | PUNDRA_EB | GAUDA_EB)
VANGA = VANGA_WB | VANGA_EB
PUNDRA = PUNDRA_WB | PUNDRA_EB
CHATTISGARH_N = (
    district("IND.7.19")
    | district("IND.7.7")
    | district("IND.7.12")
    | district("IND.7.21")
    | district("IND.7.16")
    | district("IND.7.17")
    | district("IND.7.25")
    | district("IND.7.26")
    | district("IND.7.13")
    | district("IND.7.3")
)
CHATTISGARH_S = province("Chhattisgarh") - CHATTISGARH_N
KALINGA_UTKALA = (
    district("IND.26.13")
    | district("IND.26.6")
    | district("IND.26.17")
    | district("IND.26.3")
)
KALINGA_PROPER = (
    district("Cuttack")
    | district("IND.26.10")
    | district("IND.26.11")
    | district("IND.26.12")
    | district("IND.26.19")
    | district("IND.26.24")
    | district("IND.26.26")
)
KALINGA_TELUGU = (
    district("IND.2.3")
    | district("IND.2.9")
    | district("IND.2.10")
    | district("IND.2.11")
)
KALINGA = KALINGA_PROPER | KALINGA_TELUGU | KALINGA_UTKALA
UTKALA_PROPER = district("IND.26.22") | district("IND.26.18") | district("IND.26.9")
UTKALA_INNER = (
    district("IND.26.1")
    | district("IND.26.8")
    | district("IND.26.14")
    | district("IND.26.28")
    | district("IND.26.30")
)
UTKALA = UTKALA_PROPER | KALINGA_UTKALA
KALINGA_GREATER = KALINGA | UTKALA
ODRA = province("Odisha") - (KALINGA_PROPER | UTKALA)
GREAT_FOREST_PROPER = ODRA | CHATTISGARH_S
GREAT_FOREST_NORTH = CHATTISGARH_N | UTKALA_PROPER | CHHOTA_NAGPUR
GREAT_FOREST = GREAT_FOREST_NORTH | GREAT_FOREST_PROPER
GREAT_FOREST_GREATER = GREAT_FOREST | UP_KALAKAVANA
BENGAL = ANGA | BIHAR_NORTHEAST | RADHA | SUHMA | GAUDA | PUNDRA | VANGA | SAMATATA

RSIKA = (
    district("IND.20.13")
    | district("IND.20.9")
    | district("IND.20.21")
    | district("IND.20.22")
)
VIDARBHA = (
    district("IND.20.2")
    | district("IND.20.3")
    | district("IND.20.7")
    | district("IND.20.2")
    | district("IND.20.35")
    | district("IND.20.3")
    | district("IND.20.34")
    | district("IND.20.36")
    | district("IND.20.19")
    | district("IND.20.5")
    | district("IND.20.8")
    | district("IND.20.10")
    | district("IND.20.11")
)
NANDED_ASMAKA = (
    taluk("IND.20.20.2")
    | taluk("IND.20.20.3")
    | taluk("IND.20.20.5")
    | taluk("IND.20.20.7")
)
NANDED_MULAKA = district("IND.20.20") - NANDED_ASMAKA
MULAKA = (
    district("IND.20.4")
    | district("IND.20.12")
    | district("IND.20.14")
    | NANDED_MULAKA
    | district("IND.20.25")
    | district("IND.32.1")
)
ASMAKA = (
    district("IND.20.1")
    | district("IND.20.6")
    | district("IND.20.16")
    | NANDED_ASMAKA
    | district("IND.32.3")
    | district("IND.32.8")
)
APARANTA = (
    district("IND.20.17")
    | district("IND.20.18")
    | district("IND.20.24")
    | district("IND.20.27")
    | district("IND.20.28")
    | district("IND.20.33")
    | district("IND.20.31")
)
GREATER_PUNE = province("Maharashtra") - (RSIKA | VIDARBHA | MULAKA | ASMAKA | APARANTA)
MAHISAKA = (
    district("IND.32.2")
    | district("IND.32.5")
    | district("IND.32.6")
    | district("IND.32.9")
)
VENGI_TG = district("IND.32.4") | district("IND.32.7") | district("IND.32.10")
VENGI_AP = district("IND.2.4") | district("IND.2.5") | district("IND.2.12")
VENGI = VENGI_TG | VENGI_AP
AP_KANCI = district("IND.2.2") | district("IND.2.7")
KUNTALA = (
    district("IND.16.1")
    | district("IND.16.5")
    | district("IND.16.15")
    | district("IND.16.21")
    | district("IND.16.24")
    | district("IND.16.6")
    | district("IND.16.7")
    | district("IND.16.13")
    | district("IND.16.16")
    | district("IND.16.30")
)
CAUVERIC = (
    district("IND.16.17")
    | district("IND.16.27")
    | district("IND.16.2")
    | district("IND.16.3")
    | district("IND.16.22")
    | district("IND.16.23")
    | district("IND.16.25")
    | district("IND.16.9")
    | district("IND.16.20")
    | district("IND.16.8")
)
TULU = district("IND.16.28") | district("IND.16.12")
KADAMBA = (
    district("IND.16.29")
    | district("IND.16.4")
    | district("IND.16.14")
    | district("IND.16.18")
    | province("Goa")
)
COORG = district("IND.16.19")
AP_BAYALU = province("IND.2") - (AP_KANCI | VENGI | KALINGA)
KA_BAYALU = province("IND.16") - (KUNTALA | KADAMBA | CAUVERIC | TULU | COORG)
BAYALU = AP_BAYALU | KA_BAYALU
VENGI_COASTAL = (
    district("IND.2.4")
    | district("IND.2.5")
    | district("IND.2.12")
    | district("IND.2.3")
)
KADAMBA_COASTAL = province("IND.10") | district("IND.16.29")
DECCAN = (
    PULINDA
    | VIDARBHA
    | RSIKA
    | MULAKA
    | ASMAKA
    | GREATER_PUNE
    | KUNTALA
    | KADAMBA
    | MAHISAKA
    | VENGI
    | BAYALU
    | CAUVERIC
) - (VENGI_COASTAL | district("IND.2.8") | KADAMBA_COASTAL)

# tamilakam
## conquer the pondicherries
KANNUR_PONDI = district("IND.17.4") | district("IND.27.2")  # to kerala
VILUPPURAM_PONDI = district("IND.31.31") | district("IND.27.3")  # to kanci
NAGAPPATTINAM_PONDI = district("IND.31.13") | district("IND.27.1")  # to cola
KERALA = province("Kerala") | KANNUR_PONDI
MALABAR = KERALA | TULU
TN_KANCI = (
    district("IND.31.4")
    | district("IND.31.29")
    | district("IND.31.30")
    | VILUPPURAM_PONDI
    | district("IND.31.2")
    | district("IND.31.8")
    | district("IND.31.23")
)
KANCI = AP_KANCI | TN_KANCI
PANDYA_PROPER = (
    district("IND.31.12")
    | district("IND.31.19")
    | district("IND.31.22")
    | district("IND.31.17")
    | district("IND.31.25")
    | district("IND.31.27")
    | district("IND.31.32")
)
PANDYA = PANDYA_PROPER | district(
    "IND.31.9"
)  # adding Kanyakumari, which is strictly Ay land
COLA = (
    district("IND.31.16")
    | district("IND.31.26")
    | district("IND.31.15")
    | district("IND.31.1")
    | district("IND.31.20")
    | district("IND.31.24")
    | NAGAPPATTINAM_PONDI
)
KONGU = province("TamilNadu") - (COLA | PANDYA | KANCI)
AY_PROPER = district("IND.17.12") | district("IND.31.9")  # Trivandrum + Kanyakumari
AY = (
    AY_PROPER | district("IND.17.6") | district("IND.17.11")
)  # south kerala, later venad
EZHIMALA_PROPER = (
    district("Kasaragod") | KANNUR_PONDI
)  # north kerala, later kolattunadu
EZHIMALA = EZHIMALA_PROPER | COORG  # Poozhinadu and Karkanadu
CERA = KERALA - (
    AY | EZHIMALA
)  # central kerala, later calicut (the zamorin one) and kochi
SIMHALA = country("LKA")
TAMIL_PROPER = KANCI | COLA | PANDYA | KERALA | KONGU
TAMIL = TAMIL_PROPER | TULU | COORG

# western silk road
KAMBOJA = (
    province("Nuristan")
    | province("Kunar")
    | province("Nangarhar")
    | province("Paktya")
    | province("Khost")
    | province("Logar")
    | province("Wardak")
    | province("Parwan")
    | province("AFG.20")
    | province("Kabul")
    | province("Kapisa")
    | province("Panjshir")
    | province("Bamyan")
)
KANDAHAR = province("Kandahar") | province("Hilmand")  # Arachosia
ZARANJ = province("AFG.7") | province("AFG.23")  # Drangiana
HERAT = province("Hirat")  # Aria
AFG_MARGIANA = province("AFG.2") | province("AFG.8")
AFG_MERU = province("AFG.1")  # Badakhshan
AFG_BACTRIA = (
    province("AFG.31")
    | province("AFG.19")
    | province("AFG.3")
    | province("AFG.4")
    | province("AFG.29")
    | province("AFG.13")
    | province("AFG.30")
)
AFG_MISC = country("AFG") - (
    KAMBOJA | KANDAHAR | ZARANJ | HERAT | AFG_MARGIANA | AFG_BACTRIA | AFG_MERU
)
KAMBOJA_EXT = KAMBOJA | AFG_MISC
BALOCH = province("Balochistan") | province("IRN.26")  # gedrosia
TJK_BACTRIA = (
    province("TJK.3") | province("TJK.1") | district("TJK.5.7")
)  # Khatlon province
TJK_SOGDIA_PROPER = province("TJK.4")
TJK_MERU = province("TJK.2") | (province("TJK.5") - TJK_BACTRIA)  # Badakhshan
UZB_BACTRIA = province("UZB.12")
UZB_SOGDIA_PROPER = (
    province("UZB.6")
    | province("UZB.10")
    | province("UZB.2")
    | province("UZB.9")
    | province("UZB.4")
    | province("UZB.11")
    | province("UZB.13")
    | province("UZB.14")
)  # Tashkentic ppl
UZB_KHWAREZM = province("UZB.5") | province("UZB.7")
UZB_FERGHANA = country("Uzbekistan") - (UZB_BACTRIA | UZB_SOGDIA_PROPER | UZB_KHWAREZM)
TKM_KHWAREZM = province("TKM.3") | province("TKM.6")
TKM_MARGIANA = country("Turkmenistan") - TKM_KHWAREZM
MARGIANA = TKM_MARGIANA | AFG_MARGIANA
BACTRIA = AFG_BACTRIA | TJK_BACTRIA | UZB_BACTRIA
MERU = AFG_MERU | TJK_MERU
SOGDIA_PROPER = UZB_SOGDIA_PROPER | TJK_SOGDIA_PROPER
FERGHANA = UZB_FERGHANA
SOGDIA = SOGDIA_PROPER | FERGHANA
KHWAREZM = UZB_KHWAREZM | TKM_KHWAREZM

# eastern silk road oasis states
# kashgar, khotan, rouran, kucha, agni, turfan
KASHGAR = district("CHN.28.9")
KHOTAN = district("CHN.28.10")
KUCHA = (
    taluk("CHN.28.1.5")
    | taluk("CHN.28.1.3")
    | taluk("CHN.28.1.7")
    | taluk("CHN.28.1.6")
)
AKSU = district("CHN.28.1") - KUCHA
ROURAN = taluk("CHN.28.3.7")
AGNI = taluk("CHN.28.3.8")
QIEMO = taluk("CHN.28.3.6")
KORLA = taluk("CHN.28.3.4")
TURFAN = district("CHN.28.14")
TARIM = (
    district("CHN.28.1")
    | district("CHN.28.3")
    | district("CHN.28.9")
    | district("CHN.28.10")
    | district("CHN.28.11")
)
DZUNGARIA = province("CHN.28") - TARIM
MONGOLIA = country("Mongolia") | province("CHN.19")

# big regions
SUBCONTINENT = (
    country("India")
    | country("Pakistan")
    | country("Afghanistan")
    | country("Bangladesh")
    | country("SriLanka")
    | country("Nepal")
    | country("Bhutan")
) | CHINESE_CLAIMS
CENTRAL_ASIA = (
    country("Afghanistan")
    | province("Balochistan")
    | province("IRN.26")
    | country("Tajikistan")
    | country("Uzbekistan")
    | country("Turkmenistan")
)
SUBCONTINENT_PROPER = (SUBCONTINENT | TERAI) - (
    CENTRAL_ASIA | INNER_KAMBOJA | HIMALAYAN | ANDAMAN_NICOBAR
)
CENTRAL_ASIA_GREATER = CENTRAL_ASIA | INNER_KAMBOJA
SEA_MARITIME = (
    SUMATRA
    | JAVA
    | BORNEO
    | SULAWESI
    | LESSER_SUNDA
    | MALUKU
    | PAPUA_IDN
    | MALAY_PENINSULA
    | KEPULAUAN
    | BANGKA
    | ANDAMAN_NICOBAR
)
SEA_MAINLAND = (
    SIAM | BURMA | LAOS | KHMER | CHAM | SIAM_BURMA_INTERM | KAREN | TIBET_BURMA_INTERM
)
SEA = SEA_MARITIME | SEA_MAINLAND
INDOSPHERE = SUBCONTINENT | CENTRAL_ASIA | TARIM | TIBET | SEA | HIMALAYAN
JAMBUDVIPA = SUBCONTINENT_PROPER - SIMHALA
NORTH_INDIA = (
    GANGETIC | BRAHMAVARTA | BENGAL | AUDICYA | RJ | MP | GUJARAT | UP_KALAKAVANA
) - PULINDA
ARYAVARTA = UP | BRAHMAVARTA
GY_DOAB = (
    KURU_PROPER
    | PANCALA_S
    | VATSA
    | district("IND.34.7")
    | district("IND.34.42")
    | district("IND.34.43")
)

# uncultivated (YYY) or historically unidentified (ZZZ) lands
YYY_MARU = RJ_MARU
YYY_NAIMISA = UP_NAIMISA
YYY_KALAKAVANA = UP_KALAKAVANA
YYY_GREAT_FOREST = GREAT_FOREST
YYY_HIMALAYAN = HIMALAYAN
ZZZ_BIHAR_NORTHEAST = BIHAR_NORTHEAST
ZZZ_BAHAWALPUR = BAHAWALPUR
ZZZ_HADOTI = HADOTI
ZZZ_GREATER_PUNE = GREATER_PUNE
ZZZ_BAYALU = BAYALU