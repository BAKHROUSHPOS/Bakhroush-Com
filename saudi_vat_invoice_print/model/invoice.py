# -*- coding: utf-8 -*-

from odoo import api, models, fields, _
from num2words import num2words
from odoo.http import request
from . import qr_code_base


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    tax_amount = fields.Monetary('Tax amount', compute='_compute_tax_amount',store=True)
    vat_text = fields.Char('Vat Text', compute='_get_vat_text',store=True)
    discount_amount = fields.Float('Discount Amount', compute='_compute_all_price',store=True)
    price_before_discount = fields.Monetary('Price B/f Disc',compute='_compute_all_price',store=True)

    @api.depends('tax_ids', 'price_unit','quantity')
    def _get_vat_text(self):
        vat = ''
        for line in self:
            for tax in line.tax_ids:
                vat += str(tax.amount) + '%,'
            line.vat_text = vat[:-1]

    @api.depends('discount','price_unit','quantity')
    def _compute_all_price(self):
        for line in self:
            line.price_before_discount = line.quantity * line.price_unit
            line.discount_amount = (line.price_before_discount  * line.discount) / 100.0


    @api.depends('price_unit','quantity','price_subtotal','price_total')
    def _compute_tax_amount(self):
        for line in self:
            line.tax_amount = line.price_total - line.price_subtotal

class AccountMove(models.Model):
    _inherit = 'account.move'

    amount_text = fields.Char(string='Amount In Words', compute='amount_to_words')
    amount_in_ar = fields.Char(string='Amount In Words', compute='amount_to_words')
    attention = fields.Many2one('res.partner', 'Attention')
    approved_by = fields.Many2one('res.partner', 'Approved By')
    vat_text = fields.Char('Vat Text',compute='_get_vat_text')
    vat_arabic_text = fields.Char('Vat Text(Arabic)',compute='_get_vat_text')
    discount = fields.Float('Discount',compute='_compute_all_price')
    price_before_discount = fields.Monetary('Total ( Excluded VAT)',compute='_compute_all_price')
    qr_image = fields.Binary("QR Code", compute='_generate_qr_code')
    delivery_date = fields.Date('Delivery Date')

    def _generate_qr_code(self):
        self.qr_image = qr_code_base.generate_qr_code(self.partner_id.name)

    # def sticker_barcode_generator(self):
    #     # patient = self.env['lab.patient'].search([('patient', '=', self.partner_id.id)])
    #     # self.qr_image = generate_qr_code(patient.name)
    #     patient = self.env['lab.patient'].search(
    #         [('patient', '=', self.partner_id.id)])
    #     data = {
    #         "qr_code_image": self.qr_image,
    #         'pid': patient.name
    #     }
    #     return self.env.ref("ehcs_qr_code_invoice.sticker_barcode_action").report_action(
    #         self, data=data
    #     )


    @api.depends('invoice_line_ids','amount_untaxed','amount_tax')
    def _compute_all_price(self):
        price_before_discount = discount = 0
        for line in self.invoice_line_ids:
           price_before_discount += line.price_before_discount
           discount += line.discount_amount

        self.price_before_discount = price_before_discount
        self.discount = discount

    @api.depends('invoice_line_ids','amount_total')
    def _get_vat_text(self):
        vat = ''
        arab = ''
        for tax in self.mapped('invoice_line_ids.tax_ids'):
            vat += str(tax.amount) + '%,'
            arab += str(tax.amount_in_arabic) + '%,'
        self.vat_text = vat[:-1]
        self.vat_arabic_text = arab[:-1]


    def amount_to_words(self):
        amount_in_eng = num2words(self.amount_total, to='currency',
                                  lang='en')

        amount_in_eng = amount_in_eng.replace('euro', 'riyals')
        amount_in_eng = amount_in_eng.replace('cents', 'halala')
        self.amount_text = amount_in_eng
        self.amount_in_ar = num2words(self.amount_total, to='currency',
                                      lang='ar')

    def invoice_validate(self):
        analytic = self.invoice_line_ids.mapped('account_analytic_id')
        if len(analytic) != 1:
            analytic = False
        if self.default_analytic:
            analytic = self.default_analytic
        if analytic is not False:
            for line in self.move_id.line_ids:
                if line.account_id.id == self.account_id.id:
                    line.write({'analytic_account_id': analytic.id, 'partner_id': self.partner_id.id})
        return super(AccountMove, self).invoice_validate()

    @api.onchange('partner_id')
    def _onchange_partner_id_other(self):
        if self.partner_id:
            self.attention = self.partner_id.id


    def invoice_print(self):
        self.ensure_one()
        self.sent = True
        return self.env['report'].get_action(self, 'custom_azmi_holding.report_azmi_invoicerishi_format_pdt')

class AccountTax(models.Model):
    _inherit = 'account.tax'

    amount_in_arabic = fields.Float('Amount in Arabic')
