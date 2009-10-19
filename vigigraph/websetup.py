# -*- coding: utf-8 -*-
"""Setup the vigigraph application"""

import logging

import transaction
from tg import config

from vigigraph.config.environment import load_environment

__all__ = ['setup_app']

log = logging.getLogger(__name__)


def setup_app(command, conf, variables):
    """Place any commands to setup vigigraph here"""
    load_environment(conf.global_conf, conf.local_conf)

    # Load the models
    from vigigraph import model
    from vigilo.models import Version

    # Create tables
    print "Creating tables"
    model.metadata.create_all()

    # Create the default user for TG, must be changed
    # for real tests and production
    manager = model.User()
    manager.user_name = u'manager'
    manager.email = u'manager@somedomain.com'
    model.DBSession.add(manager)

    group = model.UserGroup()
    group.group_name = u'managers'
    group.users.append(manager)
    model.DBSession.add(group)

    permission = model.Permission()
    permission.permission_name = u'manage'
    permission.usergroups.append(group)
    model.DBSession.add(permission)

    editor = model.User()
    editor.user_name = u'editor'
    editor.email = u'editor@somedomain.com'
    model.DBSession.add(editor)

    group = model.UserGroup()
    group.group_name = u'editors'
    group.users.append(editor)
    model.DBSession.add(group)

    permission = model.Permission()
    permission.permission_name = u'edit'
    permission.usergroups.append(group)
    model.DBSession.add(permission)

    version = Version()
    version.name = u'vigigraph'
    version.version = config['vigigraph_version']
    model.DBSession.add(version)

    model.DBSession.flush()
    transaction.commit()
    print "Successfully setup"
