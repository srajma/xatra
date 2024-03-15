"""Holder module for your favourite feature DataCollections.
- xatra.data.Loka for feature DataCollections
- xatra.data.Varuna for river DataCollections
- xatra.data.Pura for city DataCollections
"""

from .data import *

NORTHINDIAN = DataCollection(
    DataItem(
        type="river", id="1236345", river_type="relation", common_name="ganga"
    ),
    DataItem(
        type="river", id="326077", river_type="relation", common_name="yamuna"
    ),
    DataItem(
        type="river", id="15793911", river_type="relation", common_name="sarayu"
    ),
    DataItem(
        type="river", id="6722174", river_type="relation", common_name="ramaganga"
    ),
    DataItem(
        type="river",
        id="12559166",
        river_type="relation",
        common_name="suvarnanadi",
    ),
    DataItem(type="river", id="247787304", river_type="way", common_name="campa"),
    DataItem(
        type="river", id="13676883", river_type="relation", common_name="kaushika"
    ),
    DataItem(
        type="river",
        id="5388381",
        river_type="relation",
        common_name="sarasvati (ghaggar)",
    ),
    DataItem(
        type="river", id="11117634", river_type="relation", common_name="kshipra"
    ),
    DataItem(
        type="river", id="8385364", river_type="relation", common_name="chambal"
    ),
)
"""Rivers of Northern India, excluding the Audichya region."""

PENINSULAR = DataCollection(
    DataItem(
        type="river", id="5405552", river_type="relation", common_name="narmada"
    ),
    DataItem(
        type="river", id="2826093", river_type="relation", common_name="godavari"
    ),
    DataItem(
        type="river", id="337204", river_type="relation", common_name="krsnaveni"
    ),
    DataItem(
        type="river", id="2858525", river_type="relation", common_name="bhimarathi"
    ),
    DataItem(
        type="river", id="2742213", river_type="relation", common_name="tungabhadra"
    ),
    DataItem(
        type="river", id="2704746", river_type="relation", common_name="kaveri"
    ),
)
"""Rivers of Peninsular India"""

SAPTASINDHU = DataCollection(
    DataItem(
        type="river", id="1159233", river_type="relation", common_name="sindhu"
    ),
    DataItem(
        type="river",
        id="8306691",
        river_type="relation",
        common_name="vitasta (jhelum)",
    ),
    DataItem(
        type="river",
        id="6085682",
        river_type="relation",
        common_name="chandrabhaga (chenab)",
    ),
    DataItem(
        type="river",
        id="8894611",
        river_type="relation",
        common_name="iravati (ravi)",
    ),
    DataItem(
        type="river",
        id="325142",
        river_type="relation",
        common_name="satadru (sutlej)",
    ),
    DataItem(
        type="river",
        id="10693630",
        river_type="relation",
        common_name="vipasa (beas)",
    ),
)
"""Rivers of the Audichya region"""

INDIAN_SUBCONTINENT = DataCollection(NORTHINDIAN, PENINSULAR, SAPTASINDHU)
"""Rivers of the Indian Subcontinent"""

AFGHANISTAN = DataCollection(
    DataItem(
        type="river",
        id="1676476",
        river_type="relation",
        common_name="kubha (kabul)",
    ),
    DataItem(
        type="river",
        id="6608825",
        river_type="relation",
        common_name="kama (kunar)",
    ),
    DataItem(
        type="river",
        id="8623883",
        river_type="relation",
        common_name="haraxvati (arghandab)",
    ),
    DataItem(
        type="river",
        id="5252846",
        river_type="relation",
        common_name="haetumant (helmand)",
    ),
    DataItem(
        type="river", id="3173475", river_type="relation", common_name="hari (hari)"
    ),
    DataItem(
        type="river",
        id="223008",
        river_type="relation",
        common_name="vaksu (amu darya)",
    ),
)
"""Rivers of Afghanistan"""

IRANIAN_SUBCONTINENT = DataCollection(
    DataItem(
        type="river",
        id="223008",
        river_type="relation",
        common_name="vaksu (amu darya)",
    ),
    DataItem(
        type="river",
        id="1206456",
        river_type="relation",
        common_name="jaxartes (syr darya)",
    ),
)
"""Oxus and Jaxartes"""

SILKRD = DataCollection(
    IRANIAN_SUBCONTINENT,
    AFGHANISTAN,
    DataItem(
        type="river",
        id="2162521",
        river_type="relation",
        common_name="sita (tarim)",
    ),
)
"""Oxus, Jaxartes, Tarim and Afghan rivers"""

WORLD = DataCollection(INDIAN_SUBCONTINENT, SILKRD)
"""All rivers we have"""

NEXUS = DataCollection(SILKRD, SAPTASINDHU)
"""Oxus, Jaxartes, Tarim, Afghan rivers and Audichya (Sapta-Sindhu) rivers"""