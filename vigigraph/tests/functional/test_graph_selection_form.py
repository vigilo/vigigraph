# -*- coding: utf-8 -*-
# Copyright (C) 2006-2016 CS-SI
# License: GNU GPL v2 <http://www.gnu.org/licenses/gpl-2.0.html>

"""
Suite de tests de l'arbre de sélection des graphes et groupes de graphes.
"""
import transaction

from vigigraph.tests import TestController
from vigilo.models.session import DBSession
from vigilo.models.tables import Host, Graph, GraphGroup
from vigigraph.tests.functional.helpers import populateDB, addGraphs


class TestGraphTree(TestController):
    """
    Teste l'arbre de sélection des graphes
    et groupes de graphes de Vigigraph.
    """

    def setUp(self):
        """Préparation de la base de données de tests."""

        # Initialisation de la base
        super(TestGraphTree, self).setUp()

        # Ajout de données de tests dans la base
        (host1, host2, host3) = populateDB()

        # Ajout de graphes dans la base
        addGraphs(host1, host2, host3)

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
            Host.name == u'host1 éà').first()

        # Récupération de l'hôte 'host2' dans la base de données
        host2 = DBSession.query(Host).filter(
            Host.name == u'host2 éà').first()

        # Récupération de l'hôte 'host3' dans la base de données
        host3 = DBSession.query(Host).filter(
            Host.name == u'host3 éà').first()

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
        # host1 accessibles à l'utilisateur 'manager'
        response = self.app.post(
        '/rpc/graphtree?host_id=%s' % (host1.idhost, ), {
            }, extra_environ={'REMOTE_USER': 'manager'})
        json = response.json

        # On s'assure que la liste de groupes
        # de graphes retournée contient bien 'graphgroup1'
        self.assertEqual(
            json, {
                'items': [],
                'groups': [{'id': graphgroup1.idgroup,
                            'name': graphgroup1.name,
                            'type': 'group'}]
            }
        )

        # Récupération des groupes de graphes de l'hôte
        # host2 accessibles à l'utilisateur 'manager'
        response = self.app.post(
        '/rpc/graphtree?host_id=%s' % (host2.idhost, ), {
            }, extra_environ={'REMOTE_USER': 'manager'})
        json = response.json

        # On s'assure que la liste de groupes
        # de graphes retournée contient bien 'graphgroup2'
        self.assertEqual(
            json, {
                'items': [],
                'groups': [{'id': graphgroup2.idgroup,
                            'name': graphgroup2.name,
                            'type': 'group'}]
            }
        )

        # Récupération des groupes de graphes de l'hôte
        # host1 accessibles à l'utilisateur 'poweruser'
        response = self.app.post(
        '/rpc/graphtree?host_id=%s' % (host1.idhost, ), {
            }, extra_environ={'REMOTE_USER': 'poweruser'})
        json = response.json

        # On s'assure que la liste de groupes
        # de graphes retournée contient bien 'graphgroup1'
        self.assertEqual(
            json, {
                'items': [],
                'groups': [{'id': graphgroup1.idgroup,
                            'name': graphgroup1.name,
                            'type': 'group'}]
            }
        )

        # Récupération des groupes de graphes de l'hôte
        # host2 accessibles à l'utilisateur 'poweruser'
        response = self.app.post(
        '/rpc/graphtree?host_id=%s' % (host2.idhost, ), {
            }, extra_environ={'REMOTE_USER': 'poweruser'})
        json = response.json

        # On s'assure que la liste de groupes
        # de graphes retournée contient bien 'graphgroup2'
        self.assertEqual(
            json, {
                'items': [],
                'groups': [{'id': graphgroup2.idgroup,
                            'name': graphgroup2.name,
                            'type': 'group'}]
            }
        )

        # Récupération des groupes de graphes de l'hôte
        # host2 accessibles à l'utilisateur 'user'
        response = self.app.post(
        '/rpc/graphtree?host_id=%s' % (host2.idhost, ), {
            }, extra_environ={'REMOTE_USER': 'user'})
        json = response.json

        # On s'assure que la liste de groupes
        # de graphes retournée contient bien 'graphgroup2'
        self.assertEqual(
            json, {
                'items': [],
                'groups': [{'id': graphgroup2.idgroup,
                            'name': graphgroup2.name,
                            'type': 'group'}]
            }
        )

        # Récupération des groupes de graphes de l'hôte
        # host3 accessibles à l'utilisateur 'poweruser'
        response = self.app.post(
        '/rpc/graphtree?host_id=%s' % (host3.idhost, ), {
            }, extra_environ={'REMOTE_USER': 'poweruser'})
        json = response.json

        # On s'assure que la liste de groupes
        # de graphes retournée contient bien 'graphgroup3'
        self.assertEqual(
            json, {
                'items': [],
                'groups': [{'id': graphgroup3.idgroup,
                            'name': graphgroup3.name,
                            'type': 'group'}]
            }
        )

    def test_get_graph_groups_when_not_allowed(self):
        """
        Récupération des groupes de graphes sans les bons droits
        """

        # Récupération de l'hôte 'host1' dans la base de données
        host1 = DBSession.query(Host).filter(
            Host.name == u'host1 éà').first()

        # Récupération de l'hôte 'host3' dans la base de données
        host3 = DBSession.query(Host).filter(
            Host.name == u'host3 éà').first()

        # Récupération des groupes de graphes de l'hôte
        # host1 accessibles à l'utilisateur 'user'
        response = self.app.post(
        '/rpc/graphtree?host_id=%s' % (host1.idhost, ), {
            }, extra_environ={'REMOTE_USER': 'user'})
        json = response.json

        # On s'assure que la liste de groupes
        # de graphes retournée est vide
        self.assertEqual(
            json, {
                'graphs': [],
                'groups': []
            }
        )

        # Récupération des groupes de graphes de l'hôte
        # host3 accessibles à l'utilisateur 'user'
        response = self.app.post(
        '/rpc/graphtree?host_id=%s' % (host3.idhost, ), {
            }, extra_environ={'REMOTE_USER': 'user'})
        json = response.json

        # On s'assure que la liste de groupes
        # de graphes retournée est vide
        self.assertEqual(
            json, {
                'graphs': [],
                'groups': []
            }
        )

        # Récupération des groupes de graphes de l'hôte
        # host1 accessibles à l'utilisateur 'visitor'
        response = self.app.post(
        '/rpc/graphtree?host_id=%s' % (host1.idhost, ), {
            }, extra_environ={'REMOTE_USER': 'visitor'})
        json = response.json

        # On s'assure que la liste de groupes
        # de graphes retournée est vide
        self.assertEqual(
            json, {
                'graphs': [],
                'groups': []
            }
        )

    def test_get_graph_groups_as_anonymous(self):
        """
        Récupération des groupes de graphes en tant qu'anonyme
        """

        # Récupération de l'hôte 'host1' dans la base de données
        host1 = DBSession.query(Host).filter(
            Host.name == u'host1 éà').first()

        # Récupération des groupes de graphes de l'hôte
        # 'host1' par un utilisateur anonyme : le contrôleur
        # doit retourner une erreur 401 (HTTPUnauthorized)
        self.app.post(
            '/rpc/graphtree?host_id=%s' % (host1.idhost, ), {
            }, status=401)

    def test_get_graph_groups_from_inexisting_host(self):
        """
        Récupération des groupes de graphes d'un hôte inexistant
        """

        # Récupération des groupes d'hôtes accessibles à l'utilisateur
        # 'visitor' et appartenant à un groupe principal inexistant
        response = self.app.post(
            '/rpc/graphtree?host_id=6666666', {
            }, extra_environ={'REMOTE_USER': 'visitor'})
        json = response.json

        # On s'assure que la liste de groupes
        # de graphes retournée est vide
        self.assertEqual(
            json, {
                'graphs': [],
                'groups': []
            }
        )

