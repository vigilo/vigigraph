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

    print "Testing whether VigiGraph was already installed"
    installed = DBSession.query(
            tables.Permission.permission_name
        ).filter(tables.Permission.permission_name == u'vigigraph-access'
        ).scalar()

    if installed:
        print "VigiGraph has already been installed"
        return

    DBSession.add(tables.Permission(
        permission_name=u'vigigraph-access',
        description=u'Gives access to VigiGraph',
    ))
    DBSession.flush()

