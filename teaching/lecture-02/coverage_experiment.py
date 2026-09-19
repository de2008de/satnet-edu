"""Lecture 02: change only inclination and measure sampled ground access."""

import csv
from pathlib import Path

from satnet_edu import Network


def main():
    output = Path("outputs/lecture-02")
    output.mkdir(parents=True, exist_ok=True)
    summary = []
    for inclination in (53, 85):
        net = Network(f"Lecture 02: inclination {inclination}", epoch="2026-01-01T00:00:00Z")
        net.add_constellation(planes=6, sats_per_plane=12, altitude_km=550,
                              inclination_deg=inclination)
        net.add_ground_station("Mid", lat=50, lon=0, label="50 N")
        net.add_ground_station("North", lat=70, lon=0, label="70 N")
        net.set_link_policy(topology="orbital_neighbors", max_isl_km=4000,
                            min_elevation_deg=25)
        run = net.run(duration_s=21600, step_s=30)
        stem = output / f"inclination-{inclination}"
        run.save(stem.with_suffix(".json"))
        run.export_html(stem.with_suffix(".html"), language="en")
        rows = []
        for frame in run.to_dict()["frames"]:
            counts = {site: sum(site in (link["source"], link["target"])
                                for link in frame["links"])
                      for site in ("Mid", "North")}
            rows.append({"t_s": frame["t_s"], **counts})
        with stem.with_suffix(".csv").open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=["t_s", "Mid", "North"])
            writer.writeheader()
            writer.writerows(rows)
        for site in ("Mid", "North"):
            counts = [row[site] for row in rows]
            covered = sum(count > 0 for count in counts)
            summary.append({"inclination_deg": inclination, "site": site,
                            "samples": len(counts), "covered_samples": covered,
                            "covered_sample_fraction": covered / len(counts),
                            "mean_contact_count": sum(counts) / len(counts)})
            print(f"i={inclination}, {site}: {covered}/{len(counts)} samples covered")
    with (output / "summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(summary[0]))
        writer.writeheader()
        writer.writerows(summary)
    print(f"Open the HTML viewers and compare contact-count CSV files in {output}.")
    print("Sample fractions include both endpoints. They are not exact time coverage.")


if __name__ == "__main__":
    main()
