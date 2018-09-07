# -*- coding: utf-8 -*-

from datetime import datetime

from odoo import models, fields, api, _
from odoo.exceptions import UserError,ValidationError

class EntitySatus(models.Model):
    _name = 'entity.status'

    name = fields.Char('Name')

class CRM(models.Model):
    _inherit = 'res.partner'

    @api.onchange('company_type')
    def onchange_company_type(self):
        super(CRM, self).onchange_company_type()
        self.id_type = False
        if self.company_type == 'person':
            self.id_type = 'rsa_id'

    # fields added for Individual
    first_name = fields.Char('First Name')
    preferred_name = fields.Char('Preferred Name')
    id_type = fields.Selection([('rsa_id', 'RSA ID'), ('passport', 'Passport'), ('temp_id', 'Temporary ID')], string="ID type", default="rsa_id")
    id_rsa = fields.Char('ID Number')
    surname = fields.Char('Surname')
    initials = fields.Char('Initials')
    second_name = fields.Char('Second Name')
    date_of_birth = fields.Date('Date of Birth')
    gender = fields.Selection([('male', 'Male'), ('female', 'Female')], string="Gender")
    marrige_date = fields.Date('Marriage Date')
    country_of_birth = fields.Many2one('res.country', string='Country of Birth', ondelete='restrict')
    home_language = fields.Selection([
        ('Afrikaans', 'Afrikaans'),
        ('Albanian', 'Albanian'),
        ('Arabic', 'Arabic'),
        ('Bengali', 'Bengali'),
        ('Bosnian', 'Bosnian'),
        ('Cantonese', 'Cantonese'),
        ('Croatian', 'Croatian'),
        ('Czech', 'Czech'),
        ('Danish', 'Danish'),
        ('Dutch', 'Dutch'),
        ('English', 'English'),
        ('Fijian', 'Fijian'),
        ('Filipino', 'Filipino'),
        ('Finnish', 'Finnish'),
        ('French', 'French'),
        ('German', 'German'),
        ('Greek', 'Greek'),
        ('Hebrew', 'Hebrew'),
        ('Hindi', 'Hindi'),
        ('Irish', 'Irish'),
        ('IsiNdebele', 'IsiNdebele (Ndebele)'),
        ('IsiXhosa', 'IsiXhosa (Xhosa)'),
        ('IsiZulu', 'IsiZulu (Zulu)'),
        ('Italian', 'Italian'),
        ('Japanese', 'Japanese'),
        ('Korean', 'Korean'),
        ('Lao', 'Lao'),
        ('Malay', 'Malay'),
        ('Mandarin', 'Mandarin'),
        ('Maori', 'Maori'),
        ('Nepali', 'Nepali'),
        ('Northern', 'Northern'),
        ('Sotho', 'Sotho (Sepedi)'),
        ('Norwegian', 'Norwegian'),
        ('Other', 'Other'),
        ('Persian', 'Persian'),
        ('Polish', 'Polish'),
        ('Portugese', 'Portugese'),
        ('Russian', 'Russian'),
        ('Sesotho', 'Sesotho (Southern Sotho)'),
        ('Setswana', 'Setswana (Tswana)'),
        ('SiSwati', 'SiSwati (Swati)'),
        ('Spanish', 'Spanish'),
        ('Swedish', 'Swedish'),
        ('Thai', 'Thai'),
        ('Tshivenda', 'Tshivenda (Venda)'),
        ('Vietnamese', 'Vietnamese'),
        ('Welsh', 'Welsh'),
        ('Xitsonga', 'Xitsonga (Tsonga)'),
    ], string="Home Language")
    third_name = fields.Char('Third Name')
    retirement_age = fields.Integer('Retirement Age')
    marital_status = fields.Selection([
        ('single', 'Single'),
        ('married_cop', 'Married (COP)'),
        ('life_partner', 'Life Partner'),
        ('married_anc', 'Married (ANC)'),
        ('married_anc_acc', 'Married (ANC with Accrual)'),
        ('engaged', 'Engaged'),
        ('live_in', 'Live in Relationship'),
        ('divorce', 'Divorced'),
        ('widowed', 'Widowed'),
        ('married_unk', 'Married - Unknown Legal Status'),
        ('unknown', 'Unknown'),
    ], string="Marital Status")
    maiden_name = fields.Char('Maiden Name')
    nationality = fields.Many2one('res.country', string='Nationality', ondelete='restrict')
    resident_status = fields.Selection([
        ('permanent', 'Permanent Residence'),
        ('sa_citizen', 'SA Citizen'),
        ('emp_pass', 'Employment Pass'),
        ('foreigner', 'Foreigner'),
    ], string="Resident Status")
    religion = fields.Selection([
        ('Atheist', 'Atheist'),
        ('Baha', "Baha'i"),
        ('Buddhist', 'Buddhist'),
        ('Candombl', 'Candombl'),
        ('Christian_Anglican', 'Christian - Anglican'),
        ('Christian_Baptist', 'Christian - Baptist'),
        ('Christian_Methodist', 'Christian - Methodist'),
        ('Christian_Protestant', 'Christian - Protestant'),
        ('Christian_Catholic', 'Christian - Catholic'),
        ('Christian_Greek', 'Christian - Greek'),
        ('Orthodox', 'Orthodox'),
        ('Christian_Roman Catholic', 'Christian - Roman Catholic'),
        ('Christian_Other', 'Christian - Other'),
        ('HinduIslam', 'HinduIslam'),
        ('Jain', 'Jain'),
        ('Jehovah', "Jehovah's Witness"),
        ('Judaism', 'Judaism'),
        ('Mormon', 'Mormon'),
        ('Other', 'Other'),
        ('Paganist', 'Paganist'),
        ('Rastafari', 'Rastafari'),
        ('Santeria', 'Santeria'),
        ('Shinto', 'Shinto'),
        ('Sikh', 'Sikh'),
        ('Taoism', 'Taoism'),
        ('Unitarian', 'Unitarian'),
        ('Zoroastrian', 'Zoroastrian'),
    ], string="Religion")
    tax_resident_status = fields.Selection([
        ('resident', 'Resident'),
        ('non_resident', 'Non Resident')
    ], string="Tax Resident Status")
    health = fields.Selection([
        ('excellent', 'Excellent'),
        ('good', 'Good'),
        ('poor', 'Poor'),
        ], string="Health")

    qualification = fields.Selection([
        ('no_matric', 'No Matric'),
        ('matric', 'Matric'),
        ('3_y_d', '3 Year Dipl/Degr'),
        ('4_y_d', '4 Year Dipl/Degr'),
    ], 'Qualification')
    gross_month_salary = fields.Float('Gross Monthly Salary')
    employer = fields.Many2one('res.partner', string='Employer')
    employer_name = fields.Char('Employer Name')
    occupation = fields.Char('Occupation')
    gross_retirement_fund = fields.Boolean('Group Retirement Fund')
    fund_value = fields.Float('Fund Value')
    smokes_status = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No'),
    ], 'Smoker Status')
    medical_aid_company = fields.Char('Medical Aid Company')
    medical_aid_plan = fields.Char('Medical Aid Plan')
    medical_aid_number = fields.Char('Medical Aid Number')
    medical_aid_date = fields.Date('Medical Aid Date')

    # fields added for Company
    trade_name = fields.Char('Trade Name')
    company = fields.Selection([
        ('public_company', 'Public Company'),
        ('close_corporation', 'Close Corporation'),
        ('section_21_company', 'Section 21 Company'),
        ('incorporated_practice', 'Incorporated Practice'),
    ], string="Company Type")
    total_issue_share = fields.Float('Total Issue Share')
    financial_year_end = fields.Date('Financial Year End')
    date_of_valuation = fields.Date('Date of Valuation')
    valuation_method = fields.Selection([
        ('earning_multi', 'Earnings Multiple'),
        ('net_asset_back', 'Net Asset Back'),
        ('discounted_chasflow', 'Discounted Cashflow'),
    ], string='Valuation Method')
    company_name = fields.Char('Name')
    date_of_inco = fields.Date('Date of Incorporation')
    revenue = fields.Float('Revenue')
    nbr_emp = fields.Integer('Number of Employees')
    valuation_type = fields.Selection([
        ('fair_market_value', 'Fair Market Value'),
        ('formal_value', 'Formal Valuation'),
    ], string="Valuation Type")
    valuation_provider = fields.Selection([
        ('business_owner', 'Business Owners'),
        ('accountant', 'Accountant'),
        ('other', 'other'),
    ], string="Valuation Provided By")
    firm_name = fields.Char('Firm')
    reg_number = fields.Char('Registration Number')
    business_value = fields.Float('Business Value')

    # fields added for both Company and Individual
    last_prev_name = fields.Char('Last Previous Name')
    tax_office = fields.Char('Tax Office')
    income_tax_number = fields.Char('Income Tax Number')
    client_adviser_id = fields.Many2one('res.users', 'Client Adviser')
    admin_id = fields.Many2one('res.users', 'Administrator')
    portfolio_analyst_id = fields.Many2one('res.users', 'Portfolio Analyst')
    entity_status = fields.Many2many('entity.status', 'res_partner_entity_rel', 'partner_id', 'entity_id', string='Entity Status')
    category = fields.Selection([
        ('diamond_first', 'Diamond / First'),
        ('platinum_business', 'Platinum / Business'),
        ('gold_ecomony', 'Gold / Economy'),
        ('eb', 'EB'),
        ('client', 'Client'),
        ('supplier', 'Supplier'),
        ('unknown', 'Unknown'),
    ], string="Category")
    services = fields.Many2many('crm_attooh.service', 'res_partner_service_rel', 'partner_id', 'service_id', string='Services')
    privacy = fields.Selection([('yes', 'Yes'), ('no', 'No')], string="Privacy")

    # change string of existing field
    vat = fields.Char(string='VAT Number')

    relationship = fields.Selection([
            ('Additional_Partner', 'Additional Partner'),
            ('Adult_Dependant', 'Adult Dependant'),
            ('Aunt', 'Aunt'),
            ('Child', 'Child'),
            ('Cousin', 'Cousin'),
            ('Dependent Parent', 'Dependent Parent'),
            ('Dependent Parent-in-law', 'Dependent Parent-in-law'),
            ('Ex-Partner', 'Ex-Partner'),
            ('Fiance', 'Fiance'),
            ('Fiancee', 'Fiancee'),
            ('Foster_Child', 'Foster Child'),
            ('Foster_Parent', 'Foster Parent'),
            ('Foster_Sibling', 'Foster Sibling'),
            ('Friend', 'Friend'),
            ('God_Parent', 'God Parent'),
            ('Godchild', 'Godchild'),
            ('Grand_Aunt', 'Grand Aunt'),
            ('Grand_Nephew', 'Grand Nephew'),
            ('Grand_Niece', 'Grand Niece'),
            ('Grand_Parent', 'Grand Parent'),
            ('Grand_Parent-in-Law', 'Grand Parent-in-Law'),
            ('Grand_Uncle', 'Grand Uncle'),
            ('Grandchild', 'Grandchild'),
            ('Great_Grand_Aunt', 'Great Grand Aunt'),
            ('Great_Grand_Nephew', 'Great Grand Nephew'),
            ('Great_Grand_Niece', 'Great Grand Niece'),
            ('Great_Grand_Parent', 'Great Grand Parent'),
            ('Great_Grand_Uncle', 'Great Grand Uncle'),
            ('Great_Grandchild', 'Great Grandchild'),
            ('Half-Sibling', 'Half-Sibling'),
            ('Nephew', 'Nephew'),
            ('Niece', 'Niece'),
            ('Other', 'Other'),
            ('Parent', 'Parent'),
            ('Parent-In-Law', 'Parent-In-Law'),
            ('Partner', 'Partner'),
            ('Servant', 'Servant'),
            ('Sibling', 'Sibling'),
            ('Sibling-in-Law', 'Sibling-in-Law'),
            ('Spouse', 'Spouse'),
            ('Step_Sibling', 'Step Sibling'),
            ('Stepchild', 'Stepchild'),
            ('Step-Grand-Parent', 'Step-Grand Parent'),
            ('Step-Grandchild', 'Step-Grandchild'),
            ('Step-Parent', 'Step-Parent'),
            ('Uncle', 'Uncle'),
            ('Ward', 'Ward'),
        ], string="Relationship")

    is_beneficiary = fields.Boolean('Is a Beneficiary')
    dependent_id = fields.Many2one('res.partner')
    dependent_ids = fields.One2many('res.partner', 'dependent_id', string="Relationship")
    income_ids = fields.One2many('partner.income', 'partner_id', string="Incomes")
    expense_ids = fields.One2many('partner.expense', 'partner_id', string="Expenses")
    deduction_ids = fields.One2many('partner.deduction', 'partner_id', string="Deductions")
    debt_obligation_ids = fields.One2many('debt.obligations', 'partner_id', string='Debt Obligations',
                                  domain=[('account_status', 'in', ('Active', 'In Arrears')), ('ignore', '=', False)],
                                  track_visibility='always')
    other_debt_obligation_ids = fields.One2many('debt.obligations', 'partner_id', string='Other Debt Obligations',
                                  domain=[('account_status', 'not in', ('Active', 'In Arrears')), ('ignore', '=', True)],
                                  track_visibility='always')
    asset_ids = fields.One2many('partner.asset', 'partner_id', string='Assets')
    attachment_count = fields.Integer(compute="_compute_attachment_count", string="Attachments")

    spouse_id = fields.Many2one('res.partner', 'Spouse')

    def _compute_attachment_count(self):
        Attachment = self.env['ir.attachment']
        for partner in self:
            partner.attachment_count = Attachment.search_count([('res_model', '=', 'res.partner'), ('res_id', '=', partner.id)])

    @api.multi
    def view_attachments(self):
        self.ensure_one()
        attachments = self.env['ir.attachment'].search([('res_model', '=', 'res.partner'), ('res_id', '=', self.id)])
        action = self.env.ref('base.action_attachment').read()[0]
        action['domain'] = [('id', 'in', attachments.ids)]
        action['context'] = {'default_res_model': 'res.partner', 'default_res_id': self.id}
        return action

    @api.onchange('first_name')
    def on_change_first_name(self):
        if not self.preferred_name:
            if self.name:
                name = self.name
                first_name = name.split(' ')
                first_name[0] = self.first_name
                self.name = ' '.join(first_name)
            else:
                self.name = self.first_name

    @api.onchange('surname')
    def on_change_surname(self):
        if self.name:
            name = self.name
            surname = name.split(' ')
            if len(surname) > 1:
                surname[-1] = self.surname
                self.name = ' '.join(surname)
            else:
                self.name = '%s %s' % (self.name, self.surname)
        else:
            self.name = self.surname

    @api.onchange('preferred_name')
    def on_change_preffre_name(self):
        if self.name:
            name = self.name
            preferred_name = name.split(' ')
            preferred_name[0] = self.preferred_name
            self.name = ' '.join(preferred_name)
        else:
            self.name = self.preferred_name
        if not self.preferred_name:
            if self.name:
                name = self.name
                first_name = name.split(' ')
                first_name[0] = self.first_name
                self.name = ' '.join(first_name)
            else:
                self.name = self.first_name

    @api.multi
    @api.onchange('id_rsa', 'id_type')
    def on_change_rsa_id(self):
        if self.id_type == 'rsa_id' and self.id_rsa:
            number = self.id_rsa
            valid = True
            if len(number) != 13:
                valid = False
            try:
                int(number)
            except ValueError:
                valid = False
            if not valid:
                raise UserError(_('Invalid RSA Number!'))
            current_year = datetime.now().year % 100
            prefix = '19'
            if (current_year > int(number[0:2])):
                prefix = '20'
            year = int(prefix + number[0:2])
            month = int(number[2:4])
            day = int(number[4:6])
            gender = int(number[6:10])
            resident_status = int(number[10:11])
            if (month <= 0 or month > 12):
                valid = False
            if(day <= 0 or day > 31):
                valid = False
            if not valid:
                raise UserError(_('Invalid RSA Number!'))
            if (gender <= 4999):
                self.gender = 'female'
            else:
                self.gender = 'male'
            self.date_of_birth = '%s-%s-%s' % (year, month, day)
            if resident_status == 1:
                self.resident_status = 'permanent'
            if resident_status == 0:
                self.resident_status = 'sa_citizen'

    @api.constrains('id_rsa')
    def check_duplicate_rsa_no(self):
        if self.id_rsa:
            count_no = self.search_count([('id_rsa', '=', self.id_rsa)])
            if count_no > 1:
                raise ValidationError(_('Duplicate ID Number not permitted'))


