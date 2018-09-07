# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import json
import requests
import tempfile
import xmltodict

from odoo import api, models, _
from odoo.exceptions import UserError, ValidationError
from . import etree_parser

def find(key, dictionary=None):
    if dictionary is None:
        dictionary = {}
    for k, v in dictionary.items():
        if k == key:
            yield v
        elif isinstance(v, dict):
            for result in find(key, v):
                yield result
        elif isinstance(v, list):
            for d in v:
                for result in find(key, d):
                    yield result


class CreditReport(models.AbstractModel):
    _name = 'report.crm_credit_report.credit_report'

    @api.model
    def execute(self):
        ICPSudo = self.env['ir.config_parameter'].sudo()
        mode = ICPSudo.get_param('crm_credit_report.mode', default='production')
        test_url = ICPSudo.get_param('crm_credit_report.test_url', default='https://www.uat.xds.co.za/xdsconnect/')
        production_url = ICPSudo.get_param('crm_credit_report.production_url', default='https://www.web.xds.co.za/xdsconnect/')
        username = ICPSudo.get_param('crm_credit_report.username', default='Collect_POC')
        password = ICPSudo.get_param('crm_credit_report.password', default='q7fzhc08')

        xml = """<?xml version="1.0" encoding="utf-8"?><soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"><soap:Body><Login xmlns="http://www.web.xds.co.za/XDSConnectWS"><strUser>%s</strUser><strPwd>%s</strPwd></Login></soap:Body></soap:Envelope>""" % (username, password)
        headers = {'content-type': 'text/xml'}
        url = test_url if mode == 'test' else production_url
        response = requests.post(url=url, data=xml, headers=headers)
        x = xmltodict.parse(response.text)

        try:
            for k,v in x.items():
                login_result = dict(dict(dict(v).get('soap:Body')).get('LoginResponse')).get('LoginResult')
            return login_result
        except:
            raise ValidationError(_('Something went wrong..'))

    @api.model
    def get_xsd_detail(self, partner):

        login_result = self.execute()
        xml = """<?xml version="1.0" encoding="utf-8"?><soap12:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap12="http://www.w3.org/2003/05/soap-envelope"><soap12:Body><ConnectGetCreditReport xmlns="http://www.web.xds.co.za/XDSConnectWS"><ConnectTicket>%s</ConnectTicket><EnquiryReason>Debt Review</EnquiryReason><ProductId>15</ProductId><IdNumber>%s</IdNumber><FirstName>%s</FirstName><Surname>%s</Surname><YourReference>TEST004</YourReference></ConnectGetCreditReport></soap12:Body></soap12:Envelope>"""%(
                 login_result,
                 partner.id_rsa, 
                 partner.first_name,
                 partner.surname)
        headers = {'content-type': 'text/xml'}

        ICPSudo = self.env['ir.config_parameter'].sudo()
        mode = ICPSudo.get_param('crm_credit_report.mode', default='production')
        test_url = ICPSudo.get_param('crm_credit_report.test_url', default='https://www.uat.xds.co.za/xdsconnect/')
        production_url = ICPSudo.get_param('crm_credit_report.production_url', default='https://www.web.xds.co.za/xdsconnect/')
        url = test_url if mode == 'test' else production_url

        response = requests.post(url=url, data=xml, headers=headers)
        response.raise_for_status()
        x = xmltodict.parse(response.text)
        output_dict = json.loads(json.dumps(x))
        output_dict = output_dict['soap:Envelope']['soap:Body']['ConnectGetCreditReportResponse']['ConnectGetCreditReportResult']

        with tempfile.NamedTemporaryFile(mode='w', delete=True) as f:
            f.write(output_dict)
            f.seek(0)
            configdict = etree_parser.ConvertXmlToDict(f.name)
        data = dict(configdict)
        if data.get('NoResult'):
            error = data.get('NoResult').get('Error')
            raise UserError(_(error))
        return data

    @api.model
    def get_report_values(self, docids, data=None):
        Partner = self.env['res.partner']
        DebtObligations = self.env['debt.obligations']
        partner = Partner.browse(docids)
        if len(partner) > 1:
            raise UserError(_("Credit Report is only used for single customer."))
        # TODO: raise warning it's only work for singleton
        data_dict = self.get_xsd_detail(partner)
        ConsumerDetail = list(find('ConsumerDetail', data_dict)) or [[]]
        ConsumerFraudIndicatorsSummary = list(find('ConsumerFraudIndicatorsSummary', data_dict)) or [[]]
        ConsumerCPANLRDebtSummary = list(find('ConsumerCPANLRDebtSummary', data_dict)) or [[]]
        ConsumerPropertyInformationSummary = list(find('ConsumerPropertyInformationSummary', data_dict)) or [[]]
        ConsumerDirectorSummary = list(find('ConsumerDirectorSummary', data_dict)) or [[]]
        ConsumerAccountStatus = list(find('ConsumerAccountStatus', data_dict)) or [[]]
        Consumer24MonthlyPaymentHeader = list(find('Consumer24MonthlyPaymentHeader', data_dict)) or [[]]
        Consumer24MonthlyPayment = list(find('Consumer24MonthlyPaymentHeader', data_dict)) or [[]]
        ConsumerNLRAccountStatus = list(find('ConsumerNLRAccountStatus', data_dict)) or [[]]
        ConsumerNLR24MonthlyPaymentHeader = list(find('ConsumerNLR24MonthlyPaymentHeader', data_dict)) or [[]]
        ConsumerNLR24MonthlyPayment = list(find('ConsumerNLR24MonthlyPayment', data_dict)) or [[]]
        ConsumerNLRDefinition = list(find('ConsumerNLRDefinition', data_dict)) or [[]]
        NLRAccountTypeLegend = list(find('NLRAccountTypeLegend', data_dict)) or [[]]
        AccountTypeLegend = list(find('AccountTypeLegend', data_dict)) or [[]]

        ConsumerEnquiryHistory = list(find('ConsumerEnquiryHistory', data_dict)) or [[]]
        ConsumerAddressHistory = list(find('ConsumerAddressHistory', data_dict)) or [[]]
        ConsumerTelephoneHistory = list(find('ConsumerTelephoneHistory', data_dict)) or [[]]
        ConsumerEmploymentHistory = list(find('ConsumerEmploymentHistory', data_dict)) or [[]]

        ConsumerPropertyInformation = list(find('ConsumerPropertyInformation', data_dict)) or [[]]
        ConsumerDirectorShipLink = list(find('ConsumerDirectorShipLink', data_dict)) or [[]]

        mapping_dict = {}
        for record in AccountTypeLegend[0]:
            record = dict(record)
            mapping_dict[record['AccountTypeCode']] = record['AccountTypeDesc']

        debt_obligations_ids = []
        for record in ConsumerAccountStatus[0]:
            record = dict(record)

            vals = {
                'account_no': record['AccountNo'],
                'creditor_name': record['SubscriberName'],
                'arrears_amount': record['ArrearsAmt'],
                'account_status': record['StatusCodeDesc'],
                'account_date': record['AccountOpenedDate'],
                'pay_date': record['LastPaymentDate'],
                'source': 'Bureau',
                'account_type': record['AccountType'],
                'credit_limit_amt': record['CreditLimitAmt'],
                'outstanding_total': record['CurrentBalanceAmt'],
                'monthly_commitment': record['MonthlyInstalmentAmt'],

            }
            debt_obligations_ids.append(DebtObligations.create(vals).id)
        partner.write({'debt_obligation_ids': [(6, 0, debt_obligations_ids)]})

        return {
            'doc_ids': self.ids,
            'doc_model': 'res.partner',
            'docs': partner,
            'ConsumerDetail': ConsumerDetail,
            'ConsumerFraudIndicatorsSummary': ConsumerFraudIndicatorsSummary,
            'ConsumerCPANLRDebtSummary': ConsumerCPANLRDebtSummary,
            'ConsumerPropertyInformationSummary': ConsumerPropertyInformationSummary,
            'ConsumerDirectorSummary': ConsumerDirectorSummary,
            'ConsumerAccountStatus': ConsumerAccountStatus,
            'Consumer24MonthlyPaymentHeader': Consumer24MonthlyPaymentHeader,
            'Consumer24MonthlyPayment': Consumer24MonthlyPayment,
            'ConsumerNLRAccountStatus': ConsumerNLRAccountStatus,
            'ConsumerNLR24MonthlyPaymentHeader': ConsumerNLR24MonthlyPaymentHeader,
            'ConsumerNLR24MonthlyPayment': ConsumerNLR24MonthlyPayment,
            'ConsumerNLRDefinition': ConsumerNLRDefinition,
            'NLRAccountTypeLegend': NLRAccountTypeLegend,
            'ConsumerEnquiryHistory': ConsumerEnquiryHistory,
            'ConsumerAddressHistory': ConsumerAddressHistory,
            'ConsumerTelephoneHistory': ConsumerTelephoneHistory,
            'ConsumerEmploymentHistory': ConsumerEmploymentHistory,

            'ConsumerDirectorShipLink': ConsumerDirectorShipLink,
            'ConsumerPropertyInformation': ConsumerPropertyInformation,
        }
