# Satellite Networking: A Five-Lecture Introduction

Five English lectures connect satellite-network architecture to orbital coverage,
routing, changing connections, and reproducible experiments. Each lecture has
one title slide and nine teaching slides, with editable monochrome TikZ/PGFPlots
figures and instructor notes in native LaTeX Beamer.

Instructor: **Yi Ching (David) Chou**.

| Lecture | Topic | Slides | Source |
|---|---|---|---|
| 01 | [Satellite Network Architecture](lecture-01/README.md) | [PDF](lecture-01/lecture-01.pdf) | [TeX](lecture-01/main.tex) |
| 02 | [Orbits, Constellations, and Coverage](lecture-02/README.md) | [PDF](lecture-02/lecture-02.pdf) | [TeX](lecture-02/main.tex) |
| 03 | [Links, Topology, and Routing](lecture-03/README.md) | [PDF](lecture-03/lecture-03.pdf) | [TeX](lecture-03/main.tex) |
| 04 | [Dynamics, Handover, and Performance](lecture-04/README.md) | [PDF](lecture-04/lecture-04.pdf) | [TeX](lecture-04/main.tex) |
| 05 | [Designing and Evaluating Satellite Networks](lecture-05/README.md) | [PDF](lecture-05/lecture-05.pdf) | [TeX](lecture-05/main.tex) |

Students should know basic networking concepts such as packets, links, and paths.
The lectures explain the additional orbital geometry and graph concepts they use.
Companion Python experiments assume an installed copy of SatNet Edu.

The companion [Lab 01: Experiments with SatNet Edu](lab-01/README.md) walks
students through installation, recording, interactive inspection, and a
controlled failure comparison in ten slides:
[PDF](lab-01/lab-01.pdf) · [TeX](lab-01/main.tex) · [Python script](lab-01/experiment.py).

## Build the slides

From the repository root, with Docker running:

```powershell
.\teaching\make.cmd lecture-03
.\teaching\make.cmd lecture-04
.\teaching\make.cmd lecture-05
.\teaching\make.cmd lab-01
```

On Linux or macOS, use `make -C teaching lecture-03`, with the corresponding
number for another lecture. Both entry points accept `lecture-01` through
`lecture-05`, `lab-01`, and equivalent `pdf-lecture-NN` / `pdf-lab-01` aliases.

The default image is `texlive/texlive:latest`. To reuse a local image on Windows,
set `$env:LATEX_IMAGE = 'comp-7005-latex'` before building. With local TeX Live,
run `sh teaching/build.sh lecture-03` instead.

Each target compiles `teaching/lecture-NN/main.tex` with pdfLaTeX and latexmk,
writes logs to `build/latex/lecture-NN/`, and publishes
`teaching/lecture-NN/lecture-NN.pdf` only after success.
The lab target follows the same layout under `teaching/lab-01/` and
`build/latex/lab-01/`. With local TeX Live, use `sh teaching/build.sh lab-01`.

## Work with the material

Edit the lecture's `main.tex` directly. The shared theme is `satnetslides.sty`,
and the reusable component icons are in `lecture-01/icons.tex`. No PowerPoint,
raster image generator, or slide-authoring script is required to edit or build.

Figures distinguish ideal calculations, constructed examples, and simulator
experiments. Queueing, packet reordering, handover preparation, and transport
windows in Lecture 04 are conceptual extensions beyond the simulator's geometric
snapshot model. The [model description](../docs/MODEL.md) explains its limits.
