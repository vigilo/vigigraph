# -*- coding: utf-8 -*-
"""
Suite de tests du formulaire de sélection des hôtes et groupes d'hôtes.
"""
from nose.tools import assert_equal
import transaction

from vigigraph.tests import TestController
from vigilo.models.session import DBSession
from vigilo.models.tables import Host, \
    Graph, GraphGroup, Permission
from vigilo.models.demo.functions import add_supitemgroup, \
    add_host, add_host2group, add_usergroup, add_user, \
    add_supitemgrouppermission, add_usergroup_permission, \
    add_graph, add_graphgroup, add_graph2group, \
    add_perfdatasource, add_perfdatasource2graph, \
    add_vigiloserver, add_application


class TestHostSelectionForm(TestController):
    """
    Teste le formulaire de sélection des
    hôtes et groupes d'hôtes de Vigigraph.
    """

    def setUp(self):
        """Préparation de la base de données de tests."""

        # Initialisation de la base
        super(TestHostSelectionForm, self).setUp()

        # Ajout d'un serveur de supervision
        vigiloserver = add_vigiloserver(u'locahost')

        # Ajout d'une application 'vigirrd'
        add_application(u"vigirrd")

        # Ajout d'un groupe d'hôtes principal
        mainhostgroup = add_supitemgroup(u'mhg', None)

        # Ajout d'un premier groupe d'hôtes de second niveau
        hostgroup1 = add_supitemgroup(u'hg1', mainhostgroup)

        # Ajout d'un second groupe d'hôtes de second niveau
        hostgroup2 = add_supitemgroup(u'hg2', mainhostgroup)

        # Ajout de trois hôtes
        host1 = add_host(u'host1')
        host2 = add_host(u'host2')
        host3 = add_host(u'host3')

        # Ajout du premier hôte dans le groupe d'hôtes principal.
        add_host2group(host1, mainhostgroup)
        # Ajout du deuxième hôte dans le premier
        # groupe d'hôtes de second niveau.
        add_host2group(host2, hostgroup1)
        # Ajout du troisième hôte dans le second
        # groupe d'hôtes de second niveau.
        add_host2group(host3, hostgroup2)

        # Ajout de trois graphes
        graph1 = add_graph("graph1")
        graph2 = add_graph("graph2")
        graph3 = add_graph("graph3")

        # Ajout d'une perfdatasource pour chaque hôte
        datasource1 = add_perfdatasource(
            u'load', host1, None, None, vigiloserver)
        datasource2 = add_perfdatasource(
            u'load', host2, None, None, vigiloserver)
        datasource3 = add_perfdatasource(
            u'load', host3, None, None, vigiloserver)

        # Ajout d'une perfdatsource à chaque graphe
        add_perfdatasource2graph(datasource1, graph1)
        add_perfdatasource2graph(datasource2, graph2)
        add_perfdatasource2graph(datasource3, graph3)

        # Ajout de trois groupes de graphes
        graphgroup1 = add_graphgroup("graphgroup1")
        graphgroup2 = add_graphgroup("graphgroup2")
        graphgroup3 = add_graphgroup("graphgroup3")

        # Ajout de chaque graphe à un groupe de graphes
        add_graph2group(graph1, graphgroup1)
        add_graph2group(graph2, graphgroup2)
        add_graph2group(graph3, graphgroup3)

        # Ajout de trois groupes d'utilisateurs
        poweruser_group = add_usergroup(u'powerusers')
        user_group = add_usergroup(u'users')
        visitor_group = add_usergroup(u'visitor')

        # Ajout de trois utilisateurs
        add_user(u'poweruser', u'some.power@us.er',
            u'Power User', u'poweruserpass', u'powerusers')
        add_user(u'user', u'some.random@us.er',
            u'User', u'userpass', u'users')
        add_user(u'visitor', u'some.visiting@us.er',
            u'', u'visitorpass', u'visitor')

        # Ajout des permissions sur le groupe d'hôtes
        # principal pour le premier groupe d'utilisateurs
        add_supitemgrouppermission(mainhostgroup, poweruser_group)

        # Ajout des permissions sur le premier groupe d'hôtes
        # secondaire pour le second groupe d'utilisateurs
        add_supitemgrouppermission(hostgroup1, user_group)

        # Ajout de la permission 'vigigraph-access' aux groupes d'utilisateurs
        perm = Permission.by_permission_name(u'vigigraph-access')
        add_usergroup_permission(poweruser_group, perm)
        add_usergroup_permission(user_group, perm)
        add_usergroup_permission(visitor_group, perm)

        # Validation des ajouts dans la base
        DBSession.flush()
        transaction.commit()

