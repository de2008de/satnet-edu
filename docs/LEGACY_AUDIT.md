# M0: original framework audit

Inputs are preserved unmodified in `handoff/inputs`. Extract with PowerShell
`Expand-Archive handoff/inputs/UserGS_simulation-main.zip legacy` to rerun
`.venv/Scripts/python tools/legacy_fixture.py`. Never run the batch `source/main.py`.

SHA-256:
- UserGS: `93bca9f4c25352f3d8320bcb809ad3d593c91bf697b722a4e830a2e24ecdb2dc`
- UI: `1dc40a366d46a1daeec06e896c2cf491af4f1f5966a573ca1e2e792a39deeeef`

The fixture executes the archived `generate_tle_for_sat`, `tle_to_ephem`, and
`Satellite.distance_from` directly, using six satellites at 0, 60, 600 seconds.
Lightweight containers avoid instantiating Battery. It does not use the old UI engine.

Observed issues and decisions:
- `generate_tle.py:127` rewrites both designator and epoch to 2000 day 1. Preserve
  original mean motion, WGS72, eccentricity 1e-7, and alternating half-slot phases;
  replace only the designator columns and recompute the checksum in the adapter.
- `read_tles.py:70` labels the numeric epoch TDB. Original simulation passes calendar
  strings into PyEphem. New API uses explicit UTC dates and does not convert this
  mislabeled TDB value to UTC (which would shift the intended calendar instant).
- Satellite construction samples NumPy global RNG for Battery. Constellation imports
  user/traffic/timezone data. Neither is necessary for propagation; decouple both.
- Topology assumes list-index IDs and creates self loops for tiny constellations.
  Keep neighbor rules using explicit (plane, slot) maps, then remove loops/duplicates.
- `routing.route_traffic` mutates power, traffic, offload and research statistics.
  New read-only routing must not call it. `task.py` uses NetworkX shortest paths.
- `simulation.register(args=[])` has a mutable default; time/event organization is
  retained conceptually, using a pure sampling grid and explicit failure boundaries.
- `helpers/distance.py` imports absent `tles.generate_tle`; do not import it wholesale.
- Requirements include unused `common`, plotting/statistical packages and omit some
  transitive imports such as scipy. No attempt was made to install the entire list.

Runtime selection: Python 3.11; ephem, sgp4, astropy (original period constants),
jsonschema (data contract). No server, commercial dishes, energy, users, plotting,
timezonefinder, or networkx runtime dependency is needed by the extracted core.
pytest/build/playwright are development tools only. Actual versions are in fixture
and `requirements-lock.txt`. The archive has no top-level license.
