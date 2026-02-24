from shapely.geometry import GeometryCollection, LineString, Point, Polygon, mapping

from xatra.paxmax import _polygonal_only, paxmax_aggregate


def test_polygonal_only_drops_line_and_point_artifacts():
    geom = GeometryCollection(
        [
            Polygon([(0, 0), (3, 0), (3, 3), (0, 3), (0, 0)]),
            LineString([(0, 0), (3, 3)]),
            Point(1, 1),
        ]
    )

    cleaned = _polygonal_only(geom)

    assert cleaned is not None
    assert cleaned.geom_type in {"Polygon", "MultiPolygon"}


def test_paxmax_static_flag_uses_polygonal_geometry_only():
    geom = GeometryCollection(
        [
            Polygon([(0, 0), (4, 0), (4, 4), (0, 4), (0, 0)]),
            LineString([(0, 0), (4, 4)]),
            Point(2, 2),
        ]
    )

    result = paxmax_aggregate(
        [
            {
                "label": "X",
                "display_label": "X",
                "geometry": mapping(geom),
                "period": None,
            }
        ]
    )

    assert result["mode"] == "static"
    flag = result["flags"][0]
    assert flag["geometry"]["type"] in {"Polygon", "MultiPolygon"}
    assert flag["centroid"] is not None
