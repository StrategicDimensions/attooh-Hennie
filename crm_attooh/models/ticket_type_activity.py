from odoo import models, fields, api, _


class ticket_type_activity(models.Model):
    _name = 'ticket.type.activity'
    _description = 'Ticket Type Activity'

    name = fields.Char(string='Summary', required=True)
    activity_date = fields.Integer(string="Activity Date")
    assign_to_owner = fields.Boolean(string="Assign to Owner?")
    activity_type_id = fields.Many2one('mail.activity.type', string="Activity Type")
    user_id = fields.Many2one('res.users', string="Assigned To")
    employee_role_id = fields.Many2one('employee.roles', string="Assigned To")
    ticket_type_id = fields.Many2one('helpdesk.ticket.type', string="Ticket Type")
    active = fields.Boolean(default=True)