##### Cinquième onglet déroulant du formulaire #####

    def test_get_graphs_when_allowed(self):
        """
        Récupération des graphes avec les bons droits
        """

        # Récupération de l'hôte 'host1' dans la base de données
        host1 = DBSession.query(Host).filter(
            Host.name == u'host1 éà').first()

        # Récupération de l'hôte 'host2' dans la base de données
        host2 = DBSession.query(Host).filter(
            Host.name == u'host2 éà').first()

        # Récupération de l'hôte 'host3' dans la base de données
        host3 = DBSession.query(Host).filter(
            Host.name == u'host3 éà').first()

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
            Graph.name == u'graph1 éà').first()

        # Récupération du graphe 'graph2'
        # dans la base de données
        graph2 = DBSession.query(Graph).filter(
            Graph.name == u'graph2 éà').first()

        # Récupération du graphe 'graph3'
        # dans la base de données
        graph3 = DBSession.query(Graph).filter(
            Graph.name == u'graph3 éà').first()

        # Récupération des graphes du groupe de graphes
        # 'graphgroup1' accessibles à l'utilisateur 'manager'
        response = self.app.post(
        '/rpc/graphtree?parent_id=%s&host_id=%s' %
            (graphgroup1.idgroup, host1.idhost), {},
            extra_environ={'REMOTE_USER': 'manager'})
        json = response.json

        # On s'assure que la liste de
        # graphes retournée contient 'graph1'
        self.assertEqual(
            json, {
                'items': [{'id': graph1.idgraph,
                           'name': graph1.name,
                           'type': 'item'}],
                'groups': []
            }
        )

        # Récupération des graphes du groupe de graphes
        # 'graphgroup2' accessibles à l'utilisateur 'manager'
        response = self.app.post(
        '/rpc/graphtree?parent_id=%s&host_id=%s' %
            (graphgroup2.idgroup, host2.idhost), {},
            extra_environ={'REMOTE_USER': 'manager'})
        json = response.json

        # On s'assure que la liste de
        # graphes retournée contient 'graph2'
        self.assertEqual(
            json, {
                'items': [{'id': graph2.idgraph,
                           'name': graph2.name,
                           'type': 'item'}],
                'groups': []
            }
        )

        # Récupération des graphes du groupe de graphes
        # 'graphgroup1' accessibles à l'utilisateur 'poweruser'
        response = self.app.post(
        '/rpc/graphtree?parent_id=%s&host_id=%s' %
            (graphgroup1.idgroup, host1.idhost), {},
            extra_environ={'REMOTE_USER': 'poweruser'})
        json = response.json

        # On s'assure que la liste de
        # graphes retournée contient 'graph1'
        self.assertEqual(
            json, {
                'items': [{'id': graph1.idgraph,
                           'name': graph1.name,
                           'type': 'item'}],
                'groups': []
            }
        )

        # Récupération des graphes du groupe de graphes
        # 'graphgroup2' accessibles à l'utilisateur 'poweruser'
        response = self.app.post(
        '/rpc/graphtree?parent_id=%s&host_id=%s' %
            (graphgroup2.idgroup, host2.idhost), {},
            extra_environ={'REMOTE_USER': 'poweruser'})
        json = response.json

        # On s'assure que la liste de
        # graphes retournée contient 'graph2'
        self.assertEqual(
            json, {
                'items': [{'id': graph2.idgraph,
                           'name': graph2.name,
                           'type': 'item'}],
                'groups': []
            }
        )

        # Récupération des graphes du groupe de graphes
        # 'graphgroup2' accessibles à l'utilisateur 'user'
        response = self.app.post(
        '/rpc/graphtree?parent_id=%s&host_id=%s' %
            (graphgroup2.idgroup, host2.idhost), {},
            extra_environ={'REMOTE_USER': 'user'})
        json = response.json

        # On s'assure que la liste de
        # graphes retournée contient 'graph2'
        self.assertEqual(
            json, {
                'items': [{'id': graph2.idgraph,
                           'name': graph2.name,
                           'type': 'item'}],
                'groups': []
            }
        )

        # Récupération des graphes du groupe de graphes
        # 'graphgroup3' accessibles à l'utilisateur 'poweruser'
        response = self.app.post(
        '/rpc/graphtree?parent_id=%s&host_id=%s' %
            (graphgroup3.idgroup, host3.idhost), {},
            extra_environ={'REMOTE_USER': 'poweruser'})
        json = response.json

        # On s'assure que la liste de
        # graphes retournée contient 'graph3'
        self.assertEqual(
            json, {
                'items': [{'id': graph3.idgraph,
                           'name': graph3.name,
                           'type': 'item'}],
                'groups': []
            }
        )

    def test_get_graphs_when_not_allowed(self):
        """
        Récupération des graphes sans les bons droits
        """

        # Récupération de l'hôte 'host1' dans la base de données
        host1 = DBSession.query(Host).filter(
            Host.name == u'host1 éà').first()

        # Récupération de l'hôte 'host3' dans la base de données
        host3 = DBSession.query(Host).filter(
            Host.name == u'host3 éà').first()

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
        '/rpc/graphtree?parent_id=%s&host_id=%s' %
            (graphgroup1.idgroup, host1.idhost), {},
            extra_environ={'REMOTE_USER': 'user'})
        json = response.json

        # On s'assure que la liste de groupes
        # de graphes retournée est vide
        self.assertEqual(
            json, {
                'graphs': [],
                'groups': []
            }
        )

        # Récupération des graphes du groupe de graphes
        # 'graphgroup1' accessibles à l'utilisateur 'visitor'
        response = self.app.post(
        '/rpc/graphtree?parent_id=%s&host_id=%s' %
            (graphgroup1.idgroup, host1.idhost), {},
            extra_environ={'REMOTE_USER': 'visitor'})
        json = response.json

        # On s'assure que la liste de groupes
        # de graphes retournée est vide
        self.assertEqual(
            json, {
                'graphs': [],
                'groups': []
            }
        )

        # Récupération des graphes du groupe de graphes
        # 'graphgroup3' accessibles à l'utilisateur 'user'
        response = self.app.post(
        '/rpc/graphtree?parent_id=%s&host_id=%s' %
            (graphgroup3.idgroup, host3.idhost), {},
            extra_environ={'REMOTE_USER': 'user'})
        json = response.json

        # On s'assure que la liste de groupes
        # de graphes retournée est vide
        self.assertEqual(
            json, {
                'graphs': [],
                'groups': []
            }
        )

    def test_get_graphs_as_anonymous(self):
        """
        Récupération des graphes en tant qu'anonyme
        """

        # Récupération de l'hôte 'host1' dans la base de données
        host1 = DBSession.query(Host).filter(
            Host.name == u'host1 éà').first()

        # Récupération du groupe de graphes
        # 'graphgroup1' dans la base de données
        graphgroup1 = DBSession.query(GraphGroup).filter(
            GraphGroup.name == u'graphgroup1').first()

        # Récupération des graphes du groupe de graphes
        # 'graphgroup1' par un utilisateur anonyme : le contrôleur
        # doit retourner une erreur 401 (HTTPUnauthorized)
        self.app.post(
            '/rpc/graphtree?parent_id=%s&host_id=%s' %
            (graphgroup1.idgroup, host1.idhost),
            {}, status=401)

    def test_get_graphs_from_inexisting_graph_group(self):
        """
        Récupération des graphes d'un groupe de graphes inexistant
        """

        # Récupération des graphes accessibles à l'utilisateur
        # 'manager' et appartenant à un groupe inexistant
        response = self.app.post(
            '/rpc/graphtree?parent_id=6666666&host_id=6666666', {
            }, extra_environ={'REMOTE_USER': 'manager'})
        json = response.json

        # On s'assure que la liste de
        # graphes retournée est vide
        self.assertEqual(
            json, {
                'graphs': [],
                'groups': []
            }
        )
