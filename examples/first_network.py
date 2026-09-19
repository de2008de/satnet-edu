from satnet_edu import Network

def make_network():
    net=Network('Vancouver → Tokyo',epoch='2000-01-01T00:00:00Z',seed=42)
    net.add_constellation(planes=6,sats_per_plane=12,altitude_km=1000,inclination_deg=53)
    net.add_ground_station('A',lat=49.28,lon=-123.12,label='Vancouver')
    net.add_ground_station('B',lat=35.68,lon=139.69,label='Tokyo')
    net.set_link_policy(topology='orbital_neighbors',max_isl_km=4000,min_elevation_deg=10)
    return net

if __name__=='__main__':
    run=make_network().run(duration_s=1800,step_s=5,record_routes=[('A','B')])
    print(run.save('outputs/experiment.json'))
    print(run.export_html('outputs/experiment.html'))
    print('Reachable samples:',sum(f['routes'][0]['status']=='reachable' for f in run.to_dict()['frames']),'/ 361')
