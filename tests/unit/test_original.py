import json
import math
from pathlib import Path

import pytest
from satnet_edu import Network
from satnet_edu.engine.clock import sample_times


def test_original_regression():
    data = json.loads((Path(__file__).parents[1] / "fixtures/legacy-usergs.json").read_text())
    net = Network()
    net.add_constellation(planes=2, sats_per_plane=3, altitude_km=1000, inclination_deg=53)
    assert [o["tle"] for o in net.to_dict()["objects"]] == data["tles"]
    for frame in data["frames"]:
        nodes = list(net.at(frame["t_s"]).nodes.values())
        for node, old in zip(nodes, frame["states"]):
            assert node.lat_deg == pytest.approx(old["sublat_deg"], abs=0.0001)
            assert node.lon_deg == pytest.approx(old["sublong_deg"], abs=0.0001)
        for node, old in zip(nodes[1:], frame["distances_from_first_km"]):
            assert math.dist(nodes[0].position_ecef_km, node.position_ecef_km) == pytest.approx(old, abs=0.01)


def test_time_grid():
    assert sample_times(0, 10, 4) == [0, 4, 8, 10]
    assert sample_times(3, 0, 4) == [3]
    with pytest.raises(ValueError):
        sample_times(0, 10, 0)
