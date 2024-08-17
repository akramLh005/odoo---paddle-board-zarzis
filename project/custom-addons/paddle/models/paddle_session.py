# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class PaddleSession(models.Model):
    _name = 'paddle.session'
    _inherit = ['mail.thread']
    _description = "Paddle Board Session"
    _order = "from_time"
    _rec_name = 'complete_name'

    name = fields.Char('Session Name')
    complete_name = fields.Char('Complete Name', compute='_compute_complete_name', recursive=True, store=True)
    from_time = fields.Text(string="From", required=True, tracking=True)
    to_time = fields.Text(string="To", required=True, tracking=True)

    session_state = fields.Selection([
        ('sunrise', 'Sunrise'),
        ('noon', 'Noon'),
        ('sunset', 'Sunset')
    ], string='Session State', default='sunrise', tracking=True)

    request_ids = fields.One2many('paddle.board', 'session_id2', string='Hide field', readonly=True)

    def name_get(self):
        return [(record.id, "%s - %s" % (record.from_time, record.to_time)) for record in self]

    @api.depends('from_time', 'to_time')
    def _compute_complete_name(self):
        for rec in self:
            rec.complete_name = '%s - %s' % (rec.from_time, rec.to_time)
