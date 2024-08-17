# -*- coding: utf-8 -*-
import calendar as cal
from babel.dates import format_datetime, format_time

from odoo.tools.misc import babel_locale_parse, get_lang

from odoo import models, fields, api, _
from datetime import datetime
from dateutil.relativedelta import relativedelta
import calendar


class PaddleDate(models.Model):
    _name = 'paddle.date'
    _inherit = ['mail.thread']
    _description = "Paddle Board Date"
    _order = "date Asc"
    _rec_name = 'date'

    is_available = fields.Boolean(store=True, default=True)
    is_published = fields.Boolean(store=True, default=False)

    sequence = fields.Integer('Sequence')
    date = fields.Date(string="Date")

    max_nbr_person = fields.Integer(string="Max", tracking=True)
    session_ids = fields.One2many('session.lines', 'date_id', string='Sessions')
    request_ids = fields.One2many('paddle.board', 'date_id', string='Current User', readonly=True)

    def get_available_appointment_months(self):
        """ Fetch available months with weeks for booking appointments.

        :returns: list of dicts (1 per month) containing weeks with day information and available appointment slots
        """
        self.ensure_one()
        today = datetime.now()  # Assuming users are in Tunis time (Africa/Tunis)

        locale = babel_locale_parse(get_lang(self.env).code)
        month_dates_calendar = cal.Calendar(locale.first_week_day).monthdatescalendar

        months = []
        # Start date can be today or another date based on your requirement
        start_date = today  # Replace with desired starting date if needed

        # Iterate through the next 3 months (adjust as needed)
        for i in range(3):
            dates = month_dates_calendar(start_date.year, start_date.month)
            month_weeks = []
            for week in dates:
                week_days = []
                for day in week:
                    # Check available slots (assuming a single session per date)
                    available_slots = self.env['paddle.date'].search_count([
                        ('date', '=', day),
                        ('is_published', '=', True),  # Check for available dates
                    ])

                    # Calculate remaining slots if max_nbr_person is set
                    remaining_slots = available_slots if available_slots else None
                    # if self.max_nbr_person and available_slots:
                    #     # Assuming reservations are stored in 'request_ids'
                    #     reservations = self.env['paddle.board'].search_count([
                    #         ('date_id', '=', self.id),
                    #         ('date', '=', day),
                    #     ])
                    #     remaining_slots = max(0, available_slots - reservations)

                    # Create a dictionary for each day with relevant information
                    day_dict = {
                        'day': day,
                        'weekend_cls': day.weekday() in (calendar.SUNDAY, calendar.SATURDAY) or '',
                        'today_cls': day == today and 'bg-primary text-white' or '',
                        'slots': remaining_slots,  # Indicate remaining slots (or available_slots if max_nbr_person not set)
                    }
                    week_days.append(day_dict)
                month_weeks.append(week_days)
            months.append({
                'id': i,  # Unique identifier for the month (counter)
                'month': format_datetime(start_date, 'MMMM Y', locale=get_lang(self.env).code),
                'weeks': month_weeks,
            })
            start_date = start_date + relativedelta(months=1)

        return months

    @api.model
    def get_active_sessions(self, id):
        """ Search for active sessions associated with the provided date ID.
        """

        # Assuming 'id' is the actual date ID (YYYY-MM-DD format)
        date_obj = datetime.strptime(id, '%Y-%m-%d').date()  # Convert ID to date object

        active_sessions = self.env['paddle.date'].search([
            ('date', '=', date_obj),
        ])

        # Prepare a list of dictionaries for the active sessions
        session_data = []
        for session in active_sessions.session_ids:
            if session.nbr_place_taken < active_sessions.max_nbr_person:
                session_data.append({
                    'id': session.id,
                    'name': session.session_id.complete_name,  # Assuming 'name' field exists in 'session.lines' model
                })

        return session_data

    @api.model
    def get_places_left(self, date_id, session_id):
        """ Search for active sessions associated with the provided date ID.
        """

        # Assuming 'id' is the actual date ID (YYYY-MM-DD format)
        date_obj = datetime.strptime(date_id, '%Y-%m-%d').date()  # Convert ID to date object

        active_sessions = self.env['paddle.date'].search([
            ('date', '=', date_obj),
        ])

        # Prepare a list of dictionaries for the active sessions
        max_number = []
        for session in active_sessions.session_ids:
            if session.session_id.id == int(session_id):
                max_number.append({
                    'max_number': int(active_sessions.max_nbr_person - session.nbr_place_taken)
                })
                break

        return max_number

    @api.model
    def get_contract_status(self):
        """
        This function will be used in the dashboard
        Get the number of contract depending on its state
        :return: dict
        """

        result = {'all_days': self.search_count([]), 'True_programs': self.search_count([('is_published', '=', True)]),
                  'False_programs': self.search_count([('is_published', '=', False)])}

        return result


class SessionLines(models.Model):
    _name = 'session.lines'
    _inherit = ['mail.thread']
    _description = "Session Date Lines"

    date_id = fields.Many2one('paddle.date')
    session_id = fields.Many2one('paddle.session')

    from_time = fields.Text(related="session_id.from_time")
    to_time = fields.Text(related="session_id.to_time")

    session_state = fields.Selection(related="session_id.session_state")

    nbr_place_taken = fields.Integer(string="Taken", default=0)
    
