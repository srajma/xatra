from xatra.maps.FlagMap import Flag, FlagMap, Path, Label
from xatra.matchers import *
from xatra.data import Loka, Varuna
from xatra.maps.nations import INDIAN_SUBCONTINENT

CITIES = {
    "Delhi": Label(type="city", name="Delhi", location=[28.7041, 77.1025]),
    "Mumbai": Label(type="city", name="Mumbai", location=[19.0760, 72.8777]),
    "Kolkata": Label(type="city", name="Kolkata", location=[22.5726, 88.3639]),
    "Chennai": Label(type="city", name="Chennai", location=[13.0827, 80.2707]),
    "Bangalore": Label(type="city", name="Bangalore", location=[12.9716, 77.5946]),
    "Hyderabad": Label(type="city", name="Hyderabad", location=[17.3850, 78.4867]),
    "Pune": Label(type="city", name="Pune", location=[18.5204, 73.8567]),
    "Ahmedabad": Label(type="city", name="Ahmedabad", location=[23.0225, 72.5714]),
    "Ranchi": Label(type="city", name="Ranchi", location=[23.3441, 85.3096]),
    "Jaipur": Label(type="city", name="Jaipur", location=[26.9124, 75.7873]),
    "Surat": Label(type="city", name="Surat", location=[21.1702, 72.8311]),
    "Lucknow": Label(type="city", name="Lucknow", location=[26.8467, 80.9462]),
    "Kanpur": Label(type="city", name="Kanpur", location=[26.4499, 80.3319]),
    "Kannauj": Label(type="city", name="Kannauj", location=[27.0551, 79.9133]),
    "Prayagraj": Label(type="city", name="Prayagraj", location=[25.4358, 81.8463]),
    "Nagpur": Label(type="city", name="Nagpur", location=[21.1458, 79.0882]),
    "Gondia": Label(type="city", name="Gondia", location=[21.4602, 80.1920]),
    "Patna": Label(type="city", name="Patna", location=[25.5941, 85.1376]),
    "Indore": Label(type="city", name="Indore", location=[22.7196, 75.8577]),
    "Bhopal": Label(type="city", name="Bhopal", location=[23.2599, 77.4126]),
    "Ludhiana": Label(type="city", name="Ludhiana", location=[30.9010, 75.8573]),
    "Agra": Label(type="city", name="Agra", location=[27.1767, 78.0081]),
    "Pryagraj": Label(type="city", name="Pryagraj", location=[25.4358, 81.8463]),
    "Varanasi": Label(type="city", name="Varanasi", location=[25.3176, 82.9739]),
    "Ayodhya": Label(type="city", name="Ayodhya", location=[26.7925, 82.1942]),
    "Vadodara": Label(type="city", name="Vadodara", location=[22.3072, 73.1812]),
    "Nashik": Label(type="city", name="Nashik", location=[20.0059, 73.7910]),
    "Aurangabad": Label(type="city", name="Aurangabad", location=[19.8762, 75.3433]),
    "Amaravati": Label(type="city", name="Amaravati", location=[20.9331, 77.7519]),
    "Udaipur": Label(type="city", name="Udaipur", location=[24.5854, 73.7125]),
    "Ajmer": Label(type="city", name="Ajmer", location=[26.4499, 74.6399]),
    "Amritsar": Label(type="city", name="Amritsar", location=[31.6340, 74.8723]),
    "Chandigarh": Label(type="city", name="Chandigarh", location=[30.7333, 76.7794]),
    "Coimbatore": Label(type="city", name="Coimbatore", location=[11.0168, 76.9558]),
    "Goa": Label(type="city", name="Goa", location=[15.2993, 74.1240]),
    "Mangalore": Label(type="city", name="Mangalore", location=[12.9141, 74.8560]),
    "Madurai": Label(type="city", name="Madurai", location=[9.9252, 78.1198]),
    "Kochi": Label(type="city", name="Kochi", location=[9.9312, 76.2673]),
    "Visakhapatnam": Label(
        type="city", name="Visakhapatnam", location=[17.6868, 83.2185]
    ),
    "Ongole": Label(type="city", name="Ongole", location=[15.9129, 80.1529]),
    "Nellore": Label(type="city", name="Nellore", location=[14.4426, 79.9865]),
    "Tanjore": Label(type="city", name="Tanjore", location=[10.7867, 79.1378]),
    "Bhubaneswar": Label(type="city", name="Bhubaneswar", location=[20.2961, 85.8245]),
    "Thiruvananthapuram": Label(
        type="city", name="Thiruvananthapuram", location=[8.5241, 76.9366]
    ),
    "Vijayawada": Label(type="city", name="Vijayawada", location=[16.5062, 80.6480]),
    "Jodhpur": Label(type="city", name="Jodhpur", location=[26.2389, 73.0243]),
    "Raipur": Label(type="city", name="Raipur", location=[21.2514, 81.6296]),
    "Kota": Label(type="city", name="Kota", location=[25.2138, 75.8648]),
    "Guwahati": Label(type="city", name="Guwahati", location=[26.1445, 91.7362]),
    "Jabalpur": Label(type="city", name="Jabalpur", location=[23.1815, 79.9864]),
    "Gwalior": Label(type="city", name="Gwalior", location=[26.2183, 78.1828]),
    "Bikaner": Label(type="city", name="Bikaner", location=[28.0229, 73.3119]),
    "Kolhapur": Label(type="city", name="Kolhapur", location=[16.7050, 74.2433]),
    "Akola": Label(type="city", name="Akola", location=[20.7096, 77.0022]),
    "Solapur": Label(type="city", name="Solapur", location=[17.6599, 75.9064]),
    "Hubli": Label(type="city", name="Hubli", location=[15.3647, 75.1240]),
    "Belgaum": Label(type="city", name="Belgaum", location=[15.8497, 74.4977]),
    "Davangere": Label(type="city", name="Davangere", location=[14.4644, 75.9218]),
    "Mysore": Label(type="city", name="Mysore", location=[12.2958, 76.6394]),
    "Gulbarga": Label(type="city", name="Gulbarga", location=[17.3850, 76.4797]),
    "Shimoga": Label(type="city", name="Shimoga", location=[13.9299, 75.5681]),
    "Tumkur": Label(type="city", name="Tumkur", location=[13.3409, 77.1010]),
    "Dhanbad": Label(type="city", name="Dhanbad", location=[23.7957, 86.4304]),
    "Muzaffarpur": Label(type="city", name="Muzaffarpur", location=[26.1209, 85.3647]),
    "Darbhanga": Label(type="city", name="Darbhanga", location=[26.1524, 85.8971]),
    "Purnia": Label(type="city", name="Purnia", location=[25.7781, 87.4700]),
    "Gaya": Label(type="city", name="Gaya", location=[24.7964, 85.0070]),
    "Bhagalpur": Label(type="city", name="Bhagalpur", location=[25.2445, 86.9718]),
    "Kishanganj": Label(type="city", name="Kishanganj", location=[26.1119, 87.9563]),
    "Rae Bareli": Label(type="city", name="Rae Bareli", location=[26.2301, 81.2409]),
    "Jammu": Label(type="city", name="Jammu", location=[32.7266, 74.8570]),
    "Pathankot": Label(type="city", name="Pathankot", location=[32.2746, 75.6527]),
    "Jalandhar": Label(type="city", name="Jalandhar", location=[31.3260, 75.5762]),
    "Ambala": Label(type="city", name="Ambala", location=[30.3753, 76.7821]),
    "Vidisha": Label(type="city", name="Vidisha", location=[23.5260, 77.8210]),
}
"""City co-ordinates"""