##### Quatrième onglet déroulant du formulaire #####

    def test_get_graph_groups_when_allowed(self):
        """
        Récupération des groupes de graphes avec les bons droits
        """

        # Récupération de l'hôte 'host1' dans la base de données
        host1 = DBSession.query(Host).filter(
            Host.name == u'host1').first()

        # Récupération de l'hôte 'host2' dans la base de données
        host2 = DBSession.query(Host).filter(
            Host.name == u'host2').first()

        # Récupération de l'hôte 'host3' dans la base de données
        host3 = DBSession.query(Host).filter(
            Host.name == u'host3').first()

        # Récupération du groupe de graphes
        # 'graphgroup1' dans la base de données
        graphgroup1 = DBSession.query(GraphGroup).filter(
            GraphGroup.name == u'graphgroup1').first()

        # Récupération du groupe de graphes
        # 'graphgroup2' dans la base de données
        graphgroup2 = DBSession.query(GraphGroup).filter(
            GraphGroup.name == u'graphgroup2').first()

        # Récupération du groupe de graphes
        # 'graphgroup3' dans la base de données
        graphgroup3 = DBSession.query(GraphGroup).filter(
            GraphGroup.name == u'graphgroup3').first()

        # Récupération des groupes de graphes de l'hôte
        # host1 accessibles à l'utilisateur 'poweruser'
        response = self.app.post(
        '/rpc/graphgroups?idhost=%s' % (host1.idhost, ), {
            }, extra_environ={'REMOTE_USER': 'poweruser'})
        json = response.json

        # On s'assure que la liste de groupes
        # de graphes retournée contient bien 'graphgroup1'
        assert_equal(
            json, {"items": [
                [graphgroup1.name, unicode(graphgroup1.idgroup)]
            ]}
        )

        # Récupération des groupes de graphes de l'hôte
        # host2 accessibles à l'utilisateur 'poweruser'
        response = self.app.post(
        '/rpc/graphgroups?idhost=%s' % (host2.idhost, ), {
            }, extra_environ={'REMOTE_USER': 'poweruser'})
        json = response.json

        # On s'assure que la liste de groupes
        # de graphes retournée contient bien 'graphgroup2'
        assert_equal(
            json, {"items": [
                [graphgroup2.name, unicode(graphgroup2.idgroup)]
            ]}
        )

        # Récupération des groupes de graphes de l'hôte
        # host2 accessibles à l'utilisateur 'user'
        response = self.app.post(
        '/rpc/graphgroups?idhost=%s' % (host2.idhost, ), {
            }, extra_environ={'REMOTE_USER': 'user'})
        json = response.json

        # On s'assure que la liste de groupes
        # de graphes retournée contient bien 'graphgroup2'
        assert_equal(
            json, {"items": [
                [graphgroup2.name, unicode(graphgroup2.idgroup)]
            ]}
        )

        # Récupération des groupes de graphes de l'hôte
        # host3 accessibles à l'utilisateur 'poweruser'
        response = self.app.post(
        '/rpc/graphgroups?idhost=%s' % (host3.idhost, ), {
            }, extra_environ={'REMOTE_USER': 'poweruser'})
        json = response.json

        # On s'assure que la liste de groupes
        # de graphes retournée contient bien 'graphgroup3'
        assert_equal(
            json, {"items": [
                [graphgroup3.name, unicode(graphgroup3.idgroup)]
            ]}
        )
    def test_get_graph_groups_when_not_allowed(self):
        """
        Récupération des groupes de graphes sans les bons droits
        """

        # Récupération de l'hôte 'host1' dans la base de données
        host1 = DBSession.query(Host).filter(
            Host.name == u'host1').first()

        # Récupération de l'hôte 'host3' dans la base de données
        host3 = DBSession.query(Host).filter(
            Host.name == u'host3').first()

        # Récupération des groupes de graphes de l'hôte
        # host1 accessibles à l'utilisateur 'user'
        response = self.app.post(
        '/rpc/graphgroups?idhost=%s' % (host1.idhost, ), {
            }, extra_environ={'REMOTE_USER': 'user'})
        json = response.json

        # On s'assure que la liste de groupes
        # de graphes retournée est vide
        assert_equal(
            json, {"items": []}
        )

        # Récupération des groupes de graphes de l'hôte
        # host3 accessibles à l'utilisateur 'user'
        response = self.app.post(
        '/rpc/graphgroups?idhost=%s' % (host3.idhost, ), {
            }, extra_environ={'REMOTE_USER': 'user'})
        json = response.json

        # On s'assure que la liste de groupes
        # de graphes retournée est vide
        assert_equal(
            json, {"items": []}
        )

        # Récupération des groupes de graphes de l'hôte
        # host1 accessibles à l'utilisateur 'visitor'
        response = self.app.post(
        '/rpc/graphgroups?idhost=%s' % (host1.idhost, ), {
            }, extra_environ={'REMOTE_USER': 'visitor'})
        json = response.json

        # On s'assure que la liste de groupes
        # de graphes retournée est vide
        assert_equal(
            json, {"items": []}
        )

    def test_get_graph_groups_from_inexisting_host(self):
        """
        Récupération des groupes de graphes d'un hôte inexistant
        """

        # Récupération des groupes d'hôtes accessibles à l'utilisateur
        # 'visitor' et appartenant à un groupe principal inexistant
        response = self.app.post(
            '/rpc/graphgroups?idhost=6666666', {
            }, extra_environ={'REMOTE_USER': 'visitor'})
        json = response.json

        # On s'assure que la liste de groupes
        # de graphes retournée est vide
        assert_equal(
            json, {"items": []}
        )

