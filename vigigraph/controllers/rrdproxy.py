# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4: 
"""Gestion RRD par proxy"""

import urllib
import urllib2
from HTMLParser import HTMLParser
from pylons.i18n import ugettext as _


class RRDProxy(object):
    '''
    Proxy RRD

    cf http://www.voidspace.org.uk/python/articles/urllib2_francais.shtml
    '''

    def __init__(self, url):
        '''Constructeur'''
        #" a renseigner selon configuration
        self._url = url

    def rrd_last_value(self, server, indicator):
        '''
        lecture derniere valeur de metrologie associee au parametre indicator
     
        @param server : serveur
        @type server : C{str}
        @param indicator : indicateur
        @type indicator : C{str}

        @rtype: liste de deux elements
        '''

        values = {'host' : server,
                  'indicator' : indicator}

        data = urllib.urlencode(values)
        print 'data %s', data

        url = self._url
        url += '/rrdgraph.py'
        url += '/outputMetrologie'
    
        proxy_handler = urllib2.ProxyHandler({'http': url})
        opener = urllib2.build_opener(proxy_handler)

        value = None
        handle = opener.open(url, data)
        if handle is not None:
            result = handle.read()
            # result = liste -> on prend le premier element ???
            #if result is not None:
            #    value = result[0] 
            handle.close()

        return result

    def rrd_img(self, server, graphtemplate):
        '''
        lecture image

        @param server : serveur
        @type server : C{str}
        @param graphtemplate : graphe
        @type graphtemplate : C{str}

        @rtype : image
        '''

        values = {'server' : server,
                  'graphtemplate' : graphtemplate,
                  'direct' : 1}

        data = urllib.urlencode(values)

        url = self._url
        url += '/rrdgraph.py'

        #print 'A - ***** %s' % url
 
        proxy_handler = urllib2.ProxyHandler({'http': url})
        opener = urllib2.build_opener(proxy_handler)

        result = None
        handle = opener.open(url, data)
        if handle is not None:
            result = handle.read()
            handle.close()

        #print 'B - ***** %s' % result

        return result


    def rrd_img_data(self, server, graphtemplate):
        '''
        lecture donnees image : src et alt

        @param server : serveur
        @type server : C{str}
        @param graphtemplate : graphe
        @type graphtemplate : C{str}

        @rtype : C{str}
        '''

        result = {}

        values = {'server' : server,
                  'graphtemplate' : graphtemplate,
                  'details' : 0}

        data = urllib.urlencode(values)

        url = self._url
        url += '/rrdgraph.py'
    
        proxy_handler = urllib2.ProxyHandler({'http': url})
        opener = urllib2.build_opener(proxy_handler)

        handle = opener.open(url, data)
        if handle is not None:
            text = handle.read()

            imghtmlparser = ImgHTMLParser()
            result = imghtmlparser.get_src_alt(text)
            imghtmlparser.close()

            handle.close()
        return result


    def rrd_img_u(self, server, graphtemplate, urlp):
        '''
        lecture image

        @param server : serveur
        @type server : C{str}
        @param graphtemplate : graphe
        @type graphtemplate : C{str}

        @rtype : image
        '''

        values = {'server' : server,
                  'graphtemplate' : graphtemplate,
                  'direct' : 1}

        data = urllib.urlencode(values)

        url = urlp
        url += '/rrdgraph.py'

        #print 'A - ***** %s' % url
 
        proxy_handler = urllib2.ProxyHandler({'http': url})
        opener = urllib2.build_opener(proxy_handler)

        result = None
        handle = opener.open(url, data)
        if handle is not None:
            result = handle.read()
            handle.close()

        #print 'B - ***** %s' % result

        return result

    def rrd_img_ap(self, server, graphtemplate, direct, duration, start, details):
        '''
        lecture image avec all parameters
     
        @param server : serveur
        @type server : C{str}
        @param graphtemplate : graphe
        @type graphtemplate : C{str}
        @param direct : 
        @type direct : int
        @param start : 
        @type start : int
        @param duration : 
        @type duration : int
        @param details : 
        @type details : int

        @rtype:
        '''

        values = {'server' : server,
                  'graphtemplate' : graphtemplate,
                  'direct' : direct,
                  'duration' : duration,
                  'start' : start,
                  'details' : details
        }

        data = urllib.urlencode(values)
        print 'I - ***** data %s', data

        url = self._url
        url += '/rrdgraph.py'
        print 'I - ***** url %s' % url
    
        proxy_handler = urllib2.ProxyHandler({'http': url})
        opener = urllib2.build_opener(proxy_handler)

        value = None
        handle = opener.open(url, data)
        if handle is not None:
            result = handle.read()
            handle.close()

        return result

    def rrd_getstarttime(self, server, getstarttime):
        '''
        lecture valeur temps
     
        @param server : serveur
        @type server : C{str}
        @param getstarttime : 
        @type getstarttime : int

        @rtype:
        '''

        values = {'server' : server,
                  'getstarttime' : getstarttime
                 }

        data = urllib.urlencode(values)
        print 'T - ***** data %s', data

        url = self._url
        url += '/rrdgraph.py'
        print 'T - ***** url %s' % url
    
        proxy_handler = urllib2.ProxyHandler({'http': url})
        opener = urllib2.build_opener(proxy_handler)

        value = None
        handle = opener.open(url, data)
        if handle is not None:
            result = handle.read()
            handle.close()

        print 'T - ***** result %s' % result

        return result


