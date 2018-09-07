from odoo import models, fields, api, _
from datetime import date


class mail_activity(models.Model):
    _name = 'stage.activity'

    name = fields.Char(string='Summary', required=True)
    active = fields.Boolean(default=True)
    activity_date = fields.Integer(string="Activity Date")
    assign_to_owner = fields.Boolean(string="Assign to Owner?")
    activity_type_id = fields.Many2one('mail.activity.type', string="Activity Type")
    employee_role_id = fields.Many2one('employee.roles', string="Employee Role")
#     user_id = fields.Many2one('employee.roles', string="Assigned To")
    user_id = fields.Many2one('res.users', string="Assigned To")
    team_ids = fields.Many2many('crm.team', 'activity_stage_rel', 'activity_id', 'stage_id', string='Teams')
    crm_stage_id = fields.Many2one('crm.stage', string="Stage")

#     @api.depends('date_deadline')
#     def _compute_activity_date(self):
#         for each in self:
#             if each.date_deadline:
#                 each.activity_date = (fields.Date.from_string(each.date_deadline) - date.today()).days


class MailActivity(models.Model):
    _inherit = 'mail.activity'

    stage_activity_id = fields.Many2one('stage.activity', string="Stage Activity")

    @api.model
    def create(self, values):
        # already compute default values to be sure those are computed using the current user
        values_w_defaults = self.default_get(self._fields.keys())
        values_w_defaults.update(values)

        # continue as sudo because activities are somewhat protected
        activity = super(models.Model, self.sudo()).create(values_w_defaults)
        activity_user = activity.sudo(self.env.user)
        activity_user._check_access('create')
        if activity.date_deadline <= fields.Date.today():
            self.env['bus.bus'].sendone(
                (self._cr.dbname, 'res.partner', activity.user_id.partner_id.id),
                {'type': 'activity_updated', 'activity_created': True})
        return activity_user

class CrmAutomatedEmails(models.Model):
    _name = "crm.automated.email"

    crm_stage_id = fields.Many2one('crm.stage', string="Stage")
    email_template_id = fields.Many2one('mail.template', domain=[('model', '=', 'crm.lead')], string='Email Templates', request=True)
    user_id = fields.Many2one('res.users', string='Users', required=True)


class CrmSignatureRequest(models.Model):
    _name = "crm.signature.request"

    crm_stage_id = fields.Many2one('crm.stage', string="Stage")
    signature_request_template_id = fields.Many2one('signature.request.template', string='Signature Request Templates', required=True)
    user_id = fields.Many2one('res.users', string='Users', required=True)


class crm_stage(models.Model):
    _inherit = 'crm.stage'

    team_ids = fields.Many2many('crm.team', 'crm_team_stage_rel', 'team_id', 'stage_id', string='Teams')
    stage_activity_ids = fields.One2many('stage.activity', 'crm_stage_id', string="Activities")
    stage_automated_email_ids = fields.One2many('crm.automated.email', 'crm_stage_id', string="Email Templates")
    stage_signature_request_ids = fields.One2many('crm.signature.request', 'crm_stage_id', string="Signature Request")
    has_portal_access = fields.Boolean('Subscribe to Portal')
