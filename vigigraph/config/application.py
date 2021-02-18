# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 sw=4 ts=4 et :
# Copyright (C) 2006-2021 CS GROUP - France
# License: GNU GPL v2 <http://www.gnu.org/licenses/gpl-2.0.html>

"""WSGI middleware initialization for the vigigraph application."""

import imp
import os.path
from pkg_resources import resource_filename, working_set
from tg.support.statics import StaticsMiddleware
from logging import getLogger

__all__ = ['make_app']


def make_app(global_conf, **app_conf):
    """
    Set vigigraph up with the settings found in the PasteDeploy configuration
    file used.

    This is the PasteDeploy factory for the vigigraph application.

    C{app_conf} contains all the application-specific settings (those defined
    under ``[app:main]``).

    @param global_conf: The global settings for vigigraph (those
        defined under the ``[DEFAULT]`` section).
    @type global_conf: C{dict}
    @return: The vigigraph application with all the relevant middleware
        loaded.
    """
    # Charge le fichier "app_cfg.py" se trouvant aux côtés de "settings.ini".
    mod_info = imp.find_module('app_cfg', [ global_conf['here'] ])
    app_cfg = imp.load_module('vigigraph.config.app_cfg', *mod_info)
    base_config = app_cfg.base_config

    # Initialisation de l'application et de son environnement d'exécution.
    app = base_config.make_wsgi_app(global_conf, app_conf, wrap_app=None)
    LOGGER = getLogger("vigigraph")

    max_age = app_conf.get("cache_max_age")
    try:
        max_age = int(max_age)
    except (ValueError, TypeError):
        max_age = 0

    # Mise en place du répertoire d'extensions
    #setup_plugins_path(app_conf.get("plugins_dir",
    #                   os.path.join(global_conf['here'], 'plugins')))

    # Spécifique projets
    extensions = app_conf.get("extensions", [])
    for module in ["turbogears", "vigigraph"]:
        for entry in working_set.iter_entry_points(
                                "vigilo.%s.public" % module):
            if (entry.name != "enterprise" and entry.name not in extensions):
                # les points d'entrée "enterprise" sont automatiquement
                # chargés, il faut lister les autres dans la conf
                continue
            new_public_dir = resource_filename(entry.module_name, "public")
            LOGGER.debug("Adding static files directory for ext %s: %s",
                         (entry.name, new_public_dir))
            app = StaticsMiddleware(app, new_public_dir, max_age)

    # Apply middleware for static files in reverse order
    # (user-supplied customizations override theme/application-provided files)
    app = StaticsMiddleware(app, resource_filename('vigigraph', 'public'), max_age)
    app = StaticsMiddleware(app, resource_filename('vigilo.themes.public', 'common'), max_age)
    app = StaticsMiddleware(app, resource_filename('vigilo.themes.public', 'vigigraph'), max_age)
    app = StaticsMiddleware(app, os.path.join(global_conf['here'], 'public'), max_age)
    return app
