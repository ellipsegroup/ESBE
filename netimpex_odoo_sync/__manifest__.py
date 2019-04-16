# -*- coding: utf-8 -*-
{
    'name': "netimpex_odoo_sync",

    'summary': """Module for fetching data from netimplex and store into database.
       """,

    'description': """
        Coded things to fetch data from netimplex using netimplex API and then store data into odoo instance database.
    """,

    'author': "CIS",
    'website': "http://www.cisin.com",

    'category': 'Uncategorized',
    'version': '0.1',

    'depends': ['product','sale'],

    'data': [
        'security/ir.model.access.csv',
        'data/data.xml',
        'views/views.xml',
        'views/templates.xml',
    ],
}