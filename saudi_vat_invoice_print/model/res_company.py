# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class inherit_res_company(models.Model):
    _inherit= 'res.company'
    
    header_img = fields.Binary("Header Image")
    footer_img = fields.Binary("Footer Image")
    arabic = fields.Char('Arabic Name')
    arabic_vat = fields.Char('VAT Arabic')

class ResBank(models.Model):
    _inherit= 'res.bank'

    iban = fields.Char('IBAN')
    branch = fields.Char('Branch')