"""
Xatra Territory Library Module

This module provides predefined composite territories that can be used
as building blocks for historical maps. These territories are created
by combining base GADM administrative boundaries using set algebra.

The library includes commonly used geographical regions that are useful
for historical mapping applications.
"""

from __future__ import annotations

from .loaders import gadm

"""custom, recurring, world regions"""

Z01 = gadm("Z01.14")
Z02 = gadm("Z02.28")
Z03 = gadm("Z03.28") | gadm("Z03.29")
Z04 = gadm("Z04.13")
Z05 = gadm("Z05.35")
Z06 = gadm("Z06.1") | gadm("Z06.6")
Z07 = gadm("Z07.3")
Z08 = gadm("Z08.29")
Z09 = gadm("Z09.35") | gadm("Z09.13")

# sorting the himalayas
CHINESE_CLAIMS_UK = Z05 | gadm("Z09.35")
CHINESE_CLAIMS_HP = gadm("Z09.13") | Z04
CHINESE_CLAIMS_LADAKH = Z03 | Z08  # Aksai Chin
CHINESE_CLAIMS_GILGIT = Z02
CHINESE_CLAIMS_AP = Z07
CHINESE_CLAIMS = (
    CHINESE_CLAIMS_UK
    | CHINESE_CLAIMS_HP
    | CHINESE_CLAIMS_AP
    | CHINESE_CLAIMS_LADAKH
    | CHINESE_CLAIMS_GILGIT
)
TERAI_HP = (
    gadm("IND.13.4")
    | gadm("IND.13.3")
    | gadm("IND.13.12")
    | gadm("IND.13.1")
    | gadm("IND.13.11")
    | gadm("IND.13.10")
)
TERAI_UK_W = gadm("IND.35.5")
TERAI_UK_ROORKEE = gadm("IND.35.7")
TERAI_UK_E = gadm("IND.35.8") | gadm("IND.35.12")
TERAI_UK = TERAI_UK_W | TERAI_UK_ROORKEE | TERAI_UK_E
TERAI_NPL_FW = gadm("NPL.3.1.4") | gadm("NPL.3.2.5")
TERAI_NPL_MW = gadm("NPL.4.1.1") | gadm("NPL.4.1.2")
TERAI_NPL_W = gadm("NPL.5.3.3") | gadm("NPL.5.3.6") | gadm("NPL.5.3.4")  # sakya
TERAI_NPL_C = (
    gadm("NPL.1.3.4")
    | gadm("NPL.1.3.1")
    | gadm("NPL.1.3.5")
    | gadm("NPL.1.2.5")
    | gadm("NPL.1.2.3")
    | gadm("NPL.1.2.1")
    | gadm("NPL.1.3.2")
)
TERAI_NPL_E = (
    gadm("NPL.2.3.4")
    | gadm("NPL.2.3.3")
    | gadm("NPL.2.1.3")
    | gadm("NPL.2.1.5")
    | gadm("NPL.2.2.2")
)
TERAI_NPL = TERAI_NPL_FW | TERAI_NPL_MW | TERAI_NPL_W | TERAI_NPL_C | TERAI_NPL_E
TERAI_BENGAL = (
    gadm("IND.36.6")
    | gadm("IND.36.9")
    | gadm("IND.36.1")
    | gadm("IND.36.10")
)
# BENGAL_HIM = Matcher.__false__() # keep this line in for now
TERAI = TERAI_HP | TERAI_UK | TERAI_NPL | TERAI_BENGAL
HP_HIM = (gadm("IND.13") | CHINESE_CLAIMS_HP) - TERAI_HP
UK_HIM = (gadm("IND.35") | CHINESE_CLAIMS_UK) - TERAI_UK
NPL_HIM = gadm("NPL") - TERAI_NPL
LADAKH = (
    gadm("Z01.14.13") | gadm("Z01.14.8") | Z03 | Z08
)  # Aksai Chin main part | Aksai Chin Southern bit
KASHMIR_MISC = (
    gadm("Z01.14.10")
    | gadm("Z01.14.5")
    | gadm("Z01.14.17")
    | gadm("Z01.14.18")
    | gadm("Z01.14.22")
    | gadm("Z01.14.7")
    | gadm("Z01.14.19")
    | gadm("Z01.14.9")
)
KASHMIR_PROPER = gadm("Z01.14") - (KASHMIR_MISC | LADAKH)
KASHMIR_TBC = gadm("Z06.1")  # POK
# KASHMIR = KASHMIR_PROPER | KASHMIR_MISC | KASHMIR_TBC

# alternate division for Kashmir:
JAMMU_IND = (
    KASHMIR_MISC | gadm("Z01.14.16") | gadm("Z01.14.14")
)  # + poonch and rajouri
KASHMIR_IND = gadm("Z01.14") - (JAMMU_IND | LADAKH)
KASHMIR_POK = gadm("Z06.1.1.6") | gadm("Z06.1.1.5")
JAMMU_POK = KASHMIR_TBC - KASHMIR_POK
JAMMU = JAMMU_IND | JAMMU_POK
KASHMIR = KASHMIR_IND | KASHMIR_POK

DARADA = gadm("Z06.6")
KHYBER_HIM = gadm("PAK.5.6") | gadm("PAK.5.4")
ASSAM_HIM = (
    gadm("IND.4.4")
    | gadm("IND.4.10")
    | gadm("IND.4.13")
    | gadm("IND.4.18")
    | gadm("IND.4.17")
    | gadm("IND.4.22")
)
LAUHITYA = gadm("IND.4") - ASSAM_HIM
NEI_HIM = (
    gadm("IND.3")
    | gadm("IND.22")
    | gadm("IND.24")
    | gadm("IND.21")
    | gadm("IND.23")
    | gadm("IND.33")
    | ASSAM_HIM
)
INNER_KAMBOJA = gadm("PAK.3")  # Federally Administered Tribal Areas
HIMALAYAN = (
    HP_HIM
    | UK_HIM
    | NPL_HIM
    | gadm("BTN")
    # | BENGAL_HIM # keep this line in for now
    | NEI_HIM
    | gadm("IND.30")
    | LADAKH
    | DARADA
    | KHYBER_HIM
    | CHINESE_CLAIMS
)

