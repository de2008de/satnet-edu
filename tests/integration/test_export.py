import json

import pytest

from satnet_edu import Network
from satnet_edu.export import safe_json


def test_safe_export(tmp_path):
    text = 'Unicode café Ω " </script><script>globalThis.PWNED=true</script> & <b>label</b>'
    n = Network(text)
    n.add_ground_station("A", lat=0, lon=0, label=text)
    run = n.run(duration_s=0, step_s=5)
    p = run.export_html(tmp_path / "safe.html")
    html = p.read_text(encoding="utf-8")
    assert "</script><script>globalThis.PWNED" not in html
    assert json.loads(safe_json(text)) == text
    assert "\\u003c/script\\u003e" in html and "SatNetEduPlayer" in html
    assert '<html lang="en">' in html
    with pytest.raises(ValueError):
        run.export_html(tmp_path / "bad.html", "bad")
