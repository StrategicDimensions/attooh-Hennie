# -*- coding: utf-8 -*-

from odoo import fields, models


class DocumentType(models.Model):
    _name = "document.type"
    _description = "Document Type"

    name = fields.Char('Document Name', required=True)
    available = fields.Boolean('Available on Portal')


class IrAttachment(models.Model):
    _inherit = "ir.attachment"

    document_type = fields.Many2one('document.type', string='Document Type')
    document_available = fields.Boolean(related="document_type.available", store=True)
