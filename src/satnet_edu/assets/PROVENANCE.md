# Provenance

Source: preserved `handoff/inputs/UserGS_simulation-main.zip` (hash in LEGACY_AUDIT).
Research context: *Commercial Dishes Can Be My Ladder: Sustainable and Collaborative
Data Offloading in LEO Satellite Networks*, IEEE INFOCOM 2025,
DOI 10.1109/INFOCOM55648.2025.11044527. Paper PDF was not supplied or reproduced.

| Archived source | New location / treatment |
|---|---|
| helpers/generate_tle.py:63–141 | engine/orbit.py: TLE initialization, phases, RAAN; epoch repair |
| helpers/orbital_period.py, mean_motion.py | engine/orbit.py: original period constants and conversion |
| helpers/read_tles.py:62–79 | engine/orbit.py: readtle; explicit UTC replaces TDB label |
| models/constellation.py:21–54 | network.py + engine/usergs_adapter.py: generation and compute loop, decoupled |
| models/satellite.py:119–138 | original function executed for regression; new ECEF conversion validated against it |
| models/topology.py:10–55 | engine/topology.py: neighbor formulas, explicit IDs, no loops |
| simulation.py | engine/clock.py: new pure sampling implementation; inherited time/event organization |
| models/task.py:47–51 | engine/routing.py: new deterministic shortest-path implementation, no Task/Bid |
| UI lab.css/html + coastlines.json | web/player/src: visual adaptation and unchanged local map asset |

New work: generic GroundStation, immutable snapshots, explicit UTC/scenario validation,
physical link filtering, endpoint-only GS routing, scheduled faults, trace schema and
recorder, playback-only player, safe offline export, tests and documentation.

The old UI `satlab/model.py` is NOT used. Its JavaScript routing/failure model is NOT
used. Original research auction, energy and offloading models are outside v0.1.
No paper plots or full experiments have been reproduced. See TEST_REPORT for actual
regression results. No IEEE endorsement or public-release permission is implied.
