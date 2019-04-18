 # -*- coding: utf-8 -*-

from odoo import models, fields, api

class Suppllier_details(models.Model):

    _inherit = 'res.partner'

    vendor_cid = fields.Integer("CID", required=False)
    vendor_company_code = fields.Char("Company Code")
    vendor_bank_name = fields.Char("Bank Name")
    vendor_account_number = fields.Char("Account Number")
    vendor_bic = fields.Char("BIC")
    vendor_vat = fields.Char("VAT")
    vendor_payment_term = fields.Char("Payment Terms")
    vendor_discout = fields.Float("Discount")
    vendor_currency = fields.Many2one('res.currency')
    vendor_registration_date = fields.Date("Registration Date")
    vendor_country = fields.Many2one('res.country')
    no_of_users = fields.Integer("Number of Users")

