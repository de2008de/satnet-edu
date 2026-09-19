"""Safe single-file packing; never runs the simulation engine."""

import json
from importlib.resources import files
from pathlib import Path

from .trace.io import DEFAULT_MAX_BYTES
from .trace.validate import validate_trace


def safe_json(value):
    return (
        json.dumps(value, ensure_ascii=True, allow_nan=False, separators=(",", ":"))
        .replace("&", "\\u0026")
        .replace("<", "\\u003c")
        .replace(">", "\\u003e")
    )


def export_html(trace, path, language="en"):
    if language != "en":
        raise ValueError("language: this edition supports English (en) only")
    validate_trace(trace)
    payload = safe_json(trace)
    if len(payload.encode("utf-8")) > DEFAULT_MAX_BYTES:
        raise ValueError("trace exceeds offline export size limit")
    script = (
        files("satnet_edu")
        .joinpath("assets/satnet-edu-player.js")
        .read_text(encoding="utf-8")
    )
    html = f'''<!doctype html>
<html lang="{language}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>SatNet Edu</title><style>body{{margin:0;background:#fff}}</style></head>
<body><main id="viewer"></main><script type="application/json" id="trace-data">{payload}</script>
<script>{script}</script><script>
const player=SatNetEduPlayer.createPlayer(document.getElementById('viewer'),{{language:'{language}'}});
player.load(JSON.parse(document.getElementById('trace-data').textContent)).catch(()=>{{}});
</script></body></html>'''
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html, encoding="utf-8")
    return path.resolve()
