# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 sw=4 ts=4 et :
"""
Global configuration file for TG2-specific settings in vigigraph.

This file complements development/deployment.ini.

Please note that **all the argument values are strings**. If you want to
convert them into boolean, for example, you should use the
:func:`paste.deploy.converters.asbool` function, as in::

    from paste.deploy.converters import asbool
    setting = asbool(global_conf.get('the_setting'))

"""

# pylint: disable-msg=W0611
# W0611: 19: Unused import 'app_globals', 'helpers'

import vigigraph
from vigilo.turbogears import VigiloAppConfig
from vigigraph.lib import app_globals, helpers

base_config = VigiloAppConfig('vigigraph')
base_config.package = vigigraph

base_config["external_links"] = [
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
