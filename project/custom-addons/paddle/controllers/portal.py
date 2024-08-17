# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import json

from odoo import http, _
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.exceptions import AccessError, MissingError
from collections import OrderedDict
from odoo.http import request

from babel.dates import format_datetime, format_date, format_time
from datetime import datetime, date
from odoo.tools.misc import babel_locale_parse, get_lang

def _formated_weekdays(locale):
    """ Return the weekdays' name for the current locale
        from Mon to Sun.
        :param locale: locale
    """
    formated_days = [
        format_date(date(2021, 3, day), 'EEE', locale=locale)
        for day in range(1, 8)
    ]
    # Get the first weekday based on the lang used on the website
    first_weekday_index = babel_locale_parse(locale).first_week_day
    # Reorder the list of days to match with the first weekday
    formated_days = list(formated_days[first_weekday_index:] + formated_days)[:7]
    return formated_days


class PortalPaddle(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'invoice_count' in counters:
            invoice_count = request.env['paddle.board'].search_count(self._get_invoices_domain()) \
                if request.env['paddle.board'].check_access_rights('read', raise_exception=False) else 0
            values['invoice_count'] = invoice_count
        return values

    # ------------------------------------------------------------
    # My Invoices
    # ------------------------------------------------------------

    # def _invoice_get_page_view_values(self, invoice, access_token, **kwargs):
    #     values = {
    #         'page_name': 'invoice',
    #         'invoice': invoice,
    #     }
    #     return self._get_page_view_values(invoice, access_token, values, 'my_invoices_history', False, **kwargs)
    #
    def _get_invoices_domain(self):
        return [('state', 'not in', ('cancel', 'draft')), ('move_type', 'in', ('out_invoice', 'out_refund', 'in_invoice', 'in_refund', 'out_receipt', 'in_receipt'))]

    @http.route('/my/details', type='http', auth="user", website=True)
    def portal_my_paddle_details(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, **kw):
        values = self._prepare_my_invoices_values(page, date_begin, date_end, sortby, filterby)

        # content according to pager and archive selected
        invoices = request.env['paddle.board'].sudo().search([('user_id', '=', request.env.user.id)])
        request.session['my_invoices_history'] = invoices.ids[:100]
        values['task_count'] = request.env['paddle.board'].search_count([])

        values.update({
            'invoices': invoices,
        })
        return request.render("paddle.portal_my_paddle2", values)

    @http.route('/my/request', type='http', auth="user", website=True, csrf=False)
    def portal_my_paddle_request2(self, page=1, date_begin=None, date_end=None, sortby=None, filterby=None, **kw):
        values = self._prepare_my_invoices_values(page, date_begin, date_end, sortby, filterby)

        # content according to pager and archive selected
        invoices = request.env['paddle.board'].sudo().search([('user_id', '=', request.env.user.id)])
        available_dates = request.env['paddle.date'].sudo().search([('is_available', '=', True),
                                                                    ('is_published', '=', True)])
        sessions = request.env['paddle.session'].sudo().search([])

        values.update({
            'invoices': invoices,
            'available_dates': available_dates,
            'sessions': sessions,
            'formated_days': _formated_weekdays(get_lang(request.env).code),
            'available_months': available_dates[0].get_available_appointment_months(),
        })
        return request.render("paddle.apply-paddle", values)

    @http.route('/website/form/paddle.board.order', type='http', auth="public", methods=['POST'], website=True)
    def website_form_paddleboard(self, **kwargs):
        if kwargs:
            rec = request.env['paddle.board'].sudo().create({
                "name": kwargs.get('name'),
                "nbr_person": kwargs.get('nbr_person'),
                "phone": kwargs.get('phone'),
                "user_id": request.env.user.id,
                "date_id": kwargs.get('date_id'),
                "session_id2": kwargs.get('session_id2'),
            })
            date = request.env['paddle.date'].sudo().search([('id', '=', kwargs.get('date_id'))])

            total_nbr_place_taken = 0
            for line in date.session_ids:
                if line.session_id.id == int(kwargs.get('session_id2')):
                    line.nbr_place_taken += int(kwargs.get('nbr_person'))
                total_nbr_place_taken += line.nbr_place_taken
                if total_nbr_place_taken >= date.max_nbr_person * len(date.session_ids.ids):
                    date.is_published = False
                    break

        return json.dumps({'id': rec.id})

    def _prepare_my_invoices_values(self, page, date_begin, date_end, sortby, filterby, domain=None, url="/my/invoices"):
        values = self._prepare_portal_layout_values()

        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        values.update({
            'date': date_begin,
        })
        return values
