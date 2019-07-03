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

            logger.info("----------------------------------------------%s", pricelist.get('unitprice_currency'))
            supplier_id = None
            supplier_name = ""
            if supplier:
                supplier_id = supplier[0].id
                supplier_name = supplier[0].name
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


                product_id.product_tmpl_id.write({
                    'x_studio_carton_type': pricelist.get('Packing_type'), 
                    'x_studio_carton_l': pricelist.get('Packing_length'), 
                    'x_studio_carton_width': pricelist.get('Packing_width'), 
                    'x_studio_carton_height': pricelist.get('Packing_height'), 
                    'x_studio_carton_weight': pricelist.get('Packing_weight'), 
                    'x_studio_pieces_per_carton': pricelist.get('Pieces_pr_Packing'),
                    'x_studio_buying_price_netimpex':pricelist.get('unitprice'),
                    'x_studio_buying_currency_netimpex':pricelist.get('unitprice_currency'),
                    'x_studio_supplier_netimpex' : supplier_name,
                    })
                    
        return

    def get_or_create_product_category(self, product_category):
         
        article_category = self.env['product.category'].search([('name', '=', product_category)])
        if not article_category:
            article_category = self.env['product.category'].create({'name':product_category})
            return article_category.id

        return article_category[0].id

    def create_products(self):
        """
        Create Products 
        """
        get_product_url = NETIMPEX_API_BASE_URL+ARTICLE_MASTER_URL
        get_product_response = requests.get(get_product_url)
        product_data = get_product_response.json()
        logger.info("-----------------------total products "+str(len(product_data)))
        logger.info("-----------------------import - 1500 - all")
        
        for index, product in enumerate(product_data[1500:]):
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
             'description':  product.get('article_description')
            }

            product_category = product.get('Article_category')
            if product_category : 
                vals['categ_id'] = self.get_or_create_product_category(product_category)


            if not product_id:
                product_id = self.env['product.product'].create(vals)
            else:
                product_id.write(vals)

            product_id.product_tmpl_id.write({
                'x_studio_hs_code' : product.get('hscode'),
                'x_studio_article_length': product.get('Article_length'),
                'x_studio_article_height': product.get('Article_height'),
                'x_studio_article_weight': product.get('Article_weight'),
                'x_studio_article_width': product.get('Article_width'),
                })
        
        return

    def get_delivery_dict(self, partner):
        del_country = self.env['res.country'].search([('code', '=',partner['delivery_country'])])
        del_country_id = False
        if del_country:
            del_country_id = del_country[0].id

        delivery_vals = {
            'type':'delivery', 
            'street': partner.get('delivery_Address'),
            'street2': partner.get('delivery_streetname'),
            'city': partner.get('delivery_city'),
            'zip': partner.get('delivery_zip_code'),
            'country_id': del_country_id,
            'name': partner.get('delivery_ContactPerson'),
            'email': partner.get('delivery_Emailid'),
            'phone': partner.get('delivery_Phoneno'),
        }

        return delivery_vals


    def create_partners(self):
        """
        Create Products 
        """
        get_partner_url = NETIMPEX_API_BASE_URL+COMPANY_MASTER_URL

        get_partner_response = requests.get(get_partner_url)
        partner_data = get_partner_response.json()
        
        logger.info("-----------------------total partners "+str(len(partner_data)))
        for index, partner in enumerate(partner_data):

            logger.info(str(index)+"----------"+partner.get('company_name'))
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
                'company_type': 'company',
            }

            comp_type = partner.get('cpy_type')
            if comp_type and comp_type.lower()=='customer':
                vals['customer'] = True
                vals['supplier'] = False

            if comp_type and comp_type.lower()=='supplier':
                vals['supplier'] = True
                vals['customer'] = False

            partner_cid = self.env['res.partner'].search([('vendor_cid', '=', partner['cid'])])

            delivery_vals = self.get_delivery_dict(partner)
            if not partner_cid:
                vals['child_ids'] = [(0, 0,  delivery_vals)] 
                self.env['res.partner'].create(vals)
            else:
                child_ids = partner_cid.child_ids.search([('parent_id', '=', partner_cid.id), ('street', '=', delivery_vals['street']), ('street2', '=', delivery_vals['street2']),])

                if child_ids: 
                    delivery_id = child_ids[0].id
                    vals['child_ids'] = [(1, delivery_id, delivery_vals)]
                else:
                    vals['child_ids'] = [(0, 0,  delivery_vals)] 

                partner_cid.write(vals)
        return



    @api.model
    def create(self, vals):
        try:
            tools.image_resize_images(vals)
            return super(Product, self).create(vals)
        except IOError:
            pass
        except Exception:
            pass
        return


    @api.model
    def get_products_from_netimpex(self):
        print ("--------------------start cron for data import")
        #Create Suppliers
        logger.info("Creating partners")
        self.create_partners()
        logger.info("Partners created")

        ############################################################################
        #Commented blow code to bypass import product and price list data into odoo 
        #in order to update only partner data it should be uncommented after complete
        # this task
        ############################################################################

        #Create Products
        # logger.info("Creating products")
        # self.create_products() 
        # logger.info("Products created")
        #Create and Update Pricelist for Products
        # logger.info("Creating pricelist")
        # self.create_pricelist()
        logger.info("pricelist created")
        return

class ProductTemplate(models.Model):
    _inherit = ['product.template']


    def remove_redundant_article(self):

        logger.info("--------------------------------------------------inside remove redundant article cron")

        all_products = self.env["product.template"].search([])

        duplicate_products_name = []

        for each_product in all_products:
            logger.info("==========================product name %s" % each_product.name)
            duplicate_products = self.env["product.template"].search([('name', '=', each_product.name)])

            if len(duplicate_products)>1 and duplicate_products[0].name not in duplicate_products_name:
                duplicate_products_name.append(duplicate_products[0].name)
                for each_duplicate_product in duplicate_products[1:]:
                    each_duplicate_product.write({'active':False})


        logger.info("=============================%s" % duplicate_products_name)