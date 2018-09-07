# -*- coding: utf-8 -*-

from odoo import http, _
from odoo.http import request

from odoo.addons.portal.controllers.portal import get_records_pager, CustomerPortal, pager as portal_pager

class CustomerPortal(CustomerPortal):

    def _prepare_portal_layout_values(self):
        values = super(CustomerPortal, self)._prepare_portal_layout_values()
        Signature = request.env['signature.request']
        partner_id = request.env.user.partner_id.id
        signature = Signature.search([('request_item_ids.partner_id', '=', partner_id)])
        values['signature_count'] = len(signature)
        return values

    @http.route(['/my/signatures', '/my/signatures/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_signatures(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        Signature = request.env['signature.request']
        partner_id = request.env.user.partner_id.id
        signature = Signature.search([('request_item_ids.partner_id', '=', partner_id)])
        domain = [('id', 'in', signature.ids)]

        searchbar_sortings = {
            'date': {'label': _('Newest'), 'order': 'create_date desc'},
            'reference': {'label': _('Name'), 'order': 'reference'},
            'state': {'label': _('State'), 'order': 'state'},
        }
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']

        # archive groups - Default Group By 'create_date'
        archive_groups = self._get_archive_groups('signature.request', domain)
        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]
        # signatures count
        signature_count = Signature.search_count(domain)
        # pager
        pager = portal_pager(
            url="/my/signatures",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=signature_count,
            page=page,
            step=self._items_per_page
        )

        # TODO: TurboG(me) can we remove sodo and handle it with access rule ??
        signatures = Signature.sudo().search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_signature_history'] = signatures.ids[:100]

        values.update({
            'date': date_begin,
            'date_end': date_end,
            'signatures': signatures,
            'page_name': 'signatures',
            'archive_groups': archive_groups,
            'default_url': '/my/signatures',
            'pager': pager,
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby
        })
        return request.render("crm_attooh.portal_my_signatures", values)

    def has_signature_access(self, signature_id):
        Signature = request.env['signature.request']
        partner_id = request.env.user.partner_id.id
        signature = Signature.search([('request_item_ids.partner_id', '=', partner_id)])
        return signature_id in signature.ids and True or False

    @http.route(['/my/signature/<int:signature_id>'], type='http', auth="user", website=True)
    def portal_my_signature(self, signature_id=None, **kw):
        if self.has_signature_access(signature_id):
            signature = request.env['signature.request'].sudo().browse(signature_id)
            vals = {'signature': signature}
            history = request.session.get('my_signature_history', [])
            vals.update(get_records_pager(history, signature))
            return request.render("crm_attooh.portal_my_signature", vals)
        return request.redirect('/my')
