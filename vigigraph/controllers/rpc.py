# -*- coding: utf-8 -*-
"""RPC controller for the combobox of vigigraph"""

from tg import request, expose

from vigigraph.lib.base import BaseController
from vigigraph.model import DBSession
from vigigraph.model import Host, HostGroup
from vigigraph.model import Service, ServiceGroup, ServiceLowLevel
from vigigraph.model import PerfDataSource

from vigilo.models.secondary_tables import SERVICE_GROUP_TABLE
from vigilo.models.secondary_tables import HOST_GROUP_TABLE

from sqlalchemy.orm import aliased

from pylons.i18n import ugettext as _

import time
import random
import urllib2

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
        if hostgroup is not None and \
        hostgroup.hosts is not None:
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
    def selectHostAndService(self, **kwargs):
        """Render the JSON document for the Host and Service"""
        host = kwargs.get('host');
        service = kwargs.get('service');

        groups = []
        services = None

        if host is not None:
            hg1 = aliased(HostGroup)
            hg2 = aliased(HostGroup)
            sg =  aliased(ServiceGroup)
            if service is not None:
                for hg1_r, hg2_r, sg_r in \
                    DBSession.query(hg1, hg2, sg) \
                    .filter(hg1.parent == None) \
                    .filter(hg2.parent != None) \
                    .filter(HOST_GROUP_TABLE.c.idhost == Host.idhost) \
                    .filter(HOST_GROUP_TABLE.c.idgroup == hg2.idgroup) \
                    .filter(SERVICE_GROUP_TABLE.c.idservice == Service.idservice) \
                    .filter(SERVICE_GROUP_TABLE.c.idgroup == sg.idgroup) \
                    .filter(Host.idhost == ServiceLowLevel.idhost) \
                    .filter(Service.idservice == ServiceLowLevel.idservice) \
                    .filter(Host.name == host ) \
                    .filter(Service.servicename == service):
                    if hg1_r.idgroup == hg2_r.parent.idgroup:
                        groups.append(hg1_r.name)
                        groups.append(hg2_r.name)
                        groups.append(sg_r.name)
            else:
                for hg1_r, hg2_r in \
                    DBSession.query(hg1, hg2) \
                    .filter(hg1.parent == None) \
                    .filter(hg2.parent != None) \
                    .filter(HOST_GROUP_TABLE.c.idhost == Host.idhost) \
                    .filter(HOST_GROUP_TABLE.c.idgroup == hg2.idgroup) \
                    .filter(Host.name == host ):
                    if hg1_r.idgroup == hg2_r.parent.idgroup:
                        groups.append(hg1_r.name)
                        groups.append(hg2_r.name)
                        groups.append(None)

        if groups is not None and groups != []:
            return dict(items=groups)
        else:
            return dict(items=[])

    @expose('json')
    def searchHostAndService(self, **kwargs):
        """Render the JSON document for the Host and Service"""
        host = kwargs.get('host');
        service = kwargs.get('service');

        servicegroups_l = None
        if host is not None and service is not None:
            servicegroups_l = DBSession.query(Host.name, ServiceLowLevel.servicename) \
                    .join((ServiceLowLevel, ServiceLowLevel.idhost == Host.idhost)) \
                    .filter(Host.name.like('%'+host+'%')) \
                    .filter(ServiceLowLevel.servicename.like('%'+service+'%')) \
                    .all()
        elif host is not None and service is None:
            servicegroups_l = DBSession.query(Host.name, ServiceLowLevel.servicename) \
                    .join((ServiceLowLevel, ServiceLowLevel.idhost == Host.idhost)) \
                    .filter(Host.name.like('%'+host+'%')) \
                    .all()
        elif host is None and service is not None:
            servicegroups_l = DBSession.query(Host.name, ServiceLowLevel.servicename) \
                    .join((ServiceLowLevel, ServiceLowLevel.idhost == Host.idhost)) \
                    .filter(ServiceLowLevel.servicename.like('%'+service+'%')) \
                    .all()
        elif host is None and service is None:
            servicegroups_l = DBSession.query(Host.name, ServiceLowLevel.servicename) \
                    .join((ServiceLowLevel, ServiceLowLevel.idhost == Host.idhost)) \
                    .all()

        if servicegroups_l is not None and servicegroups_l != []:
            return dict(items=[(sg[0], sg[1]) for sg in set(servicegroups_l)])
        else:
            return dict(items=[])

    @expose(content_type='image/png')
    def getImage(self, host, start=None, duration=86400, graph=None, details=1):
        '''getImage'''
        if start is None:
            start = int(time.time()) - 24*3600

        # valeurs particulieres
        direct = 1
        fakeIncr = random.randint(0,9999999999)

        # TODO : url_l : selon configuration
        url_l = 'http://localhost/rrdgraph'

        rrdproxy = RRDProxy(url_l)
        try:
            #result = rrdproxy.rrd_img_ap(host, graph, direct, start, duration, int(details), fakeincr)
            result = rrdproxy.rrd_img_ap(host, graph, direct, duration, start, int(details))
        except urllib2.URLError, e:
            print _("Can't get RRD graph \"%s\" on host \"%s\"") \
                    % (graph, host)
            result = None

        return result

    @expose('')
    def getStartTime(self, host):
        '''getStartTime'''

        getstarttime = 1
        fakeincr = random.randint(0,9999999999)

        # TODO : url_l : selon configuration
        url_l = 'http://localhost/rrdgraph'

        rrdproxy = RRDProxy(url_l)
        try:
            #result = rrdproxy.rrd_getstarttime(host, getstarttime, fakeincr)
            result = rrdproxy.rrd_getstarttime(host, getstarttime)
        except urllib2.URLError, e:
            print _("Can't get RRD data on host \"%s\"") \
                    % (host)
            result = -1

        return result

    @expose('')
    def subPage(self, host):
        '''subPage'''
        #try:
        #    #util.redirect(req,"/%s/cgi-bin/nagios2/status.cgi?host=%s \
        #&style=detail&supNav=1"%(navconf.hosts[host]['supServer'],host))
        #except:
        #    req.content_type = "text/html"
        #    req.write("<html><body bgcolor='#C3C7D3'> \
        #<p>Unable to find supervision page for %s.<br/>Are You sure \
        #it has been inserted into the supervision configuration ? \
        #</p></body></html>\n"%host)

        return 'subPage'

