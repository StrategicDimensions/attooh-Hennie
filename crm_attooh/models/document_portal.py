# -*- coding: utf-8 -*-

from odoo import http, _
from odoo.http import request
import base64
from odoo.addons.portal.controllers.portal import get_records_pager, CustomerPortal, pager as portal_pager

class CustomerPortal(CustomerPortal):

    def _prepare_portal_layout_values(self):
        values = super(CustomerPortal, self)._prepare_portal_layout_values()
        Attachment = request.env['ir.attachment']
        partner_id = request.env.user.partner_id
        attachments = Attachment.search([('res_model', '=', 'res.partner'), ('document_available', '=', True), ('res_id', '=', partner_id.id)])
        values['document_count'] = len(attachments)
        return values

    @http.route(['/my/attachments', '/my/attachments/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_attachments(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        Attachment = request.env['ir.attachment']
        partner_id = request.env.user.partner_id
        attachments = Attachment.search([('res_model', '=', 'res.partner'), ('document_available', '=', True), ('res_id', '=', partner_id.id)])
        domain = [('id', 'in', attachments.ids)]

        searchbar_sortings = {
            'date': {'label': _('Newest'), 'order': 'create_date desc'},
            'name': {'label': _('Name'), 'order': 'name'},
        }
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']

        # archive groups - Default Group By 'create_date'
        archive_groups = self._get_archive_groups('ir.attachment', domain)
        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]
        # attachments count
        attachment_count = Attachment.search_count(domain)
        # pager
        pager = portal_pager(
            url="/my/attachments",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=attachment_count,
            page=page,
            step=self._items_per_page
        )

        attachments = Attachment.search(domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_attachment_history'] = attachments.ids[:100]

        values.update({
            'date': date_begin,
            'date_end': date_end,
            'attachments': attachments,
            'attachment_count': attachment_count,
            'page_name': 'attachments',
            'archive_groups': archive_groups,
            'default_url': '/my/attachments',
            'pager': pager,
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby
        })
        
        return request.render("crm_attooh.portal_my_attachments", values)

    def has_attachment_access(self, attachment_id):
        Attachment = request.env['ir.attachment']
        partner_id = request.env.user.partner_id
        attachments = Attachment.search([('res_model', '=', 'res.partner'), ('document_available', '=', True), ('res_id', '=', partner_id.id)])
        return attachment_id in attachments.ids and True or False

    @http.route(['/my/attachment/<int:attachment_id>'], type='http', auth="user", website=True)
    def portal_my_attachment(self, attachment_id=None, **kw):
        if self.has_attachment_access(attachment_id):
            attachment = request.env['ir.attachment'].sudo().browse(attachment_id)
            vals = {'attachment': attachment}
            history = request.session.get('my_attachment_history', [])
            vals.update(get_records_pager(history, attachment))
            return request.render("crm_attooh.portal_my_attachment", vals)
        return request.redirect('/my')
    
    @http.route('/upload_document', type='http', auth="public", website=True)
    def upload_document(self, **post):
        filename = post.get('doc_attachment').filename
        file = post.get('doc_attachment')
        attach_id = request.env['ir.attachment'].create({
                        'name' : filename,
                        'type': 'binary',
                        'datas_fname':filename,
                        'datas': base64.b64encode(file.read()),
                        'document_available': True,
                        'document_type': post.get('doc_type'),
                        'res_id': request.env.user.partner_id.id if request.env.user.partner_id else False,
                        'res_model': 'res.partner',
                        'create_uid': request.env.user.id
                    })
        attach_id._compute_res_name()
        return request.redirect('/my/attachments')
