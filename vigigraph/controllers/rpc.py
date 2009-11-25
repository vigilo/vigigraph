# -*- coding: utf-8 -*-
"""RPC controller for the combobox of vigigraph"""

from tg import request, expose
from vigigraph.lib.base import BaseController
from vigigraph.model import DBSession
from vigigraph.model import HostGroup, Host



__all__ = ['RpcController']


class RpcController(BaseController):
    """
    Class Gérant la lecture des différents champs des combobox de vigigraph.
    """

    @expose('json')
    def maingroups(self, nocache=None):
        """Render the JSON document for the combobox Main Group"""
        topgroups = DBSession.query(HostGroup.name, HostGroup.idgroup) \
                .filter(HostGroup.parent == None) \
                .order_by(HostGroup.name) \
                .all()
        if topgroups is not None:
            return dict(items=[(tpg[0], str(tpg[1])) for tpg in topgroups])
        return None
    
    @expose('json')
    def hostgroups(self, maingroupid, nocache=None):
        """Render the JSON document for the combobox Other Group"""
        hostgroups = DBSession.query(HostGroup.name, HostGroup.idgroup)\
                     .filter(HostGroup.idparent == maingroupid) \
                     .all()
        if hostgroups is not None:
            return dict(items=[(hg[0], str(hg[1])) for hg in hostgroups])
        return None

    @expose('json')
    def hosts(self, othergroupid, nocache=None):
        """Render the JSON document for the combobox Host Name"""
        hostgroup = DBSession.query(HostGroup) \
                .filter(HostGroup.idgroup == othergroupid) \
                .first()
        if hostgroup is not None and hostgroup.hosts is not None:
            return dict(items=[(h.name, h.name) for h in hostgroup.hosts])
        return None

#    @expose('json')
#    def graphgroups(self, hostname, nocache=None):
#        """Render the JSON document for the combobox Graph Group"""
#        hostgroup = DBSession.query(GraphGroup) \
#                .filter(HostGroup.idgroup == othergroupid) \
#                .first()
#        if hostgroup is not None and hostgroup.hosts is not None:
#            return dict(items=[(h.name, h.name) for h in hostgroup.hosts])
#        return None

