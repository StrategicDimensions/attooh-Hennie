# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
from odoo import models, _
_logger = logging.getLogger(__name__)
from clickatell.http import Http

class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'

    def message_post_send_sms(self, sms_message, numbers=None, partners=None, note_msg=None, log_error=False):
        """ This is the custom method especially made for Clickatell api call // Added by Dhruvil
            Send an SMS text message and post an internal note in the chatter if successfull
            :param sms_message: plaintext message to send by sms
            :param partners: the numbers to send to, if none are given it will take those
                                from partners or _get_default_sms_recipients
            :param partners: the recipients partners, if none are given it will take those
                                from _get_default_sms_recipients, this argument
                                is ignored if numbers is defined
            :param note_msg: message to log in the chatter, if none is given a default one
                             containing the sms_message is logged
        """
        if not numbers:
            if not partners:
                partners = self._get_default_sms_recipients()

                # Collect numbers, we will consider the message to be sent if at least one number can be found
                numbers = list(set([i.mobile for i in partners if i.mobile]))
        if numbers:
            try:
                sms_account_id = self.env['sms.account'].search([], limit=1, order="id desc")
                if sms_account_id:
                    sms_number_id = self.env['sms.number'].search([], limit=1, order="id desc")
                    from_number = sms_number_id.mobile_number if sms_number_id else ''
                    for each_number in numbers:
                        sms_account_id.send_message(from_number, each_number, sms_message, 'calendar.event', False, False)[0]
                else: pass
            except Exception as e:
                if not log_error:
                    raise e
#                 mail_message = _('Insufficient credit, unable to send SMS message: %s') % sms_message
#         else:
#             mail_message = _('No mobile number defined, unable to send SMS message: %s') % sms_message
#         for thread in self:
#             thread.message_post(body=mail_message)
        return False
