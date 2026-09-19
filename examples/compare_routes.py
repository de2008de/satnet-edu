from first_network import make_network

from satnet_edu import RouteQuery

if __name__ == "__main__":
    run = make_network().run(
        duration_s=300,
        step_s=5,
        record_routes=[
            RouteQuery("A-B-delay", "A", "B", "delay"),
            RouteQuery("A-B-hops", "A", "B", "hops"),
        ],
    )
    print(run.save("outputs/compare-routes.json"))
    print(run.export_html("outputs/compare-routes.html"))
