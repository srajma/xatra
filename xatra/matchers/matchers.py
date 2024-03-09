"""
Library of Matchers for flags
"""


# useful function tool
def _curry(func):
    def curried(*args):
        # print(f'{args}')
        if len(args) == func.__code__.co_argcount:
            return func(*args)
        else:
            return lambda x: curried(*(args + (x,)))

    return curried


# basic version of match
@_curry
def match_raw(field, value, feature):
    return value == feature.get("properties", {}).get(field, "")


# supported fields:
# COUNTRY, NAME_i, GID_i
# e.g. match("COUNTRY", "Tajikistan", feature) matches all features in Tajikistan
@_curry
def match_field(field, value, feature):
    if field == "COUNTRY":
        return match_raw(field, value, feature)
    elif field.startswith("NAME_"):  # also match VARNAME_
        check_NAME = match_raw(field, value, feature)
        check_VARNAME = value in feature.get("properties", {}).get(
            "VAR" + field, ""
        ).split("|")
        return check_NAME or check_VARNAME
    elif field.startswith("GID_"):
        gid = feature.get("properties", {}).get(field, "")
        return gid == value or gid.startswith(value + "_")


@_curry
def name_starts_with(level, value, feature):
    return feature.get("properties", {}).get("NAME_" + str(level), "").startswith(value)


# more intuitive match (matches any level = i field)
# e.g. match_level(0, "Tajikistan", feature)
@_curry
def match(level, value, feature):
    check_COUNTRY = level == 0 and match_field("COUNTRY", value, feature)
    check_NAME = match_field("NAME_" + str(level), value, feature)
    check_GID = match_field("GID_" + str(level), value, feature)
    return check_COUNTRY or check_NAME or check_GID


# e.g. country("India"); province("Sindh")
country = match(0)
province = match(1)
district = match(2)
taluk = match(3)

# e.g. union(country("India"), province("Sindh")) matches everything in India or Sindh
# a matcher is a function: feature -> Bool, i.e. exactly what you'd pass to a flag as a property

union = lambda *matchers: lambda feature: any(
    [matcher(feature) for matcher in matchers]
)
inter = lambda *matchers: lambda feature: all(
    [matcher(feature) for matcher in matchers]
)
compl = lambda matcher: lambda feature: not matcher(feature)
minus = lambda big, small: inter(big, compl(small))

"""custom, recurring, world regions"""

# sorting the himalayas
CHINESE_CLAIMS_UK = union(country("Z05"), province("Z09.35"))
CHINESE_CLAIMS_HP = union(province("Z09.13"), country("Z04"))
CHINESE_CLAIMS_LADAKH = union(country("Z03"), country("Z08"))  # Aksai Chin
CHINESE_CLAIMS_GILGIT = country("Z02")
CHINESE_CLAIMS_AP = country("Z07")
CHINESE_CLAIMS = union(
    CHINESE_CLAIMS_UK,
    CHINESE_CLAIMS_HP,
    CHINESE_CLAIMS_AP,
    CHINESE_CLAIMS_LADAKH,
    CHINESE_CLAIMS_GILGIT,
)
TERAI_HP = union(
    district("IND.13.4"),
    district("IND.13.3"),
    district("IND.13.12"),
    district("IND.13.1"),
    district("IND.13.11"),
    district("IND.13.10"),
)
TERAI_UK = union(
    district("IND.35.5"),
    district("IND.35.12"),
    district("IND.35.7"),
    district("IND.35.8"),
)
TERAI_NPL_FW = union(taluk("NPL.3.1.4"), taluk("NPL.3.2.5"))
TERAI_NPL_MW = union(taluk("NPL.4.1.1"), taluk("NPL.4.1.2"))
TERAI_NPL_W = union(taluk("NPL.5.3.3"), taluk("NPL.5.3.6"), taluk("NPL.5.3.4"))  # sakya
TERAI_NPL_C = union(  # janakpur
    taluk("NPL.1.3.4"),
    taluk("NPL.1.3.1"),
    taluk("NPL.1.3.5"),
    taluk("NPL.1.2.5"),
    taluk("NPL.1.2.3"),
    taluk("NPL.1.2.1"),
)
TERAI_NPL_E = union(
    taluk("NPL.2.3.4"),
    taluk("NPL.2.3.3"),
    taluk("NPL.2.1.3"),
    taluk("NPL.2.1.5"),
    taluk("NPL.2.2.2"),
)
TERAI_NPL = union(TERAI_NPL_FW, TERAI_NPL_MW, TERAI_NPL_W, TERAI_NPL_C, TERAI_NPL_E)
TERAI = union(TERAI_HP, TERAI_UK, TERAI_NPL)
HP_HIM = minus(union(province("HimachalPradesh"), CHINESE_CLAIMS_HP), TERAI_HP)
UK_HIM = minus(union(province("Uttarakhand"), CHINESE_CLAIMS_UK), TERAI_UK)
NPL_HIM = minus(country("Nepal"), TERAI_NPL)
LADAKH = union(
    district("Leh(Ladakh)"),
    district("Kargil"),
    country("Z03"),  # Aksai Chin main part
    country("Z08"),  # Aksai Chin Southern bit
)
KASHMIR_MISC = union(  # Jammu & Kashmir excluding the Kashmir valley proper
    district("Z01.14.10"),
    district("Z01.14.5"),
    district("Z01.14.17"),
    district("Z01.14.18"),
    district("Z01.14.22"),
    district("Jammu"),
    district("Z01.14.19"),
    district("Z01.14.9"),
)
KASHMIR_PROPER = minus(province("JammuandKashmir"), union(KASHMIR_MISC, LADAKH))
KASHMIR_TBC = province("Z06.1")  # POK
KASHMIR = union(KASHMIR_PROPER, KASHMIR_MISC, KASHMIR_TBC)
DARADA = province("Gilgit-Baltistan")
KHYBER_HIM = union(district("Malakand"), district("Hazara"))
BENGAL_HIM = union(
    district("Darjiling"),
    district("Jalpaiguri"),
    district("Alipurduar"),
    district("KochBihar"),
)
ASSAM_HIM = union(
    district("IND.4.4"),
    district("IND.4.10"),
    district("IND.4.13"),
    district("IND.4.18"),
    district("IND.4.17"),
    district("IND.4.22"),
)
LAUHITYA = minus(province("Assam"), ASSAM_HIM)
NEI_HIM = union(  # NE India excluding Assam
    province("ArunachalPradesh"),
    province("Meghalaya"),
    province("Nagaland"),
    province("Manipur"),
    province("Mizoram"),
    province("Tripura"),
    ASSAM_HIM,
)
INNER_KAMBOJA = province("PAK.3")  # Federally Administered Tribal Areas
HIMALAYAN = union(
    HP_HIM,
    UK_HIM,
    NPL_HIM,
    country("Bhutan"),
    BENGAL_HIM,
    NEI_HIM,
    province("Sikkim"),
    LADAKH,
    DARADA,
    KHYBER_HIM,
    CHINESE_CLAIMS,
)

