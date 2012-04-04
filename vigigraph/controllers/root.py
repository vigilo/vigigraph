# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4:
# Copyright (C) 2006-2012 CS-SI
# License: GNU GPL v2 <http://www.gnu.org/licenses/gpl-2.0.html>

"""Vigigraph Controller"""

# pylint: disable-msg=W0613
# W0613: Unused argument : les arguments des contrôleurs sont les composants
#        de la query-string de l'URL


import logging
from tg import expose, require
from pylons.i18n import lazy_ugettext as l_, get_lang
from repoze.what.predicates import Any, All, not_anonymous, \
                                    has_permission, in_group
from pkg_resources import resource_filename

from vigilo.turbogears.controllers.auth import AuthController
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
    api = ApiRootController("/api")

    @expose('index.html')
    @require(All(
        not_anonymous(msg=l_("You need to be authenticated")),
        Any(
            in_group('managers'),
            has_permission('vigigraph-access',
                msg=l_("You don't have access to VigiGraph")),
        )
    ))
    def index(self):
        """Handle the front-page."""
        return dict(page='index')

    @expose()
    def i18n(self):
        import gettext
        import pylons
        import os.path

        # Repris de pylons.i18n.translation:_get_translator.
        conf = pylons.config.current_conf()
        try:
            rootdir = conf['pylons.paths']['root']
        except KeyError:
            rootdir = conf['pylons.paths'].get('root_path')
        localedir = os.path.join(rootdir, 'i18n')

        lang = get_lang()

        # Localise le fichier *.mo actuellement chargé
        # et génère le chemin jusqu'au *.js correspondant.
        filename = gettext.find(conf['pylons.package'], localedir,
            languages=lang)
        js = filename[:-3] + '.js'
        # Récupère et envoie le contenu du fichier de traduction *.js.
        fhandle = open(js, 'r')
        translations = fhandle.read()
        fhandle.close()

        # Même chose pour les thèmes
        themes_filename = gettext.find(
            'vigilo-themes',
            resource_filename('vigilo.themes.i18n', ''),
            languages=lang)
        themes_js = themes_filename[:-3] + '.js'
        fhandle = open(themes_js, 'r')
        translations += fhandle.read()
        fhandle.close()

        # Extensions Enterprise
        try:
            ent_filename = gettext.find(
                'vigilo-vigigraph-enterprise',
                resource_filename('vigilo.vigigraph_enterprise.i18n', ''),
                languages=lang)
        except ImportError:
            pass
        else:
            # Le nom du fichier sera None s'il n'existe pas
            # de traductions dans la langue demandée.
            if ent_filename is not None:
                fhandle = open(ent_filename[:-3] + '.js', 'r')
                translations += fhandle.read()
                fhandle.close()

        return translations
