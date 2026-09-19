# Development status

Scope: v0.1 M0–M4 only. M5 editor/challenges/service/community are deferred.

## M0
Input hashes verified. Original source audit and UTC/ECEF ADR recorded.
Command: `.venv/Scripts/python tools/legacy_fixture.py`.
Result: 6 satellites × 3 samples saved to tests/fixtures/legacy-usergs.json.
Commit: 466edc3. No original batch experiment is run.
Licensing unresolved; local development continues, public release is not authorized.

## M1
Extracted UserGS TLE/PyEphem path and immutable positions; generated
`examples/data/minimal.json`. Minimal file-import/seek page in web/demo/minimal.html.
`.venv/Scripts/python -m pytest -q`: 2 passed (TLE exact, position/distance regression,
sampling). `.venv/Scripts/python tools/smoke_m1.py`: browser file import/seek check.
Route capability explicitly false in this first trace. Full contract and player follow.

## M2
M1 commit: da5021a; file:// import and seek passed in Edge headless.
Implemented generic GS, manual satellites with distance policy, immutable snapshots,
neighbor candidates + Earth/range/elevation filtering, endpoint-only GS paths,
delay/hops deterministic routing, scenario roundtrip and half-open scheduled failures.
Trace schemas and semantic validators enforce the sampling grid and recorded paths.
`.venv/Scripts/python -m pytest -q -p no:cacheprovider`: 25 passed.
`python -m satnet_edu validate examples/data/minimal.json`: 5 samples valid.
Example HTML export is completed in M3; its final run is recorded under M4.
