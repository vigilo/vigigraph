# -*- coding: utf-8 -*-
"""RPC controller for the combobox of vigigraph"""

import time, urlparse, urllib2
import logging

# La fonction parse_qsl a été déplacée dans Python 2.6.
try:
    from urlparse import parse_qsl
except ImportError:
    from cgi import parse_qsl

from pylons.i18n import ugettext as _, lazy_ugettext as l_
from webob.exc import HTTPPreconditionFailed
from tg import expose, request, redirect, tmpl_context, \
                config, validate, flash
from tg.decorators import paginate
from repoze.what.predicates import not_anonymous, has_permission, \
                                    in_group, Any, All
from formencode import validators, schema
from sqlalchemy import or_
from sqlalchemy.sql.expression import literal_column

from vigilo.turbogears.controllers import BaseController
from vigilo.turbogears.helpers import get_current_user
from vigilo.turbogears.controllers.proxy import get_through_proxy

from vigilo.models.session import DBSession
from vigilo.models.tables import Host
from vigilo.models.tables import SupItemGroup
from vigilo.models.tables import PerfDataSource
from vigilo.models.tables import Graph, GraphGroup
from vigilo.models.tables import Change

from vigilo.models.tables.secondary_tables import SUPITEM_GROUP_TABLE
from vigilo.models.tables.secondary_tables import GRAPH_GROUP_TABLE
from vigilo.models.tables.secondary_tables import GRAPH_PERFDATASOURCE_TABLE
from vigilo.models.functions import sql_escape_like

LOGGER = logging.getLogger(__name__)

__all__ = ['RpcController']


