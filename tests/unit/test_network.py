import random
from dataclasses import FrozenInstanceError

import pytest

from satnet_edu import LinkState, Network, NodeState, Snapshot
from satnet_edu.engine.geometry import (
    C_KM_S,
    elevation_deg,
    visible_isl,
)
from satnet_edu.engine.geometry import (
    EARTH_RADIUS_KM as R,
)
from satnet_edu.engine.topology import candidate_pairs


@pytest.mark.parametrize(
    "planes,slots,count", [(1, 1, 0), (1, 3, 3), (2, 3, 9), (3, 4, 24)]
)
def test_neighbors(planes, slots, count):
    n = Network()
    n.add_constellation(
        planes=planes, sats_per_plane=slots, altitude_km=1000, inclination_deg=53
    )
    s = n.to_dict()
    pairs = candidate_pairs(s["objects"], s["constellations"], "orbital_neighbors")
    assert (
        len(pairs) == count
        and len(set(pairs)) == count
        and all(a != b for a, b in pairs)
    )


@pytest.mark.parametrize("value", [True, float("nan"), float("inf"), -1, "6"])
def test_bad_numbers(value):
    with pytest.raises(ValueError):
        Network().add_constellation(
            planes=value, sats_per_plane=3, altitude_km=1000, inclination_deg=53
        )
    with pytest.raises(ValueError):
        Network().at(value)


def test_geometry():
    assert not visible_isl((R + 1000, 0, 0), (-R - 1000, 0, 0))
    assert visible_isl((R + 1000, 0, 0), (R + 1000, 1000, 0))
    assert elevation_deg((R, 0, 0), (R + 1000, 0, 0)) == 90
    assert elevation_deg((R, 0, 0), (R, 1000, 0)) == 0


def test_purity_failure_roundtrip():
    n = Network()
    n.add_constellation(
        planes=1, sats_per_plane=3, altitude_km=1000, inclination_deg=53
    )
    n.add_failure(node_id="S01-01", start_s=3, end_s=7)
    state = random.getstate()
    a = n.at(0)
    n.at(8)
    n.at(2)
    assert a == n.at(0) and state == random.getstate()
    with pytest.raises(TypeError):
        a.nodes["x"] = None
    with pytest.raises(FrozenInstanceError):
        a.nodes["S01-01"].enabled = False
    run = n.run(duration_s=10, step_s=4, record_routes=[("S01-01", "S01-01")]).to_dict()
    assert [f["t_s"] for f in run["frames"]] == [0, 3, 4, 7, 8, 10]
    assert [n.at(t).nodes["S01-01"].enabled for t in [2, 3, 6, 7]] == [
        True,
        False,
        False,
        True,
    ]
    assert Network.from_dict(n.to_dict()).to_dict() == n.to_dict()
    assert (
        n.run(duration_s=10, step_s=4, record_routes=[("S01-01", "S01-01")]).to_dict()
        == run
    )
    assert (
        not n.at(0, disabled=["S01-01"]).nodes["S01-01"].enabled
        and n.at(0).nodes["S01-01"].enabled
    )


def graph():
    nodes = {x: NodeState(x, True, (0, 0, 0), 0, 0, 0) for x in "ABCDE"}
    links = {}
    for a, b, d in [
        ("A", "B", 9),
        ("B", "D", 9),
        ("A", "C", 1),
        ("C", "E", 1),
        ("E", "D", 1),
    ]:
        links[a + b] = LinkState(a + b, a, b, "isl", d, d / C_KM_S * 1000)
    return Snapshot(0, nodes, links, {x: "satellite" for x in nodes})


def test_routing():
    s = graph()
    assert s.route("A", "D", "hops").path == ("A", "B", "D")
    assert s.route("A", "D", "delay").path == ("A", "C", "E", "D")
    assert s.route("A", "A").hops == 0
    with pytest.raises(ValueError):
        s.route("A", "X")
    kinds = dict(s.kinds)
    kinds["C"] = "ground_station"
    assert Snapshot(0, s.nodes, s.links, kinds).route("A", "D").path == ("A", "B", "D")
    assert Snapshot(0, s.nodes, {}, s.kinds).route("A", "D").reason == "no_path"


def test_manual_epoch():
    n = Network(epoch="2025-06-02T12:00:00Z")
    n.add_satellite(
        "custom", altitude_km=1000, inclination_deg=60, raan_deg=20, phase_deg=45
    )
    assert n.to_dict()["objects"][0]["tle"][0][18:32] == "25153.50000000"
    with pytest.raises(ValueError, match="distance"):
        n.at(0)
    n.set_link_policy(topology="distance")
    assert n.at(0).nodes["custom"].altitude_km > 900
    assert Network.from_dict(n.to_dict()).to_dict() == n.to_dict()