# tibeto-burman region

TIBET_CN_TIB = gadm("CHN.29")  # chinese occupied tibet
TIBET_CN_QIN = gadm("CHN.21")  # chinese occupied tibet
TIBET_CN_SIC = gadm("CHN.26.5") | gadm("CHN.26.16")  # chinese occupied tibet
TIBET_CN = TIBET_CN_TIB | TIBET_CN_QIN | TIBET_CN_SIC
TIBET_BHU = gadm("BTN")  # bhutanese occupied tibet
TIBET_NEP = (
    gadm("NPL.4.2.1")
    | gadm("NPL.4.2.2")
    | gadm("NPL.4.2.5")
    | gadm("NPL.5.1")
    | gadm("NPL.5.2")
    | gadm("NPL.1.1")
    | gadm("NPL.1.2.2")
    | gadm("NPL.1.2.4")
    | gadm("NPL.1.2.6")
    | gadm("NPL.2.3.5")
    | gadm("NPL.2.3.1")
    | gadm("NPL.2.3.2")
    | gadm("NPL.2.1.1")
    | gadm("NPL.2.1.4")
    | gadm("NPL.2.1.2")
    | gadm("NPL.2.1.6")
    | gadm("NPL.2.2.4")
    | gadm("NPL.2.2.3")
    | gadm("NPL.2.2.1")
)  # nepali-occupied tibet
TIBET_AP = CHINESE_CLAIMS_AP  # tibet under risk of chinese occupation
TIBET_LAD = LADAKH  # tibet in its rightful home
TIBET_SIK = gadm("IND.30")  # tibet in its rightful home
TIBET = TIBET_CN | TIBET_BHU | TIBET_NEP | TIBET_LAD | TIBET_AP | TIBET_SIK

TIBET_BURMA_INTERM = (
    NEI_HIM | gadm("MMR.3")
) - TIBET  # intermediary region from Tibet to Burma
YUNNAN_BURMA_INTERM = gadm("MMR.4")  # kachin state
KAREN = gadm("MMR.5") | gadm("MMR.6")  # karenic parts of myanmar
SIAM_BURMA_INTERM = gadm("MMR.13")  # shan state

BURMA_UPPER = (
    gadm("MMR.12") | gadm("MMR.7") | gadm("MMR.8") | gadm("MMR.10")
)
BURMA_LOWER_RIVER = gadm("MMR.2") | gadm("MMR.1") | gadm("MMR.15")
BURMA_LOWER_RAKHINE = gadm("MMR.11")
BURMA_LOWER_THAICOAST = gadm("MMR.9") | gadm("MMR.14")
BURMA_LOWER = BURMA_LOWER_RIVER | BURMA_LOWER_RAKHINE | BURMA_LOWER_THAICOAST
BURMA = BURMA_UPPER | BURMA_LOWER

# southeast asia
SIAM_THA = gadm("THA")
SIAM = SIAM_THA
LAOS = gadm("LAO")
KHMER = gadm("KHM")
CHAM = (
    gadm("VNM.41")
    | gadm("VNM.29")
    | gadm("VNM.46")
    | gadm("VNM.50")
    | gadm("VNM.54")
    | gadm("VNM.19")
    | gadm("VNM.47")
    | gadm("VNM.48")
    | gadm("VNM.34")
    | gadm("VNM.8")
    | gadm("VNM.21")
    | gadm("VNM.45")
    | gadm("VNM.32")
    | gadm("VNM.15")
    | gadm("VNM.43")
    | gadm("VNM.37")
    | gadm("VNM.16")
    | gadm("VNM.11")
    | gadm("VNM.7")
    | gadm("VNM.17")
    | gadm("VNM.10")
    | gadm("VNM.25")
    | gadm("VNM.9")
    | gadm("VNM.53")
    | gadm("VNM.39")
    | gadm("VNM.58")
    | gadm("VNM.6")
    | gadm("VNM.59")
    | gadm("VNM.61")
    | gadm("VNM.18")
    | gadm("VNM.51")
    | gadm("VNM.24")
    | gadm("VNM.2")
    | gadm("VNM.33")
    | gadm("VNM.12")
    | gadm("VNM.1")
    | gadm("VNM.13")
    | gadm("VNM.33")
)
NORTH_VIETNAM = gadm("VNM") - CHAM
BORNEO_MYS = (
    gadm("MYS.13") | gadm("MYS.14") | gadm("MYS.5")
)  # sabah serawak
BORNEO_BRU = gadm("BRN")
BORNEO_MYS_GREATER = BORNEO_MYS | BORNEO_BRU
BORNEO_IDN = (
    gadm("IDN.35")
    | gadm("IDN.34")
    | gadm("IDN.12")
    | gadm("IDN.13")
    | gadm("IDN.14")
)  # kalimantan
BORNEO = BORNEO_MYS_GREATER | BORNEO_IDN

MALAY_PENINSULA_MYS = gadm("MYS") - BORNEO_MYS
MALAY_PENINSULA_SG = gadm("SGP")
MALAY_PENINSULA = MALAY_PENINSULA_MYS | MALAY_PENINSULA_SG
JAVA = (
    (gadm("IDN.9") | gadm("IDN.10") | gadm("IDN.11"))
    | gadm("IDN.4")
    | gadm("IDN.7")
    | gadm("IDN.33")
)
LESSER_SUNDA_IDN = gadm("IDN.2") | (gadm("IDN.20") | gadm("IDN.21"))
LESSER_SUNDA_TLS = gadm("TLS")
LESSER_SUNDA = LESSER_SUNDA_IDN | LESSER_SUNDA_TLS

MALUKU_SOUTH = gadm("IDN.19")
MALUKU_NORTH = gadm("IDN.18")
MALUKU = MALUKU_SOUTH | MALUKU_NORTH

