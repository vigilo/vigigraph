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
base_config.renderers = []

base_config.package = vigigraph

#Set the default renderer
base_config.default_renderer = 'genshi'
base_config.renderers.append('genshi')

#Configure the base SQLALchemy Setup
base_config.use_sqlalchemy = True

# Configure the authentication backend
base_config.auth_backend = 'sqlalchemy'

# override this if you would like to provide a different who plugin for
# managing login and logout of your application
base_config.sa_auth.form_plugin = None

# You may optionally define a page where you want users to be redirected to
# on login:
base_config.sa_auth.post_login_url = '/post_login'

# You may optionally define a page where you want users to be redirected to
# on logout:
base_config.sa_auth.post_logout_url = '/post_logout'


##################################
# Settings specific to Vigigraph #
##################################

# Vigigraph version
base_config['vigigraph_version'] = u'0.1'

