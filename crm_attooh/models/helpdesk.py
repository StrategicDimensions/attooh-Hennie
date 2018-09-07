# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError


class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'

    activites_created = fields.Boolean(string="Activites Created")

    @api.multi
    def write(self, val):
        if self.stage_id and self.stage_id.name in ('New'):
            if val.get('stage_id') and self.env['helpdesk.stage'].browse(val.get('stage_id')).name in ('In Progress'):
                if not self.user_id:
                    raise ValidationError(_("Please assign the ticket to proceed"))
                return super(HelpdeskTicket, self.with_context(custom_context=True)).write(val)
        return super(HelpdeskTicket, self).write(val)

    @api.onchange('stage_id')
    def onchanhge_stage_id(self):
        user_id = False
        if self.stage_id.name == 'In Progress':
            for activity in self.ticket_type_id.ticket_type_activity_ids:
                date_deadline = datetime.today() + timedelta(days=activity.activity_date)
                if activity.assign_to_owner:
                    user_id = self.user_id and self.user_id.id or False
                else:
                    user_id = activity.employee_role_id.employee_id and activity.employee_role_id.employee_id.id or False
                activities = self.env['mail.activity'].search(
                    [('res_id', '=', self._origin.id), ('stage_activity_id', '=', activity.id)])
                if not activities:
                    self.env['mail.activity'].sudo().create({
                        'activity_type_id': activity.activity_type_id and activity.activity_type_id.id or False,
                        'res_id': self._origin.id,
                        'res_model_id': self.env.ref('helpdesk.model_helpdesk_ticket').id,
                        'date_deadline': date_deadline,
                        'summary': activity.name,
                        'user_id': user_id,
                        'res_model': 'helpdesk.ticket',
#                         'stage_activity_id': activity.id, #Edited by Dhruvil
                        #It's not correct, here someone tries to put value of ticket.type.activity object in stage.activity
                        #both objects are different 

                    })

    @api.multi
    def create_activity_from_ticket(self):
        summary_list = \
                ['Request Client Instruction. Request copy of New Utility Bill (not older than 3 months)',
                'Record Keeping: Update details on system and copy/scan /File of written instruction and new utility bill (FAIS)',
                'Forward to Product Supplier: Client Instruction and a copy of Utility Bill',
                'Follow up with Product Supplier that the relevant changes have been made',
                'Notify Client of change of address']
        cancellation_of_policy_list = \
                ['Get a Cancellation Letter from the client',
               'Forward the Letter to the Product Supplier & Follow up',
               'Send confirmation of cancellation to the client',
               'Notify the Broker of the cancellation',
               'Scan/Copy the information on system',
               'File Activity']
        beneficiary_list = \
                [['Get instruction from client & capture and link asset on system', 0],
                ['Fill in request on relevant document and send to client to sign', 3],
                ['If not received from client; follow up', 4],
                ['Receive signed docs, file on system and send to Insurer service department', 5],
                ['Confirm request has been processed and inform client via email/SMS', 5],
                ['Change beneficiary on relevant asset on system', 5],
                ['File activity', 5]]
        counter_offer_letter_list = \
                ['Receive Counter Offer Letter from Product Supplier with amended terms (loadings, exclusions etc)',
                'Notify the Advisor of the terms of the Letter',
                'Contact Client and book the appointment for the Advisor to discuss the terms and conditions of Counter Offer',
                'Appointment. Advisor to discuss with the client accept and sign',
                'Record Keeping. Copy/Scan/File of all documents pertaining to this transaction',
                'Record Keeping. Update Policy Schedule on system',
                'Forward to Product Supplier: all documentaion, signed Counter Offer Letter',
                'Follow p with the Product Supplier if the case is accepted']
        claims_list = \
                ['Receive a call about the claim',
                'Capture on system as activity, link assets',
                'Notify the Broker that the claim has been received',
                'Forward Forms to the Client / Spouse',
                'All forms and policy document collected',
                'Forms checked by Administrator / Service Clerk',
                'Submit all forms and documents to Product Providers',
                'Follow up with Product Provider ',
                'Notify the client that the deposit has taken place',
                'Print Letter of Confirmation and forward to client',
                'File Activity. Copy/Scan all documents on system']
        cession_colateral_list = \
                [['Follow up with the Product Supplier for values and forms', 7],
                ['Contact the client to sign cession form , original policy contract, revenue stamp and other specific documents required by Product', 10],
                ['Appointment Collect original policy document form from client, client complete and sign cession', 11],
                ['Check the Documentation correctly completed', 12],
                ['Record Keeping: Scan of all relevant documents and file', 12],
                ['Forward to Product Supplier: All Cession Documents', 12],
                ['Follow up with Product Supplier', 12],
                ['Cession Disclosure: Cession has been recorded: name of the cession: name of the cessionary', 13],
                ['Notify Client : Fax/email/psot letter to the client confirming the cession has been recorded: attach copy of documents and cession disclosure', 14],
                ['Notify Advisor of registration of cession Record Keeping: Update Policy Schedule and Planning projections, in system', 15],
                ['Record Keeping: Update Policy Schedule and Planning projections, in system', 16]]
        cession_outright_list = \
                [['Follow up with Product Supplier for values and forms', 5],
                ['Contact to sign Cession form, original policy contract, revenue stamp and any other required documentation', 8],
                ['Appointment. Collect the original policy document from client. Client must complete and sign Cession Forms', 9],
                ['Check Documentation: correctly completed ', 10],
                ['Record Keeping: Copy, Scan all relevant documents and file (FAIS) ', 10],
                ['Forward to Product Supplier: All cession documentation ', 10],
                ['Follow up with Product Supplier ', 10],
                ['Cession Disclosure: On receipt of confirmation check Product Supplier has disclosed', 11],
                ['Notify Client: Fax/Email/post letter to client confirming that the Cession has been registered', 12],
                ['Notify Advisor: of registration of Cession. Client portfolio has changed ', 13],
                ['Record Keeping: Copy, Scan all relevant documents and file (FAIS) and System', 14],
                ['Record Keeping: Update policy schedule, System', 15]]
        debit_order_list = \
                ['Request written instruction/debit order form : from client with proof of bank as required by Product Supplier',
                'Follow up with client to return the signed instruction/debit order form ',
                'Forward to Product Supplier all documents ',
                'Follow up with Product Supplier in terms of serice level agreement ',
                'Forward to Client confirmation received from Product Supplier ',
                'Record Keeping. Update the client information on system',
                'File Actvity: Scan/Copy of all records pertaining this transaction ']
        early_retirement_list = \
                ['Request the forms, values or quote from the Product Supplier ',
                'Forward the forms to the client for completion ',
                'Appointment Collect original policy document form from client',
                'Check the Documentation correctly completed ',
                'Submit all forms and documents to Product Supplier',
                'Follow up with Product Supplier ',
                'Notify Client: Fax/Email/post letter to client confirming that the deposit has been done ',
                'Notify the Advisor of the completion of the request',
                'Record Keeping: Copy, Scan all relevant documents on system',
                'File Activity ']
        maturity_list = \
                ['Check Documentation Completed correctly and signed by client ',
                'Forward to Product Supplier: all maturity documentation and new investment options',
                'Follow up with Product Supplier ',
                'Notify client that the deposit has taken place will be forwarded for onward transmission ',
                'Notify advisor that the deposit has taken place',
                'Record Keeping, copy/scan/file maturity documentation ',
                'Record Keeping, capture details on system',
                'Forward confirmation to Client: Confirmation of maturity letter and documentation ',
                'Review Maturity Documents from Product Supplier. Draw new file',
                'Notify Advisor. Give File to Advisor with maturity documentation ',
                'Advisor to prepare options, reviews, client positions on system and prepare relevant options',
                'Request Quotations.Call Prodcuct Supplier for quotes',
                'Follow up with Product Suppliers for quotes and product details ',
                'Contact Client: Book appointment for advisor to see client 3 months Maturity due date of policy ',
                'Appointment: Advisor sees client. Dicloses all options, tax considerations, re-investment ']
        surrender_list = \
                [['Contact the Product Supplier to get current Surrender values and forms Check with Product Supplier for their particular procedures ', 0],
                ['Notify Advisor of Potential Surrender of Policy/Investments ', 1],
                ['Contact the Client to discuss, sign, original contract and other specific documentation required by the Product Supplier ', 2],
                ['Check the Documentation of correctly completed', 3],
                ['Forward to Product Supplier : all documents ', 3],
                ['Notify the client as soon as the deposit has taken place: Scan, Copy, File any confirmation received from the Product Supplier ', 3],
                ['Notify the Advisor of the completion of surrender ', 4],
                ['Record Keeping: Update Policy Schedule, Production Book and system', 4]]
        loans_list = \
                [['Request information on the relevant loan information/quotation from the Product Supplier. Ensure that the required dsiclosures are included', 0],
                ['Notify Advisor. Prepare client file with relevant loan quotation and documents and give to advisor to review for suitability and relevant loan history ', 2],
                ['Appointment: Contact/Call client and discuss implications and alternatives', 3],
                ['Check Documentation correctly completed ', 4],
                ['Forward to Product Supplier all loan documentation ', 5],
                ['Follow up with Product Supplier ', 6],
                ['Record Keeping: Copy/File/Scan copies of all records pertaining to this transaction ', 6],
                ['Notify Client: Fax/Email/Post Letter to client confirming this transaction ', 7],
                ['Notify Advisor that the loan has been taken place. ', 8],
                ['Record Keeping. Copy/ File/ Scan all copies all records pertaining this transaction ', 9]]
        tax_certificates_list = \
                [['Request signed LOA from client', 0],
                ['Request information of the relevant client from the Product Supplier ', 1],
                ['Follow up with the Product Supplier if information is not received ', 3],
                ['Forward the information to the client ', 4],
                ['File Activity: Scan/Copy information on system', 5]]
        fund_changes_list = \
                ['Notify the Advisor of the potential changes and give the advisor the file ',
                'Contact the Client - discuss the request for switch, check mandate, client to sign if neccessry ',
                'Forward to Client all the relevant forms for client signatures if necessary',
                'Check Documentation: correctly completed ',
                'Forward to Product Supplier: all documenation ',
                'Notify Client. Fax/ Email / post letter to client confirming the switch',
                'Recording Keeping. Update policy schedule on system',
                'Recording Keeping. Copy/File/Scan of copies of all records pertaining this transactions ']
        repurchase_list = \
                ['Contact the Prooduct Supllier and get the relevant repurchase forms ',
                'Notify Advisor regarding the repurchase request ',
                'Contact the Client to discuss, sign, original contract and other specific documentation required by the Product Supplier ',
                'Check the Documentation of correctly completed',
                'Forward to Product Supplier : all documents ',
                'Notify the client as soon as the deposit has taken place: Scan, Copy, File any confrimation received from the Product Supplier ',
                'Notify the Advisor of the completion of the repurchase ',
                'Record Keeping: File Activity ']
        activity_type_id = self.env['mail.activity.type'].search([('name', '=', 'Todo')], order="id desc", limit=1)
        list_acticity = []
        list_acticity = summary_list if self.env.context.get('from_update')\
                   else cancellation_of_policy_list if self.env.context.get('from_update_cancel_policy')\
                   else beneficiary_list if self.env.context.get('from_update_beneficiary')\
                   else counter_offer_letter_list if self.env.context.get('from_update_counter_offer')\
                   else claims_list if self.env.context.get('from_update_claims')\
                   else cession_colateral_list if self.env.context.get('from_update_cession_colateral')\
                   else cession_outright_list if self.env.context.get('from_update_cession_outright')\
                   else debit_order_list if self.env.context.get('from_update_debit_order')\
                   else early_retirement_list if self.env.context('from_update_early_retirement')\
                   else maturity_list if self.env.context('from_update_maturity')\
                   else surrender_list if self.env.context('from_update_surrender')\
                   else loans_list if self.env.context('from_update_loans')\
                   else tax_certificates_list if self.env.context('from_update_tax_certificates')\
                   else fund_changes_list if self.env.context('from_update_fund_changes')\
                   else repurchase_list if self.env.context('from_update_repurchase')\
                   else []
        if list_acticity:
            day_count = 0
            self.activites_created = True
            for each in list_acticity:
                self.env['mail.activity'].create({'summary': each[0] if type(each) is list else each,
                                              'user_id': self.user_id.id,
                                              'date_deadline': datetime.now().date() + timedelta(days= each[1] if type(each) is list else day_count),
                                              'activity_type_id': activity_type_id.id if activity_type_id else False,
                                              'res_id': self.id,
                                              'res_model': 'helpdesk.ticket',
                                              'res_model_id': self.env['ir.model'].search([('model', '=', 'helpdesk.ticket')], order="id desc", limit=1).id
                                              })
                if isinstance(each, str):
                    day_count += 1

class HelpdeskTicketType(models.Model):
    _inherit = 'helpdesk.ticket.type'

    ticket_type_activity_ids = fields.One2many('ticket.type.activity', 'ticket_type_id',
                                               string="Ticket Type Activities")
