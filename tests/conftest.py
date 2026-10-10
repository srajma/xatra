import pytest

from xatra.data_installer import is_data_installed

HAS_DATA = is_data_installed()

# Modules that load GADM data at import time.
collect_ignore = [] if HAS_DATA else ["test_adminrivers_labels.py"]


def pytest_configure(config):
    config.addinivalue_line("markers", "needs_data: needs the ~/.xatra geodata (xatra-install-data)")


def pytest_collection_modifyitems(config, items):
    if HAS_DATA:
        return
    skip = pytest.mark.skip(reason="xatra geodata not installed (run xatra-install-data)")
    for item in items:
        if "needs_data" in item.keywords:
            item.add_marker(skip)
