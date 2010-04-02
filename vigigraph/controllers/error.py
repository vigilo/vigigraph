# -*- coding: utf-8 -*-
"""Error controller"""

from tg import request, expose

__all__ = ['ErrorController']

# pylint: disable-msg=R0201
class ErrorController(object):
    """
    Generates error documents as and when they are required.

    The ErrorDocuments middleware forwards to ErrorController when error
    related status codes are returned from the application.

    This behaviour can be altered by changing the parameters to the
    ErrorDocuments middleware in your config/middleware.py file.
    
    """

    @expose('error.html')
    def document(self, *args, **kwargs):
        """Render the error document"""
        resp = request.environ.get('pylons.original_response')
        default_message = ("<p>We're sorry but we weren't able to process "
                           " this request.</p>")
        values = dict(prefix=request.environ.get('SCRIPT_NAME', ''),
                      code=request.params.get('code', resp.status_int),
                      message=request.params.get('message', default_message))
        return values

    @expose()
    def rrd_txt_error(self, **kwargs):
        """
        Gestion erreur rrd
        
        @param kwargs : arguments nommes
        @type kwargs  : dict
                          (pour la clé 'txt', contient le texte) 

        @return: texte de l erreur
        @rtype  : C{str}
        """

        txt = None
        if kwargs is not None:
            txt = kwargs.get('txt')
        return txt

    @expose('rrd_error.html')
    def rrd_error(self, **kwargs):
        """
        Gestion erreur rrd
        
        @param kwargs : arguments nommes
        @type kwargs  : dict
                          (pour la clé 'host', contient l'hôte) 

        @return: page erreur
        @rtype: page (-> dict sur template rrd_error.html)
        """

        host = None
        if kwargs is not None:
            host = kwargs.get('host')
            return dict(host=host)
        else:
            return None

    @expose('rrd_error.html')
    def rrd_exportCSV_error(self, **kwargs):
        """
        Gestion erreur rrd sur export CSV
        
        @param kwargs : arguments nommes
        @type kwargs  : dict
                          (pour la clé 'host', contient l'hôte) 

        @return: page erreur
        @rtype: page (-> dict sur template rrd_error.html)
        """

        host = None
        if kwargs is not None:
            host = kwargs.get('host')
            return dict(host=host)
        else:
            return None

    @expose('nagios_host_error.html')
    def nagios_host_error(self, **kwargs):
        """
        Gestion erreur nagios sur l hote
        
        @param kwargs : arguments nommes
        @type kwargs  : dict

        @return: page erreur
        @rtype: page
        
        (arguments nommes : pour la clé 'host', contient l'hôte) 
        """

        host = None
        if kwargs is not None:
            host = kwargs.get('host')
            return dict(host=host)
        else:
            return None

    @expose('nagios_host_service_error.html')
    def nagios_host_service_error(self, **kwargs):
        """
        Gestion erreur nagios sur l'hote et le service
        
        @param kwargs : arguments nommes
        @type kwargs  : dict
                          (pour la clé 'host', contient l'hôte) 
                          (pour la clé 'service', contient le service) 

        @return: page erreur
        @rtype: page (-> dict sur template nagios_host_service_error.html)
        """

        host = None
        service = None
        if kwargs is not None:
            host = kwargs.get('host')
            service = kwargs.get('service')
            return dict(host=host, service=service)
        else:
            return None

