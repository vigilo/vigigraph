# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 sw=4 ts=4 et :
# Copyright (C) 2011-2020 CS-SI
# License: GNU GPL v2 <http://www.gnu.org/licenses/gpl-2.0.html>

"""
Global configuration file for TG2-specific settings in vigigraph.

This file complements development/deployment.ini.

Please note that **all the argument values are strings**. If you want to
convert them into boolean, for example, you should use the
:func:`paste.deploy.converters.asbool` function, as in::

    from paste.deploy.converters import asbool
    setting = asbool(global_conf.get('the_setting'))

"""


import vigigraph
from vigilo.turbogears import VigiloAppConfig
from vigigraph.lib import app_globals # pylint: disable-msg=W0611
# W0611: Unused import: imports nécessaires pour le fonctionnement

base_config = VigiloAppConfig('VigiGraph')
base_config.package = vigigraph

base_config["external_links"] = [
    {
        'label': 'Alarms',
        'image': 'images/preferences-system-windows.png',
        'tooltip': 'Display alarms for the selected host',
        'uri': '../vigiboard/?host={host}',
        'sameWindow': True,
    },
    {
        'label': 'Nagios page',
        'image': 'images/nagios-16.png',
        'tooltip': 'Display Nagios page for the selected host',
        'uri': 'nagios/{host}/cgi-bin/status.cgi?host={host}&style=detail&supNav=1',
        'sameWindow': True,
    },
    {
        'label': 'Metrology page',
        'image': 'images/preferences-system-windows.png',
        'tooltip': 'Display a page with all the graphs for the selected host',
        'uri': 'rpc/fullHostPage?host={host}',
        'sameWindow': True,
    },
]

# Extensions (Entreprise ou spécifique projet)
base_config["extensions"] = ()
