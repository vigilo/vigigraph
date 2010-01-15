# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4: 
"""Gestion Nagios par proxy"""

import urllib
import urllib2

from pylons.i18n import ugettext as _


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

        #print "get_status"

        handle = None
        result = None

        values = {'host' : host,
                  'style' : 'detail',
                  'supNav' : 1}

        data = urllib.urlencode(values)
        #print "data %s" % data

        url = self._url
        url += '/status.cgi'
        #print "url %s" % url
    
        proxy_handler = urllib2.ProxyHandler({'http': url})
        opener = urllib2.build_opener(proxy_handler)
        #print "proxy_handler %s" % proxy_handler
        #print "opener %s" % opener

        try:
            handle = opener.open(url, data)
        except urllib2.URLError, e:
            #print "build_opener - URLError %s" % (e.reason)
            #print "build_opener - URLError %s" % (e.read())
            raise
        except urllib2.HTTPError, e:
            #print "build_opener - HTTPError %s" % (e.code)
            #print "build_opener - HTTPError %s" % (e.read())
            raise
        finally:
            if handle is not None:
                result = handle.read()
                handle.close()

        #print "result %s" % result

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

        #print "get_extinfo"

        handle = None
        result = None

        values = {'host' : host,
                  'service' : service,
                  'type' : 2,
                  'supNav' : 1}

        data = urllib.urlencode(values)
        #print "data %s" % data

        url = self._url
        url += '/extinfo.cgi'
        #print "url %s" % url

        proxy_handler = urllib2.ProxyHandler({'http': url})
        opener = urllib2.build_opener(proxy_handler)

        try:
            handle = opener.open(url, data)
        except urllib2.URLError, e:
            #print "build_opener - URLError %s" % (e.reason)
            raise
        except urllib2.HTTPError, e:
            #print "build_opener - HTTPError %s" % (e.code)
            raise
        finally:
            if handle is not None:
                result = handle.read()
                handle.close()

        #print "result %s" % result

        return result
