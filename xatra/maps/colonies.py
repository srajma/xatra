"""A map of early Indian colonies in Suvarnabhumi (Southeast Asia) in the
1st-2nd centuries. 
"""

from xatra.maps.FlagMap import Label, Flag, FlagMap
from xatra.maps.nations import flags
from xatra.matchers import *
from xatra.data import Loka
from xatra.utilities import css_str

css_port = {"color": "black", "line-height": "1"}
"""Type 1: black squares, for cities mentioned in Indian literature."""
css_port_bullet = {"border-radius": "0%", "background-color": "black"}
"""Type 1: black squares, for cities mentioned in Indian literature."""
css_colony = {"color": "blue", "line-height": "1"}
"""Type 2: blue circles, for capitals of Indian(-ized) states known from local history."""
css_colony_bullet = {"border-radius": "50%", "background-color": "blue"}
"""Type 2: blue circles, for capitals of Indian(-ized) states known from local history."""
css_general = {"color": "#666666", "text-transform": "uppercase", "font-weight": "bold"}
"""Misc labels on map."""


def colon(name, desc=None):
    if desc:
        return f"{name}<br><span style='font-size: 0.7em'>{desc}</span>"
    else:
        return name


general_labels_SEA = [
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
    Label(
        type="custom_label",
        name="Suvarṇabhūmi",
        location=[6.053218, 107.823257],
        css={"font-size": "18pt"},
    ),
]
for label in general_labels_SEA:
    label.css = css_general | label.css
    label.ref = "Moti Chandra, Trade and Trade Routes in Ancient India"

