# -*- coding:utf-8 -*-

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    payment_acceptance = fields.Selection([
        ('100', '100'),
        ('50', '50'),
    ], string="Payment % on Acceptance", default='50')
    payment_on_acceptance = fields.Monetary(compute='_compute_payment_amount', string='Payment on Acceptance')
    payment_on_completion = fields.Monetary(compute='_compute_payment_amount', string='Payment on Completion')

    def _compute_payment_amount(self):
        for order in self:
            payment_on_acceptance = payment_on_completion = 0.00
            if order.payment_acceptance == '50':
                payment_on_acceptance = (order.amount_total * 50.00) / 100.00
                payment_on_completion = (order.amount_total * 50.00) / 100.00
            elif order.payment_acceptance == '100':
                payment_on_acceptance = order.amount_total
                payment_on_completion = 0.00
            order.payment_on_acceptance = payment_on_acceptance
            order.payment_on_completion = payment_on_completion

    @api.multi
    def action_confirm(self):
        self.ensure_one()
        res = super(SaleOrder, self).action_confirm()
        if self.opportunity_id:
            self.opportunity_id.action_set_won()
        return res

    @api.model
    def create(self, vals):
        order = super(SaleOrder, self).create(vals)
        opportunity_id = vals.get('opportunity_id')
        if opportunity_id:
            opportunity = self.env['crm.lead'].browse(opportunity_id)
            if opportunity.planned_revenue == 0:
                opportunity.planned_revenue = order.amount_untaxed
        return order
