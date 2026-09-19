LATEX_IMAGE ?= texlive/texlive:latest
REPO_DIR := $(abspath ..)

.PHONY: help lecture-01 pdf-lecture-01 lecture-02 pdf-lecture-02
help:
	@echo 'make lecture-01|lecture-02 [LATEX_IMAGE=your-local-texlive-image]'

lecture-01: pdf-lecture-01
pdf-lecture-01:
	docker run --rm -v "$(REPO_DIR):/work" -w /work "$(LATEX_IMAGE)" sh teaching/build.sh lecture-01

lecture-02: pdf-lecture-02
pdf-lecture-02:
	docker run --rm -v "$(REPO_DIR):/work" -w /work "$(LATEX_IMAGE)" sh teaching/build.sh lecture-02
