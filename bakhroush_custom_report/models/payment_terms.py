# -*- coding: utf-8 -*-

from odoo import fields, models , api, _

class PaymentTerms(models.Model):
    _inherit = 'account.payment.term'

    allowed_users = fields.Many2many('res.users', string='Allowed Users')