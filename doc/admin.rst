**********************
Guide d'administration
**********************


Installation
============

Prérequis logiciels
-------------------
Afin de pouvoir faire fonctionner VigiGraph, l'installation préalable
des logiciels suivants est requise :

- python (>= 2.5), sur la machine où VigiGraph est installé
- Apache (>= 2.2.0), sur la machine où VigiGraph est installé
- apache-mod_wsgi (>= 2.3), sur la machine où VigiGraph est installé
- postgresql-server (version 8.3), éventuellement sur une machine distante

Reportez-vous aux manuels de ces différents logiciels pour savoir
comment procéder à leur installation sur votre machine.
VigiGraph requiert également la présence de plusieurs dépendances Python.
Ces dépendances seront automatiquement installées en même temps que le
paquet de VigiGraph.

Installation du paquet RPM
--------------------------
L'installation de l'application se fait en installant simplement
le paquet RPM « vigilo-vigigraph ». La procédure exacte d'installation
dépend du gestionnaire de paquets utilisé.
Les instructions suivantes décrivent la procédure pour les gestionnaires
de paquets RPM les plus fréquemment rencontrés.

Installation à l'aide de urpmi ::

    urpmi vigilo-vigigraph

Installation à l'aide de yum ::

    yum install vigilo-vigigraph


Démarrage et arrêt de VigiGraph
===============================
VigiGraph fonctionne comme un site web standard. À ce titre, il n'est pas
nécessaire d'exécuter une commande spécifique pour démarrer VigiGraph,
dès lors que le serveur web qui l'héberge a été lancé, à l'aide de la
commande ::

    service httpd start

De la même manière, il n'y a pas de commande spécifique pour arrêter VigiGraph.
L'application est arrêtée en même temps que le serveur web,
à l'aide de la commande :
service httpd stop


Configuration de VigiGraph
==========================
La configuration initialement fournie avec VigiGraph est très rudimentaire.
Elle est décomposée en deux fichiers :

-   le fichier « settings.ini » d'une part, qui contient la majorité
    des options de configuration ;
-   et le fichier « app_cfg.py » qui contient des options de configuration
    plus complexes, nécessitant l'utilisation d'un langage
    plus complet (Python).

Ce chapitre a pour but de présenter les différentes options de configuration
disponibles afin de configurer VigiGraph en fonction de vos besoins.
Les chapitres  à  reprennent l'ordre de la configuration utilisé dans
le fichier « settings.ini » de l'application. Toutes les options de
configuration citées ici se trouvent sous la section [app:main] du
fichier « settings.ini ».
Enfin, le chapitre  donne des informations quant à la méthode utilisée
pour intégrer VigiGraph sur un serveur web de type Apache, grâce au
module mod_wsgi.
La configuration de la journalisation des événements se fait également
au travers du fichier « settings.ini ». Néanmoins, comme ce procédé est commun
aux différents composants de Vigilo, celui-ci fait l'objet d'une documentation
séparée dans le document *Vigilo – Journaux d'événements*.

Configuration de la base de données
-----------------------------------
Pour fonctionner, VigiGraph nécessite qu'une base de données soit accessible.
Ce chapitre décrit les options de configuration se rapportant à la base de
données.

Connexion à la base de données
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
La configuration de la connexion à la base de base de données se fait
en modifiant la valeur de la clé « sqlalchemy.url » sous la section [app:main].
Cette clé contient une URL qui contient tous les paramètres nécessaires
pour pouvoir se connecter à la base de données.
Le format de cette URL est le suivant ::

    sgbd://nom_utilisateur:mot_de_passe@adresse_serveur:port_serveur/nom_base_de_donnees

Le champ « :port_serveur » est optionnel et peut être omis si vous utilisez
le port par défaut d'installation du SGBD choisi.

Par exemple, voici la valeur correspondant à une installation mono-poste
par défaut de VigiGraph :

    postgresql://vigilo:vigilo@localhost/vigilo

..  warning::
    À l'heure actuelle, seul PostgreSQL a fait l'objet de tests intensifs.
    D'autres SGBD peuvent également fonctionner, mais aucun support ne sera
    fourni pour ces SGBD.

