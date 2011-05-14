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

import vigigraph
from vigilo.turbogears import VigiloAppConfig
from vigigraph.lib import app_globals, helpers

base_config = VigiloAppConfig('vigigraph')
base_config.package = vigigraph

# Extensions (Entreprise ou spécifique projet)
base_config["extensions"] = ()
