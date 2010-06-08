# -*- coding: utf-8 -*-
"""RPC controller for the combobox of vigigraph"""

import time, urlparse
import logging

# La fonction parse_qsl a été déplacée dans Python 2.6.
try:
    from urlparse import parse_qsl
except ImportError:
    from cgi import parse_qsl

from pylons.i18n import ugettext as _, lazy_ugettext as l_
from tg import expose, request, redirect, tmpl_context, \
                config, validate, flash
from tg.decorators import paginate
from repoze.what.predicates import not_anonymous, has_permission, \
                                    in_group, Any, All
from formencode import validators, schema
from sqlalchemy import or_

from vigilo.turbogears.controllers import BaseController
from vigilo.turbogears.helpers import get_current_user

from vigilo.models.session import DBSession
from vigilo.models.tables import Host
from vigilo.models.tables import SupItemGroup
from vigilo.models.tables import PerfDataSource
from vigilo.models.tables import Graph, GraphGroup
from vigilo.models.tables.grouphierarchy import GroupHierarchy

from vigilo.models.tables.secondary_tables import SUPITEM_GROUP_TABLE
from vigilo.models.tables.secondary_tables import GRAPH_GROUP_TABLE
from vigilo.models.tables.secondary_tables import GRAPH_PERFDATASOURCE_TABLE
from vigilo.models.functions import sql_escape_like

