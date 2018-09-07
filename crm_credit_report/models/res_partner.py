# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import base64
import time

from odoo import api, models, _
from odoo.exceptions import UserError
from odoo.tools.safe_eval import safe_eval


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.multi
    def get_credit_report(self):
        if len(self) > 1:
            raise UserError(_("Please select only one record to get a credit report."))
        record = self

        report_template = self.env.ref('crm_credit_report.action_credit_report')
        report = report_template
        result, format = report.render_qweb_pdf(record.ids)
        pdf = base64.b64encode(result)
        report_name = safe_eval(report_template.print_report_name, {'object': record, 'time': time})

        attachment = self.env['ir.attachment'].create({
            'name': report_name,
            'datas': pdf,
            'datas_fname': report_name,
            'mimetype': 'application/pdf',
            'res_model': 'res.partner',
            'res_id': record.id,
        })
        record.message_post(body="Credit Report", attachment_ids=attachment.ids)
        return True