### MUMBAI - DELHI LINE ###

MUMBAI_AHMEDBAD = Path(
    name="MUMBAI DELHI LINE",
    points=[CITIES["Mumbai"], CITIES["Surat"], CITIES["Vadodara"], CITIES["Ahmedabad"]],
)
AHMEDABAD_DELHI = Path(
    name="MUMBAI DELHI LINE",
    points=[
        CITIES["Ahmedabad"],
        CITIES["Udaipur"],
        CITIES["Ajmer"],
        CITIES["Jaipur"],
        CITIES["Delhi"],
    ],
)
MUMBAI_DELHI = MUMBAI_AHMEDBAD.add(AHMEDABAD_DELHI)

### DEHATI BACHAO DEHATI PADHAO LINE ###

JAMMU_DELHI = Path(
    name="DEHATI BACHAO DEHATI PADHAO LINE",
    points=[
        CITIES["Jammu"],
        CITIES["Pathankot"],
        CITIES["Amritsar"],
        CITIES["Jalandhar"],
        CITIES["Ludhiana"],
        CITIES["Chandigarh"],
        CITIES["Ambala"],
        CITIES["Delhi"],
    ],
)
DELHI_PATNA = Path(
    name="DEHATI BACHAO DEHATI PADHAO LINE",
    points=[
        CITIES["Delhi"],
        CITIES["Agra"],
        CITIES["Kannauj"],
        CITIES["Kanpur"],
        CITIES["Rae Bareli"],
        CITIES["Prayagraj"],
        CITIES["Varanasi"],
        CITIES["Patna"],
    ],
)
PATNA_KOLKATA = Path(
    name="DEHATI BACHAO DEHATI PADHAO LINE",
    points=[CITIES["Patna"], CITIES["Gaya"], CITIES["Dhanbad"], CITIES["Kolkata"]],
)
DEHATI_LINE = JAMMU_DELHI.add(DELHI_PATNA).add(PATNA_KOLKATA)
LUCKNOW_EXT = Path(
    name="DEHATI BACHAO DEHATI PADHAO LINE",
    points=[CITIES["Kanpur"], CITIES["Lucknow"]],
)
AYODHYA_EXT = Path(
    name="DEHATI BACHAO DEHATI PADHAO LINE",
    points=[CITIES["Prayagraj"], CITIES["Ayodhya"]],
)
BIHAR_EXT = Path(
    name="DEHATI BACHAO DEHATI PADHAO LINE",
    points=[
        CITIES["Patna"],
        CITIES["Muzaffarpur"],
        CITIES["Darbhanga"],
        CITIES["Purnia"],
        CITIES["Kishanganj"],
    ],
)

