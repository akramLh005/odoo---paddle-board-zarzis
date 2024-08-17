# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


{
    'name': 'Paddle Board Zarzis',
    'version': '16.0',
    'category': 'Project Paddle Board',
    'author': "Wael Dhaoui",
    'description': """


""",
    'depends': ['website', 'mail', 'web', 'base', 'portal', 'web_domain_field'],
    'data': [
        'security/ir.model.access.csv',
        'data/website_form_paddle_request.xml',
        # 'data/custom_layout.xml',
        'views/paddle_request.xml',
        'views/paddle_session.xml',
        'views/paddle_date.xml',
        'views/paddle_request_portal.xml',
        'views/menu.xml',
    ],

    'demo': [],
    'license': 'LGPL-3',
    'installable': True,
    'application': True,
    'auto_install': False,
    'assets': {
        'web.assets_frontend': [
            'paddle/static/src/scss/appointment.scss',
            'paddle/static/src/js/appointment_select_appointment_slot.js',
            'paddle/static/src/js/website_form_send.js',
        ],
        'web.assets_backend': [
            'paddle/static/src/xml/dashboard.xml',
            'paddle/static/src/js/dashboard.js',

        ],
    }
}
