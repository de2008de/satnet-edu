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

## M3
M2 commit: 9b186e8. Classic and ESM players are built from one source, with a
ShadowRoot per instance and the bundled original coastline asset. Offline HTML uses
the same classic bundle. No fetch, model propagation, link generation, or shortest
path implementation exists in the player. Full schema/reference/path validation runs
before playback; checking sums is validation, not route optimization.
`python tools/build_player.py`; all four main examples executed successfully.
`python tools/browser_tests.py`: passed in Edge/Chromium, offline context/file://,
zero HTTP requests and page errors. Covered import/drop, play/pause/end/seek/reload,
recorded queries, fault recovery, Chinese, 390px viewport, malicious labels, two
instances, CSS isolation and destroy. Desktop/mobile screenshots inspected.
`python -m pytest -q -p no:cacheprovider`: 26 passed.
`python -m build --wheel --no-isolation`: local wheel built; clean install follows.

## M4 — complete

M3 commit: d7f0512. M4 implementation and report are in the final `M4:` local commit
(use `git log --oneline`; avoiding a self-referential hash in this file).

- Clean Python 3.11 wheel installation tested in .venv-clean; all five examples run
  from a different working directory with imports resolving to site-packages.
- 50 Python tests passed; 2 valid/8 invalid ESM fixtures checked; full Edge browser
  integration passed, including ESM and comparison to Python's recorded metrics.
- Small, standard and larger benchmark scenarios completed; measurements and memory
  limitations recorded in docs/TEST_REPORT.md and docs/benchmark-results.json.
- README, API, trace format, model, migration and third-party notices
  describe the actual implementation. No hidden engine fallback or live server required.
- Built classic/ESM distributions are checked in, not only the Python copy; schemas,
  coastline and notices are present in the wheel. Exported HTML and both browser forms
  use the same validated player source. M1's unvalidated prototype is in Git history;
  its current demo now uses the final player.
- Original archive hashes unchanged. No blanket license or public publishing.
- Known upstream propagation edge case, browser/platform coverage limits and unmeasured
  peak memory disclosed. Custom routing callbacks, energy, editor, challenges, hosted
  execution and community remain deferred. Stop at v0.1; M5 has not been started.

Primary outputs: outputs/experiment.json and outputs/experiment.html,
outputs/scheduled-failure.html, examples/data/scheduled-failure.json, and
dist/satnet_edu-0.1.0-py3-none-any.whl. Output files can be regenerated from examples;
small real traces and browser distributions are checked into the repository.

## English edition — user-directed revision

The English edition supersedes the bilingual interface noted in the original M3
history. All maintained documentation, interface text, sample names and exported
pages now use English. The language switcher was removed; API/CLI language options
accept `en` only. Unicode user labels remain supported as data. Original files under
handoff remain unchanged as provenance records, not maintained product documentation.

Rebuilt the classic/ESM/wheel assets and offline examples, and refreshed the desktop
and mobile screenshots. Validation: 50 Python tests passed; ESM accepted 2 valid
files and rejected 8 corrupted files; English browser integration passed with zero
HTTP requests during offline tests and zero page errors.
