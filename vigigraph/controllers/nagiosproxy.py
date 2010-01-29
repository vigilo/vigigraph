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
        #" a renseigner selon configuration
        self._url = url

    def get_status(self, host):
        '''
        lecture status
     
        @param host : hôte
        @type host : C{str}

        @rtype: 
        '''

        handle = None
        result = None

        values = {'host' : host,
                  'style' : 'detail',
                  'supNav' : 1}

        data = urllib.urlencode(values)

        url = self._url
        url = os.path.join(url, 'status.cgi')
    
        proxy_handler = urllib2.ProxyHandler({'http': url})
        opener = urllib2.build_opener(proxy_handler)

        try:
            handle = opener.open(url, data)
        except urllib2.URLError, e:
            raise
        finally:
            if handle is not None:
                result = handle.read()
                handle.close()

        return result

    def get_extinfo(self, host, service):
        '''
        lecture informations
     
        @param host : hôte
        @type host : C{str}
        @param service : service
        @type service : C{str}

        @rtype: 
        '''

        handle = None
        result = None

        values = {'host' : host,
                  'service' : service,
                  'type' : 2,
                  'supNav' : 1}

        data = urllib.urlencode(values)

        url = self._url
        url = os.path.join(url, 'extinfo.cgi')

        proxy_handler = urllib2.ProxyHandler({'http': url})
        opener = urllib2.build_opener(proxy_handler)

        try:
            handle = opener.open(url, data)
        except urllib2.URLError, e:
            raise
        finally:
            if handle is not None:
                result = handle.read()
                handle.close()

        return result
