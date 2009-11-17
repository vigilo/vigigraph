# -*- coding: utf-8 -*-
from sqlalchemy import and_

from vigigraph import model
from vigigraph.model import DBSession

from datetime import datetime

import transaction

#DBSession.autocommit = True

# Groupe (Group)
def add_group(name, parent=None):
    g = DBSession.query(model.Group).filter(model.Group.name == name).first()
    if not g:
        if parent:
            g = model.Group(name=name, idparent=parent.idgroup)
        else:
            g = model.Group(name=name)
        print "Ajout du Groupe: ", name
        DBSession.add(g)
    return g

# Groupe de host (HostGroup)
def add_hostgroup(hostname, group):
    hg = DBSession.query(model.HostGroup) \
         .filter(model.HostGroup.hostname == hostname) \
         .filter(model.HostGroup.idgroup == group.idgroup) \
         .first()
    if not hg:
        hg = model.HostGroup(hostname=hostname, idgroup=group.idgroup)
        print "Ajout de l'hote %s dans le Groupe %s" % (hostname, group.idgroup)
        DBSession.add(hg)
    return hg

# Hôte (Host)
def add_host(name, checkhostcmd, fqhn, hosttpl, snmpcommunity, mainip, snmpport):
    h = DBSession.query(model.Host).filter(model.Host.name == name).first()
    if not h:
        h = model.Host(name=name, checkhostcmd=checkhostcmd, fqhn=fqhn, 
                       hosttpl=hosttpl, snmpcommunity=snmpcommunity, mainip=mainip, snmpport=snmpport)
        print "Ajout de l'hôte: ", name
        DBSession.add(h)
    return h

## DS [PerfDataSource)
#def add_ds(name, op_dep, servicetype):
#    s = DBSession.query(model.

## Graph (Graph)
#def add_graph(name, template, vlabel):
#    g =  DBSession.query(model.Graph).filter(model.Graph.name == name).first()
#    if not g:
#        g = model.Graph(name=name, template=template, vlabel=vlabel)
#        print "Ajout du graph: ", name
#        DBSession.add(g)
#    return g

g1 = add_group(u'Serveurs')
g2 = add_group(u'Telecoms')
g3 = add_group(u'Serveurs Linux', g1)
g4 = add_group(u'NORTEL', g2)
g5 = add_group(u'CISCO', g2)


h1 = add_host(u'proto4', u'dummy', u'proto4.si.c-s.fr', u'linuxserver', u'public', u'127.0.0.1', u'12')
h2 = add_host(u'server.mails', u'dummy', u'messagerie.si.c-s.fr', u'linuxserver', u'public', u'127.0.0.1', u'12')
h3 = add_host(u'testnortel', u'dummy', u'testnortel.si.c-s.fr', u'switch', u'public', u'127.0.0.1', u'12')
h4 = add_host(u'proto6', u'dummy', u'proto6.si.c-s.fr', u'ciscorouter', u'public', u'127.0.0.1', u'12')

hg1 =  add_hostgroup(u'proto4', g3)
hg2 =  add_hostgroup(u'server.mails', g3)
hg3 =  add_hostgroup(u'testnortel', g4)
hg4 =  add_hostgroup(u'proto6', g5)
hg4 =  add_hostgroup(u'proto6', g3)

transaction.commit()