##### Cinquième onglet déroulant du formulaire #####

    def test_get_graphs_when_allowed(self):
        """
        Récupération des graphes avec les bons droits
        """

        # Récupération de l'hôte 'host1' dans la base de données
        host1 = DBSession.query(Host).filter(
            Host.name == u'host1').first()

        # Récupération de l'hôte 'host2' dans la base de données
        host2 = DBSession.query(Host).filter(
            Host.name == u'host2').first()

        # Récupération de l'hôte 'host3' dans la base de données
        host3 = DBSession.query(Host).filter(
            Host.name == u'host3').first()

        # Récupération du groupe de graphes
        # 'graphgroup1' dans la base de données
        graphgroup1 = DBSession.query(GraphGroup).filter(
            GraphGroup.name == u'graphgroup1').first()

        # Récupération du groupe de graphes
        # 'graphgroup2' dans la base de données
        graphgroup2 = DBSession.query(GraphGroup).filter(
            GraphGroup.name == u'graphgroup2').first()

        # Récupération du groupe de graphes
        # 'graphgroup3' dans la base de données
        graphgroup3 = DBSession.query(GraphGroup).filter(
            GraphGroup.name == u'graphgroup3').first()

        # Récupération du graphe 'graph1'
        # dans la base de données
        graph1 = DBSession.query(Graph).filter(
            Graph.name == u'graph1').first()

        # Récupération du graphe 'graph2'
        # dans la base de données
        graph2 = DBSession.query(Graph).filter(
            Graph.name == u'graph2').first()

        # Récupération du graphe 'graph3'
        # dans la base de données
        graph3 = DBSession.query(Graph).filter(
            Graph.name == u'graph3').first()

        # Récupération des graphes du groupe de graphes
        # 'graphgroup1' accessibles à l'utilisateur 'poweruser'
        response = self.app.post(
        '/rpc/graphs?idgraphgroup=%s&idhost=%s' %
            (graphgroup1.idgroup, host1.idhost), {},
            extra_environ={'REMOTE_USER': 'poweruser'})
        json = response.json

        # On s'assure que la liste de
        # graphes retournée contient 'graph1'
        assert_equal(
            json, {"items": [
                [graph1.name, unicode(graph1.idgraph)]
            ]}
        )

        # Récupération des graphes du groupe de graphes
        # 'graphgroup2' accessibles à l'utilisateur 'poweruser'
        response = self.app.post(
        '/rpc/graphs?idgraphgroup=%s&idhost=%s' %
            (graphgroup2.idgroup, host2.idhost), {},
            extra_environ={'REMOTE_USER': 'poweruser'})
        json = response.json

        # On s'assure que la liste de
        # graphes retournée contient 'graph2'
        assert_equal(
            json, {"items": [
                [graph2.name, unicode(graph2.idgraph)]
            ]}
        )

        # Récupération des graphes du groupe de graphes
        # 'graphgroup2' accessibles à l'utilisateur 'user'
        response = self.app.post(
        '/rpc/graphs?idgraphgroup=%s&idhost=%s' %
            (graphgroup2.idgroup, host2.idhost), {},
            extra_environ={'REMOTE_USER': 'user'})
        json = response.json

        # On s'assure que la liste de
        # graphes retournée contient 'graph2'
        assert_equal(
            json, {"items": [
                [graph2.name, unicode(graph2.idgraph)]
            ]}
        )

        # Récupération des graphes du groupe de graphes
        # 'graphgroup3' accessibles à l'utilisateur 'poweruser'
        response = self.app.post(
        '/rpc/graphs?idgraphgroup=%s&idhost=%s' %
            (graphgroup3.idgroup, host3.idhost), {},
            extra_environ={'REMOTE_USER': 'poweruser'})
        json = response.json

        # On s'assure que la liste de
        # graphes retournée contient 'graph3'
        assert_equal(
            json, {"items": [
                [graph3.name, unicode(graph3.idgraph)]
            ]}
        )

    def test_get_graphs_when_not_allowed(self):
        """
        Récupération des graphes sans les bons droits
        """

        # Récupération de l'hôte 'host1' dans la base de données
        host1 = DBSession.query(Host).filter(
            Host.name == u'host1').first()

        # Récupération de l'hôte 'host3' dans la base de données
        host3 = DBSession.query(Host).filter(
            Host.name == u'host3').first()

        # Récupération du groupe de graphes
        # 'graphgroup1' dans la base de données
        graphgroup1 = DBSession.query(GraphGroup).filter(
            GraphGroup.name == u'graphgroup1').first()

        # Récupération du groupe de graphes
        # 'graphgroup3' dans la base de données
        graphgroup3 = DBSession.query(GraphGroup).filter(
            GraphGroup.name == u'graphgroup3').first()

        # Récupération des graphes du groupe de graphes
        # graphgroup1 accessibles à l'utilisateur 'user'
        response = self.app.post(
        '/rpc/graphs?idgraphgroup=%s&idhost=%s' %
            (graphgroup1.idgroup, host1.idhost), {},
            extra_environ={'REMOTE_USER': 'user'})
        json = response.json

        # On s'assure que la liste de groupes
        # de graphes retournée est vide
        assert_equal(
            json, {"items": []}
        )

        # Récupération des graphes du groupe de graphes
        # 'graphgroup1' accessibles à l'utilisateur 'visitor'
        response = self.app.post(
        '/rpc/graphs?idgraphgroup=%s&idhost=%s' %
            (graphgroup1.idgroup, host1.idhost), {},
            extra_environ={'REMOTE_USER': 'visitor'})
        json = response.json

        # On s'assure que la liste de groupes
        # de graphes retournée est vide
        assert_equal(
            json, {"items": []}
        )

        # Récupération des graphes du groupe de graphes
        # 'graphgroup3' accessibles à l'utilisateur 'user'
        response = self.app.post(
        '/rpc/graphs?idgraphgroup=%s&idhost=%s' %
            (graphgroup3.idgroup, host3.idhost), {},
            extra_environ={'REMOTE_USER': 'user'})
        json = response.json

        # On s'assure que la liste de groupes
        # de graphes retournée est vide
        assert_equal(
            json, {"items": []}
        )

    def test_get_graphs_from_inexisting_graph_group(self):
        """
        Récupération des graphes d'un groupe de graphes inexistant
        """

        # Récupération des graphes accessibles à l'utilisateur
        # 'visitor' et appartenant à un groupe inexistant
        response = self.app.post(
            '/rpc/graphs?idgraphgroup=6666666&idhost=6666666', {
            }, extra_environ={'REMOTE_USER': 'visitor'})
        json = response.json

        # On s'assure que la liste de
        # graphes retournée est vide
        assert_equal(
            json, {"items": []}
        )


