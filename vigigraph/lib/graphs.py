# -*- coding: utf-8 -*-
"""Functions for graphs"""

from tg import config

import string

from time import gmtime, strftime
from datetime import datetime


def graphsList(**kwargs):
    """
    Page liste des graphes
        
    @param **kwargs : arguments nommes
    @type **kwargs : dict

    """
    graphslist = []
    format = "%d-%m-%Y %H:%M"
    for key in kwargs:
        # titre
        title = "Inconnu"
        graph = ""
        server = ""
        lca = kwargs[key].split("?")
        if len(lca) == 2:
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
        graph['sts'] = _(strftime(format, gmtime(v)))
        v = int(start) + int(duration)
        graph['ets'] = _(strftime(format, gmtime(v)))
        graph['src'] = urllib2.unquote(kwargs[key])
        graphslist.append(graph)
    return graphslist

def tempoDelayRefresh():
    """
    Lecture de la temporisation pour le rafraichissement automatique
    dans le fichier de configuration development.ini
    (valeur par defaut = 30000)

    @return : valeur de temporisation (en millisecondes)
    @rtype : C{str}
    """

    delay = config.get('delay_refresh')
    delay = string.strip(delay)

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

def getExportFileName(host, indicator_f, start, end):
    """
    Determination nom fichier pour export
    -> <hote>_<indicator_f>_<date_heure_debut>_<date_heure_fin>
    avec format <date_heure_...> = AAMMJJ-hhmmss

    @param host : hôte
    @type host : C{str}
    @param graph : graphe
    @type graph : C{str}
    @param indicator_f : indicateur graphe ( nom du graphe ou d un des indicateurs)
    @type indicator_f : C{str}
    @param start : date-heure de debut des donnees
    @type start : C{str}

    @return : nom du fichier
    @rtype : C{str}
    """

    # plage temps sous forme texte
    format = '%Y%m%d-%H%M%S'

    dt = datetime.utcfromtimestamp(int(start))
    str_start = dt.strftime(format)

    dt = datetime.utcfromtimestamp(int(end))
    str_end = dt.strftime(format)

    # nom fichier
    filename = '%s_%s_%s_%s' % (host, indicator_f, str_start, str_end)

    # remplacement caracteres particuliers
    lc = [' ', '|', '/', '\\', ':', '?', '*', '<', '>', '"']
    for c in lc:
        filename = filename.replace(c, "_")

    # extension
    filename += ".csv"

    return filename

def setExportFile(writer, dict_values, dict_indicators, sep_value):
    """
    Ecriture des donnees sous forme texte dans le fichier d export
    (les donnees se rapportent aux indicateurs passes en parametre)

    @param writer : gestion csv pour lecture/ecriture
    @type writer : csv.DictWriter (voir Python)
    @param dict_values : valeurs
    @type dict_values : dict
    @param dict_indicators : indicateurs
    @type dict_indicators : dict
    @param sep_value : separateur partie entiere - partie decimale
    @type sep_value : C{str}

    @return : resultat generation (pas de valeurs -> false, sinon true)
    @rtype : booleen
    """

    # format pour valeur temps
    format = '%Y/%m/%d %H:%M:%S'

    result = (dict_values is not None or dict_values != "{}")
    if result:
        # parcours valeurs
        for key_tv in dict_values:
            tv = dict_values[key_tv]

            # generation ligne
            dict_data = {}
            for key_i in dict_indicators:
                iv = dict_indicators[key_i]
                v = str(tv[key_i])

                # temps sous forme texte
                if iv == 'TimeStamp':
                    dt = datetime.utcfromtimestamp(int(v))
                    v = dt.strftime(format)

                # separateur dans valeur -> remplacement . par ,
                v = v.replace(".", sep_value)

                dict_data[iv] = v

            writer.writerow(dict_data)

    return result