### AKARAVANTI REWARD LINE ###

AKARAVANTI = Path(
    name="AKARAVANTI REWARD LINE",
    points=[
        CITIES["Vadodara"],
        CITIES["Indore"],
        CITIES["Bhopal"],
        CITIES["Vidisha"],
        CITIES["Jabalpur"],
    ],
)
AKARAVANTI_EXT_DAKSHINAPATHA = Path(
    name="AKARAVANTI REWARD LINE",
    points=[CITIES["Gondia"], CITIES["Jabalpur"], CITIES["Varanasi"]],
)

### MUMBAI - NAGPUR LINE ###

MUMBAI_NAGPUR = Path(
    name="MUMBAI NAGPUR LINE",
    points=[
        CITIES["Mumbai"],
        CITIES["Nashik"],
        CITIES["Aurangabad"],
        CITIES["Amaravati"],
        CITIES["Nagpur"],
        CITIES["Gondia"],
    ],
)

### MUMBAI - BANGALORE LINE ###

MUMBAI_BANGALORE = Path(
    name="MUMBAI BANGALORE LINE",
    points=[
        CITIES["Mumbai"],
        CITIES["Pune"],
        CITIES["Kolhapur"],
        CITIES["Belgaum"],
        CITIES["Hubli"],
        CITIES["Bangalore"],
    ],
)

### MUMBAI - HYDERABAD LINE ###

MUMBAI_HYDERABAD = Path(
    name="MUMBAI HYDERABAD LINE",
    points=[
        CITIES["Pune"],
        CITIES["Solapur"],
        CITIES["Gulbarga"],
        CITIES["Hyderabad"],
    ],
)

### BANGALORE - HYDERABAD LINE ###

BANGALORE_HYDERABAD = Path(
    name="BANGALORE HYDERABAD LINE",
    points=[CITIES["Bangalore"], CITIES["Hyderabad"]],
)

### MOOLNIVASI REWARD LINE ###

MOOLNIVASI = Path(
    name="MOOLNIVASI REWARD LINE",
    points=[
        CITIES["Gondia"],
        CITIES["Raipur"],
        CITIES["Ranchi"],
        CITIES["Dhanbad"],
    ],
)

### EAST COAST REWARD LINE ###

EAST_COAST = Path(
    name="EAST COAST REWARD LINE",
    points=[
        CITIES["Kolkata"],
        CITIES["Bhubaneswar"],
        CITIES["Visakhapatnam"],
        CITIES["Vijayawada"],
        CITIES["Ongole"],
        CITIES["Nellore"],
        CITIES["Chennai"],
    ],
)
EAST_COAST_EXT_HYDERABAD = Path(
    name="EAST COAST REWARD LINE",
    points=[CITIES["Vijayawada"], CITIES["Hyderabad"]],
)

### WEST COAST REWARD LINE ###

