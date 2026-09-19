# Lecture 05: Designing and Evaluating Satellite Networks

[View the slides](lecture-05.pdf) · [Edit the Beamer source](main.tex)

One title slide and nine teaching slides, in English. Instructor:
Yi Ching (David) Chou.

1. Testable questions and model capabilities
2. Controlled baseline and failure comparisons
3. Coverage, reachability, and conditional delay
4. Sample fractions versus time-weighted estimates
5. Defined component failures and alternate paths
6. Matched comparisons and recovery
7. Resource tradeoffs and dominated designs
8. Reproducible scenarios, recordings, and viewers
9. A final network-design investigation

Students should be able to choose meaningful metrics, run a controlled comparison,
explain a result using paths and time histories, and state its limitations.
Numerical tables in the slides are explicitly constructed teaching examples.
Run the companion script to obtain actual results for its specific configuration.

Build from the repository root with `.\teaching\make.cmd lecture-05` on Windows
or `make -C teaching lecture-05` on Linux/macOS. See the
[course build guide](../README.md#build-the-slides).

## Paired failure experiment

After installing SatNet Edu, run from the repository root:

```sh
python teaching/lecture-05/experiment.py
```

The baseline uses a 6-by-12 constellation at 1000 km and 53 degrees, Vancouver
and Tokyo endpoints, a 10-degree mask, orbital-neighbor candidates, and a 4000 km
ISL limit. Both runs share epoch 2026-01-01 UTC and cover 0 to 1200 seconds at
10-second intervals, including both endpoints.

The script finds the minimum-propagation baseline path at 600 seconds and chooses
the middle interior satellite. A cloned scenario disables that satellite on
`[600, 900)`. The failure is therefore a targeted stress case. It is not a random
fleet failure or an estimate of operational reliability. The chosen ID and rule
are saved in `outputs/lecture-05/summary.json`.

Outputs in `outputs/lecture-05/`:

- `baseline.json` and `failure.json`: complete simulation recordings.
- `baseline.html` and `failure.html`: offline English viewers.
- `paired-metrics.csv`: matching timestamps, reachability, propagation delay,
  delay differences when both routes exist, and local contact counts.
- `summary.json`: sample metrics and explicitly labeled left-hold time estimates.

Missing delay values remain missing. Sample averages include the final endpoint.
Time estimates weight each state by the interval until the next frame, with no
duration assigned to the final frame. They can miss unobserved transitions.

For a design revision, keep the same failed satellite ID when it identifies a
corresponding component. Re-selecting the middle node of a new route changes the
stress case. If the constellation membership changes, define and report the
comparison rule explicitly. Examine both routes and no-path intervals, and do
not equate reachability with throughput or a propagation change with application
latency.

See the [simulation model](../../docs/MODEL.md) and [API](../../docs/API.md).
