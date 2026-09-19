"""Compare routing objectives on identical SatNet Edu snapshots."""

from pathlib import Path

from satnet_edu import Network, RouteQuery


def main():
    net = Network("Lecture 03: routing objectives", epoch="2026-01-01T00:00:00Z")
    net.add_constellation(planes=6, sats_per_plane=12, altitude_km=1000,
                          inclination_deg=53)
    net.add_ground_station("A", lat=49.28, lon=-123.12, label="Vancouver")
    net.add_ground_station("B", lat=35.68, lon=139.69, label="Tokyo")
    net.set_link_policy(topology="orbital_neighbors", max_isl_km=4000,
                        min_elevation_deg=10)
    snapshot = net.at(120)
    for metric in ("hops", "delay"):
        route = snapshot.route("A", "B", metric=metric)
        if route.reachable:
            print(metric, route.path, route.hops, route.propagation_ms)
        else:
            print(metric, route.reason)
    run = net.run(duration_s=1200, step_s=10, record_routes=[
        RouteQuery("hops", "A", "B", "hops"),
        RouteQuery("delay", "A", "B", "delay"),
    ])
    output = Path("outputs/lecture-03")
    output.mkdir(parents=True, exist_ok=True)
    run.save(output / "routing.json")
    run.export_html(output / "routing.html", language="en")
    print(f"Open {output / 'routing.html'} and switch between the two queries.")


if __name__ == "__main__":
    main()
