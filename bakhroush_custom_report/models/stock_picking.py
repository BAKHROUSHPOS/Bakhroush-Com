# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError, UserError
from odoo.tools import float_is_zero, float_compare
from datetime import datetime
from odoo.tools.float_utils import float_round

class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    code = fields.Char('Short Name', required=True, size=250, help="Short name used to identify your warehouse")
    allowed_users = fields.Many2many('res.users', string='Allowed Users')

class StockBackorderConfirmation(models.TransientModel):
    _inherit = 'stock.backorder.confirmation'

    def _prepare_invoice_vals(self,picking):
        self.ensure_one()
        vals = {
            'payment_reference': picking.name,
            'invoice_origin': picking.name,
            'picking_id': picking.id,
            # 'journal_id': self.session_id.config_id.invoice_journal_id.id,
            'move_type': 'out_invoice',
            'ref': picking.name,
            'partner_id': picking.partner_id.id,
            'narration': picking.note or '',
            'currency_id': picking.sale_id.pricelist_id.currency_id.id,
            'invoice_user_id': picking.env.user.id,
            'invoice_date': datetime.today(),
            'fiscal_position_id': picking.sale_id.fiscal_position_id.id,
            'invoice_line_ids': [(0, None, self._prepare_invoice_line(line)) for line in picking.move_ids_without_package],
            'invoice_payment_term_id':picking.sale_id.payment_term_id.id,
            # 'attention': self.partner_id.id,
            # 'approved_by': self.env.user.id
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
            'sale_line_ids':[(6, 0, pick_line.sale_line_id.ids)],
            'product_uom_id': pick_line.product_id.uom_id.id,
        }

    def create_payment(self,invoice,picking):
        journal = picking.sale_id.payment_term_id.default_cash_payment
        payment = self.env['account.payment'].sudo().create({
            'payment_method_id': self.env.ref('account.account_payment_method_manual_in').id or False,
            'payment_type': 'inbound',
            'partner_id':picking.partner_id.commercial_partner_id.id,
            'partner_type': 'customer',
            'journal_id': journal.id,
            'date': datetime.today(),
            'currency_id': invoice.currency_id.id ,
            'amount': abs(invoice.amount_total),
            'ref': picking.name,
        })
        return payment

    def force_create_invoice_payment(self,picking):
        account_inv_obj = self.env['account.move']
        account_move_line = self.env['account.move.line']

        move_vals = self._prepare_invoice_vals(picking)
        new_move = account_inv_obj.sudo().create(move_vals)
        message = _(
            "This invoice has been created from the Delivery note: <a href=# data-oe-model=stock.picking data-oe-id=%d>%s</a>") % (
                      picking.id, picking.name)
        new_move.message_post(body=message)
        new_move.sudo().action_post()
        return new_move

    def process(self):
        pickings_to_do = self.env['stock.picking']
        pickings_not_to_do = self.env['stock.picking']
        for line in self.backorder_confirmation_line_ids:
            if line.to_backorder is True:
                pickings_to_do |= line.picking_id
            else:
                pickings_not_to_do |= line.picking_id

        for pick_id in pickings_not_to_do:
            moves_to_log = {}
            for move in pick_id.move_lines:
                if float_compare(move.product_uom_qty,
                                 move.quantity_done,
                                 precision_rounding=move.product_uom.rounding) > 0:
                    moves_to_log[move] = (move.quantity_done, move.product_uom_qty)
            pick_id._log_less_quantities_than_expected(moves_to_log)

        pickings_to_validate = self.env.context.get('button_validate_picking_ids')
        if pickings_to_validate:
            for picking in self.env['stock.picking'].browse(pickings_to_validate).with_context(skip_backorder=True):
                if picking.sale_id.payment_term_id.force_invoice:
                    invoice = self.force_create_invoice_payment(picking)
                    picking.sudo().write({'invoice_id': invoice.id})
                    payment = self.create_payment(invoice,picking)
                    payment.sudo().action_post()
                    (invoice + payment.move_id).line_ids \
                        .filtered(lambda line: line.account_internal_type == 'receivable') \
                        .reconcile()
                    invoice.sudo().write({'payment_id': payment.id})

            pickings_to_validate = self.env['stock.picking'].browse(pickings_to_validate).with_context(skip_backorder=True)
            if pickings_not_to_do:
                pickings_to_validate = pickings_to_validate.with_context(picking_ids_not_to_backorder=pickings_not_to_do.ids)

            return pickings_to_validate.button_validate()
        return True

