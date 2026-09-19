from satnet_edu import Network

net = Network("Original propagation · six satellites")
net.add_constellation(planes=2, sats_per_plane=3, altitude_km=1000, inclination_deg=53)
run = net.run(duration_s=120, step_s=30)
print(run.save("examples/data/minimal.json"))
