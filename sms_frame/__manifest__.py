# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': "SMS Framework",
    'author': "Sythil Tech",
    'category': "Tools",
    'support': "steven@sythiltech.com.au",
    'summary':'Allows you to send and receive smses from multiple gateways',
    'description':'Allows you to send and receive smses from multiple gateways',    
    'license':'LGPL-3',
    'data': [
        # 'data/ir.cron.csv',
        # 'data/res.country.csv',
        'data/ir.model.access.csv',
        'data/sms.gateway.csv',
        'data/mail.message.subtype.csv',
        'data/sms_data.xml',
        'data/clickatell_data.xml',
        'views/sms_views.xml',
        'views/res_partner_views.xml',
        'views/sms_message_views.xml',
        'views/sms_template_views.xml',
        'views/sms_account_views.xml',
        'views/sms_number_views.xml',
        'views/sms_compose_views.xml',
        'views/ir_actions_server_views.xml',
        'views/ir_actions_todo.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [],
    'depends': ['mail'],
    'images':[
        'static/description/3.jpg',
    ],
    'qweb': ['static/src/xml/sms_compose.xml'],
    'installable': True,
}
