NAME := vigigraph

all: build

include buildenv/Makefile.common

MODULE := $(NAME)
CODEPATH := $(NAME)
lint: lint_pylint
tests: tests_nose
clean: clean_python
