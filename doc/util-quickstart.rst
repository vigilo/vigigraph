Démarrage rapide
================
VigiGraph fournit une interface graphique accessible depuis un navigateur Web.
La configuration par défaut est suffisante pour un démarrage rapide.

Accès à l'interface
-------------------
L'utilisation de VigiGraph se fait simplement en accédant, via votre
navigateur, à l'adresse indiquée par votre administrateur. Par exemple :
http://supervision.example.com/vigigraph/.

Authentification
----------------

..  note::
    Dans le cas où un mécanisme d'authentification externe a été défini par
    votre administrateur, il se peut qu'aucune authentification ne vous soit
    demandée, même lorsqu'il s'agit de votre première connexion. Le reste de ce
    chapitre décrit le cas où une authentification interne a lieu et ne
    s'applique donc pas au cas de figure cité ci-dessus. Contactez votre
    administrateur pour plus d'information sur la configuration utilisée.


Si vous ne vous êtes jamais connecté sur VigiGraph ou si vous n'êtes plus
authentifié, le formulaire d'authentification de la figure suivante s'affiche:

    ..  figure:: img/login_form.png

        Écran d'authentification.


Selon le compte utilisateur auquel vous vous connecterez, vous disposerez d'un
accès à plus ou moins d'hôtes et de services (et donc d'informations).
Les données d'authentification demandées ici vous ont normalement été
transmises par votre administrateur.

- Saisir les données d'authentification en renseignant les zones de saisie
  « Identifiant » et « Mot de passe ».
- Valider la saisie en cliquant sur le bouton « Connexion » (entouré en rouge
  sur la figure suivante).


..  figure:: img/login_form_connection.png

    Bouton de validation des données d'authentification.


En cas de succès, la page d'accueil s'affiche. Sinon, le formulaire
d'authentification s'affiche à nouveau, avec un message précisant la nature de
l'erreur:

    ..  figure:: img/login_failure.png

        Formulaire après un échec de l'authentification.

.. vim: set tw=79 :