# pylint: disable-msg=R0201
class RpcController(BaseController):
    """
    Class Controleur TurboGears
    """

    # L'accès à ce contrôleur nécessite d'être identifié.
    allow_only = All(
        not_anonymous(msg=l_("You need to be authenticated")),
        Any(
            in_group('managers'),
            has_permission('vigigraph-access',
                msg=l_("You don't have access to VigiGraph")),
        ),
    )

    presets = [
        {"caption" : _("Last %d hours") %  12, "duration" : 43200},
        {"caption" : _("Last %d hours") %  24, "duration" : 86400},
        {"caption" : _("Last %d days") %    2, "duration" : 192800},
        {"caption" : _("Last %d days") %    7, "duration" : 604800},
        {"caption" : _("Last %d days") %   14, "duration" : 1209600},
        {"caption" : _("Last %d months") %  3, "duration" : 86400 * 31 * 3},
        {"caption" : _("Last %d months") %  6, "duration" : 86400 * 183},
        {"caption" : _("Last year"), "duration" : 86400 * 365},
    ]

    def process_form_errors(self, *argv, **kwargv):
        """
        Gestion des erreurs de validation : On affiche les erreurs
        puis on redirige vers la dernière page accédée.
        """
        for k in tmpl_context.form_errors:
            flash("'%s': %s" % (k, tmpl_context.form_errors[k]), 'error')
        redirect(request.environ.get('HTTP_REFERER', '/'))

    class SearchHostAndGraphSchema(schema.Schema):
        """Schéma de validation pour la méthode L{searchHostAndGraph}."""
        search_form_host = validators.String(if_missing=None)
        search_form_graph = validators.String(if_missing=None)

    # @TODO définir un error_handler différent pour remonter l'erreur via JS.
    @validate(
        validators = SearchHostAndGraphSchema(),
        error_handler = process_form_errors)
    @expose('json')
    def searchHostAndGraph(self, search_form_host, search_form_graph):
        """
        Determination des couples (hote-graphe) repondant aux criteres de
        recherche sur hote et/ou graphe.

        Un critere peut correspondre a un intitule complet hote ou graphe
        ou a un extrait.

        @return: couples hote-graphe
        @rtype: dict
        """
        user = get_current_user()
        items = []

        if user is None:
            return dict(items=[])

        # On a un nom de graphe, mais pas de nom d'hôte,
        # on considère que l'utilisateur veut tous les graphes
        # correspondant au motif, quel que soit l'hôte.
        if search_form_graph:
            if not search_form_host:
                search_form_host = '*'

            search_form_host = sql_escape_like(search_form_host)
            search_form_graph = sql_escape_like(search_form_graph)

            items = DBSession.query(
                    Host.idhost.label('idhost'),
                    Host.name.label('hostname'),
                    Graph.idgraph.label('idgraph'),
                    Graph.name.label('graphname'),
                ).distinct().join(
                    (PerfDataSource, PerfDataSource.idhost == Host.idhost),
                    (GRAPH_PERFDATASOURCE_TABLE, \
                        GRAPH_PERFDATASOURCE_TABLE.c.idperfdatasource == \
                        PerfDataSource.idperfdatasource),
                    (Graph, Graph.idgraph == \
                        GRAPH_PERFDATASOURCE_TABLE.c.idgraph),
                    (SUPITEM_GROUP_TABLE, SUPITEM_GROUP_TABLE.c.idsupitem == \
                        Host.idhost),
                ).filter(Host.name.ilike(search_form_host)
                ).filter(Graph.name.ilike(search_form_graph)
                ).order_by(
                    Host.name.asc(),
                    Graph.name.asc(),
                )

        # On a ni hôte, ni indicateur. On renvoie une liste vide.
        # Si l'utilisateur voulait vraiment quelque chose,
        # il n'avait qu'à le demander.
        elif not search_form_host:
            return []

        # Sinon, on a juste un motif pour un hôte.
        # On renvoie la liste des hôtes correspondant.
        else:
            search_form_host = sql_escape_like(search_form_host)
            items = DBSession.query(
                    Host.idhost.label('idhost'),
                    Host.name.label('hostname'),
                ).distinct().join(
                    (SUPITEM_GROUP_TABLE, SUPITEM_GROUP_TABLE.c.idsupitem == \
                        Host.idhost),
                ).filter(Host.name.ilike(search_form_host)
                ).order_by(Host.name.asc())

        # Les managers ont accès à tout.
        # Les autres ont un accès restreint.
        is_manager = in_group('managers').is_met(request.environ)
        if not is_manager:
            supitemgroups = [sig[0] for sig in user.supitemgroups() if sig[1]]
            # pylint: disable-msg=E1103
            items = items.filter(
                SUPITEM_GROUP_TABLE.c.idgroup.in_(supitemgroups))

        items = items.limit(100).all() # pylint: disable-msg=E1103
        if not search_form_graph:
            ids = [(item.idhost, None) for item in items]
            labels = [(item.hostname, None) for item in items]
        else:
            ids = [(item.idhost, item.idgraph) for item in items]
            labels = [(item.hostname, item.graphname) for item in items]

        return dict(labels=labels, ids=ids)

    @expose('graphslist.html')
    def graphsList(self, nocache=None, **kwargs):
        """
        Generation document avec url des graphes affiches
        (pour l impression )

        @param kwargs : arguments nommes
        @type kwargs  : dict

        @return: url de graphes
        @rtype: document html
        """
        # @TODO: le must serait de hot-patcher mootools pour que son serializer
        # d'URL utilise directement le format attendu par TurboGears
        # (notation pointée plutôt qu'avec des crochets)

        if not kwargs:
            return dict(graphslist=[])

        # On est obligé de convertir le format en UTF-8 car strftime
        # n'accepte pas les chaînes Unicode en entrée.
        # TRANSLATORS: Format Python de date/heure, lisible par un humain.
        format = _("%a, %d %b %Y %H:%M:%S").encode('utf8')
        i = 0
        graphslist = []

        while True:
            try:
                host = kwargs['graphs[%d][host]' % i]
                graph = kwargs['graphs[%d][graph]' % i]
                start = int(kwargs.get('graphs[%d][start]' % i, time.time() - 86400))
                duration = int(kwargs.get('graphs[%d][duration]' % i))
                nocache = kwargs['graphs[%d][nocache]' % i]
            except KeyError:
                break

            if not (host and graph and duration and nocache):
                break

            graphslist.append({
                'host': host,
                'graph': graph,
                'start': start,
                'duration': duration,
                'nocache': nocache,
                'start_date': time.strftime(format,
                    time.localtime(start)).decode('utf8'),
                'end_date': time.strftime(format,
                    time.localtime(start + duration)).decode('utf8')
            })
            i += 1
        return dict(graphslist=graphslist)

    @expose('json')
    def tempoDelayRefresh(self, nocache=None):
        """
        Determination valeur temporisation pour le rafraichissement automatique
        d un graphe

        @return: valeur de temporisation
        @rtype: C{str}
        """

        try:
            delay = int(config['refresh_delay'])
        except (ValueError, KeyError):
            delay = 30
        return {'delay': delay}

    class GetIndicatorsSchema(schema.Schema):
        """Schéma de validation pour la méthode L{getIndicators}."""
        host = validators.String(not_empty=True)
        graph = validators.String(not_empty=True)
        nocache = validators.String(if_missing=None)

    # @TODO définir un error_handler différent pour remonter l'erreur via JS.
    @validate(
        validators = GetIndicatorsSchema(),
        error_handler = process_form_errors)
    @expose('json')
    def getIndicators(self, host, graph, nocache):
        """
        Liste d indicateurs associes a un graphe

        @param graph : graphe
        @type graph  : C{str}

        @return: dictionnaire des indicateurs d un graphe
        @rtype: document json (sous forme de dict)
        """

        indicators = self.getListIndicators(host, graph)
        indicators = [(ind.name, ind.label) for ind in indicators]
        return dict(items=indicators)

    class StartTimeSchema(schema.Schema):
        """Schéma de validation pour la méthode L{getIndicators}."""
        host = validators.String(not_empty=True)
        nocache = validators.String(if_missing=None)

    # @TODO définir un error_handler différent pour remonter l'erreur via JS.
    @validate(
        validators = StartTimeSchema(),
        error_handler = process_form_errors)
    @expose('json')
    def startTime(self, host, nocache):
        return get_through_proxy(
            'vigirrd', host,
            '/starttime?host=%s' % urllib2.quote(host, '')
        )

    class FullHostPageSchema(schema.Schema):
        """Schéma de validation pour la méthode L{fullHostPage}."""
        host = validators.String(not_empty=True)
        start = validators.Int(if_missing=None)
        duration = validators.Int(if_missing=86400)

    # VIGILO_EXIG_VIGILO_PERF_0010:Visualisation globale des graphes
    # VIGILO_EXIG_VIGILO_PERF_0020:Visualisation unitaire des graphes
    # On utilise la même page pour les 2 fonctionalités.
    @validate(
        validators = FullHostPageSchema(),
        error_handler = process_form_errors)
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

        start = int(start)
        duration = int(duration)

        user = get_current_user()
        if user is None:
            return dict(host=host, start=start, duration=duration,
                        presets=self.presets, graphs=[])

        # Récupération de la liste des noms des graphes,
        # avec vérification des permissions de l'utilisateur.
        graphs = DBSession.query(
                Graph.name
            ).distinct(
            ).join(
                (GRAPH_PERFDATASOURCE_TABLE,
                    GRAPH_PERFDATASOURCE_TABLE.c.idgraph == Graph.idgraph),
                (PerfDataSource, PerfDataSource.idperfdatasource ==
                    GRAPH_PERFDATASOURCE_TABLE.c.idperfdatasource),
                (Host, Host.idhost == PerfDataSource.idhost),
                (SUPITEM_GROUP_TABLE, SUPITEM_GROUP_TABLE.c.idsupitem == \
                    Host.idhost),
            ).filter(Host.name == host)

        # Les managers ont accès à tout.
        # Les autres ont un accès restreint.
        is_manager = in_group('managers').is_met(request.environ)
        if not is_manager:
            supitemgroups = [sig[0] for sig in user.supitemgroups() if sig[1]]
            graphs = graphs.filter(
                SUPITEM_GROUP_TABLE.c.idgroup.in_(supitemgroups))

        graphs = graphs.all()
        return dict(host=host, start=start, duration=duration,
                    presets=self.presets, graphs=graphs)


    @expose('searchhost.html')
    @paginate('hosts', items_per_page=10)
    def searchHost(self, *args, **kwargs):
        """
        Affiche les résultats de la recherche par nom d'hôte.
        La requête de recherche (L{query}) correspond à un préfixe
        qui sera recherché dans le nom d'hôte. Ce préfixe peut
        contenir les caractères '*' et '?' qui agissent comme des
        "jokers".

        @param query: Prefixe de recherche sur les noms d'hôtes
        @type query: C{unicode}
        """
        query = kwargs.get('query')
        if not query:
            redirect("searchHostForm")

        query = sql_escape_like(query.strip())
        user = get_current_user()
        if user is None:
            return dict(items=[])

        # Récupère les hôtes auxquels l'utilisateur a réellement accès.
        hosts = DBSession.query(
                Host.name,
            ).distinct(
            ).join(
                (SUPITEM_GROUP_TABLE, SUPITEM_GROUP_TABLE.c.idsupitem == \
                    Host.idhost),
            ).filter(Host.name.like(query + u'%')
            ).order_by(
                Host.name.asc(),
            )

        # Les managers ont accès à tout.
        # Les autres ont un accès restreint.
        is_manager = in_group('managers').is_met(request.environ)
        if not is_manager:
            supitemgroups = [sig[0] for sig in user.supitemgroups() if sig[1]]
            hosts = hosts.filter(
                SUPITEM_GROUP_TABLE.c.idgroup.in_(supitemgroups))

        return dict(hosts=hosts)

    # VIGILO_EXIG_VIGILO_PERF_0030:Moteur de recherche des graphes
    @expose('getopensearch.xml', content_type='text/xml')
    def getOpenSearch(self):
        """
        Moteur de recherche des graphes

        @return: document
        @rtype: document xml
        """
        return dict()

    @expose('json')
    def hosttree(self, parent_id=None):
        """
        Affiche un étage de l'arbre de
        sélection des hôtes et groupes d'hôtes.

        @param parent_id: identifiant du groupe d'hôte parent
        @type  parent_id: C{int} or None
        """

        # Si l'identifiant du groupe parent n'est pas
        # spécifié, on retourne la liste des groupes racines,
        # fournie par la méthode get_root_host_groups.
        if parent_id is None:
            return self.get_root_host_groups()

        # TODO: Utiliser un schéma de validation
        parent_id = int(parent_id)
        parent = DBSession.query(SupItemGroup).get(parent_id)
        if not parent:
            return dict(groups = [], leaves = [])

        # On récupère la liste des groupes qui ont pour parent
        # le groupe dont l'identifiant est passé en paramètre
        # et auquel l'utilisateur a accès.
        db_groups = list(parent.children) # copie
        user = get_current_user()
        is_manager = in_group('managers').is_met(request.environ)
        user_groups = {}
        if not is_manager:
            user_groups = dict(user.supitemgroups())
            copy = list(db_groups)
            for db_group in copy:
                if not user_groups.get(db_group.idgroup, False):
                    db_groups.remove(db_group)

        groups = []
        for group in db_groups:
            groups.append({
                'id'   : group.idgroup,
                'name' : group.name,
            })

        # On récupère la liste des hôtes appartenant au
        # groupe dont l'identifiant est passé en paramètre
        hosts = []
        if is_manager or user_groups.get(parent_id, False):
            db_hosts = DBSession.query(
                Host.idhost,
                Host.name,
            ).join(
                SUPITEM_GROUP_TABLE,
            ).filter(SUPITEM_GROUP_TABLE.c.idgroup == parent_id
            ).order_by(Host.name.asc())
            hosts = []
            for host in db_hosts.all():
                hosts.append({
                    'id'   : host.idhost,
                    'name' : host.name,
                })

        return dict(groups = groups, leaves = hosts)

    @expose('json')
    def graphtree(self, host_id=None, parent_id=None):
        """
        Affiche un étage de l'arbre de sélection
        des graphes et groupes de graphes.

        @param parent_id: identifiant du groupe de graphes parent
        @type  parent_id: C{int} or None
        """

        # Si l'identifiant de l'hôte n'est pas spécifié, on
        # retourne un dictionnaire contenant deux listes vides
        if host_id is None:
            return dict(groups = [], leaves=[])

        # On vérifie les permissions sur l'hôte
        # TODO: Utiliser un schéma de validation
        host_id = int(host_id)
        host = DBSession.query(Host).get(host_id)
        if host is None:
            return dict(groups = [], leaves=[])
        user = get_current_user()
        if not host.is_allowed_for(user):
            return dict(groups = [], leaves=[])

        # On récupère la liste des groupes de graphes associés à l'hôte
        host_graph_groups = DBSession.query(
            GraphGroup
        ).distinct(
        ).join(
            (GRAPH_GROUP_TABLE, \
                GRAPH_GROUP_TABLE.c.idgroup == GraphGroup.idgroup),
            (Graph, Graph.idgraph == GRAPH_GROUP_TABLE.c.idgraph),
            (GRAPH_PERFDATASOURCE_TABLE, \
                    GRAPH_PERFDATASOURCE_TABLE.c.idgraph == Graph.idgraph),
            (PerfDataSource, PerfDataSource.idperfdatasource == \
                    GRAPH_PERFDATASOURCE_TABLE.c.idperfdatasource),
        ).filter(PerfDataSource.idhost == host_id
        ).order_by(GraphGroup.name.asc())
        host_graph_groups = host_graph_groups.all()

        # Si l'identifiant du groupe parent n'est pas spécifié,
        # on récupère la liste des groupes de graphes racines.
        if parent_id is None:
            graph_groups = GraphGroup.get_top_groups()[0].children

        # Sinon on récupère la liste des graphes dont le
        # groupe passé en paramètre est le parent direct.
        else:
            # TODO: Utiliser un schéma de validation
            parent_id = int(parent_id)
            parent = DBSession.query(GraphGroup).get(parent_id)
            graph_groups = parent.children

        # On réalise l'intersection des deux listes
        groups = []
        for gg in graph_groups:
            if gg in host_graph_groups:
                groups.append({
                    'id'   : gg.idgroup,
                    'name' : gg.name,
                })

        # On récupère la liste des graphes appartenant au
        # groupe dont l'identifiant est passé en paramètre
        graphs = []
        if parent_id:
            db_graphs = DBSession.query(
                Graph.idgraph,
                Graph.name,
            ).distinct(
            ).join(
                (GRAPH_GROUP_TABLE,
                    GRAPH_GROUP_TABLE.c.idgraph == Graph.idgraph),
                (GRAPH_PERFDATASOURCE_TABLE,
                    GRAPH_PERFDATASOURCE_TABLE.c.idgraph == Graph.idgraph),
                (PerfDataSource,
                    PerfDataSource.idperfdatasource == \
                        GRAPH_PERFDATASOURCE_TABLE.c.idperfdatasource),
            ).filter(GRAPH_GROUP_TABLE.c.idgroup == parent_id
            ).filter(PerfDataSource.idhost == host_id
            ).order_by(Graph.name.asc())
            for graph in db_graphs.all():
                graphs.append({
                    'id'   : graph.idgraph,
                    'name' : graph.name,
                })

        return dict(groups = groups, leaves = graphs)

    def get_root_host_groups(self):
        """
        Retourne tous les groupes racines (c'est à dire n'ayant
        aucun parent) d'hôtes auquel l'utilisateur a accès.

        @return: Un dictionnaire contenant la liste de ces groupes.
        @rtype : C{dict} of C{list} of C{dict} of C{mixed}
        """

        root_groups = list(SupItemGroup.get_top_groups()[0].children)

        # On filtre ces groupes racines afin de ne
        # retourner que ceux auquels l'utilisateur a accès
        user = get_current_user()
        is_manager = in_group('managers').is_met(request.environ)
        if not is_manager:
            user_groups = [sig[0] for sig in user.supitemgroups()]
            copy = list(root_groups)
            for root_group in copy:
                if root_group.idgroup not in user_groups:
                    root_groups.remove(root_group)

        groups = []
        for group in root_groups:
            groups.append({
                'id'   : group.idgroup,
                'name' : group.name,
            })

        return dict(groups = groups, leaves=[])

    def getListIndicators(self, host, graph):
        """
        Liste d indicateurs associes a un graphe

        @param graph : graphe
        @type graph  : C{str}

        @return: liste d indicateurs
        @rtype  : list
        """

        indicators = []
        if graph is not None:
            indicators = DBSession.query(
                    PerfDataSource.name, PerfDataSource.label
                ).distinct(
                ).join(
                    (GRAPH_PERFDATASOURCE_TABLE, \
                        GRAPH_PERFDATASOURCE_TABLE.c.idperfdatasource == \
                        PerfDataSource.idperfdatasource),
                    (Graph, Graph.idgraph == \
                        GRAPH_PERFDATASOURCE_TABLE.c.idgraph),
                    (Host, Host.idhost == PerfDataSource.idhost),
                ).filter(Graph.name == graph
                ).filter(Host.name == host
                ).all()
        return indicators

    @expose('json')
    def dbmtime(self):
        change = Change.by_table_name(u"Graph")
        if change is None:
            return {"mtime": None}
        mtime = change.last_modified.replace(microsecond=0)
        return {"mtime": mtime}

    @expose('json')
    def selectHostAndGraph(self, host, graph):
        # @TODO: vérifier les permissions
        ids = DBSession.query(
                Host.idhost, Graph.idgraph
            ).join(
                (PerfDataSource, PerfDataSource.idhost == Host.idhost),
                (GRAPH_PERFDATASOURCE_TABLE, \
                    GRAPH_PERFDATASOURCE_TABLE.c.idperfdatasource == \
                    PerfDataSource.idperfdatasource),
                (Graph, Graph.idgraph == \
                    GRAPH_PERFDATASOURCE_TABLE.c.idgraph),
            ).filter(Graph.name == unicode(graph)
            ).filter(Host.name == unicode(host)
            ).first()

        return {
            'idhost': ids and ids.idhost or None,
            'idgraph': ids and ids.idgraph or None,
        }
