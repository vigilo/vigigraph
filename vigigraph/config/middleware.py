# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 sw=4 ts=4 et :
# Copyright (C) 2006-2011 CS-SI
# License: GNU GPL v2 <http://www.gnu.org/licenses/gpl-2.0.html>

"""WSGI middleware initialization for the vigigraph application."""

from vigigraph.config.app_cfg import base_config
from vigigraph.config.environment import load_environment

from pkg_resources import resource_filename, working_set
from paste.cascade import Cascade
from paste.urlparser import StaticURLParser
from logging import getLogger

__all__ = ['make_app']

# Use base_config to setup the necessary PasteDeploy application factory.
# make_base_app will wrap the TG2 app with all the middleware it needs.
make_base_app = base_config.setup_tg_wsgi_app(load_environment)


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
    app = make_base_app(global_conf, full_stack=full_stack, **app_conf)

    # On définit 2 middlewares pour fichiers statiques qui cherchent
    # les fichiers dans le thème actuellement chargé.
    # Le premier va les chercher dans le dossier des fichiers spécifiques
    # à l'application, le second cherche dans les fichiers communs.
    app_static = StaticURLParser(resource_filename(
        'vigilo.themes.public', 'vigigraph'))
    common_static = StaticURLParser(resource_filename(
        'vigilo.themes.public', 'common'))
    local_static = StaticURLParser(resource_filename(
        'vigigraph', 'public'))
    cascade_list = [app_static, common_static, local_static, app]

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
            cascade_list.insert(0, StaticURLParser(new_public_dir))

    app = Cascade(cascade_list)
    return app