class PartnerIncome(models.Model):
    _name = 'partner.income'
    _description = "Partner Income"

    income = fields.Selection([('Basic Salary', 'Basic Salary'),
                               ('Gross Salary', 'Gross Salary'),
                               ('Income', 'Income'),
                               ('Bonuses', 'Bonuses'),
                               ('House allowance', 'House allowance'),
                               ('Interest received', 'Interest received'),
                               ('Maintenance', 'Maintenance'),
                               ('Overtime', 'Overtime'),
                               ('Personal gifts', 'Personal gifts'),
                               ('Rent received', 'Rent received'),
                               ('Second Job', 'Second Job'),
                               ('Subsidies and grants', 'Subsidies and grants'),
                               ('Basic Income', 'Basic Income'),
                               ('Pension', 'Pension'),
                               ('Other Income', 'Other Income')
                              ], string='Income', required=True)
    original_amount = fields.Float('Amount')
    comment = fields.Char('Comment')
    partner_id = fields.Many2one('res.partner', 'Partner')


class PartnerDeduction(models.Model):
    _name = 'partner.deduction'
    _description = "Partner Deduction"

    deduction = fields.Selection([('PAYE', 'PAYE'),
                                  ('UIF', 'UIF'),
                                  ('RAS / Endowment', 'RAS / Endowment'),
                                  ('SITE', 'SITE'),
                                  ('Other Deduction', 'Other Deduction'),
                                  ('Medical-Aid', 'Medical-Aid'),
                                  ('Pension Fund', 'Pension Fund'),
                                  ('Loans', 'Loans'),
                                  ('Union Subscription', 'Union Subscription'),
                                  ('Insurance', 'Insurance'),
                                  ('Group Life', 'Group Life'),
                                  ('Garnishees / Admin Order', 'Garnishees / Admin Order'),
                                  ('Funeral Policy', 'Funeral Policy')
                                  ], string='Deduction', required=True)
    original_amount = fields.Float('Amount')
    comment = fields.Char('Comment')
    partner_id = fields.Many2one('res.partner', 'Partner')