# tibeto-burman region

TIBET_CN_TIB = province("CHN.29")  # chinese occupied tibet
TIBET_CN_QIN = province("CHN.21")  # chinese occupied tibet
TIBET_CN_SIC = union(
    district("CHN.26.5"), district("CHN.26.16")
)  # chinese occupied tibet
TIBET_CN = union(TIBET_CN_TIB, TIBET_CN_QIN, TIBET_CN_SIC)
TIBET_BHU = country("Bhutan")  # bhutanese occupied tibet
TIBET_NEP = union(
    taluk("NPL.4.2.1"),
    taluk("NPL.4.2.2"),
    taluk("NPL.4.2.5"),
    district("NPL.5.1"),
    district("NPL.5.2"),
    district("NPL.1.1"),
    taluk("NPL.1.2.2"),
    taluk("NPL.1.2.4"),
    taluk("NPL.1.2.6"),
    taluk("NPL.2.3.5"),
    taluk("NPL.2.3.1"),
    taluk("NPL.2.3.2"),
    taluk("NPL.2.1.1"),
    taluk("NPL.2.1.4"),
    taluk("NPL.2.1.2"),
    taluk("NPL.2.1.6"),
    taluk("NPL.2.2.4"),
    taluk("NPL.2.2.3"),
    taluk("NPL.2.2.1"),
)  # nepali-occupied tibet
TIBET_AP = CHINESE_CLAIMS_AP  # chinese-occupied tibet :(
TIBET_LAD = LADAKH  # tibet in its rightful home
TIBET_SIK = province("Sikkim")  # tibet in its rightful home
TIBET = union(TIBET_CN, TIBET_BHU, TIBET_NEP, TIBET_LAD, TIBET_AP, TIBET_SIK)

TIBET_BURMA_INTERM = minus(
    union(NEI_HIM, province("MMR.3")), TIBET
)  # intermediary region from Tibet to Burma
YUNNAN_BURMA_INTERM = province("MMR.4")  # kachin state
KAREN = union(province("MMR.5"), province("MMR.6"))  # karenic parts of myanmar
SIAM_BURMA_INTERM = province("MMR.13")  # shan state

BURMA_UPPER = union(
    province("MMR.12"), province("MMR.7"), province("MMR.8"), province("MMR.10")
)
BURMA_LOWER_RIVER = union(
    province("MMR.2"),
    province("MMR.1"),
    province("MMR.15"),
)
BURMA_LOWER_RAKHINE = province("MMR.11")
BURMA_LOWER_THAICOAST = union(province("MMR.9"), province("MMR.14"))
BURMA_LOWER = union(BURMA_LOWER_RIVER, BURMA_LOWER_RAKHINE, BURMA_LOWER_THAICOAST)
BURMA = union(BURMA_UPPER, BURMA_LOWER)

# southeast asia
SIAM_THA = country("Thailand")
SIAM = union(SIAM_THA)
LAOS = country("Laos")
KHMER = country("Cambodia")
CHAM = union(
    province("VNM.41"),
    province("VNM.29"),
    province("VNM.46"),
    province("VNM.50"),
    province("VNM.54"),
    province("VNM.19"),
    province("VNM.47"),
    province("VNM.48"),
    province("VNM.34"),
    province("VNM.8"),
    province("VNM.21"),
    province("VNM.45"),
    province("VNM.32"),
    province("VNM.15"),
    province("VNM.43"),
    province("VNM.37"),
    province("VNM.16"),
    province("VNM.11"),
    province("VNM.7"),
    province("VNM.17"),
    province("VNM.10"),
    province("VNM.25"),
    province("VNM.9"),
    province("VNM.53"),
    province("VNM.23"),
    province("VNM.39"),
    province("VNM.58"),
    province("VNM.6"),
    province("VNM.59"),
    province("VNM.61"),
    province("VNM.18"),
    province("VNM.51"),
    province("VNM.24"),
    province("VNM.2"),
    province("VNM.33"),
    province("VNM.12"),
    province("VNM.1"),
    province("VNM.13"),
    province("VNM.33"),
)
NORTH_VIETNAM = minus(country("Vietnam"), CHAM)
BORNEO_MYS = union(
    province("MYS.13"), province("MYS.14"), province("MYS.5")
)  # sabah serawak
BORNEO_BRU = country("Brunei")
BORNEO_MYS_GREATER = union(BORNEO_MYS, BORNEO_BRU)
BORNEO_IDN = union(
    province("IDN.35"),
    province("IDN.34"),
    province("IDN.12"),
    province("IDN.13"),
    province("IDN.14"),
)  # kalimantan
BORNEO = union(BORNEO_MYS_GREATER, BORNEO_IDN)

