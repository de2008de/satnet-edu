# Lecture 01: Satellite Network Architecture

An introduction to LEO satellite networking, following a packet from a user
terminal through space and ground infrastructure to a server. Worked examples
connect orbital geometry to the network behavior a user experiences.

[View the slides (PDF)](lecture-01.pdf) · [Edit the Beamer source](main.tex)

The lecture contains one title slide and nine teaching slides:

1. The complete Internet access path
2. Altitude, propagation time, and orbital motion
3. Elevation, slant range, and usable contacts
4. Constellation planes, inclination, and satellite spacing
5. Spot beams, shared capacity, and bottlenecks
6. Ground relays and inter-satellite routes
7. Contact windows and handover
8. End-to-end delay and round-trip time
9. A changing graph and competing routing objectives

After this lecture, students should be able to trace an end-to-end path, explain
why the path can change for a stationary user, distinguish coverage from capacity,
and reason about propagation delay, complete Internet latency, and route selection.

Numerical examples are geometric calculations or explicitly stated teaching
scenarios. The diagrams describe generic architectures. LaTeX speaker notes
include derivations, teaching prompts, and background sources for instructors.

## Editing

The deck is native LaTeX Beamer. Edit [main.tex](main.tex), the reusable
[monochrome theme](../satnetslides.sty), and the [TikZ icons](icons.tex).
Figures are TikZ paths, tables use `booktabs`, and the contact-window plot uses
PGFPlots with [numeric data](contact-windows.csv). No PowerPoint or image-generation
runtime is required.

Build from the repository root on Windows with Docker Desktop running:

```powershell
.\teaching\make.cmd lecture-01
```

On Linux or macOS with Docker and GNU Make:

```sh
make -C teaching lecture-01
```

The default image is `texlive/texlive:latest`. Set `LATEX_IMAGE` to reuse an
installed TeX Live image. For example, in PowerShell:

```powershell
$env:LATEX_IMAGE = 'comp-7005-latex'
.\teaching\make.cmd lecture-01
```

With a local TeX Live installation, run `sh teaching/build.sh lecture-01`, or
run `latexmk -pdf -jobname=lecture-01 main.tex` inside this directory.
Both Docker entry points use the same build script and pdfLaTeX engine. Build
files and logs go to `build/latex/lecture-01/`. A successful build updates
`teaching/lecture-01/lecture-01.pdf`. A failed build leaves the published PDF intact.

The default handout has exactly ten pages. The `studenthandout` switch in
`main.tex` changes the Beamer class mode. Add explicit overlay specifications
if a future teaching version needs progressive reveals.