class PartnerExpense(models.Model):
    _name = 'partner.expense'
    _description = "Partner Expense"

    expense = fields.Selection([
        ('Accounting fees', 'Accounting fees'),
        ('Accounts (Edgars, Woolworths etc.)', 'Accounts (Edgars, Woolworths etc.)'),
        ('Bank Charges', 'Bank Charges'),
        ('Bond repayment/Rent', 'Bond repayment/Rent'),
        ('Cell phone (Personal)', 'Cell phone (Personal)'),
        ('Chemist', 'Chemist'),
        ('Cleaning services', 'Cleaning services'),
        ('Clothing', 'Clothing'),
        ('Credit card', 'Credit card'),
        ('DSTV', 'DSTV'),
        ('Entertainment (Personal)', 'Entertainment (Personal)'),
        ('Food / Meat / Groceries', 'Food / Meat / Groceries'),
        ('Funeral policy', 'Funeral policy'),
        ('Garden / House maintenance', 'Garden / House maintenance'),
        ('Garden Services', 'Garden Services'),
        ('Holiday/s', 'Holiday/s'),
        ('Internet', 'Internet'),
        ('Levies', 'Levies'),
        ('Life assurance', 'Life assurance'),
        ('Medical Aid Contribution', 'Medical Aid Contribution'),
        ('Municipal services', 'Municipal services'),
        ('Personal loans', 'Personal loans'),
        ('Personal training/Sport', 'Personal training/Sport'),
        ('Rates & Taxes', 'Rates & Taxes'),
        ('Salary expenses', 'Salary expenses'),
        ('Savings effort', 'Savings effort'),
        ('School Fees', 'School Fees'),
        ('Security', 'Security'),
        ('Short term assurance', 'Short term assurance'),
        ('Telephone (Personal)', 'Telephone (Personal)'),
        ('Tithing/Donations', 'Tithing/Donations'),
        ('Travel fees/Fuel (Personal)', 'Travel fees/Fuel (Personal)'),
        ('Tuition/School fees', 'Tuition/School fees'),
        ('Vehicle instalment 1', 'Vehicle instalment 1'),
        ('Vehicle instalment 2', 'Vehicle instalment 2'),
        ('Vehicle maintenance', 'Vehicle maintenance')
    ], string='Expense', required=True)
    original_amount = fields.Float('Amount')
    comment = fields.Char('Comment')
    partner_id = fields.Many2one('res.partner', 'Partner')


