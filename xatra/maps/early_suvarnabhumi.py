"""A map of early Indian colonies in Suvarnabhumi (Southeast Asia) in the
1st-2nd centuries. 
"""

from xatra.maps.FlagMap import Label, Flag, FlagMap
from xatra.maps.nations import flags
from xatra.matchers import *
from xatra.data import Loka

css_city1 = {"color": "black", "line-height": "1"}
"""Type 1: black squares, for cities mentioned in Indian literature."""
css_bullet1 = {"border-radius": "0%", "background-color": "black"}
"""Type 1: black squares, for cities mentioned in Indian literature."""
css_city2 = {"color": "blue", "line-height": "1"}
"""Type 2: blue circles, for capitals of Indian(-ized) states known from local history."""
css_bullet2 = {"border-radius": "50%", "background-color": "blue"}
"""Type 2: blue circles, for capitals of Indian(-ized) states known from local history."""
css_general = {"color": "#666666", "text-transform": "uppercase", "font-weight": "bold"}


def c2(name, desc=None):
    if desc:
        return f"{name}<br><span style='font-size: 0.7em'>{desc}</span>"
    else:
        return name


general_labels = [
    Label(type="custom_label", name="Yāva", location=[-7.3, 110.0]),
    Label(
        type="custom_label", name="Karpūradvīpa/<br>Barhiṇadvīpa", location=[0.0, 114.0]
    ),
    Label(
        type="custom_label",
        name="Kaṭāha",
        location=[6.0, 100.3],
        css={"transform": "rotate(60deg)"},
    ),
    Label(
        type="custom_label",
        name="Dvīpāntara",
        location=[0.0, 106.9],
        css={"transform": "rotate(-20deg)"},
    ),
]
for label in general_labels:
    label.css |= css_general
    label.ref = "Moti Chandra, Trade and Trade Routes in Ancient India"

cities1 = [
    Label(type="city", name="Takkasilā", location=[20.70, 92.40], ref="p. 132"),
    Label(type="city", name="Kālamukha", location=[19.71, 93.50], ref="p. 132"),
    Label(type="city", name="Vesuṅga", location=[16.81, 96.18], ref="p. 132"),
    Label(type="city", name="Verāpatha", location=[14.09, 98.19], ref="p. 132"),
    Label(type="city", name="Takkola", location=[8.89, 98.27], ref="p. 132"),
    Label(type="city", name="Tāṁbraliṅga", location=[3.80, 103.33], ref="p. 132"),
    Label(type="city", name="Vaṅga", location=[-2.36, 106.15], ref="p. 133"),
    Label(type="city", name="Ailavaddhana", location=[-8.50, 117.21], ref="p. 133"),
    Label(type="city", name="Suvarṇakūṭa", location=[11.46, 103.08], ref="p. 133"),
    Label(type="city", name="Kamalapura", location=[11.07, 103.68], ref="p. xiv"),
    Label(type="city", name="Samudrapaṭṭaṇa", location=[-0.91, 100.35], ref="p. 141"),
]
for label in cities1:
    label.css |= css_city1
    label.css_bullet |= css_bullet1
    label.ref = f"Moti Chandra, Trade and Trade Routes in Ancient India. {label.ref}"

cities2 = [
    Label(
        type="city",
        name=c2("Suddhamāvati/Thaton", "Telugu explorers or Tissa's son"),
        location=[17.33, 96.47],
        ref="p. 31",
    ),
    Label(
        type="city",
        name=c2("Saṅkissa/Tagaung", "Abhirāja"),
        location=[23.5, 96.0],
        ref="p. 31",
    ),
    Label(
        type="city",
        name=c2("Śrīkṣetra/Pyu", "under Saṅkissa"),
        location=[18.81, 95.29],
        ref="p. 31",
    ),
    Label(
        type="city",
        name=c2("Dhaññavatī/Arakanese", "under Saṅkissa"),
        location=[20.87, 93.06],
        ref="p. 31",
    ),
    Label(
        type="city",
        name=c2("Vyādhapura/Funan", "Kauṇḍinya I"),
        location=[11.00, 104.98],
        ref="p. 20",
    ),
    Label(
        type="city",
        name=c2("Kīrtinagara/Oc Eo", "under Vyādhapura"),
        location=[10.249203, 105.147056],
        ref="p. 21",
    ),
    Label(
        type="city",
        name=c2("Tien-Suen", "under Vyādhapura"),
        location=[9.196281, 99.329105],
        ref="p. 21",
    ),
    Label(
        type="city",
        name=c2("Kambuja", "Kambu Swayambhuva/Indraprastha prince"),
        location=[14.901246, 105.868371],
        ref="p. 24",
    ),
    Label(
        type="city",
        name=c2("Campa", "Śrī Māra"),
        location=[16.196377, 108.131374],
        ref="p. 25",
    ),
    Label(
        type="city",
        name=c2("Langkasuka", "Mauryan prince?"),
        location=[6.759206, 101.307032],
        ref="p. 28",
    ),
    Label(
        type="city",
        name=c2("??", "Amarāvati-style Buddhist statue found at Sempaga"),
        location=[-2.316840, 119.128122],
        ref="p. 28",
    ),
    Label(
        type="city",
        name=c2("Yava", "Hastināpura prince, Deva-varman?"),
        location=[-6.455765, 110.771262],
        ref="p. 33",
    ),
]
for label in cities2:
    label.css |= css_city2
    label.css_bullet |= css_bullet2
    label.ref = (
        f"RC Majumdar, Ancient Indian Colonization in South-East Asia. {label.ref}"
    )

all_labels = general_labels + cities1 + cities2

EARLY_SUVARNABHUMI = FlagMap(
    flags=flags,
    loka=Loka.SEA,
    custom_labels=all_labels,
    custom_html=(
        "Earliest recorded Indian colonies and states in Southeast Asia, c. 1st and 2nd. "
        "centuries BC. Black squares are cities mentioned in Indian literature; blue circles"
        "are Indian(-ized) kingdoms known from local or Chinese history.<br><br>"
        "<b>Sources:</b><br>"
        "RC Majumdar (1979), <i>Ancient Indian colonization in Southeast Asia.</i> p. 20-33.<br>"
        "Moti Chandra (1977), <i>Trade and Trade Routes in Ancient India.</i> p. 132-133, xiv"
    ),
    labels_on_map=False,
    base_maps=(
        ["Esri.WorldPhysical"],
        ["OpenStreetMap", "CartoDB.Positron", "Esri.WorldImagery", "OpenTopoMap"],
    ),
)