from vigigraph.widgets.searchhostform import SearchHostForm

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
                msg=l_("You don't have access on VigiGraph")),
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
        user = get_current_user()
        if user is None:
            return dict(items=[])

        groups_with_parents = DBSession.query(
                GroupHierarchy.idparent,
            ).distinct()

        # Les managers ont accès à tout.
        # Les autres ont un accès restreint.
        is_manager = in_group('managers').is_met(request.environ)
        if not is_manager:
            supitemgroups = [sig[0] for sig in user.supitemgroups() if sig[1]]
            groups_with_parents = groups_with_parents.filter(
                GroupHierarchy.idchild.in_(supitemgroups))

        groups_with_parents = [g.idparent for g in groups_with_parents.all()]
        children = DBSession.query(
                SupItemGroup
            ).distinct(
            ).join(
                (GroupHierarchy, GroupHierarchy.idchild == SupItemGroup.idgroup)
            ).filter(GroupHierarchy.hops > 0)

        topgroups = DBSession.query(
                SupItemGroup,
            ).filter(SupItemGroup.idgroup.in_(groups_with_parents)
            ).except_(children).order_by(SupItemGroup.name).all()
        topgroups = [(sig.name, str(sig.idgroup)) for sig in topgroups]
        return dict(items=topgroups)

    class HostgroupsSchema(schema.Schema):
        """Schéma de validation pour la méthode L{hostgroups}."""
        maingroupid = validators.Int(not_empty=True)
        nocache = validators.String(if_missing=None)

    # @TODO définir un error_handler différent pour remonter l'erreur via JS.
    @validate(
        validators = HostgroupsSchema(),
        error_handler = process_form_errors)
    @expose('json')
    def hostgroups(self, maingroupid, nocache):
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
        user = get_current_user()
        if user is None:
            return dict(items=[])

        hostgroups = DBSession.query(
                SupItemGroup.name,
                SupItemGroup.idgroup,
            ).distinct().join(
                (GroupHierarchy, GroupHierarchy.idchild == \
                    SupItemGroup.idgroup),
            ).filter(GroupHierarchy.idparent == maingroupid
            ).filter(GroupHierarchy.hops == 1
            ).order_by(SupItemGroup.name.asc())

        # Les managers ont accès à tout.
        # Les autres ont un accès restreint.
        is_manager = in_group('managers').is_met(request.environ)
        if not is_manager:
            supitemgroups = [sig[0] for sig in user.supitemgroups() if sig[1]]
            hostgroups = hostgroups.filter(
                SupItemGroup.idgroup.in_(supitemgroups))

        hostgroups = [(hg.name, str(hg.idgroup)) for hg in hostgroups.all()]
        hostgroups.insert(0, (_('No subgroup'), str(maingroupid)))
        return dict(items=hostgroups)

    class HostsSchema(schema.Schema):
        """Schéma de validation pour la méthode L{hosts}."""
        othergroupid = validators.Int(not_empty=True)
        nocache = validators.String(if_missing=None)

    # @TODO définir un error_handler différent pour remonter l'erreur via JS.
    @validate(
        validators = HostsSchema(),
        error_handler = process_form_errors)
    @expose('json')
    def hosts(self, othergroupid, nocache):
        """
        Determination des hotes associes au groupe
        dont identificateur = argument

        @param othergroupid : identificateur d un groupe
        @type othergroupid : int

        @return: hotes
        @rtype: document json (sous forme de dict)
        """
        user = get_current_user()
        if user is None:
            return dict(items=[])

        groups_with_parents = DBSession.query(
                GroupHierarchy.idparent,
            ).distinct()

        # Les managers ont accès à tout.
        # Les autres ont un accès restreint.
        is_manager = in_group('managers').is_met(request.environ)
        if not is_manager:
            supitemgroups = [sig[0] for sig in user.supitemgroups() if sig[1]]
            groups_with_parents = groups_with_parents.filter(
                GroupHierarchy.idchild.in_(supitemgroups))

        groups_with_parents = [g.idparent for g in groups_with_parents.all()]
        hosts = DBSession.query(
                Host.name,
                Host.idhost,
            ).distinct(
            ).join(
                (SUPITEM_GROUP_TABLE, SUPITEM_GROUP_TABLE.c.idsupitem == \
                    Host.idhost),
            ).filter(SUPITEM_GROUP_TABLE.c.idgroup == othergroupid
            ).filter(SUPITEM_GROUP_TABLE.c.idgroup.in_(groups_with_parents)
            ).order_by(
                Host.name.asc(),
            ).all()
            
        hosts = [(h.name, str(h.idhost)) for h in hosts]
        return dict(items=hosts)

    class GraphGroupsSchema(schema.Schema):
        """Schéma de validation pour la méthode L{graphgroups}."""
        idhost = validators.Int(not_empty=True)
        nocache = validators.String(if_missing=None)

    # @TODO définir un error_handler différent pour remonter l'erreur via JS.
    @validate(
        validators = GraphGroupsSchema(),
        error_handler = process_form_errors)
    @expose('json')
    def graphgroups(self, idhost, nocache):
        """
        Determination des groupes de graphes associes a l hote
        dont identificateur = argument

        @param idhost : identificateur d un hote
        @type idhost : int

        @return: groupes de service
        @rtype: document json (sous forme de dict)
        """
        user = get_current_user()
        if user is None:
            return dict(items=[])

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
                (SUPITEM_GROUP_TABLE, SUPITEM_GROUP_TABLE.c.idsupitem == \
                    PerfDataSource.idhost),
            ).filter(PerfDataSource.idhost == idhost
            ).order_by(GraphGroup.name.asc())

        # Les managers ont accès à tout.
        # Les autres ont un accès restreint.
        is_manager = in_group('managers').is_met(request.environ)
        if not is_manager:
            supitemgroups = [sig[0] for sig in user.supitemgroups() if sig[1]]
            graphgroups = graphgroups.filter(
                SUPITEM_GROUP_TABLE.c.idgroup.in_(supitemgroups))
        
        graphgroups = [(gg.name, str(gg.idgroup)) for gg in graphgroups.all()]
        return dict(items=graphgroups)

    class GraphsSchema(schema.Schema):
        """Schéma de validation pour la méthode L{graphs}."""
        idgraphgroup = validators.Int(not_empty=True)
        idhost = validators.Int(not_empty=True)
        nocache = validators.String(if_missing=None)

    # @TODO définir un error_handler différent pour remonter l'erreur via JS.
    @validate(
        validators = GraphsSchema(),
        error_handler = process_form_errors)
    @expose('json')
    def graphs(self, idgraphgroup, idhost, nocache):
        """
        Determination des graphes
        avec un service dont identificateur = argument

        @param idgraph : identificateur d un service
        @type idgraph : int

        @return: graphes
        @rtype: document json (sous forme de dict)
        """
        user = get_current_user()
        if user is None:
            return dict(items=[])

        graphs = DBSession.query(
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
                (SUPITEM_GROUP_TABLE, SUPITEM_GROUP_TABLE.c.idsupitem == \
                    PerfDataSource.idhost),
            ).filter(GraphGroup.idgroup == idgraphgroup
            ).filter(PerfDataSource.idhost == idhost
            ).order_by(Graph.name.asc())

        # Les managers ont accès à tout.
        # Les autres ont un accès restreint.
        is_manager = in_group('managers').is_met(request.environ)
        if not is_manager:
            supitemgroups = [sig[0] for sig in user.supitemgroups() if sig[1]]
            graphs = graphs.filter(
                SUPITEM_GROUP_TABLE.c.idgroup.in_(supitemgroups))

        graphs = [(pds.name, str(pds.idgraph)) for pds in graphs.all()]
        return dict(items=graphs)

    class SearchHostAndGraphSchema(schema.Schema):
        """Schéma de validation pour la méthode L{searchHostAndGraph}."""
        host = validators.String(if_missing=None)
        graph = validators.String(if_missing=None)
        nocache = validators.String(if_missing=None)

    # @TODO définir un error_handler différent pour remonter l'erreur via JS.
    @validate(
        validators = SearchHostAndGraphSchema(),
        error_handler = process_form_errors)
    @expose('json')
    def searchHostAndGraph(self, host, graph, nocache):
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
        user = get_current_user()
        items = []

        if user is None:
            return dict(items=[])

        # On a un nom d'indicateur, mais pas de nom d'hôte,
        # on considère que l'utilisateur veut tous les indicateurs
        # correspondant au motif, quel que soit l'hôte.
        if graph is not None:
            if host is None:
                host = '*'

            host = sql_escape_like(host)
            graph = sql_escape_like(graph)

            items = DBSession.query(
                    Host.name.label('hostname'),
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
                ).join(
                    (SUPITEM_GROUP_TABLE, SUPITEM_GROUP_TABLE.c.idsupitem == \
                        Host.idhost),
                ).filter(Host.name.ilike('%' + host + '%')
                ).order_by(Host.name.asc())

        # Les managers ont accès à tout.
        # Les autres ont un accès restreint.
        is_manager = in_group('managers').is_met(request.environ)
        if not is_manager:
            supitemgroups = [sig[0] for sig in user.supitemgroups() if sig[1]]
            items = items.filter(
                SUPITEM_GROUP_TABLE.c.idgroup.in_(supitemgroups))

        items = items.limit(100).all()
        if graph is None:
            items = [(item.hostname, "") for item in items]
        else:
            items = [(item.hostname, item.graphname) for item in items]
        return dict(items=items)

    class SelectHostAndGraphSchema(schema.Schema):
        """Schéma de validation pour la méthode L{selectHostAndGraph}."""
        host = validators.String(if_missing=None)
        graph = validators.String(if_missing=None)
        nocache = validators.String(if_missing=None)

    # @TODO définir un error_handler différent pour remonter l'erreur via JS.
    @validate(
        validators = SelectHostAndGraphSchema(),
        error_handler = process_form_errors)
    @expose('json')
    def selectHostAndGraph(self, host, graph, nocache):
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
                ).distinct().join(
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
                    ).distinct().join(
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
                ).distinct().join(
                    (GRAPH_GROUP_TABLE, GRAPH_GROUP_TABLE.c.idgroup == \
                        GraphGroup.idgroup),
                    (Graph, Graph.idgraph == GRAPH_GROUP_TABLE.c.idgraph),
                ).filter(Graph.name == graph
                ).scalar()

            # Même principe que pour l'hôte.
            if idgraphgroup is not None:
                selected_graphgroups = DBSession.query(
                        GraphGroup.name,
                    ).distinct().join(
                        (GroupHierarchy, GroupHierarchy.idparent == \
                            GraphGroup.idgroup),
                    ).filter(GroupHierarchy.idchild == idgraphgroup
                    ).order_by(
                        GroupHierarchy.hops.desc()
                    ).all()

        hostgroups = [hg.name for hg in selected_hostgroups]
        # @FIXME: Ce test est nécessaire tant que l'interface Qooxdoo
        # monolithique est conservée (ie: 2 niveaux de profondeur figés).
        if len(hostgroups) != 2:
            hostgroups.append(_('No subgroup'))
        graphgroups = [gg.name for gg in selected_graphgroups]
        return dict(items=[hostgroups, graphgroups])        

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
        if not kwargs:
            return dict(graphslist=[])

        # TRANSLATORS: Format Python de date/heure, lisible par un humain.
        format = _("%a, %d %b %Y %H:%M:%S")
        graphslist = []
        for url in kwargs.itervalues():
            parts = urlparse.urlparse(url)
            params = dict(parse_qsl(parts.query))

            graph = {}
            start = int(params.get('start', time.time() - 86400))
            duration = int(params.get('duration', 86400))

            graph['graph'] = params.get('graphtemplate')
            graph['start_date'] = time.strftime(format, time.localtime(start))
            graph['end_date'] = time.strftime(format,
                                    time.localtime(start + duration))
            graph['img_src'] = url
            graph['host'] = params['host']
            graphslist.append(graph)
        return dict(graphslist=graphslist)

    @expose(content_type='text/plain')
    def tempoDelayRefresh(self, nocache=None):
        """
        Determination valeur temporisation pour le rafraichissement automatique
        d un graphe

        @return: valeur de temporisation
        @rtype: C{str}
        """

        try:
            delay = int(config['delay_refresh'])
        except (ValueError, KeyError):
            delay = 36000
        return str(delay)

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
        indicators = [ind.name for ind in indicators]
        return dict(items=indicators)


    class FullHostPageSchema(schema.Schema):
        """Schéma de validation pour la méthode L{fullHostPage}."""
        host = validators.String(not_empty=True)
        start = validators.Int(if_missing=None)
        duration = validators.Int(if_missing=86400)

    # VIGILO_EXIG_VIGILO_PERF_0010:Visualisation globale des graphes
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
            )

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


    class SingleGraphSchema(schema.Schema):
        """Schéma de validation pour la méthode L{singleGraph}."""
        host = validators.String(not_empty=True)
        graph = validators.String(not_empty=True)
        start = validators.Int(if_missing=None)
        duration = validators.Int(if_missing=86400)

    # VIGILO_EXIG_VIGILO_PERF_0020:Visualisation unitaire des graphes
    @validate(
        validators = SingleGraphSchema(),
        error_handler = process_form_errors)
    @expose('singlegraph.html')
    def singleGraph(self, host, graph, start, duration):
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

        start = int(start)
        duration = int(duration)

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
            ).filter(Host.name.like(query + '%')
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
                    PerfDataSource.name
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

