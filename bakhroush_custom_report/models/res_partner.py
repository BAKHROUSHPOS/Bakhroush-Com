# -*- coding: utf-8 -*-

from odoo import fields, models , api, _

class ResPartner(models.Model):
    _name = 'res.partner'
    _inherit = 'res.partner'

    is_employee = fields.Boolean('Is an Employee')