$ErrorActionPreference = 'Stop'
$taskRoot = Split-Path -Parent $PSScriptRoot
$env:UV_CACHE_DIR = Join-Path $taskRoot '.cache\uv'
$taskPython = Join-Path $taskRoot '.venv\Scripts\python.exe'
Push-Location $taskRoot
try {
    & $taskPython -m build --wheel --no-isolation
    if ($LASTEXITCODE -ne 0) { throw 'Wheel build failed' }
    uv venv --python $taskPython .venv-clean
    if ($LASTEXITCODE -ne 0) { throw 'Clean environment creation failed' }
    uv pip install --offline --python .venv-clean\Scripts\python.exe dist\satnet_edu-0.1.0-py3-none-any.whl
    if ($LASTEXITCODE -ne 0) { throw 'Clean wheel installation failed' }
    $cleanPython = Join-Path $taskRoot '.venv-clean\Scripts\python.exe'
    $checkDir = Join-Path $taskRoot 'test-results\clean-install'
    New-Item -ItemType Directory -Force $checkDir | Out-Null
    Push-Location $checkDir
    try {
        foreach ($example in @('first_network', 'compare_routes', 'scheduled_failure', 'custom_constellation', 'minimal')) {
            & $cleanPython (Join-Path $taskRoot "examples\$example.py")
            if ($LASTEXITCODE -ne 0) { throw "Clean example failed: $example" }
        }
        & $cleanPython -m satnet_edu validate outputs\experiment.json
        if ($LASTEXITCODE -ne 0) { throw 'Clean CLI validation failed' }
        & $cleanPython -m satnet_edu export-html outputs\experiment.json --output outputs\cli-export.html
        if ($LASTEXITCODE -ne 0) { throw 'Clean CLI export failed' }
        & $cleanPython -c "import satnet_edu; print('Installed package:', satnet_edu.__file__)"
    } finally { Pop-Location }
} finally { Pop-Location }
