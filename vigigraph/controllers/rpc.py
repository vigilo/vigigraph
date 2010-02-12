# -*- coding: utf-8 -*-
"""RPC controller for the combobox of vigigraph"""

from tg import expose, response, request, redirect, config
from tg import exceptions

from vigigraph.lib.base import BaseController

from vigilo.models.configure import DBSession
from vigilo.models import Host, HostGroup
from vigilo.models import Service, ServiceGroup, LowLevelService
from vigilo.models import PerfDataSource
from vigilo.models import Graph

from vigilo.models.secondary_tables import SERVICE_GROUP_TABLE
from vigilo.models.secondary_tables import HOST_GROUP_TABLE
from vigilo.models.secondary_tables import GRAPH_PERFDATASOURCE_TABLE

from sqlalchemy.orm import aliased
        
from vigilo.turbogears.rrdproxy import RRDProxy
from nagiosproxy import NagiosProxy

from pylons.i18n import ugettext as _

import time
import random
import urllib
import urllib2
import csv
import os
import logging

from time import gmtime, strftime

from searchhostform import SearchHostForm

LOGGER = logging.getLogger(__name__)

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
            return dict(items=[(h.name, str(h.idhost)) \
            for h in hostgroup.hosts])
        else:
            return dict(items=[])

    @expose('json')
    def servicegroups(self, idhost, nocache=None):
        """Render the JSON document for the combobox Graph Group"""
        # passage par une table intermédiaire à cause de l'héritage
        servicegroups = DBSession.query \
            (ServiceGroup.name, LowLevelService.idservice) \
            .join((SERVICE_GROUP_TABLE, \
            SERVICE_GROUP_TABLE.c.idgroup == ServiceGroup.idgroup))  \
            .join((LowLevelService, \
            SERVICE_GROUP_TABLE.c.idservice == LowLevelService.idservice)) \
            .filter(LowLevelService.idhost == idhost) \
            .all()
        if servicegroups is not None and servicegroups != []:
            return dict(items=[(sg[0], str(sg[1])) \
            for sg in set(servicegroups)])
        else:
            return dict(items=[])

    @expose('json')
    def graphs(self, idservice, nocache=None):
        """Render the JSON document for the combobox Graph Name"""
        graphs_l = DBSession.query(Graph.name, Graph.idgraph) \
            .join((GRAPH_PERFDATASOURCE_TABLE, \
            GRAPH_PERFDATASOURCE_TABLE.c.idgraph == Graph.idgraph)) \
            .join((PerfDataSource, \
            GRAPH_PERFDATASOURCE_TABLE.c.idperfdatasource == \
            PerfDataSource.idperfdatasource)) \
            .filter(PerfDataSource.idservice == idservice) \
            .all()
        if graphs_l is not None or graphs_l != []:
            return dict(items=[(pds[0], str(pds[1])) \
            for pds in set(graphs_l)])
        else:
            return dict(items=[])

    @expose('json')
    def searchHostAndService(self, **kwargs):
        """Render the JSON document for the Host and Service"""

        host = kwargs.get('host')
        service = kwargs.get('service')

        servicegroups_l = None
        if host is not None and service is not None:
            servicegroups_l = DBSession.query( \
              Host.name, LowLevelService.servicename) \
              .join((LowLevelService, LowLevelService.idhost == Host.idhost)) \
              .filter(Host.name.like('%'+host+'%')) \
              .filter(LowLevelService.servicename.like('%'+service+'%')) \
              .all()
        elif host is not None and service is None:
            servicegroups_l = DBSession.query( \
              Host.name, LowLevelService.servicename) \
              .join((LowLevelService, LowLevelService.idhost == Host.idhost)) \
              .filter(Host.name.like('%'+host+'%')) \
              .all()
        elif host is None and service is not None:
            servicegroups_l = DBSession.query( \
              Host.name, LowLevelService.servicename) \
              .join((LowLevelService, LowLevelService.idhost == Host.idhost)) \
              .filter(LowLevelService.servicename.like('%'+service+'%')) \
              .all()
        elif host is None and service is None:
            servicegroups_l = DBSession.query( \
              Host.name, LowLevelService.servicename) \
              .join((LowLevelService, LowLevelService.idhost == Host.idhost)) \
              .all()

        if servicegroups_l is not None and servicegroups_l != []:
            return dict(items=[(sg[0], sg[1]) for sg in set(servicegroups_l)])
        else:
            return dict(items=[])

    @expose('json')
    def selectHostAndService(self, **kwargs):
        """Render the JSON document for the Host and Service"""
        
        host = kwargs.get('host')
        #service = kwargs.get('service')
        service = None

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
                .filter(Host.idhost == LowLevelService.idhost) \
                .filter(Service.idservice == LowLevelService.idservice) \
                .filter(Host.name == host ) \
                .filter(Service.servicename == service):
                    if hg1_r.idgroup == hg2_r.parent.idgroup:
                        groups.append(hg1_r.name)
                        groups.append(hg2_r.name)
                        groups.append(sg_r.name)
                        # 1 seul ensemble
                        break
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
                        # 1 seul ensemble
                        break

        if groups is not None and groups != []:
            return dict(items=groups)
        else:
            return dict(items=[])

    @expose(content_type='text/plain')
    def getImage(self, host, start=None, duration=86400, graph=None, \
    details=1, nocache=0):
        '''Image - as Text'''
        result = None

        if start is None:
            start = int(time.time()) - 24*3600

        # valeurs particulieres
        direct = 1
        fakeIncr = random.randint(0, 9999999999)

        # url
        url_l = config.get('rrd_url')
        if url_l is not None:
            # proxy
            rrdproxy = RRDProxy(url_l)
            try:
                result = rrdproxy.get_img_name_with_params(host, graph, \
                direct, duration, start, int(details))
            except urllib2.URLError, e:
                txt = _("Can't get RRD graph \"%s\" on host \"%s\"") \
                    % (graph, host)
                LOGGER.error(txt)
                exceptions.HTTPNotFound(comment=txt)

        return result

    @expose(content_type='image/png')
    def getImage_png(self, host, start=None, duration=86400, graph=None, \
    details=1):
        '''Image - as png'''
        result = None

        if start is None:
            start = int(time.time()) - 24*3600

        # valeurs particulieres
        direct = 1
        fakeIncr = random.randint(0, 9999999999)

        # url
        url_l = config.get('rrd_url')
        if url_l is not None:
            # proxy
            rrdproxy = RRDProxy(url_l)
            try:
                result = rrdproxy.get_img_with_params(host, graph, direct, \
                duration, start, int(details))
            except urllib2.URLError, e:
                txt = _("Can't get RRD graph \"%s\" on host \"%s\"") \
                    % (graph, host)
                LOGGER.error(txt)
                exceptions.HTTPNotFound(comment=txt)

        return result

    @expose('')
    def getStartTime(self, host, nocache=None):
        '''StartTime RRD'''
        result = None

        getstarttime = 1
        fakeincr = random.randint(0, 9999999999)

        # url
        url_l = config.get('rrd_url')
        if url_l is not None:
            # proxy
            rrdproxy = RRDProxy(url_l)
            try:
                #result=rrdproxy.get_getstarttime(host, getstarttime, fakeincr)
                result = rrdproxy.get_starttime(host, getstarttime)
            except urllib2.URLError, e:
                txt = _("Can't get RRD data on host \"%s\"") \
                    % (host)
                LOGGER.error(txt)
                exceptions.HTTPNotFound(comment=txt)

        return result

    @expose('')
    def supPage(self, host):
        '''supPage'''
        result = None

        # url
        url_l = config.get('nagios_url')
        if url_l is not None:
            # proxy
            nagiosproxy = NagiosProxy(url_l)
            try:
                result = nagiosproxy.get_status(host)
            except urllib2.URLError, e:
                response.content_type = "text/html"
                response.write("<html><body bgcolor='#C3C7D3'> \
                <p>Unable to find supervision page for %s.<br/>Are You sure \
                it has been inserted into the supervision configuration ? \
                </p></body></html>\n" % host)

        return result

    @expose('')
    def servicePage(self, host, service=None):
        '''servicePage'''
        result = None

        # url
        url_l = config.get('nagios_url')
        if url_l is not None:
            # proxy
            nagiosproxy = NagiosProxy(url_l)
            try:
                result = nagiosproxy.get_extinfo(host, service)
            except urllib2.URLError, e:
                response.content_type = "text/html"
                response.write("<html><body bgcolor='#C3C7D3'> \
                <p>Unable to find supervision page for %s/%s.<br/>Are You sure \
                it has been inserted into the supervision configuration ? \
                </p></body></html>\n" % (host, service))

        return result

    @expose('')
    def metroPage(self, host):
        '''metroPage'''
        result = None

        # url
        url_l = config.get('rrd_url')
        if url_l is not None:
            # proxy
            rrdproxy = RRDProxy(url_l)
            try:
                result = rrdproxy.get_host(host)
            except urllib2.URLError, e:
                response.content_type = "text/html"
                response.write("<html><body bgcolor='#C3C7D3'> \
                <p>Unable to find metrology page for %s.<br/>Are You sure \
                it has been inserted into the supervision configuration ? \
                </p></body></html>\n" % host)

        return result

    @expose('graphslist.html', content_type='text/html')
    def graphsList(self, nocache=None, **kwargs):
        '''graphsList'''
        graphslist = []
        format = "%d-%m-%Y %H:%M"
        for key in kwargs:
            # titre
            title = "Inconnu"
            graph = ""
            server = ""
            lca = kwargs[key].split("?")
            if len(lca) == 2:
                largs = lca[1].split("&")
                for arg in largs:
                    larg = arg.split("=")
                    if len(larg) == 2:
                        if larg[0] == "server":
                            server = larg[1]
                        elif larg[0] == "graphtemplate":
                            graph = larg[1]
                        elif larg[0] == "start":
                            start = larg[1]
                        elif larg[0] == "duration":
                            duration = larg[1]
            if graph != "" or server != "":
                title = "'%s' Graph for host %s" % \
                  (urllib.unquote_plus(graph), server)
            graph = {}
            graph['title'] = title
            v = int(start)
            graph['sts'] = _(strftime(format, gmtime(v)))
            v = int(start) + int(duration)
            graph['ets'] = _(strftime(format, gmtime(v)))
            graph['src'] = urllib2.unquote(kwargs[key])
            graphslist.append(graph)
        return dict(graphslist=graphslist)

    @expose(content_type='text/plain')
    def tempoDelayRefresh(self, nocache=None):
        '''tempo pour rafraichissement'''
        delay = config.get('delay_refresh')
        return str(delay)

    @expose('json')
    def getIndicators(self, nocache=None, graph=None):
        '''Indicators for graph'''
        indicators = self.getListIndicators(graph)
        if indicators is not None and indicators != []:
            return dict(items=[(ind[0], str(ind[1])) for ind in indicators])
        else:
            return dict(items=[])

    def getListIndicators(self, graph=None):
        '''List of Indicators'''
        indicators = []
        if graph is not None:
            indicators = DBSession.query \
              (PerfDataSource.name, PerfDataSource.idperfdatasource) \
              .join((GRAPH_PERFDATASOURCE_TABLE, \
              GRAPH_PERFDATASOURCE_TABLE.c.idperfdatasource == \
              PerfDataSource.idperfdatasource)) \
              .join((Graph, \
              Graph.idgraph == GRAPH_PERFDATASOURCE_TABLE.c.idgraph)) \
              .filter(Graph.name == graph) \
              .all()
        return indicators

    @expose('', content_type='text/csv')
    def exportCSV(self, nocache=None, host=None, graph=None, indicator=None, \
    start=None, end=None):
        '''export CSV'''

        result = None
        b_export = False

        # separateurs
        sep_values = ";"
        sep_value = ","

        sep = config.get("export_csv_sep_values")
        if sep is not None:
            sep_values = sep
            
        sep = config.get("export_csv_sep_value")
        if sep is not None:
            sep_value = sep

        filename = None

        # indicateurs
        if indicator is not None:
            dict_indicators = {}
            indicators = self.getListIndicators(graph)
            indicators_l = []

            if indicator == "All":
                b_export = True
                for i in range(len(indicators)):
                    indicators_l.append(indicators[i][0])
                filename = graph
            else:
                for i in range(len(indicators)):
                    if indicator == indicators[i][0]:
                        b_export = True
                        indicators_l.append(indicator)
                        filename = indicator
                        break

            if b_export:
                # nom fichier final
                lc = [' ', '|', '/', '\\', ':', '?', '*', '<', '>', '"']
                for c in lc:
                    filename = filename.replace(c, "_")
                filename += ".csv"

                idx = 0
                dict_indicators[idx] = 'TimeStamp'

                for i in range(len(indicators_l)):
                    idx += 1
                    dict_indicators[idx] = indicators_l[i]

                # url selon configuration
                url_l = config.get('rrd_url')
                if url_l is not None:
                    # donnees via proxy
                    rrdproxy = RRDProxy(url_l)
                    try:
                        result = rrdproxy.exportCSV(server=host, graph=graph, \
                        indicator=indicator, start=start, end=end)
                    except urllib2.URLError, e:
                        b_export = False
                        response.content_type = "text/html"
                        response.write("<html><body bgcolor='#C3C7D3'> \
                        <p>Unable to export for %s %s %s.<br/> \
                        </p></body></html>\n" % (host, graph, indicator))
                    finally:
                        if b_export:
                            # conversion sous forme de dictionnaire
                            dict_values = {}
                            if result is not None:
                                if result != "{}":
                                    if result.startswith("{") and \
                                    result.endswith("}"):
                                        dict_values = eval(result)
 
                            fieldnames = tuple([dict_indicators[k] \
                            for k in dict_indicators])

                            # fichier
                            f = open(filename, 'wt')
                            fn = 'attachment;filename='+filename+"'"
                            response.headerlist.append \
                            (('Content-Disposition', fn))
                            try:
                                writer = csv.DictWriter(f, \
                                fieldnames=fieldnames, delimiter=sep_values, \
                                quoting=csv.QUOTE_ALL)

                                # entête
                                headers = dict( (n, n) for n in fieldnames )
                                writer.writerow(headers)
                                '''
                                dict_data = {}
                                for key_i in dict_indicators:
                                    iv = dict_indicators[key_i]
                                    dict_data[iv] = iv
                                writer.writerow(dict_data)
                                '''

                                # valeurs
                                if dict_values is not None or \
                                dict_values != "{}":
                                    for key_tv in dict_values:
                                        tv = dict_values[key_tv]
                                        dict_data = {}
                                        for key_i in dict_indicators:
                                            iv = dict_indicators[key_i]
                                            # remplacement . par ,
                                            v = str(tv[key_i])
                                            v = v.replace(".", sep_value)
                                            dict_data[iv] = v
                                        writer.writerow(dict_data)
                            finally:
                                f.close()

                            return open(filename, 'rt').read()

        if b_export == False:
            return 'KO'

    @expose('fullhostpage.html')
    def fullHostPage(self, host, start=None, duration=86400):
        """
        fullHostPage
        """

        presels = [
            {"caption" : "Last 12h", "duration" : 43200},
            {"caption" : "Last 24h", "duration" : 86400},
            {"caption" : "Last 2d",  "duration" : 192800},
            {"caption" : "Last 7d",  "duration" : 604800},
            {"caption" : "Last 14d", "duration" : 1209600},
            {"caption" : "Last 3m", "duration" : 86400*31*3},
            {"caption" : "Last 6m", "duration" : 86400*183},
            {"caption" : "Last year", "duration" : 86400*365},
        ]

        if start is None:
            start = int(time.time()) - int(duration)

        # graphes pour hote
        hgs = DBSession.query(Graph.name) \
              .join((GRAPH_PERFDATASOURCE_TABLE, \
              GRAPH_PERFDATASOURCE_TABLE.c.idgraph == Graph.idgraph)) \
              .join((PerfDataSource, \
              GRAPH_PERFDATASOURCE_TABLE.c.idperfdatasource == \
              PerfDataSource.idperfdatasource)) \
              .join((LowLevelService, \
              PerfDataSource.idservice == LowLevelService.idservice)) \
              .join((Host, \
              LowLevelService.idhost == Host.idhost)) \
              .filter(Host.name == host) \
              .all()

        # dictionnaire -> {0 : [hote, graph_0], ..., n: [hote, graph_n] }
        i = 0
        dhgs = {}
        for hg in hgs:
            elt = [host, hg]
            dhgs[i] = elt
            i += 1

        return dict(host=host, start=start, duration=duration, \
        presels=presels, dhgs=dhgs)

    @expose ('singlegraph.html')
    def singleGraph(self, host, graph, start=None, duration=86400):
        """
        singleGraph
        """

        presels = [
        {"caption" : "Last 12h", "duration" : 43200},
        {"caption" : "Last 24h", "duration" : 86400},
        {"caption" : "Last 2d",  "duration" : 192800},
        {"caption" : "Last 7d",  "duration" : 604800},
        {"caption" : "Last 14d", "duration" : 1209600},
        {"caption" : "Last 3m", "duration" : 86400*31*3},
        {"caption" : "Last 6m", "duration" : 86400*183},
        {"caption" : "Last year", "duration" : 86400*365},
        ]

        if start is None:
            start = int(time.time()) - int(duration)

        return dict(host=host, graph=graph, start=start, duration=duration, \
        presels=presels)

    @expose('searchhostform.html')
    def searchHostForm(self):
        '''searchhostform'''
        searchhostform = SearchHostForm('search_host_form', \
            submit_text=None)

        return dict(searchhostform=searchhostform)

    @expose ('searchhost.html')
    def searchHost(self, query=None):
        '''
        searchHost
        '''

        hosts = []
        if query is not None:
            r = urllib.unquote_plus(query)
            rl = r.split(',')

            headings = []
            for i in range(len(rl)):
                headings.append(rl[i].strip() + '%')

            # hotes
            for i in range(len(headings)):
                hosts += DBSession.query(Host.name) \
                        .filter(Host.name.like(headings[i])) \
                        .all()

            if hosts is not None and hosts != []:
                return dict(hosts=hosts)
            else:
                return dict(hosts=[])
        else:
            redirect("searchHostForm")


    @expose ('getopensearch.xml', content_type='text/xml')
    def getOpenSearch(self):
        '''
        getOpenSearch
        '''

        here = "http://"
        here += request.host
        here += '/rpc'

        dir_l = os.path.join(os.getcwd(), 'vigigraph/public')
        result = dict(here=here, dir=dir_l)

        return result
