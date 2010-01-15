This file is for you to describe the vigigraph application. Typically
you would include information such as the information below:

Installation and Setup
======================

Install ``vigigraph`` using the setup.py script::

    $ cd vigigraph
    $ python setup.py install

Create the project database for any model classes defined::

    $ paster setup-app development.ini

Start the paste http server::

    $ paster serve development.ini

While developing you may want the server to reload after changes in package files (or its dependencies) are saved. This can be achieved easily by adding the --reload option::

    $ paster serve --reload development.ini

Then you are ready to go.


*****************
* Attention !!! *
*****************

vigilo2

- accès aux données nagios:
  * l'authentification a été modifiée dans les fichiers de configuration suivants
    (par rapport à ce qui a été décrit par Vincent sur nagios dans le Wiki)
    - /etc/nagios/cgi.cfg
      * modification de use_authentication -> 0
    - /etc/httpd/conf/webapps.d/nagios.conf
      * suppression des lignes Auth* et Require valid-user dans <Directory /usr/lib/nagios/cgi>

- rafraichissement graphes
  * la réalisation des IHM en javascript s'effectue avec qooxdoo. La version utilisée correspond
    à celle utilisée sur Vigilo1, soit la version 0.7. Dans cette version, les ToggleButton n'existent pas.
    De plus, il n'est pas prévu de migrer sur une version ultérieure de qooxdoo (mais même au contraire de 
    migrer vers motools)
    -> il ya donc un problème sur le rafraichissement des graphes pour indiquer l'état courant: bouton enfoncé ou relaché !

- search et select
  * dans selectHostAndService de rpc.py  
    - service : positionné à None 
    - données renvoyées -> première occurence