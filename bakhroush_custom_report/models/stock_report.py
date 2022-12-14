# -*- coding: utf-8 -*-

from odoo import tools
from odoo import api, fields, models, _
from odoo.exceptions import UserError

class StockReport(models.Model):
    _inherit = 'stock.report'

    driver_name = fields.Many2one('hr.employee', string='Driver', store=True)

    def _select(self):
        select_str = super(StockReport, self)._select()
        select_str += """,sp.driver_name as driver_name"""
        return select_str
    def _from(self):
        from_str = """
            stock_move sm
            LEFT JOIN (
                SELECT
                    id,
                    name,
                    date_done,
                    date as creation_date,
                    scheduled_date,
                    partner_id,
                    driver_name,
                    backorder_id IS NOT NULL as is_backorder,
                    extract(epoch from avg(date_trunc('day',date_done)-date_trunc('day',scheduled_date)))/(24*60*60)::decimal(16,2) as delay,
                    extract(epoch from avg(date_trunc('day',date_done)-date_trunc('day',date)))/(24*60*60)::decimal(16,2) as cycle_time
                FROM
                    stock_picking
                GROUP BY
                    id,
                    name,
                    date_done,
                    date,
                    scheduled_date,
                    partner_id,
                    is_backorder
            ) sp ON sm.picking_id = sp.id
            LEFT JOIN stock_picking_type spt ON sm.picking_type_id = spt.id
            INNER JOIN product_product p ON sm.product_id = p.id
            INNER JOIN product_template t ON p.product_tmpl_id = t.id
            INNER JOIN product_category cat ON t.categ_id = cat.id
            WHERE t.type = 'product'
        """

        return from_str

    def _group_by(self):
        group_by_str = super(StockReport, self)._group_by()
        group_by_str += """,sp.driver_name"""
        return group_by_str

class DeliverySlipReport(models.Model):
    _name = "report.bakhroush_custom_report.slip_dot_bakhroush"
    _description = "Delivery Slip"

    @api.model
    def _get_report_values(self, docids, data=None):
        note_ids = self.env['stock.picking'].browse(docids)
        for note_id in note_ids:
            if note_id.state != 'done':
                raise UserError(_("يجب عليك تأكيد الشحنة حتى يمكنك طباعتها"))
        return {
            'docs': note_ids,
        }

class DeliverySlipConcreteReport(models.Model):
    _name = "report.bakhroush_custom_report.slip_concrete_bakhroush"
    _description = "Delivery Slip Concrete"

    @api.model
    def _get_report_values(self, docids, data=None):
        note_ids = self.env['stock.picking'].browse(docids)
        for note_id in note_ids:
            if note_id.state != 'done':
                raise UserError(_("يجب عليك تأكيد الشحنة حتى يمكنك طباعتها"))
        return {
            'docs': note_ids,
        }