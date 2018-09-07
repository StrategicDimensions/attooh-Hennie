# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from werkzeug import urls
import time


from odoo import api, fields, models, _
from odoo.addons.payment.models.payment_acquirer import ValidationError
from odoo.tools.float_utils import float_compare

import logging

_logger = logging.getLogger(__name__)


class PaymentAcquirerMygate(models.Model):
    _inherit = 'payment.acquirer'

    provider = fields.Selection(selection_add=[('mygate', 'mygate')])
    mygate_merchant_id = fields.Char(string='Merchant Key', required_if_provider='mygate', groups='base.group_user')
    mygate_application_id = fields.Char(string='Merchant Application', required_if_provider='mygate', groups='base.group_user')

    def _get_mygate_urls(self, environment):
        """ mygate URLs"""
        if environment == 'prod':
            return {'mygate_form_url': 'https://virtual.mygateglobal.com/PaymentPage.cfm'}
        else:
            return {'mygate_form_url': 'https://virtual.mygateglobal.com/PaymentPage.cfm'}

    @api.multi
    def mygate_form_generate_values(self, values):
        self.ensure_one()
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        mygate_values = dict(values,
                            mode=0 if self.environment == 'test' else 1,
                            merchantID=self.mygate_merchant_id,
                            applicationID=self.mygate_application_id,
                            merchantReference=values['reference'],
                            amount=values['amount'],
                            txtCurrencyCode=values['currency'] and values['currency'].name or '',
                            redirectSuccessfulURL=urls.url_join(base_url, '/payment/mygate/return'),
                            redirectFailedURL=urls.url_join(base_url, '/payment/mygate/error'),
                            return_url= values.get('return_url'),
                            recipient=values.get('partner_name'),
                            shippingAddress1=values.get('partner_address'),
                            shippingAddress2=values.get('partner_zip'),
                            shippingAddress3=values.get('partner_city'),
                            shippingAddress4=values.get('partner_state').name,
                            shippingAddress5=values.get('partner_country').name,
                            email=values.get('partner_email'),
                            phone=values.get('partner_phone'))
        return mygate_values

    @api.multi
    def mygate_get_form_action_url(self):
        self.ensure_one()
        return self._get_mygate_urls(self.environment)['mygate_form_url']


