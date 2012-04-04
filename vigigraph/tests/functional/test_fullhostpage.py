# -*- coding: utf-8 -*-
# Copyright (C) 2006-2012 CS-SI
# License: GNU GPL v2 <http://www.gnu.org/licenses/gpl-2.0.html>

"""
Tests les accès à la page rpc/fullHostPage
permettant d'afficher tous les graphes
associés à un hôte.
"""
import transaction, urllib2

from vigigraph.tests import TestController
from vigilo.models.session import DBSession
from vigigraph.tests.functional.helpers import populateDB, addGraphs


class TestFullHostPage(TestController):
    """
    Teste la page d'affichage de tous les graphs d'un hôte.
    """

    def setUp(self):
        """Préparation de la base de données de tests."""

        # Initialisation de la base
        super(TestFullHostPage, self).setUp()

        # Ajout de données de tests dans la base
        (host1, host2, host3) = populateDB()

        # Ajout de graphes dans la base
        addGraphs(host1, host2, host3)

        # Validation des ajouts dans la base
        DBSession.flush()
        transaction.commit()

    def _check_results(self, user, hosts):
        for host in hosts:
            if hosts[host]:
                response = self.app.get(
                    '/rpc/fullHostPage?host=%s' %
                        urllib2.quote(host.encode('utf-8')),
                    extra_environ={"REMOTE_USER": user}
                )
                index = int(host[4])
                self.assertTrue(
                    '/vigirrd/%s/index?graphtemplate=%s' % (
                        urllib2.quote((u'host%d éà' % index).encode('utf-8')),
                        urllib2.quote((u'graph%d éà' % index).encode('utf-8')),
                    ) in response.unicode_body
                )
            else:
                response = self.app.get(
                    '/rpc/fullHostPage?host=%s' %
                        urllib2.quote(host.encode('utf-8')),
                    extra_environ={"REMOTE_USER": user},
                    status = 403
                )

    def test_direct_permission(self):
        """Accès à rpc/fullHostPage avec permission sur le groupe"""
        hosts = {
            u'host1 éà': False,
            u'host2 éà': True,
            u'host3 éà': False,
        }
        self._check_results('user', hosts)

    def test_permission_on_parent(self):
        """Accès à rpc/fullHostPage avec permission sur le parent du groupe"""
        hosts = {
            u'host1 éà': True,
            u'host2 éà': True,
            u'host3 éà': True,
        }
        self._check_results('poweruser', hosts)

    def test_no_permission(self):
        """Accès à rpc/fullHostPage sans permissions"""
        hosts = {
            u'host1 éà': False,
            u'host2 éà': False,
            u'host3 éà': False,
        }
        self._check_results('visitor', hosts)

    def test_anonymous(self):
        """Accès à rpc/fullHostPage en anonyme"""
        for host in (u'host1 éà', u'host2 éà', u'host3 éà'):
            self.app.get(
                '/rpc/fullHostPage?host=%s' %
                    urllib2.quote(host.encode('utf-8'), ''),
                status=401
            )

    def test_managers(self):
        """Accès à rpc/fullHostPage depuis le compte manager"""
        hosts = {
            u'host1 éà': True,
            u'host2 éà': True,
            u'host3 éà': True,
        }
        self._check_results('manager', hosts)
