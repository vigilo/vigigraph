# -*- coding: utf-8 -*-
# vim:set expandtab tabstop=4 shiftwidth=4: 
"""Vigigraph Controller"""

import logging
from tg import expose, flash, require, request, redirect
from pylons.i18n import ugettext as _, lazy_ugettext as l_
from repoze.what.predicates import Any, All, not_anonymous, \
                                    has_permission, in_group

from vigilo.turbogears.controllers import BaseController
from vigilo.turbogears.controllers.error import ErrorController
from vigilo.turbogears.controllers.proxy import ProxyController
from vigilo.turbogears.controllers.api.root import ApiRootController

from vigigraph.controllers.rpc import RpcController

__all__ = ['RootController']

LOGGER = logging.getLogger(__name__)

# pylint: disable-msg=R0201
class RootController(BaseController):
    """
    The root controller for the vigigraph application.
    """
    error = ErrorController()
    rpc = RpcController()
    nagios = ProxyController('nagios', '/nagios/',
        not_anonymous(l_('You need to be authenticated')))
    rrdgraph = ProxyController('rrdgraph', '/rrdgraph/',
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

    @expose('login.html')
    def login(self, came_from='/'):
        """Start the user login."""
        login_counter = request.environ['repoze.who.logins']
        if login_counter > 0:
            flash(_('Wrong credentials'), 'warning')
        return dict(page='login', login_counter=str(login_counter),
                    came_from=came_from)
    
    @expose()
    def post_login(self, came_from='/'):
        """
        Redirect the user to the initially requested page on successful
        authentication or redirect her back to the login page if login failed.
        
        """
        if not request.identity:
            login_counter = request.environ['repoze.who.logins'] + 1
            redirect('/login', came_from=came_from, __logins=login_counter)
        userid = request.identity['repoze.who.userid']
        LOGGER.info(_('"%(username)s" logged in (from %(IP)s)') % {
                'username': userid,
                'IP': request.remote_addr,
            })
        flash(_('Welcome back, %s!') % userid)
        redirect(came_from)

    @expose()
    def post_logout(self, came_from='/'):
        """
        Redirect the user to the initially requested page on logout and say
        goodbye as well.
        
        """
        LOGGER.info(_('Some user logged out (from %(IP)s)') % {
                'IP': request.remote_addr,
            })
        flash(_('We hope to see you soon!'))
        redirect(came_from)

