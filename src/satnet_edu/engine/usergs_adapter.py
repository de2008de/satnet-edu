"""Decoupled UserGS constellation update loop, with immutable public states."""
from ..state import NodeState, Snapshot
from .orbit import propagate


def snapshot(net, t_s, disabled):
    states = {}
    disabled = set(disabled)
    ids = {o["id"] for o in net._objects}
    if not disabled <= ids:
        raise ValueError(f"disabled: unknown node IDs {sorted(disabled - ids)}")
    for obj in sorted(net._objects, key=lambda o: o["id"]):
        p, (lat, lon, alt) = propagate(obj["tle"], net._epoch, t_s)
        states[obj["id"]] = NodeState(obj["id"], obj["id"] not in disabled, p, lat, lon, alt)
    return Snapshot(t_s, states, {}, {o["id"]: o["kind"] for o in net._objects})
