import sys, xatra
from xatra.loaders import gadm, naturalearth
from xatra.territory_library import *
m = xatra.Map()
m.Flag(label="Kushana", value=GANDHARA | PUNJAB | KAMBOJA | BACTRIA | UP_WEST | MATSYA, note="Kanishka's empire")
m.Flag(label="Satavahana", value=VIDARBHA | ASMAKA | MULAKA | APARANTA | GREATER_PUNE | VENGI)
m.Flag(label="Kshatrapa", value=GUJARAT | AVANTI | SINDH_S, note="Western Satraps")
m.Flag(label="Kalinga", value=KALINGA_GREATER)
m.Flag(label="Cola", value=COLA)
m.Flag(label="Pandya", value=PANDYA)
m.Flag(label="Cera", value=CERA)
m.Flag(label="Simhala", value=SIMHALA)
m.Flag(label="Magadha", value=MAGADHA | ANGA | VANGA)
m.Flag(label="Yaudheya", value=YAUDHEYA)
m.Flag(label="Kosala", value=KOSALA | VATSA | KASI)
m.River(label="Gaṅgā", value=naturalearth("1159122643"), show_label=True)
m.Path(label="Uttarāpatha", value=[[34.0,71.5],[31.5,74.3],[28.6,77.2],[25.4,81.8],[25.6,85.1]], show_label=True)
for name, pos in [("Pāṭaliputra",[25.6,85.1]),("Mathurā",[27.5,77.7]),("Puruṣapura",[34.0,71.5]),("Ujjayinī",[23.2,75.8]),("Pratiṣṭhāna",[19.5,75.4]),("Kāñcī",[12.8,79.7]),("Madurai",[9.9,78.1])]:
    m.Point(label=name, position=pos, show_label=True)
m.Text(label="Jambudvīpa", position=[21.5, 79.5])
m.TitleBox("<h2>India, c. 150 CE</h2><p>The age of the Kushanas and Satavahanas.</p>")
m.show(out_html=sys.argv[1])
