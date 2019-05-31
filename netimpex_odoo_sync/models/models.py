 # -*- coding: utf-8 -*-

import re, base64
import requests
from PIL import Image
import io
import json
import datetime
from odoo.exceptions import Warning
from odoo import models, fields, api, tools
import logging

logger=logging.getLogger()

IMAGE_BASE_URL = 'http://www.esbe.netimpex.com/'
ARTICLE_MASTER_URL = '/ArticleMaster'
ARTICLE_PRICELIST_URL = '/ArticlePricelist'
COMPANY_MASTER_URL = '/CompanyMaster'
NETIMPEX_API_BASE_URL = 'http://www.esbeapi.netimpex.com:89/api'

class Product(models.Model):
    """docstring for Product"""
    _inherit = ['product.product']

    netimpex_product_id = fields.Integer('Netimpex Article Id', required=False)
    agency_code_id = fields.Char('Agency Code')
    article_width_id = fields.Char('Width')
    article_height_id = fields.Char('Height')
    article_length_id = fields.Char('Length')
    article_create_date = fields.Date('Create Date')
    article_hsn_code = fields.Char('HS Code')
    pricelist_line = fields.One2many('product.pricelist.lines', 'product_id', string='Pricelist Lines', copy=True)

    def create_pricelist(self):
        """
        Create Pricelist 
        """
        get_pricelist_url = NETIMPEX_API_BASE_URL+ARTICLE_PRICELIST_URL
        get_pricelist_response = requests.get(get_pricelist_url)
        pricelist_data = get_pricelist_response.json()
  
        for index, pricelist in enumerate(pricelist_data):
            art_id = pricelist.get('Article_id')
            product_id = self.env['product.product'].search([('netimpex_product_id', '=', art_id)])
            pricelist_id = pricelist.get('price_id')
            check_pricelist = self.env['product.pricelist.lines'].search([('netimpex_pricelist_id','=', pricelist_id)])
            supplier = self.env['res.partner'].search([('vendor_cid','=',pricelist.get('supplier_id'))])
            supplier_id = None
            if supplier:
                supplier_id = supplier[0].id
            if product_id:
                vals = {
                    'pieces_pr_packing': pricelist.get('Pieces_pr_Packing'), 
                    'agency_code': pricelist.get('agency_code'),
                    'packing_height': pricelist.get('Packing_height'),
                    'product_id': product_id[0].id,
                    'unitprice_currency': pricelist.get('unitprice_currency'),
                    'status': True if pricelist.get('isActive_status') == 'true' else False,
                    'packing_weight': pricelist.get('Packing_weight'),
                    'agency_code': pricelist.get('agency_code'),
                    # 'supplier_id': supplier_id,
                    # 'seller_ids' :  [(0,0, {'id':supplier_id , 'name': supplier.name })],
                    'date': pricelist.get('date_created').split('T')[0],
                    'packing_width': pricelist.get('Packing_width'),
                    'packing_length': pricelist.get('Packing_length'), 
                    'unitprice': pricelist.get('unitprice'), 
                    'unitprice_place': pricelist.get('unitprice_place'),
                    'netimpex_pricelist_id':pricelist.get('price_id'),
                    }
                if check_pricelist:
                    logger.info("updating new pricelist")
                    check_pricelist.write(vals)
                else:
                    logger.info("Creating new pricelist")
                    pricelist_line = self.env['product.pricelist.lines'].create(vals)
                    
        return

    def create_products(self):
        """
        Create Products 
        """
        get_product_url = NETIMPEX_API_BASE_URL+ARTICLE_MASTER_URL
        get_product_response = requests.get(get_product_url)
        product_data = get_product_response.json()
        logger.info("-----------------------total products "+str(len(product_data)))
        logger.info("-----------------------import first 1000 - 1500")
        
        for index, product in enumerate(product_data[1000:1500]):
            art_id = product.get('article_id')
            product_id = self.env['product.product'].search([('netimpex_product_id', '=', art_id)])
            TimestampUtc = product['article_create_date']
            date = TimestampUtc.split('T')[0]
            if product['picture']:
                product_image_url = IMAGE_BASE_URL+product['picture']
                image_data = requests.get(product_image_url).content
                image_b64data = base64.b64encode(image_data)
            else:
                pass

            logger.info("------------------product name %s ---- %s" % (str(index), product.get('Article_name')))
            vals = {
             'description_sale': product.get('article_description'),
             'name': product.get('Article_name'),
             'image_medium':image_b64data or "",
             'netimpex_product_id' : product.get('article_id'),
             'default_code' : product.get('refrence_no'),
             'agency_code_id' : product.get('agency_code'),
             'article_width_id' : product.get('Article_width'),
             'article_height_id' : product.get('Article_height'),
             'article_length_id' : product.get('Article_length'),
             'article_create_date' : date,
             'article_hsn_code' : product.get('hscode'),
             'x_studio_hs_code' : product.get('hscode'),
            }

            if not product_id:
                self.env['product.product'].create(vals)
            else:
                product_id.write(vals)
                
        
        return

    def create_partners(self):
        """
        Create Products 
        """
        get_partner_url = NETIMPEX_API_BASE_URL+COMPANY_MASTER_URL

        get_partner_response = requests.get(get_partner_url)
        partner_data = get_partner_response.json()

        for index, partner in enumerate(partner_data):
            country = self.env['res.country'].search([('code', '=',partner['country'])])
            
            if country:
                country_id = country[0].id

            currency = self.env['res.currency'].search([('name', '=', partner['currency'])])

            if currency:
                currency_id = currency[0].id

            vals = {
                'name':partner.get('company_name'),
                'country_id': country_id or None,
                'vendor_currency': currency_id or None,
                'vendor_cid': partner.get('cid'),
                'vendor_company_code': partner.get('company_code'),
                'vendor_bank_name': partner.get('Bank_name'),
                'vendor_account_number': partner.get('Bnk_acnt_no'),
                'vendor_bic': partner.get('bic'),
                'vendor_vat': partner.get('vat'),
                'vendor_payment_term': partner.get('Paymnt_term'),
                'vendor_discout': partner.get('Discount'),
                'vendor_registration_date' : partner.get('Regis_date').split('T')[0] if partner.get('Regis_date') else None,
                'no_of_users' : partner.get('No_of_users'),
                'customer': False,
                'supplier': True,
            }

            partner_cid = self.env['res.partner'].search([('vendor_cid', '=', partner['cid'])])
            if not partner_cid:
                self.env['res.partner'].create(vals)
            else:
                partner_cid.write(vals)
        return



    # @api.model
    # def create(self, vals):
    #     try:
    #         tools.image_resize_images(vals)
    #         return super(Product, self).create(vals)
    #     except IOError:
    #         pass
    #     except Exception:
    #         logger.info("------------------------Exception")
    #         vals.pop('image_medium')
    #         return super(Product, self).create(vals)
    #     return


    @api.model
    def get_products_from_netimpex(self):
        print ("--------------------start cron for data import")
        #Create Suppliers
        logger.info("Creating partners")
        self.create_partners()
        logger.info("Partners created")
        #Create Products
        logger.info("Creating products")
        self.create_products()
        logger.info("Products created")
        #Create and Update Pricelist for Products
        logger.info("Creating pricelist")
        self.create_pricelist()
        logger.info("pricelist created")
        return