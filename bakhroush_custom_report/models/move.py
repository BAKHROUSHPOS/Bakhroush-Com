# -*- coding: utf-8 -*-
from odoo import models, fields,api

class AccountMove(models.Model):
    _inherit = 'account.move'

    picking_id = fields.Many2one('stock.picking','Picking')
    sale_id = fields.Many2one('sale.order', 'Sale Origin')