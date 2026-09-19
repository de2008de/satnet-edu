"""Student facade, independent of research experiment globals."""
from copy import deepcopy
from .config import DEFAULT_EPOCH, identifier, integer, number, text, utc_epoch
from .engine.orbit import generate_tle, phases


class Network:
    def __init__(self, name="My satellite network", *, epoch=DEFAULT_EPOCH, seed=42, max_nodes=512, max_samples=10000):
        self.name = text(name, "name")
        self._epoch = utc_epoch(epoch)
        self.epoch = self._epoch.isoformat().replace("+00:00", "Z")
        self.seed = integer(seed, "seed", 0, 2**53 - 1)
        self.max_nodes = integer(max_nodes, "max_nodes", 1, 10000)
        self.max_samples = integer(max_samples, "max_samples", 1, 100000)
        self._objects = []
        self._constellations = []
        self._failures = []
        self._policy = dict(topology="orbital_neighbors", max_isl_km=4000, min_elevation_deg=10)

    def _check_id(self, node_id):
        identifier(node_id)
        if any(o["id"] == node_id for o in self._objects):
            raise ValueError(f"id: duplicate {node_id}")
        if len(self._objects) >= self.max_nodes:
            raise ValueError(f"nodes: exceeds max_nodes={self.max_nodes}")

    def _satellite(self, node_id, altitude_km, inclination_deg, raan_deg, phase_deg, **extra):
        self._check_id(node_id)
        number(altitude_km, "altitude_km", 100, 36000)
        number(inclination_deg, "inclination_deg", 0, 180)
        number(raan_deg, "raan_deg", 0, 360)
        number(phase_deg, "phase_deg", 0, 360)
        params = dict(altitude_km=altitude_km, inclination_deg=inclination_deg, raan_deg=raan_deg, phase_deg=phase_deg)
        satnum = sum(o["kind"] == "satellite" for o in self._objects)
        tle = generate_tle(satnum, self._epoch, **params)
        self._objects.append(dict(id=node_id, label=node_id, kind="satellite", tle=list(tle), orbit=params, **extra))
        return node_id

    def add_constellation(self, *, planes, sats_per_plane, altitude_km, inclination_deg):
        integer(planes, "planes", 1, self.max_nodes)
        integer(sats_per_plane, "sats_per_plane", 1, self.max_nodes)
        number(altitude_km, "altitude_km", 100, 36000)
        number(inclination_deg, "inclination_deg", 0, 180)
        if len(self._objects) + planes * sats_per_plane > self.max_nodes:
            raise ValueError(f"constellation: exceeds max_nodes={self.max_nodes}")
        index = len(self._constellations) + 1
        cid = f"C{index:02}"
        prefix = "" if index == 1 else cid + "-"
        ids = [f"{prefix}S{p+1:02}-{s+1:02}" for p in range(planes) for s in range(sats_per_plane)]
        for sid in ids:
            self._check_id(sid)
        for p in range(planes):
            for s in range(sats_per_plane):
                raan, phase = phases(p, s, planes, sats_per_plane)
                self._satellite(ids[p*sats_per_plane+s], altitude_km, inclination_deg, raan, phase,
                                constellation_id=cid, plane=p, slot=s)
        descriptor = dict(id=cid, planes=planes, sats_per_plane=sats_per_plane,
                          altitude_km=altitude_km, inclination_deg=inclination_deg,
                          phase_rule="usergs_alternating_half_slot")
        self._constellations.append(descriptor)
        return deepcopy(descriptor)

    def at(self, t_s, disabled=()):
        from .engine.usergs_adapter import snapshot
        number(t_s, "t_s")
        return snapshot(self, t_s, disabled)

    def run(self, *, duration_s, step_s, start_s=0, record_routes=()):
        from .trace.recorder import record
        return record(self, start_s, duration_s, step_s, record_routes)

    def to_dict(self):
        return deepcopy(dict(format="satnet-edu.scenario", schema_version="1.0.0", name=self.name,
                             epoch_utc=self.epoch, seed=self.seed,
                             limits=dict(max_nodes=self.max_nodes, max_samples=self.max_samples),
                             constellations=self._constellations, objects=self._objects,
                             link_policy=self._policy, failures=self._failures))
