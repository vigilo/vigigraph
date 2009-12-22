# -*- coding: utf-8 -*-
from sqlalchemy import and_

from vigigraph.model import Host, HostGroup
from vigigraph.model import ServiceLowLevel, ServiceGroup
from vigigraph.model import PerfDataSource, Graph
from vigigraph.model import DBSession

from datetime import datetime

import transaction

#DBSession.autocommit = True

# Groupe d'hôtes (HostGroup)
def create_HostGroup(name, parent=None):
    g = DBSession.query(HostGroup).filter(HostGroup.name == name).first()
    if not g:
        if parent:
            g = HostGroup(name=name, idparent=parent.idgroup)
        else:
            g = HostGroup(name=name)
        print "Ajout du Groupe: ", name
        DBSession.add(g)
    return g

# Hôte (Host)
#def create_Host(name, checkhostcmd, hosttpl, snmpcommunity, mainip, snmpport):
def create_Host(name):
    h = DBSession.query(Host).filter(Host.name == name).first()
    if not h:
        h = Host(name=name,
                 checkhostcmd=u'dummy',
                 hosttpl=u'linux',
                 mainip=u"127.0.0.1",
                 snmpcommunity=u"public",
                 snmpport=161,
                 weight=0)
        print "Ajout de l'hôte: ", name
        DBSession.add(h)
    return h

#Recherche de l'objet Host à partir du name
def get_host(hostname):
    """ Return Host object from hostname, None if not available"""
    return DBSession.query(Host) \
            .filter(Host.name == hostname) \
            .first()

# Ajout d'un hôte dans un groupe d'hôtes (Host -> HostGroup)
def add_Host2HostGroup(host, group):
    if host not in group.hosts:
        print "Ajout de l'hote: %(h)s dans le group: %(g)s" % \
                {'h': host.name,
                 'g': group.name}
        group.hosts.append(host)

def create_ServiceLowLevel(hostname, servicename):
    s = DBSession.query(ServiceLowLevel) \
            .join((Host, ServiceLowLevel.idhost == Host.idhost)) \
            .filter(ServiceLowLevel.servicename == servicename) \
            .filter(Host.name == hostname) \
            .first()
    if not s:
        s = ServiceLowLevel(idhost=get_host(hostname).idhost,
                servicename=servicename,
                weight = 42, 
                op_dep=u"?")
        print "Ajout du service", servicename
        DBSession.add(s)
    return s

# Groupe de services (ServiceGroup)
def create_ServiceGroup(name, parent=None):
    g = DBSession.query(ServiceGroup).filter(ServiceGroup.name == name).first()
    if not g:
        if parent:
            g = ServiceGroup(name=name, idparent=parent.idgroup)
        else:
            g = ServiceGroup(name=name)
        print "Ajout du Groupe: ", name
        DBSession.add(g)
    return g

# Ajout d'un hôte dans un groupe d'hôtes (Host -> HostGroup)
def add_ServiceLowLevel2ServiceGroup(service, group):
    if service not in group.services:
        print "Ajout du service: %(s)s dans le group: %(g)s" % \
                {'s': service.servicename,
                 'g': group.name}
        group.services.append(service)

def _get_service(hostname, servicename):
    """ Return Host object from hostname, None if not available"""
    return DBSession.query(ServiceLowLevel) \
            .join((Host, Host.idhost == ServiceLowLevel.idhost)) \
            .filter(Host.name == hostname) \
            .filter(ServiceLowLevel.servicename == servicename) \
            .first()

#Recherche de l'objet ServiceGroup à partir du name
def get_ServiceGroup(name):
    return DBSession.query(ServiceGroup).filter(ServiceGroup.name == name).first()

#Recherche de l'objet ServiceLowLevel à partir du name
def get_ServiceLowLevel(hostname, servicename):
    s = DBSession.query(ServiceLowLevel) \
            .join((Host, ServiceLowLevel.idhost == Host.idhost)) \
            .filter(ServiceLowLevel.servicename == servicename) \
            .filter(Host.name == hostname) \
            .first()
    return s

# DS (Graph)
def create_graph(name, vlabel, perfdatasources):
    gr = DBSession.query(Graph) \
            .filter(Graph.name == name) \
            .first()
    if not gr:
        gr = Graph(name=name, vlabel=vlabel)
        print "Ajout du graph: ", vlabel
        DBSession.add(gr)
    return gr

# DS (PerfDataSource)
def create_ds(name, type, service, label, graphs):
    ds = DBSession.query(PerfDataSource) \
            .filter(PerfDataSource.service == service) \
            .filter(PerfDataSource.name == name) \
            .first()
    if not ds:
        ds = PerfDataSource(name=name, type=type, service=service, label=label, graphs=graphs)
        print "Ajout de la datasource: ", label
        DBSession.add(ds)
    return ds


hg1 = create_HostGroup(u'Serveurs')
hg2 = create_HostGroup(u'Telecoms')
hg3 = create_HostGroup(u'Serveurs Linux', hg1)
hg4 = create_HostGroup(u'NORTEL', hg2)
hg5 = create_HostGroup(u'CISCO', hg2)

h1 = create_Host(u'proto4.si.c-s.fr')
h2 = create_Host(u'messagerie.si.c-s.fr')
h3 = create_Host(u'testnortel.si.c-s.fr')
h4 = create_Host(u'proto6.si.c-s.fr')

add_Host2HostGroup(h1, hg3)
add_Host2HostGroup(h2, hg3)
add_Host2HostGroup(h3, hg4)
add_Host2HostGroup(h4, hg5)
add_Host2HostGroup(h4, hg3)
add_Host2HostGroup(h4, hg3)

sg1 = create_ServiceGroup(u'Général')
sg2 = create_ServiceGroup(u'Interface Réseau')
sg3 = create_ServiceGroup(u'Performance')
sg4 = create_ServiceGroup(u'Partitions')
sg5 = create_ServiceGroup(u'Processus')

s1 = create_ServiceLowLevel(h1.name, u'Interface eth0')
s2 = create_ServiceLowLevel(h1.name, u'Interface eth1')
s3 = create_ServiceLowLevel(h1.name, u'Interface série')
s4 = create_ServiceLowLevel(h4.name, u'Interface')

add_ServiceLowLevel2ServiceGroup(s1, sg2)
add_ServiceLowLevel2ServiceGroup(s2, sg2)
add_ServiceLowLevel2ServiceGroup(s3, sg1)
add_ServiceLowLevel2ServiceGroup(s4, sg2)

gr1 = create_graph(u'graph1',u'Graph1', None)
gr2 = create_graph(u'graph2',u'Graph2', None)
gr3 = create_graph(u'graph3',u'Graph3', None)
gr4 = create_graph(u'graph4',u'Graph4', None)
gr5 = create_graph(u'graph5',u'Graph5', None)

graphs = []
for g in DBSession.query(Graph).all():
    graphs.append(g)

print 'graphs %s' % graphs

ds1 = create_ds(u'ineth0', u'GAUGE', s1 \
                , u'Données en entrée sur eth0', graphs[1:3])
ds2 = create_ds(u'outeth0', u'GAUGE', s2 \
                , u'Données en sortie sur eth0', graphs[1:3])
ds3 = create_ds(u'outeth1', u'GAUGE', s3 \
                , u'Données en sortie sur eth1', graphs[2:4])
ds4 = create_ds(u'ineth1', u'GAUGE', s4 \
                , u'Données en entrée sur eth0', graphs[3:3])

transaction.commit()
