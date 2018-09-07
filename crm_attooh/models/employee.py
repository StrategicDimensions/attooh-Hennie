from odoo import models, fields, api, _

class EmployeeRole(models.Model):
    _name = 'employee.roles'

    name = fields.Char('Name')
    employee_id = fields.Many2one('res.users', required="True", string="Employee")

    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'Name must be unique.')
    ]

