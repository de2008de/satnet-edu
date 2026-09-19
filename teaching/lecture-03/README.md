# Lecture 03: Links, Topology, and Routing

[View the slides](lecture-03.pdf) · [Edit the Beamer source](main.tex)

One title slide and nine teaching slides, in English. Instructor:
Yi Ching (David) Chou.

1. Ground links and inter-satellite links
2. Earth blockage and the grazing-distance limit
3. Elevation, slant range, and propagation
4. Candidate topology and physical filtering
5. Weighted snapshot graphs and forwarding permissions
6. Minimum hops versus minimum propagation delay
7. A worked Dijkstra trace
8. Disconnected groups and explicit no-path results
9. Comparing objectives on the same snapshot

Students should be able to construct a graph from usable links, calculate path
costs, explain a shortest-path decision, and distinguish local coverage from
end-to-end connectivity. The weighted graphs are constructed teaching examples.
Geometric examples use a 6371 km spherical Earth.

Build from the repository root with `.\teaching\make.cmd lecture-03` on Windows
or `make -C teaching lecture-03` on Linux/macOS. See the
[course build guide](../README.md#build-the-slides).

## Experiment

After installing SatNet Edu, run from the repository root:

```sh
python teaching/lecture-03/routing_experiment.py
```

The script records both route objectives for Vancouver and Tokyo using the same
snapshots. Open `outputs/lecture-03/routing.html` and switch between the `hops`
and `delay` queries. Check whether the objectives choose different paths, then
explain the associated edge costs. The default run can select the same routes
throughout the recording. Equal answers are a valid outcome, not a failed test.

The experiment uses a synthetic 6-by-12 constellation at 1000 km and 53 degrees,
a 10-degree elevation mask, a 4000 km ISL limit, and a fixed 2026-01-01 UTC epoch.
It records 20 minutes at 10-second intervals. The printed comparison uses 120 s.

## Instructor background

- [SatNet Edu model](../../docs/MODEL.md) and [Python API](../../docs/API.md)
- [ESA: Laser communications](https://www.esa.int/Applications/Connectivity_and_Secure_Communications/EDRS/Laser_communications)

Instructor notes in `main.tex` explain the geometric calculations, graph costs,
and equal-cost choices in the shortest-path trace.
