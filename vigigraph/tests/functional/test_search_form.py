# -*- coding: utf-8 -*-
"""
Suite de tests du formulaire de recherche de VigiGraph.
"""
import transaction

from vigigraph.tests import TestController
from vigilo.models.session import DBSession
from vigilo.models.tables import Host, SupItemGroup, Graph, GraphGroup

from vigigraph.tests.functional.test_host_selection_form import populateDB
from vigigraph.tests.functional.test_graph_selection_form import addGraphs


class TestSearchForm(TestController):
    """
    Teste le formulaire de recherche des
    hôtes et des graphes de Vigigraph.
    """

    def setUp(self):
        """Préparation de la base de données de tests."""

        # Initialisation de la base
        super(TestSearchForm, self).setUp()

        # Ajout de données de tests dans la base
        (host1, host2, host3) = populateDB()

        # Ajout de graphes dans la base
        addGraphs(host1, host2, host3)

        # Validation des ajouts dans la base
        DBSession.flush()
        transaction.commit()

    def test_select_host_when_allowed(self):
        """
        Résultats de la recherche sur un hôte avec les bons droits
        """

        # Récupération du groupe d'hôtes 'mhg' dans la base de données
        mainhostgroup = DBSession.query(SupItemGroup).filter(
            SupItemGroup.name == u'mhg').first()

        # Récupération du groupe d'hôtes 'hg1' dans la base de données
        hostgroup1 = DBSession.query(SupItemGroup).filter(
            SupItemGroup.name == u'hg1').first()

        # Récupération de l'hôte 'host1' dans la base de données
        host1 = DBSession.query(Host).filter(
            Host.name == u'host1').first()

        # Récupération de l'hôte 'host2' dans la base de données
        host2 = DBSession.query(Host).filter(
            Host.name == u'host2').first()

        # Récupération des résultats transmis au
        # formulaire de sélection après une recherche sur
        # l'hôte 'host1' pour l'utilisateur 'manager'
        response = self.app.post(
        '/rpc/selectHostAndGraph?host=%s' % (str(host1.name), ), {
            }, extra_environ={'REMOTE_USER': 'manager'})
        json = response.json

        # On s'assure que la liste retournée
        # contient bien 'mhg' et 'No subgroup'
        self.assertEqual(
            json, {"items": [
                [mainhostgroup.name, u'No subgroup'],
                []
            ]}
        )

        # Récupération des résultats transmis au
        # formulaire de sélection après une recherche sur
        # l'hôte 'host1' pour l'utilisateur 'poweruser'
        response = self.app.post(
        '/rpc/selectHostAndGraph?host=%s' % (str(host1.name), ), {
            }, extra_environ={'REMOTE_USER': 'poweruser'})
        json = response.json

        # On s'assure que la liste retournée
        # contient bien 'mhg' et 'No subgroup'
        self.assertEqual(
            json, {"items": [
                [mainhostgroup.name, u'No subgroup'],
                []
            ]}
        )

        # Récupération des résultats transmis au
        # formulaire de sélection après une recherche sur
        # l'hôte 'host2' pour l'utilisateur 'poweruser'
        response = self.app.post(
        '/rpc/selectHostAndGraph?host=%s' % (str(host2.name), ), {
            }, extra_environ={'REMOTE_USER': 'poweruser'})
        json = response.json

        # On s'assure que la liste retournée
        # contient bien 'mhg' et 'hostgroup1'
        self.assertEqual(
            json, {"items": [
                [mainhostgroup.name, hostgroup1.name],
                []
            ]}
        )

        # Récupération des résultats transmis au
        # formulaire de sélection après une recherche sur
        # l'hôte 'host2' pour l'utilisateur 'user'
        response = self.app.post(
        '/rpc/selectHostAndGraph?host=%s' % (str(host2.name), ), {
            }, extra_environ={'REMOTE_USER': 'user'})
        json = response.json

        # On s'assure que la liste retournée
        # contient bien 'mhg' et 'hostgroup1'
        self.assertEqual(
            json, {"items": [
                [mainhostgroup.name, hostgroup1.name],
                []
            ]}
        )

    def test_select_host_when_not_allowed(self):
        """
        Résultats de la recherche sur un hôte sans les droits
        """

        # Récupération de l'hôte 'host1' dans la base de données
        host1 = DBSession.query(Host).filter(
            Host.name == u'host1').first()

        # Récupération de l'hôte 'host3' dans la base de données
        host3 = DBSession.query(Host).filter(
            Host.name == u'host3').first()

        # Récupération des résultats transmis au
        # formulaire de sélection après une recherche sur
        # l'hôte 'host1' pour l'utilisateur 'user'
        response = self.app.post(
        '/rpc/selectHostAndGraph?host=%s' % (str(host1.name), ), {
            }, extra_environ={'REMOTE_USER': 'user'})
        json = response.json

        # On s'assure que la liste
        # retournée est vide
        self.assertEqual(
            json, {"items": [
                [],[]
            ]}
        )

        # Récupération des résultats transmis au
        # formulaire de sélection après une recherche sur
        # l'hôte 'host3' pour l'utilisateur 'user'
        response = self.app.post(
        '/rpc/selectHostAndGraph?host=%s' % (str(host3.name), ), {
            }, extra_environ={'REMOTE_USER': 'user'})
        json = response.json

        # On s'assure que la liste
        # retournée est vide
        self.assertEqual(
            json, {"items": [
                [],[]
            ]}
        )

        # Récupération des résultats transmis au
        # formulaire de sélection après une recherche sur
        # l'hôte 'host1' pour l'utilisateur 'visitor'
        response = self.app.post(
        '/rpc/selectHostAndGraph?host=%s' % (str(host1.name), ), {
            }, extra_environ={'REMOTE_USER': 'visitor'})
        json = response.json

        # On s'assure que la liste
        # retournée est vide
        self.assertEqual(
            json, {"items": [
                [],[]
            ]}
        )

        # Récupération des résultats transmis au
        # formulaire de sélection après une recherche sur
        # l'hôte 'host3' pour l'utilisateur 'visitor'
        response = self.app.post(
        '/rpc/selectHostAndGraph?host=%s' % (str(host3.name), ), {
            }, extra_environ={'REMOTE_USER': 'visitor'})
        json = response.json

        # On s'assure que la liste
        # retournée est vide
        self.assertEqual(
            json, {"items": [
                [],[]
            ]}
        )

    def test_select_host_as_anonymous(self):
        """
        Résultats de la recherche sur un hôte en tant qu'anonyme
        """

        # Récupération de l'hôte 'host1' dans la base de données
        host1 = DBSession.query(Host).filter(
            Host.name == u'host1').first()

        # Récupération des résultats transmis au
        # formulaire de sélection après une recherche sur
        # l'hôte 'host1' pour un utilisateur anonyme :
        # le contrôleur doit retourner une erreur 401.
        self.app.post(
            '/rpc/selectHostAndGraph?host=%s' % (str(host1.name), ), {
            }, status=401)

    def test_select_inexisting_host(self):
        """
        Résultats de la recherche sur un hôte inexistant
        """

        # Récupération des résultats transmis au
        # formulaire de sélection après une recherche sur
        # un hôte inexistant pour l'utilisateur 'manager'
        response = self.app.post(
        '/rpc/selectHostAndGraph?host=hote_totalement_inexistant', {
            }, extra_environ={'REMOTE_USER': 'manager'})
        json = response.json

        # On s'assure que la liste
        # retournée est vide
        self.assertEqual(
            json, {"items": [
                [], []
            ]}
        )

    def test_select_graph_without_a_host(self):
        """
        Résultats de la recherche sur un graphe sans préciser d'hôte
        """

        # Récupération du graphe 'graph1' dans la base de données
        graph1 = DBSession.query(Graph).filter(
            Graph.name == u'graph1').first()

        # On s'assure qu'une erreur 412 est retournée lorsque
        # l'on recherche un graphe sans préciser d'hôte.
        self.app.post(
        '/rpc/selectHostAndGraph?graph=%s' % (str(graph1.name), ), {
            }, extra_environ={'REMOTE_USER': 'manager'}, status=412)

    def test_select_graph_with_an_erroneous_host(self):
        """
        Résultats de la recherche sur un graphe en précisant un hôte erroné
        """

        # Récupération du graphe 'graph1' dans la base de données
        graph1 = DBSession.query(Graph).filter(
            Graph.name == u'graph1').first()

        # On s'assure qu'une liste vide est retournée lorsque
        # l'on recherche un graphe en précisant un hôte erroné.
        response = self.app.post(
        '/rpc/selectHostAndGraph?host=%s' % (str(graph1.name), ), {
            }, extra_environ={'REMOTE_USER': 'manager'})
        json = response.json

        self.assertEqual(
            json, {"items": [
                [], []
            ]}
        )

    def test_select_graph_when_allowed(self):
        """
        Résultats de la recherche sur un graphe avec les bons droits
        """

        # Récupération du groupe d'hôtes 'mhg' dans la base de données
        mainhostgroup = DBSession.query(SupItemGroup).filter(
            SupItemGroup.name == u'mhg').first()

        # Récupération du groupe d'hôtes 'hg1' dans la base de données
        hostgroup1 = DBSession.query(SupItemGroup).filter(
            SupItemGroup.name == u'hg1').first()

        # Récupération de l'hôte 'host1' dans la base de données
        host1 = DBSession.query(Host).filter(
            Host.name == u'host1').first()

        # Récupération de l'hôte 'host2' dans la base de données
        host2 = DBSession.query(Host).filter(
            Host.name == u'host2').first()

        # Récupération du groupe de graphes
        # 'graphgroup1' dans la base de données
        graphgroup1 = DBSession.query(GraphGroup).filter(
            GraphGroup.name == u'graphgroup1').first()

        # Récupération du groupe de graphes
        # 'graphgroup2' dans la base de données
        graphgroup2 = DBSession.query(GraphGroup).filter(
            GraphGroup.name == u'graphgroup2').first()

        # Récupération du graphe 'graph1' dans la base de données
        graph1 = DBSession.query(Graph).filter(
            Graph.name == u'graph1').first()

        # Récupération du graphe 'graph2' dans la base de données
        graph2 = DBSession.query(Graph).filter(
            Graph.name == u'graph2').first()

        # Récupération des résultats transmis au
        # formulaire de sélection après une recherche sur
        # le graphe 'graph1' pour l'utilisateur 'manager'
        response = self.app.post(
        '/rpc/selectHostAndGraph?host=%s&graph=%s' %
            (str(host1.name), str(graph1.name)), {
            }, extra_environ={'REMOTE_USER': 'manager'})
        json = response.json

        # On s'assure que la liste retournée
        # est conforme à celle attendue
        self.assertEqual(
            json, {"items": [
                [mainhostgroup.name, u'No subgroup'],
                [graphgroup1.name]
            ]}
        )

        # Récupération des résultats transmis au
        # formulaire de sélection après une recherche sur
        # le graphe 'graph1' pour l'utilisateur 'poweruser'
        response = self.app.post(
        '/rpc/selectHostAndGraph?host=%s&graph=%s' %
            (str(host1.name), str(graph1.name)), {
            }, extra_environ={'REMOTE_USER': 'poweruser'})
        json = response.json

        # On s'assure que la liste retournée
        # est conforme à celle attendue
        self.assertEqual(
            json, {"items": [
                [mainhostgroup.name, u'No subgroup'],
                [graphgroup1.name]
            ]}
        )

        # Récupération des résultats transmis au
        # formulaire de sélection après une recherche sur
        # le graphe 'graph2' pour l'utilisateur 'poweruser'
        response = self.app.post(
        '/rpc/selectHostAndGraph?host=%s&graph=%s' %
            (str(host2.name), str(graph2.name)), {
            }, extra_environ={'REMOTE_USER': 'poweruser'})
        json = response.json

        # On s'assure que la liste retournée
        # est conforme à celle attendue
        self.assertEqual(
            json, {"items": [
                [mainhostgroup.name, hostgroup1.name],
                [graphgroup2.name]
            ]}
        )

        # Récupération des résultats transmis au
        # formulaire de sélection après une recherche sur
        # le graphe 'graph2' pour l'utilisateur 'user'
        response = self.app.post(
        '/rpc/selectHostAndGraph?host=%s&graph=%s' %
            (str(host2.name), str(graph2.name)), {
            }, extra_environ={'REMOTE_USER': 'user'})
        json = response.json

        # On s'assure que la liste retournée
        # est conforme à celle attendue
        self.assertEqual(
            json, {"items": [
                [mainhostgroup.name, hostgroup1.name],
                [graphgroup2.name]
            ]}
        )

    def test_select_graph_when_not_allowed(self):
        """
        Résultats de la recherche sur un graphe sans les droits
        """

        # Récupération de l'hôte 'host1' dans la base de données
        host1 = DBSession.query(Host).filter(
            Host.name == u'host1').first()

        # Récupération de l'hôte 'host3' dans la base de données
        host3 = DBSession.query(Host).filter(
            Host.name == u'host3').first()

        # Récupération du graphe 'graph1' dans la base de données
        graph1 = DBSession.query(Graph).filter(
            Graph.name == u'graph1').first()

        # Récupération du graphe 'graph3' dans la base de données
        graph3 = DBSession.query(Graph).filter(
            Graph.name == u'graph1').first()

        # Récupération des résultats transmis au
        # formulaire de sélection après une recherche sur
        # le graphe 'graph1' pour l'utilisateur 'user'
        response = self.app.post(
        '/rpc/selectHostAndGraph?host=%s&graph=%s' %
            (str(host1.name), str(graph1.name)), {
            }, extra_environ={'REMOTE_USER': 'user'})
        json = response.json

        # On s'assure que la liste
        # retournée est vide
        self.assertEqual(
            json, {"items": [
                [], []
            ]}
        )

        # Récupération des résultats transmis au
        # formulaire de sélection après une recherche sur
        # le graphe 'graph3' pour l'utilisateur 'user'
        response = self.app.post(
        '/rpc/selectHostAndGraph?host=%s&graph=%s' %
            (str(host3.name), str(graph3.name)), {
            }, extra_environ={'REMOTE_USER': 'user'})
        json = response.json

        # On s'assure que la liste
        # retournée est vide
        self.assertEqual(
            json, {"items": [
                [], []
            ]}
        )

        # Récupération des résultats transmis au
        # formulaire de sélection après une recherche sur
        # le graphe 'graph1' pour l'utilisateur 'visitor'
        response = self.app.post(
        '/rpc/selectHostAndGraph?host=%s&graph=%s' %
            (str(host1.name), str(graph1.name)), {
            }, extra_environ={'REMOTE_USER': 'visitor'})
        json = response.json

        # On s'assure que la liste
        # retournée est vide
        self.assertEqual(
            json, {"items": [
                [], []
            ]}
        )

        # Récupération des résultats transmis au
        # formulaire de sélection après une recherche sur
        # le graphe 'graph3' pour l'utilisateur 'visitor'
        response = self.app.post(
        '/rpc/selectHostAndGraph?host=%s&graph=s' %
            (str(host3.name), str(graph3.name)), {
            }, extra_environ={'REMOTE_USER': 'visitor'})
        json = response.json

        # On s'assure que la liste
        # retournée est vide
        self.assertEqual(
            json, {"items": [
                [], []
            ]}
        )

    def test_select_graph_as_anonymous(self):
        """
        Résultats de la recherche sur un graphe en tant qu'anonyme
        """

        # Récupération de l'hôte 'host1' dans la base de données
        host1 = DBSession.query(Host).filter(
            Host.name == u'host1').first()

        # Récupération du graphe 'graph1' dans la base de données
        graph1 = DBSession.query(Graph).filter(
            Graph.name == u'graph1').first()

        # Récupération des résultats transmis au
        # formulaire de sélection après une recherche sur
        # le graphe 'graph1' pour un utilisateur anonyme :
        # le contrôleur doit retourner une erreur 401
        self.app.post(
            '/rpc/selectHostAndGraph?host=%s&graph=%s' %
            (str(host1.name), str(graph1.name)), {
            }, status=401)

    def test_select_inexisting_graph(self):
        """
        Résultats de la recherche sur un graphe inexistant
        """

        # Récupération de l'hôte 'host1' dans la base de données
        host1 = DBSession.query(Host).filter(
            Host.name == u'host1').first()

        # Récupération des résultats transmis au
        # formulaire de sélection après une recherche sur
        # un graphe inexistant pour l'utilisateur 'manager'
        response = self.app.post(
        '/rpc/selectHostAndGraph?host=%sgraph=graphe_totalement_inexistant' %
            (str(host1.name), ), {
            }, extra_environ={'REMOTE_USER': 'manager'})
        json = response.json

        # On s'assure que la liste
        # retournée est vide
        self.assertEqual(
            json, {"items": [
                [], []
            ]}
        )