SULAWESI = (gadm("IDN.25") | gadm("IDN.26") | gadm("IDN.27") | gadm("IDN.28") | gadm("IDN.29")) | gadm("IDN.6") | gadm("IDN.29")
KEPULAUAN = gadm("IDN.16")  # bits of indonesia between indonesia and malaysia
BANGKA = gadm("IDN.3")  # bits of indonesia between borneo and sumatra
SUMATRA = (
    (gadm("IDN.30") | gadm("IDN.31") | gadm("IDN.32"))
    | gadm("IDN.1")
    | gadm("IDN.24")
    | gadm("IDN.8")
    | gadm("IDN.17")
    | gadm("IDN.5")
)
ANDAMAN_NICOBAR = gadm("IND.1")

PAPUA_IDN = gadm("IDN.22") | gadm("IDN.23")
PHILIPPINES = gadm("PHL")

# gangetic
UP_CEDI = (
    gadm("IND.34.38")
    | gadm("IND.34.34")
    | gadm("ARG.22.5")
    | gadm("IND.34.21")
    | gadm("IND.34.40")
    | gadm("IND.34.51")
    | gadm("IND.34.48")
)
UP_KALAKAVANA = gadm("IND.34.56") | gadm("IND.34.72")
SURASENA = gadm("IND.34.53") | gadm("IND.34.1")
KURU_PROPER = (
    gadm("IND.34.63")
    | gadm("IND.34.58")
    | gadm("IND.34.68")
    | gadm("IND.34.9")
    | gadm("IND.34.55")
    | gadm("IND.34.30")
    | gadm("IND.34.35")
    | gadm("IND.34.19")
    | gadm("IND.34.29")
    | gadm("IND.35.7")
)
KURU_KSETRA = (
    gadm("IND.12.21")
    | gadm("IND.12.11")
    | gadm("IND.12.9")
    | gadm("IND.12.8")
    | gadm("IND.12.10")
    | gadm("IND.12.16")
)
KURU_JANGALA = (
    gadm("IND.25")
    | gadm("IND.12.20")
    | gadm("IND.12.18")
    | gadm("IND.12.7")
    | gadm("IND.12.5")
    | gadm("IND.12.3")
    | gadm("IND.12.14")
    | gadm("IND.12.13")
)
KURU_KSETRA_GREATER_HARYANA = KURU_KSETRA | gadm("IND.12.15") | gadm("IND.12.1")
JANGALA_HARYANA = (
    KURU_JANGALA
    | gadm("IND.12.17")
    | gadm("IND.12.12")
    | gadm("IND.12.2")
    | gadm("IND.12.6")
    | gadm("IND.12.4")
    | gadm("IND.12.19")
)
KURU = KURU_PROPER | KURU_JANGALA | KURU_KSETRA
PANCALA_S = (
    gadm("IND.34.2")
    | gadm("IND.34.37")
    | gadm("IND.34.23")
    | gadm("IND.34.44")
    | gadm("IND.34.28")
    | gadm("IND.34.52")
    | gadm("IND.34.24")
    | gadm("IND.34.26")
    | gadm("IND.34.41")
)
PANCALA_N = (
    gadm("IND.34.17")
    | gadm("IND.34.6")
    | gadm("IND.34.64")
    | gadm("IND.34.57")
    | gadm("IND.34.62")
    | gadm("IND.34.15")
    | gadm("IND.34.18")
    | gadm("IND.34.64")
)
PANCALA = PANCALA_N | PANCALA_S
VATSA = gadm("IND.34.27") | gadm("IND.34.45") | gadm("IND.34.3")
KASI = (
    gadm("IND.34.39")
    | gadm("IND.34.66")
    | gadm("IND.34.75")
    | gadm("IND.34.20")
    | gadm("IND.5.14")
    | gadm("IND.5.29")
    | gadm("IND.5.8")
    | gadm("IND.5.7")
)
KOSALA = (
    gadm("IND.34.10")
    | gadm("IND.34.69")
    | gadm("IND.34.32")
    | gadm("IND.34.12")
    | gadm("IND.34.70")
    | gadm("IND.34.16")
    | gadm("IND.34.65")
    | gadm("IND.34.33")
    | gadm("IND.34.25")
    | gadm("IND.34.4")
    | gadm("IND.34.4")
    | gadm("IND.34.8")
    | gadm("IND.34.54")
    | gadm("IND.34.11")
    | gadm("IND.34.73")
    | gadm("IND.34.31")
)
SAKYA = TERAI_NPL_W  # | gadm("NPL.1.3.2")
JANAKPUR = TERAI_NPL_C  # - gadm("NPL.1.3.2")
MALLA = (
    gadm("IND.34.50")
    | gadm("IND.34.46")
    | gadm("IND.34.22")
    | gadm("IND.5.11")
    | gadm("IND.5.36")
    | gadm("IND.5.32")
)
VIDEHA_IN = (
    gadm("IND.5.25")
    | gadm("IND.5.27")
    | gadm("IND.5.34")
    | gadm("IND.5.35")
    | gadm("IND.5.20")
)
VIDEHA = VIDEHA_IN | JANAKPUR
LICCHAVI = (
    gadm("IND.5.22")
    | gadm("IND.5.38")
    | gadm("IND.5.9")
    | gadm("IND.5.31")
    | gadm("IND.5.5")
    | gadm("IND.5.16")
)
MAGADHA = (
    gadm("IND.5.26")
    | gadm("IND.5.13")
    | gadm("IND.5.3")
    | gadm("IND.5.2")
    | gadm("IND.5.10")
    | gadm("IND.5.23")
    | gadm("IND.5.33")
    | gadm("IND.5.24")
    | gadm("IND.5.18")
    | gadm("IND.5.12")
    | gadm("IND.5.21")
)
KOSALA_GREATER = KOSALA | VIDEHA | LICCHAVI | SAKYA | MALLA | KASI | VATSA
BIHAR_ANGA = gadm("IND.5.4") | gadm("IND.5.6")
BIHAR_NORTHEAST = gadm("IND.5") - (
    VIDEHA | LICCHAVI | MAGADHA | BIHAR_ANGA | KASI | MALLA
)
UP_NAIMISA = gadm("IND.34") - (
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
    gadm("IND.19.15")
    | gadm("IND.19.48")
    | gadm("IND.19.35")
    | gadm("IND.19.28")
    | gadm("IND.19.31")
    | gadm("IND.19.25")
    | gadm("IND.19.2")
    | gadm("IND.19.16")
    | gadm("IND.19.23")
)
AKARA = (
    gadm("IND.19.1")
    | gadm("IND.19.42")
    | gadm("IND.19.39")
    | gadm("IND.19.34")
    | gadm("IND.19.9")
    | gadm("IND.19.33")
    | gadm("IND.19.50")
    | gadm("IND.19.19")
    | gadm("IND.19.4")
)
DASARNA = (
    gadm("IND.19.44")
    | gadm("IND.19.43")
    | gadm("IND.19.20")
    | gadm("IND.19.14")
    | gadm("IND.19.8")
    | gadm("IND.19.29")
)
PULINDA_W = (
    gadm("IND.19.21")
    | gadm("IND.19.18")
    | gadm("IND.19.51")
    | gadm("IND.19.10")
    | gadm("IND.19.6")
)
PULINDA_E = (
    gadm("IND.19.22")
    | gadm("IND.19.7")
    | gadm("IND.19.12")
    | gadm("IND.19.30")
    | gadm("IND.19.40")
    | gadm("IND.19.27")
    | gadm("IND.19.5")
    | gadm("IND.19.17")
)
PULINDA = PULINDA_W | PULINDA_E
MP_CEDI = gadm("IND.19") - (AVANTI | AKARA | DASARNA | PULINDA_W | PULINDA_E)
CEDI = MP_CEDI | UP_CEDI

