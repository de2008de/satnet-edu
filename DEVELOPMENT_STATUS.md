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