WEST_COAST = Path(
    name="WEST COAST REWARD LINE",
    points=[
        CITIES["Mumbai"],
        CITIES["Goa"],
        CITIES["Mangalore"],
    ],
)

### BANGALORE - MANGALORE LINE ###

BANGALORE_MANGALORE = Path(
    name="BANGALORE MANGALORE LINE",
    points=[CITIES["Bangalore"], CITIES["Mysore"], CITIES["Mangalore"]],
)

### KERALA LINE ###

KERALA = Path(
    name="KERALA LINE",
    points=[
        CITIES["Mangalore"],
        CITIES["Kochi"],
        CITIES["Thiruvananthapuram"],
    ],
)

### BANGALORE - CHENNAI LINE ###

BANGALORE_CHENNAI = Path(
    name="BANGALORE CHENNAI LINE",
    points=[CITIES["Bangalore"], CITIES["Chennai"]],
)

### TAMIL LINE ###

TAMIL = Path(
    name="TAMIL LINE",
    points=[
        CITIES["Chennai"],
        CITIES["Tanjore"],
        CITIES["Madurai"],
        CITIES["Thiruvananthapuram"],
    ],
)

### BANGALORE - KERALA LINE ###

BANGALORE_KERALA = Path(
    name="BANGALORE KERALA LINE",
    points=[CITIES["Bangalore"], CITIES["Coimbatore"], CITIES["Kochi"]],
)

### HYDERABAD-NAGPUR LINE ###

HYDERABAD_NAGPUR = Path(
    name="HYDERABAD NAGPUR LINE",
    points=[CITIES["Hyderabad"], CITIES["Nagpur"]],
)

####################

# add options to each path

PATHS = [
    MUMBAI_DELHI,
    DEHATI_LINE,
    LUCKNOW_EXT,
    AYODHYA_EXT,
    BIHAR_EXT,
    AKARAVANTI,
    AKARAVANTI_EXT_DAKSHINAPATHA,
    MUMBAI_NAGPUR,
    MUMBAI_BANGALORE,
    MUMBAI_HYDERABAD,
    BANGALORE_HYDERABAD,
    MOOLNIVASI,
    EAST_COAST,
    EAST_COAST_EXT_HYDERABAD,
    WEST_COAST,
    BANGALORE_MANGALORE,
    KERALA,
    BANGALORE_CHENNAI,
    TAMIL,
    BANGALORE_KERALA,
    # HYDERABAD_NAGPUR,
]

tooltips = {
    "MUMBAI DELHI LINE": "<b>Mumbai-Delhi line.</b>",
    "DEHATI BACHAO DEHATI PADHAO LINE": (
        "<p><b>Dehati Bachao Dehati Padhao line:</b></p>"
        "Pump UP-Bihar bros into Kashmir, Punjab, WB <br>"
        "to break caste cartels on both sides. Make <br>"
        "every caste a micro-minority so they only <br>"
        "have Hindutva to turn to."
    ),
    "AKARAVANTI REWARD LINE": (
        "<p><b>Akaravanti reward line:</b></p>"
        "Line from Vadodara to Varanasi.<br>"
        "Rewards MP for its loyalty and <br>"
        "cosmopolitanizes Purvanchal."
    ),
    "MUMBAI NAGPUR LINE": (
        "<p><b>Mumbai-Nagpur line:</b></p>"
        "Prevent caste cartels from forming in<br>"
        "the interior of Maharashtra by <br>"
        "connecting them to Mumbai. Also<br>"
        "cosmopolitanize Nagpur by pumping<br>"
        "in Moolnivasis and MP people."
    ),
    "MUMBAI BANGALORE LINE": (
        "<p><b>Mumbai-Bangalore line:</b></p>"
        "Reward Karnataka for its loyalty<br>"
        "and rejuvenate the North Karnataka<br>"
        "heartland. Connect Tier-2 cities with<br>"
        "potential, like Hubli-Dharward and<br>Belgaum."
    ),
    "EAST COAST REWARD LINE": (
        "<p><b>East coast reward line:</b></p>"
        "Reward Odisha and Andhra for their<br>"
        "loyalty, and connect Kolkata to Chennai<br>"
        "to cosmopolitanize the whole east coast."
    ),
    "WEST COAST REWARD LINE": "<b>Konkan line.</b>",
    "MUMBAI HYDERABAD LINE": (
        "<p><b>Mumbai-Hyderabad line:</b></p>"
        "Cosmopolitanize Marathwada and <br>"
        "rejuvenate North Karnataka."
    ),
    "BANGALORE HYDERABAD LINE": (
        "<p><b>Bangalore-Hyderabad line:</b></p>"
        "Connect the two biggest IT hubs in the South."
    ),
    "MOOLNIVASI REWARD LINE": (
        "<p><b>Moolnivasi reward line:</b></p>"
        "Reward Chhattisgarh and Jharkhand for <br>"
        "their loyalty, and cosmopolitanize the <br>"
        "tribal belt."
    ),
    "KERALA LINE": "<b>Kerala line.</b>",
    "BANGALORE CHENNAI LINE": "<b>Bangalore-Chennai line.</b>",
    "TAMIL LINE": "<b>Tamil line.</b>",
    "BANGALORE KERALA LINE": (
        "<p><b>Bangalore-Kerala line:</b></p>"
        "Let people live in Kerala or Coimbatore<br>"
        "and work in Bangalore."
    ),
    "HYDERABAD NAGPUR LINE": "<b>Hyderabad-Nagpur line.</b>",
    "BANGALORE MANGALORE LINE": (
        "<p><b>Bangalore-Mangalore line:</b></p>"
        "Let people live in Mangalore and work in Bangalore."
    ),
}

