# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import base64
import json
import pytz

from datetime import datetime
from psycopg2 import IntegrityError

from odoo import http
from odoo.http import request
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.translate import _
from odoo.exceptions import ValidationError
from odoo.addons.base.ir.ir_qweb.fields import nl2br

class WebsiteAttoohForm(http.Controller):
    # Dict of dynamically called filters following type of field to be fault tolerent

    def identity(self, field_label, field_input):
        return field_input

    def integer(self, field_label, field_input):
        return int(field_input)

    def floating(self, field_label, field_input):
        return float(field_input)

    def boolean(self, field_label, field_input):
        return bool(field_input)

    def date(self, field_label, field_input):
        return field_input

    def datetime(self, field_label, field_input):
        lang = request.env['ir.qweb.field'].user_lang()
        strftime_format = (u"%s %s" % (lang.date_format, lang.time_format))
        user_tz = pytz.timezone(request.context.get('tz') or request.env.user.tz or 'UTC')
        dt = user_tz.localize(datetime.strptime(field_input, strftime_format)).astimezone(pytz.utc)
        return dt.strftime(DEFAULT_SERVER_DATETIME_FORMAT)

    def binary(self, field_label, field_input):
        return base64.b64encode(field_input.read())

    def one2many(self, field_label, field_input):
        return [int(i) for i in field_input.split(',')]

    def many2many(self, field_label, field_input, *args):
        return [(args[0] if args else (6, 0)) + (self.one2many(field_label, field_input),)]

    _input_filters = {
        'char': identity,
        'text': identity,
        'html': identity,
        'date': date,
        'datetime': datetime,
        'many2one': integer,
        'one2many': one2many,
        'many2many': many2many,
        'selection': identity,
        'boolean': boolean,
        'integer': integer,
        'float': floating,
        'binary': binary,
    }

    @http.route('/website_form/personal_info', type='http', auth="user", methods=['POST'], website=True)
    def website_personal_info_form(self, *args, **kwargs):
        model_record = request.env.user.partner_id
        try:
            data = self.extract_data(model_record, request.params)
        # If we encounter an issue while extracting data
        except ValidationError as e:
            # I couldn't find a cleaner way to pass data to an exception
            return json.dumps({'error_fields': e.args[0]})
        model_record.write(data['record'])
        
        return json.dumps({'id': model_record.id})

    @http.route('/website_form/personal_detail', type='http', auth="user", methods=['POST'], website=True)
    def website_personal_detail_form(self, *args, **kwargs):
        model_record = request.env.user.partner_id
        try:
            partner = {}
            spouse = {}
            for key, value in request.params.items():
                if key.startswith('spouse_'):
                    k = key.split('spouse_')[1]
                    spouse[k] = value
                else:
                    partner[key] = value
            data = self.extract_data(model_record, partner)
            print ("\n\n\ data-------->",data)
            spouse_data = self.extract_data(model_record, spouse)
        # If we encounter an issue while extracting data
        except ValidationError as e:
            # I couldn't find a cleaner way to pass data to an exception
            return json.dumps({'error_fields': e.args[0]})
        model_record.write(data['record'])
        if model_record.spouse_id:
            model_record.spouse_id.write(spouse_data['record'])
        else:
            spouse_data['record']['name'] = '-'
            spouse_id = model_record.spouse_id.create(spouse_data['record'])
            model_record.spouse_id = spouse_id
        return json.dumps({'id': model_record.id})

    def _validate_o2m_data(self, data, field):
        related_model = request.env['res.partner']._fields[field].comodel_name
        fields = request.env[related_model]._fields
        invalid_fields = []
        for field_name, field_value in data.items():
            try:
                fn_validate = self._input_filters[fields[field_name].type]
                fn_validate(self, field_name, field_value)
            except ValueError:
                invalid_fields.append(field_name)
        return invalid_fields

    @http.route('/website_form/assets', type='http', auth="user", methods=['POST'], website=True)
    def website_asset_form(self, *args, **kwargs):
        model_record = request.env.user.partner_id
        values = request.params
        final_data = []
        res = json.loads(values['force_action'])
        valid = True
        invalid_fields = []
        for data in res['to_update']:
            id = int(data['id'])
            if id and id not in res['to_delete']:
                # invalid_fields = self._validate_o2m_data(data)
                # if (not invalid_fields):
                final_data.append([1, data['id'], data])
                # else:
                #     valid = False
            if not id:
                del data['id']
                final_data.append([0, 0, data])
        for id in res['to_delete']:
            final_data.append([2, id])
        if valid:
            model_record.write({'asset_ids': final_data})
        else:
            return json.dumps({'invalid_fields': invalid_fields})
        return json.dumps({'id': model_record.id})

    @http.route('/website_form/liabilities', type='http', auth="user", methods=['POST'], website=True)
    def website_liability_form(self, *args, **kwargs):
        model_record = request.env.user.partner_id
        values = request.params
        final_data = []
        res = json.loads(values['force_action'])
        for data in res['to_update']:
            id = int(data['id'])
            del data['id']
            if id and id not in res['to_delete']:
                final_data.append([1, id, data])
            if not id:
                final_data.append([0, 0, data])
        for id in res['to_delete']:
            final_data.append([2, id])
        model_record.write({'debt_obligation_ids': final_data})
        return json.dumps({'id': model_record.id})

    @http.route('/website_form/dependent', type='http', auth="user", methods=['POST'], website=True)
    def website_dependent_form(self, *args, **kwargs):
        model_record = request.env.user.partner_id
        values = request.params
        final_data = []
        res = json.loads(values['force_action'])
        for data in res['to_update']:
            id = int(data['id'])
            del data['id']
            if id and id not in res['to_delete']:
                final_data.append([1, id, data])
            if not id:
                final_data.append([0, 0, data])
        for id in res['to_delete']:
            final_data.append([2, id])
        model_record.write({'dependent_ids': final_data})
        return json.dumps({'id': model_record.id})

    @http.route('/website_form/bugdet_income', type='http', auth="user", methods=['POST'], website=True)
    def website_income_form(self, *args, **kwargs):
        model_record = request.env.user.partner_id
        values = request.params
        final_data = []
        res = json.loads(values['force_action'])
        for data in res['to_update']:
            id = int(data['id'])
            del data['id']
            if id and id not in res['to_delete']:
                final_data.append([1, id, data])
            if not id:
                final_data.append([0, 0, data])
        for id in res['to_delete']:
            final_data.append([2, id])
        model_record.write({'income_ids': final_data})
        return json.dumps({'id': model_record.id})

    @http.route('/website_form/bugdet_expense', type='http', auth="user", methods=['POST'], website=True)
    def website_expense_form(self, *args, **kwargs):
        model_record = request.env.user.partner_id
        values = request.params
        final_data = []
        res = json.loads(values['force_action'])
        for data in res['to_update']:
            id = int(data['id'])
            del data['id']
            if id and id not in res['to_delete']:
                final_data.append([1, id, data])
            if not id:
                final_data.append([0, 0, data])
        for id in res['to_delete']:
            final_data.append([2, id])
            
        model_record.write({'expense_ids': final_data})
        return json.dumps({'id': model_record.id})

    # Extract all data sent by the form and sort its on several properties
    def extract_data(self, model, values):

        data = {
            'record': {},        # Values to create record
            'attachments': [],  # Attached files
            'custom': '',        # Custom fields values
        }

        authorized_fields = request.env['ir.model']._get('res.partner')._get_form_writable_fields()
        error_fields = []
        for field_name, field_value in values.items():
            # If the value of the field if a file
            if hasattr(field_value, 'filename'):
                # Undo file upload field name indexing
                field_name = field_name.rsplit('[', 1)[0]

                # If it's an actual binary field, convert the input file
                # If it's not, we'll use attachments instead
                if field_name in authorized_fields and authorized_fields[field_name]['type'] == 'binary':
                    data['record'][field_name] = base64.b64encode(field_value.read())
                else:
                    field_value.field_name = field_name
                    data['attachments'].append(field_value)

            # If it's a known field
            elif field_name in authorized_fields:
                try:
                    input_filter = self._input_filters[authorized_fields[field_name]['type']]
                    data['record'][field_name] = input_filter(self, field_name, field_value)
                except ValueError:
                    error_fields.append(field_name)

            # If it's a custom field
            elif field_name != 'context':
                data['custom'] += u"%s : %s\n" % (field_name, field_value)

        # Add metadata if enabled
        environ = request.httprequest.headers.environ
        if(request.website.website_form_enable_metadata):
            data['meta'] += "%s : %s\n%s : %s\n%s : %s\n%s : %s\n" % (
                "IP"                , environ.get("REMOTE_ADDR"),
                "USER_AGENT"        , environ.get("HTTP_USER_AGENT"),
                "ACCEPT_LANGUAGE"   , environ.get("HTTP_ACCEPT_LANGUAGE"),
                "REFERER"           , environ.get("HTTP_REFERER")
            )
        missing_required_fields = [label for label, field in authorized_fields.items() if field['required'] and not label in data['record']]
        if any(error_fields):
            raise ValidationError(error_fields + missing_required_fields)
        return data
    
    @http.route(['/get_helpdesk_attachment_id'], type='json', auth="public",website=True)
    def get_helpdesk_attachment_id(self, id=0, **kw):
        if id:
            attachment = request.env['ir.attachment'].browse([int(id)])
            value = {}
            if attachment.mimetype in ('image/png', 'application/pdf', 'image/jpeg'):
                if attachment.mimetype == 'application/pdf':
                    value['file_type'] = 'pdf'
                    pdf_src = "/web/static/lib/pdfjs/web/viewer.html?file=/web/content/%s"%(attachment.id)
                    value['src'] = pdf_src
                else:
                    value['file_type'] = 'img'
                    img_src = "/web/image/%s?unique=1"%(attachment.id)
                    value['src'] = img_src
                
            else:
                value['file_type'] = 'other'
                src = "/web/content/%s?download=true"%(attachment.id)
                value['src'] = src      
            return value