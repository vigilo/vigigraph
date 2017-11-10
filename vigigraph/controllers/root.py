# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
# Copyright (C) 2006-2016 CS-SI
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
from vigilo.turbogears.controllers.api.root import ApiRootController

from vigigraph.controllers.rpc import RpcController

__all__ = ['RootController']

LOGGER = logging.getLogger(__name__)

# pylint: disable-msg=R0201
class RootController(AuthController):
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

    @expose()
    def i18n(self):
        # Repris de tg.i18n.translation:_get_translator.
        conf = config.current_conf()
        try:
            localedir = conf['localedir']
        except KeyError:
            localedir = os.path.join(conf['paths']['root'], 'i18n')

        lang = get_lang()
        modules = (
            (conf['package'].__name__, localedir),
            ('vigilo-themes', resource_filename('vigilo.themes.i18n', '')),
            ('vigilo-vigigraph-enterprise',
             resource_filename('vigilo.vigigraph_enterprise.i18n', '')),
        )

        # Charge et installe le fichier JS de traduction de chaque module
        translations = "babel.Translations.load("
        for domain, directory in modules:
            try:
                mofile = gettext.find(domain, directory, languages=lang)
                if mofile is None:
                    continue

                fhandle = open(mofile[:-3] + '.js', 'r')
                translations += fhandle.read()
                fhandle.close()
                translations += ").load("
            except ImportError:
                pass
        translations += "{}).install()"

        response.headers['Content-Type'] = 'text/javascript; charset=utf-8'
        return translations
