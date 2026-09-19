import pytest

from satnet_edu import LinkState, Network, NodeState, Snapshot
from satnet_edu.engine.clock import sample_times
from satnet_edu.engine.geometry import C_KM_S, distance, visible_isl


def test_ground_geometry_and_range_threshold():
    n = Network()
    n.add_constellation(
        planes=1, sats_per_plane=12, altitude_km=1000, inclination_deg=53
    )
    at = n.at(0)
    s = at.nodes["S01-01"]
    n.add_ground_station("A", lat=s.lat_deg, lon=s.lon_deg)
    snap = n.at(0)
    gsl = next(
        l for l in snap.links.values() if {l.source, l.target} == {"A", "S01-01"}
    )
    assert gsl.distance_km == pytest.approx(s.altitude_km, abs=1e-8)
    for link in snap.links.values():
        a, b = (snap.nodes[x].position_ecef_km for x in (link.source, link.target))
        assert link.distance_km == pytest.approx(distance(a, b))
        if link.kind == "isl":
            assert visible_isl(a, b)
    n.set_link_policy(max_isl_km=1)
    assert all(l.kind == "gsl" for l in n.at(0).links.values())


def test_gs_cannot_provide_shortcut_or_self_when_disabled():
    n = Network()
    n.add_ground_station("A", lat=0, lon=0)
    n.add_ground_station("B", lat=0, lon=0)
    assert not n.at(0).links and n.at(0).route("A", "B").reason == "no_path"
    assert n.at(0).route("A", "A").propagation_ms == 0
    assert n.at(0, disabled=["A"]).route("A", "A").reason == "endpoint_disabled"


def test_tie_break_is_id_order():
    nodes = {x: NodeState(x, True, (1, 0, 0), 0, 0, 0) for x in "ABCD"}
    links = {}
    for a, b in [("A", "C"), ("C", "D"), ("A", "B"), ("B", "D")]:
        links[a + b] = LinkState(a + b, a, b, "isl", 1, 1000 / C_KM_S)
    for metric in ["delay", "hops"]:
        assert Snapshot(0, nodes, links, {x: "satellite" for x in nodes}).route(
            "A", "D", metric
        ).path == ("A", "B", "D")


def test_multiple_shells_and_instances():
    a = Network()
    b = Network()
    for _ in range(2):
        a.add_constellation(
            planes=1, sats_per_plane=12, altitude_km=1000, inclination_deg=53
        )
    assert len(a.at(0).nodes) == 24 and not b.at(0).nodes
    objects = {o["id"]: o for o in a.to_dict()["objects"]}
    assert all(
        objects[l.source]["constellation_id"] == objects[l.target]["constellation_id"]
        for l in a.at(0).links.values()
    )


@pytest.mark.parametrize(
    "epoch",
    ["2000-01-01", "2057-01-01T00:00:00Z", "2025-01-01T00:00:00-08:00", "not-a-date"],
)
def test_bad_epoch(epoch):
    with pytest.raises(ValueError):
        Network(epoch=epoch)


def test_limits_and_input_errors():
    n = Network(max_nodes=1)
    with pytest.raises(ValueError):
        n.add_constellation(
            planes=1, sats_per_plane=2, altitude_km=1000, inclination_deg=53
        )
    assert not n.to_dict()["objects"]
    n.add_ground_station("A", lat=0, lon=180)
    with pytest.raises(ValueError):
        n.add_ground_station("B", lat=0, lon=0)
    with pytest.raises(ValueError):
        n.at(0, disabled="A")
    with pytest.raises(ValueError):
        n.at(0, disabled=["absent"])
    with pytest.raises(ValueError):
        n.add_failure(node_id="A", start_s=1, end_s=1)
    with pytest.raises(ValueError):
        n.run(duration_s=1, step_s=1e-320)
    with pytest.raises(ValueError):
        n.at(10**1000)
    assert sample_times(2, 5, 2, [{"start_s": 2, "end_s": 7}], 10) == [2, 4, 6, 7]


def test_earth_rotation_in_fixed_frame():
    # Approximately geostationary orbit: Earth-fixed longitude should barely move.
    n = Network()
    n.add_satellite(
        "geo", altitude_km=35786, inclination_deg=0.1, raan_deg=0, phase_deg=0
    )
    n.set_link_policy(topology="distance")
    a, b = n.at(0).nodes["geo"], n.at(3600).nodes["geo"]
    assert abs((a.lon_deg - b.lon_deg + 180) % 360 - 180) < 1
    assert abs(a.lat_deg) < 1 and abs(b.lat_deg) < 1


def test_original_propagator_singularity_has_clear_error():
    n = Network()
    n.add_satellite(
        "geo", altitude_km=35786, inclination_deg=0, raan_deg=0, phase_deg=0
    )
    n.set_link_policy(topology="distance")
    with pytest.raises(ValueError, match="PyEphem"):
        n.at(0)
