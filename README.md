# SatNet Edu

**Build satellite networks. Explore how they work.**

An educational satellite networking toolkit with a simple Python API and an
embeddable, trace-driven web viewer. Python calculates the experiment; the viewer
plays recorded samples. Independent of any school, website or server.

v0.1 implements the M0–M4 offline workflow in the preserved development plan.
It adapts the actual UserGS synthetic TLE/PyEphem path, with newly added physical
link checks, generic ground stations, deterministic routes and immutable snapshots.
The browser never propagates satellites or calculates a route.

## Installation and quick start

Python 3.11 is the tested target. In a fresh Python 3.11 environment:

```bash
python -m pip install -e ".[dev]"
python -m pytest
python examples/first_network.py
python -m satnet_edu validate outputs/experiment.json
python -m satnet_edu export-html outputs/experiment.json --output outputs/experiment.html
```

This Windows working copy already contains a Python 3.11 environment. From PowerShell:

```powershell
.\.venv\Scripts\python.exe examples\first_network.py
.\.venv\Scripts\python.exe examples\scheduled_failure.py
```

Open `outputs/experiment.html` or `outputs/scheduled-failure.html` directly in your
browser. Python can be closed and networking disabled. The JSON importer at
`web/demo/index.html` also opens from local files; import any generated trace.
No Node.js, web server or online map service is required after installation.
HTML files can be shared offline; JSON files can be imported into the standalone player.

```python
from satnet_edu import Network, RouteQuery

net = Network("My satellite network", epoch="2000-01-01T00:00:00Z", seed=42)
net.add_constellation(planes=6, sats_per_plane=12,
                      altitude_km=1000, inclination_deg=53)
net.add_ground_station("A", lat=49.28, lon=-123.12, label="Vancouver")
net.add_ground_station("B", lat=35.68, lon=139.69, label="Tokyo")
net.set_link_policy(topology="orbital_neighbors", max_isl_km=4000,
                    min_elevation_deg=10)
run = net.run(duration_s=1800, step_s=5, record_routes=[
    RouteQuery("A-B-delay", "A", "B", "delay"),
    RouteQuery("A-B-hops", "A", "B", "hops"),
])
run.save("outputs/my-network.json")
run.export_html("outputs/my-network.html")
```

A missing path is a normal experimental result, with null metrics. Unrecorded queries
display "Not recorded"; invalid files produce a visible error. Run Python again after
changing the network, endpoints or failures; the player only selects recorded results.

The product interface, examples, exported pages and maintained documentation are in
English. Original source materials under `handoff/` are preserved unchanged as
historical evidence and are not the maintained product documentation.

## Examples and entry points

| Entry | Result |
|---|---|
| examples/first_network.py | 72 satellites, Vancouver–Tokyo, 361 samples |
| examples/compare_routes.py | delay and hops queries in the same recording |
| examples/scheduled_failure.py | satellite/GS failures, recovery and an unreachable polar endpoint |
| examples/custom_constellation.py | manual TLE parameters with distance-based candidates |
| examples/minimal.py | original six-satellite M1 position/JSON closure |
| web/demo/index.html | independent static file importer |
| web/demo/two-players.html | two isolated components, with host CSS |
| web/demo/module.html | ESM embedding, served over HTTP |

The source facade is `src/satnet_edu/network.py`. Distribution builds are
`web/player/dist/satnet-edu-player.js` (classic `SatNetEduPlayer`) and
`web/player/dist/esm/satnet-edu-player.js` (named `createPlayer` export).
Both include local coastline data and styles; the wheel includes the same classic
bundle. See [API](docs/API.md) for embedding and all Python methods.

## Development verification

```bash
python tools/build_schemas.py
python tools/build_player.py
python tools/make_fixtures.py
python -m pytest -q
node tools/module_tests.mjs
python tools/browser_tests.py
python tools/benchmark.py
python -m build --wheel --no-isolation
```

Browser tests use locally installed Microsoft Edge (Playwright channel `msedge`);
they cover offline classic exports and a temporary local static server for ESM.
They require generated example outputs, so run the four main examples first.
No Python simulation is called by either page. Node is needed only for the optional
ESM contract test, not for building or using the shipped player.
`tools/clean_install.ps1` (requires uv and cached dependency wheels) builds/installs the wheel into a separate environment and
runs examples with a working directory outside the source tree's module paths.
`tools/legacy_fixture.py` reruns the archived core after extracting its ZIP into
`legacy/`; this is an audit tool, not a runtime dependency.

See [test report](docs/TEST_REPORT.md), [trace contract](docs/TRACE_FORMAT.md),
[model](docs/MODEL.md), [migration](docs/MIGRATION.md), and
[development status](DEVELOPMENT_STATUS.md). Recorded benchmarks include file sizes,
simulation/validation time and browser load/render observations; they are not a
real-time performance promise. Default limits: 512 nodes, 10000 samples, 128 MiB files.

## Research origins and scope

Adapted from the framework used for *Commercial Dishes Can Be My Ladder:
Sustainable and Collaborative Data Offloading in LEO Satellite Networks*, IEEE
INFOCOM 2025 (DOI 10.1109/INFOCOM55648.2025.11044527). See
[provenance](docs/PROVENANCE.md) and [legacy audit](docs/LEGACY_AUDIT.md).
The old teaching UI supplies visual reference and local map outlines; its orbit and
browser-routing engines are not used. Original archives and their hashes are preserved.

The basic metric is **one-way propagation delay**, with spherical link geometry.
No queues, protocol convergence, energy, auction or paper-result replication is claimed.
Known inherited PyEphem edge cases are explicit errors, documented in MODEL.

**Public-release licensing is unresolved:** the supplied UserGS ZIP has no top-level
license and contains Hypatia-attributed code. [Third-party notices](THIRD_PARTY_NOTICES.md)
record the pending checks; no new blanket license or public publication was made.

M5+ editors, challenges, hosted execution, accounts and communities are deferred.
SatNet Edu is an independent tool; it is not exclusive to UDTJ or any institution.