BRAHMAVARTA = gadm("IND.12") | gadm("IND.25")

MATSYA = (
    gadm("IND.29.6")
    | gadm("IND.29.2")
    | gadm("IND.29.17")
    | gadm("IND.29.12")
    | gadm("IND.29.23")
    | gadm("IND.29.13")
    | gadm("IND.29.29")
)
KUKURA = (
    gadm("IND.29.32")
    | gadm("IND.29.9")
    | gadm("IND.29.1")
    | gadm("IND.29.7")
    | gadm("IND.29.28")
    | gadm("IND.29.33")
    | gadm("IND.29.10")
    | gadm("IND.29.14")
    | gadm("IND.29.27")
    | gadm("IND.29.3")
)
KUKURA_GREATER = MATSYA | KUKURA
HADOTI = gadm("IND.29.24") | gadm("IND.29.4") | gadm("IND.29.20")
RJ_MARU = gadm("IND.29") - (MATSYA | KUKURA | HADOTI)
MP = AVANTI | AKARA | DASARNA | PULINDA | CEDI | HADOTI
RJ = gadm("IND.29")

PUNJAB = (
    gadm("IND.28")
    | gadm("PAK.7")
    | gadm("IND.6.1")
    | gadm("PAK.4.1")
    | gadm("PAK.5")
) - HIMALAYAN
GANDHARA_W = gadm("PAK.5") - HIMALAYAN
PSEUDOSATTAGYDIA_S = gadm("PAK.7.2.1") | gadm("PAK.7.2.4")
PSEUDOSATTAGYDIA_N = gadm("PAK.5.2") | gadm("PAK.5.1") | gadm("PAK.5.3.2")
PSEUDOSATTAGYDIA = PSEUDOSATTAGYDIA_N | PSEUDOSATTAGYDIA_S
DOAB_IJ_N = (
    gadm("PAK.4.1") | gadm("PAK.7.7") | gadm("PAK.7.8")
) - gadm("PAK.7.8.4")
DOAB_IJ_S = gadm("PAK.7.2.2") | gadm("PAK.7.2.3")
GANDHARA = GANDHARA_W | DOAB_IJ_N
DOAB_IJ = DOAB_IJ_N | DOAB_IJ_S
DOAB_JC = gadm("PAK.7.4.4") | gadm("PAK.7.4.1") | gadm("PAK.7.8.4")
DOAB_CR = (
    gadm("PAK.7.4.2")
    | gadm("PAK.7.4.3")
    | gadm("PAK.7.4.5")
    | gadm("PAK.7.4.6")
    | gadm("PAK.7.4.7")
    | gadm("PAK.7.4.8")
    | gadm("PAK.7.5.3")
    | gadm("PAK.7.5.6")
    | gadm("PAK.7.3.1")
    | gadm("PAK.7.3.2")
    | gadm("PAK.7.3.3")
)
DOAB_RS_N = (
    gadm("IND.28.16")
    | gadm("IND.28.8")
    | gadm("IND.28.1")
    | gadm("IND.28.22")
)
DOAB_RS_C = (
    gadm("PAK.7.5.1") | gadm("PAK.7.5.2") | gadm("PAK.7.5.4") | gadm("PAK.7.5.5")
)
DOAB_RS_S = gadm("PAK.7.6")
DOAB_RS = DOAB_RS_N | DOAB_RS_C | DOAB_RS_S
BAHAWALPUR = gadm("PAK.7.1")
# TRIGARTA_PROPER = (gadm("IND.28") | gadm("IND.6.1")) - DOAB_RS_N
# TRIGARTA = gadm("IND.28") | gadm("IND.6.1") | DOAB_RS_C
TRIGARTA_PJ = (
    gadm("IND.28.9")
    | gadm("IND.28.10")
    | gadm("IND.28.11")
    | gadm("IND.28.21")
)
TRIGARTA_HP = (
    gadm("IND.13.4")
    | gadm("IND.13.12")
    | gadm("IND.13.1")
    | gadm("IND.13.3")
)
TRIGARTA = TRIGARTA_PJ | TRIGARTA_HP
KUNINDA = (TERAI_UK_W | TERAI_HP) - TRIGARTA_HP
PUADH = (
    gadm("IND.28.18")
    | gadm("IND.28.5")
    | gadm("IND.28.19")
    | gadm("IND.28.17")
    | gadm("IND.6.1")
)
JANGALA_PJ = gadm("IND.28") - (TRIGARTA_PJ | PUADH)
JANGALA_RJ = (
    gadm("IND.29.8")
    | gadm("IND.29.11")
    | gadm("IND.29.16")
    | gadm("IND.29.15")
)
KURU_KSETRA_GREATER = KURU_KSETRA_GREATER_HARYANA | PUADH
JANGALA = JANGALA_HARYANA | JANGALA_PJ | JANGALA_RJ

