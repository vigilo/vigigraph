# -*- coding: utf-8 -*-
# Copyright (C) 2011-2020 CS-SI
# License: GNU GPL v2 <http://www.gnu.org/licenses/gpl-2.0.html>

"""Setup the vigigraph application"""

# pylint: disable-msg=W0613
# W0613: Unused argument

import imp

__all__ = ['setup_app', 'populate_db']

def setup_app(command, conf, variables):
    """Place any commands to setup vigigraph here"""
    from vigilo.turbogears import populate_db as tg_pop_db

    # Charge le fichier "app_cfg.py" se trouvant aux côtés de "settings.ini".
    mod_info = imp.find_module('app_cfg', [ conf.global_conf['here'] ])
    app_cfg = imp.load_module('vigigraph.config.app_cfg', *mod_info)

    # Initialisation de l'environnement d'exécution.
    load_environment = app_cfg.base_config.make_load_environment()
    load_environment(conf.global_conf, conf.local_conf)
    tg_pop_db()

def populate_db(bind):
    from vigilo.models.session import DBSession
    from vigilo.models import tables

    permissions = {
        'vigigraph-access':
            'Gives access to VigiGraph',
    }

    for (permission_name, description) in permissions.iteritems():
        if not tables.Permission.by_permission_name(unicode(permission_name)):
            DBSession.add(tables.Permission(
                permission_name=unicode(permission_name),
                description=unicode(description),
            ))
    DBSession.flush()
