# v0.1 verification — 2026-09-19

Executed on Windows x64, Python 3.11.15, ephem 4.2.1, sgp4 2.27, astropy 8.0.1,
jsonschema 4.26.0, Playwright 1.63.0, locally installed Edge/Chromium and Node 22.13.1.
Exact Python dependency snapshot: requirements-lock.txt (no editable machine paths).

The English-edition revision reran the 50 Python tests, ESM contract checks and browser
integration successfully. Screenshots and exported examples now show the English
interface. The original performance measurements below remain unchanged; this
language revision does not alter the simulation model.

## Completed checks

| Command / check | Observed result |
|---|---|
| tools/legacy_fixture.py | actual archived UserGS: 6 satellites × 3 times |
| python -m pytest -q -p no:cacheprovider | 50 tests passed |
| ruff check src tests tools examples | passed F/I checks; Python formatted |
| node tools/module_tests.mjs | 2 valid traces accepted; 8 corrupted files rejected |
| tools/browser_tests.py | Edge integration passed; offline stage 0 HTTP requests, 0 page errors |
| tools/clean_install.ps1 | wheel installed into separate environment; all 5 examples and both CLI commands passed |
| python -m build --wheel --no-isolation | satnet_edu-0.1.0-py3-none-any.whl built locally |

Python coverage includes exact legacy TLE regression, positions/distances, Earth-fixed
rotation, UTC and nondefault epoch, negative/boolean/nonfinite input, small topology
1×1/1×3/2×3, Earth occultation, real GSL slant range, ISL range limit, independent
shells, self/unknown/unreachable/disabled routes, known optimum for both algorithms,
ID tie break, GS relay exclusion, state/RNG purity, scenario roundtrip, sample/failure
boundaries, duplicate IDs, invalid versions/references/units/metrics, serialization,
safe script embedding, synchronized shipped schemas and player assets.

Browser integration covers file:// self-contained HTML with networking disabled,
file import and drag/drop, play/pause/end/restart/seek clamping, single frame, query
switches, missing vs unreachable data, fault/recovery, visible invalid-file errors,
node inspector, English text, keyboard Enter and visible focus, fixed map viewBox,
world seam splitting at both map centers, narrow-screen overflow, malicious Unicode
labels with script/HTML tokens, two independent players, host CSS isolation, reload,
destroy and a separate HTTP-served ESM instance. Current results and paths are checked
against Python trace values for multiple queries/times. Browser screenshots were
inspected at 1440px and 390px, available in docs/images.

No simulation server runs in the offline tests. The test runner orchestrates the
browser in Python, but does not simulate during playback. The ESM-only check uses a
temporary standard-library static file server which is shut down afterward.

## Original-core regression

Same TLE text: exact match for all six satellites. Against archived UserGS outputs:

| Quantity | Maximum absolute difference | Test tolerance |
|---|---:|---:|
| geocentric latitude | 0.0000120892° | 0.0001° |
| longitude | 0.0000072682° | 0.0001° |
| satellite distance | 0.000298954 km (0.30 m) | 0.01 km |

These are finite-precision representation/coordinate-conversion differences. The
record is docs/regression-results.json. See ADR-001 for the compatible geometry.
This validates the common propagation path, not the entire original paper model.

## Measured sizes and performance

Each benchmark includes two ground stations and delay/hops queries; step 5 s.
Single observations on this machine, not best-of repetitions or performance promises.
Simulation includes constructing the Run object. Save includes full Python validation.

| Scale | Satellites / frames | JSON bytes | Simulation s | Validate + save s | Browser JSON parse ms | Clone + validate + first draw ms | Mean seek + draw ms |
|---|---:|---:|---:|---:|---:|---:|---:|
| Small | 24 / 61 | 605995 | 0.062 | 0.204 | 0.7 | 13.2 | 0.56 |
| Standard | 72 / 361 | 10445380 | 0.919 | 3.192 | 14.6 | 141.7 | 1.28 |
| Larger | 144 / 721 | 46144712 | 5.551 | 16.236 | 69.5 | 581.3 | 2.48 |

Raw observations and environment are in docs/benchmark-results.json. The browser
performance.memory reading was a coarse repeated 10.6 MB value and is **not a reliable
peak measurement**. Python/native/browser peak memory was not measured. Draw timings
measure synchronous DOM work, not GPU paint or a frame-rate guarantee. Full snapshots
trade file size for simplicity; compression and chunking are deferred.

The default 72-star first example had 361/361 reachable Vancouver–Tokyo samples.
The fault example includes reachable, endpoint-disabled, recovered and polar no-path
results. No unavailable samples are dropped or bridged by invented links.

## Packaging and remaining limits

The clean environment imports from its own site-packages, not src/. It runs examples
from test-results/clean-install. The wheel contains both JSON schemas, bundled map,
classic player/CSS, coordinate ADR and third-party notices. No fonts,
keys, private absolute paths or old research directories are bundled.

Not tested: Firefox, Safari, actual mobile devices, assistive screen readers, operating
systems other than Windows, alternative dependency versions, or continuous physical
service availability between samples. No full INFOCOM experiment/figure reproduction.
An inherited PyEphem singularity at 35786 km and exactly 0° inclination is covered by
an explicit-error test; no fallback physics is used. Public licensing remains pending.
No public package, website, repository or research claim was published.
