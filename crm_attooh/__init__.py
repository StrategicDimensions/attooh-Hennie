# -*- coding: utf-8 -*-

from . import controllers
from . import models
from odoo import models, api
from odoo import SUPERUSER_ID


def post_init_check(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    module_name = env['ir.module.module'].search([('name', '=', 'helpdesk'),('state','!=','installed')], limit=1)
    if module_name:
        ticket_1_id = env.ref("helpdesk.type_incident")
        ticket_2_id = env.ref("helpdesk.type_question")
        if ticket_1_id:
            ticket_1_id.unlink()
        if ticket_2_id:
            ticket_2_id.unlink()