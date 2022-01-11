# -*- coding: utf-8 -*-
from odoo import models, fields,api

class ManufacturingOrder(models.Model):
    _inherit = 'mrp.production'

    @api.onchange('product_id', 'move_raw_ids', 'branch_id')
    def _onchange_for_picking_type_id(self):
        if self.branch_id:
            self.picking_type_id = self.env['stock.warehouse'].search([('branch_id', '=', self.branch_id.id)],
                                                                      limit=1).manu_type_id.id