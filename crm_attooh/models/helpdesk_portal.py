from odoo import http
from odoo.http import request
import base64
from odoo.addons.portal.controllers.portal import get_records_pager, pager as portal_pager, CustomerPortal

class CustomerPortal(CustomerPortal):
    
    @http.route('/upload_document_helpdesk', type='http', auth="user", website=True)
    def upload_document_helpdesk(self, ticket_id, doc_type, doc_attachment, **post):
        user = request.env.user
        domain = ['|', ('user_id', '=', user.id), ('partner_id', 'child_of', user.partner_id.commercial_partner_id.id), ('id', '=', int(ticket_id))]
        ticket = request.env['helpdesk.ticket'].sudo().search(domain, limit=1)
        if ticket:
            filename = doc_attachment.filename
            attach = request.env['ir.attachment'].sudo().create({
                            'name': filename,
                            'type': 'binary',
                            'datas_fname': filename,
                            'datas': base64.b64encode(doc_attachment.read()),
                            'document_available': True,
                            'document_type': doc_type,
                            'res_id': int(ticket_id) or False,
                            'res_model': 'helpdesk.ticket',
                        })
            attach._compute_res_name()
            request.env['mail.message'].sudo().create({
                'attachment_ids': [(4, attach.id)],
                'author_id': request.env.user.partner_id.id,
                'model': 'helpdesk.ticket',
                'res_id': int(ticket_id) or False,
                'message_type': 'comment',
                'website_published': True,
                'create_uid': request.env.user.id,
            })
            return request.redirect('/helpdesk/ticket/%s' % ticket_id)