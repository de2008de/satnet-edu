# Python and player API

`Network(name, epoch="2000-01-01T00:00:00Z", seed=42, max_nodes=512,
max_samples=10000)` stores a scenario. Inputs reject booleans as numbers, non-finite
values, unknown IDs, duplicate IDs and invalid ranges. Epoch requires UTC and TLE
years 1957–2056. No current date, global RNG or background clock is consulted.
The seed is recorded; the basic deterministic model does not draw random numbers.

```python
from satnet_edu import Network, RouteQuery
net = Network("My network")
shell = net.add_constellation(planes=6, sats_per_plane=12,
                             altitude_km=1000, inclination_deg=53)
net.add_ground_station("A", lat=49.28, lon=-123.12, label="Vancouver")
net.add_ground_station("B", lat=35.68, lon=139.69, label="Tokyo")
net.set_link_policy(topology="orbital_neighbors", max_isl_km=4000,
                    min_elevation_deg=10)
snapshot = net.at(120)
route = snapshot.route("A", "B", metric="delay")
if route.reachable:
    print(route.path, route.hops, route.distance_km, route.propagation_ms)
else:
    print(route.reason)
run = net.run(duration_s=1800, step_s=5, record_routes=[
    RouteQuery("delay", "A", "B"), RouteQuery("hops", "A", "B", "hops")])
run.save("outputs/experiment.json")
run.export_html("outputs/experiment.html", language="en")
```

Constellations return an independent descriptor. First-shell IDs are `S01-01` etc.;
subsequent shells use `C02-S01-01` etc. Never parse IDs for orbital membership.
Altitude range: 100–36000 km; inclination: 0–180 degrees; RAAN/phase: 0–360 degrees;
GS latitude/longitude: -90..90 / -180..180. Numbers of planes/slots are positive
integers and must fit the node limit. These are input bounds, not a guarantee that
every orbit propagates in the inherited engine (see MODEL).

`add_satellite(id, altitude_km=..., inclination_deg=..., raan_deg=..., phase_deg=...)`
adds a manual orbit. `phase_deg` is mean anomaly at TLE epoch, not ground longitude.
Use `topology="distance"` when any satellite has no regular-shell membership.
Orbital-neighbor mode never joins separate shells by their list indices.

`add_failure(node_id=..., start_s=..., end_s=...)` records a half-open interval
`[start_s,end_s)`. Overlapping failures combine by union. `at(t_s, disabled=())`
adds temporary disabled nodes to just that snapshot; it never changes configuration.
Disabled nodes retain position but have no links. `Snapshot.nodes`, `links`, and
`kinds` are read-only ID maps of frozen records. `route()` has no side effects.

Routes expose `reachable`, `path`, `link_ids`, `hops`, `distance_km`,
`propagation_ms`, `metric`, `reason`. Unreachable metrics are None, paths empty.
Reasons are `no_path` or `endpoint_disabled`. Unknown endpoints/metrics are errors.
Enabled self queries have one node, no links and zero metrics; a disabled self query
is unreachable. GS may be endpoints but never interior relays.

`run(start_s=0, duration_s=..., step_s=..., record_routes=())` includes both endpoints,
the partial final step and every in-window failure boundary. `(source,target)` query
shorthand uses delay and IDs `query-1`, `query-2`, etc. Repeated runs are independent.
Limits default to 512 nodes / 10000 samples; configurable up to 10000 / 100000.
Distance mode considers all satellite pairs; use sensible small teaching networks.

`Network.to_dict()` returns a deep copy. `Network.from_dict()` validates and restores
the complete scenario. Actual TLE must agree with recorded orbit parameters/epoch;
use the dependency versions recorded in the trace for reruns.

`Run.to_dict()` returns a deep copy. `Run.save(path, pretty=False, max_bytes=134217728)`
validates and returns an absolute Path. `satnet_edu.load(path, max_bytes=...)` performs
strict JSON/schema/semantic validation. `Run.export_html(path, language="en")` accepts
en/zh, validates and packages existing records only. Default file protection is
128 MiB. No silent decimation. JSON serialization rejects NaN and Infinity.

## Embedding

Classic script (also works from local files):

```html
<div id="viewer"></div>
<script src="satnet-edu-player.js"></script>
<script>
const player = SatNetEduPlayer.createPlayer(document.getElementById("viewer"), {
  language: "en", showInspector: false, maxBytes: 134217728
});
// await player.load(traceObject) or player.load(jsonString)
</script>
```

HTTP-hosted ESM: `import {createPlayer} from './esm/satnet-edu-player.js'`.
`load()` validates and copies input, pauses and replaces old data; errors are shown
in the component and reject its promise. Methods: `play()`, `pause()`, `seek(seconds)`,
`setSpeed(simulationSecondsPerRealSecond)`, `selectQuery(recordedId)`, `destroy()`.
`getState()` exposes a small independent status object for host integration/tests.
seek clamps to the recording window and selects the latest sample at or before
the requested time. Replay at end restarts. Single frames cannot play.

Each player owns a ShadowRoot and listeners. Destroy cancels RAF, aborts persistent
listeners, removes the root and releases records. No framework/server, host styles,
global element IDs, remote assets, telemetry, propagation or routing dependency.
Nodes/links can be selected from the keyboard-accessible inspector list. File input
and drag/drop read only the user-selected file, without uploads.
