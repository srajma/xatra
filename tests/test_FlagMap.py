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

test_FlagMap()   
#%%
