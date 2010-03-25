# -*- coding: utf-8 -*-
"""RPC controller for the combobox of vigigraph"""

from tg import expose, response, request, redirect, config, url
from tg import exceptions

from vigigraph.lib.base import BaseController

from vigilo.models.configure import DBSession
from vigilo.models import Host, HostGroup
from vigilo.models import Service, ServiceGroup, LowLevelService
from vigilo.models import PerfDataSource
from vigilo.models import Graph
from vigilo.models import Ventilation, VigiloServer, Application

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
import logging
import string

from searchhostform import SearchHostForm
from vigigraph.lib import graphs


LOGGER = logging.getLogger(__name__)

__all__ = ['RpcController']


class RpcController(BaseController):
    """
    Class Controleur TurboGears
    """
    def _get_host(self, hostname):
        """
        Return Host object from hostname, None if not available
        """
        return DBSession.query(Host) \
                .filter(Host.name == hostname) \
                .first()

    @expose('json')
    def maingroups(self, nocache=None):
        """
        Determination des groupes principaux (sans parent)

        @return : groupes principaux
        @rtype : document json (sous forme de dict)
        """
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
        """
        Determination des groupes associes au groupe parent
        dont identificateur = argument

        @param maingroupid : identificateur d un groupe principal
        @type maingroupid : int

        @return : groupes
        @rtype : document json (sous forme de dict)
        """
        hostgroups = DBSession.query(HostGroup.name, HostGroup.idgroup)\
                     .filter(HostGroup.idparent == maingroupid) \
                     .all()
        if hostgroups is not None and hostgroups != []:
            return dict(items=[(hg[0], str(hg[1])) for hg in hostgroups])
        else:
            return dict(items=[])

    @expose('json')
    def hosts(self, othergroupid, nocache=None):
        """
        Determination des hotes associes au groupe
        dont identificateur = argument

        @param othergroupid : identificateur d un groupe
        @type othergroupid : int

        @return : hotes
        @rtype : document json (sous forme de dict)
        """
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
        """
        Determination des groupes de services associes a l hote
        dont identificateur = argument

        @param idhost : identificateur d un hote
        @type idhost : int

        @return : groupes de service
        @rtype : document json (sous forme de dict)
        """
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
        """
        Determination des graphes
        avec un service dont identificateur = argument

        @param idservice : identificateur d un service
        @type idservice : int

        @return : graphes
        @rtype : document json (sous forme de dict)
        """
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
        """
        Determination des couples (hote-service) repondant aux criteres de
        recherche sur hote et/ou service

        Un critere peut correspondre a un intitule complet hote ou service
        ou a un extrait

        @param **kwargs : arguments nommes
        @type **kwargs : dict
                         ( arguments nommes -> host et service )

        @return : couples hote-service
        @rtype : document json (sous forme de dict)
        """
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
        """
        Determination (groupe principal-groupe-service) associe au couple (hote-service)

        @param **kwargs : arguments nommes
        @type **kwargs : dict
                         ( arguments nommes -> host et service )

        @return : (groupe principal-groupe-service)
        @rtype : document json (sous forme de dict)
        """
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
        """
        Determination de l url d un graphe
        (via proxy RRD)

        @param host : hôte
        @type host : C{str}
        @param start : date-heure de debut des donnees
        @type start : C{str}
        @param duration : plage de temps des données
        @type duration : C{str}
                         (parametre optionnel, initialise a 86400 = plage de 1 jour)
        @param details : indicateur affichage details dans graphe (legende)
        @type details : int
        @param graph : graphe
        @type graph : C{str}

        @return : url du graphe
        @rtype: C{str}
        """

        result = None

        if start is None:
            start = int(time.time()) - 24*3600

        # valeurs particulieres
        direct = 1
        fakeIncr = random.randint(0, 9999999999)

        rrdserver = self.getRRDServer(host)
        if rrdserver is not None:
            # url
            url_web_path = config.get('rrd_web_path')
            url_l = '%s%s' % (rrdserver, url_web_path)

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

    # VIGILO_EXIG_VIGILO_PERF_0020:Visualisation unitaire des graphes
    @expose(content_type='image/png')
    def getImage_png(self, host, start=None, duration=86400, graph=None, \
    details=1):
        """
        Affichage de l image d un graphe
        (via proxy RRD)

        @param host : hôte
        @type host : C{str}
        @param start : date-heure de debut des donnees
        @type start : C{str}
        @param duration : plage de temps des données
        @type duration : C{str}
                      (parametre optionnel, initialise a 86400 = plage de 1 jour)
        @param graph : graphe
        @type graph : C{str}
        @param details : indicateur affichage details dans graphe (legende)
        @type details : int

        @return : image du graphe
        @rtype: image png
        """
        result = None

        if start is None:
            start = int(time.time()) - 24*3600

        # valeurs particulieres
        direct = 1
        fakeIncr = random.randint(0, 9999999999)

        rrdserver = self.getRRDServer(host)
        
        if rrdserver is not None:
            # url
            url_web_path = config.get('rrd_web_path')
            url_l = '%s%s' % (rrdserver, url_web_path)

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
    def imagePage(self, server, graphtemplate):
        """
        Affichage de l image d un graphe

        @param server : hôte
        @type server : C{str}
        @param graphtemplate : graphe
        @type graphtemplate : C{str}

        @return : page avec l image du graphe (redirection sur getImage_png)
        @rtype: page
        """
        redirect('getImage_png?host=%s&graph=%s' % (server, graphtemplate))

    @expose('')
    def getStartTime(self, host, nocache=None):
        """
        Determination de la date-heure de debut des donnees RRD d un hote
        (via proxy RRD)

        @param host : hôte
        @type host : C{str}

        @return : date-heure de debut des donnees RRD
        @rtype: C{str}
        """

        result = None

        getstarttime = 1
        fakeincr = random.randint(0, 9999999999)

        rrdserver = self.getRRDServer(host)
        if rrdserver is not None:
            # url
            url_web_path = config.get('rrd_web_path')
            url_l = '%s%s' % (rrdserver, url_web_path)
    
            # proxy
            rrdproxy = RRDProxy(url_l)
            try:
                result = rrdproxy.get_starttime(host, getstarttime)
            except urllib2.URLError, e:
                txt = _("Can't get RRD data on host \"%s\"") \
                    % (host)
                LOGGER.error(txt)
                exceptions.HTTPNotFound(comment=txt)

        return result

    @expose('')
    def supPage(self, host):
        """
        Affichage page supervision Nagios pour un hote
        (appel fonction status via proxy Nagios)
        
        @param host : hôte
        @type host : C{str}

        @return : page de supervision Nagios
        @rtype : page
        """
        result = None

        nagiosserver = self.getNagiosServer(host)
        if nagiosserver is not None:
            # url
            url_web_path = config.get('nagios_web_path')
            url_l = '%s%s' % (nagiosserver, url_web_path)

            # proxy
            nagiosproxy = NagiosProxy(url_l)
            try:
                result = nagiosproxy.get_status(host)
            except urllib2.URLError, e:
                txt = _("Can't get Nagios data on host \"%s\"") \
                    % (host)
                LOGGER.error(txt)
                error_url = '../error/nagios_host_error?host=%s'
                redirect(error_url % host)

        return result

    @expose('')
    def servicePage(self, host, service=None):
        """
        Affichage page supervision Nagios pour un hote
        (appel fonction get_extinfo via proxy Nagios)

        @param host : hôte
        @type host : C{str}
        @param service : service
        @type service : C{str}

        @return : page de supervision Nagios
        @rtype : page
        """
        result = None

        nagiosserver = self.getNagiosServer(host)
        if nagiosserver is not None:
            # url
            url_web_path = config.get('nagios_web_path')
            url_l = '%s%s' % (nagiosserver, url_web_path)

            # proxy
            nagiosproxy = NagiosProxy(url_l)
            try:
                result = nagiosproxy.get_extinfo(host, service)
            except urllib2.URLError, e:
                txt = _("Can't get Nagios data on host \"%s\" service \"%s\"")\
                    % (host, service)
                LOGGER.error(txt)

                error_url = '../error'
                error_url += '/nagios_host_service_error?host=%s&service=%s'
                redirect(error_url % (host, service))

        return result

    @expose('')
    def metroPage(self, host):
        """
        Affichage page metrologie pour un hote
        (via proxy RRD)

        @param host : hôte
        @type host : C{str}

        @return : page de metrologie
        @rtype : page
        """
        result = None

        rrdserver = self.getRRDServer(host)
        if rrdserver is not None:
            # url
            url_web_path = config.get('rrd_web_path')
            url_l = '%s%s' % (rrdserver, url_web_path)

            # proxy
            rrdproxy = RRDProxy(url_l)
            try:
                result = rrdproxy.get_hostC(host)
            except urllib2.URLError, e:
                txt = _("Can't get RRD data on host \"%s\"") \
                    % (host)
                LOGGER.error(txt)
                error_url = '../error/rrd_error?host=%s'
                redirect(error_url % host)

        return result

    @expose('graphslist.html', content_type='text/html')
    def graphsList(self, nocache=None, **kwargs):
        """
        Generation document avec url des graphes affiches
        (pour l impression )

        @param **kwargs : arguments nommes
        @type **kwargs  : dict

        @return : url de graphes
        @rtype: document html
        """
        graphslist = graphs.graphsList(**kwargs)
        return dict(graphslist=graphslist)

    @expose(content_type='text/plain')
    def tempoDelayRefresh(self, nocache=None):
        """
        Determination valeur temporisation pour le rafraichissement automatique
        d un graphe

        @return : valeur de temporisation
        @rtype : C{str}
        """

        delay = graphs.tempoDelayRefresh()
        return delay

    @expose('json')
    def getIndicators(self, nocache=None, graph=None):
        """
        Liste d indicateurs associes a un graphe

        @param graph : graphe
        @type graph  : C{str}

        @return : dictionnaire des indicateurs d un graphe
        @rtype : document json (sous forme de dict)
        """

        indicators = self.getListIndicators(graph)
        if indicators is not None and indicators != []:
            return dict(items=[(ind[0], str(ind[1])) for ind in indicators])
        else:
            return dict(items=[])

    def getListIndicators(self, graph=None):
        """
        Liste d indicateurs associes a un graphe

        @param graph : graphe
        @type graph  : C{str}

        @return : liste d indicateurs
        @rtype  : list
        """

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

    # VIGILO_EXIG_VIGILO_PERF_0040:Export des donnees d'un graphe au format CSV
    @expose('', content_type='text/csv')
    def exportCSV(self, nocache=None, host=None, graph=None, indicator=None, \
    start=None, end=None):
        """
        Export CSV sous forme de fichier
        - pour un hote et un graphe
        - pour l'indicateur suivant
          - soit un des indicateurs associes au graphe
          - soit l ensemble des indicateurs -> valeur argument = All

        @param host : hôte
        @type host : C{str}
        @param graph : graphe
        @type graph : C{str}
        @param indicator : indicateur graphe
        @type indicator : C{str}
        @param start : date-heure de debut des donnees
        @type start : C{str}

        @return : fichier genere avec les donnees RRD repondant aux criteres
        @rtype  : fichier CSV
        """

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
            indicator_f = ''

            if indicator == "All":
                b_export = True
                for i in range(len(indicators)):
                    indicators_l.append(indicators[i][0])
                indicator_f = graph
            else:
                for i in range(len(indicators)):
                    if indicator == indicators[i][0]:
                        b_export = True
                        indicators_l.append(indicator)
                        indicator_f = indicator
                        break

            if b_export:
                # nom fichier
                filename = graphs.getExportFileName(host, indicator_f, \
                start, end)

                idx = 0
                dict_indicators[idx] = 'TimeStamp'

                for i in range(len(indicators_l)):
                    idx += 1
                    dict_indicators[idx] = indicators_l[i]

                rrdserver = self.getRRDServer(host)
                if rrdserver is not None:
                    # url selon configuration
                    url_web_path = config.get('rrd_web_path')
                    url_l = '%s%s' % (rrdserver, url_web_path)

                    # donnees via proxy
                    rrdproxy = RRDProxy(url_l)
                    try:
                        result = rrdproxy.exportCSV(server=host, graph=graph, \
                        indicator=indicator, start=start, end=end)
                    except urllib2.URLError, e:
                        b_export = False
                        
                        txt = _("Can't get RRD data on host \"%s\" \
                        graph \"%s\" indicator \"%s\" ") \
                        % (host, graph, indicator)
                        LOGGER.error(txt)

                        error_url = '../error'
                        error_url += '/rrd_exportCSV_error'
                        error_url += '?host=%s&graph=%s&indicator=%s'
                        redirect(error_url % (host, graph, indicator))
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
                            fn = 'attachment;filename='+filename
                            response.headerlist.append \
                            (('Content-Disposition', fn))
                            try:
                                writer = csv.DictWriter(f, \
                                fieldnames=fieldnames, delimiter=sep_values, \
                                quoting=csv.QUOTE_ALL)

                                # entête
                                headers = dict( (n, n) for n in fieldnames )
                                writer.writerow(headers)

                                # generation fichier
                                graphs.setExportFile(writer, dict_values, \
                                dict_indicators, sep_value)
                                
                            finally:
                                f.close()

                            return open(filename, 'rt').read()

        if b_export == False:
            return 'KO'

    # VIGILO_EXIG_VIGILO_PERF_0010:Visualisation globale des graphes
    @expose('fullhostpage.html')
    def fullHostPage(self, host, start=None, duration=86400):
        """
        Affichage de l'ensemble des graphes associes a un hote
        - d apres les donnees RRD
        - avec une date-heure de debut
        - pour une plage de temps 
        
        @param host : hôte
        @type host : C{str}
        @param start : date-heure de debut des donnees
        @type start : C{str}
        @param duration : plage de temps des données
        @type duration : C{str}
                         (parametre optionnel, initialise a 86400 = plage de 1 jour)

        @return : page avec les images des graphes et boutons de deplacement dans le temps
        @rtype: page html
        """

        presets = [
        {"caption" : _("Last %sh") % '12', "duration" : 43200},
        {"caption" : _("Last %sh") % '24', "duration" : 86400},
        {"caption" : _("Last %sd") % '2',  "duration" : 192800},
        {"caption" : _("Last %sd") % '7',  "duration" : 604800},
        {"caption" : _("Last %sd") % '14', "duration" : 1209600},
        {"caption" : _("Last %sm") % '3', "duration" : 86400*31*3},
        {"caption" : _("Last %sm") % '6', "duration" : 86400*183},
        {"caption" : _("Last year"), "duration" : 86400*365},
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
        presets=presets, dhgs=dhgs)

    @expose ('singlegraph.html')
    def singleGraph(self, host, graph, start=None, duration=86400):
        """
        Affichage d un graphe associe a un hote et un graphe
        - d apres les donnees RRD
        - avec une date-heure de debut
        - pour une plage de temps 
        
        @param host : hôte
        @type host : C{str}
        @param graph : graphe
        @type graph  : C{str}
        @param start : date-heure de debut des donnees
        @type start : C{str}
        @param duration : plage de temps des données 
        @type duration : C{str}
                         (parametre optionnel, initialise a 86400 = plage de 1 jour)

        @return : page avec l image du graphe et boutons de deplacement dans le temps
        @rtype: page html
        """

        presets = [
        {"caption" : _("Last %sh") % '12', "duration" : 43200},
        {"caption" : _("Last %sh") % '24', "duration" : 86400},
        {"caption" : _("Last %sd") % '2',  "duration" : 192800},
        {"caption" : _("Last %sd") % '7',  "duration" : 604800},
        {"caption" : _("Last %sd") % '14', "duration" : 1209600},
        {"caption" : _("Last %sm") % '3', "duration" : 86400*31*3},
        {"caption" : _("Last %sm") % '6', "duration" : 86400*183},
        {"caption" : _("Last year"), "duration" : 86400*365},
        ]

        if start is None:
            start = int(time.time()) - int(duration)

        return dict(host=host, graph=graph, start=start, duration=duration, \
        presets=presets)

    @expose('searchhostform.html')
    def searchHostForm(self):
        """
        Formulaire de recherche sur les hotes

        @return : page avec formulaire de recherche
        @rtype: page html
        """
        searchhostform = SearchHostForm('search_host_form', \
            submit_text=None)

        return dict(searchhostform=searchhostform)

    @expose ('searchhost.html')
    def searchHost(self, query=None):
        """
        Recherche d hotes repondant au critere de recherche

        @param query : prefixe de recherche sur les hotes
        @type query : C{str}

        @return : page
        @rtype: page html
        """

        hosts = []

        b_query = False
        if query is not None:
            query = string.strip(query)
            b_query = (query != '')

        if b_query:
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

    # VIGILO_EXIG_VIGILO_PERF_0030:Moteur de recherche des graphes
    @expose ('getopensearch.xml', content_type='text/xml')
    def getOpenSearch(self):
        """
        Moteur de recherche des graphes

        @return : document
        @rtype: document xml
        """

        here = "http://"
        here += request.host
        dir_l = url('/public')

        result = dict(here=here, dir=dir_l)

        return result

    def getRRDServer(self, host=None):
        """
        Determination Serveur RRD pour l hote courant
        (Serveur RRD -> nom de l application associee = rrdgraph)

        @param host : hôte
        @type host : C{str}

        @return : serveur RRD
        @rtype: C{str}
        """

        server = None
        if host is not None:
            result = DBSession.query \
            (VigiloServer.name) \
            .filter(VigiloServer.idvigiloserver == Ventilation.idvigiloserver) \
            .filter(Ventilation.idhost == Host.idhost) \
            .filter(Ventilation.idapp == Application.idapp) \
            .filter(Host.name == host) \
            .filter(Application.name == 'rrdgraph') \
            .first()

            if result is not None:
                server = result[0]

        return server

    def getNagiosServer(self, host=None):
        """
        Determination Serveur Nagios pour l hote courant
        (Server Nagios -> nom de l application associee = nagios)

        @param host : hôte
        @type host : C{str}

        @return : serveur Nagios
        @rtype: C{str}
        """

        server = None
        if host is not None:
            # intitulé 
            result = DBSession.query \
            (VigiloServer.name) \
            .filter(VigiloServer.idvigiloserver == Ventilation.idvigiloserver) \
            .filter(Ventilation.idhost == Host.idhost) \
            .filter(Host.name == host) \
            .filter(VigiloServer.description.like('%Nagios%')) \
            .first()

            if result is not None:
                server = result[0]

        return server
