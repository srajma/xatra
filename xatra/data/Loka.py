"""Holder module for your favourite feature DataCollections.
- xatra.data.Loka for feature DataCollections
- xatra.data.Varuna for river DataCollections
- xatra.data.Pura for city DataCollections
"""

from .data import DataItem, DataCollection
from xatra.matchers.matcherlib import *

INDIAN_SUBCONTINENT_LOC = DataCollection(
    DataItem(type="feature", id="IND", level=2),
    DataItem(type="feature", id="PAK", level=3),
    DataItem(type="feature", id="BGD", level=2),
    DataItem(type="feature", id="LKA", level=2),
    DataItem(type="feature", id="NPL", level=3),
    DataItem(type="feature", id="BTN", level=2),
    DataItem(type="break", id="IND.20.20_1", level=3),
)
"""Indian subcontinent, modern political boundaries, excludes Afghanistan.
INDIAN_SUBCONTINENT_LOC excludes Chinese claims, INDIAN_SUBCONTINENT includes it."""

INDIAN_SUBCONTINENT = DataCollection(
    INDIAN_SUBCONTINENT_LOC,
    DataItem(type="feature", id="CHN", level=2),
    filter=SUBCONTINENT,
)
"""Indian subcontinent, modern political boundaries, excludes Afghanistan.
INDIAN_SUBCONTINENT_LOC excludes Chinese claims, INDIAN_SUBCONTINENT includes it."""

IRANIAN_SUBCONTINENT = DataCollection(
    DataItem(type="feature", id="IRN", level=2),
    DataItem(type="feature", id="TJK", level=2),
    DataItem(type="feature", id="UZB", level=2),
    DataItem(type="feature", id="TKM", level=2),
    DataItem(type="feature", id="KGZ", level=2),
    DataItem(type="feature", id="KAZ", level=2),
)
"""Iranian subcontinent, modern political boundaries, excludes Afghanistan."""

AFGHANISTAN = DataCollection(DataItem(type="feature", id="AFG", level=2))
"""Afghanistan, modern political boundaries."""

CHINESE_SUBCONTINENT = DataCollection(
    DataItem(type="feature", id="CHN", level=2),
    DataItem(type="feature", id="MNG", level=2),
    DataItem(type="feature", id="JPN", level=1),
    DataItem(type="feature", id="KOR", level=1),
    DataItem(type="feature", id="PRK", level=1),
    DataItem(type="feature", id="RUS", level=2),
    DataItem(type="break", id="CHN.28_1", level=3),
)
"""East Asia, modern political boundaries."""

SEA_MAINLAND = DataCollection(
    DataItem(
        type="feature", id="IND", level=2
    ),  # Andaman and Nicobar, North-East India
    DataItem(type="feature", id="MMR", level=1),
    DataItem(type="feature", id="THA", level=1),
    DataItem(type="feature", id="LAO", level=1),
    DataItem(type="feature", id="KHM", level=1),
    DataItem(type="feature", id="VNM", level=1),
    filter=SEA_MAINLAND,
)
"""Mainland Southeast Asia, LEVEL 1 FEATURES. Excludes North Vietnam and Kachin (in Burma)"""

SEA_MAINLAND_2 = DataCollection(
    DataItem(
        type="feature", id="IND", level=2
    ),  # Andaman and Nicobar, North-East India
    DataItem(type="feature", id="MMR", level=2),
    DataItem(type="feature", id="THA", level=2),
    DataItem(type="feature", id="LAO", level=2),
    DataItem(type="feature", id="KHM", level=2),
    DataItem(type="feature", id="VNM", level=2),
    filter=SEA_MAINLAND,
)
"""Mainland Southeast Asia, LEVEL 2 FEATURES. Excludes North Vietnam and Kachin (in Burma)"""

SEA_MARITIME = DataCollection(
    DataItem(type="feature", id="MYS", level=1),
    DataItem(type="feature", id="IDN", level=1),
    DataItem(type="feature", id="BRN", level=1),
    DataItem(type="feature", id="TLS", level=1),
    DataItem(type="feature", id="SGP", level=1),
    DataItem(type="feature", id="PHL", level=1),
    filter=SEA_MARITIME,
)
"""Maritime Southeast Asia, LEVEL 1 FEATURES."""

