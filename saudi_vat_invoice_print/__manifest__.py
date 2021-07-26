# -*- coding: utf-8 -*-
{
    'name': 'Saudi Invoice Format',
    'version': '1.0',
    'depends': ['base','account'],
    'category': 'Accounting',
    'data': [
        'views/res_company.xml',
        'views/invoice.xml',
        'views/res_partner.xml',
        'reports/report_saudi_invoice.xml',
     ],
    'installable': True,
    'application': False,
}
