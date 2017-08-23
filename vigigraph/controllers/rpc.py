# -*- coding: utf-8 -*-
# Copyright (C) 2006-2016 CS-SI
# License: GNU GPL v2 <http://www.gnu.org/licenses/gpl-2.0.html>

"""RPC controller for the combobox of vigigraph"""

# pylint: disable-msg=W0613
# W0613: Unused argument : les arguments des contrôleurs sont les composants
#        de la query-string de l'URL


import time
import urllib2
import urlparse
import logging

from tg.i18n import ugettext as _, lazy_ugettext as l_, lazy_ungettext as ln_
from tg import expose, request, redirect, tmpl_context, \
    config, validate, flash, exceptions as http_exc
from tg.predicates import not_anonymous, has_permission, in_group, Any, All

from formencode import schema
from tw.forms import validators
from sqlalchemy.orm import aliased, lazyload
from sqlalchemy.sql import functions

from vigilo.turbogears.controllers import BaseController
from vigilo.turbogears.helpers import get_current_user
from vigilo.turbogears.controllers.proxy import get_through_proxy
from tg.decorators import paginate

from vigilo.models.session import DBSession
from vigilo.models.tables import Host, SupItemGroup, PerfDataSource
from vigilo.models.tables import Graph, GraphGroup, Change, UserGroup
from vigilo.models.tables import DataPermission
from vigilo.models.tables.group import Group
from vigilo.models.tables.grouphierarchy import GroupHierarchy

from vigilo.models.tables.secondary_tables import SUPITEM_GROUP_TABLE
from vigilo.models.tables.secondary_tables import GRAPH_GROUP_TABLE
from vigilo.models.tables.secondary_tables import GRAPH_PERFDATASOURCE_TABLE
from vigilo.models.tables.secondary_tables import USER_GROUP_TABLE
from vigilo.models.functions import sql_escape_like

LOGGER = logging.getLogger(__name__)

__all__ = ['RpcController']

def ungettext(singular, plural, n):
    return ln_(singular, plural, n) % {
        'qtty': n,
    }