SEA_MARITIME_2 = DataCollection(
    DataItem(type="feature", id="MYS", level=2),
    DataItem(type="feature", id="IDN", level=2),
    DataItem(type="feature", id="BRN", level=2),
    DataItem(type="feature", id="TLS", level=2),
    DataItem(type="feature", id="SGP", level=1),
    DataItem(type="feature", id="PHL", level=1),
    filter=SEA_MARITIME,
)
"""Maritime Southeast Asia, LEVEL 2 FEATURES."""

TIBET = DataCollection(
    DataItem(type="feature", id="CHN", level=2),
    DataItem(type="feature", id="IND", level=2),
    DataItem(type="feature", id="BTN", level=2),
    DataItem(type="feature", id="NPL", level=3),
    filter=TIBET,
)

SEA = DataCollection(
    SEA_MAINLAND,
    SEA_MARITIME,
    filter=SEA,
)
"""Southeast Asia excluding Tibet. Excludes North Vietnam and Kachin (in Burma)."""

SEA_GREATER = DataCollection(
    SEA,
    TIBET,
    filter=SEA_GREATER,
)
"""Southeast Asia including Tibet. Excludes North Vietnam and Kachin (in Burma)."""

LEVANT = DataCollection(
    DataItem(type="feature", id="IRQ", level=1),
    DataItem(type="feature", id="SYR", level=1),
    DataItem(type="feature", id="LBN", level=1),
    DataItem(type="feature", id="ISR", level=1),
    DataItem(type="feature", id="PSE", level=1),
    DataItem(type="feature", id="JOR", level=1),
)
"""Levant, modern political boundaries. Excludes Kuwait. LEVEL 1 FEATURES."""

LEVANT_2 = DataCollection(
    DataItem(type="feature", id="IRQ", level=2),
    DataItem(type="feature", id="SYR", level=2),
    DataItem(type="feature", id="LBN", level=2),
    DataItem(type="feature", id="ISR", level=1),
    DataItem(type="feature", id="PSE", level=2),
    DataItem(type="feature", id="JOR", level=2),
)
"""Levant, modern political boundaries. Excludes Kuwait. LEVEL 2 FEATURES."""

GULF = DataCollection(
    DataItem(type="feature", id="KWT", level=0),
    DataItem(type="feature", id="BHR", level=0),
    DataItem(type="feature", id="QAT", level=0),
    DataItem(type="feature", id="ARE", level=1),
    DataItem(type="feature", id="OMN", level=1),
    DataItem(type="feature", id="SAU", level=2),
    DataItem(type="feature", id="YEM", level=2),
)
"""Gulf, modern political boundaries. Includes Kuwait and Yemen. LEVEL 2 FEATURES."""

GULF_2 = DataCollection(
    DataItem(type="feature", id="KWT", level=1),
    DataItem(type="feature", id="BHR", level=1),
    DataItem(type="feature", id="QAT", level=1),
    DataItem(type="feature", id="ARE", level=2),
    DataItem(type="feature", id="OMN", level=2),
    DataItem(type="feature", id="SAU", level=2),
    DataItem(type="feature", id="YEM", level=2),
)
"""Gulf, modern political boundaries. Includes Kuwait and Yemen. LEVEL 2 FEATURES."""

MEDITERRANEAN = DataCollection(
    DataItem(type="feature", id="TUR", level=1),
    DataItem(type="feature", id="GRC", level=2),
    DataItem(type="feature", id="ITA", level=2),
    DataItem(type="feature", id="EGY", level=1),
    DataItem(type="feature", id="LBY", level=1),
    DataItem(type="feature", id="TUN", level=1),
    DataItem(type="feature", id="DZA", level=1),
    DataItem(type="feature", id="MAR", level=1),
    DataItem(type="feature", id="ESP", level=1),
    DataItem(type="feature", id="PRT", level=1),
    DataItem(type="feature", id="FRA", level=1),
    DataItem(type="feature", id="MKD", level=0),
    DataItem(type="feature", id="ALB", level=0),
    DataItem(type="feature", id="MNE", level=0),
    DataItem(type="feature", id="BIH", level=0),
    DataItem(type="feature", id="HRV", level=0),
    DataItem(type="feature", id="SVN", level=0),
    DataItem(type="feature", id="CYP", level=0),
)
"""Mediterranean, modern political boundaries. LEVEL 1 FEATURES."""