class ImgHTMLParser(HTMLParser):
    '''
    Parser HTML

    Analyse texte lu dans RRD pour determination valeurs src et alt
    '''

    def __init__(self):
        HTMLParser.__init__(self)
        self._dr = {}

    def get_src_alt(self, text):
        '''
        Determination valeurs pour src et alt

        @param text : texte a analyser
        @type text : C{str}


        @rtype: dictionnaire
        '''

        self.feed(text)
        return self._dr

    def handle_starttag(self, tag, attrs):
        '''
        Traitement sur debut Tag
        
        @param tag : tag a analyser
        @type tag : C{str}
        @param attrs : attributs pour tag
        @param attrs : C{str}

        @return:  donnees src et alt
        @rtype:  dictionnaire
        '''

        if tag == 'img':
            text = self.get_starttag_text()

            # texte associe a src
            start_sep = 'src="'
            end_sep = '"'
            src = self.get_value(text, start_sep, end_sep)
            
            # texte associe a alt
            start_sep = 'alt="'
            end_sep = '"'
            alt = self.get_value(text, start_sep, end_sep)

            self._dr = { 'src': src, 'alt': alt}

    def handle_endtag(self, tag):
        '''
        Traitement sur fin Tag
        
        @param tag : tag a analyser
        @type tag : C{str}
        '''
        text = ''
        if tag == 'img':
            text = self.get_starttag_text()

    def get_value(self, text, start_sep, end_sep):
        '''
        Determination texte compris entre separateurs debut et fin

        @param start_sep : separateur debut
        @type start_sep : C{str}
        @param end_sep : separateur fin
        @type end_sep : C{str}

        @rtype : C{str}
        '''

        # elements texte
        separator = ' '
        ltext = text.split(separator)

        value = ''
        b_start =  False
        b_end = False
        for elt in ltext:
            # separateur debut = debut element
            if elt.startswith(start_sep) == True:
                value = elt[len(start_sep):]
                b_start =  True

                # separateur fin = fin element
                if elt.endswith(end_sep) == True:
                    value = elt[len(start_sep):len(elt)-len(end_sep)]
                    b_start =  False
                    b_end = True
                    break

            # separateur fin = fin element
            elif elt.endswith(end_sep) == True:
                value_l = elt[:len(elt) -len(end_sep)]
                if value != '':
                    value += separator
                value += value_l
                b_start = False
                b_end = True

            # autre
            else:
                if b_start == True:
                    if value != '':
                        value += separator
                    value += elt

        return value


class SuffixManager(object):
    '''
    Gestion suffixe pour valeur metrologie
    '''

    def convert_with_suffix(self, value):
        '''
        Conversion valeur avec suffixe multiplication
        (cf http://fr.wikipedia.org/wiki/Kilo et autres)

        @param value : valeur
        @type value : valeur numérique

        @rtype : C{str}
        '''

        svalue = ''

        # signe
        sign = ''
        if value < 0:
            sign = '-'

        # determination puissance de 10
        value_l = abs(value)
        power_l = 0
        if value_l >= 1:
            svalue = str(int(value_l))
            power_l = len(svalue) - 1
        else:
            svalue = str(value_l)
            power_l = len(svalue) - 2
            power_l =  -power_l

        # data sur puissances de 10 :
        # - pour exposant < 0 : -9, -6, -3, -2, -1
        # - pour exposant = 0 :
        # - pour exposant > 0 : 1, 2, 3, 6, 9
        lpd = []
        lpd.append({'s': 'p', 'p': -9})
        lpd.append({'s': 'µ', 'p': -6})        
        lpd.append({'s': 'm', 'p': -3})
        lpd.append({'s': 'c', 'p': -2})
        lpd.append({'s': 'd', 'p': -1})
        lpd.append({'s': '', 'p': 0})
        lpd.append({'s': 'da', 'p': 1})
        lpd.append({'s': 'h', 'p': 2})
        lpd.append({'s': 'k', 'p': 3})
        lpd.append({'s': 'M', 'p': 6})
        lpd.append({'s': 'G', 'p': 9})

        power_p = None
        suffix_p = None

        power_c = None
        suffix_c = None

        value_l = float(abs(value))
        for elt in lpd:
            power_p = power_c
            suffix_p = suffix_c
            for key in elt.iterkeys():
                if key == 's':
                    suffix_c = elt[key]
                if key == 'p':
                    power_c = elt[key]

            if power_l < power_c:
                if power_p is not None:
                    if power_l >= power_p:
                        value_l /= (10 ** power_p)
                        svalue = sign
                        svalue += str(value_l)
                        svalue += suffix_p

                        break
                else:
                    svalue = sign
                    svalue += str(value_l)
                    break

        return svalue

    def convert_to_percent(self, value, maxvalue):
        '''
        Conversion avec pourcentage

        @param value : valeur
        @type value : int
        @param maxvalue : valeur max
        @type value : int

        @rtype : C{str}
        '''

        result = 'Indetermine'
        if maxvalue != 0:
            percentvalue = ( value * 100 / maxvalue)
            result = str(percentvalue) + '%'

        return result