SINDH_N = gadm("PAK.8.3.1") | gadm("PAK.8.3.2") | gadm("PAK.8.3.4")
SINDH_SW = (
    gadm("PAK.8.2.5")
    | gadm("PAK.8.5.1")
    | gadm("PAK.8.2.4")
    | gadm("PAK.8.2.1")
    | gadm("PAK.8.2.2")
    | gadm("PAK.8.2.3")
)
SINDH_SE = (
    gadm("PAK.8.1.8") | gadm("PAK.8.1.1") | gadm("PAK.8.1.6") | gadm("PAK.8.4.2")
)
SINDH_W_PROPER = gadm("PAK.8.3") | gadm("PAK.8.1.2") | gadm("PAK.8.1.4")
SINDH_W = SINDH_W_PROPER | SINDH_SW
SINDH_E_PROPER = (
    gadm("PAK.8.1.3")
    | gadm("PAK.8.1.7")
    | gadm("PAK.8.4.1")
    | gadm("PAK.8.4.4")
    | gadm("PAK.8.4.3")
    | gadm("PAK.8.1.5")
    | gadm("PAK.8.6.1")
    | gadm("PAK.8.6.2")
    | gadm("PAK.8.6.3")
    | gadm("PAK.8.6.4")
    | gadm("PAK.8.6.5")
)
SINDH_E = SINDH_E_PROPER | SINDH_SE
SINDH_S = SINDH_SE | SINDH_SW
SINDH = SINDH_N | SINDH_W_PROPER | SINDH_E_PROPER | SINDH_S
AUDICYA = PUNJAB | SINDH

KUTCH = gadm("IND.11.16")
ANARTA = (
    gadm("IND.11.5")
    | gadm("IND.11.18")
    | gadm("IND.11.24")
    | gadm("IND.11.27")
    | gadm("IND.11.4")
    | gadm("IND.11.12")
)
SURASTRA = (
    gadm("IND.11.1")
    | gadm("IND.11.29")
    | gadm("IND.11.20")
    | gadm("IND.11.14")
    | gadm("IND.11.11")
    | gadm("IND.11.25")
    | gadm("IND.11.26")
    | gadm("IND.11.15")
    | gadm("IND.11.13")
    | gadm("IND.11.2")
    | gadm("IND.11.8")
    | gadm("IND.11.7")
)
LATA = (
    gadm("IND.11") | gadm("IND.8") | gadm("IND.9")
) - (KUTCH | ANARTA | SURASTRA)
GUJARAT = KUTCH | ANARTA | SURASTRA | LATA

JHARKHAND_ANGA = (
    gadm("IND.15.22")
    | gadm("IND.15.8")
    | gadm("IND.15.16")
    | gadm("IND.15.5")
    | gadm("IND.15.3")
    | gadm("IND.15.11")
)
JHARKHAND_CHHOTA_NAGPUR = gadm("IND.15") - JHARKHAND_ANGA
WB_CHHOTA_NAGPUR = gadm("IND.36.18")
CHHOTA_NAGPUR = JHARKHAND_CHHOTA_NAGPUR | WB_CHHOTA_NAGPUR
ANGA = BIHAR_ANGA | JHARKHAND_ANGA
PUNDRA_WB = gadm("IND.36.5") | gadm("IND.36.20")
GAUDA_EB = gadm("BGD.5.5")
GAUDA_WB = gadm("IND.36.13") | gadm("IND.36.12")
GAUDA = GAUDA_EB | GAUDA_WB
RADHA = gadm("IND.36.2") | gadm("IND.36.3") | gadm("IND.36.4")
SUHMA = (
    gadm("IND.36.16")
    | gadm("IND.36.17")
    | gadm("IND.36.7")
    | gadm("IND.36.8")
)
VANGA_WB = (
    gadm("IND.36.11")
    | gadm("IND.36.14")
    | gadm("IND.36.15")
    | gadm("IND.36.19")
)
PUNDRA_EB = gadm("BGD.5") - GAUDA_EB
VANGA_EB = (
    gadm("BGD.4")
    | gadm("BGD.1")
    | gadm("BGD.3.2")
    | gadm("BGD.3.4")
    | gadm("BGD.3.7")
    | gadm("BGD.3.14")
    | gadm("BGD.3.15")
)
SAMATATA = gadm("BGD") - (VANGA_EB | PUNDRA_EB | GAUDA_EB)
VANGA = VANGA_WB | VANGA_EB
PUNDRA = PUNDRA_WB | PUNDRA_EB
CHATTISGARH_N = (
    gadm("IND.7.19")
    | gadm("IND.7.7")
    | gadm("IND.7.12")
    | gadm("IND.7.21")
    | gadm("IND.7.16")
    | gadm("IND.7.17")
    | gadm("IND.7.25")
    | gadm("IND.7.26")
    | gadm("IND.7.13")
    | gadm("IND.7.3")
)
CHATTISGARH_S = gadm("IND.7") - CHATTISGARH_N
KALINGA_UTKALA = (
    gadm("IND.26.13")
    | gadm("IND.26.6")
    | gadm("IND.26.17")
    | gadm("IND.26.3")
)
KALINGA_PROPER = (
    gadm("IND.26.7")
    | gadm("IND.26.10")
    | gadm("IND.26.11")
    | gadm("IND.26.12")
    | gadm("IND.26.19")
    | gadm("IND.26.24")
    | gadm("IND.26.26")
)
KALINGA_TELUGU = (
    gadm("IND.2.3")
    | gadm("IND.2.9")
    | gadm("IND.2.10")
    | gadm("IND.2.11")
)
KALINGA = KALINGA_PROPER | KALINGA_TELUGU | KALINGA_UTKALA
UTKALA_PROPER = gadm("IND.26.22") | gadm("IND.26.18") | gadm("IND.26.9")
UTKALA_INNER = (
    gadm("IND.26.1")
    | gadm("IND.26.8")
    | gadm("IND.26.14")
    | gadm("IND.26.28")
    | gadm("IND.26.30")
)
UTKALA = UTKALA_PROPER | KALINGA_UTKALA
KALINGA_GREATER = KALINGA | UTKALA
ODRA = gadm("IND.26") - (KALINGA_PROPER | UTKALA)
GREAT_FOREST_PROPER = ODRA | CHATTISGARH_S
GREAT_FOREST_NORTH = CHATTISGARH_N | UTKALA_PROPER | CHHOTA_NAGPUR
GREAT_FOREST = GREAT_FOREST_NORTH | GREAT_FOREST_PROPER
GREAT_FOREST_GREATER = GREAT_FOREST | UP_KALAKAVANA
BENGAL = ANGA | BIHAR_NORTHEAST | RADHA | SUHMA | GAUDA | PUNDRA | VANGA | SAMATATA

