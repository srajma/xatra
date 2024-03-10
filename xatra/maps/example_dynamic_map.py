from xatra.maps.FlagMap import Flag, Map
from xatra.matchers import *
from xatra.data import Loka, Varuna


class MyDynamic(Map):
    def __init__(self, **kwargs):
        options = {
            "custom_html": (
                f"Rough example demonstration of how dynamic maps are currently implemented."
            )
        }
        options.update(kwargs)
        super().__init__(**options)

    @property
    def flags(self):
        return [
            Flag(name="KUSHAN", matcher=PANCALA_S, period=[150, 200]),
            Flag(name="KURU", matcher=KURU_PROPER, period=[-1000, -900]),
            Flag(name="SALVA", matcher=KURU_PROPER, period=[-900, -500]),
            Flag(name="MAURYA", matcher=SUBCONTINENT_PROPER, period=[-300, -180]),
            Flag(name="ARJUNAYANA", matcher=KURU_PROPER, period=[-100, 100]),
        ]

    @property
    def geojson(self):
        return Loka.INDIAN_SUBCONTINENT.load()

    @property
    def geojson_rivers(self):
        return Varuna.INDIAN_SUBCONTINENT.load()
