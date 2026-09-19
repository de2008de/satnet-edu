"""Paired targeted-failure experiment for the final SatNet Edu lecture.

Run from the repository root. Metrics describe samples and a labeled left-hold
time estimate, not continuous operational availability or application latency.
"""

import csv
import json
from pathlib import Path
from statistics import mean

from satnet_edu import Network, RouteQuery


def make_network():
    net = Network("Lecture 05: paired failure", epoch="2026-01-01T00:00:00Z")
    net.add_constellation(planes=6, sats_per_plane=12, altitude_km=1000,
                          inclination_deg=53)
    net.add_ground_station("A", lat=49.28, lon=-123.12, label="Vancouver")
    net.add_ground_station("B", lat=35.68, lon=139.69, label="Tokyo")
    net.set_link_policy(topology="orbital_neighbors", max_isl_km=4000,
                        min_elevation_deg=10)
    return net


def summarize(frames):
    routes = [frame["routes"][0] for frame in frames]
    reachable = [route["status"] == "reachable" for route in routes]
    valid_delays = [route["propagation_ms"] for route, ok in zip(routes, reachable) if ok]
    times = [frame["t_s"] for frame in frames]
    intervals = [end - start for start, end in zip(times, times[1:])]
    held_reachable_s = sum(dt for dt, ok in zip(intervals, reachable) if ok)
    longest_held_gap_s = current_gap_s = 0
    for dt, ok in zip(intervals, reachable):
        current_gap_s = 0 if ok else current_gap_s + dt
        longest_held_gap_s = max(longest_held_gap_s, current_gap_s)
    return {
        "samples": len(frames),
        "reachable_samples": sum(reachable),
        "reachable_sample_fraction": sum(reachable) / len(frames),
        "mean_propagation_ms_when_reachable": mean(valid_delays) if valid_delays else None,
        "left_hold_reachable_time_fraction": held_reachable_s / (times[-1] - times[0]),
        "left_hold_longest_gap_s": longest_held_gap_s,
    }


def main():
    output = Path("outputs/lecture-05")
    output.mkdir(parents=True, exist_ok=True)
    baseline = make_network()
    target_route = baseline.at(600).route("A", "B", metric="delay")
    if not target_route.reachable or not target_route.path[1:-1]:
        raise RuntimeError("The baseline must have an interior route satellite at 600 s.")
    candidates = target_route.path[1:-1]
    failed_node = candidates[len(candidates) // 2]
    failed = Network.from_dict(baseline.to_dict())
    failed.add_failure(node_id=failed_node, start_s=600, end_s=900)
    recordings = {}
    summaries = {}
    for label, net in (("baseline", baseline), ("failure", failed)):
        run = net.run(duration_s=1200, step_s=10,
                      record_routes=[RouteQuery("delay", "A", "B", "delay")])
        run.save(output / f"{label}.json")
        run.export_html(output / f"{label}.html", language="en")
        frames = run.to_dict()["frames"]
        recordings[label] = frames
        summaries[label] = summarize(frames)
    baseline_frames, failure_frames = recordings["baseline"], recordings["failure"]
    if [f["t_s"] for f in baseline_frames] != [f["t_s"] for f in failure_frames]:
        raise RuntimeError("Paired metrics require identical timestamps.")
    rows = []
    for b, f in zip(baseline_frames, failure_frames):
        br, fr = b["routes"][0], f["routes"][0]
        bok, fok = br["status"] == "reachable", fr["status"] == "reachable"
        row = {"t_s": b["t_s"], "baseline_reachable": int(bok),
               "failure_reachable": int(fok), "baseline_ms": br["propagation_ms"],
               "failure_ms": fr["propagation_ms"],
               "paired_delay_difference_ms": fr["propagation_ms"] - br["propagation_ms"]
               if bok and fok else None}
        for label, frame in (("baseline", b), ("failure", f)):
            for site in ("A", "B"):
                row[f"{label}_{site}_contacts"] = sum(
                    site in (link["source"], link["target"]) for link in frame["links"])
        rows.append(row)
    with (output / "paired-metrics.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    summary = {
        "failed_node": failed_node,
        "selection_rule": "Middle interior satellite of baseline delay route at 600 s",
        "failure_interval_s": [600, 900],
        "failure_interval_convention": "start included, end excluded",
        "metrics": summaries,
        "additional_unreachable_samples": sum(
            row["baseline_reachable"] and not row["failure_reachable"] for row in rows),
        "limitations": ["Targeted stress case, not random fleet reliability",
                        "Left-hold time metrics assume no unseen state changes",
                        "Propagation only, no queues or protocol convergence"],
    }
    (output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    print(f"Open the two HTML viewers in {output} and inspect paired-metrics.csv.")


if __name__ == "__main__":
    main()
