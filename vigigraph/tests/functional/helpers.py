# -*- coding: utf-8 -*-
# Copyright (C) 2011-2015 CS-SI
# License: GNU GPL v2 <http://www.gnu.org/licenses/gpl-2.0.html>

from vigilo.models.tables import Permission

from vigilo.models.demo.functions import add_supitemgroup, \
    add_host, add_host2group, add_usergroup, add_user, \
    add_supitemgrouppermission, add_usergroup_permission

from vigilo.models.demo.functions import add_graph, \
    add_graphgroup, add_graph2group, add_perfdatasource, \
    add_perfdatasource2graph, add_vigiloserver, add_application


def populateDB():
    """
    Peuple la base de données en ajoutant :
     - 3 groupes d'hôtes ;
     - 3 hôtes ;
     - 3 utilisateurs.
    Les objets construits respectent les matrices suivantes.


    Matrice des utilisateurs et groupes d'utilisateurs :

    +-------------------+-----------+---------------+-------+-----------+
    | util. \ groupe    | managers  | powerusers    | users | visitor   |
    +===================+===========+===============+=======+===========+
    | manager           |     X     |               |       |           |
    +-------------------+-----------+---------------+-------+-----------+
    | poweruser         |           |       X       |       |           |
    +-------------------+-----------+---------------+-------+-----------+
    | user              |           |               |   X   |           |
    +-------------------+-----------+---------------+-------+-----------+
    | visitor           |           |               |       |     X     |
    +-------------------+-----------+---------------+-------+-----------+


    Matrice des groupes d'utilisateurs et des droits
    sur les groupes d'objets supervisés :

    +---------------------------+-----------+-----------+-----------+
    | usergroup \ supitemgroup  |    mhg    |    hg1    |   hg2     |
    |                           |  (host1)  |  (host2)  | (host3)   |
    +===========================+===========+===========+===========+
    | managers                  |    /      |    /      |    /      |
    +---------------------------+-----------+-----------+-----------+
    | powerusers                |    X      |    /      |    /      |
    +---------------------------+-----------+-----------+-----------+
    | users                     |           |    X      |           |
    +---------------------------+-----------+-----------+-----------+
    | visitors                  |           |           |           |
    +---------------------------+-----------+-----------+-----------+
    (X = accès explicite, / = accès implicite)


    @return: Tuple contenant les trois hôtes créés.
    @rtype:  C{tuple} of C{vigilo.models.tables.Host}
    """

    # Ajout d'un groupe d'hôtes principal
    mainhostgroup = add_supitemgroup(u'mhg', None)

    # Ajout d'un premier groupe d'hôtes de second niveau
    hostgroup1 = add_supitemgroup(u'hg1', mainhostgroup)

    # Ajout d'un second groupe d'hôtes de second niveau
    hostgroup2 = add_supitemgroup(u'hg2', mainhostgroup)

    # Ajout de trois hôtes
    # On ajoute des caractères spéciaux pour détecter les
    # conversions implicites Unicode <-> ASCII (et leurs erreurs).
    host1 = add_host(u'host1 éà')
    host2 = add_host(u'host2 éà')
    host3 = add_host(u'host3 éà')

    # Ajout du premier hôte dans le groupe d'hôtes principal.
    add_host2group(host1, mainhostgroup)
    # Ajout du deuxième hôte dans le premier
    # groupe d'hôtes de second niveau.
    add_host2group(host2, hostgroup1)
    # Ajout du troisième hôte dans le second
    # groupe d'hôtes de second niveau.
    add_host2group(host3, hostgroup2)

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

    return (host1, host2, host3)


def addGraphs(host1, host2, host3):
    """
    Ajout d'un graphe pour chacun des trois hôtes passés en paramètres.

    @param host1: Premier hôte.
    @type  host1: C{vigilo.models.tables.Host}
    @param host2: Deuxième hôte.
    @type  host2: C{vigilo.models.tables.Host}
    @param host3: Troisième hôte.
    @type  host3: C{vigilo.models.tables.Host}
    """

    # Ajout d'un serveur de supervision
    vigiloserver = add_vigiloserver(u'locahost')

    # Ajout d'une application 'vigirrd'
    add_application(u"vigirrd")

    # Ajout de trois graphes
    # On ajoute des caractères spéciaux pour détecter les
    # conversions implicites Unicode <-> ASCII (et leurs erreurs).
    graph1 = add_graph(u"graph1 éà")
    graph2 = add_graph(u"graph2 éà")
    graph3 = add_graph(u"graph3 éà")

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
