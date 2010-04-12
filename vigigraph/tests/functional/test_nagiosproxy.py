# -*- coding: utf-8 -*-
'''
Created on 02 feb. 2010
@author: flaheugu

Tests Nagios Proxy
'''

import transaction
import unittest

from tg import config
from nose.tools import eq_

from vigilo.turbogears.nagiosproxy import NagiosProxy

from vigilo.models.session import DBSession
from vigilo.models.tables import Host, Ventilation, VigiloServer, Application

from vigigraph.tests import TestController


def create_Host(name):
    '''Creation Host'''
    h = DBSession.query(Host).filter(Host.name == name).first()
    if not h:
        h = Host(name=name,
                 checkhostcmd=u'dummy',
                 hosttpl=u'linux',
                 mainip=u"127.0.0.1",
                 snmpcommunity=u"public",
                 snmpport=161,
                 weight=0)
        DBSession.add(h)
        DBSession.flush()
    return h

def create_Server(name, description):
    '''Creation Server'''
    s = DBSession.query(VigiloServer).filter(VigiloServer.name == name).first()
    if not s:
        s = VigiloServer(name=name, description=description)
        DBSession.add(s)
        DBSession.flush()
    return s

def create_Application(name):
    '''Creation Application'''
    a = DBSession.query(Application).filter(Application.name == name).first()
    if not a:
        a = Application(name=name)
        DBSession.add(a)
        DBSession.flush()
    return a

def create_Ventilation(host, server, application):
    """
    Peuple la base de données avec des informations sur la ventilation
    de la supervision, c'est-à-dire, la répartition des applications de
    supervision sur le parc et les machines gérées par chacune de ces
    applications.
    """
    v = None
    h = DBSession.query(Host).filter(Host.name == host).first()
    s = DBSession.query(VigiloServer).filter(
            VigiloServer.name == server).first()
    a = DBSession.query(Application).filter(
            Application.name == application).first()
    if h and s:
        v = Ventilation(idhost=h.idhost,
            idvigiloserver=s.idvigiloserver, idapp=a.idapp)
        DBSession.add(v)
        DBSession.flush()
    return v

def getServer(host):
    '''Server'''
    result = DBSession.query(VigiloServer.name) \
            .filter(VigiloServer.idvigiloserver == Ventilation.idvigiloserver) \
            .filter(Ventilation.idhost == Host.idhost) \
            .filter(Ventilation.idapp == Application.idapp) \
            .filter(Host.name == host) \
            .filter(Application.name == u'nagios') \
            .scalar()

    return result


class NagiosProxy_without_nagios(NagiosProxy):
    """
    Classe de substitution de NagiosProxy pour effectuer les tests
    sans nagios
    """
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
        self.url = 'http://localhost/nagios/cgi-bin'

    def test_supPage(self):
        '''fonction vérification supPage'''
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


class TestNagiosProxy_bd(TestController):
    """ Test Gestion Valeur Nagios """  

    def setUp(self):
        '''setup'''
        super(TestNagiosProxy_bd, self).setUp()

        # Host
        host = u'par.linux0'
        create_Host(host)

        # Serveurs Vigilo
        sv1 = create_Server(u'http://localhost', u'RRD+Nagios')

        # Applications Vigilo
        ap1 = create_Application(u'rrdgraph')
        ap2 = create_Application(u'nagios')

        # Ventilation
        if sv1 is not None and ap1 is not None:
            create_Ventilation(host, sv1.name, ap1.name)
        if sv1 is not None and ap2 is not None:
            create_Ventilation(host, sv1.name, ap2.name)

        DBSession.flush()
        transaction.commit()

    def test_acces_url(self):
        '''fonction vérification acces url via proxy'''

        host = u'par.linux0'
        server = getServer(host)
        url_web_path = config.get('nagios_web_path')
        url = '%s%s/%s' % (server, url_web_path, 'status.cgi')
        eq_("http://localhost/nagios/cgi-bin/status.cgi", url)

if __name__ == "__main__":
    unittest.main()

