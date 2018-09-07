# -*- coding: utf-8 -*-

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    module_crm_credit_report = fields.Boolean("XDS - Credit Bureau Integration")
