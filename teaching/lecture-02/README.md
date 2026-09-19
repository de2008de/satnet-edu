# Lecture 02: Orbits, Constellations, and Coverage

[View the slides (PDF)](lecture-02.pdf) · [Edit the Beamer source](main.tex)

Ten slides, including the title page, connect orbital motion to geometric access
at a ground terminal. Instructor: Yi Ching (David) Chou.

The nine teaching slides cover:

1. Circular-orbit speed and period
2. Inclination and subsatellite latitude
3. Earth rotation and successive ground tracks
4. Orbital planes, satellite spacing, and phasing
5. Elevation masks and footprint radius
6. Contact duration for ideal overhead passes
7. Contact unions, gaps, and average satellite count
8. A latitude limit that satellite count cannot overcome
9. A controlled inclination experiment in SatNet Edu

Students should be able to calculate simple orbital and footprint quantities,
explain why an orbit period differs from a revisit time, and distinguish a
possible coverage region from continuous access at a specific location.

## Build and edit

The deck uses the shared monochrome Beamer theme and editable TikZ/PGFPlots
figures. Speaker notes in `main.tex` explain calculations and teaching prompts.

From the repository root with Docker running:

```powershell
.\teaching\make.cmd lecture-02
```

On Linux or macOS:

```sh
make -C teaching lecture-02
```

Set `LATEX_IMAGE` to reuse an installed TeX Live image. For example, use
`$env:LATEX_IMAGE = 'comp-7005-latex'` in PowerShell. Both entry points use
`teaching/build.sh`, write logs to `build/latex/lecture-02/`, and update the PDF
only after a successful build. With local TeX Live, run
`sh teaching/build.sh lecture-02`.

The CSV plot data and `geometry-values.json` come from a standard-library Python
script. Regenerate them after changing the ideal-model parameters:

```sh
python teaching/lecture-02/generate_figures.py
```

These calculations use a spherical Earth of radius 6371 km and ideal circular
orbits. The ground-track plot includes Earth rotation. The overhead-pass plot
deliberately omits it. The contact-union timeline is a constructed teaching
example. None of these figures represents measured commercial service.

## Try the final-slide experiment

After installing SatNet Edu, run from the repository root:

```sh
python teaching/lecture-02/coverage_experiment.py
```

The experiment holds altitude, satellite count, phasing, terminal locations,
epoch, elevation mask, and sampling interval fixed while comparing inclinations
of 53 and 85 degrees. It records six hours at 30-second intervals, including both
endpoints, for terminals at 50 and 70 degrees north, both at zero longitude.

Open the HTML viewers in `outputs/lecture-02/`. Contact-count CSV files and
`summary.csv` support a comparison of sampled access and interruptions. A positive
count means a ground link exists in the model. It does not establish an Internet
route or application throughput. Covered-sample fractions are not exact
continuous-time coverage, and short contacts or gaps may fall between samples.

The simulator uses its documented TLE propagation and reference constants, so
detailed contact windows differ from the ideal calculations in the slides.

## Instructor background

- [NASA: Catalog of Earth Satellite Orbits](https://science.nasa.gov/earth/earth-observatory/catalog-of-earth-satellite-orbits/)
- [ESA: Types of orbits](https://www.esa.int/Enabling_Support/Space_Transportation/Types_of_orbits)
- [SatNet Edu simulation model](../../docs/MODEL.md)