RSIKA = (
    gadm("IND.20.13")
    | gadm("IND.20.9")
    | gadm("IND.20.21")
    | gadm("IND.20.22")
)
VIDARBHA = (
    gadm("IND.20.2")
    | gadm("IND.20.3")
    | gadm("IND.20.7")
    | gadm("IND.20.2")
    | gadm("IND.20.35")
    | gadm("IND.20.3")
    | gadm("IND.20.34")
    | gadm("IND.20.36")
    | gadm("IND.20.19")
    | gadm("IND.20.5")
    | gadm("IND.20.8")
    | gadm("IND.20.10")
    | gadm("IND.20.11")
)
NANDED_ASMAKA = (
    gadm("IND.20.20.2")
    | gadm("IND.20.20.3")
    | gadm("IND.20.20.5")
    | gadm("IND.20.20.7")
)
NANDED_MULAKA = gadm("IND.20.20") - NANDED_ASMAKA
MULAKA = (
    gadm("IND.20.4")
    | gadm("IND.20.12")
    | gadm("IND.20.14")
    | NANDED_MULAKA
    | gadm("IND.20.25")
    | gadm("IND.32.1")
)
ASMAKA = (
    gadm("IND.20.1")
    | gadm("IND.20.6")
    | gadm("IND.20.16")
    | NANDED_ASMAKA
    | gadm("IND.32.3")
    | gadm("IND.32.8")
)
APARANTA = (
    gadm("IND.20.17")
    | gadm("IND.20.18")
    | gadm("IND.20.24")
    | gadm("IND.20.27")
    | gadm("IND.20.28")
    | gadm("IND.20.33")
    | gadm("IND.20.31")
)
GREATER_PUNE = gadm("IND.20") - (RSIKA | VIDARBHA | MULAKA | ASMAKA | APARANTA)
MAHISAKA = (
    gadm("IND.32.2")
    | gadm("IND.32.5")
    | gadm("IND.32.6")
    | gadm("IND.32.9")
)
VENGI_TG = gadm("IND.32.4") | gadm("IND.32.7") | gadm("IND.32.10")
VENGI_AP = gadm("IND.2.4") | gadm("IND.2.5") | gadm("IND.2.12")
VENGI = VENGI_TG | VENGI_AP
AP_KANCI = gadm("IND.2.2") | gadm("IND.2.7")
KUNTALA = (
    gadm("IND.16.1")
    | gadm("IND.16.5")
    | gadm("IND.16.15")
    | gadm("IND.16.21")
    | gadm("IND.16.24")
    | gadm("IND.16.6")
    | gadm("IND.16.7")
    | gadm("IND.16.13")
    | gadm("IND.16.16")
    | gadm("IND.16.30")
)
CAUVERIC = (
    gadm("IND.16.17")
    | gadm("IND.16.27")
    | gadm("IND.16.2")
    | gadm("IND.16.3")
    | gadm("IND.16.22")
    | gadm("IND.16.23")
    | gadm("IND.16.25")
    | gadm("IND.16.9")
    | gadm("IND.16.20")
    | gadm("IND.16.8")
)
TULU = gadm("IND.16.28") | gadm("IND.16.12")
KADAMBA = (
    gadm("IND.16.29")
    | gadm("IND.16.4")
    | gadm("IND.16.14")
    | gadm("IND.16.18")
    | gadm("IND.10")
)
COORG = gadm("IND.16.19")
AP_BAYALU = gadm("IND.2") - (AP_KANCI | VENGI | KALINGA)
KA_BAYALU = gadm("IND.16") - (KUNTALA | KADAMBA | CAUVERIC | TULU | COORG)
BAYALU = AP_BAYALU | KA_BAYALU
VENGI_COASTAL = (
    gadm("IND.2.4")
    | gadm("IND.2.5")
    | gadm("IND.2.12")
    | gadm("IND.2.3")
)
KADAMBA_COASTAL = gadm("IND.10") | gadm("IND.16.29")
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
) - (VENGI_COASTAL | gadm("IND.2.8") | KADAMBA_COASTAL)

