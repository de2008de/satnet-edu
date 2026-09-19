#!/bin/sh
# Called inside the LaTeX container, or locally with TeX Live installed.
set -eu
case "${1:-}" in
  lecture-01) deck=lecture-01 ;;
  *) echo 'Usage: sh teaching/build.sh lecture-01' >&2; exit 2 ;;
esac
teaching_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
repo_dir=$(CDPATH= cd -- "$teaching_dir/.." && pwd)
cache_dir="$repo_dir/build/latex/$deck"
mkdir -p "$cache_dir"
cd "$teaching_dir/$deck"
if latexmk -pdf -interaction=nonstopmode -halt-on-error -file-line-error \
    -jobname="$deck" -outdir="$cache_dir" main.tex > "$cache_dir/compile.stdout" 2>&1; then
  cp "$cache_dir/$deck.pdf" "$teaching_dir/$deck/$deck.pdf"
  echo "Wrote teaching/$deck/$deck.pdf"
else
  result=$?
  tail -n 60 "$cache_dir/compile.stdout"
  exit "$result"
fi
