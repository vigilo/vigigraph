# -*- coding: utf-8 -*-
# Copyright (C) 2006-2012 CS-SI
# License: GNU GPL v2 <http://www.gnu.org/licenses/gpl-2.0.html>

"""
Suite de tests du formulaire de recherche de VigiGraph.
"""
import transaction, urllib2

from vigigraph.tests import TestController
from vigilo.models.session import DBSession
from vigilo.models.tables import Host, SupItemGroup, Graph, GraphGroup
from vigigraph.tests.functional.helpers import populateDB, addGraphs


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
        DBSession.query(SupItemGroup).filter(
            SupItemGroup.name == u'mhg').first()

        # Récupération du groupe d'hôtes 'hg1' dans la base de données
        DBSession.query(SupItemGroup).filter(
            SupItemGroup.name == u'hg1').first()

        # Récupération de l'hôte 'host1' dans la base de données
        host1 = DBSession.query(Host).filter(
            Host.name == u'host1 éà').first()

        # Récupération de l'hôte 'host2' dans la base de données
        host2 = DBSession.query(Host).filter(
            Host.name == u'host2 éà').first()

        # Récupération des résultats obtenus après une recherche
        # sur l'hôte 'host1' pour l'utilisateur 'manager'
        response = self.app.post(
            '/rpc/searchHostAndGraph?search_form_host=%s' %
                urllib2.quote(host1.name.encode('utf-8'), ''),
            {},
            extra_environ={'REMOTE_USER': 'manager'}
        )
        json = response.json

        # On s'assure que les deux listes retournées contiennent
        # respectivement le nom de l'hôte et son identifiant
        self.assertEqual(
            json, {
                'labels': [[u'host1 éà', None]],
                'ids': [[1, None]],
                'more': False,
            }
        )

        # Récupération des résultats obtenus après une recherche
        # sur l'hôte 'host1' pour l'utilisateur 'poweruser'
        response = self.app.post(
            '/rpc/searchHostAndGraph?search_form_host=%s' %
                urllib2.quote(host1.name.encode('utf-8'), ''),
            {},
            extra_environ={'REMOTE_USER': 'poweruser'}
        )
        json = response.json

        # On s'assure que les deux listes retournées contiennent
        # respectivement le nom de l'hôte et son identifiant
        self.assertEqual(
            json, {
                'labels': [[host1.name, None]],
                'ids': [[host1.idhost, None]],
                'more': False,
            }
        )

        # Récupération des résultats obtenus après une recherche
        # sur l'hôte 'host2' pour l'utilisateur 'poweruser'
        response = self.app.post(
            '/rpc/searchHostAndGraph?search_form_host=%s' %
                urllib2.quote(host2.name.encode('utf-8'), ''),
            {},
            extra_environ={'REMOTE_USER': 'poweruser'}
        )
        json = response.json

        # On s'assure que les deux listes retournées contiennent
        # respectivement le nom de l'hôte et son identifiant
        self.assertEqual(
            json, {
                'labels': [[host2.name, None]],
                'ids': [[host2.idhost, None]],
                'more': False,
            }
        )

        # Récupération des résultats obtenus après une recherche
        # sur l'hôte 'host2' pour l'utilisateur 'user'
        response = self.app.post(
            '/rpc/searchHostAndGraph?search_form_host=%s' %
                urllib2.quote(host2.name.encode('utf-8'), ''),
            {},
            extra_environ={'REMOTE_USER': 'user'}
        )
        json = response.json

        # On s'assure que les deux listes retournées contiennent
        # respectivement le nom de l'hôte et son identifiant
        self.assertEqual(
            json, {
                'labels': [[host2.name, None]],
                'ids': [[host2.idhost, None]],
                'more': False,
            }
        )

    def test_select_host_when_not_allowed(self):
        """
        Résultats de la recherche sur un hôte sans les droits
        """

        # Récupération de l'hôte 'host1' dans la base de données
        host1 = DBSession.query(Host).filter(
            Host.name == u'host1 éà').first()

        # Récupération de l'hôte 'host3' dans la base de données
        host3 = DBSession.query(Host).filter(
            Host.name == u'host3 éà').first()

        # Récupération des résultats obtenus après une recherche
        # sur l'hôte 'host1' pour l'utilisateur 'user'
        response = self.app.post(
            '/rpc/searchHostAndGraph?search_form_host=%s' %
                urllib2.quote(host1.name.encode('utf-8'), ''),
            {},
            extra_environ={'REMOTE_USER': 'user'}
        )
        json = response.json

        # On s'assure que la liste retournée est vide
        self.assertEqual(
            json, {
                'labels': [],
                'ids': [],
                'more': False,
            }
        )

        # Récupération des résultats obtenus après une recherche
        # sur l'hôte 'host3' pour l'utilisateur 'user'
        response = self.app.post(
            '/rpc/searchHostAndGraph?search_form_host=%s' %
                urllib2.quote(host3.name.encode('utf-8'), ''),
            {},
            extra_environ={'REMOTE_USER': 'user'}
        )
        json = response.json

        # On s'assure que la liste
        # retournée est vide
        self.assertEqual(
            json, {
                'labels': [],
                'ids': [],
                'more': False,
            }
        )

        # Récupération des résultats obtenus après une recherche
        # sur l'hôte 'host1' pour l'utilisateur 'visitor'
        response = self.app.post(
            '/rpc/searchHostAndGraph?search_form_host=%s' %
                urllib2.quote(host1.name.encode('utf-8'), ''),
            {},
            extra_environ={'REMOTE_USER': 'visitor'}
        )
        json = response.json

        # On s'assure que la liste
        # retournée est vide
        self.assertEqual(
            json, {
                'labels': [],
                'ids': [],
                'more': False,
            }
        )

        # Récupération des résultats obtenus après une recherche
        # sur l'hôte 'host3' pour l'utilisateur 'visitor'
        response = self.app.post(
            '/rpc/searchHostAndGraph?search_form_host=%s' %
                urllib2.quote(host3.name.encode('utf-8'), ''),
            {},
            extra_environ={'REMOTE_USER': 'visitor'}
        )
        json = response.json

        # On s'assure que la liste
        # retournée est vide
        self.assertEqual(
            json, {
                'labels': [],
                'ids': [],
                'more': False,
            }
        )

    def test_select_host_as_anonymous(self):
        """
        Résultats de la recherche sur un hôte en tant qu'anonyme
        """

        # Récupération de l'hôte 'host1' dans la base de données
        host1 = DBSession.query(Host).filter(
            Host.name == u'host1 éà').first()

        # Récupération des résultats obtenus après une recherche
        # sur l'hôte 'host1' pour un utilisateur anonyme :
        # le contrôleur doit retourner une erreur 401.
        self.app.post(
            '/rpc/searchHostAndGraph?search_form_host=%s' %
                urllib2.quote(host1.name.encode('utf-8'), ''),
            {},
            status=401
        )

    def test_select_inexisting_host(self):
        """
        Résultats de la recherche sur un hôte inexistant
        """

        # Récupération des résultats obtenus après une recherche
        # sur un hôte inexistant pour l'utilisateur 'manager'
        response = self.app.post(
        '/rpc/searchHostAndGraph?search_form_host=hote_totalement_inexistant', {
            }, extra_environ={'REMOTE_USER': 'manager'})
        json = response.json

        # On s'assure que la liste retournée est vide
        self.assertEqual(
            json, {
                'labels': [],
                'ids': [],
                'more': False,
            }
        )

    def test_select_graph_without_a_host(self):
        """
        Résultats de la recherche sur un graphe sans préciser d'hôte
        """

        # Récupération de l'hôte 'host1' dans la base de données
        host1 = DBSession.query(Host).filter(
            Host.name == u'host1 éà').first()

        # Récupération du graphe 'graph1' dans la base de données
        graph1 = DBSession.query(Graph).filter(
            Graph.name == u'graph1 éà').first()

        # Récupération des résultats obtenus après une recherche sur
        # un graphe sans préciser d'hôte par l'utilisateur 'manager'.
        response = self.app.post(
            '/rpc/searchHostAndGraph?search_form_graph=%s' %
                urllib2.quote(graph1.name.encode('utf-8'), ''),
            {},
            extra_environ={'REMOTE_USER': 'manager'}
        )
        json = response.json

        # On s'assure que la liste retournée est conforme à celle attendue
        self.assertEqual(
            json, {
                'labels': [[host1.name, graph1.name]],
                'ids': [[host1.idhost, graph1.idgraph]],
                'more': False,
            }
        )

    def test_select_graph_with_an_erroneous_host(self):
        """
        Résultats de la recherche sur un graphe en précisant un hôte erroné
        """

        # Récupération du graphe 'graph1' dans la base de données
        graph1 = DBSession.query(Graph).filter(
            Graph.name == u'graph1 éà').first()

        # On s'assure qu'une liste vide est retournée lorsque
        # l'on recherche un graphe en précisant un hôte erroné.
        response = self.app.post(
            '/rpc/searchHostAndGraph?search_form_host=%s' %
                urllib2.quote(graph1.name.encode('utf-8'), ''),
            {},
            extra_environ={'REMOTE_USER': 'manager'}
        )
        json = response.json

        # On s'assure que la liste retournée est vide
        self.assertEqual(
            json, {
                'labels': [],
                'ids': [],
                'more': False,
            }
        )

    def test_select_graph_when_allowed(self):
        """
        Résultats de la recherche sur un graphe avec les bons droits
        """

        # Récupération du groupe d'hôtes 'mhg' dans la base de données
        DBSession.query(SupItemGroup).filter(
            SupItemGroup.name == u'mhg').first()

        # Récupération du groupe d'hôtes 'hg1' dans la base de données
        DBSession.query(SupItemGroup).filter(
            SupItemGroup.name == u'hg1').first()

        # Récupération de l'hôte 'host1' dans la base de données
        host1 = DBSession.query(Host).filter(
            Host.name == u'host1 éà').first()

        # Récupération de l'hôte 'host2' dans la base de données
        host2 = DBSession.query(Host).filter(
            Host.name == u'host2 éà').first()

        # Récupération du groupe de graphes
        # 'graphgroup1' dans la base de données
        DBSession.query(GraphGroup).filter(
            GraphGroup.name == u'graphgroup1').first()

        # Récupération du groupe de graphes
        # 'graphgroup2' dans la base de données
        DBSession.query(GraphGroup).filter(
            GraphGroup.name == u'graphgroup2').first()

        # Récupération du graphe 'graph1' dans la base de données
        graph1 = DBSession.query(Graph).filter(
            Graph.name == u'graph1 éà').first()

        # Récupération du graphe 'graph2' dans la base de données
        graph2 = DBSession.query(Graph).filter(
            Graph.name == u'graph2 éà').first()

        # Récupération des résultats obtenus après une recherche
        # sur le graphe 'graph1' pour l'utilisateur 'manager'
        response = self.app.post(
        '/rpc/searchHostAndGraph?search_form_host=%s&search_form_graph=%s' % (
                urllib2.quote(host1.name.encode('utf-8'), ''),
                urllib2.quote(graph1.name.encode('utf-8'), ''),
            ), {}, extra_environ={'REMOTE_USER': 'manager'})
        json = response.json

        # On s'assure que la liste retournée
        # est conforme à celle attendue
        self.assertEqual(
            json, {
                'labels': [[host1.name, graph1.name]],
                'ids': [[host1.idhost, graph1.idgraph]],
                'more': False,
            }
        )

        # Récupération des résultats obtenus après une recherche
        # sur le graphe 'graph1' pour l'utilisateur 'poweruser'
        response = self.app.post(
            '/rpc/searchHostAndGraph?search_form_host=%s&' \
            'search_form_graph=%s' % (
                urllib2.quote(host1.name.encode('utf-8'), ''),
                urllib2.quote(graph1.name.encode('utf-8'), ''),
            ), {}, extra_environ={'REMOTE_USER': 'poweruser'})
        json = response.json

        # On s'assure que la liste retournée est conforme à celle attendue
        self.assertEqual(
            json, {
                'labels': [[host1.name, graph1.name]],
                'ids': [[host1.idhost, graph1.idgraph]],
                'more': False,
            }
        )

        # Récupération des résultats obtenus après une recherche
        # sur le graphe 'graph2' pour l'utilisateur 'poweruser'
        response = self.app.post(
            '/rpc/searchHostAndGraph?search_form_host=%s&' \
            'search_form_graph=%s' % (
                urllib2.quote(host2.name.encode('utf-8'), ''),
                urllib2.quote(graph2.name.encode('utf-8'), ''),
            ), {}, extra_environ={'REMOTE_USER': 'poweruser'})
        json = response.json

        # On s'assure que la liste retournée
        # est conforme à celle attendue
        self.assertEqual(
            json, {
                'labels': [[host2.name, graph2.name]],
                'ids': [[host2.idhost, graph2.idgraph]],
                'more': False,
            }
        )

        # Récupération des résultats obtenus après une recherche
        # sur le graphe 'graph2' pour l'utilisateur 'user'
        response = self.app.post(
            '/rpc/searchHostAndGraph?search_form_host=%s&' \
            'search_form_graph=%s' % (
                urllib2.quote(host2.name.encode('utf-8'), ''),
                urllib2.quote(graph2.name.encode('utf-8'), ''),
            ), {}, extra_environ={'REMOTE_USER': 'user'})
        json = response.json

        # On s'assure que la liste retournée
        # est conforme à celle attendue
        self.assertEqual(
            json, {
                'labels': [[host2.name, graph2.name]],
                'ids': [[host2.idhost, graph2.idgraph]],
                'more': False,
            }
        )

    def test_select_graph_when_not_allowed(self):
        """
        Résultats de la recherche sur un graphe sans les droits
        """

        # Récupération de l'hôte 'host1' dans la base de données
        host1 = DBSession.query(Host).filter(
            Host.name == u'host1 éà').first()

        # Récupération de l'hôte 'host3' dans la base de données
        host3 = DBSession.query(Host).filter(
            Host.name == u'host3 éà').first()

        # Récupération du graphe 'graph1' dans la base de données
        graph1 = DBSession.query(Graph).filter(
            Graph.name == u'graph1 éà').first()

        # Récupération du graphe 'graph3' dans la base de données
        graph3 = DBSession.query(Graph).filter(
            Graph.name == u'graph3 éà').first()

        # Récupération des résultats obtenus après une recherche
        # sur le graphe 'graph1' pour l'utilisateur 'user'
        response = self.app.post(
            '/rpc/searchHostAndGraph?search_form_host=%s&' \
            'search_form_graph=%s' % (
                urllib2.quote(host1.name.encode('utf-8'), ''),
                urllib2.quote(graph1.name.encode('utf-8'), ''),
            ), {}, extra_environ={'REMOTE_USER': 'user'})
        json = response.json

        # On s'assure que la liste retournée est vide
        self.assertEqual(
            json, {
                'labels': [],
                'ids': [],
                'more': False,
            }
        )

        # Récupération des résultats obtenus après une recherche
        # sur le graphe 'graph3' pour l'utilisateur 'user'
        response = self.app.post(
            '/rpc/searchHostAndGraph?search_form_host=%s&' \
            'search_form_graph=%s' % (
                urllib2.quote(host3.name.encode('utf-8'), ''),
                urllib2.quote(graph3.name.encode('utf-8'), ''),
            ), {}, extra_environ={'REMOTE_USER': 'user'})
        json = response.json

        # On s'assure que la liste retournée est vide
        self.assertEqual(
            json, {
                'labels': [],
                'ids': [],
                'more': False,
            }
        )

        # Récupération des résultats obtenus après une recherche
        # sur le graphe 'graph1' pour l'utilisateur 'visitor'
        response = self.app.post(
            '/rpc/searchHostAndGraph?search_form_host=%s&' \
            'search_form_graph=%s' % (
                urllib2.quote(host1.name.encode('utf-8'), ''),
                urllib2.quote(graph1.name.encode('utf-8'), ''),
            ), {}, extra_environ={'REMOTE_USER': 'visitor'})
        json = response.json

        # On s'assure que la liste retournée est vide
        self.assertEqual(
            json, {
                'labels': [],
                'ids': [],
                'more': False,
            }
        )

        # Récupération des résultats obtenus après une recherche
        # sur le graphe 'graph3' pour l'utilisateur 'visitor'
        response = self.app.post(
            '/rpc/searchHostAndGraph?search_form_host=%s&' \
            'search_form_graph=%s' % (
                urllib2.quote(host3.name.encode('utf-8'), ''),
                urllib2.quote(graph3.name.encode('utf-8'), ''),
            ), {}, extra_environ={'REMOTE_USER': 'visitor'})
        json = response.json

        # On s'assure que la liste retournée est vide
        self.assertEqual(
            json, {
                'labels': [],
                'ids': [],
                'more': False,
            }
        )

    def test_select_graph_as_anonymous(self):
        """
        Résultats de la recherche sur un graphe en tant qu'anonyme
        """

        # Récupération de l'hôte 'host1' dans la base de données
        host1 = DBSession.query(Host).filter(
            Host.name == u'host1 éà').first()

        # Récupération du graphe 'graph1' dans la base de données
        graph1 = DBSession.query(Graph).filter(
            Graph.name == u'graph1 éà').first()

        # Récupération des résultats obtenus après une recherche
        # sur le graphe 'graph1' pour un utilisateur anonyme :
        # le contrôleur doit retourner une erreur 401
        self.app.post(
            '/rpc/searchHostAndGraph?search_form_host=%s&' \
            'search_form_graph=%s' % (
                urllib2.quote(host1.name.encode('utf-8'), ''),
                urllib2.quote(graph1.name.encode('utf-8'), ''),
            ), {}, status=401)

    def test_select_inexisting_graph(self):
        """
        Résultats de la recherche sur un graphe inexistant
        """

        # Récupération de l'hôte 'host1' dans la base de données
        host1 = DBSession.query(Host).filter(
            Host.name == u'host1 éà').first()

        # Récupération des résultats obtenus après une recherche
        # sur un graphe inexistant pour l'utilisateur 'manager'
        response = self.app.post(
           '/rpc/searchHostAndGraph?search_form_host=%s&' \
           'search_form_graph=%s' % (
                urllib2.quote(host1.name.encode('utf-8'), ''),
                'graphe_totalement_inexistant',
            ), {}, extra_environ={'REMOTE_USER': 'manager'}
        )
        json = response.json

        # On s'assure que la liste retournée est vide
        self.assertEqual(
            json, {
                'labels': [],
                'ids': [],
                'more': False,
            }
        )