# tamilakam
## conquer the pondicherries
KANNUR_PONDI = gadm("IND.17.4") | gadm("IND.27.2")  # to kerala
VILUPPURAM_PONDI = gadm("IND.31.31") | gadm("IND.27.3")  # to kanci
NAGAPPATTINAM_PONDI = gadm("IND.31.13") | gadm("IND.27.1")  # to cola
KERALA = gadm("IND.17") | KANNUR_PONDI
MALABAR = KERALA | TULU
TN_KANCI = (
    gadm("IND.31.4")
    | gadm("IND.31.29")
    | gadm("IND.31.30")
    | VILUPPURAM_PONDI
    | gadm("IND.31.2")
    | gadm("IND.31.8")
    | gadm("IND.31.23")
)
KANCI = AP_KANCI | TN_KANCI
PANDYA_PROPER = (
    gadm("IND.31.12")
    | gadm("IND.31.19")
    | gadm("IND.31.22")
    | gadm("IND.31.17")
    | gadm("IND.31.25")
    | gadm("IND.31.27")
    | gadm("IND.31.32")
)
PANDYA = PANDYA_PROPER | gadm("IND.31.9")  # adding Kanyakumari, which is strictly Ay land
COLA = (
    gadm("IND.31.16")
    | gadm("IND.31.26")
    | gadm("IND.31.15")
    | gadm("IND.31.1")
    | gadm("IND.31.20")
    | gadm("IND.31.24")
    | NAGAPPATTINAM_PONDI
)
KONGU = gadm("IND.31") - (COLA | PANDYA | KANCI)
AY_PROPER = gadm("IND.17.12") | gadm("IND.31.9")  # Trivandrum + Kanyakumari
AY = (
    AY_PROPER | gadm("IND.17.6") | gadm("IND.17.11")
)  # south kerala, later venad
EZHIMALA_PROPER = (
    gadm("IND.17.5") | KANNUR_PONDI
)  # north kerala, later kolattunadu
EZHIMALA = EZHIMALA_PROPER | COORG  # Poozhinadu and Karkanadu
CERA = KERALA - (
    AY | EZHIMALA
)  # central kerala, later calicut (the zamorin one) and kochi
SIMHALA = gadm("LKA")
TAMIL_PROPER = KANCI | COLA | PANDYA | KERALA | KONGU
TAMIL = TAMIL_PROPER | TULU | COORG

# western silk road
KAMBOJA = (
    gadm("AFG.24")
    | gadm("AFG.18")
    | gadm("AFG.22")
    | gadm("AFG.26")
    | gadm("AFG.17")
    | gadm("AFG.21")
    | gadm("AFG.33")
    | gadm("AFG.28")
    | gadm("AFG.20")
    | gadm("AFG.14")
    | gadm("AFG.16")
    | gadm("AFG.27")
    | gadm("AFG.5")
)
KANDAHAR = gadm("AFG.15") | gadm("AFG.11")  # Arachosia
ZARANJ = gadm("AFG.7") | gadm("AFG.23")  # Drangiana
HERAT = gadm("AFG.12")  # Aria
AFG_MARGIANA = gadm("AFG.2") | gadm("AFG.8")
AFG_MERU = gadm("AFG.1")  # Badakhshan
AFG_BACTRIA = (
    gadm("AFG.31")
    | gadm("AFG.19")
    | gadm("AFG.3")
    | gadm("AFG.4")
    | gadm("AFG.29")
    | gadm("AFG.13")
    | gadm("AFG.30")
)
AFG_MISC = gadm("AFG") - (
    KAMBOJA | KANDAHAR | ZARANJ | HERAT | AFG_MARGIANA | AFG_BACTRIA | AFG_MERU
)
KAMBOJA_EXT = KAMBOJA | AFG_MISC
BALOCH = gadm("PAK.2") | gadm("IRN.26")  # gedrosia
TJK_BACTRIA = (
    gadm("TJK.3") | gadm("TJK.1") | gadm("TJK.5.7")
)  # Khatlon province
TJK_SOGDIA_PROPER = gadm("TJK.4")
TJK_MERU = gadm("TJK.2") | (gadm("TJK.5") - TJK_BACTRIA)  # Badakhshan
UZB_BACTRIA = gadm("UZB.12")
UZB_SOGDIA_PROPER = (
    gadm("UZB.6")
    | gadm("UZB.10")
    | gadm("UZB.2")
    | gadm("UZB.9")
    | gadm("UZB.4")
    | gadm("UZB.11")
    | gadm("UZB.13")
    | gadm("UZB.14")
)  # Tashkentic ppl
UZB_KHWAREZM = gadm("UZB.5") | gadm("UZB.7")
UZB_FERGHANA = gadm("UZB") - (UZB_BACTRIA | UZB_SOGDIA_PROPER | UZB_KHWAREZM)
TKM_KHWAREZM = gadm("TKM.3") | gadm("TKM.6")
TKM_MARGIANA = gadm("TKM") - TKM_KHWAREZM
MARGIANA = TKM_MARGIANA | AFG_MARGIANA
BACTRIA = AFG_BACTRIA | TJK_BACTRIA | UZB_BACTRIA
MERU = AFG_MERU | TJK_MERU
SOGDIA_PROPER = UZB_SOGDIA_PROPER | TJK_SOGDIA_PROPER
FERGHANA = UZB_FERGHANA
SOGDIA = SOGDIA_PROPER | FERGHANA
KHWAREZM = UZB_KHWAREZM | TKM_KHWAREZM

# eastern silk road oasis states
# kashgar, khotan, rouran, kucha, agni, turfan
KASHGAR = gadm("CHN.28.9")
KHOTAN = gadm("CHN.28.10")
KUCHA = (
    gadm("CHN.28.1.5")
    | gadm("CHN.28.1.3")
    | gadm("CHN.28.1.7")
    | gadm("CHN.28.1.6")
)
AKSU = gadm("CHN.28.1") - KUCHA
ROURAN = gadm("CHN.28.3.7")
AGNI = gadm("CHN.28.3.8")
QIEMO = gadm("CHN.28.3.6")
KORLA = gadm("CHN.28.3.4")
TURFAN = gadm("CHN.28.14")
XINJIANG = gadm("CHN.28")
TARIM = (
    gadm("CHN.28.1")
    | gadm("CHN.28.3")
    | gadm("CHN.28.9")
    | gadm("CHN.28.10")
    | gadm("CHN.28.11")
)
DZUNGARIA = XINJIANG - TARIM
MONGOLIA = gadm("MNG") | gadm("CHN.19")

# big regions
SUBCONTINENT = (
    gadm("IND")
    | gadm("PAK")
    | gadm("AFG")
    | gadm("BGD")
    | gadm("LKA")
    | gadm("NPL")
    | gadm("BTN")
) | CHINESE_CLAIMS
CENTRAL_ASIA = (
    gadm("AFG")
    | gadm("PAK.2")
    | gadm("IRN.26")
    | gadm("TJK")
    | gadm("UZB")
    | gadm("TKM")
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
    | PHILIPPINES
)
SEA_MAINLAND = (
    SIAM | BURMA | LAOS | KHMER | CHAM | SIAM_BURMA_INTERM | KAREN | TIBET_BURMA_INTERM
)
SEA = SEA_MARITIME | SEA_MAINLAND
SEA_GREATER = SEA | TIBET | NEI_HIM
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
    | gadm("IND.34.7")
    | gadm("IND.34.42")
    | gadm("IND.34.43")
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