MEDITERRANEAN_2 = DataCollection(
    DataItem(type="feature", id="TUR", level=2),
    DataItem(type="feature", id="GRC", level=2),
    DataItem(type="feature", id="ITA", level=2),
    DataItem(type="feature", id="EGY", level=2),
    DataItem(type="feature", id="LBY", level=1),
    DataItem(type="feature", id="TUN", level=2),
    DataItem(type="feature", id="DZA", level=2),
    DataItem(type="feature", id="MAR", level=2),
    DataItem(type="feature", id="ESP", level=2),
    DataItem(type="feature", id="PRT", level=2),
    DataItem(type="feature", id="FRA", level=2),
    DataItem(type="feature", id="MKD", level=1),
    DataItem(type="feature", id="ALB", level=1),
    DataItem(type="feature", id="MNE", level=1),
    DataItem(type="feature", id="BIH", level=1),
    DataItem(type="feature", id="HRV", level=1),
    DataItem(type="feature", id="SVN", level=1),
    DataItem(type="feature", id="CYP", level=1),
)
"""Mediterranean, modern political boundaries. LEVEL 2 FEATURES."""

AFRICA_EAST = DataCollection(
    DataItem(type="feature", id="SOM", level=1),
    DataItem(type="feature", id="TZA", level=1),
    DataItem(type="feature", id="SDN", level=1),
    DataItem(type="feature", id="DJI", level=0),
    DataItem(type="feature", id="ERI", level=0),
    DataItem(type="feature", id="MDG", level=1),
)
"""East Africa, modern political boundaries. LEVEL 1 FEATURES."""

AFRICA_EAST_2 = DataCollection(
    DataItem(type="feature", id="SOM", level=2),
    DataItem(type="feature", id="TZA", level=2),
    DataItem(type="feature", id="SDN", level=2),
    DataItem(type="feature", id="DJI", level=1),
    DataItem(type="feature", id="ERI", level=1),
    DataItem(type="feature", id="MDG", level=2),
)
"""East Africa, modern political boundaries. LEVEL 2 FEATURES."""

CAUCASUS = DataCollection(
    DataItem(type="feature", id="GEO", level=1),
    DataItem(type="feature", id="ARM", level=1),
    DataItem(type="feature", id="AZE", level=1),
)

INDOSPHERE = DataCollection(
    INDIAN_SUBCONTINENT,
    IRANIAN_SUBCONTINENT,
    AFGHANISTAN,
    CHINESE_SUBCONTINENT,
    SEA_GREATER,
    filter=INDOSPHERE,
)
"""Akhand Bharat"""

WORLD = DataCollection(
    AFRICA_EAST,
    GULF,
    LEVANT,
    SEA_MAINLAND,
    SEA_MARITIME,
    MEDITERRANEAN,
    AFGHANISTAN,
    IRANIAN_SUBCONTINENT,
    CHINESE_SUBCONTINENT,
    INDIAN_SUBCONTINENT,
    CAUCASUS,
    filter=WORLD,
)
"""Everything we've got."""

INDIC = DataCollection(INDIAN_SUBCONTINENT, filter=SUBCONTINENT_PROPER)
"""Core areas of India in antiquity."""

SILKRD = DataCollection(
    IRANIAN_SUBCONTINENT,
    AFGHANISTAN,
    CHINESE_SUBCONTINENT,  # for xinjiang
    INDIAN_SUBCONTINENT,  # for Balochistan, maybe Inner Kamboja
    filter=CENTRAL_ASIA_GREATER | TARIM,
)
"""Iranic regions, Afghanistan, Tarim baisin and NW Frontier territories of Pakistan."""

NEXUS = DataCollection(SILKRD, filter=CENTRAL_ASIA_GREATER | TARIM | AUDICYA)
"""Iranic regions, Afghanistan, Tarim basin and Audichya region of the Indian subcontinent"""

INDIAN_OCEAN = DataCollection(
    INDIAN_SUBCONTINENT,
    SEA,
    IRANIAN_SUBCONTINENT,
    AFGHANISTAN,
    LEVANT,
    GULF,
    MEDITERRANEAN,
    AFRICA_EAST,
    filter=INDIAN_OCEAN,
)
