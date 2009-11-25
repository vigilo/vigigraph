# -*- coding: utf-8 -*-
"""The application's model objects"""

from vigilo.models.session import DBSession
from vigilo.models.vigilo_bdd_config import metadata

metadata.bind = DBSession.bind


#####
# Generally you will not want to define your table's mappers, and data objects
# here in __init__ but will want to create modules them in the model directory
# and import them at the bottom of this file.
#
######

from vigilo.models import User, UserGroup, Permission
from vigilo.models import Host, HostGroup, ServiceLowLevel, ServiceGroup
#from vigilo.models import Service, ServiceGroup
from vigilo.models import Tag, CustomGraphView, BoardViewFilter
from vigilo.models import Graph

