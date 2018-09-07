from odoo import models, api


class Meeting(models.Model):
    """ Model for Calendar Event

        Special context keys :
            - `no_mail_to_attendees` : disabled sending email to attendees when creating/editing a meeting
    """

    _inherit = 'calendar.event'

    @api.model
    def default_get(self, fields):
        defaults = super(Meeting, self).default_get(fields)
        defaults.update({'alarm_ids': [(6, 0, [self.env.ref('attooh_sms.alarm_sms_attooh_1').id, self.env.ref('attooh_sms.alarm_sms_attooh_2').id])]})
        return defaults