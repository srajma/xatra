from xatra.maps.FlagMap import Flag, FlagMap
from xatra.matchers import *
from xatra.data import Loka, Varuna


ExampleDynamic = FlagMap(
    flags=[
        Flag(name="KUSHAN", matcher=PANCALA_S, period=[150, 200]),
        Flag(name="KURU", matcher=KURU_PROPER, period=[-1000, -900]),
        Flag(name="SALVA", matcher=KURU_PROPER, period=[-900, -500]),
        Flag(name="MAURYA", matcher=SUBCONTINENT_PROPER, period=[-300, -180]),
        Flag(name="ARJUNAYANA", matcher=KURU_PROPER, period=[-100, 100]),
    ],
    loka=Loka.INDIAN_SUBCONTINENT,
    varuna=Varuna.INDIAN_SUBCONTINENT,
    custom_html=(
        "Rough example demonstration of how dynamic maps are currently implemented."
    ),
)