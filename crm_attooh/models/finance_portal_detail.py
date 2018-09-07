# -*- coding: utf-8 -*-
#
from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal

class CustomerPortal(CustomerPortal):

    @http.route(['/my/personalfinancial'], type='http', auth="user", website=True)
    def portal_my_personalfinance(self, meeting_id=None, edit_mode=None, **kw):
        partner = request.env.user.partner_id
        Income = request.env['partner.income']
        Expense = request.env['partner.expense']

        return request.render("crm_attooh.personalfinancial_detail", {
            'partner': partner,
            'spouse': partner.spouse_id,
            'edit_mode': edit_mode,
            'Income_obj': Income,
            'Expense': Expense
        })

    @http.route(['/my/beneficiaries'], type='http', auth="user", website=True)
    def portal_my_beneficiaries(self, meeting_id=None, edit_mode=None, **kw):
        partner = request.env.user.partner_id
        return request.render("crm_attooh.my_beneficiaries", {
            'partner': partner,
            'edit_mode': edit_mode,
        })