class DebtObligations(models.Model):
    _name = "debt.obligations"
    _inherit = ['mail.thread']

    outstanding_total = fields.Float('Outstanding Balance')
    monthly_commitment = fields.Float('Monthly Installment')
    partner_id = fields.Many2one('res.partner', 'Partner')
    account_no = fields.Char('Account No.')
    arrears_amount = fields.Float('Arrears Amount')
    account_status = fields.Selection([('Active', 'Active'),
                                       ('In Arrears', 'In Arrears'),
                                       ('Paid Up', 'Paid Up'),
                                       ('Closed', 'Closed')
                                       ], string='Status of Account', default="Active", rack_visibility='always')
    account_date = fields.Date('Date Account Open')
    pay_date = fields.Date('Last Paid Date')
    account_type = fields.Selection([('H', 'Home Loan'),
                                     ('U', 'Utility'),
                                     ('J', 'Unsecured Revolving Loan'),
                                     ('F', 'Open Account'),
                                     ('T', 'Student Loans'),
                                     ('I', 'Instalment Account'),
                                     ('C', 'Credit Card'),
                                     ('V', 'Overdraft'),
                                     ('S', 'Short Term Insurance'),
                                     ('D', 'Debt Recovery'),
                                     ('B', 'Building Loan'),
                                     ('P', 'Personal Cash Loan'),
                                     ('L', 'Life Insurance'),
                                     ('G', 'Garage Card'),
                                     ('N', 'Pension Backed Lending'),
                                     ('K', 'Unsecured Term Loan'),
                                     ('E', 'Single Credit Facility'),
                                     ('O', 'Open Account'),
                                     ('R', 'Revolving Credit')
                                       ], string='Credit Type')
    client_type = fields.Selection([('Applicant', 'Applicant'),
                                     ('Co-Applicant', 'Co-Applicant')
                                   ], string='Client Type')
    source = fields.Selection([('Bureau', 'Bureau'),
                                 ('Compliant COB', 'Compliant COB'),
                                 ('Customer', 'Customer'),
                                 ('Non-compliant COB', 'Non-compliant COB')
                               ], string='Source')
    interest_rate = fields.Float('Interest Rate',)
    original_term = fields.Integer('Original Term')
    remaining_term = fields.Integer('Remaining Term')
    monthly_fee = fields.Float('Monthly Fee')
    annual_fee = fields.Float('Annual Fee')
    insurance_premium = fields.Float('Monthly Insurance Premium')
    payment_method = fields.Selection([('Debit Order', 'Debit Order'),
                                       ('EFT', 'EFT'),
                                       ('Cash', 'Cash')
                                       ], 'Payment Method')
    internal_notes = fields.Text('Internal Notes')
    credit_limit_amt = fields.Float("Debt Amount/Credit Limit")
    ignore = fields.Boolean("Ignore")
    creditor_name = fields.Char("Creditor")
    ref_no = fields.Char("Ref No.")

    @api.onchange('account_status')
    def _onchange_account_status(self):
        if self.account_status in ('Active', 'In Arrears'):
            self.update({'ignore': False})
        else:
            self.update({'ignore': True})


class PartnerAsset(models.Model):
    _name = 'partner.asset'
    _description = "Partner Asset"

    asset_type = fields.Selection([
        ('cashbonds', 'CashBonds'),
        ('shares', 'Shares'),
        ('unit_trusts', 'Unit Trusts'),
        ('containers', 'Containers'),
        ('lisps', 'LISPS'),
        ('property', 'Property'),
        ('other_investments', 'Other Investments')
    ], string="Asset Type")
    description = fields.Text(string="Description")
    current_market_value = fields.Float("Current Market Value")
    original_purchase_price = fields.Float("Original Purchase Price")
    additional_improvements = fields.Float("Additional Improvements")
    income_received = fields.Float("Income Received")
    date_of_purchase = fields.Date("Date of Purchase")
    owner = fields.Char(string="Owner/s")
    partner_id = fields.Many2one('res.partner', string='Partner')