PATHS_ECON = [
    # All the blue lines
    "MUMBAI DELHI LINE",
    "MUMBAI HYDERABAD LINE",
    "BANGALORE HYDERABAD LINE",
    "WEST COAST REWARD LINE",
    "BANGALORE MANGALORE LINE",
]
PATHS_COSMO = [
    # All the green lines
    "DEHATI BACHAO DEHATI PADHAO LINE",
    "MUMBAI NAGPUR LINE",
    "HYDERABAD NAGPUR LINE",
]
PATHS_REWARD = [
    # All the red lines
    "AKARAVANTI REWARD LINE",
    "MUMBAI BANGALORE LINE",
    "MOOLNIVASI REWARD LINE",
    "EAST COAST REWARD LINE",
]
PATHS_CARROT = [
    # All the black lines
    "KERALA LINE",
    "BANGALORE CHENNAI LINE",
    "TAMIL LINE",
    "BANGALORE KERALA LINE",
]
PATHS_OPTIONAL = [
    # All the dashed lines
    "MUMBAI HYDERABAD LINE",
    "BANGALORE HYDERABAD LINE",
    "MOOLNIVASI REWARD LINE",
    "WEST COAST REWARD LINE",
    "BANGALORE MANGALORE LINE",
    "KERALA LINE",
    "BANGALORE CHENNAI LINE",
    "TAMIL LINE",
    "BANGALORE KERALA LINE",
    "HYDERABAD NAGPUR LINE",
]


for path in PATHS:
    # path.options |= options.get(path.name, {})
    if path.name in PATHS_ECON:
        path.options |= {"color": "blue"}
    if path.name in PATHS_COSMO:
        path.options |= {"color": "green"}
    if path.name in PATHS_REWARD:
        path.options |= {"color": "red"}
    if path.name in PATHS_CARROT:
        path.options |= {"color": "black"}
    if path.name in PATHS_OPTIONAL:
        path.options |= {"dash_array": "5, 5", "opacity": 0.4} # "weight": 1.4
    path.options |= {"tooltip": tooltips.get(path.name, None)}

HSR = FlagMap(
    flags=[],
    loka=Loka.INDIAN_SUBCONTINENT,
    varuna=Varuna.INDIAN_SUBCONTINENT,
    paths=PATHS,
    custom_html=(
        "<p><b>High-speed rail network to BVILD</b></p>"
        "<p><span style='color: blue; font-weight: bold'>Blue:</span> Economic lines</p>"
        "<p><span style='color: green; font-weight: bold'>Green:</span> Cosmopolitanization / Caste-cartel breaking lines</p>"
        "<p><span style='color: red; font-weight: bold'>Red: </span> Loyalist rewarding lines<br></p>"
        "<p><span style='color: black; font-weight: bold'>Black: </span>Carrot lines (to be built after winning these places)</p>"
        "<p>Thick lines are the bare minimum. Dashed lines are still very desirable.</p>"
        "<p><b>Hover over each line</b> to see its name and purpose.</p>"
    ),
    opacity=0.3,
    show_loka=False,
    show_varuna=False,
)
