VigiGraph
=========

VigiBoard est l'interface web de Vigilo_ orientée métrologie. On peut y
visualiser les graphes de performance des différents indicateurs collectés
sur le parc supervisé.

Pour les détails du fonctionnement de VigiGraph, se reporter à la
`documentation officielle`_.


Dépendances
-----------
Vigilo nécessite une version de Python supérieure ou égale à 2.5. Le chemin de
l'exécutable python peut être passé en paramètre du ``make install`` de la
façon suivante::

    make install PYTHON=/usr/bin/python2.6

VigiGraph a besoin des modules Python suivants :

- setuptools (ou distribute)
- vigilo-turbogears


Installation
------------
L'installation se fait par la commande ``make install`` (à exécuter en
``root``).

Après avoir configuré VigiGraph dans le fichier
``/etc/vigilo/vigigraph/settings.ini``, il faut initialiser la base de données
par la commande ``vigilo-updatedb``. Enfin, il faut redémarrer Apache pour
qu'il prenne en compte le nouveau fichier de configuration de VigiGraph.

L'accès à l'interface se fait avec les identifiants suivants :

 - login : ``manager``
 - mot de passe : ``iddad``


License
-------
VigiGraph est sous licence `GPL v2`_.


.. _documentation officielle: Vigilo_
.. _Vigilo: http://www.projet-vigilo.org
.. _GPL v2: http://www.gnu.org/licenses/gpl-2.0.html

.. vim: set syntax=rst fileencoding=utf-8 tw=78 :
