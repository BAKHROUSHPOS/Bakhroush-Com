# -*- coding: utf-8 -*-

from odoo import fields, models , api, _

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    # invoice_no = fields.Many2one(
    #     'account.move',
    #     'Invoice No.'
    # )
    invoice_no = fields.Char(
        'Invoice No.'
    )
    building_permit_no = fields.Char(
        'Address / Building Permit No.',
    )
    type_of_use = fields.Char(
        'Type of Use'
    )
    customer_no = fields.Char(
        'Customer No.'
    )
    mobile_no = fields.Char(
        'Mobile No.'
    )
    location = fields.Char(
        'Location.'
    )
    time_out = fields.Char(
        'Time Out'
    )
    mixing_time = fields.Char(
        'Mixing Time'
    )
    load_time_mixer = fields.Char(
        'Load time mixer'
    )
    received_time = fields.Char(
        'Arrival / Received Time'
    )
    corresponding = fields.Char(
        'Corresponding'
    )
    car_no = fields.Many2one(
        'fleet.vehicle',
        'Car No.'
    )
    driver_name = fields.Char(
        'Driver Name'
    )
    method= fields.Selection(
        [('normal', 'Normal'), ('concrete', 'Concrete')],
        string="Method",
        required=True,
    )

    @api.onchange('car_no')
    def _onchange_car_no(self):
        if self.car_no:
            self.driver_name = self.car_no.employee_driver.name

class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    barcode = fields.Char(
        string='Barcode'
    )
    opc = fields.Boolean(
        string='OPC'
    )
    src = fields.Boolean(
        string='SRC'
    )
    quantity_of_cement = fields.Float(
        'Quantity of Cement / m3'
    )
    clas = fields.Char(
        'Class'
    )
    total_loading = fields.Char(
        'Total Loading'
    )
    slump = fields.Char(
        'Slump'
    )
    temperature = fields.Char(
        'Temperature'
    )
    weight = fields.Char(
        'Weight'
    )
    pump = fields.Char(
        'Pump'
    )
    wc = fields.Char(
        'W/C'
    )
    method = fields.Selection(
        related='picking_id.method',
        store=True
    )

    @api.onchange('barcode')
    def _onchange_barcode(self):
        if self.barcode:
            product = self.env['product.product'].search([('barcode', '=', self.barcode)])
            self.product_id = product.id
