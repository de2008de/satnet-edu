# Trace 1.0.0

JSON format `satnet-edu.trace`; canonical schemas are `schemas/trace.schema.json`
and `schemas/scenario.schema.json`, copied into package assets during builds.
Unknown versions are rejected with supported version 1.0.0, never guessed.

| Field | Meaning |
|---|---|
| producer | engine/version, original archive hash, ephem/sgp4/astropy versions |
| experiment | stable configuration hash ID, name, UTC epoch, seed, complete scenario |
| model | propagator, sphere, ECEF/geocentric definitions, units, c, constants, policies, limitations |
| recording | start/end, nominal step, actual count, named queries, capabilities |
| objects | stable IDs, labels, GS coordinates or actual TLE/orbital membership |
| frames | strictly increasing full sampled node states, available links, all recorded query results |
| events | scheduled failure interval boundaries within the recording window |
| extensions | optional JSON object; cannot override core fields |

No summary field is currently generated. No energy or packet events are recorded;
capability flags remain false, and the inspector says Not recorded. A configuration
hash identifies the scenario, not a unique execution; no wall clock or random run ID
pollutes reproducibility. Node/link arrays are sorted by stable ID. Object membership
is explicit and never inferred from an ID's spelling. IDs and labels are different.

Node state: `id`, `enabled`, `position_ecef_km:[x,y,z]`, `lat_deg`, `lon_deg`,
`altitude_km`. Disabled nodes still have locations. Link: `id`, `source`, `target`,
`kind:isl|gsl`, `distance_km`, `propagation_ms`. Link IDs are unambiguous JSON-encoded
sorted endpoint pairs, treated as opaque strings by clients.

Route: `query_id`, `status:reachable|unreachable`, `node_ids`, `link_ids`, `hops`,
`distance_km`, `propagation_ms`, `reason`. Unreachable paths are empty with null
metrics and `no_path` or `endpoint_disabled`. Reachable reason is null. One result
per declared query per frame is mandatory. There is no implicit/browser-generated path.

Sampling is start + regular steps + end + in-window failure starts/ends, sorted and
deduplicated. Example: 0..10 step 4 → 0,4,8,10. Failures [3,7) add 3 and 7; states
at those instants are already updated. Duration 0 creates one frame. A player seek
to 6 chooses sample 4 in this example. Bounds clamp. Time labels use `t_s`, not index.

Both Python and JS check structure, finite values, duplicate IDs, object/query/link
references, complete sample grid, event boundaries, failure states, path endpoints,
interior GS exclusion and path metric sums. Python additionally checks spherical
coordinate/distance consistency. The player never checks physical visibility or
optimizes paths; loading a trace is not certification that its model is truthful.
JSON is user-editable. Only re-running a trusted Python scenario can reproduce it.

Maximum input/export size defaults to 128 MiB. Node/sample limits live in the
scenario. Files are not truncated; oversize inputs give an error. No pickle, plugins,
executable strings, hidden local-file reads or uploads exist. HTML embeds JSON with
<, >, &, U+2028/U+2029 escaped; labels use textContent. Map/bundled script are local.

Fixtures: `legacy-usergs.json` is raw original-engine evidence; `real-engine-route.json`,
`minimal-valid.json`, and `examples/data/*.json` are valid new traces. `invalid-*` files
are deliberately corrupted contract tests, never demos. Hand-built unit graphs only
test optimization and do not claim orbital evidence.
