# -*- coding: utf-8 -*-
"""Functions for graphs"""

from tg import config

import urllib
import urllib2
from pylons.i18n import ugettext as _

from time import gmtime, strftime
from datetime import datetime


def graphsList(**kwargs):
    """
    Page liste des graphes
        
    @param kwargs : arguments nommes
    @type kwargs : dict
    """
    graphslist = []
    
    if kwargs is not None:
        # TRANSLATORS: Format Python de date/heure, lisible par un humain.
        format = _("%a, %d %b %Y %H:%M:%S")
        for key in kwargs:
            # titre
            title = _("Unknown")
            graph = ""
            server = ""
            # recherche arguments (apres ?) -> cle1=valeur1&cle2=valeur2&...
            lca = kwargs[key].split("?")
            if len(lca) == 2:
                # analyse de chacun des arguments -> cle=valeur
                largs = lca[1].split("&")
                for arg in largs:
                    larg = arg.split("=")
                    if len(larg) == 2:
                        if larg[0] == "server":
                            server = larg[1]
                        elif larg[0] == "graphtemplate":
                            graph = larg[1]
                        elif larg[0] == "start":
                            start = larg[1]
                        elif larg[0] == "duration":
                            duration = larg[1]
            if graph != "" or server != "":
                title = "'%s' Graph for host %s" % \
                  (urllib.unquote_plus(graph), server)
            graph = {}
            graph['title'] = title
            v = int(start)
            graph['sts'] = strftime(format, gmtime(v))
            v = int(start) + int(duration)
            graph['ets'] = strftime(format, gmtime(v))
            graph['src'] = urllib2.unquote(kwargs[key])
            graphslist.append(graph)

    return graphslist

def tempoDelayRefresh():
    """
    Lecture de la temporisation pour le rafraichissement automatique
    dans le fichier de configuration development.ini
    valeur exprimee en millisecondes, valeur par defaut = 30000

    @return: valeur de temporisation
    @rtype: C{str}
    """

    delay = config.get('delay_refresh')
    delay = delay.strip()

    b_evaluate = False
    if delay == '':
        b_evaluate = True
    else:
        if delay.isalnum():
            delay_l = int(delay)
            b_evaluate = (delay_l <= 0)
        else:
            b_evaluate = True

    if b_evaluate:
        delay = '30000'

    return delay

