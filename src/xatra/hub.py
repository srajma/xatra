"""xatrahub import helper for loading map/theme/library payloads from a hub API."""

from __future__ import annotations

import os
import json
from urllib.request import urlopen

DEFAULT_XATRAHUB_URL = "http://localhost:8088"
XATRAHUB_URL = os.environ.get("XATRAHUB_URL", DEFAULT_XATRAHUB_URL).rstrip("/")


def _normalize_path(path: str) -> str:
    raw = str(path or "").strip().strip('"').strip("'")
    if not raw.startswith("/"):
        raw = "/" + raw
    return raw


def xatrahub(path: str, filter_only=None, filter_not=None):
    """Load content from XatraHub.

    - map/css paths execute code into current globals.
    - lib paths return a namespace object with imported symbols.
    """
    import types

    p = _normalize_path(path)
    with urlopen(f"{XATRAHUB_URL}{p}", timeout=20) as resp:
        payload = json.loads(resp.read().decode("utf-8"))
    kind = str(payload.get("kind", "")).strip()
    content = payload.get("content", "")

    if kind in {"map", "css"}:
        code = str(content or "")
        if filter_only or filter_not:
            import ast
            tree = ast.parse(code or "")
            keep = []
            only = {str(x).strip() for x in (filter_only or []) if str(x).strip()}
            deny = {str(x).strip() for x in (filter_not or []) if str(x).strip()}
            for stmt in tree.body:
                seg = ast.get_source_segment(code, stmt) or ""
                allow = True
                if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
                    fn = stmt.value.func
                    if isinstance(fn, ast.Attribute) and getattr(fn.value, "id", None) == "xatra":
                        method = str(fn.attr)
                        if only and method not in only:
                            allow = False
                        if method in deny:
                            allow = False
                if allow and seg.strip():
                    keep.append(seg)
            code = "\n".join(keep)
        if code.strip():
            exec(code, globals())
        return None

    if kind == "lib":
        scope = {}
        exec(str(content or ""), scope)
        public = {k: v for k, v in scope.items() if not k.startswith("_")}
        return types.SimpleNamespace(**public)

    raise ValueError(f"Unsupported xatrahub kind: {kind}")
