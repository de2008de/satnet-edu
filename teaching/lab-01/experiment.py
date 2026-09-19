"""Lab 01: build, inspect, record, and compare a satellite-network experiment.

Run from the repository root after installing SatNet Edu. The slides follow
these numbered sections. Keep the same Python interpreter for install and run.
"""

import csv
import json
from pathlib import Path
from statistics import mean

from satnet_edu import Network, RouteQuery


# 1. Build a constellation with a fixed epoch.
net = Network("Lab 01", epoch="2026-01-01T00:00:00Z")
net.add_constellation(
    planes=6, sats_per_plane=12,
    altitude_km=1000, inclination_deg=53,
)

# 2. Add endpoints and set the usable-link rules.
net.add_ground_station(
    "A", lat=49.28, lon=-123.12, label="Vancouver")
net.add_ground_station(
    "B", lat=35.68, lon=139.69, label="Tokyo")
net.set_link_policy(
    topology="orbital_neighbors",
    max_isl_km=4000, min_elevation_deg=10,
)

# 3. Inspect one snapshot before recording a whole experiment.
route = net.at(120).route("A", "B", metric="delay")
if route.reachable:
    print("At 120 s:", route.path)
    print("Hops:", route.hops)
    print("Propagation (ms):", route.propagation_ms)
else:
    print("At 120 s:", route.reason)


# 4. Record a named case and export both machine-readable data and a viewer.
def record(network, label):
    run = network.run(
        duration_s=1200, step_s=10,
        record_routes=[RouteQuery("delay", "A", "B")],
    )
    folder = Path("outputs/lab-01")
    run.save(folder / f"{label}.json")
    run.export_html(folder / f"{label}.html")
    return run


baseline = record(net, "baseline")

# 5. Clone the baseline and disable a satellite on its route at 600 seconds.
r = net.at(600).route("A", "B", metric="delay")
if not r.reachable or len(r.path) < 3:
    raise RuntimeError("Need an interior satellite on the baseline route at 600 s.")
failed_id = r.path[len(r.path) // 2]
failed = Network.from_dict(net.to_dict())
failed.add_failure(node_id=failed_id, start_s=600, end_s=900)
failure = record(failed, "failure")
print("Disabled satellite:", failed_id, "on [600, 900) seconds")


# 6. Keep unavailable samples out of the delay mean, but in the sample count.
def summarize(run):
    frames = run.to_dict()["frames"]
    routes = [frame["routes"][0] for frame in frames]
    valid = [r for r in routes if r["status"] == "reachable"]
    return {
        "samples": len(routes),
        "reachable_samples": len(valid),
        "reachable_sample_fraction": len(valid) / len(routes),
        "mean_propagation_ms_when_reachable": (
            mean(r["propagation_ms"] for r in valid) if valid else None
        ),
    }


folder = Path("outputs/lab-01")
summary = {
    "failed_id": failed_id,
    "selection_rule": "Middle node of baseline route A to B at 600 s",
    "failure_interval_s": [600, 900],
    "baseline": summarize(baseline),
    "failure": summarize(failure),
    "metric_scope": "Sample reachability and conditional one-way propagation only",
}
(folder / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
print(json.dumps(summary, indent=2))

# 7. Export paired observations so students can explain when paths differ.
before = baseline.to_dict()["frames"]
after = failure.to_dict()["frames"]
if [f["t_s"] for f in before] != [f["t_s"] for f in after]:
    raise RuntimeError("Compare runs at matching timestamps.")
rows = []
for b, f in zip(before, after):
    br, fr = b["routes"][0], f["routes"][0]
    both = br["status"] == fr["status"] == "reachable"
    rows.append({
        "t_s": b["t_s"],
        "baseline_status": br["status"], "failure_status": fr["status"],
        "baseline_ms": br["propagation_ms"], "failure_ms": fr["propagation_ms"],
        "difference_ms": fr["propagation_ms"] - br["propagation_ms"] if both else None,
        "baseline_path": " -> ".join(br["node_ids"]),
        "failure_path": " -> ".join(fr["node_ids"]),
    })
with (folder / "paired.csv").open("w", newline="", encoding="utf-8") as handle:
    writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)
print(f"Open {folder / 'baseline.html'} and {folder / 'failure.html'} in a browser.")
