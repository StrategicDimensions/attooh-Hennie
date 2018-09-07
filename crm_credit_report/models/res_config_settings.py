# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    mode = fields.Selection([
    	('test', 'Test'),
        ('production', 'Production')
    ], string="Mode", default='production')
    test_url = fields.Char(string='Test URL', default='https://www.uat.xds.co.za/xdsconnect/')
    production_url = fields.Char(string="Production URL", default='https://www.web.xds.co.za/xdsconnect/')
    username = fields.Char(string="Username", default='Collect_POC')
    password = fields.Char(string="Password", default='q7fzhc08')
    id_verification = fields.Char("ID Verification Operation Name")
    marital_status_verification = fields.Char(string="Marital Status Verification Operation Name")
    debt_review_verification = fields.Char(string="Debt Review Verification Operation Name")
    credir_report = fields.Char(string="Credit Report Operation Name")

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()

        res.update(
            mode = ICPSudo.get_param('crm_credit_report.mode', default='production'),
            test_url = ICPSudo.get_param('crm_credit_report.test_url', default='https://www.uat.xds.co.za/xdsconnect/'),
            production_url = ICPSudo.get_param('crm_credit_report.production_url', default='https://www.web.xds.co.za/xdsconnect/'),
            username = ICPSudo.get_param('crm_credit_report.username', default='Collect_POC'),
            password = ICPSudo.get_param('crm_credit_report.password', default='q7fzhc08'),
            id_verification = ICPSudo.get_param('crm_credit_report.id_verification'),
            marital_status_verification = ICPSudo.get_param('crm_credit_report.marital_status_verification'),
            debt_review_verification = ICPSudo.get_param('crm_credit_report.debt_review_verification'),
            credir_report = ICPSudo.get_param('crm_credit_report.credir_report')
        )
        return res

    @api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        ICPSudo.set_param("crm_credit_report.mode", self.mode)
        ICPSudo.set_param("crm_credit_report.test_url", self.test_url)
        ICPSudo.set_param("crm_credit_report.production_url", self.production_url)
        ICPSudo.set_param('crm_credit_report.username', self.username)
        ICPSudo.set_param('crm_credit_report.password', self.password)
        ICPSudo.set_param('crm_credit_report.id_verification', self.id_verification)
        ICPSudo.set_param('crm_credit_report.marital_status_verification', self.marital_status_verification)
        ICPSudo.set_param('crm_credit_report.debt_review_verification', self.debt_review_verification)
        ICPSudo.set_param('crm_credit_report.credir_report', self.credir_report)
