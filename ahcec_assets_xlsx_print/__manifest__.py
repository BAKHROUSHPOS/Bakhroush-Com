{
    'name': 'Fixed Assets Register Report',
    'category': 'Assets',
    'license': "AGPL-3",
    'summary': "Give The assets report in excel",
    'author': 'Aneesh.AV',
    'depends': [
                'base',
                'account',
                'account_asset',
                ],
    'data': [
            'security/ir.model.access.csv',
            'wizard/report_menu.xml',
            ],
    'installable': True,
    'auto_install': False,
}
