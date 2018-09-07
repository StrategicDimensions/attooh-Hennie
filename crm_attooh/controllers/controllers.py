# -*- coding: utf-8 -*-
from odoo import http

# class CrmAttooh(http.Controller):
#     @http.route('/crm_attooh/crm_attooh/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/crm_attooh/crm_attooh/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('crm_attooh.listing', {
#             'root': '/crm_attooh/crm_attooh',
#             'objects': http.request.env['crm_attooh.crm_attooh'].search([]),
#         })

#     @http.route('/crm_attooh/crm_attooh/objects/<model("crm_attooh.crm_attooh"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('crm_attooh.object', {
#             'object': obj
#         })