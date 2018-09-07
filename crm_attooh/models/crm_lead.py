# -*- coding: utf-8 -*-
import base64
import io
from PyPDF2 import PdfFileReader, PdfFileWriter
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from odoo.modules.module import get_module_resource

from odoo import models, fields, api, _
from datetime import datetime, timedelta
from odoo.exceptions import UserError


class CrmAttooh(models.Model):
    _name = 'crm_attooh.service'

    name = fields.Char()

class SignatureRequest(models.Model):
    _inherit = 'signature.request'

    lead_id = fields.Many2one('crm.lead')

    @api.model
    def initialize_sign_new(self, id, signers, followers, lead_id, reference, subject, message, record=False, send=True):
        signature_request = self.create(
            {'template_id': id, 'reference': reference, 'lead_id': lead_id, 'follower_ids': [(6, 0, followers)],
             'favorited_ids': [(4, self.env.user.id)]})
        signature_request.set_signers(signers)
        if send:
            signature_request.action_sent(subject, message)
            signature_request._message_post(_('Waiting for signatures.'), type='comment', subtype='mt_comment')
        if record:
            body = _('%s has been sent to %s') % (subject, record.partner_id.name)
            record.message_post(body, message_type='comment')
        return {
            'id': signature_request.id,
            'token': signature_request.access_token,
            'sign_token': signature_request.request_item_ids.filtered(
                lambda r: r.partner_id == self.env.user.partner_id).access_token,
        }

    @api.one
    def generate_completed_document(self):
        if len(self.template_id.signature_item_ids) <= 0:
            self.completed_document = self.template_id.attachment_id.datas
            return

        old_pdf = PdfFileReader(io.BytesIO(base64.b64decode(self.template_id.attachment_id.datas)), overwriteWarnings=False)
        font = "Helvetica"
        normalFontSize = 0.015

        packet = io.BytesIO()
        can = canvas.Canvas(packet)
        itemsByPage = self.template_id.signature_item_ids.getByPage()
        SignatureItemValue = self.env['signature.item.value']
        for p in range(0, old_pdf.getNumPages()):
            page = old_pdf.getPage(p)
            width = float(page.mediaBox.getUpperRight_x())
            height = float(page.mediaBox.getUpperRight_y())

            # Set page orientation (either 0, 90, 180 or 270)
            rotation = page.get('/Rotate')
            if rotation:
                can.rotate(rotation)
                # Translate system so that elements are placed correctly
                # despite of the orientation
                if rotation == 90:
                    width, height = height, width
                    can.translate(0, -height)
                elif rotation == 180:
                    can.translate(-width, -height)
                elif rotation == 270:
                    width, height = height, width
                    can.translate(-width, 0)

            items = itemsByPage[p + 1] if p + 1 in itemsByPage else []
            for item in items:
                value = SignatureItemValue.search([('signature_item_id', '=', item.id), ('signature_request_id', '=', self.id)], limit=1)
                if not value or not value.value:
                    continue

                value = value.value

                if item.type_id.type == "text":
                    can.setFont(font, height * item.height * 0.8)
                    can.drawString(width * item.posX, height * (1 - item.posY - item.height * 0.9), value)

                elif item.type_id.type == "textarea":
                    can.setFont(font, height * normalFontSize * 0.8)
                    lines = value.split('\n')
                    y = (1 - item.posY)
                    for line in lines:
                        y -= normalFontSize * 0.9
                        can.drawString(width * item.posX, height * y, line)
                        y -= normalFontSize * 0.1

                elif item.type_id.type == "signature" or item.type_id.type == "initial":
                    img = base64.b64decode(value[value.find(',') + 1:])
                    can.drawImage(ImageReader(io.BytesIO(img)), width * item.posX, height * (1 - item.posY - item.height), width * item.width, height * item.height, 'auto', True)

                elif item.type_id.type == "checkbox":
                    symboia_font_family = get_module_resource('crm_attooh', 'fonts', 'Symbola_hint.ttf')
                    symbola_font = TTFont('Symbola', symboia_font_family)
                    pdfmetrics.registerFont(symbola_font)
                    styles = getSampleStyleSheet()
                    styles["Title"].fontName = 'Symbola'
                    can.setFont('Symbola', height * item.height * 0.5)
                    if value == "True":
                        can.drawString(width * item.posX, height * (1 - item.posY - item.height * 0.9), '\u2611')
                    else:
                        can.drawString(width * item.posX, height * (1 - item.posY - item.height * 0.9), '\u2610')
            can.showPage()
        can.save()

        item_pdf = PdfFileReader(packet, overwriteWarnings=False)
        new_pdf = PdfFileWriter()

        for p in range(0, old_pdf.getNumPages()):
            page = old_pdf.getPage(p)
            page.mergePage(item_pdf.getPage(p))
            new_pdf.addPage(page)

        output = io.BytesIO()
        new_pdf.write(output)
        self.completed_document = base64.b64encode(output.getvalue())
        output.close()

