"""Real-engine valid traces and intentionally corrupted contract inputs."""

import copy
import json
from pathlib import Path

from satnet_edu import Network

root = Path(__file__).resolve().parents[1]
target = root / "tests/fixtures"
target.mkdir(exist_ok=True)
n = Network("Minimal valid trace")
n.add_ground_station("A", lat=0, lon=0)
n.run(duration_s=0, step_s=1).save(target / "minimal-valid.json")
n = Network("Real engine contract reference")
n.add_constellation(planes=1, sats_per_plane=12, altitude_km=1000, inclination_deg=53)
trace = n.run(duration_s=0, step_s=1, record_routes=[("S01-01", "S01-02")]).to_dict()
(target / "real-engine-route.json").write_text(json.dumps(trace), encoding="utf-8")
cases = {}
for name in [
    "version",
    "nan",
    "infinity",
    "duplicate",
    "unknown-edge",
    "missing-query",
    "metric",
    "fault-state",
]:
    d = copy.deepcopy(trace)
    f = d["frames"][0]
    if name == "version":
        d["schema_version"] = "9.0.0"
    if name == "nan":
        f["node_states"][0]["lat_deg"] = float("nan")
    if name == "infinity":
        f["links"][0]["distance_km"] = float("inf")
    if name == "duplicate":
        f["node_states"].append(f["node_states"][0])
    if name == "unknown-edge":
        f["routes"][0]["link_ids"][0] = "does-not-exist"
    if name == "missing-query":
        f["routes"] = []
    if name == "metric":
        f["routes"][0]["propagation_ms"] += 1
    if name == "fault-state":
        f["node_states"][0]["enabled"] = False
    (target / f"invalid-{name}.json").write_text(json.dumps(d), encoding="utf-8")
print("Wrote real engine fixtures and eight corrupted files (not demonstrations).")
