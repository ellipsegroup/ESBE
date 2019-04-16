 # -*- coding: utf-8 -*-

# import requests
# import json
# import re
# import datetime
# from odoo.exceptions import Warning
from odoo import models, fields, api

class ProductPricelist(models.Model):
    
    _name = 'product.pricelist.lines'

    unitprice = fields.Float('Unit Price', required=True)
    unitprice_currency = fields.Char('Unit Price Currency')
    unitprice_place = fields.Char('Unitprice Place')
    packing_length = fields.Float('Packing Lrngth')
    packing_width = fields.Float('Packing Width')
    packing_height = fields.Float('Packing Height')
    packing_weight = fields.Float('Packing Weight')
    pieces_pr_packing = fields.Integer('Peices Per Packaging')
    date = fields.Date('Date')
    status = fields.Boolean('Status', default=False)
    agency_code = fields.Char('Agency Code')
    product_id = fields.Many2one('product.template', string='Product Reference', required=True, ondelete='cascade', index=True, copy=False)
    netimpex_pricelist_id = fields.Integer('Netimpex Pricelist ID')

    
