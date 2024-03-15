"""Holder module for your favourite feature DataCollections.
- xatra.data.Loka for feature DataCollections
- xatra.data.Varuna for river DataCollections
- xatra.data.Pura for city DataCollections
"""

from .data import *

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
    DataItem(type="break", id="CHN.28_1", level=3),
)
"""East Asia, modern political boundaries. TODO: include Japan and Korea"""

SEA_MAINLAND = DataCollection(
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
"""Mainland Southeast Asia. Excludes North Vietnam and Kachin (in Burma)"""

SEA_MARITIME = DataCollection(
    DataItem(type="feature", id="MYS", level=2),
    DataItem(type="feature", id="IDN", level=2),
    DataItem(type="feature", id="BRN", level=2),
    DataItem(type="feature", id="TLS", level=2),
    DataItem(type="feature", id="SGP", level=1),
    filter=SEA_MARITIME,
)
"""Maritime Southeast Asia."""

SEA = DataCollection(SEA_MAINLAND, SEA_MARITIME, filter=SEA)
"""Southeast Asia. Excludes North Vietnam and Kachin (in Burma)."""

LEVANT = DataCollection(
    DataItem(type="feature", id="IRQ", level=2),
    DataItem(type="feature", id="SYR", level=2),
    DataItem(type="feature", id="LBN", level=2),
    DataItem(type="feature", id="ISR", level=1),
    DataItem(type="feature", id="PSE", level=2),
    DataItem(type="feature", id="JOR", level=2),
)
"""Levant, modern political boundaries. Excludes Kuwait."""

GULF = DataCollection(
    DataItem(type="feature", id="KWT", level=1),
    DataItem(type="feature", id="BHR", level=1),
    DataItem(type="feature", id="QAT", level=1),
    DataItem(type="feature", id="ARE", level=2),
    DataItem(type="feature", id="OMN", level=2),
    DataItem(type="feature", id="SAU", level=2),
    DataItem(type="feature", id="YEM", level=2),
)
"""Gulf, modern political boundaries. Includes Kuwait and Yemen."""

MEDITERRANEAN = DataCollection(
    DataItem(type="feature", id="TUR", level=2),
    DataItem(type="feature", id="GRC", level=2),
    DataItem(type="feature", id="ITA", level=2),
    DataItem(type="feature", id="EGY", level=2),
    DataItem(type="feature", id="LBY", level=1),
    DataItem(type="feature", id="TUN", level=2),
)
"""Mediterranean, modern political boundaries. TODO: Include a lot of things."""

AFRICA_EAST = DataCollection(
    DataItem(type="feature", id="SOM", level=2),
    DataItem(type="feature", id="TZA", level=2),
    DataItem(type="feature", id="SDN", level=2),
    DataItem(type="feature", id="DJI", level=2),
    DataItem(type="feature", id="ERI", level=2),
    DataItem(type="feature", id="MDG", level=2),
)
"""East Africa, modern political boundaries."""

INDOSPHERE = DataCollection(
    INDIAN_SUBCONTINENT,
    IRANIAN_SUBCONTINENT,
    AFGHANISTAN,
    CHINESE_SUBCONTINENT,
    SEA,
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