Choix d'un préfixe pour les tables de la base de données
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Vous pouvez choisir un préfixe qui sera appliqué aux noms des tables
de la base de données en indiquant ce préfixe dans la clé « db_basename »
sous la section [app:main]. Par défaut, la configuration suppose
que les tables de Vigilo porteront le préfixe « vigilo_ ».

Si vous optez pour l'utilisation d'un préfixe, veillez à ce que celui-ci
ne contiennent que des caractères alpha-numériques (a-zA-Z0-9)
ou le caractère « _ ».

Si vous décidez de ne pas utiliser de préfixe, veillez à ce que
la base de données configurée ne soit utilisée que par Vigilo,
au risque d'un conflit avec une éventuelle application tierce.

Optimisation de la couche d'abstraction
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
L'option « sqlalchemy.echo » permet de forcer l'affichage des requêtes SQL.
En production, cette valeur doit être positionnée à « False ».
Elle est redondante avec la configuration des journaux d'événements
(voir le document intitulé Vigilo - Journaux d'événements pour plus
d'information).

L'option « sqlalchemy.echo_pool » permet d'activer le mode de débogage
du gestionnaire de connexions à la base de données. De même que pour
l'option « sqlalchemy.echo » ci-dessus, elle doit être positionnée
à « False » en production.

L'option « sqlalchemy.pool_recycle » permet de définir la durée
après laquelle une connexion est « recyclée » (recréée).

L'option « sqlalchemy.pool_size » permet de configurer le nombre
de connexions gérées simultanément par le gestionnaire de connexions
à la base de données. La valeur recommandée est 20.

L'option « sqlalchemy.max_overflow » permet de limiter le nombre maximal
de connexions simultanées à la base de données. La limite correspond
à la somme de « sqlalchemy.pool_size » et « sqlalchemy.max_overflow ».
Une valeur de 100 convient généralement.

La documentation d'API de SQLAlchemy (la bibliothèque d'abstraction
de la base de données utilisée par Vigilo) donne quelques informations
supplémentaires sur le rôle de ces différents paramètres.
Cette documentation est accessible à l'adresse
http://www.sqlalchemy.org/docs/05/reference/sqlalchemy/pooling.html.

Configuration des éléments de sécurité
--------------------------------------
Ce chapitre décrit les options relatives à la gestion des données
de sécurité (clés de chiffrements, etc.) utilisées par VigiGraph.

Choix de la méthode de hachage des mots de passe
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Lorsque l'authentification de Vigilo se base sur les comptes contenus dans
la base de données, les mots de passe des utilisateurs sont stockés sous
forme hachée afin de rendre plus difficile le cassage de ces mots de passe.

La méthode de hachage sélectionnée peut être configurée en modifiant
la valeur de la clé « password_hashing_function » sous la section [app:main].
Les méthodes de hachage disponibles sont variées.

Les fonctions de hachage suivantes sont notamment disponibles :

- md5
- sha1
- sha224
- sha256
- sha384
- sha512

Des fonctions supplémentaires peuvent être disponibles en fonction
de votre installation de Python.

..  warning::
    En cas d'absence d'une valeur pour cette option ou si la fonction de
    hachage indiquée n'existe pas, les mots de passe sont stockés en clair.
    Vérifiez donc la valeur indiquée.

..  warning::
    Cette option ne doit être modifiée qu'au moment de l'installation.
    Si vous modifiez la méthode utilisée ultérieurement, les comptes
    précédemment enregistrés ne seront plus utilisables. En particulier,
    le compte d'administration créé par défaut.

Clé de chiffrement / déchiffrement des sessions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Afin de ne pas dévoiler certains paramètres associés à un utilisateur,
le fichier de session qui contient ces paramètres est chiffré à l'aide
d'une clé symétrique, utilisée à la fois pour le chiffrement
et le déchiffrement des sessions de tous les utilisateurs de VigiGraph.

L'option « beaker.session.secret » permet de choisir la clé utilisée
pour chiffrer et déchiffrer le contenu des sessions. Cette clé peut être
la même que celle configurée pour le chiffrement / déchiffrement
des cookies (voir le chapitre ), mais ceci est déconseillé
afin d'éviter que la compromission de l'une des deux clés
n'entraine la compromission de l'autre.

