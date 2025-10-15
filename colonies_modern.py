#!/usr/bin/env python3
"""
A modern translation of the old xatra colonies map.
Shows early Indian colonies in Suvarnabhumi (Southeast Asia) in the 1st-2nd centuries.
"""

import xatra
from xatra import Icon
from xatra.loaders import gadm

def colon(name, desc=None):
    """Helper function to format colony names with descriptions."""
    if desc:
        return f"{name}<br><span style='font-size: 0.7em'>{desc}</span>"
    else:
        return name

# Create the Southeast Asia colonies map
def create_sea_colonies_map():
    map = xatra.Map()
    
    # Base map options
    map.BaseOption("Esri.WorldPhysical", default=True)
    map.BaseOption("OpenStreetMap")
    map.BaseOption("CartoDB.Positron")
    map.BaseOption("Esri.WorldImagery")
    map.BaseOption("OpenTopoMap")
    
    # Add some basic territorial context
    map.Flag(label="India", value=gadm("IND"), note="Indian subcontinent")
    
    # General labels for Southeast Asia
    general_labels = [
        ("Yāva", [110.0, -7.3]),
        ("Karpūradvīpa/<br>Barhiṇadvīpa", [114.0, 0.0]),
        ("Kaṭāha", [100.3, 6.0]),
        ("Dvīpāntara", [106.9, 0.0]),
        ("Suvarṇabhūmi", [107.823257, 6.053218]),
    ]
    
    for name, position in general_labels:
        map.Text(label=name, position=position, classes="general-label")
    
    # Ports mentioned in Indian literature (black squares)
    ports = [
        ("Takkasilā", [92.40, 20.70], "p. 132"),
        ("Kālamukha", [93.50, 19.71], "p. 132"),
        ("Vesuṅga", [96.18, 16.81], "p. 132"),
        ("Verāpatha", [98.19, 14.09], "p. 132"),
        ("Takkola", [98.27, 8.89], "p. 132"),
        ("Tāṁbraliṅga", [103.33, 3.80], "p. 132"),
        ("Vaṅga", [106.15, -2.36], "p. 133"),
        ("Ailavaddhana", [117.21, -8.50], "p. 133"),
        ("Suvarṇakūṭa", [103.08, 11.46], "p. 133"),
        ("Kamalapura", [103.68, 11.07], "p. xiv"),
        ("Samudrapaṭṭaṇa", [100.35, -0.91], "p. 141"),
    ]
    
    # Create port icon
    port_icon = Icon.builtin("port.svg", icon_size=(20, 20), icon_anchor=(10, 10))
    
    for name, position, ref in ports:
        note = f"Moti Chandra, Trade and Trade Routes in Ancient India. {ref}"
        map.Point(label=name, position=position, icon=port_icon, classes="port", note=note)
    
    # Colonies - capitals of Indian(-ized) states (blue circles)
    colonies = [
        (colon("Suddhamāvati/Thaton", "Telugu explorers or Tissa's son"), [96.47, 17.33], "p. 31"),
        (colon("Saṅkissa/Tagaung", "Abhirāja"), [96.0, 23.5], "p. 31"),
        (colon("Śrīkṣetra/Pyu", "under Saṅkissa"), [95.29, 18.81], "p. 31"),
        (colon("Dhaññavatī/Arakanese", "under Saṅkissa"), [93.06, 20.87], "p. 31"),
        (colon("Vyādhapura/Funan", "Kauṇḍinya I"), [104.98, 11.00], "p. 20"),
        (colon("Kīrtinagara/Oc Eo", "under Vyādhapura"), [105.147056, 10.249203], "p. 21"),
        (colon("Tien-Suen", "under Vyādhapura"), [99.329105, 9.196281], "p. 21"),
        (colon("Kambuja", "Kambu Swayambhuva/Indraprastha prince"), [105.868371, 14.901246], "p. 24"),
        (colon("Campa", "Śrī Māra"), [108.131374, 16.196377], "p. 25"),
        (colon("Langkasuka", "Mauryan prince?"), [101.307032, 6.759206], "p. 28"),
        (colon("??", "Amarāvati-style Buddhist statue found at Sempaga"), [119.128122, -2.316840], "p. 28"),
        (colon("Yava", "Hastināpura prince, Deva-varman?"), [110.771262, -6.455765], "p. 33"),
    ]
    
    # Create city icon for colonies
    city_icon = Icon.builtin("city.png", icon_size=(20, 20), icon_anchor=(10, 10))
    
    for name, position, ref in colonies:
        note = f"RC Majumdar, Ancient Indian Colonization in South-East Asia. {ref}"
        map.Point(label=name, position=position, icon=city_icon, classes="colony", note=note)
    
    # Title and legend
    map.TitleBox("""
    <b>Earliest recorded Indian colonies and states in Southeast Asia</b><br>
    c. 1st and 2nd centuries<br><br>
    <div style="display: flex; align-items: center; margin: 5px 0;">
        <span style="display: inline-block; width: 20px; height: 20px; background: black; margin-right: 10px;"></span>
        Cities and ports mentioned in Indian literature
    </div>
    <div style="display: flex; align-items: center; margin: 5px 0;">
        <span style="display: inline-block; width: 20px; height: 20px; background: blue; border-radius: 50%; margin-right: 10px;"></span>
        Capitals of Indian(-ized) states known from local or Chinese history
    </div><br>
    <b>Sources:</b><br>
    RC Majumdar (1979), <i>Ancient Indian colonization in Southeast Asia.</i> p. 20-33.<br>
    Moti Chandra (1977), <i>Trade and Trade Routes in Ancient India.</i> p. 132-133, xiv
    """)
    
    # CSS styling
    map.CSS("""
    .general-label {
        color: #666666;
        text-transform: uppercase;
        font-weight: bold;
        font-size: 14px;
    }
    
    .port {
        /* Port styling handled by icon */
    }
    
    .colony {
        /* Colony styling handled by icon */
    }
    
    #title {
        background: rgba(255, 255, 255, 0.95);
        border: 1px solid #ccc;
        padding: 12px 16px;
        border-radius: 8px;
        max-width: 500px;
        font-size: 14px;
        line-height: 1.4;
    }
    """)
    
    return map

