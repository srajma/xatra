"""Runtime settings sourced from environment variables."""

from __future__ import annotations

import os
import warnings


def _parse_caching_env() -> bool:
    """Parse CACHING environment variable.

    Accepted false values: 0, false, no, off
    Accepted true values: 1, true, yes, on, empty/unset
    """
    raw = os.environ.get("CACHING", "")
    value = raw.strip().lower()
    if value in ("", "1", "true", "yes", "on"):
        return True
    if value in ("0", "false", "no", "off"):
        return False
    warnings.warn(
        f"Invalid CACHING environment variable value: '{raw}'. "
        "Expected one of: 1, 0, true, false, yes, no, on, off. Defaulting to True.",
        UserWarning,
        stacklevel=3,
    )
    return True


CACHING_ENABLED = _parse_caching_env()