De la même manière, vous pouvez configurer les autres interfaces graphiques
de Vigilo pour utiliser les mêmes clés, ou opter de préférence pour des clés
différentes (là encore, pour éviter la propagation d'une compromission).

Clé de chiffrement / déchiffrement des cookies
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
L'association entre un utilisateur et sa session se fait à l'aide d'un cookie
de session enregistré sur le navigateur de l'utilisateur.

De la même manière que les sessions sont chiffrées afin de garantir
la confidentialité de leur contenu, le cookie de session est également
chiffré afin de protéger son contenu.

L'option « sa_auth.cookie_secret » permet de choisir la clé utilisée
pour chiffrer et déchiffrer le contenu du cookie. Cette clé peut être la même
que celle configurée pour le chiffrement / déchiffrement des sessions
(voir le chapitre ), mais ceci est déconseillé afin d'éviter que la
compromission de l'une des deux clés n'entraine la compromission de l'autre.

De la même manière, vous pouvez configurer les autres interfaces graphiques
de Vigilo pour utiliser les mêmes clés, ou opter de préférence pour des
clés différentes (là encore, pour éviter la propagation d'une compromission).

Utilisation d'un mécanisme d'authentification externe
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Pour utiliser un mécanisme d'authentification externe (par exemple : Kerberos),
définissez la clé « external_auth » à « True » sous la section [app:main].
Dans ce mode, Vigilo ne tente pas d'authentifier l'utilisateur par rapport
aux comptes contenus dans sa base de données, mais utilise uniquement
le nom d'utilisateur transmis par la source d'authentification externe.

Le nom d'utilisateur peut être transmis de plusieurs manières,
par exemple sous la forme d'une variable d'environnement.

..  warning::
    N'utilisez ce mode de fonctionnement que si vous comprenez bien les
    risques associés. En particulier, le fait qu'aucun mot de passe ne sera
    demandé à l'utilisateur pour confirmer son identité.

Emplacement de la configuration des authentifications / autorisations
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
La directive « auth.config » de la section [app:main] permet d'indiquer
l'emplacement du fichier contenant la configuration de la couche
d'authentification / autorisation de Vigilo.

Il n'est généralement pas nécessaire de modifier cette valeur.
La configuration de cette couche d'abstraction est détaillée
dans le document *Vigilo – Authentification et autorisation*.

Configuration de l'interface
----------------------------
Ce chapitre décrit les options qui modifient l'apparence de l'interface
graphique de VigiGraph.

Langue par défaut de VigiGraph
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Au sein de son interface, VigiGraph tente de s'adapter au navigateur
de l'utilisateur pour afficher les pages dans sa langue.

Toutefois, si l'utilisateur n'a pas paramétré sa langue ou bien si
aucune traduction n'est disponible qui soit en accord avec les paramètres
du navigateur de l'utilisateur, une langue par défaut est utilisée (dans
l'installation par défaut de VigiGraph, cette langue est le Français « fr »).

Vous pouvez modifier la langue utilisée par défaut en changeant la valeur
de la clé « lang » sous la section [app:main]. La valeur de cette clé
est le code de la langue à utiliser, sur deux caractères et en minuscules
(format ISO 3166-1 « alpha 2 »). Exemples de codes valides : fr, en, de, …

La liste complète des codes possibles est disponible sur
http://fr.wikipedia.org/wiki/ISO_3166-1. La langue retenue
doit être disponible parmi les traductions fournies avec VigiGraph.

Emplacement de la documentation en ligne
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Il est possible d'ajouter un lien dans l'interface graphique qui redirige
l'utilisateur vers la documentation en ligne de l'application.
Ceci se fait en assignant une URL à l'option « help_link ».

Si cette option est renseignée, une icône en forme de bouée de sauvetage
.. image:: img/help_icon.png

apparaît dans l'interface graphique qui permet à l'utilisateur d'accéder
à l'URL indiquée.

Délai de rafraîchissement automatique
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Les veilleurs ont la possibilité d'activer un rafraîchissement automatique
des graphes. L'option « refresh_delay » permet de choisir le délai,
en secondes, entre deux rafraîchissements automatiques d'un graphe.

Configuration du lien d'accueil
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Vous avez la possibilité de rediriger l'utilisateur vers une page
de votre choix lorsque celui-ci clique sur le logo de Vigilo
.. image:: img/vigilo.png

dans l'interface graphique de VigiGraph.
Ceci se fait en modifiant l'URL donnée par l'option « logo_link ».

Configuration des serveurs mandataires
--------------------------------------
VigiGraph permet d'accéder à la page d'état Nagios d'un hôte ou d'un service,
et ce malgré le fait que ces hôtes/services sont supervisés par des serveurs
Nagios différents. De même, il est capable d'afficher des graphes de métrologie
en interrogeant le serveur VigiRRD qui gère un hôte donné.
Ceci est rendu possible par l'existence d'un serveur mandataire (proxy) au sein
de Vigilo qui relaye les requêtes au serveur Nagios ou VigiRRD adéquat.
Le chapitre  présente tout d'abord les options communes à tous les types
de serveurs mandataires de Vigilo. Puis, le chapitre  détaille les options
spécifiques au serveur mandataire pour Nagios intégré dans VigiGraph.
Enfin, le chapitre  détaille les options spécifiques au serveur mandataire
pour VigiRRD, dont la configuration est très proche de celle du serveur
mandataire pour Nagios.

Options communes à tous les serveurs mandataires de Vigilo
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Les options communes à tous les serveurs mandataires de Vigilo
concernent l'authentification auprès d'un serveur mandataire intermédiaire.

Elles sont au nombre de trois :

-   « app_proxy_auth_method » indique la méthode d'authentification
    à utiliser et peut valoir « basic » ou « digest » ,

-   « app_proxy_auth_username » indique le nom d'utilisateur à utiliser
    pour se connecter au serveur mandataire intermédiaire ,

-   « app_proxy_auth_password » indique le mot de passe associé
    à ce nom d'utilisateur.

Ces trois options doivent être renseignées pour que l'authentification
auprès du serveur mandataire intermédiaire soit effective.

Options spécifiques au serveur mandataire Nagios
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
L'option « app_path.nagios » indique l'emplacement de l'installation
de Nagios sur le serveur web distant, à partir de la racine du serveur web.
Généralement, il s'agit de « /nagios/ » (emplacement par défaut lors
d'une nouvelle installation de l'interface graphique CGI de Nagios).

L'option « app_scheme.nagios » indique le protocole à utiliser
pour communiquer avec le serveur web distant.
Les protocoles supportés sont « http » et « https ».

L'option « app_port.nagios » permet d'indiquer le port à utiliser
pour se connecter, dans le cas où il ne s'agit pas du port standard.
Par défaut, le serveur mandataire Nagios utilise le port standard associé
au protocole donné par « app_scheme.nagios » (80 pour HTTP, 443 pour HTTPS).

L'option « app_redirect.nagios » permet de modifier le comportement
du serveur mandataire. Lorsque cette option vaut « True »,
le serveur mandataire agit comme un simple redirecteur de requêtes.
Dans ce mode, les options d'authentification liées au serveur mandataire
sont ignorées. Ce mode de fonctionnement est utile afin de tester
la configuration mais n'est pas recommandé en production.

Les options « app_auth_method.nagios », « app_auth_username.nagios »
et « app_auth_password.nagios » permettent d'indiquer la méthode
d'authentification, le nom d'utilisateur et le mot de passe pour accéder
à l'interface CGI de Nagios.
Ces options sont similaires à celles décrites au chapitre .

Options spécifiques au serveur mandataire VigiRRD
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Les options de configuration pour le serveur mandataire VigiRRD
sont exactement les mêmes que pour le serveur mandataire Nagios
présenté au chapitre , en remplaçant simplement le suffixe « .nagios »
par « .vigirrd ».

Configuration des sessions
--------------------------
Chaque fois qu'un utilisateur se connecte à VigiGraph, un fichier de session
est créé permettant de sauvegarder certaines préférences de cet utilisateur
(par exemple, le thème de l'application, la taille de la police de caractères,
etc.). Ce chapitre décrit les options relatives à la gestion des sessions.

Emplacement des fichiers de session
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Le dossier dans lequel les fichiers de session seront stockés est indiqué
par l'option « cache_dir ».

Nom du cookie de session
^^^^^^^^^^^^^^^^^^^^^^^^
Afin d'associer un utilisateur au fichier de session qui lui correspond,
un cookie de session est créé sur le navigateur de l'utilisateur.

L'option « beaker.session.key » permet de choisir le nom du cookie créé.
Le nom doit être composé de caractères alphanumériques (a-zA-Z0-9)
et commencer par une lettre (a-zA-Z).

Intégration de VigiGraph avec Apache / mod_wsgi
===============================================
VigiGraph a été testé avec le serveur libre Apache. L'application utilise
en outre le module Apache « mod_wsgi » pour communiquer avec le serveur.
Ce module implémente un modèle de communication basé sur l'interface WSGI.
Le reste de ce chapitre décrit la configuration utilisée pour réaliser
cette intégration.

Fichier de configuration pour Apache
------------------------------------
Le fichier de configuration pour l'intégration de VigiGraph dans Apache
se trouve généralement dans /etc/vigilo/vigigraph/vigigraph.conf
(un lien symbolique vers ce fichier est créé dans le dossier de configuration
d'Apache, généralement dans /etc/httpd/conf.d/vigigraph.conf).

En général, il n'est pas nécessaire de modifier le contenu de ce fichier.
Ce chapitre vise toutefois à fournir quelques informations sur
le fonctionnement de ce fichier, afin de permettre d'éventuelles
personnalisations de ce comportement.

Ce fichier tente tout d'abord de charger le module « mod_wsgi »
(directive LoadModule) puis ajoute les directives de configuration
nécessaires à Apache pour faire fonctionner VigiGraph,
reprises partiellement ci-dessous ::

    WSGIRestrictStdout off
    WSGIPassAuthorization on
    WSGIDaemonProcess vigigraph user=apache group=apache threads=2
    WSGIScriptAlias /vigilo/vigigraph "/etc/vigilo/vigigraph/vigigraph.wsgi"

    KeepAlive Off

    <Directory "/etc/vigilo/vigigraph/">
    <Files "vigigraph.wsgi">
    WSGIProcessGroup vigigraph
    WSGIApplicationGroup %{GLOBAL}

    Order deny,allow
    Allow from all
    </Files>
    </Directory>

L'option WSGIRestrictStdout est positionnée à « off » afin d'éviter
qu'Apache ne tue le processus de l'application lorsque des données
sont envoyées sur la sortie standard. Ceci permet de récupérer
les erreurs critiques pouvant être émises par l'application.
Ces erreurs apparaissent alors dans le journal des événements
d'Apache (configuré par la directive error_log).

L'option WSGIPassAuthorization positionnée à « on » indique à Apache
et mod_wsgi que les informations d'authentification éventuellement
transmises par l'utilisateur doivent être transmises à VigiGraph.
En effet, Vigilo utilise son propre mécanisme de gestion de
l'authentification et des autorisations (voir la documentation
intitulée Vigilo - Authentification et autorisation) et utilise
donc ces informations.

L'option WSGIDaemonProcess permet de créer un groupe de processus
affecté au traitement des requêtes HTTP destinées à VigiGraph.
Il permet d'utiliser un nom d'utilisateur et un groupe prédéfini
(afin de réduire les privilèges nécessaires), ainsi que le nombre
de processus légers à utiliser pour traiter les requêtes (ici, 2).

L'option WSGIScriptAlias indique l'emplacement à partir duquel
VigiGraph sera accessible (ici, http://example.com/vigilo/vigigraph
si le serveur Apache est configuré pour le domaine « example.com »)
et l'emplacement du script WSGI nécessaire au lancement de l'application
(voir le chapitre ).

L'option KeepAlive positionnée à « off » est nécessaire afin de contourner
un problème dans le module « mod_wsgi » d'Apache.

Les autres options permettent d'exécuter le script WSGI de VigiGraph
à l'aide du groupe de processus défini précédemment.

La liste complète des directives de configuration supportées
par le module « mod_wsgi » d'Apache est disponible à l'adresse
http://code.google.com/p/modwsgi/wiki/ConfigurationDirectives.

Script WSGI de VigiGraph
------------------------
Le script WSGI de VigiGraph est un script Python très simple qui a pour but
de démarrer l'exécution de VigiGraph à partir du fichier de configuration
associé (/etc/vigilo/vigigraph/settings.ini).

Vous n'avez généralement pas besoin de modifier son contenu,
sauf éventuellement pour adapter l'emplacement du fichier de configuration
en fonction de votre installation.

Annexes
=======

.. include:: ../../turbogears/doc/glossaire.rst

.. vim: set tw=79 :