MALAY_PENINSULA_MYS = minus(country("Malaysia"), BORNEO_MYS)
MALAY_PENINSULA_SG = country("SGP")
MALAY_PENINSULA = union(MALAY_PENINSULA_MYS, MALAY_PENINSULA_SG)
JAVA = union(
    name_starts_with(1, "Jawa"),
    province("IDN.4"),
    name_starts_with(1, "Jakarta"),
    name_starts_with(1, "Yogyakarta"),
)
LESSER_SUNDA_IDN = union(
    province("IDN.2"),  # bali
    name_starts_with(1, "NusaTeng"),  # nusa tenggara
)  # just east of java
LESSER_SUNDA_TLS = country("TLS")
LESSER_SUNDA = union(LESSER_SUNDA_IDN, LESSER_SUNDA_TLS)

MALUKU_SOUTH = province("IDN.19")
MALUKU_NORTH = province("IDN.18")
MALUKU = union(MALUKU_SOUTH, MALUKU_NORTH)  # just east of lesser sunda

SULAWESI = union(
    name_starts_with(1, "Sulawesi"),
    province("IDN.6"),
    province("IDN.29"),
)  # just east of borneo

KEPULAUAN = province("IDN.16")  # bits of indonesia between indonesia and malaysia
BANGKA = province("IDN.3")  # bits of indonesia between borneo and sumatra
SUMATRA = union(
    name_starts_with(1, "Sumatera"),
    province("IDN.1"),
    province("IDN.24"),
    province("IDN.8"),
    province("IDN.17"),
    province("IDN.5"),
)
ANDAMAN_NICOBAR = province("IND.1")

PAPUA_IDN = union(province("IDN.22"), province("IDN.23"))

# gangetic
UP_CEDI = union(  # Protruding bits of UP belonging to Cedi region
    district("Jalaun"),
    district("IND.34.34"),
    district("Banda"),
    district("Chitrakoot"),
    district("Jhansi"),
    district("Mahoba"),
    district("Lalitpur"),
)
UP_KALAKAVANA = union(  # Protruding bits of UP belonging to Kalakavana forest
    district("Mirzapur"), district("Sonbhadra")
)
SURASENA = union(district("Mathura"), district("Agra"))
KURU_PROPER = union(
    district("Saharanpur"),
    district("Muzaffarnagar"),
    district("Shamli"),
    district("Baghpat"),
    district("Meerut"),
    district("Ghaziabad"),
    district("Hapur"),
    district("Bulandshahr"),
    district("GautamBuddhaNagar"),
    district("IND.35.7"),  # Haridwar (spelled Hardwar in data); in Uttarakhand not UP
)
KURU_KSETRA = union(
    district("Yamunanagar"),
    district("Kurukshetra"),
    district("Kaithal"),
    district("Jind"),
    district("Karnal"),
    district("Panipat"),
)
KURU_JANGALA = union(
    province("NCTofDelhi"),
    district("Sonipat"),
    district("Rohtak"),
    district("Jhajjar"),
    district("Gurgaon"),
    district("Faridabad"),
    district("Palwal"),
    district("Mewat"),
)
KURU = union(KURU_PROPER, KURU_JANGALA, KURU_KSETRA)
PANCALA_S = union(
    district("Aligarh"),
    district("Hathras"),
    district("Etah"),
    district("Kasganj"),
    district("IND.34.28"),
    district("Mainpuri"),
    district("Etawah"),
    district("Farrukhabad"),
    district("Kannauj"),
)
PANCALA_N = union(
    district("Bijnor"),
    district("Amroha"),
    district("Sambhai"),
    district("Moradabad"),
    district("Rampur"),
    district("Bareilly"),
    district("Budaun"),
    district("IND.34.64"),
)
PANCALA = union(PANCALA_N, PANCALA_S)
VATSA = union(district("Fatehpur"), district("Kaushambi"), district("Allahabad"))
KASI = union(
    district("Jaunpur"),
    district("SantRaviDasNagar"),
    district("Varanasi"),
    district("Chandauli"),
    district("Kaimur"),
    district("Rohtas"),
    district("Buxar"),
    district("IND.5.7"),
)  # Bhojpur district; there's another in Nepal (actually that one's Lev 3 so it'd be fine)
KOSALA = union(
    district("Bahraich"),
    district("Shravasti"),
    district("Gonda"),
    district("IND.34.12"),
    district("SiddharthNagar"),
    district("Basti"),
    district("SantKabirNagar"),
    district("Gorakhpur"),
    district("Faizabad"),
    district("Ambedkarnagar"),
    district("AmbedkarNagar"),
    district("Azamgarh"),
    district("IND.34.54"),
    district("IND.34.11"),
    district("Sultanpur"),
    district("Ghazipur"),
)
SAKYA = TERAI_NPL_W
JANAKPUR = TERAI_NPL_C
MALLA = union(
    district("Maharajganj"),
    district("Kushinagar"),
    district("Deoria"),
    district("IND.5.11"),
    district("Siwan"),
    district("Saran"),
)
VIDEHA_IN = union(
    district("PashchimChamparan"),
    district("PurbaChamparan"),
    district("Sheohar"),
    district("Sitamarhi"),
    district("Madhubani"),
)
VIDEHA = union(VIDEHA_IN, JANAKPUR)
LICCHAVI = union(
    district("Muzaffarpur"),
    district("Vaishali"),
    district("Darbhanga"),
    district("Samastipur"),
    district("Begusarai"),
    district("Khagaria"),
)
MAGADHA = union(
    district("Patna"),
    district("Jehanabad"),
    district("IND.5.3"),
    district("IND.5.2"),
    district("Gaya"),
    district("Nalanda"),
    district("Sheikhpura"),
    district("Nawada"),
    district("Lakhisarai"),
    district("IND.5.12"),
    district("IND.5.21"),
)
KOSALA_GREATER = union(KOSALA, VIDEHA, LICCHAVI, SAKYA, MALLA, KASI, VATSA)
BIHAR_ANGA = union(district("IND.5.4"), district("IND.5.6"))
BIHAR_NORTHEAST = minus(
    province("Bihar"), union(VIDEHA, LICCHAVI, MAGADHA, BIHAR_ANGA, KASI, MALLA)
)
UP_NAIMISA = minus(
    province("UttarPradesh"),
    union(
        KURU_PROPER,
        PANCALA_S,
        PANCALA_N,
        SURASENA,
        KOSALA,
        KASI,
        VATSA,
        MALLA,
        UP_CEDI,
        UP_KALAKAVANA,
    ),
)
BIHAR_N = union(LICCHAVI, VIDEHA)
BIHAR = union(
    MAGADHA, LICCHAVI, VIDEHA
)  # east Bihar (ANGA and BIHAR_NORTHEAST) goes to Bengal (below)
UP_EAST = KOSALA_GREATER
UP_WEST = union(KURU_PROPER, PANCALA, SURASENA)
UP = union(UP_WEST, UP_EAST, UP_NAIMISA)
# UP = minus(province("UttarPradesh"), union(UP_CEDI, UP_KALAKAVANA))
GANGETIC = union(UP, BIHAR)

