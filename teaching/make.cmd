@echo off
setlocal EnableExtensions DisableDelayedExpansion
if not defined LATEX_IMAGE set "LATEX_IMAGE=texlive/texlive:latest"
if not "%~2"=="" goto usage_error
if "%~1"=="" goto help
if /I "%~1"=="help" goto help
if /I "%~1"=="lecture-01" goto build
if /I "%~1"=="pdf-lecture-01" goto build
goto usage_error

:help
echo Usage: .\teaching\make.cmd lecture-01
echo Set LATEX_IMAGE to reuse a local TeX Live image.
exit /b 0

:usage_error
echo Unknown target. Use lecture-01 or pdf-lecture-01.
exit /b 2

:build
pushd "%~dp0.."
if errorlevel 1 exit /b 1
docker run --rm -v "%CD%:/work" -w /work "%LATEX_IMAGE%" sh teaching/build.sh lecture-01
set "RC=%ERRORLEVEL%"
popd
endlocal & exit /b %RC%
