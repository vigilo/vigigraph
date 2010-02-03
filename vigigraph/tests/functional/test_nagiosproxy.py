# -*- coding: utf-8 -*-
'''
Created on 02 feb. 2010
@author: flaheugu

Tests Nagios Proxy
'''

import unittest

from vigigraph.controllers.nagiosproxy import NagiosProxy

#from vigilo.common.conf import settings


class NagiosProxy_without_nagios(NagiosProxy):
    """ Classe de substitution de NagiosProxy 
    pour effectuer les tests sans nagios"""
    def __init__(self, content, *args, **kwargs):
        '''Constructeur'''
        super(NagiosProxy_without_nagios, self).__init__(*args, **kwargs)
        self.content = content

    def _retrieve_content(self, *args, **kwargs):
        '''Retour - Surcharge'''
        return self.content


class TestNagiosProxy(unittest.TestCase):
    """ Test Gestion Valeur Nagios """  

    def __init__(self, *args, **kwargs):
        '''Constructeur'''
        super(TestNagiosProxy, self).__init__(*args, **kwargs)
        #self.url = settings.get('NAGIOS_URL') -> ne marche pas
        self.url = 'http://localhost/nagios/cgi-bin'

    def test_subPage(self):
        '''fonction vérification subPage'''
        result = None

        host = 'par.linux0'

        content = '''<html><head>
        </head></html>
        '''

        url = self.url
        if url is not None:
            nagiosproxy = NagiosProxy_without_nagios(content, url)
            result = nagiosproxy.get_status(host)

        assert(result != None)
    
    def test_servicePage(self):
        '''fonction vérification servicePage'''
        result = None

        host = 'par.linux0'
        service = 'Load'

        content = '''<html><head>
        </head></html>
        '''

        url = self.url
        if url is not None:
            nagiosproxy = NagiosProxy_without_nagios(content, url)
            result = nagiosproxy.get_extinfo(host, service)

        assert(result != None)


if __name__ == "__main__": 
    unittest.main()
