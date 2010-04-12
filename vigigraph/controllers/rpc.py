# -*- coding: utf-8 -*-
"""RPC controller for the combobox of vigigraph"""

import time
import urllib
import urllib2
import logging

from pylons.i18n import ugettext as _, lazy_ugettext as l_
from tg import expose, response, request, redirect, config, url, exceptions
from sqlalchemy.orm import aliased
from repoze.what.predicates import not_anonymous

from vigigraph.lib.base import BaseController

from vigilo.models.session import DBSession
from vigilo.models.tables import LowLevelService, Host
from vigilo.models.tables import SupItemGroup, GroupHierarchy
from vigilo.models.tables import PerfDataSource
from vigilo.models.tables import Graph, GraphGroup
from vigilo.models.tables import Ventilation, VigiloServer, Application

from vigilo.models.tables.secondary_tables import SUPITEM_GROUP_TABLE
from vigilo.models.tables.secondary_tables import GRAPH_GROUP_TABLE
from vigilo.models.tables.secondary_tables import GRAPH_PERFDATASOURCE_TABLE
from vigilo.models.functions import sql_escape_like
        
from vigilo.turbogears.rrdproxy import RRDProxy
from vigilo.turbogears.nagiosproxy import NagiosProxy

from vigigraph.widgets.searchhostform import SearchHostForm
from vigigraph.lib import graphs


LOGGER = logging.getLogger(__name__)

__all__ = ['RpcController']