# greater madhya pradesh
AVANTI = union(
    district("Dewas"),
    district("Ujjain"),
    district("Ratlam"),
    district("Mandsaur"),
    district("Neemuch"),
    district("Jhabua"),
    district("Alirajpur"),
    district("IND.19.16"),
    district("Indore"),
)
AKARA = union(
    district("AgarMalwa"),
    district("Shajapur"),
    district("Sehore"),
    district("IND.19.34"),
    district("Bhopal"),
    district("Raisen"),
    district("Vidisha"),
    district("IND.19.19"),
    district("IND.19.4"),
)
DASARNA = union(
    district("IND.19.44"),
    district("IND.19.43"),
    district("Gwalior"),
    district("IND.19.14"),
    district("IND.19.8"),
    district("IND.19.29"),
)
PULINDA_W = union(
    district("IND.19.21"),
    district("IND.19.18"),
    district("IND.19.51"),
    district("IND.19.10"),
    district("IND.19.6"),
)
PULINDA_E = union(
    district("Hoshangabad"),
    district("IND.19.7"),
    district("IND.19.12"),
    district("IND.19.30"),
    district("IND.19.40"),
    district("IND.19.27"),
    district("IND.19.5"),
    district("IND.19.17"),
)
PULINDA = union(PULINDA_W, PULINDA_E)
MP_CEDI = minus(province("IND.19"), union(AVANTI, AKARA, DASARNA, PULINDA_W, PULINDA_E))
CEDI = union(MP_CEDI, UP_CEDI)

# haryana/brahmavarta/"bharata" of panini
BRAHMAVARTA = union(province("Haryana"), province("NCTofDelhi"))

# rajasthan
MATSYA = union(
    district("IND.29.6"),
    district("IND.29.2"),
    district("Jaipur"),
    district("IND.29.12"),
    district("IND.29.23"),
    district("IND.29.13"),
    district("IND.29.29"),
)
KUKURA = union(
    district("IND.29.32"),
    district("IND.29.9"),
    district("Ajmer"),
    district("IND.29.7"),
    district("IND.29.28"),
    district("Udaipur"),
    district("Chittaurgarh"),
    district("IND.29.14"),
    district("IND.29.27"),
    district("IND.29.3"),
)
KUKURA_GREATER = union(MATSYA, KUKURA)
HADOTI = union(district("IND.29.24"), district("IND.29.4"), district("IND.29.20"))
RJ_MARU = minus(province("Rajasthan"), union(MATSYA, KUKURA, HADOTI))
MP = union(AVANTI, AKARA, DASARNA, PULINDA, CEDI, HADOTI)
RJ = province("Rajasthan")

