# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from clickatell.http import Http

from odoo import api, fields, models


class SmsGatewayClickatell(models.Model):
    _name = "sms.gateway.clickatell"

    @api.multi
    def send_message(self, sms_gateway_id, from_number, to_number, sms_content, my_model_name='', my_record_id=0, media=None, queued_sms_message=None):
        sms_account = self.env['sms.account'].search([('id', '=', sms_gateway_id)], limit=1, order="id desc")
        clickatell1 = Http(sms_account.clicKatell_username, sms_account.clicKatell_password, sms_account.clicKatell_api)

        response = clickatell1.sendMessage(to_number, sms_content.decode('utf-8') if not isinstance(sms_content, str) else sms_content)
#         response = clickatell1.sendMessage(to_number, sms_content.decode('utf-8'), {'from': '41798073057'})
        return response

    def check_messages(self, account_id, message_id=""):
        return True

    def _add_message(self, sms_message, account_id):
        return True


class SmsAccountClickatell(models.Model):
    _inherit = "sms.account"
    _description = "Adds the Clickatell specific gateway settings to the sms gateway accounts"

    clicKatell_username = fields.Char(string='Username')
    clicKatell_password = fields.Char(string='Password')
    clicKatell_api = fields.Char(string="API Key")
