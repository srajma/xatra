import re

from shapely.geometry import Polygon, mapping

import xatra
from xatra.flagmap import _format_legend_value, generate_colormap_svg, _default_data_colormap
from xatra.paxmax import _compute_centroid_for_geometry, _polygonal_only
from xatra.territory import Territory


def _square(lat=10.0, lon=70.0, size=2.0):
    return Territory.from_polygon([[lat, lon], [lat, lon + size], [lat + size, lon + size], [lat + size, lon]])


def test_default_basemap_when_none_chosen():
    m = xatra.Map()
    m.Flag("A", _square())
    payload = m._export_json()
    assert len(payload["base_options"]) == 1
    assert payload["base_options"][0]["name"] == "Atlas"
    assert payload["base_options"][0]["default"] is True


def test_first_basemap_becomes_default_if_none_marked():
    m = xatra.Map()
    m.BaseOption("OpenStreetMap")
    m.BaseOption("Esri.WorldImagery")
    defaults = [b["default"] for b in m._export_json()["base_options"]]
    assert defaults == [True, False]


def test_atlas_and_physical_basemaps_can_coexist():
    m = xatra.Map()
    m.BaseOption("Xatra.Atlas", default=True)
    m.BaseOption("Esri.WorldPhysical")
    assert [b.name for b in m._base_options] == ["Atlas", "Esri.WorldPhysical"]


def test_fit_bounds_only_without_explicit_view():
    m = xatra.Map()
    m.Flag("A", _square(10, 70, 2))
    payload = m._export_json()
    (min_lat, min_lng), (max_lat, max_lng) = payload["fit_bounds"]
    assert (min_lat, min_lng, max_lat, max_lng) == (10, 70, 12, 72)

    m2 = xatra.Map()
    m2.Flag("A", _square())
    m2.zoom(6)
    assert m2._export_json()["fit_bounds"] is None


def test_watermark_added_once():
    m = xatra.Map()
    m.Flag("A", _square())
    m.to_html_string()
    m.to_html_string()
    credits = [tb for tb in m._title_boxes if "xatra-credit" in tb.html]
    assert len(credits) == 1


def test_payload_cannot_close_script_tag():
    m = xatra.Map()
    m.Flag("</script><script>alert(1)</script>", _square())
    html = m.to_html_string()
    script = html.split("const payload = ", 1)[1].split("\n", 1)[0]
    assert "</script>" not in script


def test_legend_values_are_compact():
    assert _format_legend_value(55.526719662194964) == "55.5"
    assert _format_legend_value(1234567) == "1.23M"
    assert _format_legend_value(2500) == "2,500"
    assert _format_legend_value(0.0045678) == "0.00457"


def test_colormap_svg_has_gradient_rect_and_ticks():
    svg = generate_colormap_svg(_default_data_colormap(), 55.526719662194964, 94.8257934204185)
    assert "<rect" in svg and "linearGradient" in svg
    labels = re.findall(r">([^<>]+)</text>", svg)
    assert labels == ["55.5", "75.2", "94.8"]


def test_artifact_holes_are_dropped_but_enclaves_kept():
    outer = [(0, 0), (10, 0), (10, 10), (0, 10), (0, 0)]
    speck = [(1, 1), (1.01, 1), (1.01, 1.01), (1, 1.01), (1, 1)]
    sliver = [(3, 3), (8, 3), (8, 3.002), (3, 3.002), (3, 3)]
    enclave = [(5, 5), (7, 5), (7, 7), (5, 7), (5, 5)]
    cleaned = _polygonal_only(Polygon(outer, [speck, sliver, enclave]))
    assert len(cleaned.interiors) == 1
    assert cleaned.interiors[0].coords[0] == (5.0, 5.0)


def test_label_anchor_lies_inside_concave_territory():
    c_shape = Polygon([(0, 0), (10, 0), (10, 2), (2, 2), (2, 8), (10, 8), (10, 10), (0, 10), (0, 0)])
    lat, lng = _compute_centroid_for_geometry(mapping(c_shape))
    from shapely.geometry import Point

    assert c_shape.contains(Point(lng, lat))


def test_script_markers_relied_on_by_xatra_gui():
    # xatra-gui rewrites the inline script (external geometry loading) by
    # matching these exact strings; changing them silently breaks its previews.
    m = xatra.Map()
    m.Flag("A", _square())
    html = m.to_html_string()
    assert "    <script>\n      const payload = " in html
    assert "      const geometryRegistry = payload.geometry_registry || {};" in html
    assert html.count("      setupSearch();\n    </script>") == 1
