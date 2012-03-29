# -*- coding: utf-8 -*-
# Copyright (C) 2006-2011 CS-SI
# License: GNU GPL v2 <http://www.gnu.org/licenses/gpl-2.0.html>

"""
Suite de tests de l'arbre de sélection des hôtes et groupes d'hôtes.
"""
import transaction

from vigigraph.tests import TestController
from vigilo.models.session import DBSession
from vigilo.models.tables import Host, SupItemGroup
from vigigraph.tests.functional.helpers import populateDB

class TestHostTree(TestController):
    """
    Teste l'arbre de sélection des hôtes
    et groupes d'hôtes de Vigigraph.
    """

    def setUp(self):
        """Préparation de la base de données de tests."""

        # Initialisation de la base
        super(TestHostTree, self).setUp()

        # Ajout de données de tests dans la base
        populateDB()

        # Validation des ajouts dans la base
        DBSession.flush()
        transaction.commit()

    def test_get_root_host_groups_as_manager(self):
        """
        Récupération des groupes d'hôtes racines en tant que manager

        L'utilisateur "manager" appartient au groupe "managers",
        qui a accès à tout et doit donc pouvoir lister tous
        les groupes racines.
        """
        # Récupération du groupe d'hôtes 'mhg' dans la base de données
        mainhostgroup = DBSession.query(SupItemGroup).filter(
            SupItemGroup.name == u'mhg').first()

        # Récupération des groupes d'hôtes principaux
        # accessibles à l'utilisateur 'manager'.
        response = self.app.post(
            '/rpc/hosttree', {
            }, extra_environ={'REMOTE_USER': 'manager'})
        json = response.json

        # On s'assure que la liste de groupes
        # d'hôtes retournée contient bien 'mhg'
        self.assertEqual(
            json, {
                'items': [], 'groups': [{
                    'id': mainhostgroup.idgroup,
                    'name': mainhostgroup.name,
                    'type': 'group',
                }]
            }
        )

    def test_get_main_host_groups_when_directly_allowed(self):
        """
        Récupération des groupes d'hôtes racines avec permissions directes

        L'utilisateur "poweruser" a les permissions sur le
        groupe racine "mhg" et peut donc le lister.
        """
        # Récupération du groupe d'hôtes 'mhg' dans la base de données
        mainhostgroup = DBSession.query(SupItemGroup).filter(
            SupItemGroup.name == u'mhg').first()

        # Récupération des groupes d'hôtes principaux
        # accessibles à l'utilisateur 'poweruser'
        response = self.app.post(
            '/rpc/hosttree', {
            }, extra_environ={'REMOTE_USER': 'poweruser'})
        json = response.json

        # On s'assure que la liste de groupes
        # d'hôtes retournée contient bien 'mhg'
        self.assertEqual(
            json, {
                'items': [], 'groups': [{
                    'id': mainhostgroup.idgroup,
                    'name': mainhostgroup.name,
                    'type': 'group',
                }]
            }
        )

    def test_get_root_host_groups_for_children(self):
        """
        Récupération des groupes d'hôtes racines pour un sous-groupe

        L'utilisateur "user" n'a pas les permissions sur "mhg",
        mais il a accès au sous-groupe "hg1". Il doit pouvoir
        lister le groupe racine "mhg" pour pouvoir accéder à "hg1".
        """
        # Récupération du groupe d'hôtes 'mhg' dans la base de données
        mainhostgroup = DBSession.query(SupItemGroup).filter(
            SupItemGroup.name == u'mhg').first()

        # Récupération des groupes d'hôtes principaux
        # accessibles à l'utilisateur 'user'
        response = self.app.post(
            '/rpc/hosttree', {
            }, extra_environ={'REMOTE_USER': 'user'})
        json = response.json

        # On s'assure que la liste de groupes
        # d'hôtes retournée contient bien 'mhg'
        self.assertEqual(
            json, {
                'items': [], 'groups': [{
                    'id': mainhostgroup.idgroup,
                    'name': mainhostgroup.name,
                    'type': 'group',
                }]
            }
        )

    def test_get_main_host_groups_when_not_allowed(self):
        """
        Récupération des groupes d'hôtes principaux sans les bons droits

        L'utilisateur "visitor" n'a accès à rien et ne doit donc
        pas pouvoir lister le groupe racine "mhg".
        """

        # Récupération des groupes d'hôtes principaux
        # accessibles à l'utilisateur 'visitor'
        response = self.app.post(
            '/rpc/hosttree', {
            }, extra_environ={'REMOTE_USER': 'visitor'})
        json = response.json

        # On s'assure que la liste de groupes d'hôtes retournée est bien vide
        self.assertEqual(
            json, {'items': [], 'groups': []}
        )

    def test_get_main_host_groups_as_anonymous(self):
        """
        Récupération des groupes d'hôtes principaux en tant qu'anonyme

        Une tentative de récupération des groupes racines
        sans être authentifié doit demander à l'utilisateur
        de s'authentifier.
        """

        # Récupération des groupes d'hôtes principaux
        # par un utilisateur anonyme : le contrôleur doit
        # retourner une erreur 401 (HTTPUnauthorized)
        self.app.post(
            '/rpc/hosttree', {
            }, status=401)

    def test_get_host_groups_when_allowed(self):
        """
        Récupération des groupes d'hôtes secondaires avec les bons droits
        """

        # Récupération du groupe d'hôtes 'mhg' dans la base de données
        mainhostgroup = DBSession.query(SupItemGroup).filter(
            SupItemGroup.name == u'mhg').first()

        # Récupération du groupe d'hôtes 'hg1' dans la base de données
        hostgroup1 = DBSession.query(SupItemGroup).filter(
            SupItemGroup.name == u'hg1').first()

        # Récupération du groupe d'hôtes 'hg2' dans la base de données
        hostgroup2 = DBSession.query(SupItemGroup).filter(
            SupItemGroup.name == u'hg2').first()

        # Récupération de l'hôte 'host1' dans la base de données
        host1 = DBSession.query(Host).filter(
            Host.name == u'host1 éà').first()

        # Récupération des groupes d'hôtes
        # accessibles à l'utilisateur 'manager'
        response = self.app.post(
            '/rpc/hosttree?parent_id=%s' % (mainhostgroup.idgroup, ), {
            }, extra_environ={'REMOTE_USER': 'manager'})
        json = response.json

        # On s'assure que la liste de groupes d'hôtes retournée
        # contient bien 'No subgroup', 'hg1', et 'hg2'
        self.assertEqual(
            json, {
                'items': [
                    {'id': host1.idhost, 'name': host1.name, 'type': 'item'}
                ],
                'groups': [
                    {
                        'id': hostgroup1.idgroup,
                        'name': hostgroup1.name,
                        'type': 'group',
                    },
                    {
                        'id': hostgroup2.idgroup,
                        'name': hostgroup2.name,
                        'type': 'group',
                    },
                ],
            }
        )

        # Récupération des groupes d'hôtes
        # accessibles à l'utilisateur 'poweruser'
        response = self.app.post(
            '/rpc/hosttree?parent_id=%s' % (mainhostgroup.idgroup, ), {
            }, extra_environ={'REMOTE_USER': 'poweruser'})
        json = response.json

        # On s'assure que la liste de groupes d'hôtes retournée
        # contient bien 'No subgroup', 'hg1', et 'hg2'
        self.assertEqual(
            json, {
                'items': [
                    {'id': host1.idhost, 'name': host1.name, 'type': 'item'}
                ],
                'groups': [
                    {
                        'id': hostgroup1.idgroup,
                        'name': hostgroup1.name,
                        'type': 'group',
                    },
                    {
                        'id': hostgroup2.idgroup,
                        'name': hostgroup2.name,
                        'type': 'group',
                    },
                ],
            }
        )

        # Récupération des groupes d'hôtes
        # accessibles à l'utilisateur 'user'
        response = self.app.post(
            '/rpc/hosttree?parent_id=%s' % (mainhostgroup.idgroup, ), {
            }, extra_environ={'REMOTE_USER': 'user'})
        json = response.json

        # On s'assure que la liste de groupes
        # d'hôtes retournée contient bien 'hg1'
        self.assertEqual(
            json, {
                'items': [],
                'groups': [
                    {
                        'id': hostgroup1.idgroup,
                        'name': hostgroup1.name,
                        'type': 'group',
                    },
                ],
            }
        )

    def test_get_host_groups_when_not_allowed(self):
        """
        Récupération des groupes d'hôtes secondaires sans les bons droits
        """

        # Récupération du groupe d'hôtes 'mhg' dans la base de données
        mainhostgroup = DBSession.query(SupItemGroup).filter(
            SupItemGroup.name == u'mhg').first()

        # Récupération des groupes d'hôtes
        # accessibles à l'utilisateur 'visitor'
        response = self.app.post(
            '/rpc/hosttree?parent_id=%s' % (mainhostgroup.idgroup, ), {
            }, extra_environ={'REMOTE_USER': 'visitor'})
        json = response.json

        # On s'assure que la liste de groupes d'hôtes retournée est bien vide
        self.assertEqual(
            json, {'items': [], 'groups': []}
        )

    def test_get_host_groups_as_anonymous(self):
        """
        Récupération des groupes d'hôtes secondaires en tant qu'anonyme
        """

        # Récupération du groupe d'hôtes 'mhg' dans la base de données
        mainhostgroup = DBSession.query(SupItemGroup).filter(
            SupItemGroup.name == u'mhg').first()

        # Récupération des groupes d'hôtes par un
        # utilisateur anonyme : le contrôleur doit
        # retourner une erreur 401 (HTTPUnauthorized)
        self.app.post(
            '/rpc/hosttree?parent_id=%s' % (mainhostgroup.idgroup, ), {
            }, status=401)

    def test_get_host_groups_from_inexisting_main_group(self):
        """
        Récupération des groupes d'hôtes d'un groupe principal inexistant
        """

        # Récupération des groupes d'hôtes accessibles à l'utilisateur
        # 'manager' et appartenant à un groupe principal inexistant
        response = self.app.post(
            '/rpc/hosttree?parent_id=6666666', {
            }, extra_environ={'REMOTE_USER': 'manager'})
        json = response.json

        # On s'assure que la liste de groupes d'hôtes retournée est bien vide
        self.assertEqual(
            json, {'items': [], 'groups': []}
        )

    def test_get_hosts_when_allowed(self):
        """
        Récupération des hôtes avec les bons droits
        """

        # Récupération du groupe d'hôtes 'mhg' dans la base de données
        mainhostgroup = DBSession.query(SupItemGroup).filter(
            SupItemGroup.name == u'mhg').first()

        # Récupération du groupe d'hôtes 'hg1' dans la base de données
        hostgroup1 = DBSession.query(SupItemGroup).filter(
            SupItemGroup.name == u'hg1').first()

        # Récupération du groupe d'hôtes 'hg2' dans la base de données
        hostgroup2 = DBSession.query(SupItemGroup).filter(
            SupItemGroup.name == u'hg2').first()

        # Récupération de l'hôte 'host1' dans la base de données
        host1 = DBSession.query(Host).filter(
            Host.name == u'host1 éà').first()

        # Récupération de l'hôte 'host2' dans la base de données
        host2 = DBSession.query(Host).filter(
            Host.name == u'host2 éà').first()

        # Récupération des hôtes du groupe 'mhg'
        # accessibles à l'utilisateur 'manager'
        response = self.app.post(
            '/rpc/hosttree?parent_id=%s' % (mainhostgroup.idgroup, ), {
            }, extra_environ={'REMOTE_USER': 'manager'})
        json = response.json

        # On s'assure que la liste d'hôtes retournée contient bien 'host1'
        self.assertEqual(
            json, {
                'items': [
                    {
                        'id': host1.idhost,
                        'name': host1.name,
                        'type': 'item',
                    },
                ],
                'groups': [
                    {
                        'id': hostgroup1.idgroup,
                        'name': hostgroup1.name,
                        'type': 'group',
                    },
                    {
                        'id': hostgroup2.idgroup,
                        'name': hostgroup2.name,
                        'type': 'group',
                    },
                ],
            }
        )

        # Récupération des hôtes du groupe 'hg1'
        # accessibles à l'utilisateur 'manager'
        response = self.app.post(
            '/rpc/hosttree?parent_id=%s' % (hostgroup1.idgroup, ), {
            }, extra_environ={'REMOTE_USER': 'manager'})
        json = response.json

        # On s'assure que la liste d'hotes retournée contient bien 'host2'
        self.assertEqual(
            json, {
                'items': [
                    {
                        'id': host2.idhost,
                        'name': host2.name,
                        'type': 'item',
                    },
                ],
                'groups': [],
            }
        )

        # Récupération des hôtes du groupe 'mhg'
        # accessibles à l'utilisateur 'poweruser'
        response = self.app.post(
            '/rpc/hosttree?parent_id=%s' % (mainhostgroup.idgroup, ), {
            }, extra_environ={'REMOTE_USER': 'poweruser'})
        json = response.json

        # On s'assure que la liste d'hôtes retournée contient bien 'host1'
        self.assertEqual(
            json, {
                'items': [
                    {
                        'id': host1.idhost,
                        'name': host1.name,
                        'type': 'item',
                    },
                ],
                'groups': [
                    {
                        'id': hostgroup1.idgroup,
                        'name': hostgroup1.name,
                        'type': 'group',
                    },
                    {
                        'id': hostgroup2.idgroup,
                        'name': hostgroup2.name,
                        'type': 'group',
                    },
                ],
            }
        )

        # Récupération des hôtes du groupe 'hg1'
        # accessibles à l'utilisateur 'poweruser'
        response = self.app.post(
            '/rpc/hosttree?parent_id=%s' % (hostgroup1.idgroup, ), {
            }, extra_environ={'REMOTE_USER': 'poweruser'})
        json = response.json

        # On s'assure que la liste d'hotes retournée contient bien 'host2'
        self.assertEqual(
            json, {
                'items': [
                    {
                        'id': host2.idhost,
                        'name': host2.name,
                        'type': 'item',
                    },
                ],
                'groups': [],
            }
        )

        # Récupération des hôtes du groupe 'hg1'
        # accessibles à l'utilisateur 'user'
        response = self.app.post(
            '/rpc/hosttree?parent_id=%s' % (hostgroup1.idgroup, ), {
            }, extra_environ={'REMOTE_USER': 'user'})
        json = response.json

        # On s'assure que la liste d'hôtes retournée contient bien 'host2'
        self.assertEqual(
            json, {
                'items': [
                    {
                        'id': host2.idhost,
                        'name': host2.name,
                        'type': 'item',
                    },
                ],
                'groups': [],
            }
        )

    def test_get_hosts_when_not_allowed(self):
        """
        Récupération des hôtes sans les bons droits
        """

        # Récupération du groupe d'hôtes 'mhg' dans la base de données
        mainhostgroup = DBSession.query(SupItemGroup).filter(
            SupItemGroup.name == u'mhg').first()

        # Récupération du groupe d'hôtes
        # secondaire 'hg1' dans la base de données
        hostgroup1 = DBSession.query(SupItemGroup).filter(
            SupItemGroup.name == u'hg1').first()

        # Récupération du groupe d'hôtes
        # secondaire 'hg2' dans la base de données
        hostgroup2 = DBSession.query(SupItemGroup).filter(
            SupItemGroup.name == u'hg2').first()

        # Récupération des hôtes du groupe 'mhg'
        # accessibles à l'utilisateur 'user'
        response = self.app.post(
            '/rpc/hosttree?parent_id=%s' % (mainhostgroup.idgroup, ), {
            }, extra_environ={'REMOTE_USER': 'user'})
        json = response.json

        # On s'assure que la liste d'hôtes retournée est vide
        self.assertEqual(
            json, {
                'items': [],
                'groups': [
                    {
                        'name': hostgroup1.name,
                        'id': hostgroup1.idgroup,
                        'type': 'group',
                    },
                ],
            }
        )

        # Récupération des hôtes du groupe 'hg2'
        # accessibles à l'utilisateur 'user'
        response = self.app.post(
            '/rpc/hosttree?parent_id=%s' % (hostgroup2.idgroup, ), {
            }, extra_environ={'REMOTE_USER': 'user'})
        json = response.json

        # On s'assure que la liste d'hôtes retournée est vide
        self.assertEqual(
            json, {'items': [], 'groups': []}
        )

        # Récupération des hôtes du groupe 'mhg'
        # accessibles à l'utilisateur 'visitor'
        response = self.app.post(
            '/rpc/hosttree?parent_id=%s' % (mainhostgroup.idgroup, ), {
            }, extra_environ={'REMOTE_USER': 'visitor'})
        json = response.json

        # On s'assure que la liste d'hôtes retournée est vide
        self.assertEqual(
            json, {'items': [], 'groups': []}
        )

        # Récupération des hôtes du groupe 'hg1'
        # accessibles à l'utilisateur 'visitor'
        response = self.app.post(
            '/rpc/hosttree?parent_id=%s' % (hostgroup1.idgroup, ), {
            }, extra_environ={'REMOTE_USER': 'visitor'})
        json = response.json

        # On s'assure que la liste d'hôtes retournée est vide
        self.assertEqual(
            json, {'items': [], 'groups': []}
        )

    def test_get_hosts_as_anonymous(self):
        """
        Récupération des hôtes en tant qu'anonyme
        """

        # Récupération du groupe d'hôtes 'mhg' dans la base de données
        mainhostgroup = DBSession.query(SupItemGroup).filter(
            SupItemGroup.name == u'mhg').first()

        # Récupération des hôtes du groupe 'mhg' par
        # un utilisateur anonyme : le contrôleur doit
        # retourner une erreur 401 (HTTPUnauthorized)
        self.app.post(
            '/rpc/hosttree?parent_id=%s' % (mainhostgroup.idgroup, ), {
            }, status=401)

    def test_get_hosts_from_inexisting_secondary_group(self):
        """
        Récupération des hôtes d'un groupe secondaire inexistant
        """

        # Récupération des hôtes accessibles à l'utilisateur
        # 'manager' et appartenant à un groupe secondaire inexistant
        response = self.app.post(
            '/rpc/hosttree?parent_id=6666666', {
            }, extra_environ={'REMOTE_USER': 'manager'})
        json = response.json

        # On s'assure que la liste retournée est vide
        self.assertEqual(
            json, {'items': [], 'groups': []}
        )
