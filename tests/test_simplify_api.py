from xatra import Map, get_current_map, new_map, simplify
from xatra.loaders import get_active_simplification_tolerance, set_active_simplification_tolerance
from xatra.territory import Territory
from xatra.geometry_cache import clear_geometry_cache, get_geometry_cache_stats


def _tiny_square(lat: float = 10.0, lon: float = 70.0) -> Territory:
    return Territory.from_polygon(
        [
            [lat, lon],
            [lat, lon + 1.0],
            [lat + 1.0, lon + 1.0],
            [lat + 1.0, lon],
        ]
    )


def test_map_simplify_and_pyplot_wrapper():
    m = Map()
    m.simplify(0.025)
    assert m._simplify_tolerance == 0.025
    m.simplify(None)
    assert m._simplify_tolerance is None

    new_map()
    simplify(0.05)
    assert get_current_map()._simplify_tolerance == 0.05


def test_export_applies_active_simplification():
    m = Map()
    m.simplify(0.01)
    m.Flag("Test", _tiny_square())
    payload = m._export_json()
    assert payload["flags"]["mode"] == "static"
    assert get_active_simplification_tolerance() == 0.01


def test_geometry_cache_key_isolation_by_simplification():
    clear_geometry_cache(memory_only=True)
    t = _tiny_square()

    set_active_simplification_tolerance(None)
    t.to_geometry()
    size_without = get_geometry_cache_stats()["memory_cache_size"]

    set_active_simplification_tolerance(0.02)
    t.to_geometry()
    size_with = get_geometry_cache_stats()["memory_cache_size"]

    assert size_with >= size_without + 1
    set_active_simplification_tolerance(None)
