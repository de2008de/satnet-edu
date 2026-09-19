"""Ground endpoints placed beneath real t=0 satellite samples; no fake links."""

from satnet_edu import Network, RouteQuery


def make_network():
    net = Network("A recorded outage · failure and recovery")
    net.add_constellation(
        planes=2, sats_per_plane=12, altitude_km=1000, inclination_deg=53
    )
    snapshot = net.at(0)
    a, b = snapshot.nodes["S01-01"], snapshot.nodes["S01-02"]
    net.add_ground_station("A", lat=a.lat_deg, lon=a.lon_deg, label="Ground A")
    net.add_ground_station("B", lat=b.lat_deg, lon=b.lon_deg, label="Ground B")
    net.add_ground_station("Polar", lat=-90, lon=0, label="Outside coverage")
    net.add_failure(node_id="S01-02", start_s=70, end_s=140)
    net.add_failure(node_id="A", start_s=100, end_s=180)
    return net


if __name__ == "__main__":
    run = make_network().run(
        duration_s=300,
        step_s=5,
        record_routes=[
            RouteQuery("A-B-delay", "A", "B"),
            RouteQuery("A-B-hops", "A", "B", "hops"),
            RouteQuery("A-Polar", "A", "Polar"),
        ],
    )
    print(run.save("examples/data/scheduled-failure.json"))
    print(run.export_html("outputs/scheduled-failure.html"))
