@echo off
setlocal EnableExtensions DisableDelayedExpansion
if not defined LATEX_IMAGE set "LATEX_IMAGE=texlive/texlive:latest"
if not "%~2"=="" goto usage_error
if "%~1"=="" goto help
if /I "%~1"=="help" goto help
if /I "%~1"=="lecture-01" goto lecture01
if /I "%~1"=="pdf-lecture-01" goto lecture01
if /I "%~1"=="lecture-02" goto lecture02
if /I "%~1"=="pdf-lecture-02" goto lecture02
goto usage_error

:help
echo Usage: .\teaching\make.cmd lecture-01 or lecture-02
echo Set LATEX_IMAGE to reuse a local TeX Live image.
exit /b 0

:usage_error
echo Unknown target. Use lecture-01 or lecture-02. Both accept a pdf- prefix.
exit /b 2

:lecture01
set "DECK=lecture-01"
goto build

:lecture02
set "DECK=lecture-02"
goto build

:build
pushd "%~dp0.."
if errorlevel 1 exit /b 1
docker run --rm -v "%CD%:/work" -w /work "%LATEX_IMAGE%" sh teaching/build.sh "%DECK%"
set "RC=%ERRORLEVEL%"
popd
endlocal & exit /b %RC%
