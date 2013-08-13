Annexes
=======

.. include:: ../../turbogears/doc/glossaire.rst

Liste des URL
-------------

Le tableau suivant recense les URL disponibles dans VigiGraph.
Les paramètres obligatoires de l'URL sont indiqués en gras (dans la colonne du milieu).

..  list-table:: Liste des URL
    :widths: 20 30 50
    :header-rows: 1

    * - Fonctionnalité
      - URL
      - Détail
    * - Interface principale
      - <prefix_url>/
      - L'interface principale d'accès à VigiGraph s'affiche.
    * - Recherche d'un hôte ou d'un ensemble d'hôtes.
      - <prefixe_url>/rpc/searchHost?**query**=intitulé_query>
      - VigiGraph affiche l'ensemble des hôtes dont le nom contient
        <intitulé_query>, sans distinction majuscules/minuscules.
    * - Image d'un graphe au format PNG.
      - <prefixe_url>/rpc/getImage_png?**host**=<intitulé_host>&**graph**=<intiulé_graph>&start=<intitulé_start>&duration=<intitulé_duration>
      - Paramètres :
        - <intitulé_host> = serveur cible
        - <intitulé_graph> = graphe
        - <intitulé_start> = date-heure de début du graph
        - <intitulé_duration> = durée du graphe
    * - Export CSV.
      - <prefixe_url>/rpc/exportCSV?**host**=<intitulé_host>&**indicator**=<intitulé_indicator>
      -

        Paramètres :

        - <intitulé_host> = serveur cible
        - <intitulé_indicator> = indicateur associé à un graphe

        Particularités :

        - Pour un export sur l'ensemble des indicateurs, <intitulé_indicator>
          est renseigné avec la chaîne « all».

        Exemple :
        localhost:8082/rpc/exportCSV?host=par.linux0&indicator=IO%20Reads

Les intitulés du type ``...`` permettent le paramétrage de l'URL.
Ils sont de type chaîne de caractères.

.. vim: set tw=79 :
