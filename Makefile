NAME := vigigraph

SUBST_FILES := \
	deployment/logrotate.conf \
	deployment/settings.ini   \
	deployment/vigigraph.conf \
	deployment/vigigraph.wsgi

all: build
build: $(SUBST_FILES)

include buildenv/Makefile.common.python
MODULE := $(NAME)
EPYDOC_PARSE := vigigraph\.controllers
JSFILES = vigigraph/public/js

deployment/%: deployment/%.in
	sed -e 's,@SYSCONFDIR@,$(SYSCONFDIR),g' \
	    -e 's,@HTTPD_USER@,$(HTTPD_USER),g' \
	    -e 's,@NAGIOS_BIN@,$(NAGIOS_BIN),g' \
	    -e 's,@LOCALSTATEDIR@,$(LOCALSTATEDIR),g' $^ > $@

install: build install_python install_data
install_pkg: build install_python_pkg install_data

install_python: $(PYTHON) $(SUBST_FILES)
	$(PYTHON) setup.py install --record=INSTALLED_FILES
install_python_pkg: $(PYTHON)
	$(PYTHON) setup.py install --single-version-externally-managed \
		$(SETUP_PY_OPTS) --root=$(DESTDIR) --record=INSTALLED_FILES

install_data: $(SUBST_FILES)
	# Permissions de la conf
	chmod a+rX -R $(DESTDIR)$(SYSCONFDIR)/vigilo/$(NAME)
	[ `id -u` -ne 0 ] || chgrp $(HTTPD_USER) $(DESTDIR)$(SYSCONFDIR)/vigilo/$(NAME)/*.ini
	chmod 640 $(DESTDIR)$(SYSCONFDIR)/vigilo/$(NAME)/*.ini
	# Apache
	mkdir -p $(DESTDIR)$(HTTPD_DIR)
	ln -f -s $(SYSCONFDIR)/vigilo/$(NAME)/$(NAME).conf $(DESTDIR)$(HTTPD_DIR)/$(PKGNAME).conf
	echo $(HTTPD_DIR)/$(PKGNAME).conf >> INSTALLED_FILES
	mkdir -p $(DESTDIR)$(LOCALSTATEDIR)/log/vigilo/$(NAME)
	[ `id -u` -ne 0 ] || chown $(HTTPD_USER): $(DESTDIR)$(LOCALSTATEDIR)/log/vigilo/$(NAME)
	install -m 644 -p -D deployment/logrotate.conf $(DESTDIR)/etc/logrotate.d/$(PKGNAME)
	# Installation du app_cfg.py
	install -m 644 -p app_cfg.py $(DESTDIR)$(SYSCONFDIR)/vigilo/$(NAME)/
	# Cache
	mkdir -p $(DESTDIR)$(LOCALSTATEDIR)/cache/vigilo/sessions
	chmod 750 $(DESTDIR)$(LOCALSTATEDIR)/cache/vigilo/sessions
	[ `id -u` -ne 0 ] || chown $(HTTPD_USER): $(DESTDIR)$(LOCALSTATEDIR)/cache/vigilo/sessions

lint: lint_pylint
tests: tests_nose
doc: apidoc sphinxdoc
clean: clean_python
	rm -f $(SUBST_FILES)

.PHONY: install_pkg install_python install_python_pkg install_data