# pylint: disable-msg=R0201
class RpcController(BaseController):
    """
    Class Controleur TurboGears
    """

    # L'accès à ce contrôleur nécessite d'être identifié.
    allow_only = All(
        not_anonymous(msg=l_("You need to be authenticated")),
        Any(
            config.is_manager,
            has_permission('vigigraph-access',
                msg=l_("You don't have access to VigiGraph")),
        ),
    )

    # Plages de temps affichées sur la page de métrologie complète
    # d'un hôte avec la durée associée (en secondes).
    # Voir aussi graph.js pour l'équivalent côté JavaScript sur un graphe.
    presets = [
        {
            "caption" :
                ungettext("Last %(qtty)d hour", "Last %(qtty)d hours", 12),
            "duration" : 43200,
        },
        {
            "caption" :
                ungettext("Last %(qtty)d hour", "Last %(qtty)d hours", 24),
            "duration" : 86400,
        },
        {
            "caption" :
                ungettext("Last %(qtty)d day", "Last %(qtty)d days", 2),
            "duration" : 192800,
        },
        {
            "caption" :
                ungettext("Last %(qtty)d day", "Last %(qtty)d days", 7),
            "duration" : 604800,
        },
        {
            "caption" :
                ungettext("Last %(qtty)d day", "Last %(qtty)d days", 14),
            "duration" : 1209600,
        },
        {
            "caption" :
                ungettext("Last %(qtty)d month", "Last %(qtty)d months", 1),
            "duration" : 86400 * 30,
        },
        {
            "caption" :
                ungettext("Last %(qtty)d month", "Last %(qtty)d months", 3),
            "duration" : 86400 * 30 * 3,
        },
        {
            "caption" :
                ungettext("Last %(qtty)d month", "Last %(qtty)d months", 6),
            "duration" : 86400 * 30 * 6,
        },
        {
            "caption" :
                ungettext("Last %(qtty)d year", "Last %(qtty)d years", 1),
            "duration" : 86400 * 365,
        },
    ]

    def process_form_errors(self, *args, **kwargs):
        """
        Gestion des erreurs de validation : On affiche les erreurs
        puis on redirige vers la dernière page accédée.
        """
        for k in tmpl_context.form_errors:
            flash("'%s': %s" % (k, tmpl_context.form_errors[k]), 'error')
        redirect(request.environ.get('HTTP_REFERER', '/'))

    class SearchHostAndGraphSchema(schema.Schema):
        """Schéma de validation pour la méthode L{searchHostAndGraph}."""
        search_form_host = validators.UnicodeString(if_missing=None)
        search_form_graph = validators.UnicodeString(if_missing=None)

    # @TODO définir un error_handler différent pour remonter l'erreur via JS.
    @validate(
        validators = SearchHostAndGraphSchema(),
        error_handler = process_form_errors)
    @expose('json')
    def searchHostAndGraph(self, search_form_host=None, search_form_graph=None):
        """
        Determination des couples (hote-graphe) repondant aux criteres de
        recherche sur hote et/ou graphe.

        Un critere peut correspondre a un intitule complet hote ou graphe
        ou a un extrait.

        @return: couples hote-graphe
        @rtype: document json (sous forme de dict)
        """
        limit = 100
        user = get_current_user()
        ids = []
        labels = []

        if user is None:
            return dict(items=[])

        # On a un nom d'indicateur, mais pas de nom d'hôte,
        # on considère que l'utilisateur veut tous les indicateurs
        # correspondant au motif, quel que soit l'hôte.
        if search_form_graph:
            if not search_form_host:
                search_form_host = u'*'

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
        if not config.is_manager.is_met(request.environ):
            supitemgroups = [sig[0] for sig in user.supitemgroups() if sig[1]]
            # pylint: disable-msg=E1103
            items = items.join(
                (GroupHierarchy, GroupHierarchy.idchild == \
                    SUPITEM_GROUP_TABLE.c.idgroup)
            ).filter(GroupHierarchy.idparent.in_(supitemgroups))

        items = items.limit(limit + 1).all() # pylint: disable-msg=E1103
        more_results = len(items) > limit

        if not search_form_graph:
            for i in xrange(min(limit, len(items))):
                ids.append((items[i].idhost, None))
                labels.append((items[i].hostname, None))
        else:
            for i in xrange(min(limit, len(items))):
                ids.append((items[i].idhost, items[i].idgraph))
                labels.append((items[i].hostname, items[i].graphname))

        return dict(labels=labels, ids=ids, more=more_results)

    @expose('graphslist.html')
    def graphsList(self, graphs=None, **kwargs):
        """
        Génération d'une page d'impression avec les graphes sélectionnés.

        @param graphs : Liste des graphes à imprimer
        @type graphs  : C{list}
        @param kwargs : arguments supplémentaires (inutilisés)
        @type kwargs  : c{dict}

        @return: Paramètres pour la génération de la page d'impression
        @rtype: dict
        """
        # @TODO: le must serait de hot-patcher mootools pour que son serializer
        # d'URL utilise directement le format attendu par TurboGears
        # (notation pointée plutôt qu'avec des crochets)

        if not graphs:
            return dict(graphslist=[])

        if not isinstance(graphs, list):
            graphs = [graphs]

        # On est obligé de convertir le format en UTF-8 car strftime
        # n'accepte pas les chaînes Unicode en entrée.
        # TRANSLATORS: Format Python de date/heure, lisible par un humain.
        format = _("%a, %d %b %Y %H:%M:%S").encode('utf8')
        graphslist = []
        for graph in graphs:
            params = urlparse.parse_qs(graph, True, True)
            try:
                host = params['host'][0]
                graph = params['graph'][0]
                start = int(params['start'][0] or time.time() - 86400)
                duration = int(params['duration'][0])
                nocache = params['nocache'][0]
            except (KeyError, TypeError, ValueError):
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
        host = validators.UnicodeString(not_empty=True)
        graph = validators.UnicodeString(not_empty=True)
        nocache = validators.UnicodeString(if_missing=None)

    # @TODO définir un error_handler différent pour remonter l'erreur via JS.
    @validate(
        validators = GetIndicatorsSchema(),
        error_handler = process_form_errors)
    @expose('json')
    def getIndicators(self, host, graph, nocache=None):
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
        host = validators.UnicodeString(not_empty=True)
        nocache = validators.UnicodeString(if_missing=None)

    # @TODO définir un error_handler différent pour remonter l'erreur via JS.
    @validate(
        validators = StartTimeSchema(),
        error_handler = process_form_errors)
    @expose('json')
    def startTime(self, host, nocache=None):
        # urllib2.quote() ne fonctionne pas sur le type unicode.
        # On transcode d'abord le nom d'hôte en UTF-8.
        quote_host = isinstance(host, unicode) and \
                        host.encode('utf-8') or host
        return get_through_proxy(
            'vigirrd', host,
            '/starttime?host=%s' % urllib2.quote(quote_host, '')
        )

    class FullHostPageSchema(schema.Schema):
        """Schéma de validation pour la méthode L{fullHostPage}."""
        host = validators.UnicodeString(not_empty=True)
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
        @param duration : plage de temps des données. Parametre optionnel,
            initialisé a 86400 = plage de 1 jour.
        @type duration : C{str}

        @return: page avec les images des graphes et boutons de deplacement
            dans le temps
        @rtype: page html
        """
        if start is None:
            start = int(time.time()) - int(duration)
        else:
            start = int(start)
        duration = int(duration)

        user = get_current_user()
        if user is None:
            return dict(host=host, start=start, duration=duration,
                        presets=self.presets, graphs=[])

        # Vérification des permissions de l'utilisateur sur l'hôte.
        if not config.is_manager.is_met(request.environ):
            # Récupération des groupes auxquels l'utilisateur a accès.
            supitemgroups = [sig[0] for sig in user.supitemgroups() if sig[1]]

            # On vérifie que l'hôte en question existe bel et bien.
            host_obj = Host.by_host_name(host)
            if not host_obj:
                message = _('No such host "%s"') % host
                LOGGER.warning(message)
                raise http_exc.HTTPNotFound(message)

            # Récupération des groupes dont l'hôte fait partie
            hostgroups = [g.idgroup for g in host_obj.groups]
            # Si aucun des groupes de l'hôte ne fait partie des groupes
            # auxquels l'utilisateur a accès, on affiche une erreur 403.
            if len(set(hostgroups).intersection(set(supitemgroups))) < 1:
                message = _('Access denied to host "%s"') % host
                LOGGER.warning(message)
                raise http_exc.HTTPForbidden(message)

        # Récupération de la liste des noms des graphes associés à l'hôte.
        graphs = DBSession.query(
                Graph.name
            ).distinct(
            ).join(
                (GRAPH_PERFDATASOURCE_TABLE,
                    GRAPH_PERFDATASOURCE_TABLE.c.idgraph == Graph.idgraph),
                (PerfDataSource, PerfDataSource.idperfdatasource ==
                    GRAPH_PERFDATASOURCE_TABLE.c.idperfdatasource),
                (Host, Host.idhost == PerfDataSource.idhost),
            ).filter(Host.name == host)

        graphs = graphs.all()
        return dict(host=host, start=start, duration=duration,
                    presets=self.presets, graphs=graphs)


    class SearchHostSchema(schema.Schema):
        """Schéma de validation pour la méthode L{getIndicators}."""
        allow_extra_fields = True
        filter_extra_fields = True
        query = validators.UnicodeString(not_empty=True)

    @expose('searchhost.html')
    @validate(
        validators = SearchHostSchema(),
        error_handler = process_form_errors)
    @paginate('hosts', items_per_page=10)
    def searchHost(self, query):
        """
        Affiche les résultats de la recherche par nom d'hôte.
        La requête de recherche (C{query}) correspond à un préfixe
        qui sera recherché dans le nom d'hôte. Ce préfixe peut
        contenir les caractères '*' et '?' qui agissent comme des
        "jokers".

        @keyword query: Prefixe de recherche sur les noms d'hôtes
        @type    query: C{unicode}
        """
        if not query:
            redirect("searchHostForm")
            return

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
            ).order_by(Host.name.asc(),)

        # Les managers ont accès à tout.
        # Les autres ont un accès restreint.
        if not config.is_manager.is_met(request.environ):
            supitemgroups = [sig[0] for sig in user.supitemgroups() if sig[1]]
            hosts = hosts.join(
                    (GroupHierarchy, GroupHierarchy.idchild == \
                        SUPITEM_GROUP_TABLE.c.idgroup)
                ).filter(GroupHierarchy.idparent.in_(supitemgroups))

        return dict(hosts=[h.name for h in hosts])

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
    def hosttree(self, parent_id=None, onlytype="", offset=0, noCache=None):
        """
        Affiche un étage de l'arbre de
        sélection des hôtes et groupes d'hôtes.

        @param parent_id: identifiant du groupe d'hôte parent
        @type  parent_id: C{int} or None
        """

        # Si l'identifiant du groupe parent n'est pas
        # spécifié, on retourne la liste des groupes racines,
        # fournie par la méthode get_root_hosts_groups.
        if parent_id is None:
            return self.get_root_host_groups()

        # TODO: Utiliser un schéma de validation
        parent_id = int(parent_id)
        offset = int(offset)

        # On vérifie si le groupe parent fait partie des
        # groupes auxquel l'utilisateur a accès, et on
        # retourne une liste vide dans le cas contraire
        is_manager = config.is_manager.is_met(request.environ)
        if not is_manager:
            direct_access = False
            user = get_current_user()

            # On calcule la distance de ce groupe par rapport aux groupes
            # sur lesquels l'utilisateur a explicitement les permissions.
            #
            # La distance est définie ainsi :
            # 0 : l'utilisateur a des droits explicites sur ce groupe.
            # > 0 : l'utilisateur a accès implicitement au groupe.
            # < 0 : l'utilisateur n'a pas d'accès (il peut juste parcourir
            #       ce groupe)
            #
            # Il faut 2 étapes pour trouver la distance. La 1ère essaye
            # de trouver une distance >= 0, la 2ème une distance <= 0.

            # Distance positive.
            distance = DBSession.query(
                    functions.max(GroupHierarchy.hops)
                ).join(
                    (Group, Group.idgroup == GroupHierarchy.idparent),
                    (DataPermission,
                        DataPermission.idgroup == Group.idgroup),
                    (UserGroup,
                        UserGroup.idgroup == DataPermission.idusergroup),
                    (USER_GROUP_TABLE, USER_GROUP_TABLE.c.idgroup == \
                        UserGroup.idgroup),
                ).filter(USER_GROUP_TABLE.c.username == user.user_name
                ).filter(Group.grouptype == u'supitemgroup'
                ).filter(GroupHierarchy.idchild == parent_id
                ).scalar()

            if distance is None:
                # Distance négative.
                distance = DBSession.query(
                        functions.max(GroupHierarchy.hops)
                    ).join(
                        (Group, Group.idgroup == GroupHierarchy.idchild),
                        (DataPermission,
                            DataPermission.idgroup == Group.idgroup),
                        (UserGroup,
                            UserGroup.idgroup == DataPermission.idusergroup),
                        (USER_GROUP_TABLE, USER_GROUP_TABLE.c.idgroup == \
                            UserGroup.idgroup),
                    ).filter(USER_GROUP_TABLE.c.username == user.user_name
                    ).filter(Group.grouptype == u'supitemgroup'
                    ).filter(GroupHierarchy.idparent == parent_id
                    ).scalar()
                if distance is not None:
                    distance = -distance

            if distance is None:
                # Pas d'accès à ce groupe.
                return dict(groups = [], items = [])

            direct_access = distance >= 0

        limit = int(config.get("max_menu_entries", 20))
        result = {"groups": [], "items": []}

        if not onlytype or onlytype == "group":
            # On récupère la liste des groupes dont
            # l'identifiant du parent est passé en paramètre
            gh1 = aliased(GroupHierarchy, name='gh1')
            gh2 = aliased(GroupHierarchy, name='gh2')

            db_groups = DBSession.query(
                SupItemGroup
            ).options(lazyload('_path_obj')
            ).distinct(
            ).join(
                (gh1, gh1.idchild == SupItemGroup.idgroup),
            ).filter(gh1.hops == 1
            ).filter(gh1.idparent == parent_id
            ).order_by(SupItemGroup.name.asc())

            if not is_manager and not direct_access:
                # On ne doit afficher que les fils du groupe <parent_id>
                # tels que l'utilisateur a accès explicitement à l'un
                # des fils de l'un de ces groupes.
                db_groups = db_groups.join(
                        (gh2, gh2.idparent == gh1.idchild),
                        (DataPermission,
                            DataPermission.idgroup == gh2.idchild),
                        (UserGroup,
                            UserGroup.idgroup == DataPermission.idusergroup),
                        (USER_GROUP_TABLE,
                            USER_GROUP_TABLE.c.idgroup == UserGroup.idgroup),
                    ).filter(USER_GROUP_TABLE.c.username == user.user_name)

            num_children_left = db_groups.count() - offset
            if offset:
                result["continued_from"] = offset
                result["continued_type"] = "group"
            all_groups = db_groups.limit(limit).offset(offset).all()
            for group in all_groups:
                result["groups"].append({
                    'id'   : group.idgroup,
                    'name' : group.name,
                    'type' : "group",
                })
            if num_children_left > limit:
                result["groups"].append({
                    'name': _("Next %(limit)s") % {"limit": limit},
                    'offset': offset + limit,
                    'parent_id': parent_id,
                    'type': 'continued',
                    'for_type': 'group',
                })

        # On récupère la liste des hôtes appartenant au
        # groupe dont l'identifiant est passé en paramètre
        if ((not onlytype or onlytype == "item")
                and (is_manager or direct_access)):
            db_hosts = DBSession.query(
                Host.idhost,
                Host.name,
            ).join(
                (SUPITEM_GROUP_TABLE,
                    SUPITEM_GROUP_TABLE.c.idsupitem == Host.idhost
                    ),
            ).filter(SUPITEM_GROUP_TABLE.c.idgroup == parent_id
            ).order_by(Host.name.asc())
            num_children_left = db_hosts.count() - offset
            if offset:
                result["continued_from"] = offset
                result["continued_type"] = "item"
            all_hosts = db_hosts.limit(limit).offset(offset).all()
            for host in all_hosts:
                result["items"].append({
                    'id'   : host.idhost,
                    'name' : host.name,
                    'type' : "item",
                })
            if num_children_left > limit:
                result["items"].append({
                    'name': _("Next %(limit)s") % {"limit": limit},
                    'offset': offset + limit,
                    'parent_id': parent_id,
                    'type': 'continued',
                    'for_type': 'item',
                })

        return result

    @expose('json')
    def graphtree(self, host_id=None, parent_id=None, offset=0, noCache=None):
        """
        Affiche un étage de l'arbre de sélection
        des graphes et groupes de graphes.

        @param parent_id: identifiant du groupe de graphes parent
        @type  parent_id: C{int} or None
        """

        # Si l'identifiant de l'hôte n'est pas spécifié, on
        # retourne un dictionnaire contenant deux listes vides
        if host_id is None:
            return dict(groups = [], graphs=[])

        # On vérifie les permissions sur l'hôte
        # TODO: Utiliser un schéma de validation
        host_id = int(host_id)
        host = DBSession.query(Host
            ).filter(Host.idhost == host_id
            ).first()
        if host is None:
            return dict(groups = [], graphs=[])
        user = get_current_user()
        if not host.is_allowed_for(user):
            return dict(groups = [], graphs=[])

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
            (SUPITEM_GROUP_TABLE, \
                SUPITEM_GROUP_TABLE.c.idsupitem == PerfDataSource.idhost),
        ).filter(PerfDataSource.idhost == host_id
        ).order_by(GraphGroup.name.asc()
        ).all()

        # Si l'identifiant du groupe parent n'est pas spécifié,
        # on récupère la liste des groupes de graphes racines.
        if parent_id is None:
            graph_groups = GraphGroup.get_top_groups()

        # Sinon on récupère la liste des graphes dont le
        # groupe passé en paramètre est le parent direct
        else:
            # TODO: Utiliser un schéma de validation
            parent_id = int(parent_id)
            graph_groups = DBSession.query(
                GraphGroup
            ).join(
                (GroupHierarchy, GroupHierarchy.idchild == \
                    GraphGroup.idgroup),
            ).filter(GroupHierarchy.hops == 1
            ).filter(GroupHierarchy.idparent == parent_id
            ).order_by(GraphGroup.name.asc()
            ).all()

        # On réalise l'intersection des deux listes
        groups = []
        for gg in graph_groups:
            if gg in host_graph_groups:
                groups.append({
                    'id'   : gg.idgroup,
                    'name' : gg.name,
                    'type' : "group",
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
                    'type' : "item",
                })

        return dict(groups=groups, items=graphs)

    def get_root_host_groups(self):
        """
        Retourne tous les groupes racines (c'est à dire n'ayant
        aucun parent) d'hôtes auquel l'utilisateur a accès.

        @return: Un dictionnaire contenant la liste de ces groupes.
        @rtype : C{dict} of C{list} of C{dict} of C{mixed}
        """

        # On récupère tous les groupes qui ont un parent.
        children = DBSession.query(
            SupItemGroup,
        ).distinct(
        ).join(
            (GroupHierarchy, GroupHierarchy.idchild == SupItemGroup.idgroup)
        ).filter(GroupHierarchy.hops > 0)

        # Ensuite on les exclut de la liste des groupes,
        # pour ne garder que ceux qui sont au sommet de
        # l'arbre et qui constituent nos "root groups".
        root_groups = DBSession.query(
            SupItemGroup,
        ).except_(children
        ).order_by(SupItemGroup.name)

        # On filtre ces groupes racines afin de ne
        # retourner que ceux auquels l'utilisateur a accès
        user = get_current_user()
        if not config.is_manager.is_met(request.environ):
            user_groups = [ug[0] for ug in user.supitemgroups()]
            root_groups = root_groups.filter(
                SupItemGroup.idgroup.in_(user_groups))

        groups = []
        for group in root_groups.all():
            groups.append({
                'id'   : group.idgroup,
                'name' : group.name,
                'type' : "group",
            })

        return dict(groups=groups, items=[])

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

    @expose('json')
    def external_links(self):
        return dict(links=config['external_links'])
