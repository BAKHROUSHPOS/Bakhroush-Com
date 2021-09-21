# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError, UserError
from odoo.tools import float_is_zero, float_compare
from datetime import datetime


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
    dummy_src_location = fields.Many2one('stock.location', 'Dummy source location')
    allowed_users = fields.Many2many('res.users', string='Allowed Users')

    balance_amount = fields.Float(string='Customer Balance', compute='_get_balance_in_partner')
    picking_total_value = fields.Float(string='Total Value', compute='_get_balance_in_partner')

    @api.depends('partner_id', 'move_line_ids_without_package')
    def _get_balance_in_partner(self):
        for record in self:
            record.balance_amount = record.sale_id.partner_balance
            amount = 0
            for line in record.move_line_ids_without_package:
                amount += (line.move_id.sale_line_id.price_unit * line.qty_done)
            record.picking_total_value = amount

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

    @api.depends('destination_warehouse', 'source_warehouse', 'location_dest_id', 'location_id')
    def _compute_additional_approve(self):
        for pick in self:
            branches = [p.id for p in self.env.user.branch_ids]
            if pick.destination_warehouse and pick.location_dest_id.branch_id.id not in [p.id for p in
                                                                                         self.env.user.branch_ids]:
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

    def _prepare_invoice_vals(self):
        self.ensure_one()
        vals = {
            'payment_reference': self.name,
            'invoice_origin': self.name,
            'picking_id': self.id,
            # 'journal_id': self.session_id.config_id.invoice_journal_id.id,
            'move_type': 'out_invoice',
            'ref': self.name,
            'partner_id': self.partner_id.id,
            'narration': self.note or '',
            'currency_id': self.sale_id.pricelist_id.currency_id.id,
            'invoice_user_id': self.env.user.id,
            'invoice_date': datetime.today(),
            'fiscal_position_id': self.sale_id.fiscal_position_id.id,
            'invoice_line_ids': [(0, None, self._prepare_invoice_line(line)) for line in self.move_ids_without_package],
            'attention': self.partner_id.id,
            'approved_by': self.env.user.id
        }
        return vals

    def _prepare_invoice_line(self, pick_line):
        return {
            'product_id': pick_line.product_id.id,
            'quantity': pick_line.quantity_done,
            'discount': pick_line.sale_line_id.discount,
            'price_unit': pick_line.sale_line_id.price_unit,
            'name': pick_line.product_id.display_name,
            'tax_ids': [(6, 0, pick_line.sale_line_id.tax_id.ids)],
            'product_uom_id': pick_line.product_id.uom_id.id,
        }

    def create_payment(self,invoice):
        journal = self.sale_id.payment_term_id.default_cash_payment
        payment = self.env['account.payment'].create({
            'payment_method_id': self.env.ref('account.account_payment_method_manual_in').id or False,
            'payment_type': 'inbound',
            'partner_id':self.partner_id.commercial_partner_id.id,
            'partner_type': 'customer',
            'journal_id': journal.id,
            'date': datetime.today(),
            'currency_id': invoice.currency_id.id ,
            'amount': abs(invoice.amount_total),
            'ref': self.name,
        })
        return payment

    def force_create_invoice_payment(self):
        account_inv_obj = self.env['account.move']
        account_move_line = self.env['account.move.line']

        move_vals = self._prepare_invoice_vals()
        print(move_vals)
        new_move = account_inv_obj.sudo().create(move_vals)
        message = _(
            "This invoice has been created from the Delivery note: <a href=# data-oe-model=stock.picking data-oe-id=%d>%s</a>") % (
                      self.id, self.name)
        new_move.message_post(body=message)
        new_move.action_post()
        return new_move



    def button_validate_custom(self):
        for picking in self:
            if picking.sale_id:

                precision_digits = self.env['decimal.precision'].precision_get('Product Unit of Measure')
                no_quantities_done = all(
                    float_is_zero(move_line.qty_done, precision_digits=precision_digits) for move_line in
                    picking.move_line_ids.filtered(lambda m: m.state not in ('done', 'cancel')))
                # no_reserved_quantities = all(
                #     float_is_zero(move_line.product_qty, precision_rounding=move_line.product_uom_id.rounding) for
                #     move_line in picking.move_line_ids)
                if no_quantities_done:
                    raise ValidationError(
                        _("No Quantity is added"))
                else:
                    if picking.sale_id.payment_term_id.force_invoice:
                        pick = picking.button_validate()
                        if pick:
                            invoice = picking.force_create_invoice_payment()
                            payment = self.create_payment(invoice)
                            payment.action_post()
                            invoice.write({'payment_id': payment.id})
                    else:
                        if self.picking_total_value >= abs(self.balance_amount):
                            picking.button_validate()
                            picking.force_create_invoice_payment()
                        else:
                            if self.env.user.has_group('account.group_account_manager'):
                                picking.button_validate()
                                picking.force_create_invoice_payment()
                            else:
                                raise ValidationError(
                                    _("Customer is having credit, Only Accounts Department can approve the delivery"))
            else:
                picking.button_validate()


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