# audicya
PUNJAB = minus(
    union(
        province("Punjab"),
        district("Chandigarh"),
        district("Islamabad"),
        province("Khyber-Pakhtunkhwa"),
    ),
    HIMALAYAN,
)
GANDHARA_W = minus(province("Khyber-Pakhtunkhwa"), HIMALAYAN)
PSEUDOSATTAGYDIA_S = union(taluk("PAK.7.2.1"), taluk("PAK.7.2.4"))
PSEUDOSATTAGYDIA_N = union(
    district("DeraIsmailKhan"), district("Bannu"), taluk("PAK.5.3.2")
)
PSEUDOSATTAGYDIA = union(PSEUDOSATTAGYDIA_N, PSEUDOSATTAGYDIA_S)
DOAB_IJ_N = minus(
    union(district("Islamabad"), district("Rawalpindi"), district("Sargodha")),
    taluk("PAK.7.8.4"),
)
DOAB_IJ_S = union(taluk("PAK.7.2.2"), taluk("PAK.7.2.3"))
GANDHARA = union(GANDHARA_W, DOAB_IJ_N)
DOAB_IJ = union(DOAB_IJ_N, DOAB_IJ_S)
DOAB_JC = union(taluk("PAK.7.4.4"), taluk("PAK.7.4.1"), taluk("PAK.7.8.4"))
DOAB_CR = union(
    taluk("PAK.7.4.2"),
    taluk("PAK.7.4.3"),
    taluk("PAK.7.4.5"),
    taluk("PAK.7.4.6"),
    taluk("PAK.7.4.7"),
    taluk("PAK.7.4.8"),
    taluk("PAK.7.5.3"),
    taluk("PAK.7.5.6"),
    taluk("PAK.7.3.1"),
    taluk("PAK.7.3.2"),
    taluk("PAK.7.3.3"),
)
DOAB_RS_N = union(
    district("IND.28.16"),
    district("IND.28.8"),
    district("IND.28.1"),
    district("IND.28.22"),
)
DOAB_RS_C = union(
    taluk("PAK.7.5.1"), taluk("PAK.7.5.2"), taluk("PAK.7.5.4"), taluk("PAK.7.5.5")
)
DOAB_RS_S = district("Multan")
DOAB_RS = union(DOAB_RS_N, DOAB_RS_C, DOAB_RS_S)
BAHAWALPUR = district("Bahawalpur")
TRIGARTA_PROPER = minus(union(province("IND.28"), district("Chandigarh")), DOAB_RS_N)
TRIGARTA = union(province("IND.28"), district("Chandigarh"), DOAB_RS_C)
SINDH_N = union(taluk("PAK.8.3.1"), taluk("8.3.2"), taluk("PAK.8.3.4"))
SINDH_SW = union(
    taluk("PAK.8.2.5"),
    taluk("PAK.8.5.1"),
    taluk("PAK.8.2.4"),
    taluk("PAK.8.2.1"),
    taluk("PAK.8.2.2"),
    taluk("PAK.8.2.3"),
)
SINDH_SE = union(
    taluk("PAK.8.1.8"), taluk("PAK.8.1.1"), taluk("PAK.8.1.6"), taluk("PAK.8.4.2")
)
SINDH_W_PROPER = union(district("PAK.8.3"), taluk("PAK.8.1.2"), taluk("PAK.8.1.4"))
SINDH_W = union(SINDH_W_PROPER, SINDH_SW)
SINDH_E_PROPER = union(
    taluk("PAK.8.1.3"),
    taluk("PAK.8.1.7"),
    taluk("PAK.8.4.1"),
    taluk("PAK.8.4.4"),
    taluk("PAK.8.4.3"),
    taluk("PAK.8.1.5"),
    taluk("PAK.8.6.1"),
    taluk("PAK.8.6.2"),
    taluk("PAK.8.6.3"),
    taluk("PAK.8.6.4"),
    taluk("PAK.8.6.5"),
)
SINDH_E = union(SINDH_E_PROPER, SINDH_SE)
SINDH_S = union(SINDH_SE, SINDH_SW)
SINDH = union(SINDH_N, SINDH_W_PROPER, SINDH_E_PROPER, SINDH_S)
AUDICYA = union(PUNJAB, SINDH)

# gujarat
KUTCH = district("IND.11.16")
ANARTA = union(
    district("IND.11.5"),
    district("IND.11.18"),
    district("IND.11.24"),
    district("IND.11.27"),
    district("IND.11.4"),
    district("IND.11.12"),
)
SURASTRA = union(
    district("IND.11.1"),
    district("IND.11.29"),
    district("IND.11.20"),
    district("IND.11.14"),
    district("IND.11.11"),
    district("IND.11.25"),
    district("IND.11.26"),
    district("IND.11.15"),
    district("IND.11.13"),
    district("IND.11.2"),
    district("IND.11.8"),
    district("IND.11.7"),
)
LATA = minus(
    union(province("IND.11"), province("DadraandNagarHaveli"), province("DamanandDiu")),
    union(KUTCH, ANARTA, SURASTRA),
)
GUJARAT = union(KUTCH, ANARTA, SURASTRA, LATA)

