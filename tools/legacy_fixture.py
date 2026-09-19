"""Run the actual archived UserGS path without main.py or research workloads."""
import json
import math
import sys
from importlib.metadata import version
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "legacy/UserGS_simulation-main/source"))
import ephem
from helpers.generate_tle import generate_tle_for_sat
from helpers.read_tles import tle_to_ephem
from models.satellite import Satellite


def main():
    tles = [generate_tle_for_sat(i, i // 3, i % 3, 2, 3, 53, 1000000) for i in range(6)]
    sats = [SimpleNamespace(ephem=tle_to_ephem(tle, None)[0]) for tle in tles]
    frames = []
    for seconds in [0, 60, 600]:
        date = ephem.Date(ephem.Date("2000/1/1 00:00:00") + seconds / 86400)
        obs = ephem.Observer()
        obs.date = date
        obs.lat = obs.lon = "0"
        obs.elevation = 0
        obs.pressure = 0
        states = []
        for sat in sats:
            sat.ephem.compute(obs)
            s = sat.ephem
            states.append(dict(sublat_deg=math.degrees(s.sublat), sublong_deg=math.degrees(s.sublong),
                               elevation_m=s.elevation, range_m=s.range, az_rad=float(s.az), alt_rad=float(s.alt)))
        distances = [Satellite.distance_from(sats[0], sat, SimpleNamespace(current_time=date)) / 1000 for sat in sats[1:]]
        frames.append(dict(t_s=seconds, states=states, distances_from_first_km=distances))
    data = dict(source_zip_sha256="93bca9f4c25352f3d8320bcb809ad3d593c91bf697b722a4e830a2e24ecdb2dc",
                config=dict(planes=2, sats_per_plane=3, inclination_deg=53, altitude_km=1000, epoch="2000-01-01T00:00:00Z"),
                environment={p: version(p) for p in ["ephem", "sgp4", "astropy", "numpy"]},
                python=sys.version.split()[0], tles=tles, frames=frames,
                legacy_epoch_label=str(tle_to_ephem(tles[0], None)[1]),
                legacy_epoch_scale=tle_to_ephem(tles[0], None)[1].scale)
    path = ROOT / "tests/fixtures/legacy-usergs.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(f"Original UserGS: {len(sats)} satellites, {len(frames)} samples -> {path.name}")


if __name__ == "__main__":
    main()
