# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 sw=4 ts=4 et :
# Copyright (C) 2006-2020 CS-SI
# License: GNU GPL v2 <http://www.gnu.org/licenses/gpl-2.0.html>

"""WSGI middleware initialization for the vigigraph application."""

import imp
import os.path
from pkg_resources import resource_filename, working_set
from paste.cascade import Cascade
from paste.urlparser import StaticURLParser
from logging import getLogger

__all__ = ['make_app']


def make_app(global_conf, full_stack=True, **app_conf):
    """
    Set vigigraph up with the settings found in the PasteDeploy configuration
    file used.

    This is the PasteDeploy factory for the vigigraph application.

    C{app_conf} contains all the application-specific settings (those defined
    under ``[app:main]``).

    @param global_conf: The global settings for vigigraph (those
        defined under the ``[DEFAULT]`` section).
    @type global_conf: C{dict}
    @param full_stack: Should the whole TG2 stack be set up?
    @type full_stack: C{str} or C{bool}
    @return: The vigigraph application with all the relevant middleware
        loaded.
    """
    # Charge le fichier "app_cfg.py" se trouvant aux côtés de "settings.ini".
    mod_info = imp.find_module('app_cfg', [ global_conf['here'] ])
    app_cfg = imp.load_module('vigigraph.config.app_cfg', *mod_info)
    base_config = app_cfg.base_config

    # Initialisation de l'application et de son environnement d'exécution.
    load_environment = base_config.make_load_environment()
    make_base_app = base_config.setup_tg_wsgi_app(load_environment)
    app = make_base_app(global_conf, full_stack=True, **app_conf)

    max_age = app_conf.get("cache_max_age")
    try:
        max_age = int(max_age)
    except (ValueError, TypeError):
        max_age = None

    # Personalisation des fichiers statiques via un dossier public/
    # dans le répertoire contenant le fichier settings.ini chargé.
    custom_static = StaticURLParser(os.path.join(global_conf['here'], 'public'),
                                    cache_max_age=max_age)

    # On définit 2 middlewares pour fichiers statiques qui cherchent
    # les fichiers dans le thème actuellement chargé.
    # Le premier va les chercher dans le dossier des fichiers spécifiques
    # à l'application, le second cherche dans les fichiers communs.
    app_static = StaticURLParser(
        resource_filename('vigilo.themes.public', 'vigigraph'),
        cache_max_age=max_age)
    common_static = StaticURLParser(
        resource_filename('vigilo.themes.public', 'common'),
        cache_max_age=max_age)
    local_static = StaticURLParser(
        resource_filename('vigigraph', 'public'),
        cache_max_age=max_age)
    cascade_list = [custom_static, app_static, common_static, local_static, app]

    LOGGER = getLogger("vigigraph")
    ## Mise en place du répertoire d'extensions
    #setup_plugins_path(base_config.get("plugins_dir",
    #                   "/etc/vigilo/vigigraph/plugins"))

    # Spécifique projets
    for module in ["turbogears", "vigigraph"]:
        for entry in working_set.iter_entry_points(
                                "vigilo.%s.public" % module):
            if (entry.name != "enterprise" and
                    entry.name not in base_config.get("extensions", [])):
                # les points d'entrée "enterprise" sont automatiquement
                # chargés, il faut lister les autres dans la conf
                continue
            new_public_dir = resource_filename(entry.module_name, "public")
            LOGGER.debug("Adding static files directory for ext %s: %s",
                         (entry.name, new_public_dir))
            cascade_list.insert(0, StaticURLParser(new_public_dir,
                                                   cache_max_age=max_age))

    app = Cascade(cascade_list)
    return app