# Create the sea routes map
def create_sea_routes_map():
    map = xatra.Map()
    
    # Base map options
    map.BaseOption("Esri.WorldPhysical", default=True)
    map.BaseOption("OpenStreetMap")
    map.BaseOption("CartoDB.Positron")
    map.BaseOption("Esri.WorldImagery")
    map.BaseOption("OpenTopoMap")
    
    # Add territorial context
    map.Flag(label="Mediterranean", value=gadm("GRC") | gadm("TUR") | gadm("EGY") | gadm("LBY"), note="Mediterranean region")
    map.Flag(label="Gulf", value=gadm("SAU") | gadm("ARE") | gadm("QAT") | gadm("BHR") | gadm("KWT"), note="Persian Gulf")
    map.Flag(label="East Africa", value=gadm("SOM") | gadm("ETH") | gadm("KEN") | gadm("TZA"), note="East African coast")
    map.Flag(label="Levant", value=gadm("SYR") | gadm("LBN") | gadm("ISR") | gadm("PSE"), note="Levant region")
    map.Flag(label="Iranic", value=gadm("IRN") | gadm("AFG"), note="Iranic region")
    map.Flag(label="Indian Subcontinent", value=gadm("IND") | gadm("PAK") | gadm("BGD") | gadm("LKA"), note="Indian subcontinent", color="#444444")
    map.Flag(label="Southeast Asia", value=gadm("THA") | gadm("VNM") | gadm("KHM") | gadm("LAO") | gadm("MMR") | gadm("MYS") | gadm("IDN") | gadm("PHL"), note="Southeast Asia")
    
    # Ports in other regions
    other_ports = [
        ("Dvīpa Sukhadara", [53.826729, 12.486956]),
        ("Romā", [12.516424, 41.887902]),
        ("Gaṅgana/Kāliyadvīpa", [39.423733, -6.109298], "p. 133"),
        ("Apāragaṅgana", [39.326029, -7.462715], "p. 133"),
        ("Alassaṇḍa/<br>Yavanapura", [29.919430, 31.210757], "p. 133"),
        ("Barbara?", [45.012126, 10.438412]),
        ("Antākhī", [36.178443, 36.209129], "p. xiv"),
        ("Bāveru", [44.423970, 32.519873]),
    ]
    
    # Create port icon
    port_icon = Icon.builtin("port.svg", icon_size=(16, 16), icon_anchor=(8, 8))
    
    for name, position, *ref in other_ports:
        note = f"Moti Chandra, Trade and Trade Routes in Ancient India. {ref[0] if ref else ''}"
        map.Point(label=name, position=position, icon=port_icon, classes="port", note=note)
    
    # General labels for other regions
    other_labels = [
        ("Pārasīka", [51.597872, 29.244868]),
        ("Khuramāla Sea/<br>Pārasavāsa Sea", [52.671155, 26.191326], "p. 61"),
        ("Dadhimāla Sea", [38.700488, 20.083571], "p. 61, 63"),
        ("Agnimāla Sea", [47.519639, 12.332840], "p. 61, 63"),
        ("Marukāntāra Desert", [35.475510, 18.953132], "p. 61, 63"),
        (colon("Nīlakuṣamāla?", "(Suez gulf)"), [33.147515, 28.576944], "p. 61, 63"),
        (colon("Nalamāla?", "(old Suez canal)"), [32.296720, 31.094234], "p. 61, 63"),
        ("Yavana", [21.801574, 39.134265], "p. 133"),
        ("Parama-yavana", [29.463347, 38.453380], "p. 133"),
        ("Roma-Viṣaya", [11.792144, 43.347301]),
        ("Valabhāmukha Sea", [19.468104, 35.392349], "p. 61, 63"),
        ("Yavana", [27.000472, 33.964831]),
        ("Jambudvīpa", [78.480723, 21.407506]),
        ("Cīnā", [114.330864, 30.750277]),
        ("Kālayavana?", [38.311893, 10.068956]),
    ]
    
    for name, position, *ref in other_labels:
        note = f"Moti Chandra, Trade and Trade Routes in Ancient India. {ref[0] if ref else ''}"
        map.Text(label=name, position=position, classes="general-label", note=note)
    
    # Title
    map.TitleBox("""
    <b>Sea routes of India < 300 AD</b><br><br>
    <b>Sources:</b><br>
    Moti Chandra (1977), <i>Trade and Trade Routes in Ancient India.</i> p. 61-63
    """)
    
    # CSS styling
    map.CSS("""
    .general-label {
        color: #666666;
        text-transform: uppercase;
        font-weight: bold;
        font-size: 12px;
    }
    
    .port {
        /* Port styling handled by icon */
    }
    
    #title {
        background: rgba(255, 255, 255, 0.95);
        border: 1px solid #ccc;
        padding: 12px 16px;
        border-radius: 8px;
        max-width: 400px;
        font-size: 14px;
        line-height: 1.4;
    }
    """)
    
    return map

if __name__ == "__main__":
    # Create and export the Southeast Asia colonies map
    print("Creating Southeast Asia colonies map...")
    sea_map = create_sea_colonies_map()
    sea_map.show(out_json="colonies_sea.json", out_html="colonies_sea.html")
    print("Southeast Asia colonies map exported to colonies_sea.html")
    
    # Create and export the sea routes map
    print("Creating sea routes map...")
    routes_map = create_sea_routes_map()
    routes_map.show(out_json="colonies_routes.json", out_html="colonies_routes.html")
    print("Sea routes map exported to colonies_routes.html")