ports_SEA = [
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
for label in ports_SEA:
    label.css = css_port | label.css
    label.css_bullet = css_port_bullet | label.css_bullet
    label.ref = f"Moti Chandra, Trade and Trade Routes in Ancient India. {label.ref}"

colonies_SEA = [
    Label(
        type="city",
        name=colon("Suddhamāvati/Thaton", "Telugu explorers or Tissa's son"),
        location=[17.33, 96.47],
        ref="p. 31",
    ),
    Label(
        type="city",
        name=colon("Saṅkissa/Tagaung", "Abhirāja"),
        location=[23.5, 96.0],
        ref="p. 31",
    ),
    Label(
        type="city",
        name=colon("Śrīkṣetra/Pyu", "under Saṅkissa"),
        location=[18.81, 95.29],
        ref="p. 31",
    ),
    Label(
        type="city",
        name=colon("Dhaññavatī/Arakanese", "under Saṅkissa"),
        location=[20.87, 93.06],
        ref="p. 31",
    ),
    Label(
        type="city",
        name=colon("Vyādhapura/Funan", "Kauṇḍinya I"),
        location=[11.00, 104.98],
        ref="p. 20",
    ),
    Label(
        type="city",
        name=colon("Kīrtinagara/Oc Eo", "under Vyādhapura"),
        location=[10.249203, 105.147056],
        ref="p. 21",
    ),
    Label(
        type="city",
        name=colon("Tien-Suen", "under Vyādhapura"),
        location=[9.196281, 99.329105],
        ref="p. 21",
    ),
    Label(
        type="city",
        name=colon("Kambuja", "Kambu Swayambhuva/Indraprastha prince"),
        location=[14.901246, 105.868371],
        ref="p. 24",
    ),
    Label(
        type="city",
        name=colon("Campa", "Śrī Māra"),
        location=[16.196377, 108.131374],
        ref="p. 25",
    ),
    Label(
        type="city",
        name=colon("Langkasuka", "Mauryan prince?"),
        location=[6.759206, 101.307032],
        ref="p. 28",
    ),
    Label(
        type="city",
        name=colon("??", "Amarāvati-style Buddhist statue found at Sempaga"),
        location=[-2.316840, 119.128122],
        ref="p. 28",
    ),
    Label(
        type="city",
        name=colon("Yava", "Hastināpura prince, Deva-varman?"),
        location=[-6.455765, 110.771262],
        ref="p. 33",
    ),
]
for label in colonies_SEA:
    label.css = css_colony | label.css
    label.css_bullet = css_colony_bullet | label.css_bullet
    label.ref = (
        f"RC Majumdar, Ancient Indian Colonization in South-East Asia. {label.ref}"
    )

all_labels_SEA = general_labels_SEA + ports_SEA + colonies_SEA

ports_OTHER = [
    Label(
        type="city",
        name="Dvīpa Sukhadara",
        location=[12.486956, 53.826729],
    ),
    Label(
        type="city",
        name="Romā",
        location=[41.887902, 12.516424],
    ),
    Label(
        type="city",
        name="Gaṅgana/Kāliyadvīpa",
        location=[-6.109298, 39.423733],
        ref="p. 133",
    ),
    Label(
        type="city", name="Apāragaṅgana", location=[-7.462715, 39.326029], ref="p. 133"
    ),
    Label(
        type="city",
        name="Alassaṇḍa/<br>Yavanapura",
        location=[31.210757, 29.919430],
        ref="p. 133",
    ),
    Label(type="city", name="Barbara?", location=[10.438412, 45.012126]),
    Label(type="city", name="Antākhī", location=[36.209129, 36.178443], ref="p. xiv"),
    Label(type="city", name="Bāveru", location=[32.519873, 44.423970]),
    # funny thing AI came up with, not real:
    # Label(
    #     type="city",
    #     name="Kālakācārya",
    #     location=[-0.789275, 36.428155]
    # ),
]
for label in ports_OTHER:
    label.css = css_port | label.css
    label.css_bullet = css_port_bullet | label.css_bullet
    label.ref = f"Moti Chandra, Trade and Trade Routes in Ancient India. {label.ref}"

general_labels_OTHER = [
    Label(
        type="custom_label",
        name="Pārasīka",
        location=[29.244868, 51.597872],
        css={"transform": "rotate(45deg)"},
    ),
    Label(
        type="custom_label",
        name="Khuramāla Sea/<br>Pārasavāsa Sea",
        location=[26.191326, 52.671155],
        css={"transform": "rotate(38deg)"},
        ref="p. 61",
    ),
    Label(
        type="custom_label",
        name="Dadhimāla Sea",
        location=[20.083571, 38.700488],
        css={"transform": "rotate(60deg)"},
        ref="p. 61, 63",
    ),
    Label(
        type="custom_label",
        name="Agnimāla Sea",
        location=[12.332840, 47.519639],
        css={"transform": "rotate(-20deg)"},
        ref="p. 61, 63",
    ),
    Label(
        type="custom_label",
        name="Marukāntāra Desert",
        location=[18.953132, 35.475510],
        css={"transform": "rotate(60deg)"},
        ref="p. 61, 63",
    ),
    Label(
        type="custom_label",
        name=colon("Nīlakuṣamāla?", "(Suez gulf)"),
        location=[28.576944, 33.147515],
        css={"font-size": "0.85em", "line-height": "1"},
        ref="p. 61, 63",
    ),
    Label(
        type="custom_label",
        name=colon("Nalamāla?", "(old Suez canal)"),
        location=[31.094234, 32.296720],
        css={"transform": "rotate(10deg)", "font-size": "0.85em", "line-height": "1"},
        ref="p. 61, 63",
    ),
    Label(
        type="custom_label",
        name="Yavana",
        location=[39.134265, 21.801574],
        ref="p. 133",
    ),
    Label(
        type="custom_label",
        name="Parama-yavana",
        location=[38.453380, 29.463347],
        ref="p. 133",
    ),
    Label(
        type="custom_label",
        name="Roma-Viṣaya",
        location=[43.347301, 11.792144],
    ),
    Label(
        type="custom_label",
        name="Valabhāmukha Sea",
        location=[35.392349, 19.468104],
        ref="p. 61, 63",
    ),
    Label(
        type="custom_label",
        name="Yavana",
        location=[33.964831, 27.000472],
        css={"font-size": "18pt"},
    ),
    Label(
        type="custom_label",
        name="Jambudvīpa",
        location=[21.407506, 78.480723],
        css={"font-size": "24pt", "color": "#333333"},
    ),
    Label(
        type="custom_label",
        name="Cīnā",
        location=[30.750277, 114.330864],
        css={"font-size": "18pt"},
    ),
    Label(
        type="custom_label",
        name="Kālayavana?",
        location=[10.068956, 38.311893],
        css={"font-size": "18pt", "transform": "rotate(45deg)"},
    ),
]
for label in general_labels_OTHER:
    label.css = css_general | label.css
    label.ref = f"Moti Chandra, Trade and Trade Routes in Ancient India. {label.ref}"

all_labels_OTHER = general_labels_OTHER + ports_OTHER
all_labels_ports = ports_SEA + ports_OTHER + general_labels_SEA + general_labels_OTHER
all_labels = all_labels_SEA + all_labels_OTHER

css_port_full = css_str(Label.css_default["city"] | css_port)
css_port_bullet_full = css_str(Label.css_default["city_bullet"] | css_port_bullet)
css_colony_full = css_str(Label.css_default["city"] | css_colony)
css_colony_bullet_full = css_str(Label.css_default["city_bullet"] | css_colony_bullet)
example_port_html = (
    f'<div style="{css_port_full}">'
    f'<span style="{css_port_bullet_full}"></span>'
    f"Cities and ports mentioned in Indian literature"
    f"</div>"
)
example_colony_html = (
    f'<div style="{css_colony_full}">'
    f'<span style="{css_colony_bullet_full}"></span>'
    f"Capitals of Indian(-ized) states known from local or Chinese history"
    f"</div>"
)

EARLY_SUVARNABHUMI = FlagMap(
    flags=flags,
    loka=Loka.SEA,
    custom_labels=all_labels_SEA,
    custom_html=(
        "Earliest recorded Indian colonies and states in Southeast Asia, c. 1st and 2nd centuries."
        "<br><br>" + example_port_html + "<br>" + example_colony_html + "<br>"
        "<b>Sources:</b><br>"
        "RC Majumdar (1979), <i>Ancient Indian colonization in Southeast Asia.</i> p. 20-33.<br>"
        "Moti Chandra (1977), <i>Trade and Trade Routes in Ancient India.</i> p. 132-133, xiv"
    ),
    labels_on_map=False,
    drop_orphans=True,
    base_maps=(
        ["Esri.WorldPhysical"],
        ["OpenStreetMap", "CartoDB.Positron", "Esri.WorldImagery", "OpenTopoMap"],
    ),
    # css_legend={"height": "275px"},
)

flags_sea_route = [
    Flag(name="MEDITERRANEAN", matcher=MEDITERRANEAN),
    Flag(name="GULF", matcher=GULF),
    Flag(name="AFRICA_EAST_SPOTTY", matcher=AFRICA_EAST_SPOTTY),
    Flag(name="LEVANT", matcher=LEVANT),
    Flag(name="IRANIC", matcher=IRANIC),
    Flag(name="SUBCONTINENT_PROPER", matcher=SUBCONTINENT_PROPER),
    Flag(name="SEA", matcher=SEA),
]

custom_colors_sea_route = {"SUBCONTINENT_PROPER": "#444444"}  # mainland India

SEA_ROUTES = FlagMap(
    flags=flags_sea_route,
    loka=Loka.INDIAN_OCEAN,
    custom_labels=all_labels,
    custom_colors=custom_colors_sea_route,
    labels_on_map=False,
    drop_orphans=True,
    custom_html=(
        "Sea routes of India < 300 AD.<br><br>"
        "<b>Sources:</b><br>"
        "Moti Chandra (1977), <i>Trade and Trade Routes in Ancient India.</i> p. 61-63"
    ),
    base_maps=(
        ["Esri.WorldPhysical"],
        ["OpenStreetMap", "CartoDB.Positron", "Esri.WorldImagery", "OpenTopoMap"],
    ),
    zoom_start=4,
)
