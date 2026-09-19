from copy import deepcopy
import json
from pathlib import Path

DEFAULT_MAX_BYTES = 128 * 1024 * 1024


class Run:
    def __init__(self, data):
        # Normalize tuples and enforce JSON finite values.
        self._data = json.loads(json.dumps(data, allow_nan=False))

    def to_dict(self):
        return deepcopy(self._data)

    def save(self, path, pretty=False, *, max_bytes=DEFAULT_MAX_BYTES):
        from .validate import validate_trace
        validate_trace(self._data)
        data = json.dumps(self._data, ensure_ascii=False, allow_nan=False, indent=2 if pretty else None, separators=None if pretty else (",", ":"))
        if len(data.encode("utf-8")) > max_bytes:
            raise ValueError(f"trace exceeds max_bytes={max_bytes}")
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(data, encoding="utf-8")
        return path.resolve()

    def export_html(self, path, language="en"):
        from ..export import export_html
        return export_html(self._data, path, language)


def load(path, *, max_bytes=DEFAULT_MAX_BYTES):
    from .validate import validate_trace
    path = Path(path)
    if path.stat().st_size > max_bytes:
        raise ValueError(f"trace exceeds max_bytes={max_bytes}")
    def invalid(value):
        raise ValueError(f"JSON contains non-finite value: {value}")
    data = json.loads(path.read_text(encoding="utf-8"), parse_constant=invalid)
    validate_trace(data)
    return Run(data)
