#!/usr/bin/env python3
"""
Tests for icon library helpers and Leaflet built-in marker behavior.
"""

from xatra import Icon


def test_bootstrap_defaults():
    icon = Icon.bootstrap("bank2")
    assert icon.icon_url.endswith("/icons/bank2.svg")
    assert icon.icon_size == (24, 24)
    assert icon.icon_anchor == (12, 12)
    assert icon.popup_anchor == (0, -12)


def test_bootstrap_anchor_overrides():
    icon = Icon.bootstrap(
        "geo-alt-fill",
        icon_size=(20, 30),
        icon_anchor=(10, 30),
        popup_anchor=(0, -24),
    )
    assert icon.icon_size == (20, 30)
    assert icon.icon_anchor == (10, 30)
    assert icon.popup_anchor == (0, -24)


def test_leaflet_builtin_defaults():
    icon = Icon.builtin("marker-icon.png")
    assert icon.icon_size == (25, 41)
    assert icon.icon_anchor == (12, 41)
    assert icon.popup_anchor == (1, -34)
    assert icon.shadow_url is not None
    assert icon.shadow_size == (41, 41)
    assert icon.shadow_anchor == (12, 41)


def test_builtin_rejects_non_leaflet_assets():
    try:
        Icon.builtin("temple.svg")
        assert False, "Expected ValueError for removed built-in asset"
    except ValueError as e:
        assert "Only Leaflet marker assets are available" in str(e)
