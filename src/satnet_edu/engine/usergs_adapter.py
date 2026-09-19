"""Decoupled UserGS constellation update loop, with immutable public states."""
from ..state import NodeState, Snapshot
from .orbit import propagate
from .geometry import ground_position
from .topology import build_links


def snapshot(net, t_s, disabled):
    states = {}
    disabled = set(disabled)
    ids = {o["id"] for o in net._objects}
    if not disabled <= ids:
        raise ValueError(f"disabled: unknown node IDs {sorted(disabled - ids)}")
    disabled.update(f["node_id"] for f in net._failures if f["start_s"] <= t_s < f["end_s"])
    for obj in sorted(net._objects, key=lambda o: o["id"]):
        if obj["kind"] == "satellite":
            p, (lat, lon, alt) = propagate(obj["tle"], net._epoch, t_s)
        else:
            lat, lon, alt = obj["lat_deg"], obj["lon_deg"], 0.0
            p = ground_position(lat, lon)
        states[obj["id"]] = NodeState(obj["id"], obj["id"] not in disabled, p, lat, lon, alt)
    links = build_links(net._objects, net._constellations, states, net._policy)
    return Snapshot(t_s, states, links, {o["id"]: o["kind"] for o in net._objects})