class SignatureItemTypeAttooh(models.Model):
    _inherit = "signature.item.type"

    type = fields.Selection(selection_add=[('checkbox', 'Checkbox')])


class CRM(models.Model):
    _inherit = 'crm.lead'

    service_ids = fields.Many2many('crm_attooh.service', 'crm_lead_service_rel', 'lead_id', 'service_id',
                                   string='Services')
    signature_requests_count = fields.Integer("# Signature Requests", compute='_compute_signature_requests')
    signature_ids = fields.One2many('signature.request', 'lead_id')
#     product_area = fields.Selection([
#         ('financial_planning', 'Financial Planning'),
#         ('short_term', 'Short Term'),
#         ('health', 'Health'),
#         ('investments', 'Investments'),
#         ('risk', 'Risk')
#         ], default="financial_planning", string="Product Area")
    product_area_id = fields.Many2one('product.area', string="Product Area")
    referred = fields.Many2one('res.partner', 'Referred By')

    submission_data = fields.Date('Submission Date')
    product_provider_id = fields.Many2one('res.partner', string='Product Provider', domain="[('supplier', '=', True)]")
    product_id = fields.Many2one('product.template', 'Product')
    premium = fields.Float('Premium')
    commission_year_1 = fields.Float('1st year Commission')
    commission_year_2 = fields.Float('2nd year Commission')
    monthly_commission = fields.Float(' Monthly Ongoing Commission')
    date_of_issue = fields.Date('Date of Issue')
    vitality = fields.Boolean('Vitality')
    doc = fields.Date('DOC')
    complience_mail = fields.Date('Compliance Mail')
    fica = fields.Boolean('FICA')
    issued_commission_year_1 = fields.Float('Issued 1st year Commission')
    issued_commission_year_2 = fields.Float('Issued 2nd year Commission')
    issued_monthly_commission = fields.Float('Issued Monthly Ongoing Commission')
    contract_policy_number = fields.Char('Contract/Policy Number')
    book_notes = fields.Text('Production Book Notes')
    currency_id = fields.Many2one('res.currency', string='Currency', default=lambda self: self.env.user.company_id.currency_id.id)

    # string changes on existing fields
    phone = fields.Char('Work Phone')
    # team_id = fields.Many2one(string='Sales to New Business')

    @api.multi
    def get_user_id(self, activity):
        user_id = False
        user_id = activity.employee_role_id.employee_id and activity.employee_role_id.employee_id.id or False
        return user_id

    @api.onchange('stage_id')
    def onchanhge_stage_id(self):
        user_id = False
        for activity in self.stage_id.stage_activity_ids:
            if self._origin.team_id and activity.team_ids and self._origin.team_id.id in activity.team_ids.ids:
                date_deadline = datetime.today() + timedelta(days=activity.activity_date)
                if activity.assign_to_owner:
                    user_id = self.user_id and self.user_id.id or False
                else:
                    if self.user_id.is_financial_advisor:
                        role_ids = self.user_id.user_employee_roles_ids
                        if not role_ids:
                            user_id = self.get_user_id(activity)
                        else:
                            emp_role_id = role_ids.filtered(lambda l: l.employee_role_id.id == activity.employee_role_id.id)
                            if emp_role_id:
                                user_id = emp_role_id.employee_id.id
                            else:
                                user_id = self.get_user_id(activity)
                    else:
                        user_id = self.get_user_id(activity)
                activities = self.env['mail.activity'].search(
                    [('res_id', '=', self._origin.id), ('stage_activity_id', '=', activity.id)])
                if not activities:
                    self.env['mail.activity'].sudo().create({
                        'activity_type_id': activity.activity_type_id and activity.activity_type_id.id or False,
                        'res_id': self._origin.id,
                        'res_model_id': self.env.ref('crm.model_crm_lead').id,
                        'date_deadline': date_deadline,
                        'summary': activity.name,
                        'user_id': user_id,
                        'stage_activity_id': activity.id,
                        })

    @api.multi
    def write(self, vals):
        res = super(CRM, self).write(vals)
        if vals.get('stage_id'):
            for record in self:
                if not record.partner_id:
                    raise UserError(_('Please select customer on opportunity'))
                automate_emails = self.stage_id.stage_automated_email_ids.filtered(lambda r: r.user_id == self.user_id)
                for email in automate_emails:
                    record.message_post_with_template(email.email_template_id.id)
                signature_requests = self.stage_id.stage_signature_request_ids.filtered(lambda r: r.user_id == self.user_id)
                for request in signature_requests:
                    template = request.signature_request_template_id
                    signers = [{
                        'partner_id': record.partner_id.id,
                        'role': 1
                    }]
                    message = _('Signature Request for %s ') % record.stage_id.name
                    subject = _('Signature Request - %s') % template.attachment_id.name
                    Request = self.env['signature.request']
                    Request.initialize_sign_new(template.id, signers, [], record.id,
                        template.attachment_id.name, subject, message, record, True)
                if self.stage_id.has_portal_access:
                    PortalWiard = self.env['portal.wizard']
                    portal = PortalWiard.create({
                        'user_ids': [(0, 0, {
                            'partner_id': record.partner_id.id,
                            'email': record.partner_id.email,
                            'in_portal': True,
                            'user_id': self.env.user.id
                        })]
                    })
                    portal.action_apply()
                    body = _('Portal invitation has been send to %s') % record.partner_id.name
                    self.message_post(body, message_type='comment')
        return res

    @api.multi
    @api.onchange('product_area_id')
    def onchanhge_product_area(self):
        if self.product_area_id.id == self.env.ref('crm_attooh.product_short_term').id:
            self.team_id = self.env.ref('crm_attooh.crm_team_attooh_1')
        elif self.product_area_id.id == self.env.ref('crm_attooh.product_area_health').id:
            self.team_id = self.env.ref('crm_attooh.crm_team_attooh_2')
        elif self.product_area_id.id == self.env.ref('crm_attooh.product_area_investments').id:
            self.team_id = self.env.ref('crm_attooh.crm_team_attooh_3')
        elif self.product_area_id.id == self.env.ref('crm_attooh.product_area_risk').id:
            self.team_id = self.env.ref('crm_attooh.crm_team_attooh_4')
        else:
            self.team_id = self.env.ref('crm_attooh.crm_team_attooh_5')

    @api.multi
    def _compute_signature_requests(self):
        self.ensure_one()
        self.signature_requests_count = len(self.signature_ids)

    @api.multi
    def open_lead_signature(self):
        self.ensure_one()
        action = self.env['ir.actions.act_window'].for_xml_id('website_sign', 'signature_request_action')
        action['domain'] = [('id', 'in', self.signature_ids.ids)]
        return action

class CrmTeamAttooh(models.Model):
    _inherit = "crm.team"

    @api.model
    @api.returns('self', lambda value: value.id if value else False)
    def _get_default_team_id(self, user_id=None):
        return self.env.ref('crm_attooh.crm_team_attooh_5')


class ProductArea(models.Model):
    _name = 'product.area'

    name = fields.Char(string="Product Area")
