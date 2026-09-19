from satnet_edu import Network

if __name__ == "__main__":
    net = Network(
        "Custom orbits · explicit mean anomalies", epoch="2025-06-02T12:00:00Z"
    )
    for i, phase in enumerate([0, 25, 50]):
        net.add_satellite(
            f"Test-{i + 1}",
            altitude_km=1000,
            inclination_deg=60,
            raan_deg=20,
            phase_deg=phase,
        )
    net.set_link_policy(topology="distance", max_isl_km=5000, min_elevation_deg=10)
    run = net.run(duration_s=600, step_s=30, record_routes=[("Test-1", "Test-3")])
    print(run.save("outputs/custom-constellation.json"))
    print(run.export_html("outputs/custom-constellation.html"))
