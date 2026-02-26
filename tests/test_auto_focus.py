import xatra
from xatra.territory_library import PARTHIA


def test_auto_focus_handles_tuple_coordinates_in_serialized_geometry():
    m = xatra.Map()
    focus = m._calculate_auto_focus_from_serialized_elements(
        pax={
            "mode": "static",
            "flags": [
                {
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [((10.0, 20.0), (14.0, 20.0), (14.0, 24.0), (10.0, 24.0), (10.0, 20.0))
                        ],
                    }
                }
            ],
        },
        rivers_serialized=[],
        paths_serialized=[],
        points_serialized=[],
        texts_serialized=[],
        admins_serialized=[],
        admin_rivers_serialized=[],
        data_serialized=[],
        dataframes_serialized=[],
    )

    assert focus == (22.0, 12.0)


def test_auto_focus_for_parthia_flag_is_not_default():
    m = xatra.Map()
    m.Flag(value=PARTHIA, label="PARTHIA")

    payload = m._export_json()

    assert payload["initial_focus"] != (22.0, 79.0)