class StockImmediateTransfer(models.TransientModel):
    _inherit = 'stock.immediate.transfer'


    def _prepare_invoice_vals(self,picking):
        self.ensure_one()
        vals = {
            'payment_reference': picking.name,
            'invoice_origin': picking.name,
            'picking_id': picking.id,
            # 'journal_id': self.session_id.config_id.invoice_journal_id.id,
            'move_type': 'out_invoice',
            'ref': picking.name,
            'partner_id': picking.partner_id.id,
            'narration': picking.note or '',
            'currency_id': picking.sale_id.pricelist_id.currency_id.id,
            'invoice_user_id': picking.env.user.id,
            'invoice_date': datetime.today(),
            'fiscal_position_id': picking.sale_id.fiscal_position_id.id,
            'invoice_line_ids': [(0, None, self._prepare_invoice_line(line)) for line in picking.move_ids_without_package],
            'invoice_payment_term_id':picking.sale_id.payment_term_id.id,
            # 'attention': self.partner_id.id,
            # 'approved_by': self.env.user.id
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
            'sale_line_ids':[(6, 0, pick_line.sale_line_id.ids)],
            'product_uom_id': pick_line.product_id.uom_id.id,
        }

    def create_payment(self,invoice,picking):
        journal = picking.sale_id.payment_term_id.default_cash_payment
        payment = self.env['account.payment'].sudo().create({
            'payment_method_id': self.env.ref('account.account_payment_method_manual_in').id or False,
            'payment_type': 'inbound',
            'partner_id':picking.partner_id.commercial_partner_id.id,
            'partner_type': 'customer',
            'journal_id': journal.id,
            'date': datetime.today(),
            'currency_id': invoice.currency_id.id ,
            'amount': abs(invoice.amount_total),
            'ref': picking.name,
        })
        return payment

    def force_create_invoice_payment(self,picking):
        account_inv_obj = self.env['account.move']
        account_move_line = self.env['account.move.line']

        move_vals = self._prepare_invoice_vals(picking)
        new_move = account_inv_obj.sudo().create(move_vals)
        message = _(
            "This invoice has been created from the Delivery note: <a href=# data-oe-model=stock.picking data-oe-id=%d>%s</a>") % (
                      picking.id, picking.name)
        new_move.message_post(body=message)
        new_move.sudo().action_post()
        return new_move

    def process(self):
        pickings_to_do = self.env['stock.picking']
        pickings_not_to_do = self.env['stock.picking']
        for line in self.immediate_transfer_line_ids:
            if line.to_immediate is True:
                pickings_to_do |= line.picking_id
            else:
                pickings_not_to_do |= line.picking_id
        for picking in pickings_to_do:
            # If still in draft => confirm and assign
            if picking.state == 'draft':
                picking.action_confirm()
                if picking.state != 'assigned':
                    picking.action_assign()
                    if picking.state != 'assigned':
                        raise UserError(
                            _("Could not reserve all requested products. Please use the \'Mark as Todo\' button to handle the reservation manually."))
            for move in picking.move_lines.filtered(lambda m: m.state not in ['done', 'cancel']):
                for move_line in move.move_line_ids:
                    move_line.qty_done = move_line.product_uom_qty
            if picking.sale_id.payment_term_id.force_invoice:
                invoice = self.force_create_invoice_payment(picking)
                picking.sudo().write({'invoice_id':invoice.id})
                payment = self.create_payment(invoice,picking)
                payment.sudo().action_post()
                (invoice + payment.move_id).line_ids \
                    .filtered(lambda line: line.account_internal_type == 'receivable') \
                    .reconcile()
                invoice.sudo().write({'payment_id': payment.id})


        pickings_to_validate = self.env.context.get('button_validate_picking_ids')
        if pickings_to_validate:
            pickings_to_validate = self.env['stock.picking'].browse(pickings_to_validate)
            pickings_to_validate = pickings_to_validate - pickings_not_to_do
            return pickings_to_validate.with_context(skip_immediate=True).button_validate()
        return True


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
        string='Driver Name',
        domain=lambda self: self.get_employee()
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
    invoice_id = fields.Many2one('account.move','Invoice',readonly=True)

    @api.depends('partner_id', 'move_line_ids_without_package')
    def _get_balance_in_partner(self):
        for record in self:
            record.balance_amount = record.sale_id.partner_balance
            amount = 0
            for line in record.move_line_ids_without_package:
                if line.qty_done > 0:
                    price = line.move_id.sale_line_id.price_unit * (
                            1 - (line.move_id.sale_line_id.discount or 0.0) / 100.0)
                    taxes = line.move_id.sale_line_id.tax_id.compute_all(
                        price,
                        line.move_id.sale_line_id.order_id.currency_id,
                        line.qty_done,
                        product=line.move_id.sale_line_id.product_id,
                        partner=line.move_id.sale_line_id.order_id.partner_shipping_id)
                    amount += taxes['total_included']
                else:
                    price = line.move_id.sale_line_id.price_unit * (
                                1 - (line.move_id.sale_line_id.discount or 0.0) / 100.0)
                    taxes = line.move_id.sale_line_id.tax_id.compute_all(
                                    price,
                                    line.move_id.sale_line_id.order_id.currency_id,
                                    line.move_id.sale_line_id.product_uom_qty,
                                    product=line.move_id.sale_line_id.product_id,
                                    partner=line.move_id.sale_line_id.order_id.partner_shipping_id)
                    # line.update({
                    #     'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                    #     'price_total': taxes['total_included'],
                    #     'price_subtotal': taxes['total_excluded'],
                    # })
                    amount += taxes['total_included']
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
    def get_employee(self):
        driver = self.env['fleet.vehicle'].search([('employee_driver', '!=', False)]).employee_driver.ids
        res = [('id', 'in', driver)]
        return res

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



    def _pre_action_done_hook(self):
        print(self.sale_id.payment_term_id.force_invoice)
        print(self.env.context)
        if not self.sale_id.payment_term_id.force_invoice and self.picking_total_value > self.balance_amount and not self.env.user.has_group('account.group_account_manager'):
            raise ValidationError(
                        _("No enough credit to for the customer, Contact Finance dep. \n\n"
                          "لا يوجد رصيد لدي العميل، يرجي مراجعة الأدارة المالية"))
        else:
            if not self.env.context.get('skip_immediate'):
                pickings_to_immediate = self._check_immediate()
                if pickings_to_immediate:
                    return pickings_to_immediate._action_generate_immediate_wizard(
                        show_transfers=self._should_show_transfers())

            if not self.env.context.get('skip_backorder'):
                pickings_to_backorder = self._check_backorder()
                if pickings_to_backorder:
                    return pickings_to_backorder._action_generate_backorder_wizard(
                        show_transfers=self._should_show_transfers())
            return True

    def button_validate(self):
        # Clean-up the context key at validation to avoid forcing the creation of immediate
        # transfers.
        if not self.driver_name and self.picking_type_id.code == 'outgoing':
            raise UserError(_('Please select the driver name.'))
        ctx = dict(self.env.context)
        ctx.pop('default_immediate_transfer', None)
        self = self.with_context(ctx)

        # Sanity checks.
        pickings_without_moves = self.browse()
        pickings_without_quantities = self.browse()
        pickings_without_lots = self.browse()
        products_without_lots = self.env['product.product']
        for picking in self:
            if not picking.move_lines and not picking.move_line_ids:
                pickings_without_moves |= picking

            picking.message_subscribe([self.env.user.partner_id.id])
            picking_type = picking.picking_type_id
            precision_digits = self.env['decimal.precision'].precision_get('Product Unit of Measure')
            no_quantities_done = all(float_is_zero(move_line.qty_done, precision_digits=precision_digits) for move_line in picking.move_line_ids.filtered(lambda m: m.state not in ('done', 'cancel')))
            no_reserved_quantities = all(float_is_zero(move_line.product_qty, precision_rounding=move_line.product_uom_id.rounding) for move_line in picking.move_line_ids)
            if no_reserved_quantities and no_quantities_done:
                pickings_without_quantities |= picking

            if picking_type.use_create_lots or picking_type.use_existing_lots:
                lines_to_check = picking.move_line_ids
                if not no_quantities_done:
                    lines_to_check = lines_to_check.filtered(lambda line: float_compare(line.qty_done, 0, precision_rounding=line.product_uom_id.rounding))
                for line in lines_to_check:
                    product = line.product_id
                    if product and product.tracking != 'none':
                        if not line.lot_name and not line.lot_id:
                            pickings_without_lots |= picking
                            products_without_lots |= product

        if not self._should_show_transfers():
            if pickings_without_moves:
                raise UserError(_('Please add some items to move.'))
            if pickings_without_quantities:
                raise UserError(self._get_without_quantities_error_message())
            if pickings_without_lots:
                raise UserError(_('You need to supply a Lot/Serial number for products %s.') % ', '.join(products_without_lots.mapped('display_name')))
        else:
            message = ""
            if pickings_without_moves:
                message += _('Transfers %s: Please add some items to move.') % ', '.join(pickings_without_moves.mapped('name'))
            if pickings_without_quantities:
                message += _('\n\nTransfers %s: You cannot validate these transfers if no quantities are reserved nor done. To force these transfers, switch in edit more and encode the done quantities.') % ', '.join(pickings_without_quantities.mapped('name'))
            if pickings_without_lots:
                message += _('\n\nTransfers %s: You need to supply a Lot/Serial number for products %s.') % (', '.join(pickings_without_lots.mapped('name')), ', '.join(products_without_lots.mapped('display_name')))
            if message:
                raise UserError(message.lstrip())

        # Run the pre-validation wizards. Processing a pre-validation wizard should work on the
        # moves and/or the context and never call `_action_done`.
        if not self.env.context.get('button_validate_picking_ids'):
            self = self.with_context(button_validate_picking_ids=self.ids)
        res = self._pre_action_done_hook()
        if res is not True:
            return res

        # Call `_action_done`.
        if self.env.context.get('picking_ids_not_to_backorder'):
            pickings_not_to_backorder = self.browse(self.env.context['picking_ids_not_to_backorder'])
            pickings_to_backorder = self - pickings_not_to_backorder
        else:
            pickings_not_to_backorder = self.env['stock.picking']
            pickings_to_backorder = self

        if not self.invoice_id:
            if not self.sale_id.payment_term_id.force_invoice and self.picking_total_value > self.balance_amount and not self.env.user.has_group(
                    'account.group_account_manager'):
                raise ValidationError(
                    _("No enough credit to for the customer, Contact Finance dep. \n\n"
                      "لا يوجد رصيد لدي العميل، يرجي مراجعة الأدارة المالية"))
            else:
                if self.sale_id.payment_term_id.force_invoice:
                    if pickings_not_to_backorder:
                        picking = pickings_not_to_backorder
                    if pickings_to_backorder:
                        picking = pickings_to_backorder

                    invoice = self.force_create_invoice_payment(picking)
                    picking.sudo().write({'invoice_id': invoice.id})
                    payment = self.create_payment(invoice, picking)
                    payment.sudo().action_post()
                    (invoice + payment.move_id).line_ids \
                        .filtered(lambda line: line.account_internal_type == 'receivable') \
                        .reconcile()
                    invoice.sudo().write({'payment_id': payment.id})

        pickings_not_to_backorder.with_context(cancel_backorder=True)._action_done()
        pickings_to_backorder.with_context(cancel_backorder=False)._action_done()

        for picking_ids in self.sale_id.picking_ids:
            if picking_ids.state not in 'done':
                picking_ids.invoice_id = False

        return True

    def _prepare_invoice_vals(self,picking):
        self.ensure_one()
        vals = {
            'payment_reference': picking.name,
            'invoice_origin': picking.name,
            'picking_id': picking.id,
            # 'journal_id': self.session_id.config_id.invoice_journal_id.id,
            'move_type': 'out_invoice',
            'ref': picking.name,
            'partner_id': picking.partner_id.id,
            'narration': picking.note or '',
            'currency_id': picking.sale_id.pricelist_id.currency_id.id,
            'invoice_user_id': picking.env.user.id,
            'invoice_date': datetime.today(),
            'fiscal_position_id': picking.sale_id.fiscal_position_id.id,
            'invoice_line_ids': [(0, None, self._prepare_invoice_line(line)) for line in picking.move_ids_without_package],
            'invoice_payment_term_id':picking.sale_id.payment_term_id.id,
            # 'attention': self.partner_id.id,
            # 'approved_by': self.env.user.id
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
            'sale_line_ids':[(6, 0, pick_line.sale_line_id.ids)],
            'product_uom_id': pick_line.product_id.uom_id.id,
        }

    def create_payment(self,invoice,picking):
        journal = picking.sale_id.payment_term_id.default_cash_payment
        payment = self.env['account.payment'].sudo().create({
            'payment_method_id': self.env.ref('account.account_payment_method_manual_in').id or False,
            'payment_type': 'inbound',
            'partner_id':picking.partner_id.commercial_partner_id.id,
            'partner_type': 'customer',
            'journal_id': journal.id,
            'date': datetime.today(),
            'currency_id': invoice.currency_id.id ,
            'amount': abs(invoice.amount_total),
            'ref': picking.name,
        })
        return payment

    def force_create_invoice_payment(self,picking):
        account_inv_obj = self.env['account.move']
        account_move_line = self.env['account.move.line']

        move_vals = self._prepare_invoice_vals(picking)
        new_move = account_inv_obj.sudo().create(move_vals)
        message = _(
            "This invoice has been created from the Delivery note: <a href=# data-oe-model=stock.picking data-oe-id=%d>%s</a>") % (
                      picking.id, picking.name)
        new_move.message_post(body=message)
        new_move.sudo().action_post()
        return new_move

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

