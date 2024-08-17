from odoo.http import request, SessionExpiredException
from odoo.addons.portal.controllers.web import Home


class Website(Home):

    def _login_redirect(self, uid, redirect=None):
        """ Redirect regular users (employees) to the backend) and others to
        the frontend
        """
        if not redirect and request.params.get('login_success'):
            if request.env['res.users'].browse(uid)._is_internal():
                redirect = '/web?' + request.httprequest.query_string.decode()
            else:
                redirect = '/'
        return super()._login_redirect(uid, redirect=redirect)
