# -*- coding: utf-8 -*-

from odoo import fields, models , api, _
from odoo.exceptions import ValidationError

class PaymentTerms(models.Model):
    _inherit = 'account.payment.term'

    allowed_users = fields.Many2many('res.users', string='Allowed Users')
    force_invoice = fields.Boolean('Create auto Invoice & Payment')
    default_cash_payment = fields.Many2one('account.journal', 'Payment Journal')
