from odoo import models, fields, api, _
from datetime import datetime


class res_partner(models.Model):
    _inherit = 'res.partner'

    @api.model
    def send_entity(self, template_name):
        if template_name:
            template_name = str(template_name)
            parter_ids = self.env['res.partner'].browse(self._context.get('active_ids'))
            """Attempt to send the sms, if any error comes back show it to the user and only log the smses that successfully sent"""
            for each in parter_ids:
                flag =False
                sms_number_id = self.env['sms.number'].search([('mobile_number', '=', '0000000000')], limit=1, order="id desc")
                if sms_number_id:
                    gateway_model = sms_number_id.account_id.account_gateway_id.gateway_model_name
                    sms_template_id = self.env['sms.template'].search([('name', '=', template_name)], limit=1, order="id desc")
                    if not sms_template_id:
                        self.env['sms.template'].create({
                                                 'name': template_name,
                                                 'model_id': self.env['ir.model'].search([('model', '=', self._context.get('active_model'))]).id,
                                                 'from_mobile_verified_id': self.env('sms_frame.sms_number_default').id,
                                                 'from_mobile': '0000000000',
                                                 'template_body': ""})
                    sms_body = self.env['sms.template'].render_template(sms_template_id.template_body, sms_template_id.model_id.model, each.id)
#                     sms_body = sms_template_id.template_body
    #                 sms_body = each.name + ' ,We have noticed that we dont have your email address kindly reply with your email address. attooh'
                    my_sms = sms_number_id.account_id.send_message(sms_number_id.mobile_number, each.mobile, sms_body.encode('utf-8'), self._context.get('active_model'), each.id, False)[0]
                    error_message = my_sms['error']
                    #display the screen with an error code if the sms/mms was not successfully sent
                    if my_sms['errorCode'] != False:
                        flag =False
                    else:
                        flag = True
                    #for single smses we only record succesful sms, failed ones reopen the form with the error message
                    if flag:
                        sms_message = self.env['sms.message'].create({
                            'record_id': each.id,
                            'model_id': self.env['ir.model'].search([('model', '=', self._context.get('active_model'))]).id,
                            'account_id': sms_number_id.account_id.id,
                            'from_mobile': sms_number_id.mobile_number,
                            'to_mobile': each.mobile,
                            'sms_content': sms_body,
                            'status_string': my_sms['error'],
                            'direction': 'O',
                            'message_date': datetime.utcnow(),
                            'status_code': my_sms['errorCode'],
                            'sms_gateway_message_id': my_sms['id'],
                            'by_partner_id': self.env.user.partner_id.id,
                            'mass_sms_id': self.env.context.get('mass_sms_id', False),
                        })
                        sms_subtype = self.env['ir.model.data'].get_object('sms_frame', 'sms_subtype')
                        self.env['res.partner'].search([('id','=', each.id)]).message_post(body=sms_body, subject="SMS Sent", message_type="comment", subtype_id=sms_subtype.id if sms_subtype else False, attachments=[])