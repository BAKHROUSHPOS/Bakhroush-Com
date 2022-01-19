# -*- coding: utf-8 -*-
from odoo import models, fields,api

class AccountMove(models.Model):
    _inherit = 'account.move'

    picking_id = fields.Many2one('stock.picking','Picking')
    sale_id = fields.Many2one('sale.order', 'Sale Origin')

# class AccountMove(models.Model):
#     _inherit = 'account.move.line'
#
#     branch_id = fields.Many2one(related='move_id.branch_id', readonly=False)
#
#     @api.depends('move_id')
#     def get_branch_id(self):
#         for line in self:
#             line.branch_id = line.move_id.branch_id.id