# -*- coding: utf-8 -*-
from odoo import http

# class NetimpexOdooSync(http.Controller):
#     @http.route('/netimpex_odoo_sync/netimpex_odoo_sync/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/netimpex_odoo_sync/netimpex_odoo_sync/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('netimpex_odoo_sync.listing', {
#             'root': '/netimpex_odoo_sync/netimpex_odoo_sync',
#             'objects': http.request.env['netimpex_odoo_sync.netimpex_odoo_sync'].search([]),
#         })

#     @http.route('/netimpex_odoo_sync/netimpex_odoo_sync/objects/<model("netimpex_odoo_sync.netimpex_odoo_sync"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('netimpex_odoo_sync.object', {
#             'object': obj
#         })