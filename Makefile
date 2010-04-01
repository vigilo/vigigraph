NAME := vigigraph

all: build

qooxdoo:
	make -C javascript build
	cp -f javascript/build/script/vigigraph.js vigigraph/public/js
	cp -rf javascript/build/resource vigigraph/public/

clean_qooxdoo:
	$(RM) vigigraph/public/js/vigigraph.js
	$(RM) -r vigigraph/public/resource
	$(RM) -r javascript/build/

include buildenv/Makefile.common

MODULE := $(NAME)
CODEPATH := $(NAME)
lint: lint_pylint
tests: tests_nose
clean: clean_python clean_qooxdoo
