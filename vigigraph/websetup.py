# -*- coding: utf-8 -*-
"""Setup the vigigraph application"""

__all__ = ['setup_app', 'populate_db']

def setup_app(command, conf, variables):
    """Place any commands to setup vigigraph here"""
    from vigilo.turbogears import populate_db
    from vigigraph.config.environment import load_environment

    load_environment(conf.global_conf, conf.local_conf)
    populate_db()

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
