import copy

import pytest

from satnet_edu import Network, Run, load
from satnet_edu.trace.validate import validate_trace


@pytest.fixture
def trace():
    n = Network()
    n.add_constellation(
        planes=1, sats_per_plane=12, altitude_km=1000, inclination_deg=53
    )
    return n.run(duration_s=0, step_s=5, record_routes=[("S01-01", "S01-02")]).to_dict()


def test_roundtrip(trace, tmp_path):
    p = Run(trace).save(tmp_path / "trace.json")
    assert load(p).to_dict() == trace


@pytest.mark.parametrize(
    "case",
    [
        "version",
        "nan",
        "duplicate",
        "query",
        "edge",
        "metric",
        "clock",
        "enabled",
        "units",
    ],
)
def test_invalid(trace, case):
    d = copy.deepcopy(trace)
    f = d["frames"][0]
    if case == "version":
        d["schema_version"] = "2.0.0"
    if case == "nan":
        f["node_states"][0]["lat_deg"] = float("nan")
    if case == "duplicate":
        f["node_states"].append(f["node_states"][0])
    if case == "query":
        f["routes"] = []
    if case == "edge":
        f["routes"][0]["link_ids"][0] = "absent"
    if case == "metric":
        f["routes"][0]["distance_km"] += 1
    if case == "clock":
        f["t_s"] = 1
    if case == "enabled":
        f["node_states"][0]["enabled"] = False
    if case == "units":
        d["model"]["units"]["length"] = "m"
    with pytest.raises(ValueError):
        validate_trace(d)