# nga and forests
JHARKHAND_ANGA = union(
    district("IND.15.22"),
    district("IND.15.8"),
    district("IND.15.16"),
    district("IND.15.5"),
    district("IND.15.3"),
    district("IND.15.11"),
)
JHARKHAND_CHHOTA_NAGPUR = minus(province("Jharkhand"), JHARKHAND_ANGA)
WB_CHHOTA_NAGPUR = district("Puruliya")
CHHOTA_NAGPUR = union(JHARKHAND_CHHOTA_NAGPUR, WB_CHHOTA_NAGPUR)
ANGA = union(BIHAR_ANGA, JHARKHAND_ANGA)
PUNDRA_WB = union(district("IND.36.5"), district("IND.36.20"))
GAUDA_EB = district("BGD.5.5")
GAUDA_WB = union(district("IND.36.13"), district("IND.36.12"))
GAUDA = union(GAUDA_EB, GAUDA_WB)
RADHA = union(district("IND.36.2"), district("IND.36.3"), district("IND.36.4"))
SUHMA = union(
    district("IND.36.16"),
    district("IND.36.17"),
    district("IND.36.7"),
    district("IND.36.8"),
)
VANGA_WB = union(
    district("IND.36.11"),
    district("IND.36.14"),
    district("IND.36.15"),
    district("IND.36.19"),
)
PUNDRA_EB = minus(province("BGD.5"), GAUDA_EB)
VANGA_EB = union(
    province("BGD.4"),
    province("BGD.1"),
    district("BGD.3.2"),
    district("BGD.3.4"),
    district("BGD.3.7"),
    district("BGD.3.14"),
    district("BGD.3.15"),
)
SAMATATA = minus(country("Bangladesh"), union(VANGA_EB, PUNDRA_EB, GAUDA_EB))
VANGA = union(VANGA_WB, VANGA_EB)
PUNDRA = union(PUNDRA_WB, PUNDRA_EB)
CHATTISGARH_N = union(
    district("IND.7.19"),
    district("IND.7.7"),
    district("IND.7.12"),
    district("IND.7.21"),
    district("IND.7.16"),
    district("IND.7.17"),
    district("IND.7.25"),
    district("IND.7.26"),
    district("IND.7.13"),
    district("IND.7.3"),
)
CHATTISGARH_S = minus(province("Chhattisgarh"), CHATTISGARH_N)
KALINGA_UTKALA = union(
    district("IND.26.13"),
    district("IND.26.6"),
    district("IND.26.17"),
    district("IND.26.3"),
)
KALINGA_PROPER = union(
    district("Cuttack"),
    district("IND.26.10"),
    district("IND.26.11"),
    district("IND.26.12"),
    district("IND.26.19"),
    district("IND.26.24"),
    district("IND.26.26"),
)
KALINGA_TELUGU = union(
    district("IND.2.3"), district("IND.2.9"), district("IND.2.10"), district("IND.2.11")
)
KALINGA = union(KALINGA_PROPER, KALINGA_TELUGU, KALINGA_UTKALA)
UTKALA_PROPER = union(
    district("IND.26.22"), district("IND.26.18"), district("IND.26.9")
)
UTKALA_INNER = union(
    district("IND.26.1"),
    district("IND.26.8"),
    district("IND.26.14"),
    district("IND.26.28"),
    district("IND.26.30"),
)
UTKALA = union(
    UTKALA_PROPER, KALINGA_UTKALA
)  # let's not include UKTALA_INNER it's weird
KALINGA_GREATER = union(KALINGA, UTKALA)
ODRA = minus(province("Odisha"), union(KALINGA_PROPER, UTKALA))
GREAT_FOREST_PROPER = union(ODRA, CHATTISGARH_S)
GREAT_FOREST_NORTH = union(CHATTISGARH_N, UTKALA_PROPER, CHHOTA_NAGPUR)
GREAT_FOREST = union(GREAT_FOREST_NORTH, GREAT_FOREST_PROPER)
GREAT_FOREST_GREATER = union(GREAT_FOREST, UP_KALAKAVANA)
BENGAL = union(ANGA, BIHAR_NORTHEAST, RADHA, SUHMA, GAUDA, PUNDRA, VANGA, SAMATATA)

# deccan
RSIKA = union(
    district("IND.20.13"),
    district("IND.20.9"),
    district("IND.20.21"),
    district("IND.20.22"),
)
VIDARBHA = union(
    district("IND.20.2"),
    district("IND.20.3"),
    district("IND.20.7"),
    district("IND.20.2"),
    district("IND.20.35"),
    district("IND.20.3"),
    district("IND.20.34"),
    district("IND.20.36"),
    district("IND.20.19"),
    district("IND.20.5"),
    district("IND.20.8"),
    district("IND.20.10"),
    district("IND.20.11"),
)
NANDED_ASMAKA = union(  # Nanded South of Narmada
    taluk("IND.20.20.2"),
    taluk("IND.20.20.3"),
    taluk("IND.20.20.5"),
    taluk("IND.20.20.7"),
)
NANDED_MULAKA = minus(district("IND.20.20"), NANDED_ASMAKA)  # Nanded North of Narmada
MULAKA = union(
    district("IND.20.4"),
    district("IND.20.12"),
    district("IND.20.14"),
    NANDED_MULAKA,
    district("IND.20.25"),
    district("IND.32.1"),
)
ASMAKA = union(
    district("IND.20.1"),
    district("IND.20.6"),
    district("IND.20.16"),
    NANDED_ASMAKA,
    district("IND.32.3"),
    district("IND.32.8"),
)
APARANTA = union(
    district("IND.20.17"),
    district("IND.20.18"),
    district("IND.20.24"),
    district("IND.20.27"),
    district("IND.20.28"),
    district("IND.20.33"),
    district("IND.20.31"),
)
GREATER_PUNE = minus(
    province("Maharashtra"), union(RSIKA, VIDARBHA, MULAKA, ASMAKA, APARANTA)
)
MAHISAKA = union(
    district("IND.32.2"),
    district("IND.32.5"),
    district("IND.32.6"),
    district("IND.32.9"),
)
VENGI_TG = union(district("IND.32.4"), district("IND.32.7"), district("IND.32.10"))
VENGI_AP = union(district("IND.2.4"), district("IND.2.5"), district("IND.2.12"))
VENGI = union(VENGI_TG, VENGI_AP)
AP_KANCI = union(district("IND.2.2"), district("IND.2.7"))
KUNTALA = union(
    district("IND.16.1"),
    district("IND.16.5"),
    district("IND.16.15"),
    district("IND.16.21"),
    district("IND.16.24"),
    district("IND.16.6"),
    district("IND.16.7"),
    district("IND.16.13"),
    district("IND.16.16"),
    district("IND.16.30"),
)
CAUVERIC = union(
    district("IND.16.17"),
    district("IND.16.27"),
    district("IND.16.2"),
    district("IND.16.3"),
    district("IND.16.22"),
    district("IND.16.23"),
    district("IND.16.25"),
    district("IND.16.9"),
    district("IND.16.20"),
    district("IND.16.8"),
)
TULU = union(district("IND.16.28"), district("IND.16.12"))
KADAMBA = union(
    district("IND.16.29"),
    district("IND.16.4"),
    district("IND.16.14"),
    district("IND.16.18"),
    province("Goa"),
)
COORG = district("IND.16.19")
AP_BAYALU = minus(province("IND.2"), union(AP_KANCI, VENGI, KALINGA))
KA_BAYALU = minus(province("IND.16"), union(KUNTALA, KADAMBA, CAUVERIC, TULU, COORG))
BAYALU = union(AP_BAYALU, KA_BAYALU)
VENGI_COASTAL = union(
    district("IND.2.4"), district("IND.2.5"), district("IND.2.12"), district("IND.2.3")
)
KADAMBA_COASTAL = union(province("IND.10"), district("IND.16.29"))
DECCAN = minus(
    union(
        PULINDA,
        VIDARBHA,
        RSIKA,
        MULAKA,
        ASMAKA,
        GREATER_PUNE,
        KUNTALA,
        KADAMBA,
        MAHISAKA,
        VENGI,
        BAYALU,
        CAUVERIC,
    ),
    union(VENGI_COASTAL, district("IND.2.8"), KADAMBA_COASTAL),
)

