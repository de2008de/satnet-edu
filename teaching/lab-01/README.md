# Lab 01: Experiments with SatNet Edu

A guided Vancouver–Tokyo experiment, from installation to an explained failure
comparison. The English deck contains one title slide and nine lab slides in
the same monochrome Beamer style as the five lectures.

Instructor: **Yi Ching (David) Chou**.

- [Slides (PDF)](lab-01.pdf)
- [Editable Beamer source](main.tex)
- [Complete experiment](experiment.py)

## Set up and run

You need Git, Python 3.11, a text editor, and a browser. Internet access is needed
for cloning and installation. The exported viewers run offline without a server,
Node.js, Docker, or LaTeX.

If you already have the repository, enter its root folder and skip the clone.
Use the same virtual-environment interpreter for installation and execution.

### Windows PowerShell

```powershell
git clone https://github.com/de2008de/satnet-edu.git
cd satnet-edu
py -3.11 -m venv .venv
$py = ".\.venv\Scripts\python.exe"
& $py -m pip install .
& $py -c "import satnet_edu; print('OK')"
& $py teaching/lab-01/experiment.py
```

Keep this PowerShell window open so `$py` remains defined. In a new window,
enter the repository root and define `$py` again before running the script.

### macOS and Linux

```bash
git clone https://github.com/de2008de/satnet-edu.git
cd satnet-edu
python3.11 -m venv .venv
.venv/bin/python -m pip install .
.venv/bin/python -c "import satnet_edu; print('OK')"
.venv/bin/python teaching/lab-01/experiment.py
```

Some Linux distributions require their Python 3.11 venv package to create the
environment. Install that package if the venv command reports it missing.

## Follow the experiment

1. Read the numbered sections in `experiment.py`. The scenario fixes its epoch,
   72-satellite constellation, ground sites, and link rules.
2. Inspect the route at 120 seconds. The supplied scenario gives four links and
   approximately 35.307 ms of one-way propagation.
3. Record 1200 seconds at a 10-second interval. The start and end are included,
   giving 121 samples per case.
4. Open `outputs/lab-01/baseline.html` in your browser. Select the **delay**
   query, pause at 120 seconds, and inspect its path and link distances.
5. Compare it with `outputs/lab-01/failure.html`. The script disables the middle
   satellite on the baseline route at 600 seconds. For this scenario that is
   **S04-03**, disabled from 600 seconds up to, but not including, 900 seconds.
6. Read `summary.json` and `paired.csv`. Compare the two recorded paths at
   matching times such as 600, 700, and 900 seconds.

All generated files are under `outputs/lab-01/`:

| File | Purpose |
|---|---|
| `baseline.json`, `failure.json` | Complete recorded network states and route answers |
| `baseline.html`, `failure.html` | Standalone interactive viewers |
| `summary.json` | Failure selection and aggregate metrics for both cases |
| `paired.csv` | Matching timestamps, route statuses, paths, delays, and delay differences |

The checked reference run is reachable at all 121 samples in both cases. Mean
one-way propagation is approximately **35.584 ms** for the baseline and
**35.805 ms** for the failure case. An outage can cause a detour while preserving
connectivity. Explain the actual paths rather than assuming every outage must
disconnect the endpoints.

Reachability uses all recorded samples as its denominator. Mean delay uses only
samples with a reachable route. A missing route has no valid delay and must not
be replaced with zero. These are sampled geometric results, not measurements of
continuous availability, throughput, or complete application latency.

## Submit and extend

Submit your Python script, both JSON recordings, both HTML viewers, and a short
report containing your prediction, the failure ID and interval, one matched path
comparison, both metric definitions, and an explanation of the outcome. Include
the summary and CSV to make the numerical comparison easy to reproduce.

For a sampling experiment, first copy the entire `outputs/lab-01/` folder to a
different name. The script overwrites its named outputs on every run. Change
`step_s=10` to `step_s=5` in the shared `record` function, then rerun. Keep all
other settings unchanged. Each case now has 241 samples over the same 1200-second
window. Compare the metrics and discuss why finer sampling can reveal changes
between earlier samples without proving that every transition was observed.

## Troubleshooting

- **Import fails:** use the virtual-environment interpreter shown above for
  both `pip install .` and execution. Run from the repository root.
- **The viewer says Not recorded:** add the query to `record_routes`, rerun the
  Python script, and reopen the newly exported HTML.
- **A sample has no path:** check endpoint IDs, ground access, usable links, and
  failures. This is a valid network result, distinct from an unrecorded query.
- **Outputs appear elsewhere:** paths are relative to the current working
  directory. Enter the repository root before running the script.

## Build the slides

With Docker running, use `.\teaching\make.cmd lab-01` on Windows or
`make -C teaching lab-01` on macOS/Linux. Both also accept `pdf-lab-01`.
See the [course build guide](../README.md#build-the-slides) for the image override
and local TeX option. The experiment itself does not require a slide build.
