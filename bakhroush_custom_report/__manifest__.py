# -*- coding: utf-8 -*-

{
    # Module Information
    'name': 'Bakhroush Custom - Report',
    'category': 'Fleet Custom',
    'sequence': 1,
    'version': '14.0.1.0.0',
    'license': 'LGPL-3',
    'summary': """Bakhroush Custom - Report""",
    'description': """Bakhroush Custom - Report""",
    # Website
    'author': 'Aneesh.AV',
    # Dependencies
    'depends': ['base','product','stock','saudi_vat_invoice_print','sale','mrp','aspl_company_branch_ee','purchase','contacts', 'hr'],
    # Data
    'data': [
        'views/data.xml',
        'security/ir.model.access.csv',
        'report/delivery_report.xml',
        'report/delivery_dotmatrix_report.xml',
        'report/delivery_concreate_dotmatrix_report.xml',
        'views/stock_picking_view.xml',
        'views/sale_view.xml',
        'views/purchase_view.xml',
        'views/mrp.xml',
        'views/res_partner_view.xml',
        'views/product_view.xml',
        'views/payment_terms.xml',
        'views/branch.xml',
        'wizards/credit_limit_wizard.xml',
        ],
    'installable': True,
    'application': True,
}
