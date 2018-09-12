# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class res_users(models.Model):
    _inherit = 'res.users'

    is_financial_advisor = fields.Boolean(string="Is Financial Advisor")
    user_employee_roles_ids = fields.One2many('user.employee.roles', 'user_id')

    @api.multi
    @api.onchange('is_financial_advisor')
    def onchange_is_financial_advisor(self):
        if self.is_financial_advisor:
            self.user_employee_roles_ids = False
            user_employee_role_lst = []
            for each in self.env['employee.roles'].search([]):
                user_employee_role_lst.append((0, 0, {
                                                   'employee_role_id': each.id,
                                                   'employee_id': each.employee_id.id,
                                                   'financial_advisor_id': self._origin.id
                                                   }))
            self.user_employee_roles_ids = user_employee_role_lst


class UserEmployeeRoles(models.Model):
    _name = 'user.employee.roles'

    employee_role_id = fields.Many2one('employee.roles', string="Role")
    employee_id = fields.Many2one('res.users', string="Employee")
    financial_advisor_id = fields.Many2one('res.users', string="Financial Advisor")
    user_id = fields.Many2one('res.users', string="User")


class PortalWizardUser(models.TransientModel):
    _inherit = 'portal.wizard.user'

    @api.multi
    def action_apply(self):
        self.env['res.partner'].check_access_rights('write')
        """ From selected partners, add corresponding users to chosen portal group. It either granted
            existing user, or create new one (and add it to the group).
        """
        error_msg = self.get_error_messages()
        if error_msg:
            # Just ignore the creation user in case of error.
            return True
            #raise UserError("\n\n".join(error_msg))

        for wizard_user in self.sudo().with_context(active_test=False):
            group_portal = wizard_user.wizard_id.portal_id
            if not group_portal.is_portal:
                raise UserError(_('Group %s is not a portal') % group_portal.name)
            user = wizard_user.partner_id.user_ids[0] if wizard_user.partner_id.user_ids else None
            # update partner email, if a new one was introduced
            if wizard_user.partner_id.email != wizard_user.email:
                wizard_user.partner_id.write({'email': wizard_user.email})
            # add portal group to relative user of selected partners
            if wizard_user.in_portal:
                user_portal = None
                # create a user if necessary, and make sure it is in the portal group
                if not user:
                    if wizard_user.partner_id.company_id:
                        company_id = wizard_user.partner_id.company_id.id
                    else:
                        company_id = self.env['res.company']._company_default_get('res.users')
                    user_portal = wizard_user.sudo().with_context(company_id=company_id)._create_user()
                else:
                    user_portal = user
                wizard_user.write({'user_id': user_portal.id})
                if not wizard_user.user_id.active or group_portal not in wizard_user.user_id.groups_id:
                    wizard_user.user_id.write({'active': True, 'groups_id': [(4, group_portal.id)]})
                    # prepare for the signup process
                    wizard_user.user_id.partner_id.signup_prepare()
                    wizard_user.with_context(active_test=True)._send_email()
                wizard_user.refresh()
            else:
                # remove the user (if it exists) from the portal group
                if user and group_portal in user.groups_id:
                    # if user belongs to portal only, deactivate it
                    if len(user.groups_id) <= 1:
                        user.write({'groups_id': [(3, group_portal.id)], 'active': False})
                    else:
                        user.write({'groups_id': [(3, group_portal.id)]})