class PaymentTransactionmygate(models.Model):
    _inherit = 'payment.transaction'

    def _confirm_so(self):
        """ Check tx state, confirm the potential SO """
        self.ensure_one()
        if self.sale_order_id.state not in ['draft', 'sent', 'sale']:
            _logger.warning('<%s> transaction STATE INCORRECT for order %s (ID %s, state %s)', self.acquirer_id.provider, self.sale_order_id.name, self.sale_order_id.id, self.sale_order_id.state)
            return 'pay_sale_invalid_doc_state'
        if not float_compare(self.amount, self.sale_order_id.amount_total, 2) == 0:
            _logger.warning(
                '<%s> transaction AMOUNT MISMATCH for order %s (ID %s): expected %r, got %r',
                self.acquirer_id.provider, self.sale_order_id.name, self.sale_order_id.id,
                self.sale_order_id.amount_total, self.amount,
            )
            self.sale_order_id.message_post(
                subject=_("Amount Mismatch (%s)") % self.acquirer_id.provider,
                body=_("The sale order was not confirmed despite response from the acquirer (%s): SO amount is %r but acquirer replied with %r.") % (
                    self.acquirer_id.provider,
                    self.sale_order_id.amount_total,
                    self.amount,
                )
            )
            return 'pay_sale_tx_amount'

        if self.state == 'authorized' and self.acquirer_id.capture_manually:
            _logger.info('<%s> transaction authorized, auto-confirming order %s (ID %s)', self.acquirer_id.provider, self.sale_order_id.name, self.sale_order_id.id)
            if self.sale_order_id.state in ('draft', 'sent'):
                self.sale_order_id.with_context(send_email=True).action_confirm()
        elif self.state == 'done':
            _logger.info('<%s> transaction completed, auto-confirming order %s (ID %s)', self.acquirer_id.provider, self.sale_order_id.name, self.sale_order_id.id)
            if self.sale_order_id.state in ('draft', 'sent'):
                adv_wiz = self.env['sale.advance.payment.inv'].with_context(active_ids=[self.sale_order_id.id]).create({
                    'advance_payment_method': 'fixed',
                    'amount': self.amount,
                })
                adv_wiz.create_invoices()
        elif self.state not in ['cancel', 'error'] and self.sale_order_id.state == 'draft':
            _logger.info('<%s> transaction pending/to confirm manually, sending quote email for order %s (ID %s)', self.acquirer_id.provider, self.sale_order_id.name, self.sale_order_id.id)
            self.sale_order_id.force_quotation_send()
        else:
            _logger.warning('<%s> transaction MISMATCH for order %s (ID %s)', self.acquirer_id.provider, self.sale_order_id.name, self.sale_order_id.id)
            return 'pay_sale_tx_state'
        return True

    @api.model
    def _mygate_form_get_tx_from_data(self, data):
        """ Given a data dict coming from mygate, verify it and find the related
        transaction record. """
        reference = data.get('_MERCHANTREFERENCE')
        pay_id = data.get('_TRANSACTIONINDEX')
        shasign = data.get('_PANHASHED')
        if not reference or not pay_id or not shasign:
            _logger.warning(_('mygate: received data with missing reference (%s) or pay_id (%s) or shashign (%s)') % (reference, pay_id, shasign))

        transaction = self.search([('reference', '=', reference)])

        if not transaction:
            _logger.warning(_('mygate: received data for reference %s; no order found') % (reference))
        elif len(transaction) > 1:
            _logger.warning(_('mygate: received data for reference %s; multiple orders found') % (reference))
        return transaction

    @api.multi
    def _mygate_form_get_invalid_parameters(self, data):
        invalid_parameters = []

        if self.acquirer_reference and data.get('_TRANSACTIONINDEX') != self.acquirer_reference:
            invalid_parameters.append(
                ('Transaction Id', data.get('_TRANSACTIONINDEX'), self.acquirer_reference))
        #check what is buyed
        if float_compare(float(data.get('_AMOUNT', '0.0')), self.amount, 2) != 0:
            invalid_parameters.append(
                ('Amount', data.get('_AMOUNT'), '%.2f' % self.amount))

        return invalid_parameters

    @api.multi
    def _mygate_form_validate(self, data):
        status = data.get('_RESULT')
        transaction_status = {
            '0': {
                'state': 'done',
                'acquirer_reference': data.get('_TRANSACTIONINDEX'),
                'date_validate': fields.Datetime.now(),
            },
            '-1': {
                'state': 'error',
                'state_message': data.get('_ERROR_MESSAGE') or _('mygate: feedback error'),
                'acquirer_reference': data.get('_TRANSACTIONINDEX'),
                'date_validate': fields.Datetime.now(),
            }
        }
        vals = transaction_status.get(status, False)
        if not vals:
            vals = transaction_status['error']
            _logger.info(vals['state_message'])
        return self.write(vals)

    def _check_or_create_sale_tx(self, order, acquirer, payment_token=None, tx_type='form', add_tx_values=None, reset_draft=True):
        tx = super(PaymentTransactionmygate, self)._check_or_create_sale_tx(order, acquirer, payment_token=None, tx_type='form', add_tx_values=None, reset_draft=True)
        # change full amount to payment on Acceptance(50%) amount
        tx.amount = order.amount_total
        return tx

    def render_sale_button(self, order, return_url, submit_txt=None, render_values=None):
        values = {
            'return_url': return_url,
            'partner_id': order.partner_shipping_id.id or order.partner_invoice_id.id,
            'billing_partner_id': order.partner_invoice_id.id,
        }
        if render_values:
            values.update(render_values)
        return self.acquirer_id.with_context(submit_class='btn btn-primary', submit_txt=submit_txt or _('Pay Now')).sudo().render(
            self.reference,
            order.amount_total,
            order.pricelist_id.currency_id.id,
            values=values,
        )
