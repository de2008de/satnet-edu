LATEX_IMAGE ?= texlive/texlive:latest
REPO_DIR := $(abspath ..)

.PHONY: help lecture-01 pdf-lecture-01 lecture-02 pdf-lecture-02 lecture-03 pdf-lecture-03 lecture-04 pdf-lecture-04 lecture-05 pdf-lecture-05 lab-01 pdf-lab-01
help:
	@echo 'make lecture-01 through lecture-05, or lab-01 [LATEX_IMAGE=your-local-texlive-image]'

lecture-01: pdf-lecture-01
pdf-lecture-01:
	docker run --rm -v "$(REPO_DIR):/work" -w /work "$(LATEX_IMAGE)" sh teaching/build.sh lecture-01

lecture-02: pdf-lecture-02
pdf-lecture-02:
	docker run --rm -v "$(REPO_DIR):/work" -w /work "$(LATEX_IMAGE)" sh teaching/build.sh lecture-02

lecture-03: pdf-lecture-03
pdf-lecture-03:
	docker run --rm -v "$(REPO_DIR):/work" -w /work "$(LATEX_IMAGE)" sh teaching/build.sh lecture-03

lecture-04: pdf-lecture-04
pdf-lecture-04:
	docker run --rm -v "$(REPO_DIR):/work" -w /work "$(LATEX_IMAGE)" sh teaching/build.sh lecture-04

lecture-05: pdf-lecture-05
pdf-lecture-05:
	docker run --rm -v "$(REPO_DIR):/work" -w /work "$(LATEX_IMAGE)" sh teaching/build.sh lecture-05

lab-01: pdf-lab-01
pdf-lab-01:
	docker run --rm -v "$(REPO_DIR):/work" -w /work "$(LATEX_IMAGE)" sh teaching/build.sh lab-01
