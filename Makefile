NAME := vigigraph

all: qooxdoo build

qooxdoo:
	make -C javascript build
	cp -f javascript/build/script/vigigraph.js vigigraph/public/js
	cp -rf javascript/build/resource vigigraph/public/

clean_qooxdoo:
	$(RM) vigigraph/public/js/vigigraph.js
	$(RM) -r vigigraph/public/resource
	$(RM) -r javascript/build/

install: qooxdoo
	$(PYTHON) setup.py install --single-version-externally-managed --root=$(DESTDIR) --record=INSTALLED_FILES
	mkdir -p $(DESTDIR)$(HTTPD_DIR)
	ln -f -s $(SYSCONFDIR)/vigilo/$(NAME)/$(NAME).conf $(DESTDIR)$(HTTPD_DIR)/
	echo $(HTTPD_DIR)/$(NAME).conf >> INSTALLED_FILES

include buildenv/Makefile.common

MODULE := $(NAME)
CODEPATH := $(NAME)
lint: lint_pylint
tests: tests_nose
clean: clean_python clean_qooxdoo
