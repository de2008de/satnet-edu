LATEX_IMAGE ?= texlive/texlive:latest
REPO_DIR := $(abspath ..)

.PHONY: help lecture-01 pdf-lecture-01
help:
	@echo 'make lecture-01 [LATEX_IMAGE=your-local-texlive-image]'

lecture-01: pdf-lecture-01
pdf-lecture-01:
	docker run --rm -v "$(REPO_DIR):/work" -w /work "$(LATEX_IMAGE)" sh teaching/build.sh lecture-01