# class StockMove(models.Model):
#     _inherit = 'stock.move'
#
#     def _prepare_move_line_vals(self, quantity=None, reserved_quant=None):
#         self.ensure_one()
#         # apply putaway
#         location_dest_id = self.location_dest_id._get_putaway_strategy(self.product_id).id or self.location_dest_id.id
#         vals = {
#             'move_id': self.id,
#             'product_id': self.product_id.id,
#             'product_uom_id': self.product_uom.id,
#             'location_id': self.location_id.id,
#             'location_dest_id': location_dest_id,
#             'picking_id': self.picking_id.id,
#             'company_id': self.company_id.id,
#         }
#         if quantity:
#             rounding = self.env['decimal.precision'].precision_get('Product Unit of Measure')
#             uom_quantity = self.product_id.uom_id._compute_quantity(quantity, self.product_uom,
#                                                                     rounding_method='HALF-UP')
#             uom_quantity = float_round(uom_quantity, precision_digits=rounding)
#             uom_quantity_back_to_product_uom = self.product_uom._compute_quantity(uom_quantity, self.product_id.uom_id,
#                                                                                   rounding_method='HALF-UP')
#             if float_compare(quantity, uom_quantity_back_to_product_uom, precision_digits=rounding) == 0:
#                 vals = dict(vals, product_uom_qty=uom_quantity,qty_done=uom_quantity)
#             else:
#                 vals = dict(vals, product_uom_qty=quantity,qty_done=quantity, product_uom_id=self.product_id.uom_id.id)
#         if reserved_quant:
#             vals = dict(
#                 vals,
#                 location_id=reserved_quant.location_id.id,
#                 lot_id=reserved_quant.lot_id.id or False,
#                 package_id=reserved_quant.package_id.id or False,
#                 owner_id=reserved_quant.owner_id.id or False,
#             )
#         return vals