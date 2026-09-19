from dataclasses import asdict
from hashlib import sha256
from importlib.metadata import version
import json

from astropy.constants import G, M_earth, R_earth

from ..engine.clock import sample_times
from ..engine.geometry import EARTH_RADIUS_KM, C_KM_S
from .io import Run


def record(net, start_s, duration_s, step_s, queries):
    if queries:
        raise ValueError("route recording is not yet available in M1")
    times = sample_times(start_s, duration_s, step_s, net._failures, net.max_samples)
    scenario = net.to_dict()
    payload = dict(format="satnet-edu.trace", schema_version="1.0.0",
        producer=dict(name="satnet-edu", version="0.1.0", source_zip_sha256="93bca9f4c25352f3d8320bcb809ad3d593c91bf697b722a4e830a2e24ecdb2dc",
                      dependencies={p: version(p) for p in ["ephem", "sgp4", "astropy"]}),
        experiment=dict(id=sha256(json.dumps(scenario, sort_keys=True).encode()).hexdigest()[:16],
                        name=net.name, epoch_utc=net.epoch, seed=net.seed, scenario=scenario),
        model=dict(propagator="UserGS synthetic TLE + PyEphem SGP4/SDP4", earth_model="sphere", earth_radius_km=EARTH_RADIUS_KM,
                   latitude_kind="geocentric", coordinate_frame="ECEF", units=dict(length="km", angle="deg", time="s", delay="ms"),
                   c_km_s=C_KM_S, tle_gravity_model="WGS72", orbit_radius_constant_m=R_earth.value,
                   orbit_mu_m3_s2=(G.value*M_earth.value), link_policy=scenario["link_policy"],
                   delay_model="one-way propagation only", limitations=["No queues, traffic, processing, protocol convergence or energy model", "Spherical educational link geometry"]),
        recording=dict(start_s=start_s, end_s=start_s+duration_s, step_s=step_s, sample_count=len(times),
                       route_queries=[], capabilities=dict(routes=False, energy=False, packet_events=False)),
        objects=sorted(scenario["objects"], key=lambda o: o["id"]), frames=[], events=[])
    for t in times:
        snap = net.at(t)
        payload["frames"].append(dict(t_s=t, node_states=[asdict(n) for n in snap.nodes.values()], links=[], routes=[]))
    return Run(payload)
