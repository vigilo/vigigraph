# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
# Copyright (C) 2006-2021 CS GROUP - France
# License: GNU GPL v2 <http://www.gnu.org/licenses/gpl-2.0.html>

"""Vigigraph Controller"""

# pylint: disable-msg=W0613
# W0613: Unused argument : les arguments des contrôleurs sont les composants
#        de la query-string de l'URL

import gettext
import os.path
import logging

from tg import expose, require, config, response
from tg.i18n import lazy_ugettext as l_, get_lang
from tg.predicates import Any, All, not_anonymous, has_permission, in_group
from pkg_resources import resource_filename

from vigilo.turbogears.controllers.auth import AuthController
from vigilo.turbogears.controllers.custom import CustomController
from vigilo.turbogears.controllers.error import ErrorController
from vigilo.turbogears.controllers.proxy import ProxyController
from vigilo.turbogears.controllers.i18n import I18nController
from vigilo.turbogears.controllers.api.root import ApiRootController

from vigigraph.controllers.rpc import RpcController

__all__ = ['RootController']

LOGGER = logging.getLogger(__name__)

# pylint: disable-msg=R0201
class RootController(AuthController, I18nController):
    """
    The root controller for the vigigraph application.
    """
    error = ErrorController()
    rpc = RpcController()
    nagios = ProxyController('nagios', '/nagios/',
        not_anonymous(l_('You need to be authenticated')))
    vigirrd = ProxyController('vigirrd', '/vigirrd/',
        not_anonymous(l_('You need to be authenticated')))
    api = ApiRootController()
    custom = CustomController()

    @expose('index.html')
    @require(All(
        not_anonymous(msg=l_("You need to be authenticated")),
        Any(
            config.is_manager,
            has_permission('vigigraph-access',
                msg=l_("You don't have access to VigiGraph")),
        )
    ))
    def index(self):
        """Handle the front-page."""
        return dict(page='index')
