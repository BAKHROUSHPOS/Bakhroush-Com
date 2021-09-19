# -*- coding: utf-8 -*-

from odoo import fields, models , api, _

class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    code = fields.Char('Short Name', required=True, size=250, help="Short name used to identify your warehouse")
    allowed_users = fields.Many2many('res.users', string='Allowed Users')

class StockPicking(models.Model):
    _inherit = 'stock.picking'

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
    driver_name = fields.Many2one(
        'hr.employee',
        string='Driver'
    )
    method = fields.Selection(
        [('normal', 'Normal'), ('concrete', 'Concrete')],
        string="Method",
        required=True,
        default='concrete'
    )
    source_warehouse = fields.Many2one(
        'stock.warehouse',
        string='Source Warehouse',
        domain=lambda self: self.get_source()
    )
    destination_warehouse = fields.Many2one(
        'stock.warehouse',
        string='Destination Warehouse',
    )
    addition_approval = fields.Boolean(
        compute='_compute_additional_approve',
        string='Additional Warehouse',
    )
    dummy_src_location = fields.Many2one('stock.location','Dummy source location')
    allowed_users = fields.Many2many('res.users',string='Allowed Users')

    balance_amount = fields.Float(string='Customer Balance',compute='_get_balance_in_partner')
    picking_total_value = fields.Float(string='Total Value',compute='_get_balance_in_partner')

    def _get_balance_in_partner(self):
        for record in self:
            record.balance_amount = record.sale_id.partner_balance
            amount = 0
            for line in record.move_line_ids_without_package:
                amount += (line.move_id.sale_line_id.price_unit * line.qty_done)
            record.picking_total_value = record.balance_amount

    @api.depends('state', 'show_validate')
    def _compute_show_validate(self):
        for picking in self:
            if not (picking.immediate_transfer) and picking.state == 'draft':
                picking.show_validate = False
            elif picking.state not in ('draft', 'waiting', 'confirmed', 'assigned'):
                picking.show_validate = False
            else:
                picking.show_validate = True
            if picking.addition_approval == True:
                picking.show_validate = False

    @api.depends('destination_warehouse', 'source_warehouse', 'location_dest_id','location_id')
    def _compute_additional_approve(self):
        for pick in self:
            branches = [ p.id for p in self.env.user.branch_ids ]
            if pick.destination_warehouse and pick.location_dest_id.branch_id.id not in [ p.id for p in self.env.user.branch_ids ]:
                pick.addition_approval = True
            else:
                pick.addition_approval = False
            users = False
            if pick.location_id.branch_id and pick.location_dest_id.branch_id:
                users = self.env['res.users'].search(
                    [('branch_ids', 'in', (pick.location_id.branch_id.id, pick.location_dest_id.branch_id.id))])
            elif pick.location_id.branch_id and not pick.location_dest_id.branch_id:
                users = self.env['res.users'].search(
                    [('branch_ids', 'in', pick.location_id.branch_id.id)])
            elif not pick.location_id.branch_id and pick.location_dest_id.branch_id:
                users = self.env['res.users'].search(
                    [('branch_ids', 'in', pick.location_dest_id.branch_id.id)])
            if users:
                pick.allowed_users = users.ids

    @api.onchange('picking_type_id')
    def _onchange_picking_type_id(self):
        if self.picking_type_id:
            self.dummy_src_location = self.picking_type_id.default_location_src_id.id
            self.source_warehouse = self.picking_type_id.warehouse_id.id
        return {'domain': {
            'picking_type_id': [('warehouse_id.allowed_users', 'in', self.env.user.id)]
        }}

    @api.model
    def get_source(self):
        res = [('id', '=', self.picking_type_id.warehouse_id.id)]
        return res

    @api.onchange('destination_warehouse')
    def _onchange_destination_warehouse(self):
        if self.destination_warehouse:
            self.location_dest_id = self.destination_warehouse.lot_stock_id.id
            return {'domain': {
                'location_id': [('branch_id', '=', self.source_warehouse.branch_id.id)]}}


    @api.onchange('car_no')
    def _onchange_car_no(self):
        if self.car_no:
            self.driver_name = self.car_no.employee_driver.id

    @api.onchange('partner_id')
    def _onchange_partner_id_other(self):
        if self.partner_id:
            self.building_permit_no = self.partner_id.street
            self.customer_no = self.partner_id.customer_no
            self.location = self.partner_id.location
            self.mobile_no = self.partner_id.mobile

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
