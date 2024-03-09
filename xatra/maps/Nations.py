"""A map of _Nations_ (not states) of India and the Silk Road region
in the ancient period. Can be regarded as a first-order approximation,
roughly valid in the period between 800 BC and 800 AD."""

from xatra.maps.FlagMap import Flag, Map
from xatra.matchers import *
from xatra.data import Loka, Varuna


class NATIONS(Map):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @property
    def flags(self):
        return [
            Flag(name="DARADA", matcher=DARADA),
            Flag(name="MARASA", matcher=LADAKH),
            Flag(name="KASHMIR_PROPER", matcher=KASHMIR_PROPER),
            Flag(name="DARVA", matcher=KASHMIR_MISC),
            Flag(name="KASHMIR_TBC", matcher=KASHMIR_TBC),
            Flag(name="INNER_KAMBOJA", matcher=INNER_KAMBOJA),
            Flag(name="VARNU", matcher=PSEUDOSATTAGYDIA),
            Flag(name="SINDH", matcher=SINDH),
            Flag(name="GANDHARA_W", matcher=GANDHARA_W),
            Flag(name="DOAB_IJ_N", matcher=DOAB_IJ_N),
            Flag(name="DOAB_IJ_S", matcher=DOAB_IJ_S),
            Flag(name="DOAB_JC", matcher=DOAB_JC),
            Flag(name="DOAB_CR", matcher=DOAB_CR),
            Flag(name="DOAB_RS_N", matcher=DOAB_RS_N),
            Flag(name="DOAB_RS_C", matcher=DOAB_RS_C),
            Flag(name="DOAB_RS_S", matcher=DOAB_RS_S),
            Flag(name="TRIGARTA_PROPER", matcher=TRIGARTA_PROPER),
            Flag(name="KUTCH", matcher=KUTCH),
            Flag(name="SURASTRA", matcher=SURASTRA),
            Flag(name="ANARTA", matcher=ANARTA),
            Flag(name="LATA", matcher=LATA),
            Flag(name="KUKURA", matcher=KUKURA),
            Flag(name="MATSYA", matcher=MATSYA),
            Flag(name="BRAHMAVARTA", matcher=BRAHMAVARTA),
            Flag(name="KURU_PROPER", matcher=KURU_PROPER),
            Flag(name="PANCALA_N", matcher=PANCALA_N),
            Flag(name="PANCALA_S", matcher=PANCALA_S),
            Flag(name="SURASENA", matcher=SURASENA),
            Flag(name="VATSA", matcher=VATSA),
            Flag(name="KOSALA", matcher=KOSALA),
            Flag(name="KASI", matcher=KASI),
            Flag(name="MALLA", matcher=MALLA),
            Flag(name="VIDEHA", matcher=VIDEHA),
            Flag(name="SAKYA", matcher=SAKYA),
            Flag(name="LICCHAVI", matcher=LICCHAVI),
            Flag(name="MAGADHA", matcher=MAGADHA),
            Flag(name="TERAI", matcher=TERAI),
            Flag(name="AVANTI", matcher=AVANTI),
            Flag(name="AKARA", matcher=AKARA),
            Flag(name="DASARNA", matcher=DASARNA),
            Flag(name="CEDI", matcher=CEDI),
            Flag(name="PULINDA", matcher=PULINDA),
            Flag(name="ANGA", matcher=ANGA),
            Flag(name="GAUDA", matcher=GAUDA),
            Flag(name="RADHA", matcher=RADHA),
            Flag(name="SUHMA", matcher=SUHMA),
            Flag(name="PUNDRA", matcher=PUNDRA),
            Flag(name="VANGA", matcher=VANGA),
            Flag(name="SAMATATA", matcher=SAMATATA),
            Flag(name="LAUHITYA", matcher=LAUHITYA),
            Flag(name="UTKALA", matcher=UTKALA),
            Flag(name="KALINGA", matcher=KALINGA),
            Flag(name="VIDARBHA", matcher=VIDARBHA),
            Flag(name="RSIKA", matcher=RSIKA),
            Flag(name="MULAKA", matcher=MULAKA),
            Flag(name="ASMAKA", matcher=ASMAKA),
            Flag(name="APARANTA", matcher=APARANTA),
            Flag(name="KUNTALA", matcher=KUNTALA),
            Flag(name="KADAMBA", matcher=KADAMBA),
            Flag(name="GANGA", matcher=CAUVERIC),
            Flag(name="MAHISAKA", matcher=MAHISAKA),
            Flag(name="TELINGA", matcher=VENGI),
            Flag(name="ALUPA", matcher=TULU),
            Flag(name="CERA", matcher=CERA),
            Flag(name="AY", matcher=AY),
            Flag(name="EZHIMALA", matcher=EZHIMALA),
            Flag(name="KANCI", matcher=KANCI),
            Flag(name="COLA", matcher=COLA),
            Flag(name="PANDYA", matcher=PANDYA),
            Flag(name="KONGU", matcher=KONGU),
            Flag(name="SIMHALA", matcher=SIMHALA),
            Flag(name="GEDROSIA", matcher=BALOCH),
            Flag(name="KAMBOJA", matcher=KAMBOJA),
            Flag(name="MERU", matcher=MERU),
            Flag(name="ZARANJ", matcher=ZARANJ),
            Flag(name="KANDAHAR", matcher=KANDAHAR),
            Flag(name="HERAT", matcher=HERAT),
            Flag(name="MARGIANA", matcher=MARGIANA),
            Flag(name="BACTRIA", matcher=BACTRIA),
            Flag(name="SOGDIA_PROPER", matcher=SOGDIA_PROPER),
            Flag(name="FERGHANA", matcher=FERGHANA),
            Flag(name="KHWAREZM", matcher=KHWAREZM),
            Flag(name="KASHGAR", matcher=KASHGAR),
            Flag(name="KHOTAN", matcher=KHOTAN),
            Flag(name="AGNI", matcher=AGNI),
            Flag(name="AKSU", matcher=AKSU),
            Flag(name="KUCHA", matcher=KUCHA),
            Flag(name="ROURAN", matcher=ROURAN),
            Flag(name="QIEMO", matcher=QIEMO),
            Flag(name="KORLA", matcher=KORLA),
            Flag(name="TURFAN", matcher=TURFAN),
            Flag(name="COORG", matcher=COORG),
            Flag(name="TIBET", matcher=TIBET),
            Flag(name="YYY_GREAT_FOREST", matcher=GREAT_FOREST),
            Flag(name="YYY_KALAKAVANA", matcher=UP_KALAKAVANA),
            Flag(name="YYY_MARU", matcher=RJ_MARU),
            Flag(name="YYY_NAIMISA", matcher=UP_NAIMISA),
            Flag(name="YYY_HIMALAYAN", matcher=HIMALAYAN),
            Flag(name="ZZZ_BAYALU", matcher=BAYALU),
            Flag(name="ZZZ_GREATER_PUNE", matcher=GREATER_PUNE),
            Flag(name="ZZZ_HADOTI", matcher=HADOTI),
            Flag(name="ZZZ_BIHAR_NORTHEAST", matcher=BIHAR_NORTHEAST),
            Flag(name="ZZZ_BAHAWALPUR", matcher=BAHAWALPUR),
            Flag(name="ZZZ_TIBET_BURMA_INTERM", matcher=TIBET_BURMA_INTERM),
            Flag(name="ZZZ_YUNNAN_BURMA_INTERM", matcher=YUNNAN_BURMA_INTERM),
            Flag(name="ZZZ_KAREN", matcher=KAREN),
            Flag(name="ZZZ_SIAM_BURMA_INTERM", matcher=SIAM_BURMA_INTERM),
            Flag(name="BURMA_UPPER", matcher=BURMA_UPPER),
            Flag(name="BURMA_LOWER", matcher=BURMA_LOWER),
            Flag(name="SIAM", matcher=SIAM),
            Flag(name="LAOS", matcher=LAOS),
            Flag(name="KHMER", matcher=KHMER),
            Flag(name="CHAM", matcher=CHAM),
            Flag(name="NORTH_VIETNAM", matcher=NORTH_VIETNAM),
            Flag(name="BORNEO_MYS_GREATER", matcher=BORNEO_MYS_GREATER),
            Flag(name="BORNEO_IDN", matcher=BORNEO_IDN),
            Flag(name="MALAY_PENINSULA", matcher=MALAY_PENINSULA),
            Flag(name="SUMATRA", matcher=SUMATRA),
            Flag(name="JAVA", matcher=JAVA),
            Flag(name="ZZZ_LESSER_SUNDA", matcher=LESSER_SUNDA),
            Flag(name="ZZZ_MALUKU", matcher=MALUKU),
            Flag(name="ZZZ_SULAWESI", matcher=SULAWESI),
            Flag(name="ZZZ_KEPULAUAN", matcher=KEPULAUAN),
            Flag(name="ZZZ_BANGKA", matcher=BANGKA),
            Flag(name="ZZZ_PAPUA_IDN", matcher=PAPUA_IDN),
            Flag(name="ANDAMAN_NICOBAR", matcher=ANDAMAN_NICOBAR),
        ]

    @property
    def custom_colors(self):
        return {
            flag.name: "#444444"  # grey these out
            for flag in self.flags
            if flag.name.startswith("YYY_") or flag.name.startswith("ZZZ_")
        }


class INDIC(NATIONS):
    def __init__(self, **kwargs):
        options = {"std_start": "india"}
        options.update(kwargs)
        super().__init__(**options)

    @property
    def geojson(self):
        return Loka.INDIC.load(verbose=self.verbose)

    @property
    def geojson_rivers(self):
        return Varuna.INDIAN_SUBCONTINENT.load(verbose=self.verbose)


class SILKRD(NATIONS):
    def __init__(self, **kwargs):
        options = {"std_start": "Meru"}
        options.update(kwargs)
        super().__init__(**options)

    @property
    def geojson(self):
        return Loka.SILKRD.load()

    @property
    def geojson_rivers(self):
        return Varuna.SILKRD.load()


class SEA(NATIONS):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @property
    def geojson(self):
        return Loka.SEA.load()

    @property
    def geojson_rivers(self):
        return super().geojson_rivers


class INDOSPHERE(NATIONS):
    def __init__(self, **kwargs):
        options = {"std_start": "brahmavarta"}
        options.update(kwargs)
        super().__init__(**options)

    @property
    def geojson(self):
        return Loka.INDOSPHERE.load()

    @property
    def geojson_rivers(self):
        return Varuna.WORLD.load()