# tamilakam
## conquer the pondicherries
KANNUR_PONDI = union(district("IND.17.4"), district("IND.27.2"))  # to kerala
VILUPPURAM_PONDI = union(district("IND.31.31"), district("IND.27.3"))  # to kanci
NAGAPPATTINAM_PONDI = union(district("IND.31.13"), district("IND.27.1"))  # to cola
KERALA = union(province("Kerala"), KANNUR_PONDI)
MALABAR = union(KERALA, TULU)
TN_KANCI = union(
    district("IND.31.4"),
    district("IND.31.29"),
    district("IND.31.30"),
    VILUPPURAM_PONDI,
    district("IND.31.2"),
    district("IND.31.8"),
    district("IND.31.23"),
)
KANCI = union(AP_KANCI, TN_KANCI)
PANDYA_PROPER = union(
    district("IND.31.12"),
    district("IND.31.19"),
    district("IND.31.22"),
    district("IND.31.17"),
    district("IND.31.25"),
    district("IND.31.27"),
    district("IND.31.32"),
)
PANDYA = union(
    PANDYA_PROPER, district("IND.31.9")
)  # adding Kanyakumari, which is strictly Ay land
COLA = union(
    district("IND.31.16"),
    district("IND.31.26"),
    district("IND.31.15"),
    district("IND.31.1"),
    district("IND.31.20"),
    district("IND.31.24"),
    NAGAPPATTINAM_PONDI,
)
KONGU = minus(province("TamilNadu"), union(COLA, PANDYA, KANCI))
AY_PROPER = union(
    district("IND.17.12"), district("IND.31.9")
)  # Trivandrum + Kanyakumari
AY = union(
    AY_PROPER, district("IND.17.6"), district("IND.17.11")
)  # south kerala, later venad
EZHIMALA_PROPER = union(
    district("Kasaragod"), KANNUR_PONDI
)  # north kerala, later kolattunadu
EZHIMALA = union(EZHIMALA_PROPER, COORG)  # Poozhinadu and Karkanadu
CERA = minus(
    KERALA, union(AY, EZHIMALA)
)  # central kerala, later calicut (the zamorin one) and kochi
SIMHALA = country("LKA")
TAMIL_PROPER = union(KANCI, COLA, PANDYA, KERALA, KONGU)
TAMIL = union(TAMIL_PROPER, TULU, COORG)

# western silk road
KAMBOJA = union(
    province("Nuristan"),
    province("Kunar"),
    province("Nangarhar"),
    province("Paktya"),
    province("Khost"),
    province("Logar"),
    province("Wardak"),
    province("Parwan"),
    province("AFG.20"),
    province("Kabul"),
    province("Kapisa"),
    province("Panjshir"),
    province("Bamyan"),
)
KANDAHAR = union(province("Kandahar"), province("Hilmand"))  # Arachosia
ZARANJ = union(province("AFG.7"), province("AFG.23"))  # Drangiana
HERAT = province("Hirat")  # Aria
AFG_MARGIANA = union(province("AFG.2"), province("AFG.8"))
AFG_MERU = province("AFG.1")  # Badakhshan
AFG_BACTRIA = union(
    province("AFG.31"),
    province("AFG.19"),
    province("AFG.3"),
    province("AFG.4"),
    province("AFG.29"),
    province("AFG.13"),
    province("AFG.30"),
)
AFG_MISC = minus(
    country("AFG"),
    union(KAMBOJA, KANDAHAR, ZARANJ, HERAT, AFG_MARGIANA, AFG_BACTRIA, AFG_MERU),
)
KAMBOJA_EXT = union(KAMBOJA, AFG_MISC)
BALOCH = union(province("Balochistan"), province("IRN.26"))  # gedrosia
TJK_BACTRIA = union(
    province("TJK.3"), province("TJK.1"), district("TJK.5.7")  # Khatlon province
)  # Dushanbe and the bit South of it
TJK_SOGDIA_PROPER = province("TJK.4")
TJK_MERU = union(
    province("TJK.2"), minus(province("TJK.5"), TJK_BACTRIA)  # Badakhshan
)  # Districts under Dushanbe Dominatrix (talk to Vatsyayana for tips)
UZB_BACTRIA = province("UZB.12")
UZB_SOGDIA_PROPER = union(
    province("UZB.6"),  # Termez
    province("UZB.10"),  # Samarqand
    province("UZB.2"),  # Bukhara
    province("UZB.9"),  # Nurota, Kermine
    province("UZB.4"),  # Dizak
    province("UZB.11"),  # Syrdaryo
    province("UZB.13"),  # Tashkent
    province("UZB.14"),
)  # Tashkentic ppl
UZB_KHWAREZM = union(province("UZB.5"), province("UZB.7"))
UZB_FERGHANA = minus(
    country("Uzbekistan"), union(UZB_BACTRIA, UZB_SOGDIA_PROPER, UZB_KHWAREZM)
)
TKM_KHWAREZM = union(province("TKM.3"), province("TKM.6"))
TKM_MARGIANA = minus(country("Turkmenistan"), TKM_KHWAREZM)
MARGIANA = union(TKM_MARGIANA, AFG_MARGIANA)
BACTRIA = union(AFG_BACTRIA, TJK_BACTRIA, UZB_BACTRIA)
MERU = union(AFG_MERU, TJK_MERU)
SOGDIA_PROPER = union(UZB_SOGDIA_PROPER, TJK_SOGDIA_PROPER)
FERGHANA = UZB_FERGHANA
SOGDIA = union(SOGDIA_PROPER, FERGHANA)
KHWAREZM = union(UZB_KHWAREZM, TKM_KHWAREZM)

