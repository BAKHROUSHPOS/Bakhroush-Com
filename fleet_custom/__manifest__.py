# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

{
    # Module Information
    'name': 'Fleet Custom',
    'category': 'Fleet Custom',
    'sequence': 1,
    'version': '14.0.1.0.0',
    'license': 'LGPL-3',
    'summary': """Fleet Custom""",
    'description': """Fleet Custom""",
    # Website
    'author': 'Aneesh.AV',
    # Dependencies
    'depends': ['fleet','account_asset'],
    # Data
    'data': [
        'security/ir.model.access.csv',
        'views/fleet_extended_view.xml',
        'views/fleet_config.xml',
         ],
    'installable': True,
    'application': True,
}
