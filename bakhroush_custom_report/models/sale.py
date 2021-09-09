# -*- coding: utf-8 -*-
from odoo import models, fields,api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    total_orders = fields.Float(string="Total Ordered",store=True, readonly=True, compute='_compute_qty',)
    total_delivered = fields.Float(string="Total Delivered" ,store=True, readonly=True, compute='_compute_qty')

    @api.onchange('partner_id','order_line','branch_id')
    def _onchange_for_warehouse(self):
        if self.branch_id:
            self.warehouse_id = self.env['stock.warehouse'].search([('branch_id','=',self.branch_id.id)],limit=1).id


    @api.depends('order_line','order_line.product_uom_qty','order_line.qty_delivered')
    def _compute_qty(self):
        for order in self:
            product_uom_qty = qty_delivered = 0.0
            for line in order.order_line:
                product_uom_qty += line.product_uom_qty
                qty_delivered += line.qty_delivered
            order.update({
                'total_orders': product_uom_qty,
                'total_delivered': qty_delivered,
            })