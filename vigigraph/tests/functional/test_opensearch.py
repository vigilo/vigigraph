# -*- coding: utf-8 -*-
# Copyright (C) 2006-2016 CS-SI
# License: GNU GPL v2 <http://www.gnu.org/licenses/gpl-2.0.html>

"""
Teste l'utilisation du module de recherche
OpenSearch intégré au navigateur.
"""
import transaction
import urllib

from vigigraph.tests import TestController
from vigilo.models.session import DBSession
from vigigraph.tests.functional.helpers import populateDB, addGraphs


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
                    u'/rpc/fullHostPage?host=%s' %
                        urllib.quote_plus(host.encode('utf-8'))
                    in response.unicode_body
                )
            else:
                self.assertTrue(
                    u'/rpc/fullHostPage?host=%s' %
                        urllib.quote_plus(host.encode('utf-8'))
                    not in response.unicode_body
                )

    def test_direct_permission(self):
        """OpenSearch avec permission sur le groupe"""
        hosts = {
            u'host1 éà': False,
            u'host2 éà': True,
            u'host3 éà': False,
        }
        self._check_results('user', hosts)

    def test_permission_on_parent(self):
        """OpenSearch avec permission sur le parent du groupe"""
        hosts = {
            u'host1 éà': True,
            u'host2 éà': True,
            u'host3 éà': True,
        }
        self._check_results('poweruser', hosts)

    def test_no_permission(self):
        """OpenSearch sans permissions"""
        hosts = {
            u'host1 éà': False,
            u'host2 éà': False,
            u'host3 éà': False,
        }
        self._check_results('visitor', hosts)

    def test_anonymous(self):
        """OpenSearch en anonyme"""
        for host in (u'host1 éà', u'host2 éà', u'host3 éà'):
            self.app.get(
                '/rpc/fullHostPage?host=%s' %
                    urllib.quote_plus(host.encode('utf-8'), ''),
                status=401
            )

    def test_managers(self):
        """OpenSearch avec le compte manager"""
        hosts = {
            u'host1 éà': True,
            u'host2 éà': True,
            u'host3 éà': True,
        }
        self._check_results('manager', hosts)
