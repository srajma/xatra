"""The canonical 'Akhand Bharat' map."""

from xatra.maps.FlagMap import Flag, FlagMap
from xatra.matchers import *
from xatra.data import Loka, Varuna

FUNDAMENTAL_COLONIES = SEA | NEI_HIM | TARIM | SOCOTRA
BRIEF_COLONIES = (
    BALOCH
    | KANDAHAR
    | ZARANJ
    | AFG_MISC
    | KAMBOJA
    | BACTRIA
    | MARGIANA
    | SOGDIA
    | MONGOLIA
    | MITANNI
    | ARMENIA
)
FUNDAMENTAL_HB = TIBET | JAPAN | KOREA
DEEP_INFLUENCE = CHINA_PROPER | MANCHURIA | BUDDHIST_RUSSIA | NORTH_VIETNAM
EXPLORED = (MEDITERRANEAN_EAST | AFRICA_EAST_SPOTTY | GULF | LEVANT | IRANIC) - (
    DEEP_INFLUENCE | FUNDAMENTAL_HB | BRIEF_COLONIES | FUNDAMENTAL_COLONIES | SUBCONTINENT_PROPER
)
flags = [
    Flag(name="INDIAN CORE", matcher=SUBCONTINENT_PROPER),
    Flag(name="FUNDAMENTAL COLONIES", matcher=FUNDAMENTAL_COLONIES),
    Flag(name="BRIEF COLONIES", matcher=BRIEF_COLONIES),
    Flag(name="FUNDAMENTALLY HINDU/BUDDHIST", matcher=FUNDAMENTAL_HB),
    Flag(name="DEEP INFLUENCE", matcher=DEEP_INFLUENCE),
    Flag(name="RAIDED", matcher=PRATIHARA_RAIDS),
    Flag(name="EXPLORED", matcher=EXPLORED),
]

CUSTOM_HTML = """
Greater Indian Sphere.<br>
<b>Indian core</b>: India proper<br>
<b>Fundamental colonies</b>: Countries whose civilizations were fundamentally an Indian endeavour.<br>
<b>Brief colonies:</b> Countries that were ruled by an Indian for a brief period of time.<br>
<b>Fundamentally Hindu/Buddhist:</b> Countries whose civilizations were fundamentally Hindu/Buddhist, but no direct Indian rule.<br>
<b>Deep Influence:</b> Countries that were significantly influenced by Indiian religion and philosophy.<br>
<b>Explored:</b> Countries that were visited by Indians in antiquity.<br>
"""

CUSTOM_COLORS = {
    "INDIAN CORE": "#740001",
    "FUNDAMENTAL COLONIES": "#e80000",
    "BRIEF COLONIES": "#fc4e2b",
    "FUNDAMENTALLY HINDU/BUDDHIST": "#f5820b",
    "DEEP INFLUENCE": "#a425d6",
    "RAIDED": "#936a27",
    "EXPLORED": "#698db3",
}

MANDALA = FlagMap(
    flags=flags,
    loka=Loka.WORLD,
    varuna=Varuna.WORLD,
    custom_html=CUSTOM_HTML,
    custom_colors=CUSTOM_COLORS,
    zoom_start=4,
)
