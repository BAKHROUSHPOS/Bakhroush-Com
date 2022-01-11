# -*- coding: utf-8 -*-
{
    'name': 'Global Discount',
    'category': 'Product',
    'sequence': 5,
    'version': '14.0.1.0',
    'license': 'LGPL-3',
    'summary': """Global discount in Sales, Purchase and Invoice.""",
    'description': """Module allows to give global discount in sales, purchase and invoice.""",
    'author': 'Acespritech Solutions Pvt. Ltd.',
    'depends': ['base', 'sale', 'sale_management', 'sale_purchase', 'purchase', 'product', 'account'],
    'data': [
        'views/res_config_settings_view.xml',
        'views/sale_view.xml',
        'views/purchase_view.xml',
        'views/invoice_view.xml',
        'report/sale_report_views.xml',
        'report/purchase_report_views.xml',
        'report/invoice_report_views.xml'
    ],
    'installable': True,
    'application': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

