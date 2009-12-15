# -*- coding: utf-8 -*-
"""RPC controller for the combobox of vigigraph"""

from tg import request, expose
from vigigraph.lib.base import BaseController
from vigigraph.model import DBSession
from vigigraph.model import HostGroup, Host, ServiceGroup, ServiceLowLevel, PerfDataSource
from vigilo.models.secondary_tables import SERVICE_GROUP_TABLE

import time


__all__ = ['RpcController']


class RpcController(BaseController):
    """
    Class Gérant la lecture des différents champs des combobox de vigigraph.
    """
    def _get_host(self, hostname):
        """ Return Host object from hostname, None if not available"""
        return DBSession.query(Host) \
                .filter(Host.name == hostname) \
                .first()

    @expose('json')
    def maingroups(self, nocache=None):
        """Render the JSON document for the combobox Main Group"""
        topgroups = DBSession.query(HostGroup.name, HostGroup.idgroup) \
                .filter(HostGroup.parent == None) \
                .order_by(HostGroup.name) \
                .all()
        if topgroups is not None and topgroups != []:
            return dict(items=[(tpg[0], str(tpg[1])) for tpg in topgroups])
        else:
            return dict(items=[])

    @expose('json')
    def hostgroups(self, maingroupid, nocache=None):
        """Render the JSON document for the combobox Other Group"""
        hostgroups = DBSession.query(HostGroup.name, HostGroup.idgroup)\
                     .filter(HostGroup.idparent == maingroupid) \
                     .all()
        if hostgroups is not None and hostgroups != []:
            return dict(items=[(hg[0], str(hg[1])) for hg in hostgroups])
        else:
            return dict(items=[])

    @expose('json')
    def hosts(self, othergroupid, nocache=None):
        """Render the JSON document for the combobox Host Name"""
        hostgroup = DBSession.query(HostGroup) \
                .filter(HostGroup.idgroup == othergroupid) \
                .first()
        if hostgroup is not None and hostgroup.hosts is not None:
            return dict(items=[(h.name, str(h.idhost)) for h in hostgroup.hosts])
        else:
            return dict(items=[])

    @expose('json')
    def servicegroups(self, idhost, nocache=None):
        """Render the JSON document for the combobox Graph Group"""
        # passage par une table intermédiaire à cause de l'héritage
        servicegroups = DBSession.query(ServiceGroup.name, ServiceLowLevel.idservice) \
                .join((SERVICE_GROUP_TABLE, SERVICE_GROUP_TABLE.c.idgroup == ServiceGroup.idgroup))  \
                .join((ServiceLowLevel, SERVICE_GROUP_TABLE.c.idservice == ServiceLowLevel.idservice)) \
                .filter(ServiceLowLevel.idhost == idhost) \
                .all()
        if servicegroups is not None and servicegroups != []:
            return dict(items=[(sg[0], str(sg[1])) for sg in set(servicegroups)])
        else:
            return dict(items=[])

    @expose('json')
    def graphs(self, idservice, nocache=None):
        """Render the JSON document for the combobox Graph Name"""
        perfdatasources = DBSession.query(PerfDataSource.name, PerfDataSource.idperfdatasource) \
                .filter(PerfDataSource.idservice == idservice) \
                .all()
        if perfdatasources is not None or perfdatasources != []:
            return dict(items=[(pds[0], str(pds[1])) for pds in set(perfdatasources)])
        else:
            return dict(items=[])

    @expose('json')
    def selectHostAndService(self, idhost, idservice):
        """Render the JSON document for the Host and Service"""
        if idservice:
            servicegroups(idhost)
        else:
            # passage par une table intermédiaire à cause de l'héritage
            servicegroups = DBSession.query(ServiceGroup.name, ServiceGroup.idgroup) \
                .join((SERVICE_GROUP_TABLE, SERVICE_GROUP_TABLE.c.idgroup == ServiceGroup.idgroup))  \
                .join((ServiceLowLevel, SERVICE_GROUP_TABLE.c.idservice == ServiceLowLevel.idservice)) \
                .filter(ServiceLowLevel.idhost == idhost) \
                .filter(ServiceLowLevel.idservice == idservice) \
                .all()
            if servicegroups is not None and servicegroups != []:
                return dict(items=[(sg[0], str(sg[1])) for sg in set(servicegroups)])
            else:
                return dict(items=[])

    @expose('json')
    def searchHostAndService(self, idhost, idservice):
        """Render the JSON document for the Host and Service"""
        if idservice:
            servicegroups(idhost)
        else:
            # passage par une table intermédiaire à cause de l'héritage
            servicegroups = DBSession.query(ServiceGroup.name, ServiceGroup.idgroup) \
                .join((SERVICE_GROUP_TABLE, SERVICE_GROUP_TABLE.c.idgroup == ServiceGroup.idgroup))  \
                .join((ServiceLowLevel, SERVICE_GROUP_TABLE.c.idservice == ServiceLowLevel.idservice)) \
                .filter(ServiceLowLevel.idhost == idhost) \
                .filter(ServiceLowLevel.idservice == idservice) \
                .all()
            if servicegroups is not None and servicegroups != []:
                return dict(items=[(sg[0], str(sg[1])) for sg in set(servicegroups)])
            else:
                return dict(items=[])

    @expose('')
    def subPage(self, host):
        #try:
        #    #util.redirect(req,"/%s/cgi-bin/nagios2/status.cgi?host=%s&style=detail&supNav=1"%(navconf.hosts[host]['supServer'],host))
        #except:
        #    req.content_type = "text/html"
        #    req.write("<html><body bgcolor='#C3C7D3'><p>Unable to find supervision page for %s.<br/>Are You sure it has been inserted into the supervision configuration ?</p></body></html>\n"%host)

        return 'subPage'

    @expose('')
    def getImage(self, req, host, graph, start=None,duration=86400,details=1):
        if start is None:
            start = int(time.time()) - 24*3600
        #req.internal_redirect("/%s/rrdgraph/rrdgraph.py?server=%s&graphtemplate=%s&direct=1&start=%s&duration=%s&details=%d&fakeIncr=%d"%(navconf.hosts[host]['metroServer'],host,urllib.quote_plus(graph),start,duration,int(details),random.randint(0,9999999999)))
        return 'getImage'

    @expose('')
    def getReport(self):
        return 'getReport'

    @expose('')
    def getStartTime(self, req, host):
        #req.internal_redirect("/%s/rrdgraph/rrdgraph.py?server=%s&getstarttime=1&fakeIncr=%d"%(navconf.hosts[host]['metroServer'],host,random.randint(0,9999999999)))
        return 'getStartTime'
