"""A map of _Nations_ (not states) of India and the Silk Road region
in the ancient period. Can be regarded as a first-order approximation,
roughly valid in the period between 800 BC and 800 AD."""

from .FlagMap import *
from .matchers import *
from xatra import raw_data

_flags = [
    Flag(name = "DARADA", matcher = DARADA), 
    Flag(name = "MARASA", matcher = LADAKH), 
    Flag(name = "KASHMIR_PROPER", matcher = KASHMIR_PROPER), 
    Flag(name = "DARVA", matcher = KASHMIR_MISC),
    Flag(name = "KASHMIR_TBC", matcher = KASHMIR_TBC),
    Flag(name = "INNER_KAMBOJA", matcher = INNER_KAMBOJA),
    Flag(name = "VARNU", matcher = PSEUDOSATTAGYDIA),
    Flag(name = "SINDH", matcher = SINDH),
    Flag(name = "GANDHARA_W", matcher = GANDHARA_W),
    Flag(name = "DOAB_IJ_N", matcher = DOAB_IJ_N),
    Flag(name = "DOAB_IJ_S", matcher = DOAB_IJ_S),
    Flag(name = "DOAB_JC", matcher = DOAB_JC),
    Flag(name = "DOAB_CR", matcher = DOAB_CR),
    Flag(name = "DOAB_RS_N", matcher = DOAB_RS_N),
    Flag(name = "DOAB_RS_C", matcher = DOAB_RS_C),
    Flag(name = "DOAB_RS_S", matcher = DOAB_RS_S),
    Flag(name = "TRIGARTA_PROPER", matcher = TRIGARTA_PROPER),
    Flag(name = "KUTCH", matcher = KUTCH),
    Flag(name = "SURASTRA", matcher = SURASTRA),
    Flag(name = "ANARTA", matcher = ANARTA),
    Flag(name = "LATA", matcher = LATA),
    Flag(name = "KUKURA", matcher = KUKURA),
    Flag(name = "MATSYA", matcher = MATSYA),
    Flag(name = "BRAHMAVARTA", matcher = BRAHMAVARTA),
    Flag(name = "KURU_PROPER", matcher = KURU_PROPER),
    Flag(name = "PANCALA_N", matcher = PANCALA_N),
    Flag(name = "PANCALA_S", matcher = PANCALA_S),
    Flag(name = "SURASENA", matcher = SURASENA),
    Flag(name = "VATSA", matcher = VATSA),
    Flag(name = "KOSALA", matcher = KOSALA),
    Flag(name = "KASI", matcher = KASI),
    Flag(name = "MALLA", matcher = MALLA),
    Flag(name = "VIDEHA", matcher = VIDEHA),
    Flag(name = "SAKYA", matcher = SAKYA),
    Flag(name = "LICCHAVI", matcher = LICCHAVI),
    Flag(name = "MAGADHA", matcher = MAGADHA),
    Flag(name = "AVANTI", matcher = AVANTI),
    Flag(name = "AKARA", matcher = AKARA),
    Flag(name = "DASARNA", matcher = DASARNA),
    Flag(name = "CEDI", matcher = CEDI),
    Flag(name = "PULINDA", matcher = PULINDA),
    Flag(name = "ANGA", matcher = ANGA),
    Flag(name = "GAUDA", matcher = GAUDA),
    Flag(name = "RADHA", matcher = RADHA),
    Flag(name = "SUHMA", matcher = SUHMA),
    Flag(name = "PUNDRA", matcher = PUNDRA),
    Flag(name = "VANGA", matcher = VANGA),
    Flag(name = "SAMATATA", matcher = SAMATATA),
    Flag(name = "LAUHITYA", matcher = LAUHITYA),
    Flag(name = "UTKALA", matcher = UTKALA),
    Flag(name = "KALINGA", matcher = KALINGA),
    Flag(name = "VIDARBHA", matcher = VIDARBHA),
    Flag(name = "RSIKA", matcher = RSIKA),
    Flag(name = "MULAKA", matcher = MULAKA),
    Flag(name = "ASMAKA", matcher = ASMAKA),
    Flag(name = "APARANTA", matcher = APARANTA),
    Flag(name = "KUNTALA", matcher = KUNTALA),
    Flag(name = "KADAMBA", matcher = KADAMBA),
    Flag(name = "GANGA", matcher = CAUVERIC),
    Flag(name = "MAHISAKA", matcher = MAHISAKA),
    Flag(name = "TELINGA", matcher = VENGI),
    Flag(name = "ALUPA", matcher = TULU),
    Flag(name = "CERA", matcher = CERA),
    Flag(name = "AY", matcher = AY),
    Flag(name = "EZHIMALA", matcher = EZHIMALA),
    Flag(name = "KANCI", matcher = KANCI),
    Flag(name = "COLA", matcher = COLA),
    Flag(name = "PANDYA", matcher = PANDYA),
    Flag(name = "KONGU", matcher = KONGU),
    Flag(name = "SIMHALA", matcher = SIMHALA),
    Flag(name = "GEDROSIA", matcher = BALOCH),
    Flag(name = "KAMBOJA", matcher = KAMBOJA),
    Flag(name = "MERU", matcher = MERU),
    Flag(name = "ZARANJ", matcher = ZARANJ),
    Flag(name = "KANDAHAR", matcher = KANDAHAR),
    Flag(name = "HERAT", matcher = HERAT),
    Flag(name = "MARGIANA", matcher = MARGIANA),
    Flag(name = "BACTRIA", matcher = BACTRIA),
    Flag(name = "SOGDIA_PROPER", matcher = SOGDIA_PROPER),
    Flag(name = "FERGHANA", matcher = FERGHANA),
    Flag(name = "KHWAREZM", matcher = KHWAREZM),
    Flag(name = "KASHGAR", matcher = KASHGAR),
    Flag(name = "KHOTAN", matcher = KHOTAN),
    Flag(name = "AGNI", matcher = AGNI),
    Flag(name = "AKSU", matcher = AKSU),
    Flag(name = "KUCHA", matcher = KUCHA),
    Flag(name = "ROURAN", matcher = ROURAN),
    Flag(name = "QIEMO", matcher = QIEMO),
    Flag(name = "KORLA", matcher = KORLA),
    Flag(name = "TURFAN", matcher = TURFAN),
    Flag(name = "COORG", matcher = COORG),
    Flag(name = "YYY_GREAT_FOREST", matcher = YYY_GREAT_FOREST),
    Flag(name = "YYY_KALAKAVANA", matcher = YYY_KALAKAVANA),
    Flag(name = "YYY_MARU", matcher = YYY_MARU),
    Flag(name = "YYY_NAIMISA", matcher = YYY_NAIMISA),
    Flag(name = "YYY_HIMALAYAN", matcher = YYY_HIMALAYAN),
    Flag(name = "ZZZ_BAYALU", matcher = ZZZ_BAYALU),
    Flag(name = "ZZZ_GREATER_PUNE", matcher = ZZZ_GREATER_PUNE),
    Flag(name = "ZZZ_HADOTI", matcher = ZZZ_HADOTI),
    Flag(name = "ZZZ_BIHAR_NORTHEAST", matcher = ZZZ_BIHAR_NORTHEAST),
    Flag(name = "ZZZ_BAHAWALPUR", matcher = ZZZ_BAHAWALPUR)
]

_custom_colors = {
    flag.name : '#444444' # grey these out
    for flag in _flags 
    if flag.name.startswith("YYY_")
    or flag.name.startswith("ZZZ_")}

indiaish = Map(
    flags = _flags, 
    geojson = raw_data.indiaish, 
    geojson_rivers = raw_data.indiaish_rivers, 
    custom_colors = _custom_colors)

silkrd = Map(
    flags = _flags, 
    geojson = raw_data.silkrd, 
    geojson_rivers = raw_data.silkrd_rivers + raw_data.afghanish_rivers, 
    custom_colors = _custom_colors,
    folium_init = "Meru")

world = Map(
    flags = _flags,
    geojson = raw_data.world,
    geojson_rivers = raw_data.world_rivers,
    custom_colors = _custom_colors,
    folium_init = "Brahmavarta")