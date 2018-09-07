# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Credit Report',
    'category': 'Sales',
    'sequence': 60,
    'summary': 'Credit Report',
    'description': "",
    'website': 'https://www.odoo.com/',
    'depends': ['crm_attooh'],
    'data': [
        'views/res_config_settings_views.xml',
        'report/credit_report.xml',
        'data/server_action_data.xml',
    ],
    'qweb': [
    ],
    'test': [
    ],
    'demo': [
    ],
    'installable': True,
    'auto_install': False,
}
