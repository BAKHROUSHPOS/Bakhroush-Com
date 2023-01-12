{
    'name': "AZK General Ledger Summary Report",
    'summary': """
        Printing General Ledger Summary Report""",
    'description': """
        Ability to Print new PDF report from General Ledger Audit report, this new report
        is summarized i.e. having only Amounts values without any extra columns.
    """,
    'author': "Azkatech",
    'website': "https://azka.tech",
    'category': 'Acconting Reports',
    'version': '14.0.0.0.0',
    "license": "AGPL-3",
    "support": "support+odoo@azka.tech",
    'depends': ['account_reports'],
    'data': [
        'reports/general_ledger_summary_report.xml',
    ],  
}