# pylint: disable-msg=R0201
class RpcController(BaseController):
    """
    Class Controleur TurboGears
    """

    # L'accès à ce contrôleur nécessite d'être identifié.
    allow_only = not_anonymous(l_("You need to be authenticated"))

    presets = [
        {"caption" : _("Last %d hours") %  12, "duration" : 43200},
        {"caption" : _("Last %d hours") %  24, "duration" : 86400},
        {"caption" : _("Last %d days") %    2, "duration" : 192800},
        {"caption" : _("Last %d days") %    7, "duration" : 604800},
        {"caption" : _("Last %d days") %   14, "duration" : 1209600},
        {"caption" : _("Last %d months") %  3, "duration" : 86400*31*3},
        {"caption" : _("Last %d months") %  6, "duration" : 86400*183},
        {"caption" : _("Last year"), "duration" : 86400*365},
    ]

    @expose('json')
    def maingroups(self, nocache=None):
        """
        Determination des groupes principaux (sans parent)

        @return: Dictionnaire dont la clé "items" contient une liste
            de tuples contenant le nom et l'ID des groupes d'éléments
            au sommet de la hiérarchie et auquels l'utilisateur a accès.
        @rtype: C{dict}
        @note: L'ID des groupes est converti en chaîne de caractères
            dans le résultat.
        """
        topgroups = [(tpg.name, str(tpg.idgroup)) \
                    for tpg in SupItemGroup.get_top_groups()]
        return dict(items=topgroups)

    @expose('json')
    def hostgroups(self, maingroupid, nocache=None):
        """
        Determination des groupes associes au groupe parent
        dont identificateur = argument

        @param maingroupid: identificateur d un groupe principal
        @type maingroupid: C{int}

        @return: Dictionnaire dont la clé "items" contient une liste
            de tuples avec le nom et l'ID des groupes d'éléments
            auxquels l'utilisateur a accès.
        @rtype: C{dict}
        @note: L'ID des groupes est converti en chaîne de caractères
            dans le résultat.
        """
        hostgroups = DBSession.query(
                SupItemGroup.name,
                SupItemGroup.idgroup,
            ).join(
                (GroupHierarchy, GroupHierarchy.idchild == \
                    SupItemGroup.idgroup),
            ).filter(GroupHierarchy.idparent == maingroupid
            ).filter(GroupHierarchy.hops == 1
            ).order_by(
                SupItemGroup.name.asc(),
            ).all()
        hostgroups = [(hg.name, str(hg.idgroup)) for hg in hostgroups]
        return dict(items=hostgroups)

    @expose('json')
    def hosts(self, othergroupid, nocache=None):
        """
        Determination des hotes associes au groupe
        dont identificateur = argument

        @param othergroupid : identificateur d un groupe
        @type othergroupid : int

        @return: hotes
        @rtype: document json (sous forme de dict)
        """
        hosts = DBSession.query(
                Host.name,
                Host.idhost,
            ).join(
                (SUPITEM_GROUP_TABLE, SUPITEM_GROUP_TABLE.c.idsupitem == \
                    Host.idhost),
                (SupItemGroup, SupItemGroup.idgroup == \
                    SUPITEM_GROUP_TABLE.c.idgroup),
            ).filter(SupItemGroup.idgroup == othergroupid
            ).order_by(
                Host.name.asc(),
            ).all()
            
        hosts = [(h.name, str(h.idhost)) for h in hosts]
        return dict(items=hosts)

    @expose('json')
    def graphgroups(self, idhost, nocache=None):
        """
        Determination des groupes de graphes associes a l hote
        dont identificateur = argument

        @param idhost : identificateur d un hote
        @type idhost : int

        @return: groupes de service
        @rtype: document json (sous forme de dict)
        """
        graphgroups = DBSession.query(
                GraphGroup.name,
                GraphGroup.idgroup,
            ).distinct(
            ).join(
                (GRAPH_GROUP_TABLE, GRAPH_GROUP_TABLE.c.idgroup == \
                    GraphGroup.idgroup),
                (Graph, Graph.idgraph == GRAPH_GROUP_TABLE.c.idgraph),
                (GRAPH_PERFDATASOURCE_TABLE, \
                    GRAPH_PERFDATASOURCE_TABLE.c.idgraph == Graph.idgraph),
                (PerfDataSource, PerfDataSource.idperfdatasource == \
                    GRAPH_PERFDATASOURCE_TABLE.c.idperfdatasource),
                (LowLevelService, LowLevelService.idservice == \
                    PerfDataSource.idservice),
            ).filter(
                LowLevelService.idhost == idhost
            ).order_by(
                GraphGroup.name.asc()
            )
        
        print "@@@\n%s\n@@@" % graphgroups
        graphgroups = graphgroups.all()

        graphgroups = [(gg.name, str(gg.idgroup)) for gg in graphgroups]
        return dict(items=graphgroups)

    @expose('json')
    def graphs(self, idgraphgroup, idhost, nocache=None):
        """
        Determination des graphes
        avec un service dont identificateur = argument

        @param idgraph : identificateur d un service
        @type idgraph : int

        @return: graphes
        @rtype: document json (sous forme de dict)
        """
        graphs_l = DBSession.query(
                Graph.name,
                Graph.idgraph,
            ).distinct().join(
                (GRAPH_GROUP_TABLE, GRAPH_GROUP_TABLE.c.idgraph == \
                    Graph.idgraph),
                (GraphGroup, GraphGroup.idgroup == \
                    GRAPH_GROUP_TABLE.c.idgroup),
                (GRAPH_PERFDATASOURCE_TABLE, \
                    GRAPH_PERFDATASOURCE_TABLE.c.idgraph == Graph.idgraph),
                (PerfDataSource, PerfDataSource.idperfdatasource == \
                    GRAPH_PERFDATASOURCE_TABLE.c.idperfdatasource),
                (LowLevelService, LowLevelService.idservice == \
                    PerfDataSource.idservice),
            ).filter(GraphGroup.idgroup == idgraphgroup
            ).filter(LowLevelService.idhost == idhost
            ).order_by(
                Graph.name.asc()
            )

        print "@@@\n%s\n@@@" % graphs_l
        graphs_l = graphs_l.all()

        graphs_l = [(pds.name, str(pds.idgraph)) for pds in graphs_l]
        return dict(items=graphs_l)

    @expose('json')
    def searchHostAndGraph(self, **kwargs):
        """
        Determination des couples (hote-graphe) repondant aux criteres de
        recherche sur hote et/ou graphe.

        Un critere peut correspondre a un intitule complet hote ou graphe
        ou a un extrait.

        @param kwargs : arguments nommes
        @type kwargs : dict
                         ( arguments nommes -> host et graphe )

        @return: couples hote-graphe
        @rtype: document json (sous forme de dict)
        """
        host = kwargs.get('host')
        graph = kwargs.get('graph')
        items = None

        # On a un nom d'indicateur, mais pas de nom d'hôte,
        # on considère que l'utilisateur veut tous les indicateurs
        # correspondant au motif, quelque soit l'hôte.
        if graph is not None:
            if host is None:
                host = '*'

            host = sql_escape_like(host)
            graph = sql_escape_like(graph)

            items = DBSession.query(
                    Host.name.label('hostname'),
                    Graph.name.label('graphname'),
                ).distinct().join(
                    (LowLevelService, LowLevelService.idhost == Host.idhost),
                    (PerfDataSource, PerfDataSource.idservice == \
                        LowLevelService.idservice),
                    (GRAPH_PERFDATASOURCE_TABLE, \
                        GRAPH_PERFDATASOURCE_TABLE.c.idperfdatasource == \
                        PerfDataSource.idperfdatasource),
                    (Graph, Graph.idgraph == \
                        GRAPH_PERFDATASOURCE_TABLE.c.idgraph),
                ).filter(Host.name.ilike('%' + host + '%')
                ).filter(Graph.name.ilike('%' + graph + '%')
                ).order_by(
                    Host.name.asc(),
                    Graph.name.asc(),
                )

        # On a ni hôte, ni indicateur. On renvoie une liste vide.
        # Si l'utilisateur voulait vraiment quelque chose,
        # il n'avait qu'à le demander.
        elif host is None:
            return []

        # Sinon, on a juste un motif pour un hôte.
        # On renvoie la liste des hôtes correspondant.
        else:
            host = sql_escape_like(host)
            items = DBSession.query(
                    Host.name.label('hostname'),
                ).filter(
                    Host.name.ilike('%' + host + '%')
                ).order_by(Host.name.asc())

        items = items.limit(100).all()
        if graph is None:
            items = [(item.hostname, "") for item in items]
        else:
            items = [(item.hostname, item.graphname) for item in items]
        return dict(items=items)

    @expose('json')
    def selectHostAndGraph(self, host=None, graph=None, nocache=None):
        """
        Renvoie les valeurs à sélectionner dans les comboboxes
        de VigiGraph pour afficher les données de l'hôte ou du
        couple hôte/graphe sélectionné.

        La clé "items" du dictionnaire renvoyé contient une liste avec
        2 éléments, chacun de ces éléments étant lui-même une liste.
        La 1ère liste contient les noms des groupes d'hôtes à sélectionner.
        La 2ème liste contient la liste des groupes de graphes à sélectionner.

        Pour le moment, la 2ème liste contiendra au plus 1 élément car
        les groupes de graphes ne sont pas récursifs. L'utilisation d'une
        liste permet d'assurer facilement une évolution vers des groupes
        de graphes récursifs.
        """

        # Ce cas ne devrait pas se produire, mais on tente
        # d'avoir un comportement gracieux malgré tout.
        if (not host) and (not graph):
            return dict(items=[[], []])

        # Groupe principal de l'hôte.
        mhg = aliased(SupItemGroup)
        # Groupe secondaire de l'hôte.
        shg = aliased(SupItemGroup)

        selected_hostgroups = []
        selected_graphgroups = []

        # @TODO: ajouter la gestion des permissions au code qui suit.
        # Pour le moment, la récupération de idsupitemgroup & idgraphgroup
        # ne prend pas en compte les permissions réelles de l'utilisateur.

        if host:
            # Sélectionne l'identifiant du premier SupItemGroup auquel
            # l'utilisateur a accès et auquel l'hôte donné appartient.
            idsupitemgroup = DBSession.query(
                    SupItemGroup.idgroup,
                ).join(
                    (SUPITEM_GROUP_TABLE, SUPITEM_GROUP_TABLE.c.idgroup == \
                        SupItemGroup.idgroup),
                    (Host, Host.idhost == SUPITEM_GROUP_TABLE.c.idsupitem),
                ).filter(Host.name == host
                ).scalar()

            # Si on a trouvé un tel groupe, on renvoie les noms des
            # groupes de la hiérarchie à sélectionner pour arriver
            # à celui-ci.
            if idsupitemgroup is not None:
                selected_hostgroups = DBSession.query(
                        SupItemGroup.name,
                    ).join(
                        (GroupHierarchy, GroupHierarchy.idparent == \
                            GraphGroup.idgroup),
                    ).filter(GroupHierarchy.idchild == idsupitemgroup
                    ).order_by(
                        GroupHierarchy.hops.desc()
                    ).all()

        if graph:
            # Le principe est le même que pour l'hôte, en considérant
            # cette fois les GraphGroup à la place des SupItemGroup.
            idgraphgroup = DBSession.query(
                    GraphGroup.idgroup,
                ).join(
                    (GRAPH_GROUP_TABLE, GRAPH_GROUP_TABLE.c.idgroup == \
                        GraphGroup.idgroup),
                    (Graph, Graph.idgraph == GRAPH_GROUP_TABLE.c.idgraph),
                ).filter(Graph.name == graph
                ).scalar()

            # Même principe que pour l'hôte.
            if idgraphgroup is not None:
                selected_graphgroups = DBSession.query(
                        GraphGroup.name,
                    ).join(
                        (GroupHierarchy, GroupHierarchy.idparent == \
                            GraphGroup.idgroup),
                    ).filter(GroupHierarchy.idchild == idgraphgroup
                    ).order_by(
                        GroupHierarchy.hops.desc()
                    ).all()

        hostgroups = [hg.name for hg in selected_hostgroups]
        graphgroups = [gg.name for gg in selected_graphgroups]
        return dict(items=[hostgroups, graphgroups])        

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

        @return: url du graphe
        @rtype: C{str}
        """

        result = None

        if start is None:
            start = int(time.time()) - 24*3600

        # valeurs particulieres
        direct = 1
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
            except urllib2.URLError:
                txt = _("Can't get RRD graph \"%(graph)\" on "
                        "host \"%(host)s\"") % {
                    'graph': graph,
                    'host': host,
                }
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

        @return: image du graphe
        @rtype: image png
        """
        result = None

        if start is None:
            start = int(time.time()) - 24*3600

        # valeurs particulieres
        direct = 1
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
            except urllib2.URLError:
                txt = _("Can't get RRD graph \"%(graph)\" on "
                        "host \"%(host)s\"") % {
                    'graph': graph,
                    'host': host,
                }
                LOGGER.error(txt)
                exceptions.HTTPNotFound(comment=txt)

        return result

    @expose()
    def imagePage(self, server, graphtemplate):
        """
        Affichage de l image d un graphe

        @param server : hôte
        @type server : C{str}
        @param graphtemplate : graphe
        @type graphtemplate : C{str}

        @return: page avec l image du graphe (redirection sur getImage_png)
        @rtype: page
        """
        redirect('getImage_png?host=%s&graph=%s' % (server, graphtemplate))

    @expose()
    def getStartTime(self, host, nocache=None):
        """
        Determination de la date-heure de debut des donnees RRD d un hote
        (via proxy RRD)

        @param host : hôte
        @type host : C{str}

        @return: date-heure de debut des donnees RRD
        @rtype: C{str}
        """

        result = None
        getstarttime = 1
        rrdserver = self.getRRDServer(host)

        if rrdserver is not None:
            # url
            url_web_path = config.get('rrd_web_path')
            url_l = '%s%s' % (rrdserver, url_web_path)
    
            # proxy
            rrdproxy = RRDProxy(url_l)
            try:
                result = rrdproxy.get_starttime(host, getstarttime)
            except urllib2.URLError:
                txt = _("Can't get RRD data on host \"%s\"") % host
                LOGGER.error(txt)
                exceptions.HTTPNotFound(comment=txt)

        return result

    @expose()
    def supPage(self, host):
        """
        Affichage page supervision Nagios pour un hote
        (appel fonction status via proxy Nagios)
        
        @param host : hôte
        @type host : C{str}

        @return: page de supervision Nagios
        @rtype: page
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
            except urllib2.URLError:
                txt = _("Can't get Nagios data on host \"%s\"") % host
                LOGGER.error(txt)
                error_url = '../error/nagios_host_error?host=%s' % host
                redirect(error_url)
        else:
            txt = _("No server has been configured to monitor \"%s\"") % host
            LOGGER.error(txt)
            error_url = '../error/nagios_host_error?host=%s' % host
            redirect(error_url)


        return result

    @expose()
    def servicePage(self, host, service=None):
        """
        Affichage page supervision Nagios pour un hote
        (appel fonction get_extinfo via proxy Nagios)

        @param host : hôte
        @type host : C{str}
        @param service : service
        @type service : C{str}

        @return: page de supervision Nagios
        @rtype: page
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
            except urllib2.URLError:
                txt = _("Can't get Nagios data on host \"%(host)s\" "
                        "and service \"%(service)s\"") % {
                            'host': host,
                            'service': service,
                        }
                LOGGER.error(txt)

                error_url = '../error/nagios_host_service_error' \
                        '?host=%s&service=%s' % (host, service)
                redirect(error_url)

        return result

    @expose()
    def metroPage(self, host):
        """
        Affichage page metrologie pour un hote
        (via proxy RRD)

        @param host : hôte
        @type host : C{str}

        @return: page de metrologie
        @rtype: page
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
            except urllib2.URLError:
                txt = _("Can't get RRD data on host \"%s\"") % host
                LOGGER.error(txt)
                error_url = '../error/rrd_error?host=%s' % host
                redirect(error_url)

        return result

    @expose('graphslist.html', content_type='text/html')
    def graphsList(self, nocache=None, **kwargs):
        """
        Generation document avec url des graphes affiches
        (pour l impression )

        @param kwargs : arguments nommes
        @type kwargs  : dict

        @return: url de graphes
        @rtype: document html
        """
        graphslist = graphs.graphsList(**kwargs)
        return dict(graphslist=graphslist)

    @expose(content_type='text/plain')
    def tempoDelayRefresh(self, nocache=None):
        """
        Determination valeur temporisation pour le rafraichissement automatique
        d un graphe

        @return: valeur de temporisation
        @rtype: C{str}
        """

        delay = graphs.tempoDelayRefresh()
        return delay

    @expose('json')
    def getIndicators(self, nocache=None, graph=None):
        """
        Liste d indicateurs associes a un graphe

        @param graph : graphe
        @type graph  : C{str}

        @return: dictionnaire des indicateurs d un graphe
        @rtype: document json (sous forme de dict)
        """

        indicators = self.getListIndicators(graph)
        indicators = [(ind.name, ind.idperfdatasource) for ind in indicators]
        return dict(items=indicators)

    def getListIndicators(self, graph=None):
        """
        Liste d indicateurs associes a un graphe

        @param graph : graphe
        @type graph  : C{str}

        @return: liste d indicateurs
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
    @expose(content_type='text/csv')
    def exportCSV(self, nocache=None, host=None, graph=None, indicator=None, \
    start=None, end=None):
        """
        Export CSV sous forme de fichier
        pour un hote et un graphe et pour l'indicateur suivant
        * soit un des indicateurs associes au graphe
        * soit l ensemble des indicateurs -> valeur argument = All

        @param host : hôte
        @type host : C{str}
        @param graph : graphe
        @type graph : C{str}
        @param indicator : indicateur graphe
        @type indicator : C{str}
        @param start : date-heure de debut des donnees
        @type start : C{str}

        @return: fichier genere avec les donnees RRD repondant aux criteres
        @rtype  : fichier CSV
        """

        result = None
        filename = None

        # indicateurs
        if indicator is None:
            raise ValueError

        rrdserver = self.getRRDServer(host)
        if not rrdserver:
            raise ValueError, host

        indicators = [ind[0] for ind in self.getListIndicators(graph)]
        if indicator != "All":
            if indicator not in indicators:
                raise ValueError, indicator
            indicators = [indicator]
            filename = graphs.getExportFileName(host, indicator, start, end)

        else:
            filename = graphs.getExportFileName(host, graph, start, end)

        indicators.insert(0, "Timestamp")

        url_web_path = config.get('rrd_web_path', '')
        url = '%s%s' % (rrdserver, url_web_path)
        rrdproxy = RRDProxy(url)

        try:
            result = rrdproxy.exportCSV(server=host, graph=graph, \
                indicator=indicator, start=start, end=end)
        except urllib2.URLError:
            txt = _("Can't get RRD data on host \"%(host)s\", "
                    "graph \"%(graph)s\" and indicator \"%(indicator)s\"") % {
                        'host': host,
                        'graph': graph,
                        'indicator': indicator,
                    }
            LOGGER.error(txt)

            error_url = '../error'
            error_url += '/rrd_exportCSV_error'
            error_url += '?host=%s&graph=%s&indicator=%s' % \
                (host, graph, indicator)
            redirect(error_url)
        else:
            response.headerlist.append(('Content-Disposition',
                'attachment;filename=%s' % filename))
            return result


    # VIGILO_EXIG_VIGILO_PERF_0010:Visualisation globale des graphes
    @expose('fullhostpage.html')
    def fullHostPage(self, host, start=None, duration=86400):
        """
        Affichage de l'ensemble des graphes associes a un hote
        * d apres les donnees RRD
        * avec une date-heure de debut
        * pour une plage de temps 
        
        @param host : hôte
        @type host : C{str}
        @param start : date-heure de debut des donnees
        @type start : C{str}
        @param duration : plage de temps des données
        @type duration : C{str}
                         (parametre optionnel, initialise a 86400 = plage de 1 jour)

        @return: page avec les images des graphes et boutons de deplacement dans le temps
        @rtype: page html
        """

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
                    presets=self.presets, dhgs=dhgs)

    @expose('singlegraph.html')
    def singleGraph(self, host, graph, start=None, duration=86400):
        """
        Affichage d un graphe associe a un hote et un graphe
        * d apres les donnees RRD
        * avec une date-heure de debut
        * pour une plage de temps 
        
        @param host : hôte
        @type host : C{str}
        @param graph : graphe
        @type graph  : C{str}
        @param start : date-heure de debut des donnees
        @type start : C{str}
        @param duration : plage de temps des données 
        @type duration : C{str}
                         (parametre optionnel, initialise a 86400 = plage de 1 jour)

        @return: page avec l image du graphe et boutons de deplacement dans le temps
        @rtype: page html
        """

        if start is None:
            start = int(time.time()) - int(duration)

        return dict(host=host, graph=graph, start=start, duration=duration, \
                    presets=self.presets)

    @expose('searchhostform.html')
    def searchHostForm(self):
        """
        Formulaire de recherche sur les hotes

        @return: page avec formulaire de recherche
        @rtype: page html
        """
        searchhostform = SearchHostForm('search_host_form', \
            submit_text=None)

        return dict(searchhostform=searchhostform)

    @expose('searchhost.html')
    def searchHost(self, query=None):
        """
        Affichage page pour hotes repondant au critere de recherche
        * dans cette page, lien sur pages de metrologie et de supervision

        @param query : prefixe de recherche sur les hotes
        @type query : C{str}

        @return: page
        @rtype: page html
        """

        hosts = []

        if query:
            r = urllib.unquote_plus(query.strip())
            rl = r.split(',')

            # hotes
            for part in rl:
                hosts += DBSession.query(Host.name) \
                        .filter(Host.name.like(part.strip() + '%')) \
                        .all()
            return dict(hosts=hosts)
        else:
            redirect("searchHostForm")

    # VIGILO_EXIG_VIGILO_PERF_0030:Moteur de recherche des graphes
    @expose('getopensearch.xml', content_type='text/xml')
    def getOpenSearch(self):
        """
        Moteur de recherche des graphes

        @return: document
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

        @return: serveur RRD
        @rtype: C{str}
        """

        result = DBSession.query(
                    VigiloServer.name
                ).filter(VigiloServer.idvigiloserver == \
                    Ventilation.idvigiloserver
                ).filter(Ventilation.idhost == Host.idhost
                ).filter(Ventilation.idapp == Application.idapp
                ).filter(Host.name == host
                ).filter(Application.name == 'rrdgraph'
                ).scalar()
        return result

    def getNagiosServer(self, host=None):
        """
        Determination Serveur Nagios pour l hote courant
        (Server Nagios -> nom de l application associee = nagios)

        @param host : hôte
        @type host : C{str}

        @return: serveur Nagios
        @rtype: C{str}
        """

        result = DBSession.query(
                    VigiloServer.name
                ).filter(VigiloServer.idvigiloserver == \
                    Ventilation.idvigiloserver
                ).filter(Ventilation.idhost == Host.idhost
                ).filter(Ventilation.idapp == Application.idapp
                ).filter(Host.name == host
                ).filter(Application.name == 'nagios'
                ).scalar()
        return result

