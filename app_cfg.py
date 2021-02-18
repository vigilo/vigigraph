# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8 sw=4 ts=4 et :
# Copyright (C) 2011-2021 CS GROUP - France
# License: GNU GPL v2 <http://www.gnu.org/licenses/gpl-2.0.html>

"""
Additional settings for VigiGraph that can only be represented
using the Python programming language.
"""

import vigigraph
from vigilo.turbogears.configurator import Configurator

options = {
    'external_links': [
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
    ],

    # Extensions (Entreprise ou spécifique projet)
    'extensions': [],
}

# Create the final configuration for the application
base_config = Configurator('VigiGraph', vigigraph)
base_config.update_blueprint(options)
