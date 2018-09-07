# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class res_users(models.Model):
    _inherit = 'res.users'

    is_financial_advisor = fields.Boolean(string="Is Financial Advisor")
    user_employee_roles_ids = fields.One2many('user.employee.roles','user_id')

    @api.multi
    @api.onchange('is_financial_advisor')
    def onchange_is_financial_advisor(self):
        if self.is_financial_advisor:
            self.user_employee_roles_ids = False
            user_employee_role_lst = []
            for each in self.env['employee.roles'].search([]):
                user_employee_role_lst.append((0,0,{
                                                   'employee_role_id':each.id,
                                                   'employee_id':each.employee_id.id,
                                                   'financial_advisor_id':self._origin.id
                                                   }))
            self.user_employee_roles_ids = user_employee_role_lst


class UserEmployeeRoles(models.Model):
    _name = 'user.employee.roles'

    employee_role_id = fields.Many2one('employee.roles', string="Role")
    employee_id = fields.Many2one('res.users', string="Employee")
    financial_advisor_id = fields.Many2one('res.users', string="Financial Advisor")
    user_id = fields.Many2one('res.users', string="User")