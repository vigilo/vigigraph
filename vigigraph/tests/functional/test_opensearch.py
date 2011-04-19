# -*- coding: utf-8 -*-
# Copyright (C) 2006-2011 CS-SI
# License: GNU GPL v2 <http://www.gnu.org/licenses/gpl-2.0.html>

"""
Teste l'utilisation du module de recherche
OpenSearch intégré au navigateur.
"""
import transaction

from vigigraph.tests import TestController
from vigilo.models.session import DBSession
from vigilo.models.tables import Host, SupItemGroup, Graph, GraphGroup

from vigigraph.tests.functional.test_host_selection_form import populateDB
from vigigraph.tests.functional.test_graph_selection_form import addGraphs


class TestOpenSearch(TestController):
    """
    Teste la page d'affichage de tous les graphs d'un hôte.
    """

    def setUp(self):
        """Préparation de la base de données de tests."""

        # Initialisation de la base
        super(TestOpenSearch, self).setUp()

        # Ajout de données de tests dans la base
        (host1, host2, host3) = populateDB()

        # Ajout de graphes dans la base
        addGraphs(host1, host2, host3)

        # Validation des ajouts dans la base
        DBSession.flush()
        transaction.commit()

    def _check_results(self, user, hosts):
        response = self.app.get(
            '/rpc/searchHost?query=host*',
            extra_environ={"REMOTE_USER": user}
        )
        for host in hosts:
            if hosts[host]:
                self.assertTrue(
                    '/rpc/fullHostPage?host=%s' % host
                    in response.body
                )
            else:
                self.assertTrue(
                    '/rpc/fullHostPage?host=%s' % host
                    not in response.body
                )

    def test_direct_permission(self):
        """OpenSearch avec permission sur le groupe"""
        hosts = {
            'host1': False,
            'host2': True,
            'host3': False,
        }
        self._check_results('user', hosts)

    def test_permission_on_parent(self):
        """OpenSearch avec permission sur le parent du groupe"""
        hosts = {
            'host1': True,
            'host2': True,
            'host3': True,
        }
        self._check_results('poweruser', hosts)

    def test_no_permission(self):
        """OpenSearch sans permissions"""
        hosts = {
            'host1': False,
            'host2': False,
            'host3': False,
        }
        self._check_results('visitor', hosts)

    def test_anonymous(self):
        """OpenSearch en anonyme"""
        for host in ('host1', 'host2', 'host3'):
            response = self.app.get(
                '/rpc/fullHostPage?host=%s' % host,
                status=401
            )

    def test_managers(self):
        """OpenSearch avec le compte manager"""
        hosts = {
            'host1': True,
            'host2': True,
            'host3': True,
        }
        self._check_results('manager', hosts)
