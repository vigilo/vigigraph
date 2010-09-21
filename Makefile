NAME := vigigraph
QOOXDOO_VER := 0.7.3

all: qooxdoo build

include buildenv/Makefile.common
PKGNAME := $(NAME)
MODULE := $(NAME)
CODEPATH := $(NAME)
EPYDOC_PARSE := vigigraph\.controllers

qooxdoo_source: javascript/qooxdoo-$(QOOXDOO_VER)-sdk/frontend/Makefile
javascript/qooxdoo-$(QOOXDOO_VER)-sdk.tar.gz:
	#wget -P javascript/ http://downloads.sourceforge.net/project/qooxdoo/qooxdoo-legacy/$(QOOXDOO_VER)/qooxdoo-$(QOOXDOO_VER)-sdk.tar.gz
	wget -P javascript/ http://vigilo-dev.si.c-s.fr/cache/qooxdoo-$(QOOXDOO_VER)-sdk.tar.gz
	touch --no-create $@
javascript/qooxdoo-$(QOOXDOO_VER)-sdk/frontend/Makefile: javascript/qooxdoo-$(QOOXDOO_VER)-sdk.tar.gz
	tar -C javascript/ -xzf javascript/qooxdoo-0.7.3-sdk.tar.gz
	patch -p0 < patches/001_qooxdoo_getBoxObjectFor.diff
	touch --no-create $@

qooxdoo: vigigraph/public/js/vigigraph.js
vigigraph/public/js/vigigraph.js: javascript/source/class/vigigraph/Application.js javascript/qooxdoo-$(QOOXDOO_VER)-sdk/frontend/Makefile
	make -C javascript build
	mkdir -p vigigraph/public/js/
	cp -f javascript/build/script/vigigraph.js vigigraph/public/js/vigigraph.js
	cp -rf javascript/build/resource vigigraph/public/

clean_qooxdoo:
	$(RM) vigigraph/public/js/vigigraph.js
	$(RM) -r vigigraph/public/resource
	$(RM) -r javascript/build/

install: vigigraph/public/js/vigigraph.js
	$(PYTHON) setup.py install --single-version-externally-managed --root=$(DESTDIR) --record=INSTALLED_FILES
	chmod a+rX -R $(DESTDIR)$(PREFIX)/lib*/python*/*
	# Permissions de la conf
	chmod a+rX -R $(DESTDIR)$(SYSCONFDIR)/vigilo/$(NAME)
	[ `id -u` -ne 0 ] || chgrp $(HTTPD_USER) $(DESTDIR)$(SYSCONFDIR)/vigilo/$(NAME)/*.ini
	chmod 600 $(DESTDIR)$(SYSCONFDIR)/vigilo/$(NAME)/*.ini
	# Apache
	mkdir -p $(DESTDIR)$(HTTPD_DIR)
	ln -f -s $(SYSCONFDIR)/vigilo/$(NAME)/$(NAME).conf $(DESTDIR)$(HTTPD_DIR)/
	echo $(HTTPD_DIR)/$(NAME).conf >> INSTALLED_FILES
	mkdir -p $(DESTDIR)/var/log/vigilo/$(NAME)
	# Déplacement du app_cfg.py
	mv $(DESTDIR)`grep '$(NAME)/config/app_cfg.py$$' INSTALLED_FILES` $(DESTDIR)$(SYSCONFDIR)/vigilo/$(NAME)/
	ln -s $(SYSCONFDIR)/vigilo/$(NAME)/app_cfg.py $(DESTDIR)`grep '$(NAME)/config/app_cfg.py$$' INSTALLED_FILES`
	echo $(SYSCONFDIR)/vigilo/$(NAME)/app_cfg.py >> INSTALLED_FILES
	# Cache
	mkdir -p $(DESTDIR)$(LOCALSTATEDIR)/cache/vigilo/sessions
	chmod 750 $(DESTDIR)$(LOCALSTATEDIR)/cache/vigilo/sessions
	[ `id -u` -ne 0 ] || chown $(HTTPD_USER): $(DESTDIR)$(LOCALSTATEDIR)/cache/vigilo/sessions

lint: lint_pylint
tests: tests_nose
clean: clean_python clean_qooxdoo