# eastern silk road oasis states
# kashgar, khotan, rouran, kucha, agni, turfan
KASHGAR = district("CHN.28.9")
KHOTAN = district("CHN.28.10")
KUCHA = union(
    taluk("CHN.28.1.5"), taluk("CHN.28.1.3"), taluk("CHN.28.1.7"), taluk("CHN.28.1.6")
)
AKSU = minus(district("CHN.28.1"), KUCHA)
ROURAN = taluk("CHN.28.3.7")
AGNI = taluk("CHN.28.3.8")
QIEMO = taluk("CHN.28.3.6")
KORLA = taluk("CHN.28.3.4")
TURFAN = district("CHN.28.14")
TARIM = union(
    district("CHN.28.1"),
    district("CHN.28.3"),
    district("CHN.28.9"),
    district("CHN.28.10"),
    district("CHN.28.11"),
)
DZUNGARIA = minus(province("CHN.28"), TARIM)
MONGOLIA = union(country("Mongolia"), province("CHN.19"))

# big regions
SUBCONTINENT = union(
    country("India"),
    country("Pakistan"),
    country("Afghanistan"),
    country("Bangladesh"),
    country("SriLanka"),
    country("Nepal"),
    country("Bhutan"),
    CHINESE_CLAIMS,
)
CENTRAL_ASIA = union(
    country("Afghanistan"),
    province("Balochistan"),
    province("IRN.26"),
    country("Tajikistan"),
    country("Uzbekistan"),
    country("Turkmenistan"),
)
SUBCONTINENT_PROPER = minus(SUBCONTINENT, union(CENTRAL_ASIA, INNER_KAMBOJA, HIMALAYAN))
CENTRAL_ASIA_GREATER = union(CENTRAL_ASIA, INNER_KAMBOJA)
SEA_MARITIME = union(
    SUMATRA,
    JAVA,
    BORNEO,
    SULAWESI,
    LESSER_SUNDA,
    MALUKU,
    PAPUA_IDN,
    MALAY_PENINSULA,
    KEPULAUAN,
    BANGKA,
    ANDAMAN_NICOBAR,
)
SEA_MAINLAND = union(
    SIAM, BURMA, LAOS, KHMER, CHAM, SIAM_BURMA_INTERM, KAREN, TIBET_BURMA_INTERM
)
SEA = union(SEA_MARITIME, SEA_MAINLAND)
INDOSPHERE = union(SUBCONTINENT, CENTRAL_ASIA, TARIM, TIBET, SEA, HIMALAYAN)
JAMBUDVIPA = minus(SUBCONTINENT_PROPER, SIMHALA)
NORTH_INDIA = minus(
    union(GANGETIC, BRAHMAVARTA, BENGAL, AUDICYA, RJ, MP, GUJARAT, UP_KALAKAVANA),
    PULINDA,
)
ARYAVARTA = union(UP, BRAHMAVARTA)
GY_DOAB = union(
    KURU_PROPER,
    PANCALA_S,
    VATSA,
    district("IND.34.7"),
    district("IND.34.42"),
    district("IND.34.43"),
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

# test_feature = {
#   "type": "Feature",
#   "properties": {
#       "GID_3": "PAK.7.7.1_1",
#       "GID_0": "PAK",
#       "COUNTRY": "Pakistan",
#       "GID_1": "PAK.7_1",
#       "NAME_1": "Punjab",
#       "NL_NAME_1": "NA",
#       "GID_2": "PAK.7.7_1",
#       "NAME_2": "Rawalpindi", # TODO: annex this region
#       "NL_NAME_2": "NA",
#       "NAME_3": "Attok",
#       "VARNAME_3": "Attock",
#       "NL_NAME_3": "NA",
#       "TYPE_3": "District",
#       "ENGTYPE_3": "District",
#       "CC_3": "NA",
#       "HASC_3": "NA"},
#   "geometry" : ""}

# print(union(MAGADHA, MONGOLIA)(test_feature))
