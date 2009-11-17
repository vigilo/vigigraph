# -*- coding: utf-8 -*-
"""RPC controller for the combobox of vigigraph"""

from tg import request, expose
from vigigraph.lib.base import BaseController
from vigigraph.model import DBSession
from vigigraph.model import Group, HostGroup, Host



__all__ = ['RpcController']


class RpcController(BaseController):
    """
    Class Gérant la lecture des différents champs des combobox de vigigraph.
    """

    @expose('json')
    def maingroups(self, nocache=None):
        """Render the JSON document for the combobox Main Group"""
        topgroups = DBSession.query(Group.name, Group.idgroup) \
                .filter(Group.parent == None) \
                .order_by(Group.name) \
                .all()
        return dict(items=[(tpg[0], str(tpg[1])) for tpg in topgroups])
    
    @expose('json')
    def hostgroups(self, maingroupid, nocache=None):
        """Render the JSON document for the combobox Other Group"""
        hostgroups = DBSession.query(Group.name, Group.idgroup)\
                     .filter(Group.idparent == maingroupid) \
                     .all()
        return dict(items=[(hg[0], str(hg[1])) for hg in hostgroups])

    @expose('json')
    def hosts(self, othergroupid, nocache=None):
        """Render the JSON document for the combobox Host Name"""
        # note actuellement Host.name est la primary_key
        hosts = DBSession.query(Host.fqhn, Host.name) \
                .join(HostGroup) \
                .filter(HostGroup.idgroup == othergroupid) \
                .all()
        return dict(items=[(h[0], h[1]) for h in hosts])