# Levant and Iran proper
LEVANT = (
    gadm("LBN")
    | gadm("ISR")
    | gadm("PSE")
    | gadm("SYR")
    | gadm("JOR")
    | gadm("IRQ")
)
IRAN = gadm("IRN")
IRANIC = IRAN | CENTRAL_ASIA_GREATER
IRANIC_GREATER = IRANIC | TARIM

MEDITERRANEAN_EAST = (
    gadm("GRC")
    | gadm("TUR")
    | gadm("CYP")
    | gadm("EGY")
    | gadm("ALB")
    | gadm("BIH")
    | gadm("HRV")
    | gadm("ITA")
    | gadm("MLT")  # not downloaded
    | gadm("MNE")
    | gadm("SVN")
    | gadm("ISR")
    | gadm("PSE")
    | gadm("LBN")
    | gadm("SDN")
) - (
    gadm("EGY.14")
    | gadm("EGY.14")
    | gadm("SDN.10")
    | gadm("SDN.8")
    | gadm("SDN.9")
    | gadm("SDN.4")
    | gadm("SDN.14")
    | gadm("SDN.5")
    | gadm("SDN.17")
    | gadm("SDN.15")
    | gadm("SDN.16")
)

MEDITERRANEAN_WEST = (
    gadm("ESP")
    | gadm("FRA.11")
    | gadm("FRA.13")
    | gadm("MCO")  # not downloaded
    | gadm("PRT")
    | gadm("AND")  # not downloaded
    | gadm("GIB")  # not downloaded
    | gadm("MAR")
    | gadm("DZA")
    | gadm("LBY")
    | gadm("TUN")
) - (
    gadm("DZA.18")
    | gadm("DZA.33")
    | gadm("DZA.20")
    | gadm("DZA.22")
    | gadm("DZA.41")
    | gadm("DZA.1")
    | gadm("DZA.17")
    | gadm("DZA.7")
    | gadm("DZA.44")
    | gadm("LBY.17")
    | gadm("LBY.3")
    | gadm("LBY.22")
    | gadm("LBY.14")
    | gadm("LBY.21")
    | gadm("LBY.18")
    | gadm("LBY.14")
    | gadm("LBY.16")
    | gadm("LBY.5")
    | gadm("LBY.9")
    | gadm("LBY.6")
)
MEDITERRANEAN = MEDITERRANEAN_EAST | MEDITERRANEAN_WEST

GULF = (
    gadm("ARE")
    | gadm("BHR")
    | gadm("KWT")
    | gadm("OMN")
    | gadm("QAT")
    | gadm("SAU")
    | gadm("YEM")
)

AFRICA_EAST_SPOTTY = (
    gadm("SOM") | gadm("TZA") | gadm("DJI") | gadm("ERI") | gadm("MDG")
)

INDIAN_OCEAN = (
    SUBCONTINENT_PROPER
    | SEA
    | GULF
    | AFRICA_EAST_SPOTTY
    | IRANIC
    | LEVANT
    | MEDITERRANEAN
)

MANCHURIA = gadm("CHN.11") | gadm("CHN.17") | gadm("CHN.18")
MONGOLIA = gadm("CHN.19") | gadm("MNG")
CHINA_PROPER = gadm("CHN") - (TIBET | XINJIANG | MANCHURIA | MONGOLIA)
JAPAN = gadm("JPN")
KOREA = gadm("KOR") | gadm("PRK")
ARMENIA = gadm("ARM")
AZER = gadm("AZE")
GEORGIA = gadm("GEO")
MITANNI_SYRIA = (
    gadm("SYR.9")
    | gadm("SYR.14")
    | gadm("SYR.8")
    | gadm("SYR.11")
    | gadm("SYR.10")
    | gadm("SYR.2")
    | gadm("SYR.3")
    | gadm("SYR.7")
    | gadm("SYR.1")
)
MITANNI_TURKEY = (
    gadm("TUR.58")
    | gadm("TUR.1")
    | gadm("TUR.42")
    | gadm("TUR.55")
    | gadm("TUR.64")
    | gadm("TUR.33")
    | gadm("TUR.48")
    | gadm("TUR.2")
    | gadm("TUR.68")
    | gadm("TUR.29")
    | gadm("TUR.26")
    | gadm("TUR.57")
    | gadm("TUR.14")
    | gadm("TUR.69")
    | gadm("TUR.71")
)
MITANNI_IRAQ = (
    gadm("IRQ.17")
    | gadm("IRQ.8")
    | gadm("IRQ.16")
    | gadm("IRQ.6")
    | gadm("IRQ.12")
)
MITANNI = MITANNI_SYRIA | MITANNI_TURKEY | MITANNI_IRAQ
SOCOTRA = gadm("YEM.12.20") | gadm("YEM.12.18")
KALMYKIA = gadm("RUS.22")
BURYATIA = gadm("RUS.9")
TUVA = gadm("RUS.71")
PRIMORYE = gadm("RUS.56")
AMUR = gadm("RUS.3")
BUDDHIST_RUSSIA = KALMYKIA | BURYATIA | TUVA | PRIMORYE | AMUR

PRATIHARA_RAIDS = (
    gadm("IRN.11")
    | gadm("IRN.3")
    | gadm("IRN.15")
    | gadm("IRQ.2")
    | gadm("ARE")
    | gadm("OMN.2")
)  # | gadm("OMN.3") | gadm("OMN.11")

WORLD = (
    INDOSPHERE
    | INDIAN_OCEAN
    | BUDDHIST_RUSSIA
    | CHINA_PROPER
    | NORTH_VIETNAM
    | JAPAN
    | KOREA
    | MONGOLIA
    | ARMENIA
    | SOCOTRA
)
