from unittest.mock import Mock, patch

import xatra
import xatra.pyplot as pyplot


def test_module_level_exports_include_new_map_method_wrappers():
    assert callable(xatra.zoom)
    assert callable(xatra.focus)
    assert callable(xatra.to_html_string)


def test_wrappers_forward_new_and_extended_map_method_args():
    dummy_map = Mock()
    dummy_map.to_html_string.return_value = "<html></html>"

    with patch("xatra.pyplot.get_current_map", return_value=dummy_map):
        pyplot.River(
            label="R",
            value={"type": "LineString", "coordinates": [[77.0, 28.0], [78.0, 29.0]]},
            note="n",
            classes="c",
            period=[0, 1],
            show_label=True,
            n_labels=3,
            hover_radius=12,
        )
        dummy_map.River.assert_called_once_with(
            "R",
            {"type": "LineString", "coordinates": [[77.0, 28.0], [78.0, 29.0]]},
            "n",
            "c",
            [0, 1],
            True,
            3,
            12,
        )

        pyplot.Path(
            label="P",
            value=[[28.0, 77.0], [29.0, 78.0]],
            note="n",
            classes="c",
            period=[0, 1],
            show_label=True,
            n_labels=2,
            hover_radius=9,
        )
        dummy_map.Path.assert_called_once_with(
            "P", [[28.0, 77.0], [29.0, 78.0]], "n", "c", [0, 1], True, 2, 9
        )

        pyplot.Point(
            label="X",
            position=[28.0, 77.0],
            note="n",
            period=[0, 1],
            icon=None,
            show_label=True,
            hover_radius=25,
            classes="city",
            rotation=30.0,
        )
        dummy_map.Point.assert_called_once_with(
            "X", [28.0, 77.0], "n", [0, 1], None, True, 25, "city", 30.0
        )

        pyplot.Text(
            label="T",
            position=[28.0, 77.0],
            note="n",
            classes="c",
            period=[0, 1],
            rotation=15.0,
        )
        dummy_map.Text.assert_called_once_with(
            "T", [28.0, 77.0], "n", "c", [0, 1], 15.0
        )

        pyplot.AdminRivers(
            period=[0, 1], classes="c", sources=["naturalearth"], show_label=True, n_labels=4
        )
        dummy_map.AdminRivers.assert_called_once_with(
            [0, 1], "c", ["naturalearth"], True, 4
        )

        pyplot.zoom(6)
        dummy_map.zoom.assert_called_once_with(6)

        pyplot.focus(28.6, 77.2)
        dummy_map.focus.assert_called_once_with(28.6, 77.2)

        assert pyplot.to_html_string() == "<html></html>"
        dummy_map.to_html_string.assert_called_once_with()
