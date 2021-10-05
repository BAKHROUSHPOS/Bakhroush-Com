# -*- coding: utf-8 -*-
from odoo import models, fields,api
from datetime import datetime


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    total_orders = fields.Float(string="Total Ordered",store=True, readonly=True, compute='_compute_qty',)
    total_delivered = fields.Float(string="Total Delivered" ,store=True, readonly=True, compute='_compute_qty')
    partner_credit = fields.Monetary(string="Credit", related='partner_id.credit')
    partner_debit = fields.Monetary(string="Debit", related='partner_id.debit')
    company_currency_id = fields.Many2one('res.currency', related="company_id.currency_id")
    partner_balance = fields.Monetary(string="In Company Currency", currency_field='company_currency_id',
                                      compute='_get_partner_balance')
    balance_in_partner_currency = fields.Monetary(
        "In Customer Currency", currency_field='currency_id', compute='_get_balance_in_partner_currency'
    )

    def _get_balance_in_partner_currency(self):
        for record in self:
            if record.pricelist_id:
                company = record.company_id or self.env.user.company_id
                rate = company.currency_id._get_conversion_rate(company.currency_id, record.pricelist_id.currency_id,
                                                                company, datetime.now().date())
                record.balance_in_partner_currency = rate * record.partner_balance

    def _get_partner_balance(self):
        for record in self:
            record.partner_balance = record.partner_credit
            # record.partner_balance = record.partner_debit - record.partner_credit

    @api.onchange('pricelist_id')
    def onchange_pricelist_id(self):
        self._get_partner_balance()
        self._get_balance_in_partner_currency()

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        super(SaleOrder, self).onchange_partner_id()
        self._get_partner_balance()
        self._get_balance_in_partner_currency()

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

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        mrp_production_ids = self.procurement_group_id.stock_move_ids.created_production_id.procurement_group_id.mrp_production_ids.ids
        if mrp_production_ids:
            for mrp in mrp_production_ids:
                self.env['mrp.production'].browse(mrp).write({'branch_id': self.branch_id.id})
        return res
