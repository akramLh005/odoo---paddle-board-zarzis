# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
import json
import calendar as cal
import random
import pytz
from datetime import datetime, timedelta, time
from dateutil import rrule
from dateutil.relativedelta import relativedelta
from odoo.tools.misc import babel_locale_parse, get_lang

from babel.dates import format_datetime, format_date, format_time
from werkzeug.urls import url_encode


class PaddleRequest(models.Model):
    _name = 'paddle.board'
    _inherit = ['mail.thread']
    _description = "Paddle Board Request"
    _order = "name Asc"

    is_contact = fields.Boolean(store=True, default=False)

    name = fields.Char(string="Name", tracking=True, required=True)
    nbr_person = fields.Integer(string="Number of Person", required=True, tracking=True)

    phone = fields.Char(string='Phone', required=True, tracking=True)

    user_id = fields.Many2one('res.users', string='Current User', readonly=True)
    date_id = fields.Many2one('paddle.date', string='Request Date')
    session_id2 = fields.Many2one('paddle.session', string='Request Session', tracking=True)

    state = fields.Selection([
        ('in_progress', 'In Progress '),
        ('approved', 'Approved'),
        ('canceled', 'Cancelled')
    ], string='Request State', readonly=True, default='in_progress', tracking=True)

    def action_approve(self):
        for rec in self:
            if rec.state == "in_progress":
                rec.write({
                    'state': 'approved'
                })

    def action_cancel(self):
        for rec in self:
            rec.write({
                'state': 'canceled'
            })

    def _get_appointment_slots(self, reference_date=None):
        """ Fetch available slots to book an appointment.

        :param datetime reference_date: starting datetime to fetch slots. If not
          given now (in UTC) is used instead. Note that minimum schedule hours
          defined on appointment type is added to the beginning of slots;

        :returns: list of dicts (1 per month) containing available slots per week
          and per day for each week (see ``_slots_generate()``), like
          [
            {'id': 0,
             'month': 'February 2022' (formatted month name),
             'weeks': [
                [{'day': '']
                [{...}],
             ],
            },
            {'id': 1,
             'month': 'March 2022' (formatted month name),
             'weeks': [ (...) ],
            },
            {...}
          ]
        """
        self.ensure_one()
        if not reference_date:
            reference_date = datetime.utcnow()

        requested_tz = pytz.timezone(self.env.user.tz or 'UTC')

        appointment_duration_days = self.max_schedule_days
        unique_slots = self.slot_ids.filtered(lambda slot: slot.slot_type == 'unique')

        if self.category == 'custom' and unique_slots:
            # With custom appointment type, the first day should depend on the first slot datetime
            start_first_slot = unique_slots[0].start_datetime
            first_day_utc = start_first_slot if reference_date > start_first_slot else reference_date
            first_day = requested_tz.fromutc(first_day_utc + relativedelta(hours=self.min_schedule_hours))
            appointment_duration_days = (unique_slots[-1].end_datetime.date() - reference_date.date()).days
        else:
            first_day = requested_tz.fromutc(reference_date + relativedelta(hours=self.min_schedule_hours))

        last_day = requested_tz.fromutc(reference_date + relativedelta(days=appointment_duration_days))

        # Compute available slots (ordered)
        slots = self._slots_generate(
            first_day.astimezone(pytz.utc),
            last_day.astimezone(pytz.utc),
            self.env.user.tz or 'UTC',
            reference_date=reference_date
        )

        # No slots -> skip useless computation
        # if not slots:
        #     return slots
        # valid_users = filter_users.filtered(lambda user: user in self.staff_user_ids) if filter_users else None
        # # Not found staff user : incorrect configuration -> skip useless computation
        # if filter_users and not valid_users:
        #     return []
        self._slots_available(
            slots,
            first_day.astimezone(pytz.UTC),
            last_day.astimezone(pytz.UTC)
        )

        total_nb_slots = sum('staff_user_id' in slot for slot in slots)
        nb_slots_previous_months = 0

        # Compute calendar rendering and inject available slots
        today = requested_tz.fromutc(reference_date)
        start = slots[0][self.env.user.tz or 'UTC'][0] if slots else today
        locale = babel_locale_parse(get_lang(self.env).code)
        month_dates_calendar = cal.Calendar(locale.first_week_day).monthdatescalendar
        months = []
        while (start.year, start.month) <= (last_day.year, last_day.month):
            nb_slots_next_months = sum('staff_user_id' in slot for slot in slots)
            has_availabilities = False
            dates = month_dates_calendar(start.year, start.month)
            for week_index, week in enumerate(dates):
                for day_index, day in enumerate(week):
                    mute_cls = weekend_cls = today_cls = None
                    today_slots = []
                    if day.weekday() in (locale.weekend_start, locale.weekend_end):
                        weekend_cls = 'o_weekend'
                    if day == today.date() and day.month == today.month:
                        today_cls = 'o_today'
                    if day.month != start.month:
                        mute_cls = 'text-muted o_mute_day'
                    else:
                        # slots are ordered, so check all unprocessed slots from until > day
                        while slots and (slots[0][self.env.user.tz or 'UTC'][0].date() <= day):
                            if (slots[0][self.env.user.tz or 'UTC'][0].date() == day) and ('staff_user_id' in slots[0]):
                                slot_staff_user_id = slots[0]['staff_user_id'].id
                                slot_start_dt_tz = slots[0][self.env.user.tz or 'UTC'][0].strftime('%Y-%m-%d %H:%M:%S')
                                slot = {
                                    'datetime': slot_start_dt_tz,
                                    'staff_user_id': slot_staff_user_id,
                                }
                                if slots[0]['slot'].allday:
                                    slot_duration = 24
                                    slot.update({
                                        'hours': _("All day"),
                                        'slot_duration': slot_duration,
                                    })
                                else:
                                    start_hour = format_time(slots[0][self.env.user.tz or 'UTC'][0].time(), format='short', locale=locale)
                                    end_hour = format_time(slots[0][self.env.user.tz or 'UTC'][1].time(), format='short', locale=locale)
                                    slot_duration = str((slots[0][self.env.user.tz or 'UTC'][1] - slots[0][self.env.user.tz or 'UTC'][0]).total_seconds() / 3600)
                                    slot.update({
                                        'hours': "%s - %s" % (start_hour, end_hour) if self.category == 'custom' else start_hour,
                                        'slot_duration': slot_duration,
                                    })
                                slot['url_parameters'] = url_encode({
                                    'staff_user_id': slot_staff_user_id,
                                    'date_time': slot_start_dt_tz,
                                    'duration': slot_duration,
                                })
                                today_slots.append(slot)
                                nb_slots_next_months -= 1
                            slots.pop(0)
                    today_slots = sorted(today_slots, key=lambda d: d['datetime'])
                    dates[week_index][day_index] = {
                        'day': day,
                        'slots': today_slots,
                        'mute_cls': mute_cls,
                        'weekend_cls': weekend_cls,
                        'today_cls': today_cls
                    }

                    has_availabilities = has_availabilities or bool(today_slots)

            months.append({
                'id': len(months),
                'month': format_datetime(start, 'MMMM Y', locale=get_lang(self.env).code),
                'weeks': dates,
                'has_availabilities': has_availabilities,
                'nb_slots_previous_months': nb_slots_previous_months,
                'nb_slots_next_months': nb_slots_next_months,
            })
            nb_slots_previous_months = total_nb_slots - nb_slots_next_months
            start = start + relativedelta(months=1)
        return months

    # def set_to_refuse(self):
    #     # wizard = self.env['state.refuse']
    #
    #     self.ensure_one()
    #     if not self.email:
    #         raise UserError(
    #             _("Missing email on  '%s'.") % self.name
    #         )
    #     template = self.env.ref('zarzis_park_erp.refuse_rental_request_email_template')
    #     compose_form = self.env.ref("mail.email_compose_message_wizard_form")
    #     ctx = dict(
    #         default_model="rental.submission",
    #         default_res_id=self.id,
    #         default_use_template=bool(template),
    #         default_template_id=template.id,
    #         default_composition_mode="comment",
    #     )
    #     action = {
    #         "name": _("Refuse Rental Request Email"),
    #         "type": "ir.actions.act_window",
    #         "view_mode": "form",
    #         "res_model": "mail.compose.message",
    #         "view_id": compose_form.id,
    #         "target": "new",
    #         "context": ctx,
    #     }
    #
    #     return action

    @api.model
    def get_contract_status(self):
        """
        This function will be used in the dashboard
        Get the number of contract depending on its state
        :return: dict
        """
        state_labels = {
            'in_progress': 'In Progress',
            'approved': 'Approved',
            'canceled': 'Canceled',
        }

        result = {'all_programs': self.search_count([]),
                  'all_days': self.env['paddle.date'].search_count([]),
                  'True_programs': self.env['paddle.date'].search_count([('is_published', '=', True)]),
                  'False_programs': self.env['paddle.date'].search_count([('is_published', '=', False)])
                  }

        for state_key, state_label in state_labels.items():
            result[state_key + '_programs'] = self.search_count([('state', '=', state_key)])

        return result
