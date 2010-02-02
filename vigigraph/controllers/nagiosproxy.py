# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4: 
"""Gestion Nagios par proxy"""

import urllib
import urllib2
import os


class NagiosProxy(object):
    '''
    Proxy Nagios

    cf http://www.voidspace.org.uk/python/articles/urllib2_francais.shtml
    '''

    def __init__(self, url):
        '''Constructeur'''
        self._url = url

    def _retrieve_content(self, url, values):
        ''' Lecture du contenu Nagios à partir d'un dictionnaire de valeurs'''

        handle = None
        result = None
        data = urllib.urlencode(values)
        proxy_handler = urllib2.ProxyHandler({'http': url})
        opener = urllib2.build_opener(proxy_handler)

        try:
            handle = opener.open(url, data)
            result = handle.read()
        except urllib2.URLError, e:
            raise
        finally:
            if handle:
                handle.close()
            
        return result


    def get_status(self, host):
        '''
        lecture status
     
        @param host : hôte
        @type host : C{str}

        @return : donnees Nagios
        @rtype: 
        '''

        values = {'host' : host,
                  'style' : 'detail',
                  'supNav' : 1}

        url = self._url
        url = os.path.join(url, 'status.cgi')

        return self._retrieve_content(url, values)


    def get_extinfo(self, host, service):
        '''
        lecture informations
     
        @param host : hôte
        @type host : C{str}
        @param service : service
        @type service : C{str}

        @return : donnees Nagios
        @rtype: 
        '''

        values = {'host' : host,
                  'service' : service,
                  'type' : 2,
                  'supNav' : 1}

        url = self._url
        url = os.path.join(url, 'extinfo.cgi')

        return self._retrieve_content(url, values)
