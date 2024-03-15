#%%
from xatra.maps.FlagMap import Flag, FlagMap
from xatra.data import Loka, Varuna
from xatra.matchers import *

flags = [
    Flag(name="KUTCH", matcher=KUTCH),
    Flag(name="SURASTRA", matcher=SURASTRA),
    Flag(name="ANARTA", matcher=ANARTA),
    Flag(name="LATA", matcher=LATA),
    Flag(name="KUKURA", matcher=KUKURA),
    Flag(name="MATSYA", matcher=MATSYA),
    Flag(name="MAHARASHTRA", matcher=SUBCONTINENT),
]

def test_FlagMap():
    fm = FlagMap(
        flags=flags,
        loka=Loka.INDIC,
        varuna=Varuna.INDIAN_SUBCONTINENT,
        custom_colors = {"KUTCH" : "#ff0000"},
        custom_html = "Test FlagMap",
        tolerance = 0.01,
        verbose=True
    )
    fm.plot(path_out = "tests/examples/test_FlagMap.html")

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

def test_ExampleDynamic():
    ExampleDynamic.plot(path_out="tests/examples/dynamic.html")

test_FlagMap()   

#%%
